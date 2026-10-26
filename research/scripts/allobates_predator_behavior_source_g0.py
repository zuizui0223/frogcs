#!/usr/bin/env python3
"""Zenodo original Allobates tadpole predator-pool assay G0: response BLIND.

This audits SOURCE integrity and *independent pool* / repeated-individual
coverage before evaluating movement or emergence. It never accesses CumlDist,
TimeToEmerge, TimeUncovered, CrossingNumber or other behavioral responses.
Nothing about attack, egg survival or pond hydroperiod is inferred.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
import hashlib
from io import StringIO
import json
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "10.5281/zenodo.18956129"
FILES = {
    "novel": {
        "name": "novelenvironment_results.csv",
        "md5": "67c34ace991c80db7331654554535faa",
        "url": "https://zenodo.org/records/18956129/files/novelenvironment_results.csv?download=1",
    },
    "shelter": {
        "name": "shelterassay_results.csv",
        "md5": "514c72d739f88d2f4a83f13d366950dc",
        "url": "https://zenodo.org/records/18956129/files/shelterassay_results.csv?download=1",
    },
}
REQUIRED = {
    "novel": {"TadpoleID","Bucket","Trial","PredatorYN","SIZE","TadpoleNo","CumlDist"},
    "shelter": {"TadpoleID","Bucket","Trial","PredatorYN","SIZE","TadpoleNo","TimeToEmerge","Batch"},
}
PROHIBITED_OUTCOME_FIELDS = {
    "CumlDist","TimeToEmerge","TimeUncovered","CrossingNumber"
}

def checked_fetch(info):
    req = Request(info["url"],headers={
        "User-Agent": "frogcs-ontogenetic-source-G0/1.0 (source-integrity QA)",
        "Accept": "text/csv, text/plain, */*"
    })
    with urlopen(req,timeout=45) as res:
        b = res.read(200000)
    if len(b)>=200000:
        raise ValueError("Source is unexpectedly large; fail closed")
    got = hashlib.md5(b).hexdigest()
    if got != info["md5"]:
        raise ValueError(f"Original Zenodo MD5 mismatch for {info['name']}: {got}")
    txt=b.decode("utf-8-sig")
    reader=csv.DictReader(StringIO(txt))
    cols=reader.fieldnames or []
    return list(reader),cols,{"md5":got,"bytes":len(b),"url":info["url"]}

def norm_status(val):
    x=str(val).strip().upper()
    if x in ("Y","YES","TRUE"):return "Y"
    if x in ("N","NO","FALSE"):return "N"
    return "invalid"

def norm_id(val):
    s=str(val or "").strip()
    if not s:return ""
    return s

def profile(rows,cols,tag):
    missing=REQUIRED[tag]-set(cols)
    if missing: raise ValueError("Required fields missing: "+",".join(sorted(missing)))
    rowkeys=set()
    individuals=defaultdict(list)
    source_pools=defaultdict(set)
    sizes=[];origin_counts=[]
    status=Counter();trials=Counter();batches=Counter()
    pool_individuals=defaultdict(set);bucket_batches=defaultdict(set);batch_predator=defaultdict(set)
    for r in rows:
        # ONLY metadata/predictor fields, never the behavioral outcome.
        tid=norm_id(r["TadpoleID"])
        pool=norm_id(r["Bucket"])
        trial=norm_id(r["Trial"])
        p=norm_status(r["PredatorYN"])
        if not tid or not pool or trial not in ("1","2","3","4"):
            raise ValueError("Incomplete or invalid sampled individual/pool/trial")
        if p=="invalid":raise ValueError("Unrecognized source predator-status field")
        k=(tid,trial)
        if k in rowkeys:raise ValueError("Duplicate individual×trial in source: "+tag)
        rowkeys.add(k)
        status[p]+=1
        source_pools[pool].add(p)
        pool_individuals[(pool,p)].add(tid)
        if "Batch" in r:
            batch=str(r.get("Batch") or "").strip()
            if batch:
                bucket_batches[pool].add(batch)
                batch_predator[batch].add(p)
        individuals[tid].append((pool,p,trial))
        trials[trial]+=1
        if "Batch" in r:batches[norm_id(r.get("Batch"))]+=1
        try:
            size=float(r["SIZE"])
            count=float(r["TadpoleNo"])
            if size<=0 or count<0:raise ValueError()
            sizes.append(size);origin_counts.append(count)
        except (TypeError,ValueError):
            raise ValueError("Cannot validate size or origin tadpole count")
    if any(len(set((pool,p) for pool,p,trial in v))>1 for v in individuals.values()):
        raise ValueError("One individual associated with multiple pool/predator states")
    conflict_pools=sorted(k for k,v in source_pools.items() if len(v)!=1)
    return ({
        "assay":tag,"row_count":len(rows),
        "column_names":cols,"individuals":len(individuals),
        "raw_bucket_label_count":len(source_pools),
        "rows_by_predator":dict(status),
        "unique_buckets_by_predator":dict(Counter(next(iter(st)) for st in source_pools.values() if len(st)==1)),
        "bucket_codes_with_conflicting_predator_status":len(conflict_pools),
        "source_pools_repeated_over_multiple_batches":sum(len(x)>1 for x in bucket_batches.values()),
        "distinct_pool_by_batch_and_predator":{
            b:{p:sum(any(r.get("Batch","").strip()==b and
                       r.get("Bucket","").strip()==pool and
                       norm_status(r.get("PredatorYN"))==p for r in rows)
                     for pool in source_pools) for p in ("Y","N")}
            for b in sorted(batch_predator)
        },
        "independent_pools_by_predator_have_sampled_individuals":{
            p:sorted(len(ids) for (pool,status),ids in pool_individuals.items() if status==p)
            for p in ("Y","N")
        },
        "trials_per_number":dict(trials),
        "batches_per_label":dict(batches),
        "size_range":[min(sizes),max(sizes)],
        "origin_pool_conspecific_count_range":[min(origin_counts),max(origin_counts)],
        "outcomes_inspected":False,
    },individuals,source_pools)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    q={}; persons={}; pools={}
    for tag,info in FILES.items():
        rows,columns,receipt=checked_fetch(info)
        summary,individuals,source_pools=profile(rows,columns,tag)
        summary["source"]=receipt
        q[tag]=summary
        persons[tag]=individuals
        pools[tag]=source_pools
    nov=set(persons["novel"]); shel=set(persons["shelter"])
    shared=nov&shel
    cross_conflicts=0
    for tid in shared:
        orig={(p,s) for p,s,t in persons["novel"][tid]}
        latter={(p,s) for p,s,t in persons["shelter"][tid]}
        if orig!=latter:cross_conflicts+=1
    # Determine distinct pool IDs by single exposure level, and expose whether
    # the same numerical Bucket code is likely reused across experimental batch.
    # Batch only occurs in shelter, so check mapping is unique by TadpoleID.
    bucket_batch=defaultdict(set)
    for tid,reps in persons["shelter"].items():
        bucket=reps[0][0]
        # original rows are available only in this process; use distribution
        # counts from source in a second minimal loop (not outcome fields).
    out={
        "source":SOURCE, "status":"PINNED_SOURCE_SCHEMA_BLIND_G0_COMPLETED",
        "assays":q,
        "individual_ids_both_assays":len(shared),
        "novel_only_ids":len(nov-shel),"shelter_only_ids":len(shel-nov),
        "cross_assay_pool_or_predator_state_conflicts":cross_conflicts,
        "source_pool_level_predator_treatment_randomized":False,
        "source_status_measures_predator_presence_in_origin_pool":True,
        "stage":"Allobates femoralis tadpole individual behavior measured after field origin",
        "original_pool_is_biological_replication_unit_not_individual":True,
        "abiotic_hydroperiod_documented":False,
        "stage_specific_attack_or_prey_survival_documented":False,
        "source_data_not_redistributed":True,
        "fitness_or_causal_predation_effect_authorized":False,
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_FROGCS_ALLOBATES_G0")
    print(json.dumps(out,indent=2,ensure_ascii=False))
    print("END_FROGCS_ALLOBATES_G0")

if __name__=="__main__":
    main()
