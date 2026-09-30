#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_LOCAL_MEMORY_GEOGRAPHIC_GENERALITY_RECEIPT_V0_1.json"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

mem=loadmod("mem",EXP/"run_naamp_species_specific_site_memory.py")

def fold(route_cluster):
    b=hashlib.sha256(str(route_cluster).encode()).digest()[0]
    return "A" if b<128 else "B"

def build_data():
    raw=mem.load_retry()
    runs,sets=mem.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=mem.spatial.stop_matrix(raw,eligible)
    site=mem.site_map(raw,eligible)
    ci=mem.ci_map(raw,eligible,sampled)
    meta,by_stratum=mem.build_history(runs)
    pairs=mem.base.pair_runs(runs,sets).copy().reset_index(drop=True)
    stable=pairs.loc[np.asarray([
        mem.stable_pair(p,sampled,site) for p in pairs.itertuples(index=False)
    ],bool)].copy().reset_index(drop=True)

    _,same=mem.sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    rows=[]
    for pid,p in enumerate(stable.itertuples(index=False)):
        rr=mem.pair_rows(
            pid,p,sampled,site,ci,meta,by_stratum,
            (str(p.wet_RunID),str(p.dry_RunID)) in same_keys
        )
        for x in rr:
            x["State"]=str(p.State)
            x["route_fold"]=fold(str(p.route_cluster))
        rows.extend(rr)
    return pd.DataFrame(rows)

def fit(d,outcome):
    return mem.fit_within(d,outcome,False)

def main():
    d=build_data()
    full=fit(d,"wet_strong")
    if full is None:
        raise RuntimeError("full local-memory model not estimable")

    states=sorted(d.State.astype(str).unique())
    loso={}
    for st in states:
        z=fit(d[d.State.astype(str)!=st].copy(),"wet_strong")
        loso[st]=z

    valid_loso=[z for z in loso.values() if z is not None]
    loso_all_positive=bool(valid_loso and all(z["same_species_memory_beta"]>0 for z in valid_loso))
    loso_all_ci_positive=bool(valid_loso and all(z["same_species_memory_ci95"][0]>0 for z in valid_loso))

    route_split={}
    route_split_full={}
    for fd in ("A","B"):
        route_split[fd]=fit(d[d.route_fold==fd].copy(),"wet_strong")
        route_split_full[fd]=fit(d[d.route_fold==fd].copy(),"wet_full")

    split_pass=bool(all(
        route_split[fd] is not None
        and route_split[fd]["same_species_memory_beta"]>0
        and route_split[fd]["same_species_memory_ci95"][0]>0
        for fd in ("A","B")
    ))
    split_full_pass=bool(all(
        route_split_full[fd] is not None
        and route_split_full[fd]["same_species_memory_beta"]>0
        and route_split_full[fd]["same_species_memory_ci95"][0]>0
        for fd in ("A","B")
    ))

    state_specific={}
    for st,g in d.groupby("State",sort=True):
        # Check informative group coverage before fitting.
        inf=g.groupby("pair_species")["same_species_prior_strong"].nunique()
        good=inf[inf>=2].index
        gg=g[g.pair_species.isin(good)].copy()
        n_groups=int(gg.pair_species.nunique())
        n_routes=int(gg.route_cluster.nunique())
        n_species=int(gg.species.nunique())
        if n_groups>=100 and n_routes>=10 and n_species>=10:
            state_specific[str(st)]=fit(g.copy(),"wet_strong")
        else:
            state_specific[str(st)]={
                "estimable":False,
                "n_informative_groups":n_groups,
                "n_routes":n_routes,
                "n_species":n_species
            }

    est=[x for x in state_specific.values() if isinstance(x,dict) and x.get("same_species_memory_beta") is not None]
    out={
      "analysis":"naamp_local_memory_geographic_generality_v0_1",
      "contract":"exploration/NAAMP_LOCAL_MEMORY_GEOGRAPHIC_GENERALITY_CONTRACT_V0_1.json",
      "coverage":{
        "rows":int(len(d)),
        "pair_species_groups":int(d.pair_species.nunique()),
        "routes":int(d.route_cluster.nunique()),
        "states":int(d.State.nunique()),
        "species":int(d.species.nunique())
      },
      "full_reference":full,
      "leave_one_state_out":loso,
      "deterministic_route_split_wet_strong":route_split,
      "deterministic_route_split_wet_full":route_split_full,
      "state_specific_descriptive":state_specific,
      "summary":{
        "loso_all_positive":loso_all_positive,
        "loso_all_ci_positive":loso_all_ci_positive,
        "route_split_both_ci_positive":split_pass,
        "route_split_full_chorus_both_ci_positive":split_full_pass,
        "n_state_specific_estimable":int(len(est)),
        "state_specific_positive_fraction":float(np.mean([x["same_species_memory_beta"]>0 for x in est])) if est else None,
        "state_specific_ci_positive_fraction":float(np.mean([x["same_species_memory_ci95"][0]>0 for x in est])) if est else None
      },
      "classification":{
        "naamp_domain_local_memory_generality_supported":bool(loso_all_positive and split_pass),
        "strong_generality_supported":bool(loso_all_ci_positive and split_pass)
      },
      "interpretation_boundary":{
        "global_universality_claim":False,
        "sampled_NAAMP_domain_only":True,
        "continuous_occupancy_proven":False,
        "causal_memory_claim":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
