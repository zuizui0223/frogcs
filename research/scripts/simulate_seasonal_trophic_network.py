#!/usr/bin/env python3
"""CONCEPTUAL ONLY: seasonal frog / salamander / dragonfly trophic motif.

Three ANNUAL breeding lineage abundances. Within-year larval/adult stages
enter via fixed activity kernels, NOT explicit stage-compartment demography.
Parameters are ARBITRARY synthetic draws: not field estimates or GloBI rates.
'Coexistence' is only apparent persistence across 4 starting conditions.
"""
import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

SEED=20261025
D_PHASES=(0.,.1,.2,.3,.4,.5)
S_PHASES=(0.,.13,.26)
N_PARAMS=256
T=np.linspace(0,1,240,endpoint=False)


def kernel(mu,width=.11):
    delta=np.abs(T-mu)%1
    delta=np.minimum(delta,1-delta)
    return np.exp(-.5*(delta/width)**2)


def edge_windows(phi_d,phi_s):
    """Direct predator/food-stage exposures, except D→S is also risk cue."""
    tad=kernel(.25)
    frog=kernel(.68)
    sal=kernel(.27+phi_s)
    dnymph=kernel(.29+phi_d)
    dem=kernel(.68+phi_d,.075)
    return {
        "salamander_larva_eats_frog_tadpole":float(np.mean(sal*tad)),
        "dragonfly_nymph_eats_frog_tadpole":float(np.mean(dnymph*tad)),
        "dragonfly_nymph_risk_to_salamander_larva":float(np.mean(dnymph*sal)),
        "frog_adult_eats_emerging_dragonfly":float(np.mean(frog*dem)),
    }


def draw_parameter_ensemble(n=N_PARAMS):
    rng=np.random.default_rng(SEED)
    return {
        "r":rng.uniform(1.4,3,(n,3)),
        "K":rng.uniform(30,120,(n,3)),
        "a":np.exp(rng.uniform(np.log(.01),np.log(.20),(n,4))),
        "benefit":rng.uniform(0,1.2,(n,3)),
        "dragonfly_risk":rng.uniform(0,.12,n),
    }


def integrate_years(param,edge,vegetation=.35,years=550,last=50):
    """Positivity-preserving Beverton-Holt-style 3-guild annual map.

    Risk suppression: dragonfly larvae reduce salamander frog feeding.
    Tadpole submerged-cover shelter lowers S→F and D→F attack rates.
    Dragonfly metamorph emerges when adult frog can eat it.
    Other trophic feeding supplements reproduction using arbitrary factors.
    """
    n=param["r"].shape[0]
    state=np.full((4,n,3),45.)
    for g in range(3):
        state[g+1,:,g]=.15  # each species tested rare in turn
    tail=np.full_like(state,np.inf)
    sf=edge["salamander_larva_eats_frog_tadpole"]
    df=edge["dragonfly_nymph_eats_frog_tadpole"]
    ds=edge["dragonfly_nymph_risk_to_salamander_larva"]
    fd=edge["frog_adult_eats_emerging_dragonfly"]
    for year in range(years):
        f,s,d=state[:,:,0],state[:,:,1],state[:,:,2]
        benefit=param["benefit"]
        r=param["r"]
        k=param["K"]
        a=param["a"]
        rf=r[:,0][None,:]*(1+benefit[:,0][None,:]*d/(50+d)*fd/.18)
        rs=r[:,1][None,:]*(1+benefit[:,1][None,:]*f/(50+f)*sf/.18)
        rd=r[:,2][None,:]*(1+benefit[:,2][None,:]*
                              (f/(50+f)*df+s/(50+s)*ds)/.18)
        shelter=math.exp(-1.3*vegetation)
        risk_to_f=(a[:,0][None,:]*s*sf*shelter/
                   (1+param["dragonfly_risk"][None,:]*d*ds)
                   + a[:,1][None,:]*d*df*shelter)
        risk_to_s=a[:,2][None,:]*d*ds
        risk_to_d=a[:,3][None,:]*f*fd*(1+.7*vegetation)
        nxt=np.stack([
            rf*f/(1+f/k[:,0][None,:])*np.exp(-np.minimum(risk_to_f,700)),
            rs*s/(1+s/k[:,1][None,:])*np.exp(-np.minimum(risk_to_s,700)),
            rd*d/(1+d/k[:,2][None,:])*np.exp(-np.minimum(risk_to_d,700))
        ],axis=2)
        if not np.isfinite(nxt).all() or np.any(nxt<0):
            raise ValueError("Invalid negative/nonfinite population")
        state=np.clip(nxt,0,1e6)
        if year>=years-last:
            tail=np.minimum(tail,state)
    # Not mutual-invasion test: persistence under several initial conditions.
    persistent=np.all(tail>1,axis=(0,2))
    return {
        "persistent_draws":int(np.sum(persistent)),
        "fraction_persistent_draws":float(np.mean(persistent)),
        "frog_salamander_dragonfly_median_final_common_start":list(
            np.median(state[0],axis=0).astype(float)),
    }


