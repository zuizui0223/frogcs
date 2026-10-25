#!/usr/bin/env python3
"""Observed GBIF stage coordinates × GloBI documented predator/prey stage grids.

Runs real GBIF occurrence SEARCH, not the country-facet or GBIF authenticated
bulk export. Same 0.5/1/2 degree grid and same month/year compatibility only.
Neither interaction events, abundance, true sympatry nor adult chorus inferred.

Source input: GloBI×GBIF stage country pilot JSON, accession 2026-10-25.
Original NPS/NAAMP research archive is unchanged. 100% source/API
completeness is tracked by species × vocabulary-stage query BEFORE analysis.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE="https://api.gbif.org/v1"
YEARS="2010,2025"
RESOLUTIONS=(0.5,1.0,2.0)
MAX_FULL_ROWS=3000
PARTIAL_PAGES=4
PAGE=300
LABELS={
    "adult":("Adult","Imago"),
    "aquatic_immature":("Larva","Nymph","Tadpole"),
    "juvenile":("Juvenile","Subadult","Immature","Young"),
    "egg":("Egg",)
}
MIXED=re.compile(r"juv\./adult|juvenile/adult|larv./adult|adult/larv",re.I)

def url(base,**query):
    return base+"?"+urllib.parse.urlencode(query)


def request_json(target,retries=3):
    for i in range(retries):
        try:
            req=urllib.request.Request(
                target,headers={"User-Agent":"FrogCS-StageGrid/0.1 (source-backed open-biodiversity research)",
                                "Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=40) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
                json.JSONDecodeError) as e:
            if i+1>=retries:
                raise RuntimeError(str(e)[:350])
            time.sleep(.6*(i+1))
    raise RuntimeError("unreachable")


def match(name):
    target=url(BASE+"/species/match",name=name,strict="true")
    result=request_json(target)
    if (result.get("rank")!="SPECIES" or
        result.get("matchType")!="EXACT" or
        int(result.get("confidence",0))<90 or
        not result.get("speciesKey")):
        return {"taxon":name,"status":"unmatched",
                "gbif_match":result}
    return {"taxon":name,"status":"accepted",
            "gbif_taxon_key":int(result["speciesKey"]),
            "gbif_name":result.get("canonicalName"),
            "gbif_match":result.get("status")}


def query_stage(key,label,limit=0,offset=0):
    params=dict(
        taxonKey=int(key),lifeStage=label,
        hasCoordinate="true",hasGeospatialIssue="false",
        occurrenceStatus="PRESENT",year=YEARS,
        limit=limit,offset=offset)
    return request_json(url(BASE+"/occurrence/search",**params))


def stage_taxon(job,lookup):
    """One full taxon×canonical-stage source, with documented truncation."""
    name,stage=job
    taxon=lookup[name]
    if taxon["status"]!="accepted":
        return {"taxon":name,"stage":stage,"status":"unmatched","records":[]}
    key=taxon["gbif_taxon_key"]
    records=[]
    label_receipts=[]
    fatal=[]
    total=0
    for label in LABELS[stage]:
        try:
            k=int(query_stage(key,label,0,0).get("count",0))
        except Exception as exc:
            fatal.append({"label":label,"error":str(exc)})
            continue
        total+=k
        if k==0:
            label_receipts.append({"label":label,"gbif_total":0,
                                   "raw_retrieved":0,"complete":True})
            continue
        if k<=MAX_FULL_ROWS:
            offsets=list(range(0,k,PAGE))
            complete_eligible=True
        else:
            end=min(k-PAGE,100000-PAGE)
            offsets=sorted({round(end*p/(PARTIAL_PAGES-1)//PAGE)*PAGE
                            for p in range(PARTIAL_PAGES)})
            complete_eligible=False
        raw=0
        err=[]
        for offset in offsets:
            try:
                result=query_stage(key,label,PAGE,offset)
                vals=result.get("results",[])
                raw+=len(vals)
                for x in vals:
                    yy=x.get("year")
                    mm=x.get("month")
                    if not isinstance(yy,int) or not (2010<=yy<=2025):
                        continue
                    if not isinstance(mm,int) or not (1<=mm<=12):
                        continue
                    try:
                        lat=float(x["decimalLatitude"])
                        lon=float(x["decimalLongitude"])
                    except (KeyError,TypeError,ValueError):
                        continue
                    if not math.isfinite(lat) or not math.isfinite(lon) or abs(lat)>90 or abs(lon)>180:
                        continue
                    uncertainty=x.get("coordinateUncertaintyInMeters")
                    try:
                        uncertainty=float(uncertainty) if uncertainty is not None else None
                    except (ValueError,TypeError):
                        uncertainty=None
                    if uncertainty is not None and uncertainty>10000:
                        continue
                    if x.get("countryCode") and x.get("countryCode")=="ZZ":
                        continue
                    gbifid=x.get("key") or x.get("gbifID")
                    if gbifid is None:
                        continue
                    records.append({
                        "record_id":str(gbifid),
                        "taxon":name,"stage":stage,"verbatim_lifeStage":label,
                        "latitude":lat,"longitude":lon,
                        "year":yy,"month":mm,
                        "country":x.get("countryCode") or "",
                        "dataset_key":x.get("datasetKey") or "",
                        "basis_of_record":x.get("basisOfRecord") or "",
                        "coordinate_uncertainty_m":uncertainty,
                        "record_has_unknown_uncertainty":int(uncertainty is None)
                    })
            except Exception as exc:
                err.append({"label":label,"offset":offset,"error":str(exc)})
        label_receipts.append({
            "label":label,"gbif_total":k,
            "raw_retrieved":raw,
            "complete":bool(complete_eligible and not err and raw==k),
            "intended_page_offsets":offsets,
            "page_errors":err})
    unique={r["record_id"]:r for r in records}
    full=(len(fatal)==0 and
          all(s["complete"] for s in label_receipts))
    return {
        "taxon":name,"stage":stage,
        "status":"complete" if full else ("source_error" if fatal else "partial"),
        "gbif_taxon_key":key,
        "gbif_facet_total":total,
        "raw_retrieved":sum(p["raw_retrieved"] for p in label_receipts),
        "accepted_unduplicated_with_month":len(unique),
        "missing_uncertainty_records":sum(r["record_has_unknown_uncertainty"]
                                        for r in unique.values()),
        "stage_labels":label_receipts,
        "fatal_errors":fatal,
        "records":list(unique.values())
    }


def cell(lat,lon,res):
    # Latitude 90 and longitude 180 belong to final half-open cell.
    y=min(int(round(180/res))-1,max(0,math.floor((lat+90.0)/res)))
    x=min(int(round(360/res))-1,max(0,math.floor((lon+180.0)/res)))
    return (x,y)


def footprints(records,res):
    spatial=set()
    year=set()
    month=set()
    yearmonth=set()
    for r in records:
        c=cell(r["latitude"],r["longitude"],res)
        spatial.add(c)
        year.add(c+(r["year"],))
        month.add(c+(r["month"],))
        yearmonth.add(c+(r["year"],r["month"]))
    return {"spatial":spatial,"same_year":year,
            "same_season_month_any_year":month,
            "same_year_month":yearmonth}


def source_class(citation):
    c=str(citation or "").lower()
    if "preston" in c and "california" in c and "food web" in c:
        return "CURATED_QUICK_POND_META_WEB"
    if "inaturalist.org/observations/" in c:
        return "SOURCE_INAT_OBSERVATION_LINK"
    if "trophic meta-web" in c or "tetra-eu" in c:
        return "CURATED_TROPHIC_META_WEB"
    return "OTHER_GLOBI_ASSOCIATION_SOURCE"


def supported_patterns(src):
    records=[]
    for p in src.get("stage_pairs_examples",[]):
        a=p.get("predator")
        b=p.get("prey")
        s=p.get("predator_stage")
        t=p.get("prey_stage")
        if not a or not b or not s or not t:
            continue
        if MIXED.search(str(p.get("original_predator_stage") or "")) or \
            MIXED.search(str(p.get("original_prey_stage") or "")):
            continue
        if s not in LABELS or t not in LABELS:
            continue
        records.append({
            "predator":a,"prey":b,
            "predator_stage":s,"prey_stage":t,
            "original_predator_stage":p.get("original_predator_stage"),
            "original_prey_stage":p.get("original_prey_stage"),
            "source":p.get("source",""),
            "provenance_class":source_class(p.get("source",""))})
    unique={}
    for p in records:
        k=(p["predator"],p["prey"],p["predator_stage"],
           p["prey_stage"],p["source"])
        unique[k]=p
    return list(unique.values())


def aggregate_pairs(patterns,status):
    result=[]
    observed_overlap_cells=[]
    for i,p in enumerate(patterns):
        lhs=status[(p["predator"],p["predator_stage"])]
        rhs=status[(p["prey"],p["prey_stage"])]
        complete=(lhs["status"]=="complete" and rhs["status"]=="complete")
        for resolution in RESOLUTIONS:
            a=footprints(lhs["records"],resolution)
            b=footprints(rhs["records"],resolution)
            overlap={k:a[k] & b[k] for k in a}
            x=dict(
                pattern_id=i+1,**p,resolution_deg=resolution,
                prey_records_accepted=rhs["accepted_unduplicated_with_month"],
                predator_records_accepted=lhs["accepted_unduplicated_with_month"],
                predator_source_completeness=lhs["status"],
                prey_source_completeness=rhs["status"],
                complete_both_stages=complete,
                predator_occupied_spatial_cells=len(a["spatial"]),
                prey_occupied_spatial_cells=len(b["spatial"]),
                spatial_overlap=len(overlap["spatial"]),
                shared_cell_years=len(overlap["same_year"]),
                shared_cell_seasonal_months=len(overlap["same_season_month_any_year"]),
                shared_cell_year_month=len(overlap["same_year_month"]),
                interpretation=("COMPLETE_SEARCH_OBSERVATION_OVERLAP_NOT_ENCOUNTER"
                    if complete else "LOWER_BOUND_NONRANDOM_SAMPLED_SOURCE_NO_ABSENCE_INFERENCE")
            )
            result.append(x)
            if resolution==1.0:
                for c in sorted(overlap["same_year_month"])[:500]:
                    observed_overlap_cells.append({
                        "pattern_id":i+1,"resolution_deg":resolution,
                        "longitude_grid_index":c[0],
                        "latitude_grid_index":c[1],
                        "center_lon":-180+(c[0]+.5)*resolution,
                        "center_lat":-90+(c[1]+.5)*resolution,
                        "year":c[2],"month":c[3],
                        "evidence":"co_reported_stage_only"})
    return result,observed_overlap_cells


def write_csv(path,rows,columns):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run(folder,src_json):
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    with Path(src_json).open(encoding="utf8") as f:
        data=json.load(f)
    patterns=supported_patterns(data)
    if not patterns:
        raise RuntimeError("Missing real jointly staged GloBI edges")
    names=sorted(set(p["predator"] for p in patterns)|
                 set(p["prey"] for p in patterns))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        matches=list(ex.map(match,names))
    lookup={p["taxon"]:p for p in matches}
    jobs=sorted({(p["predator"],p["predator_stage"]) for p in patterns} |
                {(p["prey"],p["prey_stage"]) for p in patterns})
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        result=list(ex.map(lambda j:stage_taxon(j,lookup),jobs))
    status={(x["taxon"],x["stage"]):x for x in result}
    pairs,overlap_cells=aggregate_pairs(patterns,status)
    # Avoid committing GBIF raw occurrence rows to a public source code repository.
    allrows=[r for v in result for r in v.get("records",[])]
    write_csv(out/"raw_stage_occurrences_for_audit.csv",allrows,[
        "record_id","taxon","stage","verbatim_lifeStage",
        "latitude","longitude","year","month","country","dataset_key",
        "basis_of_record","coordinate_uncertainty_m",
        "record_has_unknown_uncertainty"])
    columns=[
        "pattern_id","predator","prey","predator_stage","prey_stage",
        "original_predator_stage","original_prey_stage",
        "source","provenance_class","resolution_deg",
        "prey_records_accepted","predator_records_accepted",
        "predator_source_completeness","prey_source_completeness",
        "complete_both_stages",
        "predator_occupied_spatial_cells","prey_occupied_spatial_cells",
        "spatial_overlap","shared_cell_years","shared_cell_seasonal_months",
        "shared_cell_year_month","interpretation"]
    write_csv(out/"pair_grid_year_month_results.csv",pairs,columns)
    write_csv(out/"positive_1deg_cell_month_examples.csv",
              overlap_cells,["pattern_id","resolution_deg",
                             "longitude_grid_index","latitude_grid_index",
                             "center_lon","center_lat","year","month","evidence"])
    write_csv(out/"source_stage_completeness.csv",[
        dict(taxon=x["taxon"],stage=x["stage"],status=x["status"],
             gbif_taxon_key=x.get("gbif_taxon_key",""),
             gbif_facet_total=x.get("gbif_facet_total",0),
             raw_retrieved=x.get("raw_retrieved",0),
             accepted_with_month=x.get("accepted_unduplicated_with_month",0),
             unknown_uncertainty=x.get("missing_uncertainty_records",0))
        for x in result],[
        "taxon","stage","status","gbif_taxon_key","gbif_facet_total",
        "raw_retrieved","accepted_with_month","unknown_uncertainty"])
    source_status=[
        {k:v for k,v in x.items() if k!="records"} for x in result]
    (out/"source_audit.json").write_text(
        json.dumps(source_status,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    complete=[p for p in pairs if p["complete_both_stages"]]
    at1=[p for p in pairs if p["resolution_deg"]==1.0]
    complete1=[p for p in at1 if p["complete_both_stages"]]
    summary={
        "date":"2026-10-25",
        "output":"actual 0.5/1/2 degree joint predator/prey-stage GBIF occurrence cells, constrained by GloBI documented stage configuration",
        "source_GloBI":"research/results/global_globi_gbif/stage_bridge/observed_results.json",
        "source_GBIF":"https://api.gbif.org/v1/occurrence/search",
        "year_filter":YEARS,
        "original_gloBI_joint_stage_patterns":len(data.get("stage_pairs_examples",[])),
        "patterns_after_excluding_mixed_uncertain_stages":len(patterns),
        "distinct_taxa":len(names),
        "taxa_matched":sum(x["status"]=="accepted" for x in matches),
        "unique_taxon_stage_queries":len(jobs),
        "taxon_stage_complete":sum(x["status"]=="complete" for x in result),
        "taxon_stage_partially_sampled":sum(x["status"]=="partial" for x in result),
        "taxon_stage_source_error":sum(x["status"]=="source_error" for x in result),
        "gbif_stage_facets_total_sum":sum(x.get("gbif_facet_total",0) for x in result),
        "retrieved_distinct_records_with_date_and_quality":len(allrows),
        "complete_pair_patterns":len(complete1),
        "one_degree_complete_pair_patterns_with_grid_overlap":sum(
            x["spatial_overlap"]>0 for x in complete1),
        "one_degree_complete_pair_patterns_with_same_year_month_overlap":sum(
            x["shared_cell_year_month"]>0 for x in complete1),
        "one_degree_partial_pair_patterns_with_positive_grid_overlap":sum(
            not x["complete_both_stages"] and x["spatial_overlap"]>0
            for x in at1),
        "per_resolution_completeness_and_overlap":[
            {
                "resolution_deg":res,
                "eligible_complete_patterns":sum(x["complete_both_stages"]
                    for x in pairs if x["resolution_deg"]==res),
                "complete_patterns_shared_any_spatial_cell":sum(
                    x["complete_both_stages"] and x["spatial_overlap"]>0
                    for x in pairs if x["resolution_deg"]==res),
                "complete_patterns_shared_year_month_cell":sum(
                    x["complete_both_stages"] and x["shared_cell_year_month"]>0
                    for x in pairs if x["resolution_deg"]==res),
            }
            for res in RESOLUTIONS
        ],
        "one_degree_stage_pair_details":at1,
        "source_completeness":[dict(taxon=x["taxon"],stage=x["stage"],
            status=x["status"],gbif_total=x.get("gbif_facet_total",0),
            retrieved=x.get("raw_retrieved",0),
            accepted=x.get("accepted_unduplicated_with_month",0))
            for x in result],
        "limitations":[
            "A shared GBIF cell and month/year of separately recorded species stages is NOT observed feeding, local aquatic co-occurrence or interacting individuals.",
            "GloBI source pairs mix experimental/curated metaweb and photo-backed citations; unverified links are not direct attacks.",
            "A GBIF missing stage label does not mean no stage in nature; collecting and amateur reporting are biased.",
            "Incomplete GBIF high-volume stage queries are nonrandom offset samples; only positive overlap lower bounds, no absence inference.",
            "Scale-dependent cell overlap is a mathematical grid effect; no estimate of predation occurrence probability or effect size.",
            "Comparisons across years are confounded by GBIF reporting effort, date coverage, taxonomy and introduced populations.",
            "No emergent plant structural field, wetland hydrology, contemporaneous rain or frog chorus timing was joined here.",
            "No globally representative trophic role-reversal prevalence or P-value is provided."
        ]}
    (out/"observed_results.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_GBIF_STAGE_SPATIAL_MONTH_RESULTS")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("END_GBIF_STAGE_SPATIAL_MONTH_RESULTS")
    return summary


def selftest():
    assert cell(0.0,0.0,1.0)==(180,90)
    assert cell(-90,-180,2.0)==(0,0)
    a=[dict(latitude=10.1,longitude=20.1,year=2020,month=4)]
    b=[dict(latitude=10.5,longitude=20.6,year=2020,month=4)]
    overlap={r:len(footprints(a,r)["same_year_month"] &
                   footprints(b,r)["same_year_month"]) for r in RESOLUTIONS}
    assert overlap[1.0]==1 and overlap[0.5]==0
    assert source_class("Preston, D.L. food web California pond")=="CURATED_QUICK_POND_META_WEB"
    assert not supported_patterns({"stage_pairs_examples":[{
        "predator":"A","prey":"B","predator_stage":"adult",
        "prey_stage":"adult","original_predator_stage":"juv./adults"}]})
    print("SYNTHETIC_STAGE_GRID_COMPLETE_QA_PASS")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="research/results/gbif_stage_grid")
    parser.add_argument("--source",default="research/results/global_globi_gbif/stage_bridge/observed_results.json")
    parser.add_argument("--self-test",action="store_true")
    a=parser.parse_args()
    if a.self_test:selftest()
    else:run(a.out,a.source)
