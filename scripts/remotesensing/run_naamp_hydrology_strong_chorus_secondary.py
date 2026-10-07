#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json, os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
OUT=ROOT/"remotesensing"/"NAAMP_HYDROLOGY_STRONG_CHORUS_SECONDARY_RECEIPT_V0_1.json"

VAR_CSV=Path(os.environ.get(
    "NAAMP_HYDRO_VARIABILITY_CSV",
    str(ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_V0_2.csv")
))
B=1000
SEED=2840314

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def ci_map(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            x=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if x in (1,2,3):
            vals[(rid,st,sp)].append(x)
    return {k:max(v) for k,v in vals.items()}

def main():
    if not VAR_CSV.exists():
        raise RuntimeError(f"missing hydrology table: {VAR_CSV}")
    var=pd.read_csv(VAR_CSV)

    raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
    p1,d1,h1,hyd1,site,safe,fail=hyd.build_complete_sample(
        raw,runs,psub,dsub,hsub,var,"M1"
    )

    coverage_pairs={
        "pairs":int(len(p1)),
        "routes":int(p1.route_cluster.nunique()) if len(p1) else 0,
        "states":int(p1.State.nunique()) if len(p1) else 0,
        "pair_failures":fail
    }

    eligible=set(runs.RunID.astype(str))
    ci=ci_map(raw,eligible,sampled)

    clusters=[]
    for p,dct,h in zip(p1.itertuples(index=False),d1,hyd1):
        dry=dct["dry"]
        wet=dct["wet"]
        route_new=(~dry.any(axis=1)) & wet.any(axis=1)
        if not np.any(route_new):
            continue
        x=(h["wet_H"]-h["dry_H"]).astype(float)
        x=x-float(np.mean(x))
        for j in np.flatnonzero(route_new):
            sp=dct["species"][int(j)]
            y=np.asarray([
                int(ci.get((str(p.wet_RunID),str(st),sp),0)>=2)
                for st in dct["stops"]
            ],dtype=int)
            if y.sum()==0 or y.sum()==len(y):
                continue
            d=float(np.mean(x[y==1])-np.mean(x[y==0]))
            clusters.append({
                "route_cluster":str(p.route_cluster),
                "species":str(sp),
                "x":x.copy(),
                "y":y.copy(),
                "d":d
            })

    n=len(clusters)
    nr=len({z["route_cluster"] for z in clusters})
    nt=len({z["species"] for z in clusters})
    gate=bool(n>=500 and nr>=100 and nt>=10)

    out={
      "analysis":"naamp_hydrology_strong_chorus_secondary_v0_1",
      "contract":"revision/NAAMP_HYDROLOGY_STRONG_CHORUS_SECONDARY_V0_1.md",
      "hydrology_source_sha256":__import__("hashlib").sha256(VAR_CSV.read_bytes()).hexdigest(),
      "coverage":{"M1_pair_population":coverage_pairs,
                  "informative_pair_taxon_clusters":n,
                  "routes":nr,"taxa":nt,
                  "gate_pass":gate,
                  "thresholds":{"clusters":500,"routes":100,"taxa":10}},
      "frog_endpoint_read":False
    }
    if not gate:
        out["classification"]="secondary_inconclusive"
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    out["frog_endpoint_read"]=True
    observed=float(np.mean([z["d"] for z in clusters]))
    rng=np.random.default_rng(SEED)
    null=np.empty(B,float)
    for b in range(B):
        vals=[]
        for z in clusters:
            xp=rng.permutation(z["x"])
            y=z["y"]
            vals.append(float(np.mean(xp[y==1])-np.mean(xp[y==0])))
        null[b]=float(np.mean(vals))

    lo,hi=np.quantile(null,[.025,.975])
    p=float((1+np.sum(null>=observed))/(B+1))
    support=bool(observed>hi and p<.05)

    out.update({
      "observed_mean_delta_water_strong_minus_not":observed,
      "permutation":{"replicates":B,"seed":SEED,
                     "null_mean":float(null.mean()),
                     "null_ci95":[float(lo),float(hi)],
                     "upper_tail_p":p},
      "classification":"strong_chorus_hydrology_alignment_supported" if support else "strong_chorus_hydrology_alignment_not_supported",
      "interpretation_boundary":{
        "within_pair_taxon_spatial_alignment":True,
        "reproductive_acoustic_activity":True,
        "reproductive_success_inferred":False,
        "primary_concentration_rescued_by_secondary":False
      }
    })
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
