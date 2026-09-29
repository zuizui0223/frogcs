#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPREAD_ROBUSTNESS_RECEIPT_V0_1.json"
B=1000; KAPPA=2.0; ANCHOR=.75; SEED=2840223

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
persistence=loadmod("persist",NAAMP/"run_naamp_persistence_preserving_null.py")
base=uniform.base
spatial=uniform.spatial
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def site_map(raw,eligible):
    vals=defaultdict(set)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip(); st=(s.get("StopNumber") or "").strip(); sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0" or not st: continue
        if sid: vals[(rid,st)].add(sid)
    bad={k:v for k,v in vals.items() if len(v)>1}
    if bad: raise RuntimeError(f"SiteID conflicts {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID); sw=set(sampled[w]); sd=set(sampled[d])
    if len(sw)!=10 or sw!=sd: return False
    return all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in sw)

def obs_metric(w,d):
    dn=d.any(axis=1)
    new=(~dn)&w.any(axis=1)
    k=w[new].sum(axis=1) if np.any(new) else np.asarray([],int)
    return np.asarray([
      float(np.sum(np.maximum(k-1,0))) if len(k) else 0.0,
      float(np.sum(k>=2)) if len(k) else 0.0,
      float(np.sum(new))
    ])

def sim_metric(w,d):
    dr=d.any(axis=1)
    new=(~dr[None,:]) & w.any(axis=2)
    k=w.sum(axis=2)
    return np.column_stack([
      (np.maximum(k-1,0)*new).sum(axis=1).astype(float),
      ((k>=2)&new).sum(axis=1).astype(float),
      new.sum(axis=1).astype(float)
    ])

def simulate(dsub,probmaker,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,3),float)
    for i,d in enumerate(dsub):
        q=probmaker(d)
        w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metric(w,d["dry"])
    return num/den

def stat(v,obs):
    lo,hi=np.quantile(v,[.025,.975])
    return {"null_mean":float(np.mean(v)),"null_ci95":[float(lo),float(hi)],"observed":float(obs),"upper_tail_p":float((1+np.sum(v>=obs))/(len(v)+1))}

def main():
    pairs,pair_data,pools,dry_ids_all,sampled,ss,r0,den0,ob0,bm,rb,db,os=uniform.prepare()
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    site=site_map(raw,eligible)
    same=same.copy().reset_index(drop=True)
    same["stable"]=[stable(p,sampled,site) for p in same.itertuples(index=False)]
    sel=same[same.stable].copy().reset_index(drop=True)
    key_to_idx={(str(p.wet_RunID),str(p.dry_RunID)):i for i,p in enumerate(pairs.itertuples(index=False))}
    idx=[]
    for p in sel.itertuples(index=False):
        k=(str(p.wet_RunID),str(p.dry_RunID))
        if k not in key_to_idx: raise RuntimeError(f"pair not found {k}")
        idx.append(key_to_idx[k])
    psub=pairs.iloc[idx].copy().reset_index(drop=True)
    dsub=[pair_data[i] for i in idx]
    r,den=uniform.design_residual(psub)
    obs_rows=np.asarray([obs_metric(d["wet"],d["dry"]) for d in dsub],float)
    obs=(r[:,None]*obs_rows).sum(axis=0)/den

    dry_ids=defaultdict(set)
    for p in psub.itertuples(index=False):
        key=(str(p.State),str(p.RouteNumber),str(p.RunNumber))
        dry_ids[key].add(str(p.dry_RunID))
    selected_keys={d["key"] for d in dsub}
    pools_selected={k:pools[k] for k in selected_keys}
    stops={d["key"]:d["stops"] for d in dsub}
    probs=uniform.baseline_probs(KAPPA,pools_selected,dry_ids,stops,ss)
    def qu(d): return uniform.solve_shift(probs[d["key"]],d["wet_k"])
    hist=persistence.historical_cell_probs(pools_selected,dry_ids,stops,ss)
    def qp(d):
        p=(1-ANCHOR)*hist[d["key"]]+ANCHOR*d["dry"].astype(float)
        p=np.clip(p,1e-8,1-1e-8)
        return uniform.solve_shift(p,d["wet_k"])
    ub=simulate(dsub,qu,r,den,SEED+51000)
    pb=simulate(dsub,qp,r,den,SEED+52000)
    names=["extra_stop_incidence_gain","multi_stop_route_new_species","route_new_species_gain"]
    us={names[j]:stat(ub[:,j],obs[j]) for j in range(3)}
    ps={names[j]:stat(pb[:,j],obs[j]) for j in range(3)}
    passed=bool(obs[0]>us[names[0]]["null_ci95"][1] and obs[0]>ps[names[0]]["null_ci95"][1])
    out={
      "analysis":"naamp_route_new_spread_same_observer_physical_stop_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_SPREAD_ROBUSTNESS_CONTRACT_V0_1.json",
      "coverage":{"pairs":int(len(psub)),"routes":int(psub.route_cluster.nunique()),"observers":int(sel["_observer_token"].nunique())},
      "observed_betas":{names[j]:float(obs[j]) for j in range(3)},
      "uniform_kappa2":us,"persistence_anchor_0_75":ps,
      "classification":{"excess_multi_stop_spread_jointly_robust":passed},
      "interpretation_boundary":{"observer_turnover_required":False if passed else None,"physical_stop_relocation_required":False if passed else None,"individual_movement_inferred":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
