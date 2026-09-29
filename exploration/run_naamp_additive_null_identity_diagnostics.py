#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_ADDITIVE_NULL_IDENTITY_DIAGNOSTICS_RECEIPT_V0_1.json"
B=1000
SEED=2840223
KAPPA=2.0


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("pulse_base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial_base",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform_base",NAAMP/"run_naamp_uniform_activation_null.py")
species_mod=loadmod("species_null",EXP/"run_naamp_crossfit_species_shift_null.py")
site_mod=loadmod("site_null",EXP/"run_naamp_crossfit_site_and_additive_null.py")


def permute_site_shifts(site_map, training_block, tag):
    grouped=defaultdict(list)
    for key,val in site_map.items():
        route,stop=key.rsplit(":",1)
        grouped[route].append((stop,key,float(val)))
    out={}
    for route,rows in grouped.items():
        rows=sorted(rows,key=lambda x:x[0])
        values=np.asarray([x[2] for x in rows],float)
        seed_bytes=hashlib.sha256(f"{route}|{training_block}|{tag}".encode("utf-8")).digest()[:8]
        seed=int.from_bytes(seed_bytes,"big",signed=False)
        rng=np.random.default_rng(seed)
        perm=rng.permutation(len(rows))
        for i,(_,key,_) in enumerate(rows):
            out[key]=float(values[perm[i]])
    return out


def simulate_case(psub,dsub,probs,site_shifts,species_shifts,r,den,obs_betas,
                  include_species,include_site,seed):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)
    nonzero_sites=[]
    nonzero_species=[]

    for i,d in enumerate(dsub):
        route=str(psub.iloc[i]["route_cluster"])
        test_block=str(psub.iloc[i]["test_block"])
        train_block="late" if test_block=="early" else "early"
        eta=uniform.logit(probs[d["key"]]).copy()
        rain=float(psub.iloc[i]["rain_contrast"])

        if include_site:
            smap=site_shifts[train_block]
            site_gamma=np.asarray([float(smap.get(f"{route}:{st}",0.0)) for st in d["stops"]],float)
            eta += site_gamma[None,:]*rain
            nonzero_sites.append(int(np.sum(np.abs(site_gamma)>0)))

        if include_species:
            test_route_fold=species_mod.fold_for_route(route)
            train_route_fold="B" if test_route_fold=="A" else "A"
            spmap=species_shifts[train_route_fold]
            species_gamma=np.asarray([float(spmap.get(sp,0.0)) for sp in d["species"]],float)
            eta += species_gamma[:,None]*rain
            nonzero_species.append(int(np.sum(np.abs(species_gamma)>0)))

        pre=uniform.expit(eta)
        q=uniform.solve_shift(pre,d["wet_k"])
        wsim=rng.random((B,)+q.shape)<q[None,:,:]
        numer += r[i]*uniform.simulated_components(wsim,d["dry"])

    betas=numer/den
    mean=betas.mean(axis=0)
    cov=np.cov(betas,rowvar=False,ddof=1)
    inv=np.linalg.pinv(cov)
    cen=betas-mean[None,:]
    dnull=np.einsum("bi,ij,bj->b",cen,inv,cen)
    dv=obs_betas-mean
    dobs=float(dv@inv@dv)
    p=float((1+np.sum(dnull>=dobs))/(B+1))

    total=betas.sum(axis=1)
    valid=np.isfinite(total)&(np.abs(total)>1e-12)
    shares=betas[valid]/total[valid,None]
    obs_shares=obs_betas/float(obs_betas.sum())
    boundary=1-shares[:,3]
    obs_boundary=float(1-obs_shares[3])
    lo,hi=np.quantile(boundary,[.025,.975])

    names=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
    return {
        "primary_omnibus":{
            "monte_carlo_p":p,
            "reject":bool(p<.05),
            "observed_mahalanobis":dobs,
        },
        "observed_component_betas":{names[j]:float(obs_betas[j]) for j in range(4)},
        "null_component_beta_mean":{names[j]:float(mean[j]) for j in range(4)},
        "boundary_crossing_share":{
            "observed":obs_boundary,
            "null_mean":float(np.mean(boundary)),
            "null_ci95":[float(lo),float(hi)],
        },
        "mean_nonzero_site_shifts_per_pair":float(np.mean(nonzero_sites)) if nonzero_sites else None,
        "mean_nonzero_species_shifts_per_pair":float(np.mean(nonzero_species)) if nonzero_species else None,
    }


