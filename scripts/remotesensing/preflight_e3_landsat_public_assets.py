#!/usr/bin/env python3
"""Outcome-blind public access preflight for the final Landsat E3 contract."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

OUT=Path("remotesensing/E3_LANDSAT_C2L2_SR_PUBLIC_ASSET_PREFLIGHT_V0_1.json")
STAC="https://landsatlook.usgs.gov/stac-server/search"
COLLECTION="landsat-c2l2-sr"

# Arbitrary test points; none comes from NAAMP, and no frog data is used.
TESTS=(
  {"era":"2002","lon":-85.0,"lat":35.0,"start":"2002-04-01","end":"2002-05-31"},
  {"era":"2008","lon":-90.0,"lat":40.0,"start":"2008-04-01","end":"2008-05-31"},
  {"era":"2014","lon":-105.0,"lat":39.0,"start":"2014-04-01","end":"2014-05-31"},
)

def post(query):
    req=urllib.request.Request(
      STAC,data=json.dumps(query).encode("utf-8"),method="POST",
      headers={"Content-Type":"application/json","Accept":"application/geo+json",
               "User-Agent":"frogcs-e3-landsat-access-preflight/0.1"}
    )
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

def platform_from_id(item):
    name=str(item.get("id","")).upper()
    if name.startswith(("LC08","LC09")):return "OLI"
    if name.startswith(("LE07",)):return "ETM+"
    if name.startswith(("LT05","LT04")):return "TM"
    platform=str((item.get("properties") or {}).get("platform","")).lower()
    if "landsat-8" in platform:return "OLI"
    if "landsat-7" in platform:return "ETM+"
    if "landsat-5" in platform:return "TM"
    return None

def locate_asset(item,desired):
    assets=item.get("assets") or {}
    by_lower={str(k).lower(): (str(k),v) for k,v in assets.items()}
    entry=by_lower.get(desired.lower())
    return entry

def probe(href):
    # Read only the beginning of the server response; do not retrieve full rasters.
    if not isinstance(href,str) or not href.startswith(("http://","https://")):
        return {"status":"not_http_asset","href_scheme":str(href).split(":",1)[0] if href else None}
    req=urllib.request.Request(
      href,headers={"User-Agent":"frogcs-e3-landsat-access-preflight/0.1",
                    "Range":"bytes=0-511","Accept":"image/tiff,application/octet-stream,*/*"}
    )
    try:
        with urllib.request.urlopen(req,timeout=75) as r:
            b=r.read(512)
            final=r.geturl()
            ct=r.headers.get("Content-Type")
            tiff=b.startswith((b"II\\x2a\\x00",b"MM\\x00\\x2a",b"II\\x2b\\x00",b"MM\\x00\\x2b"))
            # Literal byte signatures are detected below as well.
            tiff=tiff or b[:4] in (bytes([73,73,42,0]),bytes([77,77,0,42]),
                                  bytes([73,73,43,0]),bytes([77,77,0,43]))
            return {
              "status":"raster_accessible" if tiff else "not_verified_tiff",
              "http_status":getattr(r,"status",None),
              "final_host":urlparse(final).netloc,
              "url_redirected":final!=href,
              "content_type":ct,
              "content_range":r.headers.get("Content-Range"),
              "sample_bytes":len(b),
              "tiff_magic":bool(tiff)
            }
    except Exception as e:
        return {"status":"asset_request_failed","exception":type(e).__name__,"detail":str(e)[:220]}

results=[]
for test in TESTS:
    bbox=[test["lon"]-.12,test["lat"]-.12,test["lon"]+.12,test["lat"]+.12]
    query={
      "collections":[COLLECTION],"bbox":bbox,
      "datetime":f'{test["start"]}T00:00:00Z/{test["end"]}T23:59:59Z',
      "limit":15
    }
    result={"era":test["era"],"test_location":[test["lon"],test["lat"]],
            "window":[test["start"],test["end"]],"frog_data_used":False}
    try:
        obj=post(query)
        feats=obj.get("features") or []
        result["scene_count_returned"]=len(feats)
        result["candidate_ids"]=[str(x.get("id")) for x in feats]
        item=next((x for x in sorted(feats,key=lambda t:str(t.get("id","")))
                   if platform_from_id(x) is not None),None)
        if item is None:
            result["status"]="no_sensor_mapped_scene"
            results.append(result); continue
        sensor=platform_from_id(item)
        result["chosen_item"]=item.get("id")
        result["sensor"]=sensor
        result["all_asset_keys"]=sorted((item.get("assets") or {}).keys())
        bands=("SR_B5","SR_B6") if sensor=="OLI" else ("SR_B4","SR_B5")
        needed={"NIR":bands[0],"SWIR1":bands[1],"QA_PIXEL":"QA_PIXEL","QA_RADSAT":"QA_RADSAT"}
        probes={}
        for role,key in needed.items():
            entry=locate_asset(item,key)
            if entry is None:
                probes[role]={"status":"missing_asset_key","wanted":key}
            else:
                actual,asset=entry
                probes[role]={"asset_key":actual,"probe":probe(asset.get("href"))}
        result["assets"]=probes
        result["status"]=("all_required_assets_accessible" if all(
          p.get("probe",{}).get("status")=="raster_accessible" for p in probes.values()
        ) else "source_or_asset_access_inconclusive")
    except Exception as e:
        result["status"]="stac_request_failed"
        result["error"]=type(e).__name__+": "+str(e)[:300]
    results.append(result)

ok=all(z["status"]=="all_required_assets_accessible" for z in results)
receipt={
  "analysis":"e3_landsat_public_asset_preflight_v0_1",
  "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
  "scene_collection":COLLECTION,
  "response_values_read":False,
  "naamp_focal_coordinates_used":False,
  "overall":"E3_public_access_pass" if ok else "E3_public_asset_access_inconclusive",
  "test_results":results
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(receipt,indent=2,ensure_ascii=False))
