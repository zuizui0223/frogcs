#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SPECIES_ROUTE_NIGHT_DRY_STATE_DECOMPOSITION_RECEIPT_V0_1.json"

B=1000
SEED=2840226
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

def group_num_den(y,q,mask):
    if not np.any(mask):
        return 0.0,0.0
    yy=np.asarray(y,float)[mask]
    qq=np.asarray(q,float)[mask]
    e=yy-qq
    s=e.sum(axis=1)
    ss=(e*e).sum(axis=1)
    num=float(np.sum((s*s-ss)/2.0))
    v=np.clip(qq*(1.0-qq),EPS,None)
    z=np.sqrt(v)
    zs=z.sum(axis=1)
    zss=(z*z).sum(axis=1)
    den=float(np.sum((zs*zs-zss)/2.0))
    return num,den

def sim_group_num(w,q,mask):
    if not np.any(mask):
        return np.zeros(w.shape[0],float)
    ww=w[:,mask,:]
    qq=np.asarray(q,float)[mask]
    e=ww.astype(float)-qq[None,:,:]
    s=e.sum(axis=2)
    ss=(e*e).sum(axis=2)
    return ((s*s-ss)/2.0).sum(axis=1)

def summarize(obs_num,den,null_num):
    if den<=0:
        return {"estimable":False}
    rho=float(obs_num/den)
    null_rho=np.asarray(null_num,float)/den
    lo,hi=np.quantile(null_rho,[.025,.975])
    p=float((1+np.sum(null_rho>=rho))/(len(null_rho)+1))
    return {
        "estimable":True,
        "rho_resid":rho,
        "null_mean":float(np.mean(null_rho)),
        "null_ci95":[float(lo),float(hi)],
        "plus_one_upper_tail_p":p,
        "positive_dependence_supported":bool(rho>hi and p<0.05)
    }

def main():
    trigger=json.loads((EXP/"NAAMP_SPECIES_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json").read_text())
    if not trigger["residual_dependence"]["positive_dependence_supported"]:
        out={"analysis":"naamp_species_route_night_residual_dependence_dry_state_decomposition_v0_1","status":"not_run_trigger_not_met"}
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)

    mask_weather=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask_weather)
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
    strata={
        "dry_route_silent":{"obs_num":0.0,"den":0.0,"null_num":np.zeros(B,float),"clusters":0,"cells":0,"positive_wet_clusters":0},
        "dry_route_active":{"obs_num":0.0,"den":0.0,"null_num":np.zeros(B,float),"clusters":0,"cells":0,"positive_wet_clusters":0}
    }

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID)
        dry_id=str(p.dry_RunID)
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
        w=rng.random((B,)+q.shape)<q[None,:,:]

        silent=~dct["dry"].any(axis=1)
        active=~silent
        for name,m in [("dry_route_silent",silent),("dry_route_active",active)]:
            n,d=group_num_den(y,q,m)
            strata[name]["obs_num"]+=n
            strata[name]["den"]+=d
            strata[name]["null_num"]+=sim_group_num(w,q,m)
            strata[name]["clusters"]+=int(np.sum(m))
            strata[name]["cells"]+=int(np.sum(m)*q.shape[1])
            strata[name]["positive_wet_clusters"]+=int(np.sum(y[m].sum(axis=1)>0)) if np.any(m) else 0

    out_strata={}
    for name,s in strata.items():
        z=summarize(s["obs_num"],s["den"],s["null_num"])
        z.update({
            "species_route_night_clusters":int(s["clusters"]),
            "species_stop_cells":int(s["cells"]),
            "clusters_with_at_least_one_wet_positive_stop":int(s["positive_wet_clusters"])
        })
        out_strata[name]=z

    out={
        "analysis":"naamp_species_route_night_residual_dependence_dry_state_decomposition_v0_1",
        "contract":"exploration/NAAMP_SPECIES_ROUTE_NIGHT_DRY_STATE_DECOMPOSITION_CONTRACT_V0_1.json",
        "status":"posthoc_linkage_audit_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "states":int(pw.State.nunique())
        },
        "strata":out_strata,
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "dry_acoustic_silence_equals_biological_absence":False,
            "unique_lower_level_mechanism_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
