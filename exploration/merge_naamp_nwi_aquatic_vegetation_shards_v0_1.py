#!/usr/bin/env python3
"""Combine geometrically vetted NWI vegetation shards before any frog response read."""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shard-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--expected",type=int,default=12)
    opts=p.parse_args()
    files=sorted(opts.shard_root.rglob("geometry_nwi_preflight.json"))
    if len(files)!=opts.expected:
        raise RuntimeError(f"incomplete NWI shard set: {len(files)} vs {opts.expected}")
    results=[json.loads(z.read_text()) for z in files]
    shards=[r.get("shard_id") for r in results]
    if sorted(shards)!=list(range(opts.expected)):
        raise RuntimeError(f"duplicate or missing shard indices {shards}")
    merged=[]
    errors=[]
    labels=Counter()
    successful=0
    attempted=0
    matching=None
    geo=None
    per_shard=[]
    for src,r in zip(files,results):
        if r.get("mode")!="full": raise RuntimeError(f"not full geometry source: {src}")
        meta=r.get("matched_route_source_only_audit")
        if not meta or meta.get("frog_outcomes_read") is not False:
            raise RuntimeError("source blind matched route verification missing")
        if matching is None:matching=meta
        if meta!=matching:raise RuntimeError("matched sample drift between shards")
        audit=r["geometry_audit"]
        if geo is None:geo=audit
        if audit!=geo:raise RuntimeError("geometry gate drift between shards")
        m=r["overlay"]
        attempted+=m["routes_attempted"]
        successful+=m["routes_success"]
        labels.update(m.get("query_feature_classes",{}))
        errors+=m.get("service_errors",[])
        f=src.parent/"site_nwi_vegetation_context.csv"
        if f.exists():
            with f.open(encoding="utf-8",newline="") as fp:
                merged.extend(list(csv.DictReader(fp)))
        per_shard.append({"shard":r["shard_id"],"routes_attempted":m["routes_attempted"],
                          "routes_success":m["routes_success"],"sites":m["site_records"]})
    ident=[(r["State"],r["RouteNumber"],r["SiteID"]) for r in merged]
    if len(ident)!=len(set(ident)):
        raise RuntimeError("same SiteID mapped into two geospatial shards")
    success=bool(attempted>=350 and successful>=300 and successful>=.70*attempted
                 and len(merged)>=2500 and sum(float(x["nwi_emergent_cover_250m"])>0 for x in merged)>=50
                 and any(k in labels for k in ("emergent","aquatic_bed")))
    out={
        "analysis":"naamp_nwi_vegetation_geometry_full_sharded_v0_1",
        "source_only":True,
        "mode":"full",
        "preflight_eligible":success,
        "matched_route_source_only_audit":matching,
        "geometry_audit":geo,
        "overlay":{
            "routes_attempted":attempted,"routes_success":successful,
            "routes_failed":attempted-successful,
            "site_records":len(merged),
            "site_nwi_wetland_polygon_250m":sum(float(x["nwi_all_wetland_cover_250m"])>0 for x in merged),
            "site_nwi_emergent_250m":sum(float(x["nwi_emergent_cover_250m"])>0 for x in merged),
            "site_nwi_aquatic_bed_250m":sum(float(x["nwi_aquatic_bed_cover_250m"])>0 for x in merged),
            "query_feature_classes":dict(sorted(labels.items())),
            "service_errors":errors[:30],
            "shards":per_shard
        },
        "interpretation":{
            "vegetation_is_NWI_polygon_context_not_actual_2001_2015_plant_data":True,
            "frog_outcomes_or_Counts_csv_used":False,
            "missing_or_failed_API_treated_as_plant_absence":False,
            "RC6_scientific_claim_modified":False
        }
    }
    opts.output.mkdir(parents=True,exist_ok=True)
    (opts.output/"geometry_nwi_preflight.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if merged:
        with (opts.output/"site_nwi_vegetation_context.csv").open("w",newline="",encoding="utf-8") as fp:
            writer=csv.DictWriter(fp,fieldnames=list(merged[0]))
            writer.writeheader()
            writer.writerows(sorted(merged,key=lambda x:(x["State"],x["RouteNumber"],x["SiteID"])))
    print("NAAMP_NWI_MERGED_RESULT_BEGIN")
    print(json.dumps(out,sort_keys=True))
    print("NAAMP_NWI_MERGED_RESULT_END",flush=True)
    if not success:print("NOT_ELIGIBLE_FOR_FROG_RESPONSE_JOIN",flush=True)
    # Gate output for GitHub Actions downstream outcome-analysis job.
    import os
    output=os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output,"a",encoding="utf-8") as f:
            f.write("eligible="+("true" if success else "false")+"\n")

if __name__=="__main__":
    main()
