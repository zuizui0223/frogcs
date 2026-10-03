#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_ROUTE_NIGHT_DEPENDENCE_LAG_PROFILE_RECEIPT_V0_1.json"

B=1000
SEED=2840228
ANCHOR=0.75
EPS=1e-7
LAGS=tuple(range(1,10))

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

def empty_acc():
    return {
        d:{
            "obs_num":0.0,"obs_x2":0.0,"obs_y2":0.0,
            "null_num":np.zeros(B),"null_x2":np.zeros(B),"null_y2":np.zeros(B),
            "pair_count":0
        }
        for d in LAGS
    }

def add_cluster(acc,e,esim):
    # e: 10 ; esim: B x 10
    for d in LAGS:
        x=e[:-d]; y=e[d:]
        a=acc[d]
        a["obs_num"]+=float(np.sum(x*y))
        a["obs_x2"]+=float(np.sum(x*x))
        a["obs_y2"]+=float(np.sum(y*y))
        xs=esim[:,:-d]; ys=esim[:,d:]
        a["null_num"]+=np.sum(xs*ys,axis=1)
        a["null_x2"]+=np.sum(xs*xs,axis=1)
        a["null_y2"]+=np.sum(ys*ys,axis=1)
        a["pair_count"]+=int(len(x))

def finalize_one(acc,which):
    if which=="near":
        use=(1,2,3)
    elif which=="far":
        use=(7,8,9)
    else:
        use=(int(which),)

    on=sum(acc[d]["obs_num"] for d in use)
    ox=sum(acc[d]["obs_x2"] for d in use)
    oy=sum(acc[d]["obs_y2"] for d in use)
    nn=sum((acc[d]["null_num"] for d in use),np.zeros(B))
    nx=sum((acc[d]["null_x2"] for d in use),np.zeros(B))
    ny=sum((acc[d]["null_y2"] for d in use),np.zeros(B))

    if ox<=0 or oy<=0 or np.any(nx<=0) or np.any(ny<=0):
        raise RuntimeError(f"nonpositive denominator for {which}")

    obs=float(on/np.sqrt(ox*oy))
    null=nn/np.sqrt(nx*ny)
    lo,hi=np.quantile(null,[.025,.975])
    p=float((1+np.sum(null>=obs))/(B+1))
    return {
        "rho_lag":obs,
        "null_mean":float(np.mean(null)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_upper_tail_p":p,
        "positive_dependence_supported":bool(obs>hi and p<0.05),
        "ordered_pair_records":int(sum(acc[d]["pair_count"] for d in use))
    }

def finalize(acc):
    return {
        "lags":{str(d):finalize_one(acc,d) for d in LAGS},
        "near_lags_1_3":finalize_one(acc,"near"),
        "far_lags_7_9":finalize_one(acc,"far")
    }

def main():
    trigger=json.loads((EXP/"NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_RECEIPT_V0_1.json").read_text())
    if trigger.get("decision")!="residual_dependence_beyond_rain_amount_common_environment":
        out={"analysis":"naamp_route_night_dependence_lag_profile_v0_1","status":"not_run_trigger_not_met"}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

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

    rng=np.random.default_rng(SEED)
    acc_all=empty_acc()
    acc_silent=empty_acc()
    clusters_all=0
    clusters_silent=0

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

        for i in range(q.shape[0]):
            e=y[i]-q[i]
            w=rng.random((B,10))<q[i][None,:]
            esim=w.astype(float)-q[i][None,:]
            add_cluster(acc_all,e,esim)
            clusters_all+=1
            if dry[i].sum()==0:
                add_cluster(acc_silent,e,esim)
                clusters_silent+=1

    out={
        "analysis":"naamp_route_night_dependence_lag_profile_v0_1",
        "contract":"exploration/NAAMP_ROUTE_NIGHT_DEPENDENCE_LAG_PROFILE_CONTRACT_V0_1.json",
        "status":"posthoc_spatial_scale_diagnostic_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "all_clusters":int(clusters_all),
            "dry_route_silent_clusters":int(clusters_silent)
        },
        "dry_route_silent":finalize(acc_silent),
        "all_clusters":finalize(acc_all),
        "decision":{
            "dry_route_silent_far_scale_supported":bool(finalize(acc_silent)["far_lags_7_9"]["positive_dependence_supported"]),
            "all_cluster_far_scale_supported":bool(finalize(acc_all)["far_lags_7_9"]["positive_dependence_supported"])
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "stop_number_is_exact_geographic_distance":False,
            "social_facilitation_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
