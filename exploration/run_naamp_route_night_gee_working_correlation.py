#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.cov_struct import Exchangeable

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_ROUTE_NIGHT_GEE_WORKING_CORRELATION_RECEIPT_V0_1.json"

ANCHOR=0.75
EPS=1e-7

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

dep=loadmod("dep",EXP/"run_naamp_species_route_night_residual_dependence.py")
rain=dep.rain
flex=dep.flex
joint=dep.joint
uniform=dep.uniform

def build_cells():
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
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835:
        raise RuntimeError(f"weather subset drift {len(pw)} != 2835")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    ys=[]; offsets=[]; groups=[]; silent_flags=[]
    gid=0
    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)

        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        q=np.clip(q,EPS,1-EPS)
        y=dct["wet"].astype(float)
        silent=~dct["dry"].any(axis=1)

        for i in range(len(dct["species"])):
            ys.append(y[i].astype(float))
            offsets.append(uniform.logit(q[i]).astype(float))
            groups.append(np.repeat(gid,len(q[i])))
            silent_flags.append(np.repeat(bool(silent[i]),len(q[i])))
            gid+=1

    y=np.concatenate(ys)
    offset=np.concatenate(offsets)
    group=np.concatenate(groups).astype(int)
    silent=np.concatenate(silent_flags).astype(bool)

    if len(y)!=187690 or gid!=18769:
        raise RuntimeError(f"cell/cluster reproduction drift cells={len(y)} clusters={gid}")
    return y,offset,group,silent,pw,weather_sha

def fit_gee(y,offset,groups,label):
    exog=np.ones((len(y),1),float)
    model=GEE(
        endog=y,
        exog=exog,
        groups=groups,
        offset=offset,
        family=sm.families.Binomial(),
        cov_struct=Exchangeable()
    )
    fit=model.fit(maxiter=100)
    dep=float(np.asarray(fit.cov_struct.dep_params).reshape(-1)[0])
    return {
        "label":label,
        "n_cells":int(len(y)),
        "n_clusters":int(len(np.unique(groups))),
        "observed_positive_fraction":float(np.mean(y)),
        "intercept":float(fit.params[0]),
        "intercept_robust_se":float(fit.bse[0]),
        "working_correlation_alpha":dep,
        "converged":bool(getattr(fit,"converged",True)),
        "iterations":int(len(getattr(fit,"fit_history",{}).get("params",[]))) if hasattr(fit,"fit_history") else None
    }

def main():
    trigger=json.loads((EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json").read_text())
    if not trigger["residual_dependence"]["positive_dependence_supported"]:
        out={"analysis":"naamp_route_night_gee_working_correlation_v0_1","status":"not_run_trigger_not_met"}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    y,offset,groups,silent,pw,weather_sha=build_cells()
    all_fit=fit_gee(y,offset,groups,"all_species_route_nights")
    silent_fit=fit_gee(y[silent],offset[silent],groups[silent],"dry_route_silent")
    active_fit=fit_gee(y[~silent],offset[~silent],groups[~silent],"dry_route_active")

    out={
        "analysis":"naamp_route_night_gee_working_correlation_v0_1",
        "contract":"exploration/NAAMP_ROUTE_NIGHT_GEE_WORKING_CORRELATION_CONTRACT_V0_1.json",
        "status":"posthoc_method_corroboration_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "cells":int(len(y)),
            "clusters":int(len(np.unique(groups)))
        },
        "gee":{
            "all":all_fit,
            "dry_route_silent":silent_fit,
            "dry_route_active":active_fit
        },
        "comparison":{
            "custom_standardized_residual_dependence_D":float(trigger["residual_dependence"]["rho_resid"]),
            "note":"D and GEE alpha are different estimands; alpha is reported only as conventional correlated-replicate corroboration."
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "unique_lower_level_mechanism_identified":False,
            "occupancy_trend_reanalysis":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
