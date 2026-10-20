#!/usr/bin/env python3
"""Response-blind USGS NAAMP station geometry -> official USFWS NWI vegetation preflight."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pyproj import CRS, Geod, Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build"/"aquatic_vegetation"
CONTRACT="exploration/NAAMP_AQUATIC_VEGETATION_DESIGN_2026_10_21.md"
SOURCE_ITEM="https://www.sciencebase.gov/catalog/item/583dc314e4b0d1899f9dea8d?format=json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
PINS={
 "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
 "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f"
}
NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
GEOD=Geod(ellps="WGS84")
MAX_GEO_KM=25.0
RADII=(100,250,500)
USER_AGENT="frogcs-plant-habitat-preflight/0.1 (+public NAAMP/NWI research)"
def fetch_json(url,params=None):
    if params:
        url=url+"?"+urllib.parse.urlencode(params)
    err=None
    for attempt in range(4):
        req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=70) as r:
                raw=r.read()
            return json.loads(raw)
        except (urllib.error.URLError,TimeoutError,OSError,ValueError) as e:
            err=e
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"GET JSON failed: {str(err)[:190]}")
def fetch_bytes(url,sha):
    err=None
    for attempt in range(4):
        req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
        try:
            with urllib.request.urlopen(req,timeout=100) as r:
                data=r.read()
            digest=hashlib.sha256(data).hexdigest()
            if digest!=sha: raise RuntimeError(f"pinned checksum mismatch {digest}")
            return data
        except (urllib.error.URLError,TimeoutError,OSError) as e:
            err=e
            time.sleep(2*(attempt+1))
    raise RuntimeError(f"GET pinned file failed {str(err)[:200]}")
def read_source_only():
    item=fetch_json(SOURCE_ITEM)
    source={}
    for name,sha in PINS.items():
        matches=[f for f in item.get("files",[]) if f.get("name")==name]
        if len(matches)!=1: raise RuntimeError(f"missing/duplicate pinned ScienceBase file {name}")
        uri=matches[0].get("downloadUri") or matches[0].get("url")
        if not uri: raise RuntimeError(f"no download URL for {name}")
        source[name]=list(csv.DictReader(io.StringIO(fetch_bytes(uri,sha).decode("utf-8-sig"))))
    source["coordinates.csv"]=list(csv.DictReader(io.StringIO(fetch_bytes(COORD_URL,COORD_SHA).decode("utf-8-sig"))))
    return source

def asfloat(x):
    try:
        return float(x)
    except (TypeError,ValueError):
        return float("nan")

def parse_year(val):
    import re
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(val or ""))
    return int(m.group(1)) if m else None

def geo_dist_km(a,b):
    _,_,d=GEOD.inv(a[1],a[0],b[1],b[0])
    return d/1000

def coordinate_gate(src):
    rawcoords=src["coordinates.csv"]
    coords={}
    conflicts=set()
    invalid={}
    for x in rawcoords:
        route=str(x.get("RouteNumber") or "").strip()
        sid=str(x.get("SiteID") or "").strip()
        key=(route,sid)
        lat=asfloat(x.get("lat"));lon=asfloat(x.get("lon"))
        if not route or not sid or not (math.isfinite(lat) and math.isfinite(lon)) or not(24<=lat<=50 and -126<=lon<=-65):
            invalid[str(key)]="outside_conus_or_nonfinite"
            continue
        if key in coords and geo_dist_km(coords[key],(lat,lon))>0.005:
            conflicts.add(key)
        else:
            coords[key]=(lat,lon)
    for key in conflicts:
        coords.pop(key,None)
    runmap={}
    for r in src["Runs.csv"]:
        year=parse_year(r.get("SurveyYear")) or parse_year(r.get("SurveyDate"))
        if year is None or not (2001<=year<=2015): continue
        if (r.get("UnifiedProtocol") or "").strip()!="1": continue
        rid=str(r.get("RunID") or "").strip()
        route=str(r.get("RouteNumber") or "").strip()
        state=str(r.get("State") or "").strip()
        if rid and route and state:
            runmap[rid]=(state,route)
    route_sites=defaultdict(dict)
    for s in src["Stops.csv"]:
        rid=str(s.get("RunID") or "").strip()
        if rid not in runmap:continue
        if (s.get("SkippedStop") or "").strip()!="0":continue
        number=str(s.get("StopNumber") or "").strip()
        siteid=str(s.get("SiteID") or "").strip()
        if not siteid or not number:continue
        state,route=runmap[rid]
        pair=(route,siteid)
        if pair in coords:
            route_sites[(state,route)][siteid]=coords[pair]
    # Unobserved route records do not enter the geographic station universe.
    accepted={}
    dropped={}
    for (state,route),sitemaps in sorted(route_sites.items()):
        points=list(sitemaps.values())
        if len(points)<8:
            dropped[f"{state}|{route}"]={"reason":"lt8_geocoded_sites","n":len(points)}
            continue
        lats=sorted(x[0] for x in points)
        lons=sorted(x[1] for x in points)
        center=(lats[len(lats)//2],lons[len(lons)//2])
        maxdev=max(geo_dist_km(center,p) for p in points)
        if maxdev>MAX_GEO_KM:
            dropped[f"{state}|{route}"]={"reason":"geometry_gt25km","n":len(points),"max_dist_km":round(maxdev,3)}
            continue
        accepted[(state,route)]={"state":state,"route":route,"center":center,
                                  "n_sites":len(points),"sites":sitemaps,
                                  "max_dist_km":maxdev}
    return accepted,{"source_coordinate_rows":len(rawcoords),"unique_coordinate_records":len(coords),
                     "conflicting_coordinate_keys":len(conflicts),
                     "conus_invalid_rows":len(invalid),
                     "source_runs_rows":len(src["Runs.csv"]),
                     "source_stops_rows":len(src["Stops.csv"]),
                     "candidate_routes":len(route_sites),
                     "geometry_eligible_routes":len(accepted),
                     "excluded_routes":len(dropped),
                     "exclusion_reasons":dict((reason,sum(x["reason"]==reason for x in dropped.values()))
                                            for reason in set(x["reason"] for x in dropped.values())),
                     "excluded_examples":dict(list(dropped.items())[:15]),
                     "response_counts_read":False}

def select_pilot(routes,number_per_state=2):
    by=defaultdict(list)
    for key,info in routes.items():
        by[key[0]].append(info)
    ans=[]
    for state,items in sorted(by.items()):
        items.sort(key=lambda a:hashlib.sha256((a["state"]+"|"+a["route"]).encode()).hexdigest())
        ans+=items[:number_per_state]
    return ans

def official_nwi_polygons(info):
    points=list(info["sites"].values())
    lat0,lon0=info["center"]
    dy=0.0055
    dx=0.0055/max(0.3,math.cos(math.radians(lat0)))
    geom={"xmin":min(p[1] for p in points)-dx,
          "ymin":min(p[0] for p in points)-dy,
          "xmax":max(p[1] for p in points)+dx,
          "ymax":max(p[0] for p in points)+dy,
          "spatialReference":{"wkid":4326}}
    rows=[]
    offset=0
    while True:
        params={
            "f":"geojson","where":"1=1",
            "geometry":json.dumps(geom,separators=(",",":")),
            "geometryType":"esriGeometryEnvelope",
            "spatialRel":"esriSpatialRelIntersects",
            "inSR":"4326","outSR":"4326",
            "outFields":"*","returnGeometry":"true",
            "resultRecordCount":"1000","resultOffset":str(offset)
        }
        data=fetch_json(NWI,params)
        if "error" in data:
            raise RuntimeError("NWI returned "+str(data["error"])[:240])
        if data.get("type")!="FeatureCollection" or not isinstance(data.get("features"),list):
            raise RuntimeError("NWI non GeoJSON response: "+str(list(data)[:8]))
        page=data["features"]
        rows.extend(page)
        if len(rows)>7000:
            raise RuntimeError("NWI route query exceeds 7000 polygons")
        if len(page)<1000 and not data.get("exceededTransferLimit",False):break
        if not page:raise RuntimeError("NWI pagination empty while has more")
        offset+=len(page)
    return rows

def classification(props):
    clean={k.split(".")[-1].upper():v for k,v in (props or {}).items()}
    label=str(clean.get("ATTRIBUTE") or "").strip().upper()
    wt=str(clean.get("WETLAND_TYPE") or "").strip()
    # Exact Cowardin class codes; e.g., PEM1C, PAB3F
    if label.startswith(("PEM","LEM","REM")):return "emergent",label,wt
    if label.startswith(("PAB","LAB","RAB")):return "aquatic_bed",label,wt
    if label.startswith(("PFO","PSS")):return "woody",label,wt
    if label.startswith(("PUB","LUB","RUB")):return "unconsolidated_bottom",label,wt
    if not label:return "unclassified",label,wt
    return "other_wetland",label,wt

def nwi_overlay(info):
    features=official_nwi_polygons(info)
    lat0,lon0=info["center"]
    crs=CRS.from_proj4(f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=m +no_defs")
    transformer=Transformer.from_crs("EPSG:4326",crs,always_xy=True).transform
    poly=[]
    classes=defaultdict(int)
    for feat in features:
        cls,attr,typ=classification(feat.get("properties"))
        classes[cls]+=1
        if feat.get("geometry") is None:continue
        try:
            geom=transform(transformer,shape(feat["geometry"]))
            if not geom.is_valid:geom=geom.buffer(0)
            if geom.is_empty:continue
        except Exception as e:
            raise RuntimeError("invalid polygon returned from NWI: "+str(e)[:160])
        poly.append((cls,geom))
    records=[]
    for sid,(lat,lon) in sorted(info["sites"].items()):
        sitepoint=Point(transformer(lon,lat))
        row={"State":info["state"],"RouteNumber":info["route"],"SiteID":sid,
             "latitude":lat,"longitude":lon,
             "source":"USFWS_NWI_2026_available_polygon_context",
             "geometry_quality_route_max_km":round(info["max_dist_km"],3),
             "nwi_service_success":True}
        for radius in RADII:
            circle=sitepoint.buffer(radius,resolution=24)
            area=float(circle.area)
            area_by=defaultdict(float)
            for cls,geom in poly:
                if geom.intersects(circle):
                    a=geom.intersection(circle).area
                    if a>0:
                        area_by[cls]+=a
                        area_by["all_wetland"]+=a
            for cls in ["emergent","aquatic_bed","woody","unconsolidated_bottom","all_wetland"]:
                value=area_by[cls]/area
                if value>1.05:
                    raise RuntimeError("NWI polygon overlap implies impossible cover >1.05")
                row[f"nwi_{cls}_cover_{radius}m"]=round(max(0,min(1,value)),6)
        records.append(row)
    return {"state":info["state"],"route":info["route"],"sites":records,
            "n_features":len(features),"n_parsed_polygon":len(poly),
            "classes":dict(classes),"status":"success"}

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--mode",choices=("pilot","full"),default="pilot")
    arg.add_argument("--per-state",type=int,default=2)
    arg.add_argument("--workers",type=int,default=3)
    opts=arg.parse_args()
    if opts.mode=="pilot" and not (1<=opts.per_state<=4):
        raise SystemExit("--per-state out of pilot bounds")
    source=read_source_only()
    routes,qc=coordinate_gate(source)
    chosen=select_pilot(routes,opts.per_state) if opts.mode=="pilot" else list(routes.values())
    allpoints=[]
    errors=[]
    classcounts=defaultdict(int)
    worked=0
    with ThreadPoolExecutor(max_workers=opts.workers) as pool:
        tasks={pool.submit(nwi_overlay,route):route for route in chosen}
        for n,future in enumerate(as_completed(tasks),1):
            info=tasks[future]
            try:
                result=future.result()
                worked+=1
                allpoints.extend(result["sites"])
                for k,v in result["classes"].items():classcounts[k]+=v
                print(f"NWI {n}/{len(chosen)} complete: {result['route']} {len(result['sites'])} site records",flush=True)
            except Exception as e:
                errors.append({"state":info["state"],"route":info["route"],
                               "error":str(e)[:240]})
                print(f"NWI {n}/{len(chosen)} failed: {info['route']} {str(e)[:120]}",flush=True)
    unique_sites=len({(r["State"],r["RouteNumber"],r["SiteID"]) for r in allpoints})
    n_emergent=sum(r["nwi_emergent_cover_250m"]>0 for r in allpoints)
    n_aquatic=sum(r["nwi_aquatic_bed_cover_250m"]>0 for r in allpoints)
    n_wetland=sum(r["nwi_all_wetland_cover_250m"]>0 for r in allpoints)
    # A route with a successful query but no wetland features is NOT proof of absent vegetation.
    status={"analysis":"naamp_nwi_aquatic_vegetation_geospatial_preflight_v0_1",
            "mode":opts.mode,"contract":CONTRACT,
            "source":{"NAAMP":"USGS ScienceBase DOI 10.5066/F7G44NG0",
                      "NWI":"USFWS official NWI Wetlands MapServer/0",
                      "coordinate_sha256":COORD_SHA,
                      "sample_selection":"SHA256 State|RouteNumber, first N per state without frog outcomes"},
            "geometry_audit":qc,
            "overlay":{"routes_attempted":len(chosen),"routes_success":worked,
                       "routes_failed":len(errors),"site_records":unique_sites,
                       "site_nwi_wetland_polygon_250m":n_wetland,
                       "site_nwi_emergent_250m":n_emergent,
                       "site_nwi_aquatic_bed_250m":n_aquatic,
                       "query_feature_classes":dict(classcounts),
                       "service_errors":errors[:15]},
            "preflight_eligible":bool(unique_sites>=100 and worked>=10 and worked>=len(chosen)/2
                                      and sum(classcounts.values())>0),
            "interpretation":{"frogs_or_Counts_csv_inspected":False,
                "nwi_polygon_classes_are_actual_aquatic_plant_species":False,
                "nwi_time_synchronized_to_2001_2015":False,
                "no_mapped_vegetation_implies_true_absence":False,
                "NWI_emergent_and_aquatic_bed_distinct":True,
                "invalid_route_coordinates_retrospectively_corrected":False,
                "RC6_manuscript_changed":False}}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"geometry_nwi_preflight.json").write_text(json.dumps(status,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    if allpoints:
        with (OUT/"site_nwi_vegetation_context.csv").open("w",newline="",encoding="utf-8") as fh:
            writer=csv.DictWriter(fh,fieldnames=list(allpoints[0]))
            writer.writeheader()
            writer.writerows(sorted(allpoints,key=lambda x:(x["State"],x["RouteNumber"],x["SiteID"])))
    print("NWI_PREFLIGHT_RESULT_BEGIN")
    print(json.dumps(status,sort_keys=True,ensure_ascii=False))
    print("NWI_PREFLIGHT_RESULT_END")
    if not status["preflight_eligible"]:
        print("NOT_ELIGIBLE: no frog outcome-linkage authorised under preflight gate.")
if __name__=="__main__":
    main()
