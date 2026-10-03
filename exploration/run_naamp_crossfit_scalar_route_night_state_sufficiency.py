#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_CROSSFIT_SCALAR_ROUTE_NIGHT_STATE_SUFFICIENCY_RECEIPT_V0_1.json"

B=1000
CONC_SEED=2840234
LAG_SEED=2840235
ANCHOR=0.75
EPS=1e-7

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

rain=loadmod("rain_amount_common",EXP/"run_naamp_rain_amount_common_environment_null.py")
latent=loadmod("latent_state",EXP/"run_naamp_logistic_normal_route_night_state.py")
flex=rain.flex
joint=rain.joint
uniform=rain.uniform

def q_for_pair(p,dct,p_hist,pred_by_train):
    test_fold=joint.fold_for_route(str(p.route_cluster))
    train_fold="B" if test_fold=="A" else "A"
    pred=pred_by_train[train_fold]
    delta=np.asarray([
        pred[str(p.wet_RunID)].get(sp,0.0)-pred[str(p.dry_RunID)].get(sp,0.0)
        for sp in dct["species"]
    ],float)
    dry=dct["dry"].astype(float)
    p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
    p_anchor=np.clip(p_anchor,EPS,1-EPS)
    pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
    q=uniform.solve_shift(pre,dct["wet_k"])
    return np.clip(q,EPS,1-EPS)

def metric_rows_from_silent(w):
    # Every supplied species row is dry-route silent.
    route_new=w.any(axis=2)
    k=w.sum(axis=2).astype(float)
    extra=np.maximum(k-1.0,0.0)*route_new
    concentration=extra*np.maximum(extra-1.0,0.0)/2.0
    return np.column_stack([
        route_new.sum(axis=1).astype(float),
        extra.sum(axis=1).astype(float),
        concentration.sum(axis=1).astype(float),
    ])

def lag_add_observed(acc,e,lags):
    for d in lags:
        x=e[:,:-d]; y=e[:,d:]
        acc["num"]+=float(np.sum(x*y))
        acc["x2"]+=float(np.sum(x*x))
        acc["y2"]+=float(np.sum(y*y))

def lag_add_sim(acc,e,lags):
    # e is B x species x 10
    for d in lags:
        x=e[:,:,:-d]; y=e[:,:,d:]
        acc["num"]+=np.sum(x*y,axis=(1,2))
        acc["x2"]+=np.sum(x*x,axis=(1,2))
        acc["y2"]+=np.sum(y*y,axis=(1,2))

def finish_lag(obs_acc,sim_acc):
    obs=float(obs_acc["num"]/np.sqrt(obs_acc["x2"]*obs_acc["y2"]))
    sim=sim_acc["num"]/np.sqrt(sim_acc["x2"]*sim_acc["y2"])
    lo,hi=np.quantile(sim,[.025,.975])
    return {
        "observed_rho_lag":obs,
        "scalar_generator_mean":float(np.mean(sim)),
        "scalar_generator_ci95":[float(lo),float(hi)],
        "observed_inside_predictive_ci":bool(lo<=obs<=hi)
    }

