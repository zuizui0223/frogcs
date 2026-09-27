#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

EARLY=set(range(2001,2008))
LATE=set(range(2008,2016))
Q=1.959963984540054

def build_baseline_context(d):
    b=d[d["SurveyYear"].isin(EARLY)].copy()
    rows=[]
    for route,g in b.groupby("route_cluster"):
        if len(g)<6:
            continue
        rows.append({
            "route_cluster":str(route),
            "State":str(g["State"].iloc[0]),
            "RouteNumber":str(g["RouteNumber"].iloc[0]),
            "baseline_runs":int(len(g)),
            "baseline_dryness":float(np.median(np.log1p(g["DaysSinceRain"].astype(float)))),
            "baseline_days_since_rain_median":float(np.median(g["DaysSinceRain"].astype(float)))
        })
    r=pd.DataFrame(rows)
    if r.empty:
        raise SystemExit("no baseline routes")
    mu=float(r["baseline_dryness"].mean())
    sd=float(r["baseline_dryness"].std(ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise SystemExit("baseline dryness has no variation")
    r["baseline_dryness_z"]=(r["baseline_dryness"]-mu)/sd
    return r,{"mean_log1p":mu,"sd_log1p":sd}

def validation_pairs(d,sets,context):
    v=d[d["SurveyYear"].isin(LATE)].copy()
    p=base.pair_runs(v,sets)
    p=p.merge(context[["route_cluster","baseline_runs","baseline_dryness","baseline_days_since_rain_median","baseline_dryness_z"]],on="route_cluster",how="inner")
    return v,p

def fit_model(d,response):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    formula=f"{response} ~ rain_contrast * baseline_dryness_z + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    f=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    term="rain_contrast:baseline_dryness_z"
    b=float(f.params[term]);se=float(f.bse[term]);p=float(f.pvalues[term])
    lo=b-Q*se;hi=b+Q*se
    rain_main=float(f.params["rain_contrast"])
    slopes={str(z):float(rain_main+b*z) for z in [-1,0,1]}
    return {
        "response":response,"formula":formula,
        "n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
        "interaction_term":term,"beta_interaction":b,"se_cluster":se,
        "ci95_interaction":[lo,hi],"p_value":p,
        "positive_ci_support":bool(lo>0),
        "rain_contrast_slope_at_baseline_dryness_z":slopes
    }

def quartile_summary(p):
    route=p[["route_cluster","baseline_dryness_z","baseline_days_since_rain_median"]].drop_duplicates("route_cluster").copy()
    try:
        route["quartile"]=pd.qcut(route["baseline_dryness_z"],4,labels=["Q1_wetter","Q2","Q3","Q4_drier"],duplicates="drop")
    except Exception:
        route["quartile"]=pd.cut(route["baseline_dryness_z"],4,labels=["Q1_wetter","Q2","Q3","Q4_drier"])
    qmap=route.set_index("route_cluster")["quartile"].to_dict()
    pp=p.copy()
    pp["quartile"]=pp["route_cluster"].map(qmap)
    out={}
    for q,g in pp.groupby("quartile",observed=True):
        rr=route[route["quartile"]==q]
        out[str(q)]={
            "routes":int(rr.route_cluster.nunique()),
            "pairs":int(len(g)),
            "median_baseline_days_since_rain":float(rr.baseline_days_since_rain_median.median()),
            "mean_rain_contrast":float(g.rain_contrast.mean()),
            "mean_richness_gain":float(g.richness_gain.mean()),
            "mean_turnover":float(g.simpson_turnover.mean())
        }
    return out

def main():
    raw=base.load()
    d,sets=base.build_runs(raw)
    context,std=build_baseline_context(d)
    v,pairs=validation_pairs(d,sets,context)
    if len(pairs)==0:
        raise SystemExit("no validation pairs with baseline context")

    primary=fit_model(pairs,"richness_gain")
    secondary=fit_model(pairs,"simpson_turnover")

    exact=pairs[pairs["year_gap"]==1].copy()
    exact_primary=fit_model(exact,"richness_gain") if len(exact) else None
    exact_secondary=fit_model(exact,"simpson_turnover") if len(exact) else None

    result={
        "analysis":"naamp_context_dependent_rainfall_pulse_v0_1",
        "contract":"NAAMP_CONTEXT_DEPENDENT_PULSE_CONTRACT_V0_1.json",
        "time_split":{"baseline":[2001,2007],"validation":[2008,2015]},
        "baseline_context":{
            "eligible_routes":int(len(context)),
            "standardization":std,
            "baseline_runs_summary":{
                "min":int(context.baseline_runs.min()),
                "median":float(context.baseline_runs.median()),
                "max":int(context.baseline_runs.max())
            },
            "median_days_since_rain_summary":{
                "min":float(context.baseline_days_since_rain_median.min()),
                "median":float(context.baseline_days_since_rain_median.median()),
                "max":float(context.baseline_days_since_rain_median.max())
            }
        },
        "validation":{
            "eligible_runs":int(len(v)),
            "matched_pairs_with_context":int(len(pairs)),
            "routes":int(pairs.route_cluster.nunique()),
            "states":int(pairs.State.nunique())
        },
        "primary_richness_interaction":primary,
        "secondary_turnover_interaction":secondary,
        "exact_consecutive_year_sensitivity":{
            "n_pairs":int(len(exact)),
            "primary_richness_interaction":exact_primary,
            "secondary_turnover_interaction":exact_secondary
        },
        "dryness_quartiles":quartile_summary(pairs),
        "interpretation_boundary":{
            "baseline_context_uses_validation_years":False,
            "validation_response_uses_baseline_years":False,
            "baseline_dryness_is_full_climate_aridity":False,
            "active_community_not_occupancy":True,
            "causal_claim_authorized":False
        }
    }

    Path("NAAMP_CONTEXT_DEPENDENT_PULSE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
