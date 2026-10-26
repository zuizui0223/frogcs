#!/usr/bin/env python3
"""Exact-source G0.A: audit global GBIF 2026-08 taxon partition inventory.

Source-blind: list partition names, original parquet byte sizes and schema
columns including lifeStage/family/month/year. NO occurrence values, survival
ratios, stage-phase overlap, diet edges or predator-prey coefficients read.
Source https://data-blog.gbif.org/post/extending-parquet-snapshots/
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,unquote
from xml.etree import ElementTree as ET
from collections import defaultdict

S3="https://gbif-public-data.s3.amazonaws.com/"
PREFIX="development/2026-08-01-DWCA/p_taxon/"
HEADERS={"User-Agent":"frogcs-global-stage-G0-source-readiness/1.0"}
TOKENS=["_Amphibia_Anura", "_Amphibia_Caudata", "_Insecta_Odonata",
        "_Insecta_Ephemeroptera", "_Insecta_Diptera_"]
FALLBACK=["Animalia_Arthropoda_Insecta_Diptera__PARTIAL"]
PRIMARY=["_Amphibia_Anura","_Amphibia_Caudata","_Insecta_Odonata",
         "_Insecta_Ephemeroptera"]

def list_s3(prefix,delimiter=None,limit=1000,token=None):
    args={"list-type":2,"prefix":prefix,"max-keys":limit}
    if delimiter:args["delimiter"]=delimiter
    if token:args["continuation-token"]=token
    req=Request(S3+"?"+urlencode(args),headers=HEADERS)
    with urlopen(req,timeout=55) as resp:
        body=resp.read(6000000)
    root=ET.fromstring(body)
    def item(e,k):
        z=e.find("{*}"+k)
        return z.text if z is not None else None
    files=[{"key":item(e,"Key"),"bytes":int(item(e,"Size") or 0),
           "etag":item(e,"ETag")} for e in root.findall("{*}Contents")]
    dirs=[item(e,"Prefix") for e in root.findall("{*}CommonPrefixes")]
    return files,dirs,item(root,"IsTruncated")=="true",item(root,"NextContinuationToken")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    collected=[];token=None;calls=0;ended=False
    while not ended:
        files,sub,trunc,token=list_s3(PREFIX,delimiter="/",token=token)
        calls+=1
        collected.extend(sub)
        if calls>10:raise ValueError("Unbounded S3 partition pagination")
        ended=not trunc
    names=sorted({unquote(s[len(PREFIX):].split("/")[0]).replace("taxonpartition=","")
                  for s in collected if s and s.startswith(PREFIX)})
    if not names:raise ValueError("No GBIF experimental partitions discovered")
    chosen=[v for v in names if any(t in v for t in TOKENS) or v in FALLBACK
            or v.endswith("_Amphibia__PARTIAL")
            or v.endswith("_Amphibia")
            or v.endswith("_Insecta__PARTIAL")
            or v.endswith("_Insecta_Diptera")
            or "_Insecta_Diptera_" in v
            or v.endswith("_Insecta_Ephemeroptera")]
    # Some orders are directly order-partitioned and have no family suffix.
    chosen+= [v for v in names if v.endswith("_Amphibia_Caudata") or
              v.endswith("_Insecta_Ephemeroptera") or
              v.endswith("_Insecta_Odonata") or v.endswith("_Amphibia_Anura")]
    chosen=sorted(set(chosen))
    group={}
    for name in chosen:
        listkey=PREFIX+"taxonpartition="+name+"/"
        files,_,trunc,nextkey=list_s3(listkey)
        if trunc:raise ValueError("Too many unbounded files in "+name)
        parquet=[f for f in files if f["key"].endswith(".parquet")]
        group[name]={"original_files":len(parquet),
                     "total_original_parquet_bytes":sum(z["bytes"] for z in parquet),
                     "paths":[{"key":z["key"],"bytes":z["bytes"],"etag":z["etag"]}
                              for z in parquet[:16]],
                     "files_truncated_to16_in_receipt":len(parquet)>16}
    report={
        "status":"GBIF_EXPERIMENTAL_STAGE_PARTITION_SOURCE_LIST_ONLY",
        "source":"GBIF experimental 2026-08-01-DWCA open Parquet",
        "source_prefix":"s3://gbif-public-data/"+PREFIX,
        "source_doi":"10.15468/dl.8yrbe7",
        "source_s3_partition_count":len(names),
        "source_partition_names":names,
        "source_guild_partition_names":chosen,
        "by_partition":group,
        "diptera_chironomidae_family_filter_must_be_source_verified":
            "Chironomidae is a family and not guaranteed to equal an entire Diptera partition",
        "gbif_collected_occurrence_count":None,
        "life_stage_record_counts_computed":False,
        "prey_ratio_or_pairwise_overlap_inspected":False,
        "predator_negative_control_qualified":False,
        "anura_source_snapshot_stage_labels_source_blind":True,
        "g1_g2_g3_results_not_estimated":True,
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_GLOBAL_STAGE_PARTITION_G0")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    print("END_GLOBAL_STAGE_PARTITION_G0")
if __name__=="__main__":main()
