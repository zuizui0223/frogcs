#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_CROSSFIT_SPECIES_CALIBRATION_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840233
EPS=1e-7
MIN_CELLS=200
MIN_POS=20
MIN_NEG=20

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

def fit_offset_intercept(y,q):
    y=np.asarray(y,float)
    q=np.clip(np.asarray(q,float),EPS,1-EPS)
    eta=uniform.logit(q)
    target=float(y.sum())
    def score(b):
        return float(uniform.expit(eta+b).sum()-target)
    return float(brentq(score,-20.0,20.0,xtol=1e-10))

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

    q0=[]; folds=[]; wets=[]; drys=[]; species_lists=[]; obs_rows=[]
    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        q=detect.q_for_pair(p,dct,p_hist,pred_by_train)
        q0.append(q)
        folds.append(joint.fold_for_route(str(p.route_cluster)))
        wets.append(dct["wet"].astype(bool))
        drys.append(dct["dry"].astype(bool))
        species_lists.append(list(dct["species"]))
        obs_rows.append(flex.metrics(dct["wet"],dct["dry"]))

    train_y={"A":defaultdict(list),"B":defaultdict(list)}
    train_q={"A":defaultdict(list),"B":defaultdict(list)}
    for fold,species,wet,q in zip(folds,species_lists,wets,q0):
        for i,sp in enumerate(species):
            train_y[fold][sp].append(wet[i].astype(float))
            train_q[fold][sp].append(q[i].astype(float))

    calibration={"A":{},"B":{}}
    audit={"A":{},"B":{}}
    for fold in ("A","B"):
        for sp in all_species:
            ys=train_y[fold].get(sp,[])
            qs=train_q[fold].get(sp,[])
            y=np.concatenate(ys) if ys else np.asarray([],float)
            q=np.concatenate(qs) if qs else np.asarray([],float)
            n=int(len(y)); pos=int(y.sum()); neg=int(n-pos)
            ok=bool(n>=MIN_CELLS and pos>=MIN_POS and neg>=MIN_NEG)
            b=fit_offset_intercept(y,q) if ok else 0.0
            calibration[fold][sp]=float(b)
            audit[fold][sp]={
                "cells":n,"positive":pos,"negative":neg,
                "eligible":ok,"intercept":float(b)
            }

    qcal=[]
    for fold,species,q,dct in zip(folds,species_lists,q0,dw):
        train_fold="B" if fold=="A" else "A"
        b=np.asarray([calibration[train_fold].get(sp,0.0) for sp in species],float)
        pre=uniform.expit(uniform.logit(q)+b[:,None])
        qc=uniform.solve_shift(pre,dct["wet_k"])
        qcal.append(np.clip(qc,EPS,1-EPS))

    r,den=uniform.design_residual(pw)
    obs=(r[:,None]*np.asarray(obs_rows,float)).sum(axis=0)/den
    rng=np.random.default_rng(SEED)
    num=np.zeros((B,3),float)
    for i,(qc,dry) in enumerate(zip(qcal,drys)):
        w=rng.random((B,)+qc.shape)<qc[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dry)
    concentration=flex.conditional(num/den,obs)

    dependence=detect.bounded_test(qcal,dw,SEED+1)["dry_route_silent"]

    rng=np.random.default_rng(SEED+2)
    acc=lag.empty_acc()
    n_silent=0
    for qc,wet,dry in zip(qcal,wets,drys):
        for i in range(qc.shape[0]):
            if dry[i].sum()!=0:
                continue
            e=wet[i].astype(float)-qc[i]
            w=rng.random((B,10))<qc[i][None,:]
            esim=w.astype(float)-qc[i][None,:]
            lag.add_cluster(acc,e,esim)
            n_silent+=1
    far=lag.finalize_one(acc,"far")

    if (not concentration["above_upper_95"] and
        not dependence["positive_dependence_supported"] and
        not far["positive_dependence_supported"]):
        decision="species_miscalibration_sufficient"
    elif (concentration["above_upper_95"] and
          dependence["positive_dependence_supported"] and
          far["positive_dependence_supported"]):
        decision="residual_route_night_dependence_after_species_calibration"
    else:
        decision="mixed"

    out={
        "analysis":"naamp_crossfit_species_calibrated_common_environment_null_v0_1",
        "contract":"exploration/NAAMP_CROSSFIT_SPECIES_CALIBRATION_NULL_CONTRACT_V0_1.json",
        "status":"posthoc_miscalibration_falsification_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "dry_route_silent_clusters":int(n_silent)
        },
        "calibration_summary":{
            "fold_A_eligible_species":int(sum(v["eligible"] for v in audit["A"].values())),
            "fold_B_eligible_species":int(sum(v["eligible"] for v in audit["B"].values())),
            "fold_A_intercept_median":float(np.median([calibration["A"][s] for s in all_species])),
            "fold_B_intercept_median":float(np.median([calibration["B"][s] for s in all_species])),
            "fold_A_intercept_range":[float(min(calibration["A"].values())),float(max(calibration["A"].values()))],
            "fold_B_intercept_range":[float(min(calibration["B"].values())),float(max(calibration["B"].values()))]
        },
        "concentration":concentration,
        "dry_route_silent_bounded_dependence":dependence,
        "dry_route_silent_far_lag_7_9":far,
        "decision":decision,
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "constant_species_miscalibration_excluded_if_residual":True,
            "unique_lower_level_mechanism_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
