#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_FLEXIBLE_COMMON_ENVIRONMENT_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840223
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5
EPS=1e-7

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

joint=loadmod("joint_base",EXP/"run_naamp_joint_species_local_memory_null.py")
mem=joint.mem
uniform=joint.uniform

def logit(p):
    p=np.clip(np.asarray(p,float),EPS,1-EPS)
    return np.log(p/(1-p))

def feature_matrix(runs, state_levels, run_levels):
    x=runs.copy().reset_index(drop=True)
    dry_x=np.log1p(x["DaysSinceRain"].astype(float).to_numpy())
    temp=x["mean_temp_c"].astype(float).to_numpy()
    doy=x["doy"].astype(float).to_numpy()

    dry_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False, lower_bound=0.0, upper_bound=5.198497031265826) - 1",
        {"v":dry_x},
        return_type="dataframe"
    ),float)
    temp_basis=np.asarray(patsy.dmatrix(
        "bs(v, df=4, degree=3, include_intercept=False, lower_bound=-10.0, upper_bound=45.0) - 1",
        {"v":temp},
        return_type="dataframe"
    ),float)

    theta=2*np.pi*doy/365.25
    harmonics=np.column_stack([
        np.sin(theta),np.cos(theta),
        np.sin(2*theta),np.cos(2*theta)
    ])
    interaction=(dry_x*temp)[:,None]

    state=np.zeros((len(x),max(0,len(state_levels)-1)),float)
    state_index={v:i for i,v in enumerate(state_levels[1:])}
    for i,v in enumerate(x["State"].astype(str)):
        j=state_index.get(v)
        if j is not None:
            state[i,j]=1.0

    run=np.zeros((len(x),max(0,len(run_levels)-1)),float)
    run_index={v:i for i,v in enumerate(run_levels[1:])}
    for i,v in enumerate(x["RunNumber"].astype(str)):
        j=run_index.get(v)
        if j is not None:
            run[i,j]=1.0

    X=np.column_stack([
        np.ones(len(x),float),
        dry_basis,temp_basis,harmonics,interaction,state,run
    ])
    return X

def run_species_counts(runs,sampled,ss):
    counts={}
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        c={}
        for st in sampled[rid]:
            for sp in ss.get((rid,st),set()):
                c[sp]=c.get(sp,0)+1
        counts[rid]=c
    return counts

