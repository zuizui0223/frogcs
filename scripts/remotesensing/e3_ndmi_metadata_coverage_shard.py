#!/usr/bin/env python3
"""Frozen E3 necessary metadata gate: all ten stops share one Landsat scene.

Only predefined physical site identities and dates from the frozen NAAMP pair
universe are combined with public Landsat scene *metadata*. No NDMI/QA raster
values or E3 concentration endpoint are read.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from shapely.geometry import Point, shape

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
OUT=ROOT/"remotesensing"/"e3_metadata_shards"
SHARD=int(os.environ.get("E3_SHARD_INDEX","0"))
SHARDS=int(os.environ.get("E3_SHARD_COUNT","8"))
LOOKBACK=32
STAC="https://planetarycomputer.microsoft.com/api/stac/v1/search"
COLLECTION="landsat-c2-l2"
ROLES={"nir08","swir16","qa_pixel","qa_radsat"}
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def request_json(url, body=None):
    last=None
    data=json.dumps(body).encode("utf-8") if body is not None else None
    for i in range(3):
        try:
            headers={"User-Agent":"frogcs-e3-metadata/0.1","Accept":"application/json"}
            if body is not None:
                headers["Content-Type"]="application/json"
            req=urllib.request.Request(url,data=data,headers=headers,
                method="POST" if body is not None else "GET")
            with urllib.request.urlopen(req,timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as ex:
            last=ex
            if isinstance(ex,urllib.error.HTTPError) and ex.code not in (408,429,500,502,503,504):
                raise
            if i<2:
                time.sleep(2.0*(i+1))
    raise last

def fetch_coordinates():
    req=urllib.request.Request(COORD_URL,headers={"User-Agent":"frogcs-e3-metadata/0.1"})
    with urllib.request.urlopen(req,timeout=180) as resp:
        blob=resp.read()
    if hashlib.sha256(blob).hexdigest()!=COORD_SHA:
        raise RuntimeError("coordinate_source_hash_drift")
    rows=list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"))))
    return {str(r["SiteID"]).strip():(
        str(r["RouteNumber"]).strip(),float(r["lat"]),float(r["lon"]))
        for r in rows if r.get("SiteID") and r.get("RouteNumber")}

def sensor(item_id):
    code=str(item_id).upper()
    if code.startswith(("LT04","LT05")):
        return "TM"
    if code.startswith("LE07"):
        return "ETM+"
    if code.startswith(("LC08","LC09")):
        return "OLI"
    return None

def parse_acquisition(item):
    props=item.get("properties") or {}
    raw=props.get("datetime") or props.get("start_datetime")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z","+00:00")).date()
    except ValueError:
        return None

def product_covers_all(item,coords):
    geometry=item.get("geometry")
    if geometry:
        try:
            polygon=shape(geometry)
            if polygon.is_valid and not polygon.is_empty:
                return (all(polygon.covers(Point(lon,lat)) for lat,lon in coords),
                        "polygon")
        except Exception:
            pass
    bb=item.get("bbox") or []
    if len(bb)>=4:
        return (all(bb[0]<=lon<=bb[2] and bb[1]<=lat<=bb[3]
                    for lat,lon in coords),"bbox_fallback")
    return False,"missing_geometry"

coords=fetch_coordinates()
raw,runs,pairs,pair_data,hist,pools,sampled,ss=flex.prepare_subset()
site=mem.site_map(raw,set(runs.RunID.astype(str)))
safe=hyd.strict_routes()
run_dates={str(r.RunID):date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)
           for r in runs.itertuples(index=False)}

specs={}
pair_count=0
for p,d in zip(pairs.itertuples(index=False),pair_data):
    if str(p.RouteNumber) not in safe:
        continue
    ids=mem.focal_siteids(p,d,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):
        continue
    wet,dry=str(p.wet_RunID),str(p.dry_RunID)
    if wet not in run_dates or dry not in run_dates:
        continue
    pair_count+=1
    for runid in (wet,dry):
        spec={"RunID":runid,"route_cluster":str(p.route_cluster),
              "State":str(p.State),"RouteNumber":str(p.RouteNumber),
              "survey_date":run_dates[runid].isoformat(),"siteids":list(ids)}
        if runid in specs and specs[runid]["siteids"]!=spec["siteids"]:
            raise RuntimeError("focal_run_site_identity_drift")
        specs[runid]=spec

keys=sorted(specs)
assigned=[r for i,r in enumerate(keys) if i%SHARDS==SHARD]
out=[]
for n,rid in enumerate(assigned,1):
    spec=specs[rid]
    pts=[coords[sid] for sid in spec["siteids"]]
    coords2=[(z[1],z[2]) for z in pts]
    lat=[z[0] for z in coords2]
    lon=[z[1] for z in coords2]
    d=date.fromisoformat(spec["survey_date"])
    start=d-timedelta(days=LOOKBACK)
    q={"collections":[COLLECTION],
       "bbox":[min(lon)-.01,min(lat)-.01,max(lon)+.01,max(lat)+.01],
       "datetime":start.isoformat()+"T00:00:00Z/"+d.isoformat()+"T23:59:59Z",
       "limit":100}
    rec={k:spec[k] for k in ("RunID","route_cluster","State","RouteNumber","survey_date")}
    rec.update({"resolved":False,"all10_one_product_candidate":False,
                "scene_count":0,"candidates":[],"bbox_fallback_count":0})
    try:
        data=request_json(STAC,q)
        items=data.get("features") or []
        rec["scene_count"]=len(items)
        if len(items)>=100:
            rec["error_type"]="stac_limit_100_overflow"
        else:
            candidates=[]
            for item in items:
                uid=str(item.get("id") or "")
                if not sensor(uid) or item.get("collection")!=COLLECTION:
                    continue
                if not ROLES.issubset(set((item.get("assets") or {}).keys())):
                    continue
                acquired=parse_acquisition(item)
                if acquired is None:
                    continue
                lag=(d-acquired).days
                if not 0<=lag<=LOOKBACK:
                    continue
                coverage,mode=product_covers_all(item,coords2)
                if mode=="bbox_fallback":
                    rec["bbox_fallback_count"]+=1
                if coverage:
                    candidates.append({"item_id":uid,
                        "acquisition_date":acquired.isoformat(),
                        "lag_days":lag,"footprint_check":mode})
            candidates.sort(key=lambda z:(z["lag_days"],z["item_id"]))
            rec["candidates"]=candidates
            rec["all10_one_product_candidate"]=bool(candidates)
            rec["resolved"]=True
    except Exception as ex:
        rec["error_type"]=type(ex).__name__
        if isinstance(ex,urllib.error.HTTPError):
            rec["http_error_code"]=int(ex.code)
    out.append(rec)
    if n==1 or n%10==0 or n==len(assigned):
        print(json.dumps({"shard":SHARD,"progress":n,"assigned":len(assigned),
            "RunID":rid,"resolved":rec["resolved"],
            "candidates":len(rec["candidates"])}),flush=True)
    time.sleep(1.0)  # bounded public STAC service request rate

OUT.mkdir(parents=True,exist_ok=True)
p=OUT/f"e3_ndmi_metadata_shard_{SHARD:02d}.json"
receipt={
    "analysis":"naamp_e3_ndmi_metadata_shard_v0_1",
    "contract":"revision/NAAMP_E3_NDMI_METADATA_COVERAGE_CONTRACT_V0_1.md",
    "shard_index":SHARD,
    "shard_count":SHARDS,
    "frozen_principal_pairs_total":int(len(pairs)),
    "strict_geometry_pair_specs":pair_count,
    "focal_runs":len(keys),
    "runs_assigned":len(assigned),
    "runs_resolved":sum(z["resolved"] for z in out),
    "runs_with_same_product":sum(z["all10_one_product_candidate"] for z in out),
    "rows":out,
    "ndmi_pixels_read":False,
    "frog_endpoint_calculated":False,
}
p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({k:receipt[k] for k in receipt if k!="rows"},indent=2))
