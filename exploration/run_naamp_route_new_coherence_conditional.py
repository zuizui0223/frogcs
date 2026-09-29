#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_COHERENCE_CONDITIONAL_RECEIPT_V0_1.json"
B=1000
KAPPA=2.0
ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

def metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    k=w[route_new].sum(axis=1) if np.any(route_new) else np.asarray([],int)
    return np.asarray([
      float(np.sum(route_new)),
      float(np.sum(np.maximum(k-1,0))) if len(k) else 0.0
    ])

def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2)
    n=route_new.sum(axis=1).astype(float)
    extra=(np.maximum(k-1,0)*route_new).sum(axis=1).astype(float)
    return np.column_stack([n,extra])

def simulate(pair_data,probmaker,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,2),float)
    for i,d in enumerate(pair_data):
        q=probmaker(d)
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metrics(w,d["dry"])
    return num/den

def conditional(sim,obs):
    x=sim[:,0]; y=sim[:,1]
    X=np.column_stack([np.ones(len(x)),x])
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef
    resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0])
    obs_resid=float(obs[1]-obs_pred)
    lo,hi=np.quantile(resid,[.025,.975])
    p=float((1+np.sum(resid>=obs_resid))/(len(resid)+1))
    return {
      "null_regression_intercept":float(coef[0]),
      "null_regression_slope":float(coef[1]),
      "null_residual_ci95":[float(lo),float(hi)],
      "observed_new_species_beta":float(obs[0]),
      "observed_extra_stop_beta":float(obs[1]),
      "predicted_extra_beta_at_observed_new_species":obs_pred,
      "observed_conditional_residual":obs_resid,
      "upper_tail_p":p,
      "above_upper_95":bool(obs_resid>hi)
    }

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs0,bm,rb,db,os=uniform.prepare()
    obs_rows=np.asarray([metrics(d["wet"],d["dry"]) for d in pair_data],float)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den
    stops={d["key"]:d["stops"] for d in pair_data}
    probs=uniform.baseline_probs(KAPPA,pools,dry_ids,stops,ss)
    def qu(d): return uniform.solve_shift(probs[d["key"]],d["wet_k"])
    hist=persistence.historical_cell_probs(pools,dry_ids,stops,ss)
    def qp(d):
        p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float)
        p=np.clip(p,1e-8,1-1e-8)
        return uniform.solve_shift(p,d["wet_k"])
    ub=simulate(pair_data,qu,r,den,uniform.SEED+61000)
    pb=simulate(pair_data,qp,r,den,uniform.SEED+62000)
    u=conditional(ub,obs); p=conditional(pb,obs)
    support=bool(u["above_upper_95"] and p["above_upper_95"])
    out={
      "analysis":"naamp_route_new_coherence_conditional_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_COHERENCE_CONDITIONAL_CONTRACT_V0_1.json",
      "n_pairs":int(len(pairs)),
      "observed":{"route_new_species_gain_beta":float(obs[0]),"extra_stop_incidence_gain_beta":float(obs[1])},
      "uniform_kappa2":u,
      "persistence_anchor_0_75":p,
      "classification":{"conditional_spatial_coherence_excess_supported":support},
      "interpretation_boundary":{"individual_movement_inferred":False,"broad_cue_identified":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
