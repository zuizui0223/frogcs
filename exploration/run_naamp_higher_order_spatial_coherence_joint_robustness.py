#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_HIGHER_ORDER_SPATIAL_COHERENCE_JOINT_ROBUSTNESS_RECEIPT_V0_1.json"
B=1000
KAPPA=2.0
ANCHOR=0.75

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
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
    if bad: raise RuntimeError(f"multiple SiteID values: {list(bad)[:10]}")
    return {k:next(iter(v)) for k,v in vals.items() if v}

def stable(p,sampled,site):
    w=str(p.wet_RunID); d=str(p.dry_RunID); ws=set(sampled[w]); ds=set(sampled[d])
    if len(ws)!=10 or ws!=ds: return False
    return all(site.get((w,st)) is not None and site.get((w,st))==site.get((d,st)) for st in ws)

def metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route)&w.any(axis=1)
    if not np.any(route_new): return np.asarray([0.,0.,0.,0.])
    k=w[route_new].sum(axis=1).astype(float)
    extra=np.maximum(k-1.,0.)
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.asarray([float(len(k)),float(extra.sum()),float(higher.sum()),float(np.sum(k>=3.))])

def sim_metrics(w,d):
    d_route=d.any(axis=1)
    route_new=(~d_route[None,:])&w.any(axis=2)
    k=w.sum(axis=2).astype(float)
    extra=np.maximum(k-1.,0.)*route_new
    higher=extra*np.maximum(extra-1.,0.)/2.
    return np.column_stack([
        route_new.sum(axis=1).astype(float),
        extra.sum(axis=1).astype(float),
        higher.sum(axis=1).astype(float),
        ((k>=3.)&route_new).sum(axis=1).astype(float)
    ])

def simulate(pair_data,probmaker,r,den,seed):
    rng=np.random.default_rng(seed); num=np.zeros((B,4),float)
    for i,d in enumerate(pair_data):
        q=probmaker(d); w=rng.random((B,)+q.shape)<q[None,:,:]
        num += r[i]*sim_metrics(w,d["dry"])
    return num/den

def conditional(sim,obs):
    X=np.column_stack([np.ones(len(sim)),sim[:,0],sim[:,1]])
    y=sim[:,2]
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X@coef; resid=y-pred
    obs_pred=float(coef[0]+coef[1]*obs[0]+coef[2]*obs[1])
    obs_resid=float(obs[2]-obs_pred)
    lo,hi=np.quantile(resid,[.025,.975])
    p=float((1+np.sum(resid>=obs_resid))/(len(resid)+1))
    return {
      "predicted_higher_order_beta":obs_pred,
      "observed_conditional_residual":obs_resid,
      "null_residual_ci95":[float(lo),float(hi)],
      "conditional_upper_tail_p":p,
      "above_upper_95":bool(obs_resid>hi),
      "null_regression":[float(x) for x in coef]
    }

def main():
    raw=base.load(); runs,route_sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)
    allpairs,same=sameobs.same_observer_pairs(raw,runs,route_sets)
    site=site_map(raw,eligible)
    keep=np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)
    selected=same.loc[keep].copy().reset_index(drop=True)
    if len(selected)<2500 or selected.route_cluster.nunique()<400:
        raise RuntimeError(f"coverage gate failed: {len(selected)} pairs, {selected.route_cluster.nunique()} routes")

    pair_data,pools,dry_ids,r,den,_=sameobs.prepare_matrix(selected,runs,sampled,ss)
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

    ub=simulate(pair_data,qu,r,den,uniform.SEED+81000)
    pb=simulate(pair_data,qp,r,den,uniform.SEED+82000)
    u=conditional(ub,obs); p=conditional(pb,obs)
    passed=bool(u["above_upper_95"] and p["above_upper_95"])
    out={
      "analysis":"naamp_higher_order_spatial_coherence_joint_robustness_v0_1",
      "coverage":{"all_pairs":int(len(allpairs)),"same_observer_pairs":int(len(same)),"intersection_pairs":int(len(selected)),"routes":int(selected.route_cluster.nunique()),"observers":int(selected["_observer_token"].nunique())},
      "observed":{"route_new_species_gain_beta":float(obs[0]),"extra_stop_incidence_gain_beta":float(obs[1]),"higher_order_within_species_mass_beta":float(obs[2]),"threeplus_species_count_beta":float(obs[3])},
      "uniform_kappa2":u,
      "persistence_anchor_0_75":p,
      "classification":{"joint_robust_higher_order_spatial_coherence":passed},
      "interpretation_boundary":{"observer_turnover_required":False if passed else None,"physical_stop_relocation_required":False if passed else None,"literal_simultaneity_inferred":False,"causal_rainfall_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
