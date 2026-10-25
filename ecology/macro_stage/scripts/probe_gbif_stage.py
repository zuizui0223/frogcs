#!/usr/bin/env python3
"""Discover macro-stage sample sizes and stage-label semantics in live GBIF API.

Query real record counts by Amphibia orders Anura/Caudata and insect order
Odonata. No record-level claims from facets; no species interactions inferred.
Responses are timestamped, URL- and SHA256-pinned for reproducibility.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path

BASE="https://api.gbif.org/v1"
TAXA=("Anura","Caudata","Odonata")
USER_AGENT="frogcs-macro-stage-ecology-audit/0.1 (public noncommercial analysis)"

def query(endpoint,params,timeout=25):
    url=BASE+endpoint+"?"+urllib.parse.urlencode(params,doseq=True)
    err=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as resp:
                raw=resp.read(3_000_001)
                if len(raw)>3_000_000:raise ValueError("GBIF API oversized response")
                record=json.loads(raw)
                return {"url":url,"http_status":resp.status,"response_sha256":hashlib.sha256(raw).hexdigest(),"data":record}
        except (urllib.error.URLError,TimeoutError) as e:
            err=f"{type(e).__name__}: {str(e)[:150]}"
            if attempt<2:time.sleep(2*(attempt+1))
    raise RuntimeError(f"GBIF source unavailable {endpoint}: {err}")

def taxon_key(taxon):
    raw=query("/species/match",{"name":taxon,"rank":"ORDER"})
    d=raw["data"]
    if d.get("rank")!="ORDER" or d.get("matchType")=="NONE" or not isinstance(d.get("usageKey"),int):
        raise ValueError("taxon key not verified for "+taxon)
    return raw,int(d["usageKey"])

def probe():
    out={"study":"macro_stage_interaction_source_feasibility_v0_1",
         "pulled_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
         "source":"GBIF live occurrence search facets, 2015–2025 coordinate records",
         "taxonomic_groups":{},"frog_or_salamander_predation_tested":False,
         "no_naamp_acoustic_data_used":True}
    for taxon in TAXA:
        match,key=taxon_key(taxon)
        facet=query("/occurrence/search",{"taxonKey":key,"hasCoordinate":"true",
             "year":"2015,2025","limit":0,
             "facet":["lifeStage","country","year","datasetKey"],
             "facetLimit":100})
        d=facet["data"]
        groups={x["field"]:[{"name":c.get("name"),"count":c.get("count")} for c in x.get("counts",[])]
                for x in d.get("facets",[])}
        out["taxonomic_groups"][taxon]={
            "taxon_key":key,"matched_scientific_name":match["data"].get("scientificName"),
            "n_coordinate_occurrences_2015_2025":d.get("count"),
            "life_stage_nonempty_total_across_returned_buckets":sum(x["count"] for x in groups.get("LIFE_STAGE",[])),
            "facet_summaries":groups,
            "source_url":facet["url"],"response_sha256":facet["response_sha256"],
            "match_url":match["url"],"match_response_sha256":match["response_sha256"]}
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    report=probe()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    compact={k:{"key":v["taxon_key"],"n":v["n_coordinate_occurrences_2015_2025"],
      "stage_buckets":v["facet_summaries"].get("LIFE_STAGE",[])[:50]}
      for k,v in report["taxonomic_groups"].items()}
    print(json.dumps(compact,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
