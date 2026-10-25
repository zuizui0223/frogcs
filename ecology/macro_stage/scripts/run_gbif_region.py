#!/usr/bin/env python3
"""Original GBIF order/lifeStage monthly macro-phenology counts for fixed regions.
No animal-interaction claims: region-level data only, not common-pond observations.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path

REGIONS={
"US25_30":("US",25,30),"US30_35":("US",30,35),"US35_40":("US",35,40),
"US40_45":("US",40,45),"US45_50":("US",45,50),
"CA45_50":("CA",45,50),"CA50_55":("CA",50,55),"CA55_60":("CA",55,60),
"FR40_50":("FR",40,50),"DE45_55":("DE",45,55),"GB50_60":("GB",50,60),
"JP30_40":("JP",30,40),"JP40_45":("JP",40,45),
"AUminus40_30":("AU",-40,-30),"AUminus30_20":("AU",-30,-20)
}
STAGES=[
("frog_egg",952,"Egg"),("frog_larva",952,"Larva"),("frog_tadpole",952,"Tadpole"),
("salamander_egg",953,"Egg"),("salamander_larva",953,"Larva"),
("odonate_larva",789,"Larva"),("odonate_nymph",789,"Nymph"),
("odonate_adult",789,"Adult"),("odonate_imago",789,"Imago"),
("all_frog",952,None),("all_salamander",953,None),("all_odonate",789,None)
]
BASE="https://api.gbif.org/v1/occurrence/search"
UA="frogcs-macro-stage-ecology-monthly/0.1"
COMMON_INAT_GBIF_DATASET="50c9509d-22c7-4a22-a47d-8c48425ef4a7"

def request(params):
    url=BASE+"?"+urllib.parse.urlencode(params,doseq=True)
    last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=26) as response:
                b=response.read(3_000_001)
                if len(b)>3_000_000:raise RuntimeError("GBIF API response exceeds 3MB")
                d=json.loads(b)
                if not isinstance(d.get("count"),int) or "facets" not in d:
                    raise RuntimeError("GBIF facet schema invalid")
                return d,{"url":url,"source_sha256":hashlib.sha256(b).hexdigest(),
                          "http_status":int(response.status)}
        except (urllib.error.URLError,TimeoutError) as e:
            last=f"{type(e).__name__}: {e}"
            if attempt!=3:time.sleep(min(12,2**attempt))
    raise RuntimeError(f"GBIF query exhausted retry: {last}")

def parse_month(d):
    summary={}
    for group in d["facets"]:
        key=group.get("field","").upper()
        summary[key]=[{"name":str(x.get("name","")),"count":int(x["count"])}
                      for x in group.get("counts",[])]
    months=[0]*12
    for q in summary.get("MONTH",[]):
        m=int(q["name"])
        if not 1<=m<=12:raise ValueError("GBIF unexpected month facet")
        months[m-1]=int(q["count"])
    return months,summary

def harvest(region, shared_dataset=False):
    country,a,b=REGIONS[region]
    records=[]
    for key,order,stage in STAGES:
        params={"country":country,"taxonKey":order,"hasCoordinate":"true",
          "year":"2015,2025","decimalLatitude":f"{a},{b}",
          "limit":0,"facet":["month","datasetKey","basisOfRecord"],
          "facetLimit":50}
        if stage is not None:params["lifeStage"]=stage
        if shared_dataset:params["datasetKey"]=COMMON_INAT_GBIF_DATASET
        d,provenance=request(params)
        monthly,facets=parse_month(d)
        if sum(monthly)>int(d["count"]):
            raise RuntimeError(f"GBIF month buckets exceed group records {region} {key}")
        rec={"stage_key":key,"group":str(order),"life_stage_filter":stage,
             "n_all_stage_query":int(d["count"]),"n_with_month":sum(monthly),
             "month_counts":monthly,
             "n_records_in_top50_datasets":sum(x["count"] for x in facets.get("DATASET_KEY",[])),
             "dataset_top50":facets.get("DATASET_KEY",[]),
             "basis_top50":facets.get("BASIS_OF_RECORD",[]),
             "provenance":provenance}
        records.append(rec)
        print(f"{region:<15} {key:<19} total={d['count']:>8} dated={sum(monthly):>8}",flush=True)
        time.sleep(.2)
    return {"report":"GBIF macro stage monthly facet v0.1",
            "original_query_date_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "region":region,"country":country,"lat_min":a,"lat_max":b,
            "years_inclusive":[2015,2025],
            "source_restriction":"shared_iNaturalist_dataset" if shared_dataset else "all_publishers",
            "dataset_key":COMMON_INAT_GBIF_DATASET if shared_dataset else None,
            "raw_stage_categories_preserved":True,
            "biological_stage_contact_observed":False,
            "life_stages_are_record_annotations_not_random_censuses":True,
            "distinct_region_site_unit":"latitude band × country, NOT a pond",
            "records":records}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--region",required=True,choices=sorted(REGIONS))
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--shared-dataset",action="store_true",help="use same GBIF iNaturalist dataset key for all three orders")
    a=p.parse_args()
    result=harvest(a.region,a.shared_dataset)
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/f"GBIF_MONTHLY_{a.region}{'_INAT' if a.shared_dataset else ''}.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__":main()