def fit_predict_environment(runs,sampled,ss,all_species,training_fold):
    x=runs.copy().reset_index(drop=True)
    x["route_fold"]=x["route_cluster"].astype(str).map(joint.fold_for_route)
    state_levels=sorted(x["State"].astype(str).unique())
    run_levels=sorted(x["RunNumber"].astype(str).unique())
    X_all=feature_matrix(x,state_levels,run_levels)
    train=(x["route_fold"].to_numpy()==training_fold)
    X=X_all[train]
    counts=run_species_counts(x,sampled,ss)

    eta_by_species={}
    audit={}
    train_routes=x.loc[train,"route_cluster"].astype(str).to_numpy()
    all_runids=x["RunID"].astype(str).to_numpy()
    train_runids=all_runids[train]

    for sp in sorted(all_species):
        y_all=np.asarray([counts[rid].get(sp,0) for rid in all_runids],float)
        y=y_all[train]
        pos_cells=int(y.sum())
        pos_routes=int(len(set(train_routes[y>0])))
        info={
            "positive_stop_cells":pos_cells,
            "positive_routes":pos_routes,
            "estimable":False,
            "method":"zero_environment_shift"
        }
        if pos_cells<MIN_POSITIVE_CELLS or pos_routes<MIN_POSITIVE_ROUTES:
            eta_by_species[sp]=np.zeros(len(x),float)
            audit[sp]=info
            continue

        prop=y/10.0
        model=sm.GLM(
            prop,X,
            family=sm.families.Binomial(),
            freq_weights=np.repeat(10.0,len(prop))
        )
        method="glm"
        try:
            fit=model.fit(maxiter=200,disp=0)
            params=np.asarray(fit.params,float)
            if (not np.all(np.isfinite(params))) or np.max(np.abs(params))>50:
                raise RuntimeError("unstable coefficients")
        except Exception:
            method="ridge_fallback"
            fit=model.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
            params=np.asarray(fit.params,float)
            if not np.all(np.isfinite(params)):
                eta_by_species[sp]=np.zeros(len(x),float)
                info["method"]="zero_after_failed_regularization"
                audit[sp]=info
                continue

        eta=X_all@params
        eta=np.clip(eta,-20,20)
        eta_by_species[sp]=eta
        p=np.clip(1/(1+np.exp(-eta[train])),EPS,1-EPS)
        yy=np.repeat(np.arange(len(prop)),10)
        # Cell-level Bernoulli log loss represented from grouped binomial counts.
        nll=float(-np.sum(y*np.log(p)+(10-y)*np.log1p(-p)))
        info.update({
            "estimable":True,
            "method":method,
            "n_training_runs":int(len(prop)),
            "negative_loglik":nll,
            "mean_predicted_stop_probability":float(np.mean(p))
        })
        audit[sp]=info

    pred={}
    for i,rid in enumerate(all_runids):
        pred[rid]={sp:float(eta_by_species[sp][i]) for sp in all_species}
    return pred,audit,{
        "training_fold":training_fold,
        "n_training_runs":int(train.sum()),
        "n_training_routes":int(x.loc[train,"route_cluster"].nunique()),
        "n_estimable_species":int(sum(1 for a in audit.values() if a["estimable"])),
        "feature_count":int(X.shape[1])
    }

def prepare_subset():
    raw=mem.load_retry()
    runs,sets=mem.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    uniform.base.load=lambda:raw
    (
        pairs,pair_data,pools,dry_ids,sampled,ss,r0,den0,obs0,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    site=mem.site_map(raw,eligible)
    meta,by_stratum,run_sites,run_site_species=mem.build_history_index(
        runs,sampled,ss,site
    )
    keep=[]; histories=[]
    for p,dct in zip(pairs.itertuples(index=False),pair_data):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            keep.append(False); histories.append(None); continue
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            keep.append(False); histories.append(None); continue
        ph,_=mem.prior_probs(dct,ids,prior,run_sites,run_site_species)
        keep.append(True); histories.append(ph)

    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    hsub=[histories[int(i)] for i in idx]

    if len(psub)!=2916 or psub.route_cluster.nunique()!=439:
        raise RuntimeError(
            f"prior-history subset drift: {len(psub)} pairs, {psub.route_cluster.nunique()} routes"
        )
    return raw,runs,psub,dsub,hsub,pools,sampled,ss

def metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    if not np.any(route_new):
        return np.asarray([0.,0.,0.])
    k=w[route_new].sum(axis=1).astype(float)
    extra=np.maximum(k-1.,0.)
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.asarray([float(len(k)),float(extra.sum()),float(higher.sum())])

def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2).astype(float)
    extra=np.maximum(k-1.,0.)*route_new
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.column_stack([
        route_new.sum(axis=1).astype(float),
        extra.sum(axis=1).astype(float),
        higher.sum(axis=1).astype(float)
    ])

def conditional(sim,obs):
    X=np.column_stack([np.ones(len(sim)),sim[:,0],sim[:,1]])
    y=sim[:,2]
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef
    resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0]+coef[2]*obs[1])
    obs_resid=float(obs[2]-obs_pred)
    lo,hi=np.quantile(resid,[.025,.975])
    p=float((1+np.sum(resid>=obs_resid))/(len(resid)+1))
    ss_res=float(np.sum((y-pred)**2)); ss_tot=float(np.sum((y-y.mean())**2))
    return {
        "predicted_concentration_beta":obs_pred,
        "observed_concentration_beta":float(obs[2]),
        "observed_conditional_residual":obs_resid,
        "null_residual_ci95":[float(lo),float(hi)],
        "conditional_upper_tail_p":p,
        "above_upper_95":bool(obs_resid>hi),
        "null_regression_r2":float(1-ss_res/ss_tot) if ss_tot>0 else None
    }

