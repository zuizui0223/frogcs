#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")
Q=1.959963984540054
EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))

def metrics_for_run(rid,stops,ss):
    sets=[set(ss.get((rid,st),set())) for st in stops]
    active=[x for x in sets if x]
    n=len(active)
    gamma=len(set().union(*active)) if active else 0
    incid=sum(len(x) for x in active)
    alpha=incid/n if n else np.nan
    beta=np.nan
    if n>=2 and alpha>0:
        beta=((gamma/alpha)-1)/(n-1)
    return {
        "n_active":float(n),
        "gamma":float(gamma),
        "alpha_active":float(alpha) if np.isfinite(alpha) else np.nan,
        "beta_norm":float(beta) if np.isfinite(beta) else np.nan,
    }

def baseline_templates(runs,sampled,ss):
    e=runs[runs["SurveyYear"].isin(EARLY)].copy()
    rows=[]
    for r in e.itertuples(index=False):
        rid=str(r.RunID)
        stops=sorted(sampled[rid])
        if len(stops)!=10:
            raise RuntimeError(f"baseline stop count drift {rid}")
        m=metrics_for_run(rid,stops,ss)
        rows.append({
            "State":str(r.State),"RouteNumber":str(r.RouteNumber),"RunNumber":str(r.RunNumber),
            "SurveyYear":int(r.SurveyYear),**m
        })
    q=pd.DataFrame(rows)
    out=[]
    for key,g in q.groupby(["State","RouteNumber","RunNumber"],sort=False):
        gb=g[np.isfinite(g["beta_norm"])].copy()
        if len(gb)<3:
            continue
        out.append({
            "State":key[0],"RouteNumber":key[1],"RunNumber":key[2],
            "baseline_beta":float(gb["beta_norm"].mean()),
            "baseline_gamma":float(g["gamma"].mean()),
            "baseline_active_stops":float(g["n_active"].mean()),
            "baseline_estimable_beta_runs":int(len(gb)),
            "baseline_total_runs":int(len(g)),
        })
    d=pd.DataFrame(out)
    if len(d)==0:
        return d
    for c in ["baseline_beta","baseline_gamma","baseline_active_stops"]:
        sd=float(d[c].std(ddof=0))
        if not sd>0:
            raise RuntimeError(f"zero baseline variance {c}")
        d["z_"+c]=(d[c]-d[c].mean())/sd
    return d

def late_pair_details(runs,sets,sampled,ss,templates):
    late=runs[runs["SurveyYear"].isin(LATE)].copy()
    pairs=base.pair_runs(late,sets)
    x=pairs.merge(
        templates,
        on=["State","RouteNumber","RunNumber"],
        how="inner",
        validate="many_to_one"
    )
    details=[]
    for p in x.itertuples(index=False):
        w,d=str(p.wet_RunID),str(p.dry_RunID)
        sw=set(sampled[w]);sd=set(sampled[d])
        if len(sw)!=10 or sw!=sd:
            raise RuntimeError(f"validation stop alignment failed {w} {d}")
        stops=sorted(sw)
        W_by={st:set(ss.get((w,st),set())) for st in stops}
        D_by={st:set(ss.get((d,st),set())) for st in stops}
        W=set().union(*(W_by[st] for st in stops))
        D=set().union(*(D_by[st] for st in stops))
        active_w={st:bool(W_by[st]) for st in stops}
        active_d={st:bool(D_by[st]) for st in stops}
        mw=metrics_for_run(w,stops,ss)
        md=metrics_for_run(d,stops,ss)

        gain_corner=0
        loss_corner=0
        for st in stops:
            for sp in W_by[st]-D_by[st]:
                if sp not in D and not active_d[st]:
                    gain_corner+=1
            for sp in D_by[st]-W_by[st]:
                if sp not in W and not active_w[st]:
                    loss_corner+=1

        details.append({
            "wet_RunID":w,"dry_RunID":d,
            "corner_expansion":float(gain_corner-loss_corner),
            "delta_active_stops":mw["n_active"]-md["n_active"],
            "delta_alpha_active":mw["alpha_active"]-md["alpha_active"]
                if np.isfinite(mw["alpha_active"]) and np.isfinite(md["alpha_active"]) else np.nan,
        })
    dd=pd.DataFrame(details)
    return late,pairs,x.merge(dd,on=["wet_RunID","dry_RunID"],how="left",validate="one_to_one")

