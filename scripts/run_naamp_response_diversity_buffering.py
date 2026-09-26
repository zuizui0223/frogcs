#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

Q=1.959963984540054
EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))

def fit_species_response(sp,events):
    x=pd.DataFrame(events)
    nr=x["route_cluster"].nunique() if len(x) else 0
    if len(x)<25 or nr<8:
        return None
    for c in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+c]=x[c]-x[c].mean()
    formula="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        f=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x["route_cluster"]}
        )
        b=float(f.params["Intercept"]);se=float(f.bse["Intercept"])
        if not np.isfinite(b) or not np.isfinite(se) or se<=0:
            return None
        return {"species":sp,"log_odds":b,"se":se,"n_events":int(len(x)),"n_routes":int(nr)}
    except Exception:
        return None

def early_species_scores(d,sets):
    e=d[d["SurveyYear"].isin(EARLY)].copy()
    pairs=base.pair_runs(e,sets)
    events=defaultdict(list)
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)];D=sets[str(r.dry_RunID)]
        for sp in W^D:
            events[sp].append({
                "y":int(sp in W),
                "route_cluster":str(r.route_cluster),
                "rain_contrast":float(r.rain_contrast),
                "temp_difference":float(r.temp_difference),
                "doy_difference":float(r.doy_difference),
                "year_gap":float(r.year_gap),
            })
    rows=[]
    for sp in sorted(events):
        z=fit_species_response(sp,events[sp])
        if z is not None: rows.append(z)
    return e,pairs,pd.DataFrame(rows)

def local_early_pools(early_runs,sets,scores):
    score_map={str(r.species):float(r.log_odds) for r in scores.itertuples(index=False)}
    pools=defaultdict(set)
    for r in early_runs.itertuples(index=False):
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        pools[key].update(sets[str(r.RunID)])

    rows=[]
    for key,pool in pools.items():
        scored=sorted([sp for sp in pool if sp in score_map])
        coverage=(len(scored)/len(pool)) if pool else 0.0
        if len(scored)<3 or coverage<0.60:
            continue
        vals=np.array([score_map[sp] for sp in scored],float)
        p=float(np.mean(vals>0))
        rd=float(4*p*(1-p))
        rows.append({
            "State":key[0],"RouteNumber":key[1],"RunNumber":key[2],
            "early_pool_richness":int(len(pool)),
            "early_scored_richness":int(len(scored)),
            "early_scored_fraction":float(coverage),
            "response_sign_diversity":rd,
            "mean_early_response":float(np.mean(vals)),
            "sd_early_response":float(np.std(vals,ddof=0)),
            "positive_early_species":int(np.sum(vals>0)),
            "negative_early_species":int(np.sum(vals<=0)),
        })
    out=pd.DataFrame(rows)
    if len(out)==0:
        return out
    z=np.log(out["early_scored_richness"].astype(float))
    sd=float(z.std(ddof=0))
    if not sd>0: raise RuntimeError("zero variance early scored richness")
    out["z_log_early_scored_richness"]=(z-z.mean())/sd
    return out

def late_validation_pairs(d,sets,pools):
    l=d[d["SurveyYear"].isin(LATE)].copy()
    pairs=base.pair_runs(l,sets)
    x=pairs.merge(pools,on=["State","RouteNumber","RunNumber"],how="inner",validate="many_to_one")
    x["discordant_total"]=x["wet_only"]+x["dry_only"]
    x["compensation_fraction"]=np.where(
        x["discordant_total"]>0,
        1.0-np.abs(x["wet_only"]-x["dry_only"])/x["discordant_total"],
        np.nan
    )
    return l,pairs,x

PRIMARY_FORMULA=(
    "richness_gain ~ rain_contrast * response_sign_diversity + "
    "rain_contrast * mean_early_response + "
    "rain_contrast * z_log_early_scored_richness + "
    "temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
)
SD_FORMULA=(
    "richness_gain ~ rain_contrast * sd_early_response + "
    "rain_contrast * mean_early_response + "
    "rain_contrast * z_log_early_scored_richness + "
    "temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
)
COMP_FORMULA=(
    "compensation_fraction ~ rain_contrast * response_sign_diversity + "
    "mean_early_response + z_log_early_scored_richness + "
    "temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
)

