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
from scipy.stats import spearmanr, binomtest

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
TRAIT_SCRIPT=ROOT/"run_naamp_rainfall_filter_traits.py"

spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

tspec=importlib.util.spec_from_file_location("trait_base",TRAIT_SCRIPT)
trait=importlib.util.module_from_spec(tspec)
assert tspec.loader
tspec.loader.exec_module(trait)

Q=1.959963984540054
EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))

def fit_species(sp,events):
    x=pd.DataFrame(events)
    if len(x)<25 or x.route_cluster.nunique()<8:
        return {
            "species":sp,"estimable":False,"n_events":int(len(x)),
            "n_routes":int(x.route_cluster.nunique()) if len(x) else 0,
            "reason":"period_eligibility"
        }
    for col in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+col]=x[col]-x[col].mean()
    formula="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        f=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x.route_cluster}
        )
        b=float(f.params["Intercept"]);se=float(f.bse["Intercept"]);p=float(f.pvalues["Intercept"])
        if not all(np.isfinite([b,se,p])) or se<=0:
            raise ValueError("nonfinite intercept")
        lo=b-Q*se;hi=b+Q*se
        return {
            "species":sp,"estimable":True,"n_events":int(len(x)),
            "n_routes":int(x.route_cluster.nunique()),
            "log_odds":b,"se":se,"ci95":[lo,hi],"p_value":p,
            "wet_probability":float(1/(1+np.exp(-b))),
            "weight":float(1/(se*se))
        }
    except Exception as e:
        return {"species":sp,"estimable":False,"n_events":int(len(x)),"reason":str(e)}

def period_response(d,sets,years):
    x=d[d["SurveyYear"].isin(years)].copy()
    pairs=base.pair_runs(x,sets)
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
                "year_gap":float(r.year_gap)
            })
    results=[fit_species(sp,events[sp]) for sp in sorted(events)]
    return x,pairs,pd.DataFrame(results)

def family_map(species):
    t,blob=trait.load_traits()
    idx={s:i for i,s in enumerate(t["species_norm"].tolist())}
    out={};audit=[]
    for sp in species:
        candidates=[sp]
        toks=sp.split()
        if len(toks)==2 and toks[0] in trait.ALIASES:
            candidates.append(trait.ALIASES[toks[0]]+" "+toks[1])
        hits=[c for c in candidates if c in idx]
        if sp in hits:
            chosen=sp
        elif len(hits)==1:
            chosen=hits[0]
        else:
            chosen=None
        fam=""
        if chosen is not None:
            fam=str(t.iloc[idx[chosen]].get("Family","") or "").strip()
        out[sp]=fam
        audit.append({"species":sp,"matched":bool(fam),"amphibio_species":chosen,"family":fam})
    return out,audit,blob

def primary_repeatability(m):
    rho,p=spearmanr(m["early_log_odds"],m["late_log_odds"])
    return {
        "n_species":int(len(m)),
        "spearman_rho":float(rho),
        "p_value":float(p),
        "positive_support":bool(rho>0 and p<0.05)
    }

def weighted_slope(m):
    f=smf.wls("late_log_odds ~ early_log_odds",data=m,weights=m["late_weight"]).fit(cov_type="HC3")
    b=float(f.params["early_log_odds"]);se=float(f.bse["early_log_odds"]);p=float(f.pvalues["early_log_odds"])
    lo=b-Q*se;hi=b+Q*se
    return {
        "beta":b,"se_hc3":se,"ci95_beta":[lo,hi],"p_value":p,
        "positive_ci_support":bool(lo>0)
    }

def sign_concordance(m):
    use=m[(m["early_log_odds"]!=0)&(m["late_log_odds"]!=0)].copy()
    same=((np.sign(use["early_log_odds"])==np.sign(use["late_log_odds"]))).sum()
    n=len(use)
    bt=binomtest(int(same),int(n),p=.5,alternative="greater") if n else None
    return {
        "n_species":int(n),"same_sign":int(same),
        "fraction_same_sign":float(same/n) if n else None,
        "one_sided_binomial_p":float(bt.pvalue) if bt else None
    }

