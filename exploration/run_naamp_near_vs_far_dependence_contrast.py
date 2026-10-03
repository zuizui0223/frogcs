#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_NEAR_VS_FAR_DEPENDENCE_CONTRAST_RECEIPT_V0_1.json"

B=2000
SEED=2840237
ANCHOR=0.75
EPS=1e-7
OBS_NEAR=0.29643298821548375
OBS_FAR=0.27178236785618926

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

rain=loadmod("rain_amount_common",EXP/"run_naamp_rain_amount_common_environment_null.py")
flex=rain.flex
joint=rain.joint
uniform=rain.uniform

def add_stats(z,e,lags):
    for d in lags:
        x=e[:-d]; y=e[d:]
        z[0]+=float(np.sum(x*y))
        z[1]+=float(np.sum(x*x))
        z[2]+=float(np.sum(y*y))

def rho(z):
    return float(z[0]/np.sqrt(z[1]*z[2]))

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

    route_stats=defaultdict(lambda:{
        "near":np.zeros(3,float),
        "far":np.zeros(3,float),
        "clusters":0
    })

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)
        dry=dct["dry"].astype(bool)
        wet=dct["wet"].astype(bool)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry.astype(float)
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=np.clip(uniform.solve_shift(pre,dct["wet_k"]),EPS,1-EPS)

        z=route_stats[str(p.route_cluster)]
        for i in range(q.shape[0]):
            if dry[i].sum()!=0:
                continue
            e=wet[i].astype(float)-q[i]
            add_stats(z["near"],e,(1,2,3))
            add_stats(z["far"],e,(7,8,9))
            z["clusters"]+=1

    routes=sorted(route_stats)
    near_mat=np.asarray([route_stats[r]["near"] for r in routes],float)
    far_mat=np.asarray([route_stats[r]["far"] for r in routes],float)
    clusters=np.asarray([route_stats[r]["clusters"] for r in routes],int)
    if len(routes)!=428 or int(clusters.sum())!=8343:
        raise RuntimeError(f"route/cluster drift routes={len(routes)} clusters={clusters.sum()}")

    near_obs=rho(near_mat.sum(axis=0))
    far_obs=rho(far_mat.sum(axis=0))
    if abs(near_obs-OBS_NEAR)>1e-10 or abs(far_obs-OBS_FAR)>1e-10:
        raise RuntimeError(f"lag reproduction drift near={near_obs} far={far_obs}")

    rng=np.random.default_rng(SEED)
    diff=np.empty(B,float)
    near_boot=np.empty(B,float)
    far_boot=np.empty(B,float)
    n=len(routes)
    for b in range(B):
        take=rng.integers(0,n,size=n)
        nb=near_mat[take].sum(axis=0)
        fb=far_mat[take].sum(axis=0)
        near_boot[b]=rho(nb)
        far_boot[b]=rho(fb)
        diff[b]=near_boot[b]-far_boot[b]

    obs_diff=float(near_obs-far_obs)
    lo,hi=np.quantile(diff,[.025,.975])
    p_lo=float((1+np.sum(diff<=0))/(B+1))
    p_hi=float((1+np.sum(diff>=0))/(B+1))
    p_two=float(min(1.0,2.0*min(p_lo,p_hi)))

    out={
        "analysis":"naamp_near_vs_far_route_dependence_contrast_v0_1",
        "contract":"exploration/NAAMP_NEAR_VS_FAR_DEPENDENCE_CONTRAST_CONTRACT_V0_1.json",
        "status":"posthoc_spatial_decay_contrast_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(len(routes)),
            "dry_route_silent_clusters":int(clusters.sum())
        },
        "observed":{
            "near_lags_1_3":near_obs,
            "far_lags_7_9":far_obs,
            "near_minus_far":obs_diff,
            "far_over_near":float(far_obs/near_obs)
        },
        "route_cluster_bootstrap":{
            "replicates":B,
            "seed":SEED,
            "near_minus_far_mean":float(np.mean(diff)),
            "near_minus_far_ci95":[float(lo),float(hi)],
            "two_sided_sign_p":p_two,
            "near_ci95":[float(x) for x in np.quantile(near_boot,[.025,.975])],
            "far_ci95":[float(x) for x in np.quantile(far_boot,[.025,.975])]
        },
        "decision":{
            "detectable_near_to_far_decay":bool(lo>0),
            "far_scale_remains_positive":bool(far_obs>0)
        },
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "stop_number_is_exact_distance":False,
            "survey_order_confounded_with_route_topology":True,
            "local_social_propagation_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
