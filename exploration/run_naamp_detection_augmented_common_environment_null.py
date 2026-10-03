#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_DETECTION_AUGMENTED_COMMON_ENVIRONMENT_NULL_RECEIPT_V0_1.json"

B=1000
CONC_SEED=2840232
DEP_SEED=2840233
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5
EPS=1e-7
DETECTION_COLS=("hearing_impairment_fraction","timeout_fraction","mean_wind")

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

rain=loadmod("rain_amount_common",EXP/"run_naamp_rain_amount_common_environment_null.py")
flex=rain.flex
joint=rain.joint
mem=rain.mem
uniform=rain.uniform
detect=loadmod("detection_quality",NAAMP/"run_naamp_detection_quality_robustness.py")

def feature_matrix_augmented(runs,state_levels,run_levels):
    baseX=rain.feature_matrix(runs,state_levels,run_levels)
    det=np.column_stack([
        runs[c].astype(float).to_numpy()
        for c in DETECTION_COLS
    ])
    if not np.isfinite(det).all():
        raise RuntimeError("nonfinite detection covariate entered augmented feature matrix")
    return np.column_stack([baseX,det])

def fit_predict_augmented(runs,sampled,ss,all_species,training_fold):
    x=runs.copy().reset_index(drop=True)
    x["route_fold"]=x["route_cluster"].astype(str).map(joint.fold_for_route)
    state_levels=sorted(x["State"].astype(str).unique())
    run_levels=sorted(x["RunNumber"].astype(str).unique())
    X_all=feature_matrix_augmented(x,state_levels,run_levels)
    train=(x["route_fold"].to_numpy()==training_fold)
    X=X_all[train]
    counts=flex.run_species_counts(x,sampled,ss)
    train_routes=x.loc[train,"route_cluster"].astype(str).to_numpy()
    all_runids=x["RunID"].astype(str).to_numpy()

    eta_by_species={}
    audit={}
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

        eta_by_species[sp]=np.clip(X_all@params,-20,20)
        info.update({"estimable":True,"method":method})
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

def q_for_pair(p,dct,p_hist,pred_by_train):
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
    return np.clip(q,EPS,1-EPS)

def concentration_test(psub,dsub,hsub,pred_by_train,r,den,obs,seed):
    rng=np.random.default_rng(seed)
    num=np.zeros((B,3),float)
    qs=[]
    shifts=[]
    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        q=q_for_pair(p,dct,p_hist,pred_by_train)
        qs.append(q)
        dry=dct["dry"].astype(float)

        # Audit implied wet-dry route-level logit shifts before pair magnitude matching.
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        pred=pred_by_train[train_fold]
        shifts.extend(abs(
            pred[str(p.wet_RunID)].get(sp,0.0)-pred[str(p.dry_RunID)].get(sp,0.0)
        ) for sp in dct["species"])

        w=rng.random((B,)+q.shape)<q[None,:,:]
        num+=r[i]*flex.sim_metrics(w,dry)

    result=flex.conditional(num/den,obs)
    sa=np.asarray(shifts,float)
    audit={
        "mean_abs_species_pair_logit_shift":float(np.mean(sa)) if len(sa) else None,
        "q95_abs_species_pair_logit_shift":float(np.quantile(sa,.95)) if len(sa) else None
    }
    return result,qs,audit

def bounded_test(qs,dsub,seed):
    rng=np.random.default_rng(seed)
    stats={
        "all":{"on":0.0,"od":0.0,"nn":np.zeros(B),"nd":np.zeros(B),"clusters":0},
        "dry_route_silent":{"on":0.0,"od":0.0,"nn":np.zeros(B),"nd":np.zeros(B),"clusters":0}
    }
    for q,dct in zip(qs,dsub):
        wet=dct["wet"].astype(float)
        dry=dct["dry"].astype(float)
        for i in range(q.shape[0]):
            e=wet[i]-q[i]
            s=float(e.sum()); ss=float(np.sum(e*e))
            on=s*s-ss
            od=9.0*ss
            w=rng.random((B,10))<q[i][None,:]
            ee=w.astype(float)-q[i][None,:]
            ssim=ee.sum(axis=1); sssim=np.sum(ee*ee,axis=1)
            nn=ssim*ssim-sssim
            nd=9.0*sssim
            labels=["all"]
            if dry[i].sum()==0:
                labels.append("dry_route_silent")
            for lab in labels:
                z=stats[lab]
                z["on"]+=on; z["od"]+=od
                z["nn"]+=nn; z["nd"]+=nd; z["clusters"]+=1

    out={}
    for lab,z in stats.items():
        if z["od"]<=0 or np.any(z["nd"]<=0):
            raise RuntimeError(f"nonpositive bounded-dependence denominator in {lab}")
        obs=float(z["on"]/z["od"])
        null=z["nn"]/z["nd"]
        lo,hi=np.quantile(null,[.025,.975])
        p=float((1+np.sum(null>=obs))/(B+1))
        out[lab]={
            "clusters":int(z["clusters"]),
            "rho_bounded":obs,
            "null_mean":float(np.mean(null)),
            "null_ci95":[float(lo),float(hi)],
            "plus_one_upper_tail_p":p,
            "positive_dependence_supported":bool(obs>hi and p<0.05)
        }
    return out

