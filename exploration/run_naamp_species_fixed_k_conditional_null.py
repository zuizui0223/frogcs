#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, itertools, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_SPECIES_FIXED_K_CONDITIONAL_NULL_RECEIPT_V0_1.json"
B=1000
SEED=2840223
KAPPA=2.0
ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

COMBOS={}
MASKS={}
for k in range(11):
    cs=list(itertools.combinations(range(10),k))
    COMBOS[k]=cs
    arr=np.zeros((len(cs),10),dtype=bool)
    for i,c in enumerate(cs):
        if c:
            arr[i,list(c)]=True
    MASKS[k]=arr

def conditional_draws(rng,p,k):
    p=np.clip(np.asarray(p,float),1e-8,1-1e-8)
    if k<=0:
        return np.zeros((B,10),dtype=bool)
    if k>=10:
        return np.ones((B,10),dtype=bool)
    masks=MASKS[int(k)]
    logodds=np.log(p)-np.log1p(-p)
    lp=masks.astype(float)@logodds
    lp-=float(np.max(lp))
    w=np.exp(lp)
    w/=float(np.sum(w))
    idx=rng.choice(len(masks),size=B,replace=True,p=w)
    return masks[idx]

def simulate(pair_data,prob_by_key,r,den,seed,anchor=False):
    rng=np.random.default_rng(seed)
    numer=np.zeros((B,4),float)
    for i,d in enumerate(pair_data):
        p=np.asarray(prob_by_key[d["key"]],float)
        if anchor:
            p=(1-ANCHOR)*p+ANCHOR*d["dry"].astype(float)
            p=np.clip(p,1e-8,1-1e-8)
        k=d["wet"].sum(axis=1).astype(int)
        wsim=np.zeros((B,p.shape[0],10),dtype=bool)
        for s,ks in enumerate(k):
            if ks==0:
                continue
            wsim[:,s,:]=conditional_draws(rng,p[s],int(ks))
        # exact conditioning audit
        if not np.all(wsim.sum(axis=2)==k[None,:]):
            raise RuntimeError("species fixed-k identity failed")
        comps=uniform.simulated_components(wsim,d["dry"])
        numer+=r[i]*comps
    return numer/den

def summarize(betas,obs):
    mean=betas.mean(axis=0)
    cov=np.cov(betas,rowvar=False,ddof=1)
    inv=np.linalg.pinv(cov)
    cen=betas-mean[None,:]
    dnull=np.einsum("bi,ij,bj->b",cen,inv,cen)
    dv=obs-mean
    dobs=float(dv@inv@dv)
    p=float((1+np.sum(dnull>=dobs))/(B+1))

    total=betas.sum(axis=1)
    valid=np.isfinite(total)&(np.abs(total)>1e-12)
    shares=betas[valid]/total[valid,None]
    obs_shares=obs/float(obs.sum())
    boundary=1-shares[:,3]
    obs_boundary=float(1-obs_shares[3])
    taxsp=shares[:,2]-shares[:,1]
    obs_taxsp=float(obs_shares[2]-obs_shares[1])

    def stat(v,o):
        lo,hi=np.quantile(v,[.025,.975])
        return {
            "null_mean":float(np.mean(v)),
            "null_ci95":[float(lo),float(hi)],
            "observed":float(o),
            "observed_percentile":float((1+np.sum(v<=o))/(len(v)+1)),
        }

    names=["corner_expansion","spatial_spread","taxonomic_deepening","within_core_rearrangement"]
    return {
        "primary_omnibus":{
            "observed_mahalanobis":dobs,
            "monte_carlo_p":p,
            "reject":bool(p<.05),
        },
        "observed_component_betas":{names[j]:float(obs[j]) for j in range(4)},
        "null_component_beta_mean":{names[j]:float(mean[j]) for j in range(4)},
        "component_shares":{names[j]:stat(shares[:,j],obs_shares[j]) for j in range(4)},
        "boundary_crossing_share":stat(boundary,obs_boundary),
        "taxonomic_minus_spatial_share":stat(taxsp,obs_taxsp),
        "valid_share_replicates":int(valid.sum()),
    }

def main():
    (
        pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs,
        beta_mask,r_beta,den_beta,obs_sor
    )=uniform.prepare()

    stops_by_key={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops_by_key,ss)

    history=simulate(
        pair_data,probs,r,den,
        seed=SEED+81000,
        anchor=False
    )
    persist=simulate(
        pair_data,probs,r,den,
        seed=SEED+82000,
        anchor=True
    )

    h=summarize(history,obs)
    p=summarize(persist,obs)

    if not h["primary_omnibus"]["reject"] and not p["primary_omnibus"]["reject"]:
        decision="species_activation_depth_sufficient_without_special_stop_placement"
    elif h["primary_omnibus"]["reject"] and not p["primary_omnibus"]["reject"]:
        decision="species_activation_depth_plus_dry_persistence_sufficient"
    elif not h["primary_omnibus"]["reject"] and p["primary_omnibus"]["reject"]:
        decision="history_weighted_fixed_k_sufficient_but_persistence_variant_rejects"
    else:
        decision="species_fixed_k_still_insufficient"

    wet_k=np.concatenate([d["wet"].sum(axis=1) for d in pair_data])
    wet_positive=wet_k[wet_k>0]
    output={
        "analysis":"naamp_species_fixed_k_conditional_null_v0_1",
        "contract":"exploration/NAAMP_SPECIES_FIXED_K_CONDITIONAL_NULL_CONTRACT_V0_1.json",
        "coverage":{
            "pairs":int(len(pairs)),
            "routes":int(pairs.route_cluster.nunique()),
            "states":int(pairs.State.nunique()),
        },
        "conditioned_wet_species_depth":{
            "active_species_instances":int(len(wet_positive)),
            "mean_k":float(np.mean(wet_positive)),
            "median_k":float(np.median(wet_positive)),
            "fraction_k_ge_2":float(np.mean(wet_positive>=2)),
            "fraction_k_ge_3":float(np.mean(wet_positive>=3)),
        },
        "history_weighted_fixed_k":h,
        "persistence_weighted_fixed_k":p,
        "decision":decision,
        "interpretation_boundary":{
            "response_conditioned_species_identity":True,
            "response_conditioned_species_stop_count":True,
            "predictive_null":False,
            "causal_rainfall_claim":False,
            "individual_movement_inferred":False,
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
