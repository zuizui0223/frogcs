#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_CROSSFIT_LATENT_ROUTE_NIGHT_GENERATOR_RECEIPT_V0_1.json"

B=1000
SEED=2840232
ANCHOR=0.75
EPS=1e-7
OBS_RHO=0.28487700425848284
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
latent=loadmod("latent_state",EXP/"run_naamp_logistic_normal_route_night_state.py")

def bounded_terms_sim(w,q):
    e=w.astype(float)-q[None,:]
    s=e.sum(axis=1)
    ss=np.sum(e*e,axis=1)
    return s*s-ss,9.0*ss

def lag_far_terms_sim(w,q):
    e=w.astype(float)-q[None,:]
    num=np.zeros(len(w),float)
    x2=np.zeros(len(w),float)
    y2=np.zeros(len(w),float)
    for d in (7,8,9):
        x=e[:,:-d]
        y=e[:,d:]
        num+=np.sum(x*y,axis=1)
        x2+=np.sum(x*x,axis=1)
        y2+=np.sum(y*y,axis=1)
    return num,x2,y2

def observed_bounded_and_far(q_list,wets,drys):
    on=od=0.0
    far_num=far_x2=far_y2=0.0
    clusters=0
    for q,wet,dry in zip(q_list,wets,drys):
        for i in range(q.shape[0]):
            if dry[i].sum()!=0:
                continue
            e=wet[i].astype(float)-q[i]
            s=float(e.sum())
            ss=float(np.sum(e*e))
            on+=s*s-ss
            od+=9.0*ss
            for d in (7,8,9):
                x=e[:-d]; y=e[d:]
                far_num+=float(np.sum(x*y))
                far_x2+=float(np.sum(x*x))
                far_y2+=float(np.sum(y*y))
            clusters+=1
    return {
        "clusters":clusters,
        "rho_bounded":float(on/od),
        "far_lag_7_9":float(far_num/np.sqrt(far_x2*far_y2))
    }

def central_interval(x):
    lo,hi=np.quantile(np.asarray(x,float),[.025,.975])
    return [float(lo),float(hi)]