def run(out):
    param=draw_parameter_ensemble()
    data=[]
    for ps in S_PHASES:
        for pd in D_PHASES:
            edges=edge_windows(pd,ps)
            result=integrate_years(param,edges)
            data.append({
                "salamander_offset_of_annual_cycle":ps,
                "dragonfly_offset_of_annual_cycle":pd,
                **edges,
                "robust_three_guild_persistence_fraction_synthetic":
                    result["fraction_persistent_draws"],
                "robust_persistent_draws_synthetic":result["persistent_draws"],
            })
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    with (out/"synthetic_phase_sweep.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)
    ordered=sorted(data,key=lambda x:x[
        "robust_three_guild_persistence_fraction_synthetic"])
    receipt={
        "study_type":"SYNTHETIC_DETERMINISTIC_THOUGHT_EXPERIMENT",
        "random_seed":SEED,"draws":N_PARAMS,"years":550,
        "last_years_for_survival":50,
        "vegetation_fixed":.35,
        "rare_species_initial_conditions":"each one of F,S,D initially 0.15, others 45; plus all initially 45",
        "phenological_offsets_tested":len(data),
        "weakest_parameter_coexistence_example":ordered[0],
        "strongest_parameter_coexistence_example":ordered[-1],
        "all_phase_results":data,
        "interpretation":"No general theorem that more synchronized development increases coexistence. This annual-map model may display nonmonotonic or opposing regimes.",
        "important_cautions":[
            "Artificial parameter ensemble, synthetic populations, no fitted field feeding, no real wetland life cycle.",
            "Stage-specific phenology is exogenously imposed. This is NOT a fully stage-structured demographic model or verified ABM/PDE.",
            "Persistent abundance above threshold from 4 starts is not mathematical mutual invasibility.",
            "The real Japanese dragonfly-salamander-frog cue experiments and Australian frog-dragonfly role reversal are different species/community systems.",
            "No claims about natural trophic dominance, wetland vegetation effects, frog chorus, eDNA or global coexistence fractions.",
        ],
    }
    (out/"synthetic_results.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_SYNTHETIC_STAGE_NETWORK")
    print(json.dumps({k:v for k,v in receipt.items() if k!="all_phase_results"},
                     ensure_ascii=False,indent=2))
    print("END_SYNTHETIC_STAGE_NETWORK")


def selftest():
    initial=edge_windows(0,0)
    displaced=edge_windows(.3,0)
    assert initial["dragonfly_nymph_eats_frog_tadpole"] > displaced[
        "dragonfly_nymph_eats_frog_tadpole"]
    assert initial["frog_adult_eats_emerging_dragonfly"] > displaced[
        "frog_adult_eats_emerging_dragonfly"]
    p=draw_parameter_ensemble(12)
    result=integrate_years(p,initial,years=150)
    assert 0<=result["fraction_persistent_draws"]<=1
    assert result["persistent_draws"]<=12
    print("STAGE_TEMPORAL_NETWORK_POSITIVITY_AND_RARE_START_QA_PASS")


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="research/results/synthetic_stage_network")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:selftest()
    else:run(args.out)
