#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_LOTO_STOP_NIGHT_HOTNESS_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840235
EPS=1e-7
LAMBDA=1.0
MIN_OTHER=3

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

detect=loadmod("detect_aug",EXP/"run_naamp_detection_augmented_common_environment_null.py")
rain=detect.rain
flex=detect.flex
joint=detect.joint
uniform=detect.uniform
lag=loadmod("lag_profile",EXP/"run_naamp_route_night_dependence_lag_profile.py")

def penalized_delta(y,q):
    y=np.asarray(y,float)
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    eta=uniform.logit(q)
    def obj(delta):
        z=eta+float(delta)
        ll=float(np.sum(y*z-np.logaddexp(0.0,z)))
        return -ll+0.5*LAMBDA*float(delta)**2
    fit=minimize_scalar(obj,bounds=(-5.0,5.0),method="bounded",
                        options={"xatol":1e-6,"maxiter":100})
    if not fit.success or not np.isfinite(fit.x):
        raise RuntimeError("stop-night penalized intercept optimization failed")
    return float(fit.x)

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)
    keep=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(keep)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835 or pw.route_cluster.nunique()!=428:
        raise RuntimeError("weather/history coverage drift")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[
        weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)
    ]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    q_base=[]; q_hot=[]; wets=[]; drys=[]; obs_rows=[]
    deltas=[]; fallback_cells=0; total_cells=0
    stop_rmse_before=[]; stop_rmse_after=[]

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        q0=detect.q_for_pair(p,dct,p_hist,pred_by_train)
        wet=dct["wet"].astype(bool)
        dry=dct["dry"].astype(bool)
        S=q0.shape[0]
        qstar=np.empty_like(q0,float)

        for i in range(S):
            others=np.asarray([k for k in range(S) if k!=i],int)
            for j in range(10):
                total_cells+=1
                if len(others)<MIN_OTHER:
                    delta=0.0
                    fallback_cells+=1
                else:
                    delta=penalized_delta(wet[others,j].astype(float),q0[others,j])
                deltas.append(delta)
                qstar[i,j]=uniform.expit(uniform.logit(q0[i,j])+delta)

        # Preserve the same observed total wet incidence magnitude.
        qstar=uniform.solve_shift(np.clip(qstar,EPS,1-EPS),dct["wet_k"])
        qstar=np.clip(qstar,EPS,1-EPS)

        obs_stop=wet.sum(axis=0).astype(float)
        stop_rmse_before.append(float(np.sqrt(np.mean((obs_stop-q0.sum(axis=0))**2))))
        stop_rmse_after.append(float(np.sqrt(np.mean((obs_stop-qstar.sum(axis=0))**2))))

        q_base.append(q0); q_hot.append(qstar)
        wets.append(wet); drys.append(dry)
        obs_rows.append(flex.metrics(wet,dry))

    r,den=uniform.design_residual(pw)
    obs=(r[:,None]*np.asarray(obs_rows,float)).sum(axis=0)/den

    rng=np.random.default_rng(SEED)
    num=np.zeros((B,3),float)
    for i,(q,dry) in enumerate(zip(q_hot,drys)):
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dry)
    concentration=flex.conditional(num/den,obs)

    dep=detect.bounded_test(q_hot,dw,SEED+1)["dry_route_silent"]

    rng=np.random.default_rng(SEED+2)
    acc=lag.empty_acc()
    n_silent=0
    for q,wet,dry in zip(q_hot,wets,drys):
        for i in range(q.shape[0]):
            if dry[i].sum()!=0:
                continue
            e=wet[i].astype(float)-q[i]
            w=rng.random((B,10))<q[i][None,:]
            esim=w.astype(float)-q[i][None,:]
            lag.add_cluster(acc,e,esim)
            n_silent+=1
    far=lag.finalize_one(acc,"far")

    if (not concentration["above_upper_95"] and
        not dep["positive_dependence_supported"] and
        not far["positive_dependence_supported"]):
        decision="stop_night_hotness_sufficient"
    elif (concentration["above_upper_95"] and
          dep["positive_dependence_supported"] and
          far["positive_dependence_supported"]):
        decision="residual_species_route_night_structure"
    else:
        decision="mixed"

    da=np.asarray(deltas,float)
    out={
        "analysis":"naamp_leave_one_taxon_out_stop_night_hotness_null_v0_1",
        "contract":"exploration/NAAMP_LOTO_STOP_NIGHT_HOTNESS_NULL_CONTRACT_V0_1.json",
        "status":"posthoc_cross_taxon_common_cause_falsification_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "dry_route_silent_clusters":int(n_silent),
            "target_species_stop_cells":int(total_cells),
            "fallback_cells_lt3_other_taxa":int(fallback_cells)
        },
        "hotness_audit":{
            "ridge_lambda":LAMBDA,
            "delta_median":float(np.median(da)),
            "delta_iqr":[float(np.quantile(da,.25)),float(np.quantile(da,.75))],
            "delta_abs_q95":float(np.quantile(np.abs(da),.95)),
            "mean_stop_richness_rmse_before":float(np.mean(stop_rmse_before)),
            "mean_stop_richness_rmse_after":float(np.mean(stop_rmse_after))
        },
        "concentration":concentration,
        "dry_route_silent_bounded_dependence":dep,
        "dry_route_silent_far_lag_7_9":far,
        "decision":decision,
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "target_taxon_wet_outcome_used_to_estimate_own_stop_hotness":False,
            "other_taxa_same_wet_survey_used":True,
            "independent_prediction":False,
            "specific_stop_night_driver_identified":False,
            "unique_lower_level_mechanism_identified":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
