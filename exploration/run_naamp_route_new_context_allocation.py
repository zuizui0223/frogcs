#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_CONTEXT_ALLOCATION_RECEIPT_V0_1.json"
B=1000
KAPPA=2.0
ANCHOR=0.75

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod

uniform=loadmod("uniform_base",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence_base",NAAMP/"run_naamp_persistence_preserving_null.py")

def simulate_uniform(pair_data,probs,r,den):
    rng=np.random.default_rng(uniform.SEED+int(KAPPA*1000))
    num=np.zeros((B,4),float)
    for i,d in enumerate(pair_data):
        q=uniform.solve_shift(probs[d["key"]],d["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*uniform.simulated_components(w,d["dry"])
    return num/den

def simulate_persist(pair_data,hist,r,den):
    rng=np.random.default_rng(uniform.SEED+int(round(ANCHOR*10000)))
    num=np.zeros((B,4),float)
    for i,d in enumerate(pair_data):
        p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float)
        p=np.clip(p,1e-8,1-1e-8)
        q=uniform.solve_shift(p,d["wet_k"])
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*uniform.simulated_components(w,d["dry"])
    return num/den

def frac(betas):
    den=betas[:,0]+betas[:,2]
    ok=np.isfinite(den)&(np.abs(den)>1e-12)
    return betas[ok,2]/den[ok]

def summary(v,obs):
    lo,hi=np.quantile(v,[.025,.975])
    return {
      "null_mean":float(np.mean(v)),
      "null_ci95":[float(lo),float(hi)],
      "observed":float(obs),
      "upper_tail_p":float((1+np.sum(v>=obs))/(len(v)+1)),
      "lower_tail_p":float((1+np.sum(v<=obs))/(len(v)+1))
    }

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs,bm,rb,db,os=uniform.prepare()
    obs_den=float(obs[0]+obs[2])
    if abs(obs_den)<=1e-12: raise RuntimeError("observed route-new denominator is zero")
    observed=float(obs[2]/obs_den)
    stops={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops,ss)
    ub=simulate_uniform(pair_data,probs,r,den)
    hist=persistence.historical_cell_probs(pools,dry_ids,stops,ss)
    pb=simulate_persist(pair_data,hist,r,den)
    uf=frac(ub); pf=frac(pb)
    us=summary(uf,observed); ps=summary(pf,observed)
    social=bool(observed>us["null_ci95"][1] and observed>ps["null_ci95"][1])
    opening=bool(observed<us["null_ci95"][0] and observed<ps["null_ci95"][0])
    out={
      "analysis":"naamp_route_new_context_allocation_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_CONTEXT_ALLOCATION_CONTRACT_V0_1.json",
      "n_pairs":int(len(pairs)),
      "observed":{
        "corner_beta":float(obs[0]),
        "taxonomic_beta":float(obs[2]),
        "route_new_dry_active_fraction":observed
      },
      "uniform_kappa2":us,
      "persistence_anchor_0_75":ps,
      "classification":{
        "simple_social_cue_excess_supported":social,
        "simple_new_site_opening_excess_supported":opening,
        "neutral_relative_to_both_nulls":bool(not social and not opening)
      },
      "interpretation_boundary":{
        "chorus_presence_measured_directly":False,
        "hydrological_site_opening_measured_directly":False,
        "causal_rainfall_claim":False,
        "submission_story_change_authorized":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