def main():
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
    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    pairs=[]
    train_y={"A":[],"B":[]}
    train_eta={"A":[],"B":[]}
    obs_rows=[]
    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        q=q_for_pair(p,dct,p_hist,pred_by_train)
        wet=dct["wet"].astype(bool)
        dry=dct["dry"].astype(bool)
        silent=(dry.sum(axis=1)==0)
        fold=joint.fold_for_route(str(p.route_cluster))
        if np.any(silent):
            train_y[fold].append(wet[silent].astype(float))
            train_eta[fold].append(uniform.logit(q[silent]))
        pairs.append({
            "q":q,
            "wet":wet,
            "dry":dry,
            "silent":silent,
            "fold":fold
        })
        obs_rows.append(flex.metrics(wet,dry))

    fit={}
    for fold in ("A","B"):
        y=np.vstack(train_y[fold])
        eta=np.vstack(train_eta[fold])
        fit[fold]=latent.fit_stratum(y,eta)

    r,den=uniform.design_residual(pw)
    obs=np.sum(r[:,None]*np.asarray(obs_rows,float),axis=0)/den

    rng_conc=np.random.default_rng(CONC_SEED)
    rng_lag=np.random.default_rng(LAG_SEED)
    numer=np.zeros((B,3),float)

    obs_near={"num":0.0,"x2":0.0,"y2":0.0}
    obs_far={"num":0.0,"x2":0.0,"y2":0.0}
    sim_near={"num":np.zeros(B),"x2":np.zeros(B),"y2":np.zeros(B)}
    sim_far={"num":np.zeros(B),"x2":np.zeros(B),"y2":np.zeros(B)}

    silent_clusters=0
    for i,z in enumerate(pairs):
        silent=z["silent"]
        if not np.any(silent):
            continue
        q=z["q"][silent]
        wet=z["wet"][silent].astype(float)
        silent_clusters+=int(q.shape[0])

        train_fold="B" if z["fold"]=="A" else "A"
        mu=float(fit[train_fold]["mu_hat"])
        sigma=float(fit[train_fold]["sigma_hat"])

        # Concentration generator.
        u=rng_conc.normal(loc=0.0,scale=sigma,size=(B,q.shape[0]))
        p=uniform.expit(uniform.logit(q)[None,:,:]+mu+u[:,:,None])
        w=rng_conc.random(p.shape)<p
        numer+=r[i]*metric_rows_from_silent(w)

        # Separate RNG for lag predictive distribution.
        ul=rng_lag.normal(loc=0.0,scale=sigma,size=(B,q.shape[0]))
        pl=uniform.expit(uniform.logit(q)[None,:,:]+mu+ul[:,:,None])
        wl=rng_lag.random(pl.shape)<pl
        esim=wl.astype(float)-q[None,:,:]
        eobs=wet-q
        lag_add_observed(obs_near,eobs,(1,2,3))
        lag_add_observed(obs_far,eobs,(7,8,9))
        lag_add_sim(sim_near,esim,(1,2,3))
        lag_add_sim(sim_far,esim,(7,8,9))

    sim=numer/den
    concentration=flex.conditional(sim,obs)
    near=finish_lag(obs_near,sim_near)
    far=finish_lag(obs_far,sim_far)

    out={
        "analysis":"naamp_crossfit_scalar_route_night_state_sufficiency_v0_1",
        "contract":"exploration/NAAMP_CROSSFIT_SCALAR_ROUTE_NIGHT_STATE_SUFFICIENCY_CONTRACT_V0_1.json",
        "status":"posthoc_crossfit_structural_sufficiency",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "dry_route_silent_clusters":int(silent_clusters),
            "routes_by_fold":{
                "A":int(pw.loc[pw.route_cluster.astype(str).map(joint.fold_for_route)=="A","route_cluster"].nunique()),
                "B":int(pw.loc[pw.route_cluster.astype(str).map(joint.fold_for_route)=="B","route_cluster"].nunique())
            }
        },
        "crossfit_latent_training":{
            "fold_A":fit["A"],
            "fold_B":fit["B"]
        },
        "observed":{
            "route_new_taxon_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "concentration_beta":float(obs[2])
        },
        "scalar_state_concentration":concentration,
        "scalar_state_lag_profile":{
            "near_lags_1_3":near,
            "far_lags_7_9":far
        },
        "decision":{
            "concentration_structurally_sufficient":bool(not concentration["above_upper_95"] and concentration["observed_conditional_residual"]>=concentration["null_residual_ci95"][0]),
            "far_lag_structurally_sufficient":bool(far["observed_inside_predictive_ci"]),
            "both_endpoints_structurally_sufficient":bool(
                (not concentration["above_upper_95"] and concentration["observed_conditional_residual"]>=concentration["null_residual_ci95"][0])
                and far["observed_inside_predictive_ci"]
            )
        },
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "route_crossfit_latent_distribution":True,
            "independent_external_confirmation":False,
            "unique_lower_level_mechanism_identified":False,
            "pair_total_retuned_after_latent_draw":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