def temporal_stability(site_early,audit_early,site_late,audit_late):
    common=sorted(
        k for k in site_early
        if k in site_late
        and audit_early.get(k,{}).get("estimable",False)
        and audit_late.get(k,{}).get("estimable",False)
    )
    a=np.asarray([site_early[k] for k in common],float)
    b=np.asarray([site_late[k] for k in common],float)
    if len(common)>=3 and np.std(a)>0 and np.std(b)>0:
        pearson=float(np.corrcoef(a,b)[0,1])
        rho,p=spearmanr(a,b)
        rho=float(rho); p=float(p)
    else:
        pearson=rho=p=None
    sign_agreement=float(np.mean(np.sign(a)==np.sign(b))) if len(common) else None
    return {
        "n_sites_estimable_both_blocks":int(len(common)),
        "pearson_gamma_correlation":pearson,
        "spearman_gamma_correlation":rho,
        "spearman_p":p,
        "sign_agreement":sign_agreement,
        "early_gamma_mean":float(np.mean(a)) if len(common) else None,
        "late_gamma_mean":float(np.mean(b)) if len(common) else None,
    }


def main():
    raw=base.load()
    runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)

    (
        pairs,pair_data,pools,dry_ids,sampled0,ss0,r0,den0,obs0,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)
    psub,dsub=site_mod.subset_pairs_and_data(pairs,pair_data)
    r,den,obs_betas=site_mod.observed_betas(psub,dsub)

    site_early,audit_early,rep_early=site_mod.fit_site_shifts(runs,sampled,ss,"early")
    site_late,audit_late,rep_late=site_mod.fit_site_shifts(runs,sampled,ss,"late")
    true_site={"early":site_early,"late":site_late}

    all_species=sorted({sp for species in pools.values() for sp in species})
    slopes_A,audit_A,fold_A=species_mod.fit_species_slopes(runs,sampled,ss,all_species,"A")
    slopes_B,audit_B,fold_B=species_mod.fit_species_slopes(runs,sampled,ss,all_species,"B")
    species_shifts={"A":slopes_A,"B":slopes_B}

    stops_by_key={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops_by_key,ss0)

    species_only=simulate_case(
        psub,dsub,probs,true_site,species_shifts,r,den,obs_betas,
        include_species=True,include_site=False,seed=SEED+33000
    )
    additive_true=simulate_case(
        psub,dsub,probs,true_site,species_shifts,r,den,obs_betas,
        include_species=True,include_site=True,seed=SEED+32000
    )

    perm_results={}
    for j,tag in enumerate(("perm1","perm2"),start=1):
        psite={
            "early":permute_site_shifts(site_early,"early",tag),
            "late":permute_site_shifts(site_late,"late",tag),
        }
        perm_results[tag]=simulate_case(
            psub,dsub,probs,psite,species_shifts,r,den,obs_betas,
            include_species=True,include_site=True,seed=SEED+34000+j
        )

    stability=temporal_stability(site_early,audit_early,site_late,audit_late)
    true_fits=not additive_true["primary_omnibus"]["reject"]
    species_rejects=species_only["primary_omnibus"]["reject"]
    perm_rejects=[x["primary_omnibus"]["reject"] for x in perm_results.values()]

    if true_fits and species_rejects and all(perm_rejects):
        identity_class="physical_site_identity_adds_predictive_information"
    elif true_fits and any(not x for x in perm_rejects):
        identity_class="generic_site_level_heterogeneity_sufficient_under_at_least_one_permutation"
    elif not true_fits:
        identity_class="true_additive_null_not_supported_in_diagnostic_rerun"
    else:
        identity_class="inconclusive"

    output={
        "analysis":"naamp_additive_null_identity_diagnostics_v0_1",
        "contract":"exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#additive_null_identity_diagnostics",
        "coverage":{
            "n_pairs":int(len(psub)),
            "n_routes":int(psub["route_cluster"].nunique()),
        },
        "site_shift_temporal_stability":stability,
        "species_only_same_subset":species_only,
        "true_additive_reference":additive_true,
        "permuted_site_identity_controls":perm_results,
        "classification":identity_class,
        "interpretation_boundary":{
            "post_readback_diagnostic":True,
            "physical_site_property_measured":False,
            "hydrology_measured":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