def simulate(psub,dsub,hsub,pred_by_train,r,den):
    rng=np.random.default_rng(SEED)
    num=np.zeros((B,3),float)
    delta_abs=[]
    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        wet_id=str(p.wet_RunID); dry_id=str(p.dry_RunID)
        delta=np.asarray([
            pred[wet_id].get(sp,0.0)-pred[dry_id].get(sp,0.0)
            for sp in dct["species"]
        ],float)
        delta_abs.append(np.abs(delta))

        dry=dct["dry"].astype(float)
        p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
        p_anchor=np.clip(p_anchor,EPS,1-EPS)
        pre=uniform.expit(uniform.logit(p_anchor)+delta[:,None])
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metrics(w,dct["dry"])

    da=np.concatenate(delta_abs) if delta_abs else np.asarray([],float)
    return num/den,{
        "mean_abs_species_pair_environment_logit_shift":float(np.mean(da)) if len(da) else 0.0,
        "q95_abs_species_pair_environment_logit_shift":float(np.quantile(da,.95)) if len(da) else 0.0,
        "max_abs_species_pair_environment_logit_shift":float(np.max(da)) if len(da) else 0.0
    }

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=prepare_subset()
    all_species=sorted({sp for spp in pools.values() for sp in spp})

    pred_A,audit_A,fold_A=fit_predict_environment(
        runs,sampled,ss,all_species,"A"
    )
    pred_B,audit_B,fold_B=fit_predict_environment(
        runs,sampled,ss,all_species,"B"
    )
    pred_by_train={"A":pred_A,"B":pred_B}

    obs_rows=np.asarray([metrics(d["wet"],d["dry"]) for d in dsub],float)
    r,den=uniform.design_residual(psub)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    sim,shift_audit=simulate(psub,dsub,hsub,pred_by_train,r,den)
    result=conditional(sim,obs)

    principal_residual=0.2969
    flex_residual=float(result["observed_conditional_residual"])
    shrink=(principal_residual-flex_residual)/principal_residual

    decision=(
        "measured_flexible_common_environment_sufficient"
        if not result["above_upper_95"]
        else
        "residual_dependence_beyond_measured_flexible_common_environment"
    )

    out={
        "analysis":"naamp_flexible_common_environment_null_v0_1",
        "contract":"exploration/NAAMP_FLEXIBLE_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json",
        "status":"posthoc_exploratory_after_explicit_2026_10_03_reopening",
        "coverage":{
            "pairs":int(len(psub)),
            "routes":int(psub.route_cluster.nunique()),
            "states":int(psub.State.nunique())
        },
        "model_training":{
            "fold_A":fold_A,
            "fold_B":fold_B,
            "fold_A_species":audit_A,
            "fold_B_species":audit_B
        },
        "environment_shift_audit":shift_audit,
        "observed":{
            "route_new_species_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "concentration_beta":float(obs[2])
        },
        "flexible_common_environment_null":result,
        "comparison_with_existing_principal_comparator":{
            "existing_predicted_concentration_beta":1.3535,
            "existing_observed_concentration_beta":1.6503,
            "existing_conditional_residual":principal_residual,
            "flexible_conditional_residual":flex_residual,
            "fraction_of_existing_residual_removed":float(shrink)
        },
        "decision":decision,
        "interpretation_boundary":{
            "independent_confirmation":False,
            "posthoc_exploratory":True,
            "rainfall_amount_directly_modeled":False,
            "unmeasured_shared_environment_excluded":False,
            "social_facilitation_identified":False,
            "synchronous_breeding_identified":False,
            "unique_lower_level_mechanism_identified":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
