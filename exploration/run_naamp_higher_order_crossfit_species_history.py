#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_HIGHER_ORDER_CROSSFIT_SPECIES_HISTORY_RECEIPT_V0_1.json"
B=1000
KAPPA=2.0
ANCHOR=0.75
SEED=2840223

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

joint=loadmod("joint",EXP/"run_naamp_joint_species_local_memory_null.py")
mem=joint.mem
uniform=joint.uniform

def metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    if not np.any(route_new): return np.asarray([0.,0.,0.,0.])
    k=w[route_new].sum(axis=1).astype(float)
    extra=np.maximum(k-1.,0.)
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.asarray([float(len(k)),float(extra.sum()),float(higher.sum()),float(np.sum(k>=3.))])

def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2).astype(float)
    extra=np.maximum(k-1.,0.)*route_new
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.column_stack([
      route_new.sum(axis=1).astype(float),
      extra.sum(axis=1).astype(float),
      higher.sum(axis=1).astype(float),
      ((k>=3.)&route_new).sum(axis=1).astype(float)
    ])

def conditional(sim,obs):
    X=np.column_stack([np.ones(len(sim)),sim[:,0],sim[:,1]])
    y=sim[:,2]
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef; resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0]+coef[2]*obs[1])
    obs_resid=float(obs[2]-obs_pred)
    lo,hi=np.quantile(resid,[.025,.975])
    p=float((1+np.sum(resid>=obs_resid))/(len(resid)+1))
    ss_res=float(np.sum((y-pred)**2)); ss_tot=float(np.sum((y-y.mean())**2))
    return {
      "predicted_higher_order_beta":obs_pred,
      "observed_conditional_residual":obs_resid,
      "null_residual_ci95":[float(lo),float(hi)],
      "conditional_upper_tail_p":p,
      "above_upper_95":bool(obs_resid>hi),
      "null_regression_intercept":float(coef[0]),
      "null_regression_new_species_slope":float(coef[1]),
      "null_regression_extra_stop_slope":float(coef[2]),
      "null_regression_r2":float(1-ss_res/ss_tot) if ss_tot>0 else None
    }

def simulate_species_full(pairs,pair_data,probs,slopes_by_train,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,4),float)
    for i,(p,dct) in enumerate(zip(pairs.itertuples(index=False),pair_data)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        slopes=slopes_by_train[train_fold]
        gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in dct["species"]],float)
        basep=probs[dct["key"]]
        eta=uniform.logit(basep)+gamma[:,None]*float(p.rain_contrast)
        pre=uniform.expit(eta)
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metrics(w,dct["dry"])
    return num/den

def simulate_joint(psub,dsub,hsub,slopes_by_train,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,4),float)
    for i,(p,dct,ph) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        dry=dct["dry"].astype(float)
        p_anchor=(1-ANCHOR)*ph+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        slopes=slopes_by_train[train_fold]
        gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in dct["species"]],float)
        eta=uniform.logit(p_anchor)+gamma[:,None]*float(p.rain_contrast)
        pre=uniform.expit(eta)
        q=uniform.solve_shift(pre,dct["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metrics(w,dct["dry"])
    return num/den

def main():
    raw=mem.load_retry()
    runs,sets=mem.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    uniform.base.load=lambda:raw
    pairs,pair_data,pools,dry_ids,sampled,ss,r0,den0,obs0,beta_mask,r_beta,den_beta,obs_sor=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    slopes_A,audit_A,fold_A=joint.fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,audit_B,fold_B=joint.fit_species_slopes(runs,sampled,ss,all_species,"B")
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    # Full-sample observed higher-order endpoints.
    obs_rows=np.asarray([metrics(d["wet"],d["dry"]) for d in pair_data],float)
    r_full,den_full=uniform.design_residual(pairs)
    obs_full=(r_full[:,None]*obs_rows).sum(axis=0)/den_full
    stops={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops,ss)
    sim_full=simulate_species_full(pairs,pair_data,probs,slopes_by_train,r_full,den_full,SEED+101000)
    species_test=conditional(sim_full,obs_full)

    # Reproduce the exact strictly-prior local-history subset.
    site=mem.site_map(raw,eligible)
    meta,by_stratum,run_sites,run_site_species=mem.build_history_index(runs,sampled,ss,site)
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
    keep=np.asarray(keep,bool); idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    hsub=[histories[int(i)] for i in idx]
    if len(psub)!=2916 or psub.route_cluster.nunique()!=439:
        raise RuntimeError(f"prior subset drift: {len(psub)} pairs {psub.route_cluster.nunique()} routes")

    obs_rows_sub=np.asarray([metrics(d["wet"],d["dry"]) for d in dsub],float)
    r_sub,den_sub=uniform.design_residual(psub)
    obs_sub=(r_sub[:,None]*obs_rows_sub).sum(axis=0)/den_sub
    sim_joint=simulate_joint(psub,dsub,hsub,slopes_by_train,r_sub,den_sub,SEED+102000)
    joint_test=conditional(sim_joint,obs_sub)

    passed=bool(species_test["above_upper_95"] and joint_test["above_upper_95"])
    common=sorted(sp for sp in all_species if audit_A[sp]["estimable"] and audit_B[sp]["estimable"])
    corr=None
    if len(common)>=3:
        aa=np.asarray([slopes_A[sp] for sp in common],float); bb=np.asarray([slopes_B[sp] for sp in common],float)
        if np.std(aa)>0 and np.std(bb)>0: corr=float(np.corrcoef(aa,bb)[0,1])

    out={
      "analysis":"naamp_higher_order_crossfit_species_history_v0_1",
      "species_shift_training":{"fold_A":fold_A,"fold_B":fold_B,"n_estimable_both_folds":int(len(common)),"crossfold_gamma_correlation":corr},
      "full_sample":{"n_pairs":int(len(pairs)),"n_routes":int(pairs.route_cluster.nunique()),"observed":{"route_new_species_beta":float(obs_full[0]),"extra_stop_beta":float(obs_full[1]),"higher_order_beta":float(obs_full[2])},"crossfit_species_null":species_test},
      "prior_history_subset":{"n_pairs":int(len(psub)),"n_routes":int(psub.route_cluster.nunique()),"observed":{"route_new_species_beta":float(obs_sub[0]),"extra_stop_beta":float(obs_sub[1]),"higher_order_beta":float(obs_sub[2])},"joint_crossfit_species_prior_history_persistence_null":joint_test},
      "classification":{"higher_order_dependence_beyond_species_and_history_supported":passed},
      "interpretation_boundary":{"literal_synchrony_inferred":False,"individual_movement_inferred":False,"causal_rainfall_claim":False,"unique_lower_level_mechanism_identified":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
