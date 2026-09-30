#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_CROSSFIT_RAIN_LOCAL_MEMORY_GATING_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840223
ANCHOR=0.75
LAMBDA_BOUNDS=(-10.0,10.0)


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


joint=loadmod("joint_base",EXP/"run_naamp_joint_species_local_memory_null.py")
mem=joint.mem
uniform=joint.uniform


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

    keep=[]
    histories=[]
    audits=[]
    for p,dct in zip(pairs.itertuples(index=False),pair_data):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            keep.append(False); histories.append(None); audits.append(None)
            continue
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            keep.append(False); histories.append(None); audits.append(None)
            continue
        ph,audit=mem.prior_probs(dct,ids,prior,run_sites,run_site_species)
        keep.append(True); histories.append(ph); audits.append(audit)

    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    hsub=[histories[int(i)] for i in idx]
    asub=[audits[int(i)] for i in idx]

    if len(psub)!=2916 or psub.route_cluster.nunique()!=439:
        raise RuntimeError(
            f"prior-memory subset drift pairs={len(psub)} routes={psub.route_cluster.nunique()}"
        )

    return raw,runs,psub,dsub,hsub,asub,pools,sampled,ss


def cell_terms(p,dct,p_hist,slopes):
    dry=dct["dry"].astype(float)
    p_anchor=(1.0-ANCHOR)*p_hist+ANCHOR*dry
    p_anchor=np.clip(p_anchor,1e-8,1-1e-8)

    gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in dct["species"]],float)
    rain=float(p.rain_contrast)
    base_eta=uniform.logit(p_anchor)+gamma[:,None]*rain

    centered=p_hist-p_hist.mean(axis=1,keepdims=True)
    m_gate=centered*(1.0-dry)
    x=rain*m_gate

    return base_eta,x


def pair_conditioned_loglik(base_eta,x,wet,wet_k,lmbda):
    eta=base_eta+lmbda*x
    pre=uniform.expit(eta)
    q=uniform.solve_shift(pre,int(wet_k))
    qq=np.clip(q,1e-12,1-1e-12)
    y=wet.astype(float)
    return float(np.sum(y*np.log(qq)+(1.0-y)*np.log1p(-qq)))


def fit_lambda(training_fold,psub,dsub,hsub,slopes):
    prepared=[]
    memory_abs=[]
    cell_count=0

    for p,dct,p_hist in zip(psub.itertuples(index=False),dsub,hsub):
        if joint.fold_for_route(str(p.route_cluster))!=training_fold:
            continue
        base_eta,x=cell_terms(p,dct,p_hist,slopes)
        prepared.append((base_eta,x,dct["wet"],dct["wet_k"]))
        memory_abs.append(np.abs(x).ravel())
        cell_count+=int(x.size)

    if not prepared:
        raise RuntimeError(f"no training pairs for fold {training_fold}")

    def objective(lmbda):
        ll=0.0
        for base_eta,x,wet,wet_k in prepared:
            ll+=pair_conditioned_loglik(base_eta,x,wet,wet_k,float(lmbda))
        return -ll

    null_nll=float(objective(0.0))
    opt=minimize_scalar(
        objective,
        bounds=LAMBDA_BOUNDS,
        method="bounded",
        options={"xatol":1e-5,"maxiter":200},
    )
    lmbda=float(opt.x)
    best_nll=float(opt.fun)
    stable=bool(opt.success and np.isfinite(lmbda) and abs(lmbda)<9.9)

    aa=np.concatenate(memory_abs) if memory_abs else np.asarray([],float)
    return lmbda,{
        "training_fold":training_fold,
        "n_training_pairs":int(len(prepared)),
        "n_training_cells":int(cell_count),
        "optimizer_success":bool(opt.success),
        "optimizer_message":str(opt.message),
        "lambda":lmbda,
        "lambda_within_stability_bound":stable,
        "negative_loglik_lambda0":null_nll,
        "negative_loglik_optimum":best_nll,
        "loglik_improvement":float(null_nll-best_nll),
        "mean_abs_rain_x_memory_gate":float(np.mean(aa)) if len(aa) else 0.0,
        "q95_abs_rain_x_memory_gate":float(np.quantile(aa,.95)) if len(aa) else 0.0,
    }


