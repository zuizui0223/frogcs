#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_CONTIGUITY_ROBUST_RECEIPT_V0_1.json"
B=1000; KAPPA=2.0; ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persistence",NAAMP/"run_naamp_persistence_preserving_null.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st: continue
        if sid: vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad: raise RuntimeError(f"multiple SiteIDs: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}

def stable(p,site,stops):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    return all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in stops)

def metrics(w,d):
    droute=d.any(axis=1); route_new=(~droute)&w.any(axis=1); k=w.sum(axis=1)
    extra=float(np.sum(np.maximum(k-1,0)*route_new)); adj=0.0
    for s in np.flatnonzero(route_new):
        occ=w[s]; adj+=float(np.sum(occ[:-1]&occ[1:]))
    return np.asarray([extra,adj],float)

def sim_metrics(w,d):
    droute=d.any(axis=1); route_new=(~droute[None,:])&w.any(axis=2); k=w.sum(axis=2)
    extra=(np.maximum(k-1,0)*route_new).sum(axis=1).astype(float)
    adj=((w[:,:,:-1]&w[:,:,1:]).sum(axis=2)*route_new).sum(axis=1).astype(float)
    return np.column_stack([extra,adj])

def conditional(sim,obs):
    x=sim[:,0]; y=sim[:,1]; X=np.column_stack([np.ones(len(x)),x])
    coef=np.linalg.lstsq(X,y,rcond=None)[0]; resid=y-X@coef
    pred=float(coef[0]+coef[1]*obs[0]); ores=float(obs[1]-pred); lo,hi=np.quantile(resid,[.025,.975])
    return {"null_residual_ci95":[float(lo),float(hi)],"observed_residual":ores,
            "predicted_adjacent_at_observed_extra":pred,
            "upper_tail_p":float((1+np.sum(resid>=ores))/(len(resid)+1)),
            "above_upper_95":bool(ores>hi)}

def main():
    pairs,pair_data,pools,dry_ids,sampled,ss,r0,den0,obs0,bm,rb,db,os=uniform.prepare()
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    site=site_map(raw,eligible)
    keep=[]
    for p,d in zip(pairs.itertuples(index=False),pair_data):
        key=(str(p.wet_RunID),str(p.dry_RunID))
        keep.append(key in same_keys and stable(p,site,d["stops"]))
    idx=np.flatnonzero(np.asarray(keep,bool))
    psub=pairs.iloc[idx].copy().reset_index(drop=True); dsub=[pair_data[int(i)] for i in idx]
    if len(psub)<2500: raise RuntimeError(f"robust subset too small {len(psub)}")
    r,den=uniform.design_residual(psub)
    obsrows=np.asarray([metrics(d["wet"],d["dry"]) for d in dsub],float); obs=(r[:,None]*obsrows).sum(axis=0)/den

    keys={d["key"] for d in dsub}; pools_sub={k:pools[k] for k in keys}; dry_sub=defaultdict(set)
    for p in psub.itertuples(index=False):
        dry_sub[(str(p.State),str(p.RouteNumber),str(p.RunNumber))].add(str(p.dry_RunID))
    stops={d["key"]:d["stops"] for d in dsub}
    probs=uniform.baseline_probs(KAPPA,pools_sub,dry_sub,stops,ss)
    hist=persistence.historical_cell_probs(pools_sub,dry_sub,stops,ss)

    def simulate(kind,seed):
        rng=np.random.default_rng(seed); num=np.zeros((B,2),float)
        for i,d in enumerate(dsub):
            if kind=="uniform": p=probs[d["key"]]
            else:
                p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float); p=np.clip(p,1e-8,1-1e-8)
            q=uniform.solve_shift(p,d["wet_k"]); w=rng.random((B,)+q.shape)<q[None,:,:]
            num+=r[i]*sim_metrics(w,d["dry"])
        return num/den

    ub=simulate("uniform",uniform.SEED+81000); pb=simulate("persistence",uniform.SEED+82000)
    uc=conditional(ub,obs); pc=conditional(pb,obs)
    out={"analysis":"naamp_route_new_contiguity_robust_v0_1",
         "contract":"exploration/NAAMP_ROUTE_NEW_CONTIGUITY_ROBUST_CONTRACT_V0_1.json",
         "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_cluster.nunique())},
         "observed":{"extra_stop_beta":float(obs[0]),"adjacent_stop_beta":float(obs[1])},
         "uniform_kappa2":uc,"persistence_anchor_0_75":pc,
         "classification":{"conditional_local_contiguity_excess_supported":bool(uc["above_upper_95"] and pc["above_upper_95"])},
         "interpretation_boundary":{"observer_turnover_required":False,"physical_stop_relocation_required":False,"causal_rainfall_claim":False}}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