def family_adjusted(m):
    y=m[m["family"].astype(str)!=""].copy()
    if len(y)<18 or y["family"].nunique()<2:
        return {"estimable":False,"n_species":int(len(y)),"reason":"insufficient_family_coverage"}
    f=smf.wls("late_log_odds ~ early_log_odds + C(family)",data=y,weights=y["late_weight"]).fit(cov_type="HC3")
    if f.df_resid<10:
        return {
            "estimable":False,"n_species":int(len(y)),"n_families":int(y.family.nunique()),
            "df_resid":float(f.df_resid),"reason":"residual_df_below_10"
        }
    b=float(f.params["early_log_odds"]);se=float(f.bse["early_log_odds"]);p=float(f.pvalues["early_log_odds"])
    lo=b-Q*se;hi=b+Q*se
    return {
        "estimable":True,"n_species":int(len(y)),"n_families":int(y.family.nunique()),
        "df_resid":float(f.df_resid),"beta":b,"se_hc3":se,
        "ci95_beta":[lo,hi],"p_value":p,"positive_ci_support":bool(lo>0)
    }

def leave_one_family_out(m):
    out=[]
    counts=m["family"].value_counts()
    for fam,n in sorted(counts.items()):
        if not fam or int(n)<2:
            continue
        x=m[m["family"]!=fam]
        if len(x)<10:
            out.append({"excluded_family":fam,"estimable":False,"n_species":int(len(x))})
            continue
        rho,p=spearmanr(x["early_log_odds"],x["late_log_odds"])
        out.append({
            "excluded_family":fam,"estimable":True,"n_species":int(len(x)),
            "spearman_rho":float(rho),"p_value":float(p)
        })
    return out

def main():
    raw=base.load()
    d,sets=base.build_runs(raw)

    early_runs,early_pairs,early=period_response(d,sets,EARLY)
    late_runs,late_pairs,late=period_response(d,sets,LATE)

    e=early[early["estimable"]==True].copy()
    l=late[late["estimable"]==True].copy()

    m=e.merge(l,on="species",suffixes=("_early","_late"))
    if len(m)<15:
        raise SystemExit(f"overlap species below minimum: {len(m)}")

    m=m.rename(columns={
        "log_odds_early":"early_log_odds","se_early":"early_se","weight_early":"early_weight",
        "wet_probability_early":"early_wet_probability","n_events_early":"early_events","n_routes_early":"early_routes",
        "log_odds_late":"late_log_odds","se_late":"late_se","weight_late":"late_weight",
        "wet_probability_late":"late_wet_probability","n_events_late":"late_events","n_routes_late":"late_routes"
    })

    fam,audit,blob=family_map(m["species"].tolist())
    m["family"]=m["species"].map(fam).fillna("")

    primary=primary_repeatability(m)
    slope=weighted_slope(m)
    signs=sign_concordance(m)
    famadj=family_adjusted(m)
    loo=leave_one_family_out(m)

    result={
        "analysis":"naamp_species_rain_response_temporal_repeatability_v0_1",
        "contract":"NAAMP_SPECIES_RAIN_RESPONSE_REPEATABILITY_CONTRACT_V0_1.json",
        "time_split":{"early":[2001,2007],"late":[2008,2015]},
        "early":{
            "eligible_runs":int(len(early_runs)),
            "matched_pairs":int(len(early_pairs)),
            "estimable_species":int(len(e))
        },
        "late":{
            "eligible_runs":int(len(late_runs)),
            "matched_pairs":int(len(late_pairs)),
            "estimable_species":int(len(l))
        },
        "overlap_species":int(len(m)),
        "primary_repeatability":primary,
        "weighted_regression_sensitivity":slope,
        "sign_concordance":signs,
        "family_structure":{
            "source":"AmphiBIO v1","git_blob_sha1":blob,
            "taxonomy_audit":audit,
            "family_adjusted":famadj,
            "leave_one_family_out":loo
        },
        "species_table":[
            {
                "species":str(r.species),"family":str(r.family),
                "early_events":int(r.early_events),"early_routes":int(r.early_routes),
                "early_log_odds":float(r.early_log_odds),"early_se":float(r.early_se),
                "early_wet_probability":float(r.early_wet_probability),
                "late_events":int(r.late_events),"late_routes":int(r.late_routes),
                "late_log_odds":float(r.late_log_odds),"late_se":float(r.late_se),
                "late_wet_probability":float(r.late_wet_probability),
                "same_sign":bool(np.sign(r.early_log_odds)==np.sign(r.late_log_odds))
            }
            for r in m.itertuples(index=False)
        ],
        "interpretation_boundary":{
            "same_species_temporal_validation":True,
            "independent_species_replication":False,
            "trait_mechanism_identified":False,
            "causal_claim_authorized":False
        }
    }

    Path("NAAMP_SPECIES_RAIN_RESPONSE_REPEATABILITY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