def simulate_crossfit(psub,dsub,hsub,slopes_by_train,lambdas,r,den,obs_betas):
    rng=np.random.default_rng(SEED)
    numer=np.zeros((B,4),float)

    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        test_fold=joint.fold_for_route(str(p.route_cluster))
        train_fold="B" if test_fold=="A" else "A"
        slopes=slopes_by_train[train_fold]
        lmbda=float(lambdas[train_fold])

        base_eta,x=cell_terms(p,dct,p_hist,slopes)
        pre=uniform.expit(base_eta+lmbda*x)
        q=uniform.solve_shift(pre,dct["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        comps=uniform.simulated_components(wsim,dct["dry"])
        numer += r[i]*comps

    return mem.summarize_sim(numer/den,obs_betas)


def main():
    raw,runs,psub,dsub,hsub,asub,pools,sampled,ss=prepare_subset()

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    slopes_A,audit_A,fold_A=joint.fit_species_slopes(
        runs,sampled,ss,all_species,"A"
    )
    slopes_B,audit_B,fold_B=joint.fit_species_slopes(
        runs,sampled,ss,all_species,"B"
    )
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    lambda_A,lambda_audit_A=fit_lambda("A",psub,dsub,hsub,slopes_A)
    lambda_B,lambda_audit_B=fit_lambda("B",psub,dsub,hsub,slopes_B)
    stable=bool(
        lambda_audit_A["lambda_within_stability_bound"]
        and lambda_audit_B["lambda_within_stability_bound"]
    )

    output={
        "analysis":"naamp_crossfit_rain_by_local_memory_gating_null_v0_1",
        "contract":"exploration/NAAMP_CROSSFIT_RAIN_LOCAL_MEMORY_GATING_NULL_CONTRACT_V0_1.json",
        "trigger":"joint_species_local_memory_null_rejected_p_0.000999",
        "coverage":{
            "pairs":int(len(psub)),
            "routes":int(psub.route_cluster.nunique()),
            "states":int(psub.State.nunique()),
        },
        "species_shift_training":{
            "fold_A":fold_A,
            "fold_B":fold_B,
        },
        "lambda_training":{
            "fold_A":lambda_audit_A,
            "fold_B":lambda_audit_B,
            "stability_gate_pass":stable,
        },
        "response_endpoints_read":False,
    }

    if not stable:
        output["decision"]="optimizer_stability_gate_failed_no_mechanism_conclusion"
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    obs_rows=np.asarray([
        uniform.component_counts(d["wet"],d["dry"])
        for d in dsub
    ],float)
    r,den=uniform.design_residual(psub)
    obs_betas=(r[:,None]*obs_rows).sum(axis=0)/den

    result=simulate_crossfit(
        psub,dsub,hsub,slopes_by_train,
        {"A":lambda_A,"B":lambda_B},
        r,den,obs_betas
    )
    p=float(result["primary_omnibus"]["monte_carlo_p"])

    decision=(
        "crossfit_rain_local_memory_gating_sufficient_stop_mechanism_escalation"
        if p>=0.05
        else
        "crossfit_rain_local_memory_gating_insufficient_stop_lower_level_mechanism_escalation"
    )

    output.update({
        "response_endpoints_read":True,
        "crossfit_gating_null":result,
        "decision":decision,
        "interpretation_boundary":{
            "lambda_is_single_global_crossfit_parameter":True,
            "currently_silent_cells_only_gated":True,
            "pair_wet_incidence_magnitude_conditioned":True,
            "failure_to_reject_is_sufficiency_not_unique_causal_proof":True,
            "continuous_occupancy_proven":False,
            "causal_rainfall_claim":False,
            "no_further_mechanism_models_authorized_under_decision_tree":True,
            "submission_story_change_authorized":False,
        },
    })

    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
