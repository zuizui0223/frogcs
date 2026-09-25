#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import norm

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

Q=1.959963984540054
BIN_ORDER=["day0","day1","days2_3","days4_7","days8plus"]
RECENT_ORDER=["day0","day1","days2_3","days4_7"]

def recency_bin(x: float) -> str:
    x=float(x)
    if x==0:return "day0"
    if x==1:return "day1"
    if 2<=x<=3:return "days2_3"
    if 4<=x<=7:return "days4_7"
    if 8<=x<=180:return "days8plus"
    raise ValueError(x)

def prepare_runs():
    d,sets=base.build_runs(base.load())
    d=d.copy()
    d["recency_bin"]=pd.Categorical(
        [recency_bin(x) for x in d["DaysSinceRain"]],
        categories=BIN_ORDER,ordered=True
    )
    d["route_season_stratum"]=(
        d["State"].astype(str)+":"+d["RouteNumber"].astype(str)+":"+d["RunNumber"].astype(str)
    )
    return d,sets

def absorb_group(df,cols,group):
    g=df.groupby(group,observed=True)
    return df[cols]-g[cols].transform("mean")

def fit_run_level(d):
    counts={b:int((d["recency_bin"]==b).sum()) for b in BIN_ORDER}
    if any(n<100 for n in counts.values()):
        raise SystemExit(f"prespecified minimum per bin failed: {counts}")

    work=d.copy()
    # Reference is >=8 days. Four dummy contrasts are therefore direct richness differences.
    for b in RECENT_ORDER:
        work[f"bin_{b}"]=(work["recency_bin"]==b).astype(float)

    spline=patsy.dmatrix(
        "bs(doy, df=5, degree=3, include_intercept=False) - 1",
        work,return_type="dataframe"
    )
    spline.columns=[f"doy_bs{i+1}" for i in range(spline.shape[1])]
    work=pd.concat([work.reset_index(drop=True),spline.reset_index(drop=True)],axis=1)

    xcols=[f"bin_{b}" for b in RECENT_ORDER]+[
        "mean_temp_c","SurveyYear"
    ]+list(spline.columns)
    within=absorb_group(work,xcols+["richness"],"route_season_stratum")
    X=within[xcols].astype(float)
    y=within["richness"].astype(float)

    # Drop rows with no within-stratum predictor information.
    informative=np.asarray(np.abs(X).sum(axis=1)>1e-12)
    X=X.loc[informative]
    y=y.loc[informative]
    groups=work.loc[informative,"route_cluster"]

    fit=sm.OLS(y,X).fit(cov_type="cluster",cov_kwds={"groups":groups})
    effects={}
    for b in RECENT_ORDER:
        term=f"bin_{b}"
        beta=float(fit.params[term]);se=float(fit.bse[term]);p=float(fit.pvalues[term])
        effects[b]={
            "difference_species_vs_days8plus":beta,
            "se_cluster":se,
            "ci95":[beta-Q*se,beta+Q*se],
            "p_value":p
        }

    pulse_end="none_detected"
    earlier_nonnegative=True
    latest=None
    for b in RECENT_ORDER:
        e=effects[b]
        if e["difference_species_vs_days8plus"]<0:
            earlier_nonnegative=False
        if earlier_nonnegative and e["ci95"][0]>0:
            latest=b
    if latest is not None:
        pulse_end=latest
    elif any(e["ci95"][0]>0 for e in effects.values()):
        pulse_end="non_monotonic_undefined"

    raw={}
    for b in BIN_ORDER:
        x=work[work["recency_bin"]==b]
        raw[b]={
            "n_runs":int(len(x)),
            "n_routes":int(x["route_cluster"].nunique()),
            "mean_richness":float(x["richness"].mean()),
            "median_richness":float(x["richness"].median()),
            "mean_temperature_c":float(x["mean_temp_c"].mean()),
            "mean_doy":float(x["doy"].mean())
        }

    return {
        "n_runs":int(len(work)),
        "n_routes":int(work["route_cluster"].nunique()),
        "n_route_season_strata":int(work["route_season_stratum"].nunique()),
        "bin_counts":counts,
        "raw_by_bin":raw,
        "fixed_effects_method":"Within-transform State×RouteNumber×RunNumber; OLS with route-clustered covariance.",
        "effects_vs_days8plus":effects,
        "prespecified_richness_pulse_end":pulse_end
    }

