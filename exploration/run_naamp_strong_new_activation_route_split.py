#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
NAAMP=ROOT/"scripts"/"naamp"
OUT=EXP/"NAAMP_STRONG_NEW_ACTIVATION_ROUTE_SPLIT_RECEIPT_V0_1.json"


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


strength=loadmod("strength_base",EXP/"run_naamp_new_activation_strength.py")
base=strength.base
spatial=strength.spatial


def fold(route_cluster):
    b=hashlib.sha256(str(route_cluster).encode("utf-8")).digest()[0]
    return "A" if b<128 else "B"


def main():
    raw=base.load()
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=strength.build_ci(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    pairs["fold"]=pairs["route_cluster"].astype(str).map(fold)

    reports={}
    for f in ("A","B"):
        sub=pairs[pairs["fold"]==f].copy().reset_index(drop=True)
        rows=[]
        for p in sub.itertuples(index=False):
            r=p._asdict()
            r.update(strength.metrics(p,sampled,by))
            rows.append(r)
        d=pd.DataFrame(rows)
        model=strength.fit(d,"strong_new_score")
        passed=bool(model["beta"]>0 and model["ci95"][0]>0)
        reports[f]={
            "n_pairs":int(len(d)),
            "n_routes":int(d["route_cluster"].nunique()),
            "strong_new_score":model,
            "pass":passed,
        }

    output={
        "analysis":"naamp_strong_new_activation_route_split_v0_1",
        "contract":"exploration/NAAMP_STRONG_NEW_ACTIVATION_ROUTE_SPLIT_CONTRACT_V0_1.json",
        "folds":reports,
        "classification":{
            "both_folds_pass":bool(reports["A"]["pass"] and reports["B"]["pass"]),
            "rule":"strong_new_score beta >0 with complete 95% CI >0 independently in both deterministic route folds"
        },
        "interpretation_boundary":{
            "internal_replication_only":True,
            "cross_continental_universality":False,
            "causal_rainfall_claim":False
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