def main():
    trigger=json.loads((EXP/"NAAMP_LOGISTIC_NORMAL_ROUTE_NIGHT_STATE_RECEIPT_V0_1.json").read_text())
    if trigger.get("status")!="posthoc_latent_state_magnitude_triggered":
        out={"analysis":"naamp_crossfit_latent_route_night_state_generator_v0_1","status":"not_run_trigger_not_met"}
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
    if len(pw)!=2835 or pw.route_cluster.nunique()!=428:
        raise RuntimeError(f"weather subset drift: pairs={len(pw)} routes={pw.route_cluster.nunique()}")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    q_list=[]
    wets=[]
    drys=[]
    folds=[]
    obs_rows=[]
    train_y={"A":[],"B":[]}
    train_eta={"A":[],"B":[]}
    silent_cluster_counts={"A":0,"B":0}

    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
        route_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold_for_q="B" if route_fold=="A" else "A"
        pred=pred_by_train[train_fold_for_q]
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
        q=uniform.solve_shift(pre,dct["wet_k"])
        q=np.clip(q,EPS,1-EPS)

        q_list.append(q)
        wets.append(wet)
        drys.append(dry)
        folds.append(route_fold)
        obs_rows.append(flex.metrics(wet,dry))

        silent=(dry.sum(axis=1)==0)
        if np.any(silent):
            train_y[route_fold].append(wet[silent].astype(float))
            train_eta[route_fold].append(uniform.logit(q[silent]))
            silent_cluster_counts[route_fold]+=int(np.sum(silent))

    # Fit latent-state magnitude separately within each route fold.
    fold_fit={}
    for fold in ("A","B"):
        y=np.vstack(train_y[fold])
        eta=np.vstack(train_eta[fold])
        fold_fit[fold]=latent.fit_stratum(y,eta)

    # Reproduce observed summary from the exact fixed q matrices.
    observed_dep=observed_bounded_and_far(q_list,wets,drys)
    if abs(observed_dep["rho_bounded"]-OBS_RHO)>1e-10:
        raise RuntimeError(f"bounded rho reproduction drift: {observed_dep['rho_bounded']}")
    if abs(observed_dep["far_lag_7_9"]-OBS_FAR)>1e-10:
        raise RuntimeError(f"far-lag reproduction drift: {observed_dep['far_lag_7_9']}")

    r,den=uniform.design_residual(pw)
    obs=(r[:,None]*np.asarray(obs_rows,float)).sum(axis=0)/den

    rng=np.random.default_rng(SEED)
    numer=np.zeros((B,3),float)
    dep_num=np.zeros(B,float)
    dep_den=np.zeros(B,float)
    far_num=np.zeros(B,float)
    far_x2=np.zeros(B,float)
    far_y2=np.zeros(B,float)

    for pair_i,(p,q,wet,dry,route_fold) in enumerate(zip(pw.itertuples(index=False),q_list,wets,drys,folds)):
        training_fold="B" if route_fold=="A" else "A"
        pars=fold_fit[training_fold]
        mu=float(pars["mu_hat"])
        sigma=float(pars["sigma_hat"])

        ns=q.shape[0]
        wsim=np.empty((B,ns,10),dtype=bool)
        for i in range(ns):
            if dry[i].sum()==0:
                u=rng.normal(0.0,sigma,size=B)
                eta=uniform.logit(q[i])[None,:]+mu+u[:,None]
                p_lat=uniform.expit(eta)
                w=rng.random((B,10))<p_lat
                wsim[:,i,:]=w

                nn,nd=bounded_terms_sim(w,q[i])
                dep_num+=nn
                dep_den+=nd
                fn,fx,fy=lag_far_terms_sim(w,q[i])
                far_num+=fn
                far_x2+=fx
                far_y2+=fy
            else:
                wsim[:,i,:]=rng.random((B,10))<q[i][None,:]

        numer+=r[pair_i]*flex.sim_metrics(wsim,dry)

    sim=numer/den

    # Same conditional concentration regression as the principal comparator.
    X=np.column_stack([np.ones(B),sim[:,0],sim[:,1]])
    y=sim[:,2]
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef
    resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0]+coef[2]*obs[1])
    obs_resid=float(obs[2]-obs_pred)
    conc_ci=central_interval(resid)
    conc_pass=bool(conc_ci[0] <= obs_resid <= conc_ci[1])

    rho_sim=dep_num/dep_den
    far_sim=far_num/np.sqrt(far_x2*far_y2)
    rho_ci=central_interval(rho_sim)
    far_ci=central_interval(far_sim)
    rho_pass=bool(rho_ci[0] <= OBS_RHO <= rho_ci[1])
    far_pass=bool(far_ci[0] <= OBS_FAR <= far_ci[1])

    n_pass=sum([conc_pass,rho_pass,far_pass])
    if n_pass==3:
        decision="route_transferable_shared_state_generator"
    elif n_pass==0:
        decision="insufficient_generator"
    else:
        decision="partial_generator"

    out={
        "analysis":"naamp_crossfit_latent_route_night_state_generator_v0_1",
        "contract":"exploration/NAAMP_CROSSFIT_LATENT_ROUTE_NIGHT_GENERATOR_CONTRACT_V0_1.json",
        "status":"posthoc_crossfit_generator_test_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "dry_route_silent_clusters_by_route_fold":silent_cluster_counts
        },
        "latent_state_training":{
            "fold_A":fold_fit["A"],
            "fold_B":fold_fit["B"],
            "application_rule":"Each focal route uses mu/sigma from the opposite deterministic route fold."
        },
        "observed":{
            "route_new_species_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "concentration_beta":float(obs[2]),
            "dry_route_silent_rho_bounded":float(observed_dep["rho_bounded"]),
            "dry_route_silent_far_lag_7_9":float(observed_dep["far_lag_7_9"])
        },
        "generator_checks":{
            "concentration":{
                "predicted_concentration_beta":obs_pred,
                "observed_conditional_residual":obs_resid,
                "generator_residual_ci95":conc_ci,
                "observed_within_generator_ci95":conc_pass,
                "generator_residual_mean":float(np.mean(resid))
            },
            "bounded_dependence":{
                "observed":OBS_RHO,
                "generator_mean":float(np.mean(rho_sim)),
                "generator_ci95":rho_ci,
                "observed_within_generator_ci95":rho_pass
            },
            "far_lag_7_9":{
                "observed":OBS_FAR,
                "generator_mean":float(np.mean(far_sim)),
                "generator_ci95":far_ci,
                "observed_within_generator_ci95":far_pass
            }
        },
        "decision":decision,
        "weather_provenance":{"era5_antecedent_amount_sha256":weather_sha},
        "interpretation_boundary":{
            "statistical_process_sufficiency_not_unique_biological_mechanism":True,
            "independent_confirmation":False,
            "social_facilitation_identified":False,
            "hydrological_causality_identified":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
