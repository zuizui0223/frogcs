#!/usr/bin/env python3
"""GBIF US life-stage point -> USFWS NWI mapped PEM polygon: source-QA pilot.

NONRANDOM fixed-offset, <=100m-coordinate-uncertainty GBIF samples, NOT
population habitat use/selection, same-pond trophic overlap or NPS stations.
Spec: research/NWI_GBIF_FOCAL_STAGE_PEM_GEO_QA_SPEC_2026-10-25.md
"""
import argparse
import collections
import concurrent.futures
import csv
import json
import math
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

GBIF="https://api.gbif.org/v1/occurrence/search"
NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
SOURCES=[
 ("Anax junius",5051741,"Odonata","Nymph"),
 ("Anax junius",5051741,"Odonata","Adult"),
 ("Taricha torosa",2431913,"Caudata","Larva"),
 ("Taricha torosa",2431913,"Caudata","Adult"),
 ("Ambystoma maculatum",2431951,"Caudata","Larva"),
 ("Ambystoma maculatum",2431951,"Caudata","Adult"),
 ("Anaxyrus boreas",2422924,"Anura","Larva"),
 ("Anaxyrus boreas",2422924,"Anura","Adult"),
 ("Pseudacris regilla",2428132,"Anura","Larva"),
 ("Pseudacris regilla",2428132,"Anura","Adult"),
]


def url(base,**kw):return base+"?"+urlencode(kw)


def retrieve(u):
    for i in range(2):
        try:
            r=Request(u,headers={"User-Agent":"frogcs-PEM-Research-Source-QA/0.1","Accept":"application/json"})
            with urlopen(r,timeout=24) as f:
                return json.loads(f.read().decode("utf8"))
        except Exception as e:
            if i==1:raise RuntimeError(str(e)[:230])
            time.sleep(1.2)
    raise RuntimeError("not reached")


def gbif_url(key,stage,offset,limit):
    return url(GBIF,taxonKey=key,lifeStage=stage,country="US",
               hasCoordinate="true",hasGeospatialIssue="false",
               occurrenceStatus="PRESENT",year="2010,2025",offset=offset,limit=limit)