def marginal_bin_means(fit,data,response):
    design_info=fit.model.data.design_info
    out={}
    cov=np.asarray(fit.cov_params())
    params=np.asarray(fit.params)
    for b in RECENT_ORDER:
        nd=data.copy()
        nd["recent_bin"]=pd.Categorical([b]*len(nd),categories=RECENT_ORDER)
        nd["c_temp"]=0.0
        nd["c_doy"]=0.0
        nd["c_year_gap"]=0.0
        mat=np.asarray(patsy.build_design_matrices([design_info],nd)[0],float)
        L=mat.mean(axis=0)
        est=float(L@params)
        se=float(math.sqrt(max(0.0,L@cov@L)))
        p=float(2*norm.sf(abs(est/se))) if se>0 else None
        out[b]={
            "adjusted_mean":est,
            "se":se,
            "ci95":[est-Q*se,est+Q*se],
            "p_vs_zero":p
        }
    return out

def fit_pair_response(df,response):
    x=df[np.isfinite(pd.to_numeric(df[response],errors="coerce"))].copy()
    if len(x)==0:return None
    x["recent_bin"]=pd.Categorical(x["recent_bin"],categories=RECENT_ORDER)
    x["c_temp"]=x["temp_difference"]-x["temp_difference"].mean()
    x["c_doy"]=x["doy_difference"]-x["doy_difference"].mean()
    x["c_year_gap"]=x["year_gap"]-x["year_gap"].mean()
    formula=f"{response} ~ C(recent_bin) + c_temp + c_doy + c_year_gap + C(RunNumber)"
    fit=smf.ols(formula,data=x).fit(cov_type="cluster",cov_kwds={"groups":x["route_cluster"]})
    return {
        "n_pairs":int(len(x)),
        "n_routes":int(x["route_cluster"].nunique()),
        "formula":formula,
        "adjusted_means_by_recent_bin":marginal_bin_means(fit,x,response),
        "raw_means_by_recent_bin":{
            b:{
                "n_pairs":int((x["recent_bin"]==b).sum()),
                "mean":float(x.loc[x["recent_bin"]==b,response].mean())
            } for b in RECENT_ORDER
        }
    }

def build_anchor_pairs(d,sets):
    pairs=base.pair_runs(d,sets)
    x=pairs[(pairs["wet_days_since_rain"]<8)&(pairs["dry_days_since_rain"]>=8)].copy()
    x["recent_bin"]=pd.Categorical(
        [recency_bin(v) for v in x["wet_days_since_rain"]],
        categories=RECENT_ORDER,ordered=True
    )
    x["richness_recent_minus_anchor"]=x["richness_gain"]
    x["recent_only_species_count"]=x["wet_only"]
    x["anchor_only_species_count"]=x["dry_only"]
    return x

def fit_anchor_package(x):
    counts={b:int((x["recent_bin"]==b).sum()) for b in RECENT_ORDER}
    outputs={}
    for response in [
        "richness_recent_minus_anchor",
        "simpson_turnover",
        "nestedness_component",
        "recent_only_species_count",
        "anchor_only_species_count"
    ]:
        outputs[response]=fit_pair_response(x,response)
    exact=x[x["year_gap"]==1].copy()
    exact_outputs={}
    for response in [
        "richness_recent_minus_anchor",
        "simpson_turnover",
        "nestedness_component",
        "recent_only_species_count",
        "anchor_only_species_count"
    ]:
        exact_outputs[response]=fit_pair_response(exact,response)
    return {
        "n_pairs":int(len(x)),
        "n_routes":int(x["route_cluster"].nunique()),
        "bin_counts":counts,
        "responses":outputs,
        "exact_consecutive_year":{
            "n_pairs":int(len(exact)),
            "bin_counts":{b:int((exact["recent_bin"]==b).sum()) for b in RECENT_ORDER},
            "responses":exact_outputs
        }
    }

def main():
    d,sets=prepare_runs()
    run_level=fit_run_level(d)
    anchor=build_anchor_pairs(d,sets)
    anchor_pkg=fit_anchor_package(anchor)

    result={
        "analysis":"naamp_rainfall_pulse_timescale_v0_1",
        "contract":"NAAMP_RAINFALL_PULSE_TIMESCALE_CONTRACT_V0_1.json",
        "recency_bins":{
            "day0":"0 days since rain",
            "day1":"1 day",
            "days2_3":"2–3 days",
            "days4_7":"4–7 days",
            "days8plus":"8–180 days"
        },
        "run_level_richness_curve":run_level,
        "matched_dry_anchor_reassembly_curve":anchor_pkg,
        "interpretation_boundary":{
            "timescale":"Programme-reported rain recency, not rainfall amount or physiological recovery time.",
            "community":"Acoustically active community, not occupancy/abundance.",
            "status":"Post-opening ecological timescale extension with exposure bins frozen before outcome readback.",
            "causal_claim_authorized":False
        }
    }
    Path("NAAMP_RAINFALL_PULSE_TIMESCALE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