FORM_GAMMA=(
    "richness_gain ~ rain_contrast * z_baseline_beta + "
    "rain_contrast * z_baseline_gamma + "
    "rain_contrast * z_baseline_active_stops + "
    "temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
)
FORM_CORNER=FORM_GAMMA.replace("richness_gain","corner_expansion",1)
FORM_ACTIVE=FORM_GAMMA.replace("richness_gain","delta_active_stops",1)
FORM_ALPHA=FORM_GAMMA.replace("richness_gain","delta_alpha_active",1)
TERM="rain_contrast:z_baseline_beta"

def fit(x,response,formula):
    y=x[np.isfinite(pd.to_numeric(x[response],errors="coerce"))].copy()
    f=smf.ols(formula,data=y).fit(cov_type="cluster",cov_kwds={"groups":y["route_cluster"]})
    b=float(f.params[TERM]);se=float(f.bse[TERM]);p=float(f.pvalues[TERM])
    return {
        "response":response,"formula":formula,"term":TERM,
        "n_pairs":int(len(y)),"n_routes":int(y["route_cluster"].nunique()),
        "beta":b,"se_cluster":se,"ci95":[b-Q*se,b+Q*se],"p_value":p,
    }

def package(x):
    return {
        "gamma_primary":fit(x,"richness_gain",FORM_GAMMA),
        "corner_secondary":fit(x,"corner_expansion",FORM_CORNER),
        "active_stops_secondary":fit(x,"delta_active_stops",FORM_ACTIVE),
        "alpha_secondary":fit(x,"delta_alpha_active",FORM_ALPHA),
    }

def correlations(templates):
    cols=["z_baseline_beta","z_baseline_gamma","z_baseline_active_stops"]
    c=templates[cols].corr()
    return {a:{b:float(c.loc[a,b]) for b in cols} for a in cols}

def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)

    templates=baseline_templates(runs,sampled,ss)
    late_runs,all_late_pairs,x=late_pair_details(runs,sets,sampled,ss,templates)

    if len(x)<300 or x["route_cluster"].nunique()<100:
        raise SystemExit(f"validation gate failed pairs={len(x)} routes={x['route_cluster'].nunique()}")

    pkg=package(x)
    primary=pkg["gamma_primary"]
    support=bool(primary["beta"]>0 and primary["ci95"][0]>0)

    exact=x[x["year_gap"]==1].copy()
    exact_pkg=package(exact) if len(exact)>=200 and exact["route_cluster"].nunique()>=80 else None

    result={
        "analysis":"naamp_latent_spatial_heterogeneity_v0_1",
        "contract":"NAAMP_LATENT_SPATIAL_HETEROGENEITY_CONTRACT_V0_1.json",
        "time_split":{"baseline":[2001,2007],"validation":[2008,2015]},
        "baseline":{
            "eligible_templates":int(len(templates)),
            "mean_beta":float(templates["baseline_beta"].mean()),
            "mean_gamma":float(templates["baseline_gamma"].mean()),
            "mean_active_stops":float(templates["baseline_active_stops"].mean()),
            "median_estimable_beta_runs":float(templates["baseline_estimable_beta_runs"].median()),
            "moderator_correlations":correlations(templates),
        },
        "validation":{
            "eligible_runs":int(len(late_runs)),
            "all_matched_pairs":int(len(all_late_pairs)),
            "analysis_pairs":int(len(x)),
            "analysis_routes":int(x["route_cluster"].nunique()),
        },
        "models":pkg,
        "frozen_primary_support_rule_pass":support,
        "exact_consecutive_year":None if exact_pkg is None else {
            "n_pairs":int(len(exact)),
            "n_routes":int(exact["route_cluster"].nunique()),
            "models":exact_pkg,
        },
        "interpretation_boundary":{
            "baseline_beta":"Early-period acoustic among-active-stop differentiation, not measured habitat heterogeneity.",
            "held_out_validation":True,
            "demographic_spatial_insurance_claim_authorized":False,
            "dispersal_claim_authorized":False,
            "causal_rainfall_claim_authorized":False,
            "endpoint_retuning_after_readback_authorized":False,
        }
    }
    Path("NAAMP_LATENT_SPATIAL_HETEROGENEITY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
