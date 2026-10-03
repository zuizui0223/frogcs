#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.sandwich_covariance import cov_cluster

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_MONITORING_INDEPENDENCE_IMPACT_RECEIPT_V0_2.json"
Q=1.959963984540054

MIN_CELLS=200
MIN_POS=20
MIN_PAIRS=30
MIN_ROUTES=10

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

v1=loadmod("monitor_v1",EXP/"run_naamp_monitoring_independence_impact.py")
rain=v1.rain
flex=v1.flex

def term(beta,se):
    return {
        "beta":float(beta),
        "se":float(se),
        "ci95":[float(beta-Q*se),float(beta+Q*se)]
    }

def safe_cluster_se(fit,group,param_name):
    names=list(fit.params.index)
    j=names.index(param_name)
    cov=cov_cluster(fit,np.asarray(group),use_correction=True)
    v=float(cov[j,j])
    if not np.isfinite(v) or v<0:
        return None
    return float(np.sqrt(v))

def make_rows():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]

    if len(pw)!=2835:
        raise RuntimeError(f"weather subset drift {len(pw)} != 2835")

    rows=[]
    for p,dct in zip(pw.itertuples(index=False),dw):
        pair_id=f"{p.wet_RunID}|{p.dry_RunID}"
        route_cluster=str(p.route_cluster)
        dry=dct["dry"].astype(bool)
        wet=dct["wet"].astype(bool)
        for si,sp in enumerate(dct["species"]):
            js=np.flatnonzero(~dry[si])
            if not len(js):
                continue
            species_pair=f"{pair_id}|{sp}"
            for j in js:
                rows.append({
                    "wet_activation":int(wet[si,j]),
                    "rain_contrast":float(p.rain_contrast),
                    "temp_difference":float(p.temp_difference),
                    "doy_difference":float(p.doy_difference),
                    "year_gap":float(p.year_gap),
                    "State":str(p.State),
                    "RunNumber":str(p.RunNumber),
                    "species":str(sp),
                    "species_pair_cluster":species_pair,
                    "pair_cluster":pair_id,
                    "route_cluster":route_cluster
                })
    df=pd.DataFrame(rows)
    if len(df)<100000:
        raise RuntimeError(f"unexpectedly small risk set {len(df)}")
    return df,pw,weather_sha

def fit_pooled(df):
    formula=(
        "wet_activation ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber) + C(species)"
    )
    fit=smf.glm(formula,data=df,family=sm.families.Binomial()).fit(maxiter=200,disp=0)
    name="rain_contrast"
    beta=float(fit.params[name])
    iid=float(fit.bse[name])
    sp=safe_cluster_se(fit,df["species_pair_cluster"],name)
    pair=safe_cluster_se(fit,df["pair_cluster"],name)
    route=safe_cluster_se(fit,df["route_cluster"],name)
    if sp is None or pair is None or route is None:
        raise RuntimeError("invalid pooled clustered covariance")
    return {
        "formula":formula,
        "converged":bool(fit.converged),
        "iid":term(beta,iid),
        "species_pair_cluster":term(beta,sp),
        "route_pair_cluster":term(beta,pair),
        "route_cluster":term(beta,route),
        "ratios":{
            "species_pair_over_iid":float(sp/iid),
            "route_pair_over_iid":float(pair/iid),
            "route_over_iid":float(route/iid)
        }
    }

