#!/usr/bin/env python3
"""Prospective NAAMP acoustic-stop neighborhood environmental/GBIF stage G0.

FROZEN SOURCE-BLIND protocol:
research/CHORUS_SITE_ENV_ENEMY_STAGE_GBIF_HYPOTHESES_2026-10-26.md

ONLY original public NAAMP location coordinates (with geometry-only QC),
GBIF georeferenced, dated and exact-stage-report opportunities and NWI
mapped polygon at the original audio recorder position are examined.
No frog call/chorus values, species route effects, competition coefficients,
predator attacks, wetland breeding density or rainfall outcomes are read.
A listening point is NOT necessarily a pond. Unreported GBIF ≠ absence.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from hashlib import sha256
from io import StringIO
import csv
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
GBIF="https://api.gbif.org/v1/occurrence/search"
TAXA={"Anura":952,"Caudata":953,"Odonata":789}
RADIUS_KM=5.0
COORD_UNCERTAINTY_MAX=1000.0
MAX_GBIF_PAGE=300
MAX_ROUTES=24
SEED="frogcs GBIF G0 before enemy/phase 2026-10-26"
GRAIN="NAAMP SiteID recording neighborhood only; NOT a verified physical breeding wetland"
STAGES={"larva","larvae","larval","tadpole","tadpoles","nymph","naiad"}
YEAR_LO,YEAR_HI=2010,2015

def get_json(url,timeout=40):
    req=Request(url,headers={
        "User-Agent":"frogcs-multisite-GBIF-geographic-G0/1.0 (public source data)",
        "Accept":"application/json"})
    with urlopen(req,timeout=timeout) as f:
        out=json.loads(f.read().decode("utf-8"))
    if not isinstance(out,dict):raise ValueError("Source did not return JSON object")
    return out

def get_bytes(url,timeout=65):
    req=Request(url,headers={"User-Agent":"frogcs-multisite-source-geometry/1.0"})
    with urlopen(req,timeout=timeout) as f:
        b=f.read(8000000)
    return b

def hav(lat1,lon1,lat2,lon2):
    p=math.pi/180
    a1,a2=lat1*p,lat2*p
    dlat=(lat2-lat1)*p
    dlon=(lon2-lon1)*p
    x=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*6371.0088*math.asin(min(1.0,math.sqrt(x)))

def coord_source():
    b=get_bytes(COORD_URL)
    digest=sha256(b).hexdigest()
    if digest!=COORD_SHA:raise ValueError("Source NAAMP coordinates SHA drift: "+digest)
    rows=list(csv.DictReader(StringIO(b.decode("utf-8-sig"))))
    if len(rows)!=12064:raise ValueError(f"Source row count drift: {len(rows)}")
    required={"RouteNumber","SiteID","lat","lon"}
    if not required.issubset(rows[0]):raise ValueError("NAAMP original coordinate schema changed")
    routes=defaultdict(dict)
    errors=Counter()
    for row in rows:
        rt=(row.get("RouteNumber") or "").strip()
        site=(row.get("SiteID") or "").strip()
        try:
            lat=float(row["lat"]);lon=float(row["lon"])
        except (KeyError,ValueError,TypeError):
            errors["not_numeric"]+=1
            continue
        if not rt or not site or not math.isfinite(lat) or not math.isfinite(lon):
            errors["missing_route_site_or_coordinate"]+=1;continue
        if not (24<=lat<=50 and -125<=lon<=-66):
            errors["outside_contiguous_us_including_positive_longitude"]+=1;continue
        if site in routes[rt] and routes[rt][site]!=(lat,lon):
            errors["conflicting_source_duplicate_site_coordinate"]+=1
            # Make route ineligible rather than choosing from duplicate;
            # sentinel invalid is marked below.
            routes[rt][site]=None
        else:
            routes[rt][site]=(lat,lon)
    possible=[];invalid_routes=Counter()
    for route,pts in routes.items():
        if any(x is None for x in pts.values()):
            invalid_routes["conflicting_coordinate_site"]+=1;continue
        if len(pts)<8:
            invalid_routes["fewer_than_8_unique_site_ids"]+=1;continue
        coords=list(pts.values())
        maximum=max(hav(*a,*b) for i,a in enumerate(coords) for b in coords[i+1:])
        if maximum>40:
            invalid_routes["source_geometry_gt40km_max_interstop_distance"]+=1;continue
        sitekeys=sorted(pts)
        if sitekeys[0]==sitekeys[-1]:
            invalid_routes["no_distinct_source_site"]+=1;continue
        left=sitekeys[0];right=sitekeys[-1]
        if hav(*pts[left],*pts[right])<.1:
            invalid_routes["endpoints_lt100m_separation"]+=1;continue
        possible.append((route,((left,pts[left]),(right,pts[right]))))
    if len(possible)<MAX_ROUTES:
        raise ValueError("Fewer than 24 source-geometry verified independent routes")
    selected=sorted(possible,key=lambda z:sha256((SEED+"|"+z[0]).encode()).hexdigest())[:MAX_ROUTES]
    sample=[(route,site,lat,lon) for route,stops in selected for site,(lat,lon) in stops]
    return sample,{"original_rows":len(rows),"raw_site_row_issues":dict(errors),
       "candidate_distinct_route_labels":len(routes),"source_geometry_eligible_routes":len(possible),
       "geometry_rejected_routes":dict(invalid_routes),
       "selected_source_routes":len(selected),"selected_source_stops":len(sample),
       "coordinates_original_sha256":digest,"source_coordinate_errors_manually_repaired":False,
       "source_route_night_phenotype_used":False,
       "site_selection":"sha256 deterministic 24 source route IDs, within each first+last sorted SiteID; 40km max interstop geometry gate independent of biology"}

def encode_bbox(lat,lon):
    dlat=RADIUS_KM/111.32
    dlon=RADIUS_KM/(111.32*math.cos(math.radians(lat)))
    return { "decimalLatitude":f"{lat-dlat:.5f},{lat+dlat:.5f}",
      "decimalLongitude":f"{lon-dlon:.5f},{lon+dlon:.5f}" }

def gbif_query(lat,lon,order):
    params={"limit":MAX_GBIF_PAGE,"offset":0,
        "country":"US","hasCoordinate":"true","hasGeospatialIssue":"false",
        "year":f"{YEAR_LO},{YEAR_HI}",
        "occurrenceStatus":"PRESENT",
        **encode_bbox(lat,lon)}
    if order in TAXA:params["taxonKey"]=TAXA[order]
    out=get_json(GBIF+"?"+urlencode(params))
    if not isinstance(out.get("count"),int) or not isinstance(out.get("results"),list):
        raise ValueError("Unexpected GBIF occurrence search schema")
    n=int(out["count"]);rows=out["results"]
    precision=0;stage=0;no_precision=0;date_ok=0
    source_keys=set();stage_keys=set();stage_names=Counter();report_months=Counter()
    accepted=0
    for r in rows:
        try:rlat=float(r["decimalLatitude"]);rlon=float(r["decimalLongitude"])
        except (KeyError,ValueError,TypeError):continue
        if hav(lat,lon,rlat,rlon)>RADIUS_KM:continue
        accepted+=1
        try:unc=float(r.get("coordinateUncertaintyInMeters"))
        except (ValueError,TypeError):unc=None
        if unc is None or not 0<=unc<=COORD_UNCERTAINTY_MAX:
            no_precision+=1
            continue
        precision+=1
        src=r.get("datasetKey")
        if src:source_keys.add(str(src))
        yy=r.get("year");mm=r.get("month")
        if not isinstance(yy,int) or not isinstance(mm,int) or not YEAR_LO<=yy<=YEAR_HI or not 1<=mm<=12:continue
        date_ok+=1
        report_months[str(mm)]+=1
        raw=str(r.get("lifeStage") or "").strip().lower()
        if raw in STAGES:
            stage+=1
            stage_names[raw]+=1
            if src:stage_keys.add(str(src))
    return {
        "source_bbox_total_not_circle":n,
        "source_search_paging_exhaustive":n<=MAX_GBIF_PAGE and len(rows)==n,
        "source_page_returned":len(rows),
        "source_circle5km_in_first300_count":accepted,
        "precision_le1km_count":precision,
        "explicitly_dated_precise_stage_2010_2015":stage,
        "explicitly_dated_precise_any_lifestage_not_required":date_ok,
        "stage_labels":dict(stage_names),
        "distinct_precise_source_dataset_keys_in_page":len(source_keys),
        "distinct_precise_staged_source_dataset_keys_in_page":len(stage_keys),
        "report_months_counts_in_sample":dict(report_months),
        "has_unknown_or_gt1km_coordinate_uncertainty_within_radius":no_precision,
        "GBIF_neighborhood_report_is_NOT_same_pond":True,
        "zero_reports_is_NOT_true_biological_absence":True
    }

def nwi_query(lat,lon):
    params={"f":"json","geometry":f"{lon:.7f},{lat:.7f}","geometryType":"esriGeometryPoint",
       "inSR":"4326","spatialRel":"esriSpatialRelIntersects",
       "outFields":"ATTRIBUTE,WETLAND_TYPE","returnGeometry":"false","where":"1=1"}
    o=get_json(NWI+"?"+urlencode(params))
    if "error" in o:raise ValueError("NWI service error "+str(o["error"])[:130])
    ff=o.get("features")
    if not isinstance(ff,list):raise ValueError("No official feature list")
    codes=sorted({x.get("attributes",{}).get("ATTRIBUTE","") for x in ff})
    return {"official_intersected_polygon_count":len(ff),
            "point_inside_any_mapped_NWI_polygon":bool(ff),
            "point_inside_any_NWI_PEM":any(c.startswith("PEM") for c in codes),
            "cowardin_codes":codes,
            "mapped_recorder_coordinate_is_not_breeding_pond":True,
            "nwi_class_is_not_live_plant_fraction_or_time_varying_water":True}

def one_site(args):
    route,site,lat,lon=args
    rec={"nwi":{},"gbif":{}}
    try:rec["nwi"]=nwi_query(lat,lon)
    except Exception as e:rec["nwi"]={"error":type(e).__name__+": "+str(e)[:160]}
    for taxon in ["Anura","Caudata","Odonata","all_taxa_background"]:
        try:rec["gbif"][taxon]=gbif_query(lat,lon,taxon)
        except Exception as e:rec["gbif"][taxon]={"error":type(e).__name__+": "+str(e)[:160]}
    return rec

def audit_from_source(sample,geometry):
    # Fixed 48 stops, six concurrent source workers, no outcome-adaptive additions.
    results=[]
    with ThreadPoolExecutor(max_workers=6) as work:
        jobs=[work.submit(one_site,entry) for entry in sample]
        for f in as_completed(jobs):results.append(f.result())
    src_gbif={}
    for t in ["Anura","Caudata","Odonata","all_taxa_background"]:
        records=[r["gbif"].get(t,{}) for r in results]
        ok=[r for r in records if "error" not in r]
        src_gbif[t]={
           "source_queries":len(records),"successful":len(ok),
           "errors":dict(Counter(z.get("error","") for z in records if "error" in z)),
           "source_bbox_total_reported_sum":sum(z["source_bbox_total_not_circle"] for z in ok),
           "searches_exhaustive":sum(z["source_search_paging_exhaustive"] for z in ok),
           "neighborhoods_with_georeferenced_records_source_precision_le1km":sum(z["precision_le1km_count"]>0 for z in ok),
           "neighborhoods_with_explicit_aquatic_lifestage_record":sum(z["explicitly_dated_precise_stage_2010_2015"]>0 for z in ok),
           "precise_larval_stage_record_count_across_neighborhoods_can_overlap":sum(z["explicitly_dated_precise_stage_2010_2015"] for z in ok),
           "source_keys_count_is_per_neighborhood_not_global":True,
           "neighborhoods_with_3plus_staged_source_keys":sum(z["distinct_precise_staged_source_dataset_keys_in_page"]>=3 for z in ok),
           "sample_complete_for_absence":len(ok)==len(records) and all(z["source_search_paging_exhaustive"] for z in ok),
           "reporting_only":True
        }
    nwi=[r["nwi"] for r in results]
    valid=[r for r in nwi if "error" not in r]
    nr={
       "queries":len(nwi),"successes":len(valid),
       "errors":dict(Counter(r.get("error") for r in nwi if "error" in r)),
       "recorder_points_intersect_any_NWI_polygon":sum(z["point_inside_any_mapped_NWI_polygon"] for z in valid),
       "recorder_points_intersect_PEM_polygon":sum(z["point_inside_any_NWI_PEM"] for z in valid),
       "cowardin_code_instances":dict(Counter(code for r in valid for code in r["cowardin_codes"])),
       "NWI_point_not_actual_breeding_wetland":True
    }
    # The three stage cohorts must each pass the preregistered ≥15
    # neighborhood positives plus ≥3 independent data publishers at site.
    phase_eligible=all(
        src_gbif[t]["successful"]==48
        and src_gbif[t]["neighborhoods_with_explicit_aquatic_lifestage_record"]>=15
        and src_gbif[t]["neighborhoods_with_3plus_staged_source_keys"]>=15
        for t in ("Anura","Caudata","Odonata")
    )
    return {
       "source_geographic_integrity":geometry,
       "GBIF_recording_coverage":src_gbif,
       "NWI_original_recorder_point_QA":nr,
       "stage_proxy_source_coverage_gate_eligible":phase_eligible,
       "same_physical_breeding_pond_verified":False,
       "source_pond_predator_or_competitor_abundance_observed":False,
       "rain_source_at_site_or_real_pond_water_level_loaded":False,
       "emergent_vegetation_cover_or_stem_density_measured_at_site":False,
       "original_2026_research_sampled_NAAMP_chorus_values_read":False,
       "GBIF_counts_are_species_recording_effort_not_predator_or_competition_intensity":True,
       "biological_predation_or_facilitation_claim_permitted":False,
       "source_rows_redistributed":False,
       "status":"SOURCE_BLIND_G0_ACOUSTIC_STOP_NEIGHBORHOOD_NOT_VERIFIED_POND"
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=None)
    parser.add_argument("--no-gbif",action="store_true",help="geometry-only preflight; do not query data")
    args=parser.parse_args()
    try:
        sample,geog=coord_source()
        if args.no_gbif:
            result={"status":"ORIGINAL_NAAMP_GEOMETRY_ONLY","source_geographic_integrity":geog}
        else:
            result=audit_from_source(sample,geog)
    except Exception as e:
        result={"status":"BLOCKED_FAIL_CLOSED","error":type(e).__name__+": "+str(e)[:250],
                "rain_hydrology_vegetation_predator_mechanism_test_completed":False}
    result["protocol"]="research/CHORUS_SITE_ENV_ENEMY_STAGE_GBIF_HYPOTHESES_2026-10-26.md"
    result["sensitivity_boundary"]="GBIF 2010–2015 georeferenced presence reports within up to 5 km of acoustic points are neither co-occurring pond-level animals nor source-verified stage encounters."
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_NAAMP_GBIF_NWI_G0")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_NAAMP_GBIF_NWI_G0")
    if result["status"]=="BLOCKED_FAIL_CLOSED":
        raise SystemExit(4)

if __name__=="__main__":
    main()
