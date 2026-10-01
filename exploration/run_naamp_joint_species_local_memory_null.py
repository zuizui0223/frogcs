#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_JOINT_SPECIES_LOCAL_MEMORY_NULL_RECEIPT_V0_1.json"

B=1000
SEED=2840223
ANCHOR=0.75
MIN_POSITIVE_CELLS=20
MIN_POSITIVE_ROUTES=5


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


mem=loadmod("prior_memory",EXP/"run_naamp_prior_local_memory_null.py")
uniform=mem.uniform


def fold_for_route(route_cluster):
    b=hashlib.sha256(str(route_cluster).encode("utf-8")).digest()[0]
    return "A" if b<128 else "B"


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


def fit_species_slopes(runs,sampled,ss,all_species,training_fold):
    x=runs.copy()
    x["route_fold"]=x["route_cluster"].astype(str).map(fold_for_route)
    x=x[x["route_fold"]==training_fold].copy().reset_index(drop=True)
    x["dry_x"]=np.log1p(x["DaysSinceRain"].astype(float))
    theta=2*np.pi*x["doy"].astype(float)/365.25
    x["sin_doy"]=np.sin(theta)
    x["cos_doy"]=np.cos(theta)
    counts=run_species_counts(x,sampled,ss)

    slopes={}
    audit={}
    for sp in sorted(all_species):
        y=np.asarray([counts[str(rid)].get(sp,0) for rid in x["RunID"].astype(str)],float)
        pos_cells=int(y.sum())
        pos_routes=int(x.loc[y>0,"route_cluster"].astype(str).nunique())
        info={
            "positive_stop_cells":pos_cells,
            "positive_routes":pos_routes,
            "estimable":False,
            "method":"zero_differential_shift",
            "dryness_beta":0.0,
            "wet_shift_gamma":0.0,
        }
        if pos_cells<MIN_POSITIVE_CELLS or pos_routes<MIN_POSITIVE_ROUTES:
            slopes[sp]=0.0
            audit[sp]=info
            continue

        d=x[["State","RunNumber","mean_temp_c","dry_x","sin_doy","cos_doy"]].copy()
        d["prop"]=y/10.0
        formula=(
            "prop ~ dry_x + mean_temp_c + sin_doy + cos_doy + "
            "C(State) + C(RunNumber)"
        )
        glm=smf.glm(
            formula,data=d,family=sm.families.Binomial(),
            freq_weights=np.repeat(10.0,len(d))
        )
        method="glm"
        try:
            fit=glm.fit(maxiter=200,disp=0)
            beta=float(fit.params["dry_x"])
            if not np.isfinite(beta) or abs(beta)>20:
                raise RuntimeError("unstable slope")
        except Exception:
            method="ridge_fallback"
            fit=glm.fit_regularized(alpha=0.01,L1_wt=0.0,maxiter=1000)
            beta=float(fit.params["dry_x"])
            if not np.isfinite(beta):
                beta=0.0
                method="zero_after_failed_regularization"

        gamma=float(-beta)
        slopes[sp]=gamma
        info.update({
            "estimable":bool(method!="zero_after_failed_regularization"),
            "method":method,
            "dryness_beta":beta,
            "wet_shift_gamma":gamma,
        })
        audit[sp]=info

    return slopes,audit,{
        "training_fold":training_fold,
        "n_runs":int(len(x)),
        "n_routes":int(x.route_cluster.nunique()),
        "n_species_total":int(len(all_species)),
        "n_species_estimable":int(sum(v["estimable"] for v in audit.values())),
    }


