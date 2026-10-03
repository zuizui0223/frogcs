#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import minimize_scalar, brentq
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_LOGISTIC_NORMAL_ROUTE_NIGHT_STATE_RECEIPT_V0_1.json"

ANCHOR=0.75
EPS=1e-7
NODES=20
SIGMA_BOUNDS=(0.0,5.0)
MU_BOUNDS=(-5.0,5.0)
PROFILE_DROP=3.841458820694124/2.0

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

GH_X,GH_W=hermgauss(NODES)
LOG_GH_W=np.log(GH_W)-0.5*np.log(np.pi)

def marginal_loglik(y,eta,mu,sigma):
    y=np.asarray(y,float)
    eta=np.asarray(eta,float)
    node_ll=np.empty((len(y),NODES),float)
    shifts=np.sqrt(2.0)*float(sigma)*GH_X+float(mu)
    for h,shift in enumerate(shifts):
        z=eta+shift
        node_ll[:,h]=np.sum(y*z-np.logaddexp(0.0,z),axis=1)
    return float(np.sum(logsumexp(node_ll+LOG_GH_W[None,:],axis=1)))

def fit_stratum(y,eta):
    y=np.asarray(y,float)
    eta=np.asarray(eta,float)
    if y.ndim!=2 or y.shape[1]!=10 or eta.shape!=y.shape:
        raise RuntimeError(f"unexpected cluster shape y={y.shape} eta={eta.shape}")

    cache={}
    def profile(sigma):
        sigma=float(sigma)
        key=round(sigma,10)
        if key in cache:
            return cache[key]
        def nll_mu(mu):
            return -marginal_loglik(y,eta,float(mu),sigma)
        mu_fit=minimize_scalar(
            nll_mu,bounds=MU_BOUNDS,method="bounded",
            options={"xatol":1e-5,"maxiter":200}
        )
        if not mu_fit.success:
            raise RuntimeError(f"mu optimization failed at sigma={sigma}")
        out=(float(-mu_fit.fun),float(mu_fit.x))
        cache[key]=out
        return out

    ll0,mu0=profile(0.0)
    sig_fit=minimize_scalar(
        lambda s:-profile(float(s))[0],
        bounds=SIGMA_BOUNDS,method="bounded",
        options={"xatol":1e-4,"maxiter":200}
    )
    if not sig_fit.success:
        raise RuntimeError("sigma optimization failed")
    sigma_hat=float(sig_fit.x)
    ll_hat,mu_hat=profile(sigma_hat)
    if ll0>ll_hat:
        sigma_hat=0.0
        ll_hat=ll0
        mu_hat=mu0

    cutoff=ll_hat-PROFILE_DROP
    if sigma_hat<=1e-8 or ll0>=cutoff:
        lo=0.0
    else:
        lo=float(brentq(lambda s:profile(float(s))[0]-cutoff,0.0,sigma_hat,xtol=1e-5))

    upper_boundary=False
    ll_upper,_=profile(SIGMA_BOUNDS[1])
    if ll_upper>=cutoff:
        hi=float(SIGMA_BOUNDS[1])
        upper_boundary=True
    else:
        hi=float(brentq(
            lambda s:profile(float(s))[0]-cutoff,
            max(sigma_hat,1e-8),SIGMA_BOUNDS[1],xtol=1e-5
        ))

    var=float(sigma_hat*sigma_hat)
    icc=float(var/(var+(math.pi**2)/3.0))
    return {
        "clusters":int(len(y)),
        "mu_hat":float(mu_hat),
        "sigma_hat":sigma_hat,
        "sigma_profile_ci95":[lo,hi],
        "profile_upper_bound_hit":bool(upper_boundary),
        "one_sd_common_state_odds_multiplier":float(math.exp(sigma_hat)),
        "latent_logistic_icc":icc,
        "log_likelihood_mle":float(ll_hat),
        "sigma0_mu_hat":float(mu0),
        "log_likelihood_sigma0":float(ll0),
        "likelihood_ratio_statistic":float(max(0.0,2.0*(ll_hat-ll0)))
    }

def main():
    trigger=json.loads((EXP/"NAAMP_BOUNDED_ROUTE_NIGHT_RESIDUAL_DEPENDENCE_RECEIPT_V0_1.json").read_text())
    if not trigger["results"]["all"]["positive_dependence_supported"]:
        out={
            "analysis":"naamp_logistic_normal_species_route_night_state_v0_1",
            "status":"not_run_bounded_dependence_trigger_not_met"
        }
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
    pred_A,audit_A,fold_A=rain.fit_predict_amount_environment(
        runs_weather,sampled,ss,all_species,"A"
    )
    pred_B,audit_B,fold_B=rain.fit_predict_amount_environment(
        runs_weather,sampled,ss,all_species,"B"
    )
    pred_by_train={"A":pred_A,"B":pred_B}

    y_all=[]; eta_all=[]
    y_silent=[]; eta_silent=[]

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
        eta=uniform.logit(q)

        y_all.append(y); eta_all.append(eta)
        silent=(dry.sum(axis=1)==0)
        if np.any(silent):
            y_silent.append(y[silent]); eta_silent.append(eta[silent])

    ya=np.vstack(y_all); ea=np.vstack(eta_all)
    ys=np.vstack(y_silent); es=np.vstack(eta_silent)

    if len(ya)!=18769 or len(ys)!=8343:
        raise RuntimeError(f"cluster-count drift all={len(ya)} silent={len(ys)}")

    result_all=fit_stratum(ya,ea)
    result_silent=fit_stratum(ys,es)

    out={
        "analysis":"naamp_logistic_normal_species_route_night_state_v0_1",
        "contract":"exploration/NAAMP_LOGISTIC_NORMAL_ROUTE_NIGHT_STATE_CONTRACT_V0_1.json",
        "status":"posthoc_latent_state_magnitude_triggered",
        "coverage":{
            "pairs":int(len(pw)),
            "routes":int(pw.route_cluster.nunique()),
            "all_clusters":int(len(ya)),
            "dry_route_silent_clusters":int(len(ys))
        },
        "model":{
            "quadrature_nodes":NODES,
            "sigma_bounds":list(SIGMA_BOUNDS),
            "mu_bounds":list(MU_BOUNDS),
            "profile_likelihood_drop":PROFILE_DROP
        },
        "all_clusters":result_all,
        "dry_route_silent":result_silent,
        "weather_provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "fixed_q_offset":True,
            "latent_icc_is_published_monitoring_design_effect":False,
            "unique_lower_level_mechanism_identified":False,
            "independent_confirmation":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