def main():
    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    eligible=set(runs["RunID"].astype(str))

    mid=rain.build_midpoints(raw,runs)
    weather,weather_sha=rain.antecedent_amounts(mid)
    det=detect.run_detection_metrics(raw,eligible,sampled,ss)

    complete_runs=set()
    for rid in runs["RunID"].astype(str):
        if rid not in weather or rid not in det.index:
            continue
        vals=[float(det.loc[rid,c]) for c in DETECTION_COLS]
        if np.isfinite(vals).all():
            complete_runs.add(rid)

    mask=np.asarray([
        str(p.wet_RunID) in complete_runs and str(p.dry_RunID) in complete_runs
        for p in psub.itertuples(index=False)
    ],bool)
    idx=np.flatnonzero(mask)
    pc=psub.iloc[idx].copy().reset_index(drop=True)
    dc=[dsub[int(i)] for i in idx]
    hc=[hsub[int(i)] for i in idx]
    if len(pc)==0:
        raise RuntimeError("no detection-complete focal pairs")

    runs_complete=runs[runs["RunID"].astype(str).isin(complete_runs)].copy().reset_index(drop=True)
    runs_complete["rain72_mm"]=[weather[str(r)]["rain72_mm"] for r in runs_complete["RunID"].astype(str)]
    runs_complete["rain72_log"]=np.log1p(runs_complete["rain72_mm"].astype(float))
    for c in DETECTION_COLS:
        runs_complete[c]=[float(det.loc[str(r),c]) for r in runs_complete["RunID"].astype(str)]

    all_species=sorted({sp for spp in pools.values() for sp in spp})

    # Same training and focal run universe for the baseline and augmented models.
    base_A,base_audit_A,base_fold_A=rain.fit_predict_amount_environment(
        runs_complete,sampled,ss,all_species,"A"
    )
    base_B,base_audit_B,base_fold_B=rain.fit_predict_amount_environment(
        runs_complete,sampled,ss,all_species,"B"
    )
    base_pred={"A":base_A,"B":base_B}

    aug_A,aug_audit_A,aug_fold_A=fit_predict_augmented(
        runs_complete,sampled,ss,all_species,"A"
    )
    aug_B,aug_audit_B,aug_fold_B=fit_predict_augmented(
        runs_complete,sampled,ss,all_species,"B"
    )
    aug_pred={"A":aug_A,"B":aug_B}

    obs_rows=np.asarray([flex.metrics(d["wet"],d["dry"]) for d in dc],float)
    r,den=uniform.design_residual(pc)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    baseline,base_qs,base_shift=concentration_test(
        pc,dc,hc,base_pred,r,den,obs,CONC_SEED
    )
    augmented,aug_qs,aug_shift=concentration_test(
        pc,dc,hc,aug_pred,r,den,obs,CONC_SEED
    )

    base_dep=bounded_test(base_qs,dc,DEP_SEED)
    aug_dep=bounded_test(aug_qs,dc,DEP_SEED)

    base_res=float(baseline["observed_conditional_residual"])
    aug_res=float(augmented["observed_conditional_residual"])
    frac=(base_res-aug_res)/base_res if base_res!=0 else None
    base_silent=float(base_dep["dry_route_silent"]["rho_bounded"])
    aug_silent=float(aug_dep["dry_route_silent"]["rho_bounded"])
    dep_frac=(base_silent-aug_silent)/base_silent if base_silent!=0 else None

    out={
        "analysis":"naamp_detection_augmented_common_environment_null_v0_1",
        "contract":"exploration/NAAMP_DETECTION_AUGMENTED_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json",
        "status":"posthoc_targeted_detection_falsification",
        "coverage":{
            "prior_history_pairs":int(len(psub)),
            "detection_complete_pairs":int(len(pc)),
            "routes":int(pc.route_cluster.nunique()),
            "states":int(pc.State.nunique()),
            "complete_training_runs":int(len(runs_complete))
        },
        "detection_covariates":list(DETECTION_COLS),
        "observed":{
            "route_new_species_beta":float(obs[0]),
            "extra_stop_beta":float(obs[1]),
            "concentration_beta":float(obs[2])
        },
        "same_sample_rain_amount_baseline":{
            "concentration":baseline,
            "bounded_dependence":base_dep,
            "environment_shift_audit":base_shift,
            "training":{"fold_A":base_fold_A,"fold_B":base_fold_B}
        },
        "detection_augmented":{
            "concentration":augmented,
            "bounded_dependence":aug_dep,
            "environment_shift_audit":aug_shift,
            "training":{"fold_A":aug_fold_A,"fold_B":aug_fold_B}
        },
        "comparison":{
            "baseline_concentration_residual":base_res,
            "augmented_concentration_residual":aug_res,
            "fraction_baseline_concentration_residual_removed":float(frac) if frac is not None else None,
            "baseline_dry_route_silent_rho_bounded":base_silent,
            "augmented_dry_route_silent_rho_bounded":aug_silent,
            "fraction_baseline_dry_silent_dependence_removed":float(dep_frac) if dep_frac is not None else None
        },
        "decision":{
            "detection_augmented_concentration_sufficient":bool(not augmented["above_upper_95"]),
            "detection_augmented_dry_silent_dependence_supported":bool(aug_dep["dry_route_silent"]["positive_dependence_supported"]),
            "residual_after_measured_detection":bool(
                augmented["above_upper_95"] or
                aug_dep["dry_route_silent"]["positive_dependence_supported"]
            )
        },
        "provenance":{
            "era5_antecedent_amount_sha256":weather_sha
        },
        "interpretation_boundary":{
            "independent_confirmation":False,
            "all_detectability_confounding_excluded":False,
            "unique_lower_level_mechanism_identified":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
