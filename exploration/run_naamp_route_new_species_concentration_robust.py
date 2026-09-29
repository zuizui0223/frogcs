#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ROUTE_NEW_SPECIES_CONCENTRATION_ROBUST_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform=loadmod("uniform",NAAMP/"run_naamp_uniform_activation_null.py")
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

def main():
    raw=base.load(); runs,sets=base.build_runs(raw); eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)
    allpairs,same=sameobs.same_observer_pairs(raw,runs,sets)
    site=site_map(raw,eligible)
    keep=np.asarray([stable(p,sampled,site) for p in same.itertuples(index=False)],bool)
    pairs=same.loc[keep].copy().reset_index(drop=True)
    if len(pairs)<2500: raise RuntimeError(f"robust subset too small: {len(pairs)}")

    # Build pair matrices using the same candidate pool logic as uniform.prepare, but only for selected pairs.
    pair_keys={(str(p.State),str(p.RouteNumber),str(p.RunNumber)) for p in pairs.itertuples(index=False)}
    strata=defaultdict(list)
    for r in runs.itertuples(index=False):
        key=(str(r.State),str(r.RouteNumber),str(r.RunNumber))
        if key in pair_keys: strata[key].append(str(r.RunID))
    pools={}
    stops_by={}
    for key,rids in strata.items():
        pool=set(); stops=None
        for rid in rids:
            rs=sorted(sampled[rid])
            if len(rs)!=10: continue
            if stops is None: stops=rs
            elif rs!=stops: raise RuntimeError(f"stop drift {key}")
            for st in rs: pool.update(ss.get((rid,st),set()))
        pools[key]=sorted(pool); stops_by[key]=stops

    species_all=sorted({sp for spp in pools.values() for sp in spp})
    sidx={sp:i for i,sp in enumerate(species_all)}
    r,den=uniform.design_residual(pairs)
    numer=np.zeros(len(species_all),float)

    for i,p in enumerate(pairs.itertuples(index=False)):
        key=(str(p.State),str(p.RouteNumber),str(p.RunNumber))
        species=pools[key]; idx={sp:j for j,sp in enumerate(species)}; stops=stops_by[key]
        d=np.zeros((len(species),10),bool); w=np.zeros_like(d)
        for t,st in enumerate(stops):
            for sp in ss.get((str(p.dry_RunID),st),set()): d[idx[sp],t]=True
            for sp in ss.get((str(p.wet_RunID),st),set()): w[idx[sp],t]=True
        dry_route=d.any(axis=1); wet_counts=w.sum(axis=1)
        route_new=(~dry_route)&(wet_counts>0)
        extra=np.maximum(wet_counts-1,0)*route_new
        for j,sp in enumerate(species):
            if extra[j]:
                numer[sidx[sp]] += r[i]*float(extra[j])

    betas=numer/den
    total=float(np.sum(betas))
    positive=np.maximum(betas,0); pos_sum=float(np.sum(positive))
    shares=positive/pos_sum if pos_sum>0 else np.zeros_like(positive)
    order=np.argsort(-shares)
    top1=float(shares[order[0]]) if pos_sum>0 else 0.0
    top5=float(np.sum(shares[order[:5]])) if pos_sum>0 else 0.0
    hhi=float(np.sum(shares**2)) if pos_sum>0 else 0.0
    loo=total-betas; allpos=bool(np.all(loo>0)); min_i=int(np.argmin(loo))
    diffuse=bool(top1<=.25 and top5<=.60 and hhi<=.10 and allpos)

    out={
      "analysis":"naamp_route_new_species_concentration_robust_v0_1",
      "contract":"exploration/NAAMP_ROUTE_NEW_SPECIES_CONCENTRATION_ROBUST_CONTRACT_V0_1.json",
      "coverage":{
        "all_pairs":int(len(allpairs)),"same_observer_pairs":int(len(same)),
        "intersection_pairs":int(len(pairs)),"routes":int(pairs.route_cluster.nunique()),
        "observers":int(pairs["_observer_token"].nunique())
      },
      "decomposition":{"total_extra_stop_beta":total,"sum_species_betas":float(np.sum(betas))},
      "concentration":{
        "n_species":int(len(species_all)),
        "n_species_positive_beta":int(np.sum(betas>0)),
        "n_species_positive_share_ge_1pct":int(np.sum(shares>=.01)),
        "top1_positive_share":top1,"top5_positive_share":top5,
        "hhi_positive_shares":hhi,
        "minimum_leave_one_species_out_beta":float(loo[min_i]),
        "species_causing_minimum_loo":species_all[min_i],
        "all_leave_one_species_out_betas_positive":allpos
      },
      "top_positive_species":[
        {"species":species_all[int(i)],"beta":float(betas[int(i)]),"positive_share":float(shares[int(i)])}
        for i in order[:15] if shares[int(i)]>0
      ],
      "classification":{"diffuse_across_taxa_under_prefixed_rule":diffuse},
      "interpretation_boundary":{"every_species_responds":False,"species_trait_mechanism_identified":False,"universal_claim":False}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
