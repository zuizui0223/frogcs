#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPECIES_SPREAD_RECEIPT_V0_1.json"
B=1000; KAPPA=2.0; ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

def observed_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    k=w[route_new].sum(axis=1) if np.any(route_new) else np.asarray([],int)
    return np.asarray([
      float(np.sum(route_new)),
      float(np.sum(np.maximum(k-1,0))) if len(k) else 0.0,
      float(np.sum(k>=2)) if len(k) else 0.0
    ])

def simulated_metrics(w,d):
    # w B x species x stop
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:]) & w.any(axis=2)
    k=w.sum(axis=2)
    n=route_new.sum(axis=1).astype(float)
    extra=(np.maximum(k-1,0)*route_new).sum(axis=1).astype(float)
    multi=((k>=2)&route_new).sum(axis=1).astype(float)
    return np.column_stack([n,extra,multi])

def simulate(pair_data,probmaker,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,3),float)
    for i,dct in enumerate(pair_data):
        q=probmaker(dct)
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*simulated_metrics(w,dct["dry"])
    return num/den

def stat(v,obs):
    lo,hi=np.quantile(v,[.025,.975])
    return {"null_mean":float(np.mean(v)),"null_ci95":[float(lo),float(hi)],"observed":float(obs),
            "upper_tail_p":float((1+np.sum(v>=obs))/(len(v)+1))}

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs_comp,bm,rb,db,os=uniform.prepare()
    obs_rows=np.asarray([observed_metrics(d["wet"],d["dry"]) for d in pair_data],float)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den
    stops={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops,ss)
    def q_uniform(d):
        return uniform.solve_shift(probs[d["key"]],d["wet_k"])
    hist=persistence.historical_cell_probs(pools,dry_ids,stops,ss)
    def q_persist(d):
        p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float)
        p=np.clip(p,1e-8,1-1e-8)
        return uniform.solve_shift(p,d["wet_k"])
    ub=simulate(pair_data,q_uniform,r,den,uniform.SEED+41000)
    pb=simulate(pair_data,q_persist,r,den,uniform.SEED+42000)
    names=["route_new_species_gain","extra_stop_incidence_gain","multi_stop_route_new_species"]
    u={names[j]:stat(ub[:,j],obs[j]) for j in range(3)}
    p={names[j]:stat(pb[:,j],obs[j]) for j in range(3)}
    broad=bool(obs[1]>u[names[1]]["null_ci95"][1] and obs[1]>p[names[1]]["null_ci95"][1])
    out={
      "analysis":"naamp_route_new_species_spread_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_SPECIES_SPREAD_CONTRACT_V0_1.json",
      "n_pairs":int(len(pairs)),
      "observed_betas":{names[j]:float(obs[j]) for j in range(3)},
      "uniform_kappa2":u,
      "persistence_anchor_0_75":p,
      "classification":{"excess_broad_species_activation_supported":broad,"localized_recruitment_not_rejected":bool(not broad)},
      "interpretation_boundary":{"individual_movement_inferred":False,"local_hydrology_identified":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