def offsets(n):
    if n<=0:return []
    return sorted({0,min(max(0,(n//600)*300),99700),
                   min(max(0,n-300),99700)})


def gbif_point(r,species,key,guild,stage):
    if r.get("taxonKey")!=key and r.get("speciesKey")!=key:
        return None,"taxon_key_mismatch"
    if str(r.get("lifeStage") or "").casefold()!=stage.casefold():
        return None,"lifestage_mismatch"
    yy,mm=r.get("year"),r.get("month")
    if not(isinstance(yy,int) and isinstance(mm,int) and
           2010<=yy<=2025 and 1<=mm<=12):
        return None,"no_precise_month"
    try:
        lat,lon=float(r["decimalLatitude"]),float(r["decimalLongitude"])
    except (ValueError,TypeError,KeyError):
        return None,"unusable_coordinates"
    if not (math.isfinite(lat) and math.isfinite(lon) and
            24<=lat<=50 and -125<=lon<=-66):
        return None,"not_contiguous_US"
    try:unc=float(r.get("coordinateUncertaintyInMeters"))
    except (TypeError,ValueError):return None,"missing_coordinate_uncertainty"
    if not(0<=unc<=100):return None,"uncertainty_above_100m"
    oid=r.get("key") or r.get("gbifID")
    if oid is None:return None,"no_occurrence_id"
    return dict(
        gbif_occurrence_id=str(oid),species=species,guild=guild,
        life_stage=stage,year=yy,month=mm,latitude=lat,longitude=lon,
        uncertainty_m=unc,basis_of_record=r.get("basisOfRecord") or "",
        gbif_dataset_key=r.get("datasetKey") or "",
        source_url=f"https://www.gbif.org/occurrence/{oid}"
    ),""


def gbif_sample(species,key,guild,stage):
    n=retrieve(gbif_url(key,stage,0,0)).get("count")
    if not isinstance(n,int):raise RuntimeError("Invalid GBIF total")
    selected={};why=collections.Counter();receipt=[]
    for offset in offsets(n):
        try:rows=retrieve(gbif_url(key,stage,offset,300)).get("results",[])
        except Exception as e:
            receipt.append({"offset":offset,"error":str(e)[:190]})
            continue
        count=0
        for row in rows:
            point,reason=gbif_point(row,species,key,guild,stage)
            if point is None:
                why[reason]+=1
                continue
            if point["gbif_occurrence_id"] in selected:
                why["duplicate_across_source_pages"]+=1
                continue
            selected[point["gbif_occurrence_id"]]=point
            count+=1
            if count>=5 or len(selected)>=15:break
        receipt.append({"offset":offset,"returned":len(rows),"accepted":count})
    audit={"species":species,"guild":guild,"stage":stage,
           "gbif_exact_species_key":key,"gbif_reported_stage_records":n,
           "fixed_offset_receipts":receipt,"gbif_points_with_known_le100m_uncertainty":len(selected),
           "excluded_by_reason":dict(why)}
    return audit,list(selected.values())


def intersect(point):
    lat,lon=point["latitude"],point["longitude"]
    link=url(NWI,geometry=f"{lon:.7f},{lat:.7f}",geometryType="esriGeometryPoint",
             inSR=4326,spatialRel="esriSpatialRelIntersects",
             outFields="ATTRIBUTE,WETLAND_TYPE,ACRES",returnGeometry="false",f="json")
    try:
        obj=retrieve(link)
        if obj.get("error") or not isinstance(obj.get("features"),list):
            raise RuntimeError("NWI returned error/no polygon features list")
        features=obj["features"]
        codes=sorted({f.get("attributes",{}).get("ATTRIBUTE")
                      for f in features
                      if isinstance(f.get("attributes",{}).get("ATTRIBUTE"),str)})
        return {**point,"NWI_result":"ok",
                "NWI_polygon_intersections":len(features),
                "NWI_codes":";".join(codes),
                "NWI_PEM_codes":";".join(x for x in codes if x.startswith("PEM")),
                "NWI_has_any_polygon":int(bool(features)),
                "NWI_has_any_PEM":int(any(x.startswith("PEM") for x in codes)),
                "NWI_error":""}
    except Exception as e:
        return {**point,"NWI_result":"error",
                "NWI_polygon_intersections":None,
                "NWI_codes":"","NWI_PEM_codes":"",
                "NWI_has_any_polygon":None,"NWI_has_any_PEM":None,
                "NWI_error":str(e)[:220]}


def describe(rows):
    ok=[r for r in rows if r["NWI_result"]=="ok"]
    pem=[r for r in ok if r["NWI_has_any_PEM"]]
    codes=collections.Counter()
    for row in pem:
        codes.update(filter(None,row["NWI_PEM_codes"].split(";")))
    return dict(source_precision_selected=len(rows),NWI_queries_succeeded=len(ok),
                NWI_queries_failed=len(rows)-len(ok),
                points_inside_mapped_NWI_polygon=sum(r["NWI_has_any_polygon"] for r in ok),
                points_inside_NWI_PEM=len(pem),
                NWI_PEM_fraction_of_queried_points=len(pem)/len(ok) if ok else None,
                PEM_codes=dict(codes),
                qualifier="NONRANDOM_GBIF_LOCATION_PILOT_NOT_HABITAT_SELECTION")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="research/results/nwi_gbif_stage_point_pilot")
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        assert offsets(0)==[] and offsets(177)==[0]
        assert offsets(30000)==[0,15000,29700]
        x,b=gbif_point({"taxonKey":5051741,"lifeStage":"Nymph",
                        "year":2020,"month":4,"decimalLatitude":40,
                        "decimalLongitude":-80,"coordinateUncertaintyInMeters":5,
                        "key":123},"Anax junius",5051741,"Odonata","Nymph")
        assert x and not b
        x,b=gbif_point({"taxonKey":5051741,"lifeStage":"Nymph",
                        "year":2020,"month":4,"decimalLatitude":40,
                        "decimalLongitude":-80,"key":123},
                       "Anax junius",5051741,"Odonata","Nymph")
        assert x is None and b=="missing_coordinate_uncertainty"
        print("GBIF_USFWS_NWI_POINT_PEM_QA_SELFTEST_PASS")
        return
    traces=[];gbif=[]
    for s in SOURCES:
        t,sub=gbif_sample(*s)
        traces.append(t);gbif+=sub
    if len(gbif)>150:raise RuntimeError("Exceeded fixed NWI query cap")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        annotated=list(pool.map(intersect,gbif))
    by=collections.defaultdict(list)
    for r in annotated:by[(r["species"],r["life_stage"])].append(r)
    samples=[{**t,**describe(by[(t["species"],t["stage"])])} for t in traces]
    result={
        "date":"2026-10-25",
        "source_GBIF":"https://api.gbif.org/v1/occurrence/search",
        "source_USFWS_NWI":"https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0",
        "fixed_selection":"5 strictly GBIF species matched taxa, 10 stage strata, default API head/middle/tail, up to 5 precise occurrence coordinates per source offset, 150 maximum NWI queries",
        "source_results":samples,
        "overall":describe(annotated),
        "status":"REAL_SOURCE_GEO_FEASIBILITY_NOT_PEM_CAUSAL_HABITAT_OR_FROG_CHORUS",
        "limitations":[
            "Not a random sample: GBIF offset ordering, taxon detection and stage-label availability are strongly biased.",
            "Only GBIF points with an explicitly documented coordinate uncertainty <=100m retained; unknown uncertainty is not treated as precise.",
            "NWI point in mapped polygons does not show actual pond habitat occupancy or a predator-prey encounter.",
            "No point intersected is not evidence of no wetland or avoidance of PEM; NWI source historical coverage and mapping accuracy vary.",
            "NPS chorus recorder SiteLocation and original NAAMP physical site coordinates have not been independently geojoined to NWI official wetlands.",
            "Original GloBI pair links and these five species are not a confirmed local frog-odonate-salamander trophic community.",
            "No mortality, breeding pulses, larval recruitment, PEM habitat preference or stage-driven coexistence estimated.",
        ]
    }
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/"observed_results.json").write_text(json.dumps(
        result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    if annotated:
        with (out/"source_GBIF_NWI_point_sample.csv").open("w",newline="",encoding="utf8") as f:
            writer=csv.DictWriter(f,fieldnames=list(annotated[0]))
            writer.writeheader();writer.writerows(annotated)
    print("BEGIN_GBIF_NWI_PEM_POINT_AUDIT")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_GBIF_NWI_PEM_POINT_AUDIT")


if __name__=="__main__":
    main()