def fit_term(x,response,formula,term):
    y=x[np.isfinite(pd.to_numeric(x[response],errors="coerce"))].copy()
    f=smf.ols(formula,data=y).fit(cov_type="cluster",cov_kwds={"groups":y["route_cluster"]})
    b=float(f.params[term]);se=float(f.bse[term]);p=float(f.pvalues[term])
    return {
        "response":response,"formula":formula,"term":term,
        "n_pairs":int(len(y)),"n_routes":int(y["route_cluster"].nunique()),
        "beta":b,"se_cluster":se,"ci95":[b-Q*se,b+Q*se],"p_value":p
    }

def correlations(x):
    cols=["response_sign_diversity","mean_early_response","z_log_early_scored_richness","sd_early_response"]
    c=x[cols].drop_duplicates().corr()
    return {a:{b:float(c.loc[a,b]) for b in cols} for a in cols}

def package(x):
    primary=fit_term(
        x,"richness_gain",PRIMARY_FORMULA,
        "rain_contrast:response_sign_diversity"
    )
    sd=fit_term(
        x,"richness_gain",SD_FORMULA,
        "rain_contrast:sd_early_response"
    )
    comp=fit_term(
        x,"compensation_fraction",COMP_FORMULA,
        "rain_contrast:response_sign_diversity"
    )
    return {"primary":primary,"sd_diagnostic":sd,"compensation_diagnostic":comp}

def main():
    raw=base.load()
    d,sets=base.build_runs(raw)
    early_runs,early_pairs,scores=early_species_scores(d,sets)
    pools=local_early_pools(early_runs,sets,scores)
    late_runs,late_pairs,x=late_validation_pairs(d,sets,pools)

    if len(x)<300 or x["route_cluster"].nunique()<100:
        raise SystemExit(
            f"validation gate failed pairs={len(x)} routes={x['route_cluster'].nunique()}"
        )

    primary_pkg=package(x)
    exact=x[x["year_gap"]==1].copy()
    exact_pkg=package(exact) if len(exact)>=200 and exact["route_cluster"].nunique()>=80 else None

    p=primary_pkg["primary"]
    support=bool(p["beta"]<0 and p["ci95"][1]<0)

    result={
        "analysis":"naamp_response_diversity_buffering_v0_1",
        "contract":"NAAMP_RESPONSE_DIVERSITY_BUFFERING_CONTRACT_V0_1.json",
        "time_split":{"trait_period":[2001,2007],"validation_period":[2008,2015]},
        "early":{
            "eligible_runs":int(len(early_runs)),
            "matched_pairs":int(len(early_pairs)),
            "estimable_species":int(len(scores)),
            "eligible_route_season_pools":int(len(pools))
        },
        "validation":{
            "eligible_runs":int(len(late_runs)),
            "all_matched_pairs":int(len(late_pairs)),
            "analysis_pairs":int(len(x)),
            "analysis_routes":int(x["route_cluster"].nunique()),
            "mean_response_sign_diversity":float(x["response_sign_diversity"].mean()),
            "mean_early_scored_richness":float(x["early_scored_richness"].mean()),
            "mean_early_scored_fraction":float(x["early_scored_fraction"].mean()),
            "moderator_correlations":correlations(x)
        },
        "primary_model":primary_pkg["primary"],
        "frozen_support_rule_pass":support,
        "secondary_diagnostics":{
            "response_sd_interaction":primary_pkg["sd_diagnostic"],
            "compensation_fraction_interaction":primary_pkg["compensation_diagnostic"]
        },
        "exact_consecutive_year":None if exact_pkg is None else {
            "n_pairs":int(len(exact)),
            "n_routes":int(exact["route_cluster"].nunique()),
            "models":exact_pkg
        },
        "interpretation_boundary":{
            "response_diversity":"Early-period acoustic wet-vs-dry response-sign diversity, not demographic response diversity.",
            "temporal_holdout":True,
            "causal_rainfall_claim_authorized":False,
            "demographic_stability_claim_authorized":False,
            "endpoint_retuning_after_readback_authorized":False
        }
    }
    Path("NAAMP_RESPONSE_DIVERSITY_BUFFERING_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
