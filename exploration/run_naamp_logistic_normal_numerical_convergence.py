#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_LOGISTIC_NORMAL_NUMERICAL_CONVERGENCE_RECEIPT_V0_1.json"

ANCHOR=0.75
EPS=1e-7
NODES=(10,20,40,60)
SIGMA_BOUNDS=(0.0,5.0)
MU_BOUNDS=(-5.0,5.0)

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

def fit_one(y,eta,nodes):
    gh_x,gh_w=hermgauss(int(nodes))
    log_w=np.log(gh_w)-0.5*np.log(np.pi)
    y=np.asarray(y,float); eta=np.asarray(eta,float)

    def ll(mu,sigma):
        shifts=np.sqrt(2.0)*float(sigma)*gh_x+float(mu)
        node_ll=np.empty((len(y),len(gh_x)),float)
        for h,shift in enumerate(shifts):
            z=eta+shift
            node_ll[:,h]=np.sum(y*z-np.logaddexp(0.0,z),axis=1)
        return float(np.sum(logsumexp(node_ll+log_w[None,:],axis=1)))

    cache={}
    def profile(sigma):
        sigma=float(sigma)
        key=round(sigma,10)
        if key in cache:
            return cache[key]
        fit_mu=minimize_scalar(
            lambda mu:-ll(mu,sigma),
            bounds=MU_BOUNDS,method="bounded",
            options={"xatol":1e-5,"maxiter":200}
        )
        if not fit_mu.success:
            raise RuntimeError(f"mu optimization failed nodes={nodes} sigma={sigma}")
        out=(float(-fit_mu.fun),float(fit_mu.x))
        cache[key]=out
        return out

    fit_sig=minimize_scalar(
        lambda s:-profile(float(s))[0],
        bounds=SIGMA_BOUNDS,method="bounded",
        options={"xatol":1e-4,"maxiter":200}
    )
    if not fit_sig.success:
        raise RuntimeError(f"sigma optimization failed nodes={nodes}")
    sigma=float(fit_sig.x)
    lik,mu=profile(sigma)
    ll0,mu0=profile(0.0)
    if ll0>lik:
        sigma=0.0; lik=ll0; mu=mu0
    return {
        "nodes":int(nodes),
        "sigma_hat":float(sigma),
        "mu_hat":float(mu),
        "log_likelihood":float(lik),
        "log_likelihood_sigma0":float(ll0)
    }

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    mid=rain.build_midpoints(raw,runs)
    weather,_=rain.antecedent_amounts(mid)

    mask=np.asarray([
        str(p.wet_RunID) in weather and str(p.dry_RunID) in weather
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pw=psub.iloc[idx].copy().reset_index(drop=True)
    dw=[dsub[int(i)] for i in idx]
    hw=[hsub[int(i)] for i in idx]
    if len(pw)!=2835:
        raise RuntimeError(f"weather subset drift {len(pw)}")

    runs_weather=runs[runs["RunID"].astype(str).isin(weather)].copy().reset_index(drop=True)
    runs_weather["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_weather["RunID"].astype(str)]
    runs_weather["rain72_log"]=np.log1p(runs_weather["rain72_mm"].astype(float))
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    pred_A,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"A")
    pred_B,_,_=rain.fit_predict_amount_environment(runs_weather,sampled,ss,all_species,"B")
    pred_by_train={"A":pred_A,"B":pred_B}

    y_all=[]; eta_all=[]; y_silent=[]; eta_silent=[]
    for p,dct,p_hist in zip(pw.itertuples(index=False),dw,hw):
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
        q=np.clip(q,EPS,1-EPS)
        y=dct["wet"].astype(float)
        eta=uniform.logit(q)
        y_all.append(y); eta_all.append(eta)
        silent=(dry.sum(axis=1)==0)
        if np.any(silent):
            y_silent.append(y[silent]); eta_silent.append(eta[silent])

    ya=np.vstack(y_all); ea=np.vstack(eta_all)
    ys=np.vstack(y_silent); es=np.vstack(eta_silent)
    if len(ya)!=18769 or len(ys)!=8343:
        raise RuntimeError("cluster count drift")

    results={"all":{},"dry_route_silent":{}}
    for n in NODES:
        results["all"][str(n)]=fit_one(ya,ea,n)
        results["dry_route_silent"][str(n)]=fit_one(ys,es,n)

    checks={}
    for stratum in results:
        s20=results[stratum]["20"]["sigma_hat"]
        s40=results[stratum]["40"]["sigma_hat"]
        s60=results[stratum]["60"]["sigma_hat"]
        rel20=abs(s20-s60)/abs(s60)
        rel40=abs(s40-s60)/abs(s60)
        checks[stratum]={
            "relative_deviation_20_vs_60":float(rel20),
            "relative_deviation_40_vs_60":float(rel40),
            "pass":bool(rel20<=0.02 and rel40<=0.005)
        }

    out={
        "analysis":"naamp_logistic_normal_route_night_numerical_convergence_v0_1",
        "contract":"exploration/NAAMP_LOGISTIC_NORMAL_NUMERICAL_CONVERGENCE_CONTRACT_V0_1.json",
        "status":"posthoc_numerical_validation",
        "coverage":{"pairs":2835,"all_clusters":18769,"dry_route_silent_clusters":8343},
        "results":results,
        "checks":checks,
        "overall_pass":bool(all(v["pass"] for v in checks.values())),
        "interpretation_boundary":{
            "numerical_validation_only":True,
            "profile_ci_sampling_validity_established":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
