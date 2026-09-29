#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_CLUSTER_ROUTE_SPLIT_REPLICATION_RECEIPT_V0_1.json"
B=1000; KAPPA=2.0; ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")

def fold(route):
    return "A" if hashlib.sha256(str(route).encode()).digest()[0]<128 else "B"

def metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    k=w.sum(axis=1)
    extra=float(np.sum(np.maximum(k-1,0)*route_new))
    adj=0.0
    for s in np.flatnonzero(route_new):
        occ=w[s]
        adj+=float(np.sum(occ[:-1]&occ[1:]))
    return np.asarray([extra,adj])

def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2)
    extra=(np.maximum(k-1,0)*route_new).sum(axis=1).astype(float)
    adj=((w[:,:,:-1]&w[:,:,1:]).sum(axis=2)*route_new).sum(axis=1).astype(float)
    return np.column_stack([extra,adj])

def conditional(sim,obs):
    X=np.column_stack([np.ones(len(sim)),sim[:,0]])
    coef=np.linalg.lstsq(X,sim[:,1],rcond=None)[0]
    resid=sim[:,1]-X@coef
    pred=float(coef[0]+coef[1]*obs[0])
    ores=float(obs[1]-pred)
    lo,hi=np.quantile(resid,[.025,.975])
    return {
      "null_regression_intercept":float(coef[0]),"null_regression_slope":float(coef[1]),
      "null_residual_ci95":[float(lo),float(hi)],"observed_conditional_residual":ores,
      "observed_extra_beta":float(obs[0]),"observed_adjacent_beta":float(obs[1]),
      "predicted_adjacent_beta":pred,
      "upper_tail_p":float((1+np.sum(resid>=ores))/(len(resid)+1)),
      "above_upper_95":bool(ores>hi)
    }

def run_fold(fname,pairs,pair_data,pools,dry_ids,ss,seedoff):
    mask=np.asarray([fold(x)==fname for x in pairs["route_cluster"].astype(str)],bool)
    idx=np.flatnonzero(mask)
    p=pairs.iloc[idx].copy().reset_index(drop=True)
    d=[pair_data[int(i)] for i in idx]
    r,den=uniform.design_residual(p)
    obsrows=np.asarray([metrics(x["wet"],x["dry"]) for x in d],float)
    obs=(r[:,None]*obsrows).sum(axis=0)/den

    keys={x["key"] for x in d}
    pools_sub={k:pools[k] for k in keys}
    dry_sub=defaultdict(set)
    for row in p.itertuples(index=False):
        key=(str(row.State),str(row.RouteNumber),str(row.RunNumber))
        dry_sub[key].add(str(row.dry_RunID))
    stops={x["key"]:x["stops"] for x in d}
    probs=uniform.baseline_probs(KAPPA,pools_sub,dry_sub,stops,ss)
    hist=persistence.historical_cell_probs(pools_sub,dry_sub,stops,ss)

    def simulate(kind,seed):
        rng=np.random.default_rng(seed); num=np.zeros((B,2),float)
        for i,x in enumerate(d):
            if kind=="uniform":
                basep=probs[x["key"]]
            else:
                basep=(1-ANCHOR)*hist[x["key"]]+ANCHOR*x["dry"].astype(float)
                basep=np.clip(basep,1e-8,1-1e-8)
            q=uniform.solve_shift(basep,x["wet_k"])
            w=rng.random((B,)+q.shape)<q[None,:,:]
            num += r[i]*sim_metrics(w,x["dry"])
        return num/den

    ub=simulate("uniform",uniform.SEED+seedoff)
    pb=simulate("persistence",uniform.SEED+seedoff+1000)
    u=conditional(ub,obs); q=conditional(pb,obs)
    passed=bool(u["above_upper_95"] and q["above_upper_95"])
    return {
      "n_pairs":int(len(p)),"n_routes":int(p.route_cluster.nunique()),
      "observed":{"extra_stop_beta":float(obs[0]),"adjacent_stop_beta":float(obs[1])},
      "uniform_kappa2":u,"persistence_anchor_0_75":q,"fold_pass":passed
    }

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r,den,obs,bm,rb,db,os=uniform.prepare()
    pairs=pairs.copy().reset_index(drop=True)
    A=run_fold("A",pairs,pair_data,pools,dry_ids,ss,81000)
    Bx=run_fold("B",pairs,pair_data,pools,dry_ids,ss,83000)
    out={
      "analysis":"naamp_cluster_route_split_replication_v0_1",
      "contract":"exploration/NAAMP_CLUSTER_ROUTE_SPLIT_REPLICATION_CONTRACT_V0_1.json",
      "folds":{"A":A,"B":Bx},
      "classification":{"both_disjoint_route_folds_pass":bool(A["fold_pass"] and Bx["fold_pass"])},
      "interpretation_boundary":{"cross_continental_universality":False,"causal_hydrology_identified":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
