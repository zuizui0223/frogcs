#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_CONTIGUITY_RECEIPT_V0_1.json"
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
    k=w.sum(axis=1)
    extra=float(np.sum(np.maximum(k-1,0)*route_new))
    adj=0.0
    for s in np.flatnonzero(route_new):
        occ=w[s]
        adj += float(np.sum(occ[:-1]&occ[1:]))
    return np.asarray([extra,adj],float)

def sim_metrics(w,d):
    # w: B x species x stop
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2)
    extra=(np.maximum(k-1,0)*route_new).sum(axis=1).astype(float)
    adj=((w[:,:,:-1]&w[:,:,1:]).sum(axis=2)*route_new).sum(axis=1).astype(float)
    return np.column_stack([extra,adj])

def simulate(pair_data,probmaker,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,2),float)
    for i,d in enumerate(pair_data):
        q=probmaker(d)
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metrics(w,d["dry"])
    return num/den

def marginal(v,obs):
    lo,hi=np.quantile(v,[.025,.975])
    return {"null_mean":float(np.mean(v)),"null_ci95":[float(lo),float(hi)],"observed":float(obs),
            "upper_tail_p":float((1+np.sum(v>=obs))/(len(v)+1))}

def conditional(sim,obs):
    x=sim[:,0]; y=sim[:,1]
    X=np.column_stack([np.ones(len(x)),x])
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    resid=y-X@coef
    pred=float(coef[0]+coef[1]*obs[0])
    ores=float(obs[1]-pred)
    lo,hi=np.quantile(resid,[.025,.975])
    return {
      "null_regression_intercept":float(coef[0]),
      "null_regression_slope":float(coef[1]),
      "null_residual_ci95":[float(lo),float(hi)],
      "observed_extra_stop_beta":float(obs[0]),
      "observed_adjacent_beta":float(obs[1]),
      "predicted_adjacent_beta_at_observed_extra":pred,
      "observed_conditional_residual":ores,
      "upper_tail_p":float((1+np.sum(resid>=ores))/(len(resid)+1)),
      "above_upper_95":bool(ores>hi)
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
    ub=simulate(pair_data,qu,r,den,uniform.SEED+71000)
    pb=simulate(pair_data,qp,r,den,uniform.SEED+72000)
    ucond=conditional(ub,obs); pcond=conditional(pb,obs)
    out={
      "analysis":"naamp_route_new_contiguity_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_CONTIGUITY_CONTRACT_V0_1.json",
      "n_pairs":int(len(pairs)),
      "observed":{"extra_stop_beta":float(obs[0]),"adjacent_stop_beta":float(obs[1])},
      "uniform_kappa2":{"adjacent_marginal":marginal(ub[:,1],obs[1]),"conditional":ucond},
      "persistence_anchor_0_75":{"adjacent_marginal":marginal(pb[:,1],obs[1]),"conditional":pcond},
      "classification":{"conditional_local_contiguity_excess_supported":bool(ucond["above_upper_95"] and pcond["above_upper_95"])},
      "interpretation_boundary":{"individual_movement_inferred":False,"hydrological_connectivity_identified":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