def fit_specieswise(df):
    out={}
    for sp,g in df.groupby("species",sort=True):
        n_cells=int(len(g))
        n_pos=int(g["wet_activation"].sum())
        n_pairs=int(g["pair_cluster"].nunique())
        n_routes=int(g["route_cluster"].nunique())
        eligible=(
            n_cells>=MIN_CELLS and n_pos>=MIN_POS and
            n_pairs>=MIN_PAIRS and n_routes>=MIN_ROUTES
        )
        rec={
            "risk_cells":n_cells,
            "positive_wet_cells":n_pos,
            "pair_clusters":n_pairs,
            "routes":n_routes,
            "eligible":bool(eligible),
            "estimable":False
        }
        if not eligible:
            out[sp]=rec
            continue

        formula=(
            "wet_activation ~ rain_contrast + temp_difference + doy_difference + "
            "year_gap + C(State) + C(RunNumber)"
        )
        try:
            fit=smf.glm(formula,data=g,family=sm.families.Binomial()).fit(maxiter=200,disp=0)
            if not bool(fit.converged) or "rain_contrast" not in fit.params:
                raise RuntimeError("nonconverged or missing rain term")
            beta=float(fit.params["rain_contrast"])
            iid=float(fit.bse["rain_contrast"])
            pair=safe_cluster_se(fit,g["pair_cluster"],"rain_contrast")
            route=safe_cluster_se(fit,g["route_cluster"],"rain_contrast")
            if not np.isfinite(iid) or iid<=0 or pair is None or route is None:
                raise RuntimeError("invalid covariance")
            rec.update({
                "estimable":True,
                "beta":beta,
                "iid_se":iid,
                "pair_cluster_se":pair,
                "route_cluster_se":route,
                "pair_over_iid":float(pair/iid),
                "route_over_iid":float(route/iid)
            })
        except Exception as e:
            rec["failure"]=type(e).__name__+":"+str(e)[:200]
        out[sp]=rec
    return out

def summarize_specieswise(records):
    est=[v for v in records.values() if v.get("estimable")]
    eligible=[v for v in records.values() if v.get("eligible")]
    def summarize(key):
        vals=np.asarray([float(v[key]) for v in est],float)
        if not len(vals):
            return None
        return {
            "median":float(np.median(vals)),
            "iqr":[float(np.quantile(vals,.25)),float(np.quantile(vals,.75))],
            "min":float(np.min(vals)),
            "max":float(np.max(vals)),
            "fraction_gt_1":float(np.mean(vals>1.0)),
            "n_gt_1":int(np.sum(vals>1.0))
        }
    return {
        "eligible_species":int(len(eligible)),
        "estimable_species":int(len(est)),
        "pair_cluster_over_iid":summarize("pair_over_iid"),
        "route_cluster_over_iid":summarize("route_over_iid")
    }

def main():
    df,pw,weather_sha=make_rows()
    pooled=fit_pooled(df)
    species_records=fit_specieswise(df)
    species_summary=summarize_specieswise(species_records)

    pair_summary=species_summary["pair_cluster_over_iid"]
    route_summary=species_summary["route_cluster_over_iid"]
    broad_pair=bool(
        pair_summary is not None and pair_summary["median"]>1 and
        pair_summary["fraction_gt_1"]>0.5
    )
    broad_route=bool(
        route_summary is not None and route_summary["median"]>1 and
        route_summary["fraction_gt_1"]>0.5
    )

    out={
        "analysis":"naamp_monitoring_independence_impact_v0_2",
        "contract":"exploration/NAAMP_MONITORING_INDEPENDENCE_IMPACT_CONTRACT_V0_2.json",
        "status":"posthoc_extension_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "risk_set_species_stop_cells":int(len(df)),
            "species":int(df.species.nunique()),
            "pair_clusters":int(df.pair_cluster.nunique()),
            "species_pair_clusters":int(df.species_pair_cluster.nunique())
        },
        "pooled":pooled,
        "specieswise":{
            "eligibility_thresholds":{
                "minimum_risk_cells":MIN_CELLS,
                "minimum_positive_wet_cells":MIN_POS,
                "minimum_species_pair_clusters":MIN_PAIRS,
                "minimum_routes":MIN_ROUTES
            },
            "summary":species_summary,
            "records":species_records
        },
        "decision":{
            "specieswise_pair_cluster_inflation_broad":broad_pair,
            "specieswise_route_cluster_inflation_broad":broad_route,
            "pooled_route_cluster_exceeds_iid":bool(pooled["ratios"]["route_over_iid"]>1)
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "exact_published_occupancy_estimator":False,
            "universal_monitoring_model_claim":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
