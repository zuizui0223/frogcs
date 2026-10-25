#!/usr/bin/env python3
"""Original observation-level macro amphibian & odonate stage audit.

Five fixed North American latitude bands × five aquatic guild-stage queries,
GBIF iNaturalist research-grade observations only. No true pond IDs, feeding
observations or NAAMP data. Public coordinates are reduced to coarse 0.5° bins.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,time,urllib.parse,urllib.request,urllib.error
from collections import Counter
from pathlib import Path

from ecology.macro_stage.scripts.run_gbif_region import COMMON_INAT_GBIF_DATASET,REGIONS

REGIONS_SELECTED=("US30_35","US35_40","US40_45","US45_50","CA45_50")
STAGE_CLASSES=(
    ("frog_larva",952,"Larva"),
    ("frog_egg",952,"Egg"),
    ("salamander_egg",953,"Egg"),
    ("salamander_larva",953,"Larva"),
    ("odonate_nymph",789,"Nymph"),
)
BASE="https://api.gbif.org/v1/occurrence/search"
UA="frogcs-macro-observation-level/0.1"
COLUMNS=("region","guild_stage","gbifID","year","month","day","grid_lat_05","grid_lon_05",
    "scientificName","speciesKey","taxonRank","coordinate_uncertainty_m",
    "basisOfRecord","datasetKey")

def fetch(params):
    url=BASE+"?"+urllib.parse.urlencode(params)
    last=""
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=30) as response:
                raw=response.read(10_000_001)
                if len(raw)>10_000_000:raise RuntimeError("unexpected GBIF response size >10MB")
                doc=json.loads(raw)
                if not isinstance(doc.get("count"),int) or not isinstance(doc.get("results"),list):
                    raise ValueError("GBIF paged occurrence schema unexpected")
                return doc,{"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"n_results":len(doc["results"])}
        except (urllib.error.URLError,TimeoutError) as e:
            last=type(e).__name__+str(e)[:160]
            if attempt<3:time.sleep(2**attempt)
    raise RuntimeError("GBIF source unavailable: "+last)

def reduced_record(row,region,group,stage,country,a,b):
    if str(row.get("datasetKey"))!=COMMON_INAT_GBIF_DATASET:
        raise ValueError("GBIF wrong publisher data")
    if str(row.get("lifeStage","")).lower()!=stage.lower():
        raise ValueError("GBIF wrong original stage code")
    # GBIF occurrence.country is a full name; query filter uses ISO countryCode.
    if row.get("countryCode")!=country:
        raise ValueError("GBIF wrong ISO countryCode")
    lat=row.get("decimalLatitude");lon=row.get("decimalLongitude")
    if not isinstance(lat,(float,int)) or not isinstance(lon,(float,int)) or not a<=lat<=b:
        raise ValueError("GBIF occurrence outside requested latitude")
    y,m=row.get("year"),row.get("month")
    if not isinstance(y,int) or not 2015<=y<=2025:
        raise ValueError("GBIF wrong year")
    if not isinstance(m,int) or not 1<=m<=12:
        return None
    day=row.get("day")
    return {"region":region,"guild_stage":group,
        "gbifID":str(row["gbifID"]),
        "year":y,"month":m,"day":day if isinstance(day,int) and 1<=day<=31 else "",
        "grid_lat_05":math.floor(lat*2)/2,
        "grid_lon_05":math.floor(lon*2)/2,
        "scientificName":str(row.get("scientificName") or ""),
        "speciesKey":row.get("speciesKey") or "",
        "taxonRank":row.get("taxonRank") or "",
        "coordinate_uncertainty_m":row.get("coordinateUncertaintyInMeters") or "",
        "basisOfRecord":row.get("basisOfRecord") or "",
        "datasetKey":str(row["datasetKey"])}

def harvest(region,outdir):
    if region not in REGIONS_SELECTED:raise ValueError("not prespecified source band")
    country,a,b=REGIONS[region]
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    output=out/f"macro_gbif_records_{region}.csv"
    records=[];source=[]
    for group,key,stage in STAGE_CLASSES:
        offset=0;total=None;unique=set();paged=0;missing_month=0
        while True:
            params={"country":country,"taxonKey":key,"hasCoordinate":"true",
              "year":"2015,2025","decimalLatitude":f"{a},{b}",
              "datasetKey":COMMON_INAT_GBIF_DATASET,
              "lifeStage":stage,"limit":300,"offset":offset}
            doc,receipt=fetch(params)
            if total is None:total=doc["count"]
            batch=doc["results"]
            if not batch and offset<total:raise RuntimeError("GBIF search unexpectedly empty early")
            for row in batch:
                rec=reduced_record(row,region,group,stage,country,a,b)
                if rec is None:
                    missing_month+=1
                    continue
                if rec["gbifID"] in unique:raise ValueError("duplicate GBIF occurrence key within stage source")
                unique.add(rec["gbifID"])
                records.append(rec)
            source.append({**receipt,"group":group,"offset":offset})
            paged+=len(batch)
            offset+=len(batch)
            if offset>=total or doc.get("endOfRecords",False):break
            if offset+300>100000:raise RuntimeError("GBIF paged API cap reached")
            time.sleep(.20)
        if paged!=total:
            raise RuntimeError(f"GBIF page count changed mid-harvest: {region} {group} n={paged}/{total}")
        print(f"{region}: {group} GBIF original pages {len([x for x in source if x['group']==group])}, observations {len(unique)}",flush=True)
    # Public record IDs repeat across stage classes only if bad publisher annotations.
    keys=[r["gbifID"] for r in records]
    if len(keys)!=len(set(keys)):raise ValueError("duplicate GBIF occurrence across groups")
    records.sort(key=lambda r:(r["year"],r["month"],r["guild_stage"],r["gbifID"]))
    with output.open("w",newline="",encoding="utf-8") as file:
        w=csv.DictWriter(file,fieldnames=COLUMNS);w.writeheader();w.writerows(records)
    counts=Counter(r["guild_stage"] for r in records)
    report={"analysis":"original_iNaturalist_stage_occurrences_by_region_2015_2025_v0_1",
      "region":region,"country":country,"latitude_band":[a,b],
      "source_datasetKey":COMMON_INAT_GBIF_DATASET,
      "all_stage_queries":[[name,key,stage] for name,key,stage in STAGE_CLASSES],
      "original_records_with_month_and_coarse_coordinate":len(records),
      "records_by_stage":dict(counts),
      "csv_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
      "source_http_page_sha256":source,
      "original_coordinates_not_exported":True,
      "spatial_unit":"0.5 degree latitude x longitude bin, NOT verified breeding pond",
      "predation_or_community_interactions_observed":False,
      "independent_of_frogcs_NAAMP":True}
    (out/f"macro_gbif_original_page_receipt_{region}.json").write_text(
       json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="source_http_page_sha256"},indent=2))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--region",required=True,choices=REGIONS_SELECTED)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    harvest(a.region,a.outdir)