def simulate_variant(psub,dsub,hsub,slopes_by_train,r,den,obs_betas,variant,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)

    for i,(p,dct,p_hist) in enumerate(zip(psub.itertuples(index=False),dsub,hsub)):
        if variant in ("memory_only","joint_true"):
            ph=p_hist
        elif variant in ("joint_perm1","joint_perm2"):
            tag="perm1" if variant.endswith("perm1") else "perm2"
            ph=p_hist[:,mem.permutation_for_pair(p,tag)]
        elif variant=="species_nonlocal_prior":
            rowmean=p_hist.mean(axis=1,keepdims=True)
            ph=np.repeat(rowmean,10,axis=1)
        else:
            raise ValueError(variant)

        dry=dct["dry"].astype(float)
        p_anchor=(1-ANCHOR)*ph+ANCHOR*dry
        p_anchor=np.clip(p_anchor,1e-8,1-1e-8)

        if variant=="memory_only":
            pre=p_anchor
        else:
            test_fold=fold_for_route(str(p.route_cluster))
            train_fold="B" if test_fold=="A" else "A"
            slopes=slopes_by_train[train_fold]
            gamma=np.asarray([float(slopes.get(sp,0.0)) for sp in dct["species"]],float)
            eta=uniform.logit(p_anchor)+gamma[:,None]*float(p.rain_contrast)
            pre=uniform.expit(eta)

        q=uniform.solve_shift(pre,dct["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        comps=uniform.simulated_components(wsim,dct["dry"])
        numer += r[i]*comps

    return mem.summarize_sim(numer/den,obs_betas)


def main():
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
    audit_rows=[]
    for p,dct in zip(pairs.itertuples(index=False),pair_data):
        ids=mem.focal_siteids(p,dct,site)
        if ids is None:
            keep.append(False); histories.append(None); audit_rows.append(None)
            continue
        prior=mem.eligible_prior_runs(p,dct,ids,meta,by_stratum,run_sites)
        if not prior:
            keep.append(False); histories.append(None); audit_rows.append(None)
            continue
        ph,audit=mem.prior_probs(dct,ids,prior,run_sites,run_site_species)
        keep.append(True); histories.append(ph); audit_rows.append(audit)

    keep=np.asarray(keep,bool)
    idx=np.flatnonzero(keep)
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[int(i)] for i in idx]
    hsub=[histories[int(i)] for i in idx]
    asub=[audit_rows[int(i)] for i in idx]

    coverage={
        "all_pairs":int(len(pairs)),
        "eligible_pairs":int(len(psub)),
        "eligible_routes":int(psub.route_cluster.nunique()),
        "eligible_states":int(psub.State.nunique()),
    }
    if coverage["eligible_pairs"]!=2916 or coverage["eligible_routes"]!=439:
        raise RuntimeError(f"prior-memory subset drift: {coverage}")

    gate=bool(coverage["eligible_pairs"]>=1500 and coverage["eligible_routes"]>=300)
    output={
        "analysis":"naamp_joint_crossfit_species_local_memory_null_v0_1",
        "contract":"exploration/NAAMP_JOINT_SPECIES_LOCAL_MEMORY_NULL_CONTRACT_V0_1.json",
        "coverage":{**coverage,"gate_pass":gate},
        "response_endpoints_read":False,
    }
    if not gate:
        OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
        print(json.dumps(output,indent=2,sort_keys=True))
        return

    all_species=sorted({sp for spp in pools.values() for sp in spp})
    slopes_A,audit_A,fold_A=fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,audit_B,fold_B=fit_species_slopes(runs,sampled,ss,all_species,"B")
    slopes_by_train={"A":slopes_A,"B":slopes_B}

    common=sorted(
        sp for sp in all_species
        if audit_A[sp]["estimable"] and audit_B[sp]["estimable"]
    )
    if len(common)>=3:
        aa=np.asarray([slopes_A[sp] for sp in common],float)
        bb=np.asarray([slopes_B[sp] for sp in common],float)
        corr=float(np.corrcoef(aa,bb)[0,1]) if np.std(aa)>0 and np.std(bb)>0 else None
    else:
        corr=None

    obs_rows=np.asarray([
        uniform.component_counts(d["wet"],d["dry"]) for d in dsub
    ],float)
    r,den=uniform.design_residual(psub)
    obs_betas=(r[:,None]*obs_rows).sum(axis=0)/den

    memory_only=simulate_variant(
        psub,dsub,hsub,slopes_by_train,r,den,obs_betas,
        "memory_only",SEED+81000
    )
    species_nonlocal=simulate_variant(
        psub,dsub,hsub,slopes_by_train,r,den,obs_betas,
        "species_nonlocal_prior",SEED+90000
    )
    joint_true=simulate_variant(
        psub,dsub,hsub,slopes_by_train,r,den,obs_betas,
        "joint_true",SEED+91000
    )
    joint_perm1=simulate_variant(
        psub,dsub,hsub,slopes_by_train,r,den,obs_betas,
        "joint_perm1",SEED+92001
    )
    joint_perm2=simulate_variant(
        psub,dsub,hsub,slopes_by_train,r,den,obs_betas,
        "joint_perm2",SEED+92002
    )

    ptrue=joint_true["primary_omnibus"]["monte_carlo_p"]
    p1=joint_perm1["primary_omnibus"]["monte_carlo_p"]
    p2=joint_perm2["primary_omnibus"]["monte_carlo_p"]

    if ptrue<.05:
        decision="combined_species_and_local_memory_insufficient"
    elif p1<.05 and p2<.05:
        decision="combined_sufficient_and_physical_site_identity_specific"
    else:
        decision="combined_sufficient_but_generic_history_heterogeneity_not_excluded"

    output.update({
        "response_endpoints_read":True,
        "species_shift_training":{
            "fold_A":fold_A,
            "fold_B":fold_B,
            "estimability":{
                "minimum_positive_stop_cells":MIN_POSITIVE_CELLS,
                "minimum_positive_routes":MIN_POSITIVE_ROUTES,
            },
            "n_estimable_both_folds":int(len(common)),
            "crossfold_gamma_correlation":corr,
        },
        "history_audit":{
            "median_prior_runs":float(np.median([x["prior_runs"] for x in asub])),
            "median_min_site_exposure":float(np.median([x["site_exposure_min"] for x in asub])),
        },
        "same_subset_diagnostics":{
            "memory_only_reference":memory_only,
            "species_nonlocal_prior_plus_crossfit_shift":species_nonlocal,
        },
        "joint_true_local_memory_plus_crossfit_species_shift":joint_true,
        "joint_site_identity_permuted_controls":{
            "perm1":joint_perm1,
            "perm2":joint_perm2,
        },
        "decision":decision,
        "interpretation_boundary":{
            "species_shifts_crossfit_across_routes":True,
            "local_probability_weights_strictly_prior":True,
            "failure_to_reject_is_sufficiency_not_unique_identification":True,
            "continuous_occupancy_proven":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    })

    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
