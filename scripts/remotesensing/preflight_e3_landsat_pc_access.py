#!/usr/bin/env python3
"""Outcome-blind public Landsat C2L2 access validation via Planetary Computer.

Uses only three unrelated test coordinates. Never reads NAAMP site or frog data.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

OUT = Path("remotesensing/E3_LANDSAT_C2L2_PC_ACCESS_PREFLIGHT_V0_2.json")
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN = "https://planetarycomputer.microsoft.com/api/sas/v1/sign"
COLLECTION = "landsat-c2-l2"
TESTS = (
    {"era":"2002","lon":-85.0,"lat":35.0,"start":"2002-04-01","end":"2002-05-31"},
    {"era":"2008","lon":-90.0,"lat":40.0,"start":"2008-04-01","end":"2008-05-31"},
    {"era":"2014","lon":-105.0,"lat":39.0,"start":"2014-04-01","end":"2014-05-31"},
)
ROLES = {"NIR":"nir08","SWIR1":"swir16","QA_PIXEL":"qa_pixel","QA_RADSAT":"qa_radsat"}
HEADERS = {"User-Agent":"frogcs-e3-pc-access/0.2","Accept":"application/json"}

def json_request(url, body=None):
    headers = dict(HEADERS)
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body is not None else None,
        headers=headers, method="POST" if body is not None else "GET"
    )
    with urllib.request.urlopen(req, timeout=80) as resp:
        return json.loads(resp.read().decode("utf-8"))

def sensor(item):
    code = str(item.get("id","")).upper()
    if code.startswith(("LT04","LT05")): return "TM"
    if code.startswith("LE07"): return "ETM+"
    if code.startswith(("LC08","LC09")): return "OLI"
    return None

def sign_asset(raw_href):
    if not str(raw_href).startswith("https://"):
        raise RuntimeError("asset_href_is_not_https")
    url = SIGN + "?" + urllib.parse.urlencode({"href":raw_href})
    data = json_request(url)
    signed = data.get("href")
    if not isinstance(signed,str) or not signed.startswith("https://"):
        raise RuntimeError("missing_signed_https_url")
    return signed

def tif_magic(data):
    return data[:4] in (
        bytes([73,73,42,0]), bytes([77,77,0,42]),
        bytes([73,73,43,0]), bytes([77,77,0,43])
    )

def probe(signed, lon, lat):
    # Signed URLs must never be included in any result artifact or error output.
    out = {"status":"unverified"}
    req=urllib.request.Request(
        signed,headers={"User-Agent":"frogcs-e3-pc-access/0.2",
                        "Accept":"image/tiff,application/octet-stream,*/*",
                        "Range":"bytes=0-511"}
    )
    try:
        with urllib.request.urlopen(req,timeout=80) as resp:
            buf=resp.read(512)
            out.update({
                "http_status":getattr(resp,"status",None),
                "content_type":resp.headers.get("Content-Type"),
                "content_range_present":bool(resp.headers.get("Content-Range")),
                "asset_host":urlparse(resp.geturl()).hostname,
                "tiff_magic":bool(tif_magic(buf)),
            })
        if not out["tiff_magic"]:
            out["status"]="not_tiff_bytes"
            return out
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                          GDAL_HTTP_MULTIRANGE="YES",
                          VSI_CACHE="TRUE"):
            with rasterio.open(signed) as ds:
                xs,ys=transform("EPSG:4326",ds.crs,[lon],[lat])
                row,col=ds.index(xs[0],ys[0])
                inb=(0<=row<ds.height and 0<=col<ds.width)
                out.update({
                    "crs":str(ds.crs),
                    "width":int(ds.width),"height":int(ds.height),
                    "resolution_m":[float(abs(ds.res[0])),float(abs(ds.res[1]))],
                    "index_in_bounds":bool(inb),
                    "band_count":int(ds.count),
                    "dtype":ds.dtypes[0],
                })
                if inb:
                    a=ds.read(1,window=Window(col,row,1,1))
                    out["sample_dn"]=int(a[0,0])
                out["status"]="geo_tiff_sample_ok" if inb else "outside_image_bounds"
    except Exception as ex:
        out["status"]="asset_open_failed"
        out["error_type"]=type(ex).__name__
        # Do not leak SAS URL from exception text.
    return out

results=[]
for test in TESTS:
    rec={
      "era":test["era"],"test_location":[test["lon"],test["lat"]],
      "frog_data_used":False,"focal_naamp_coordinates_used":False,
    }
    try:
        q={
          "collections":[COLLECTION],
          "bbox":[test["lon"]-.12,test["lat"]-.12,
                  test["lon"]+.12,test["lat"]+.12],
          "datetime":test["start"]+"T00:00:00Z/"+test["end"]+"T23:59:59Z",
          "limit":25,
        }
        data=json_request(STAC,q)
        scenes=data.get("features") or []
        rec["scene_count_returned"]=len(scenes)
        rec["candidate_ids"]=[str(z.get("id")) for z in scenes]
        choices=[z for z in scenes if sensor(z) and all(
            key in (z.get("assets") or {}) for key in ROLES.values())]
        if not choices:
            rec["status"]="no_matching_usgs_sensor_assets"
            results.append(rec)
            continue
        item=sorted(choices,key=lambda z:str(z.get("id")))[0]
        rec["chosen_item"]=str(item.get("id"))
        rec["sensor"]=sensor(item)
        rec["collection"]=item.get("collection")
        rec["platform"]=str((item.get("properties") or {}).get("platform"))
        rec["roles"]={}
        for role,key in ROLES.items():
            href=(item.get("assets") or {})[key].get("href")
            signed=sign_asset(href)
            rec["roles"][role]={"asset_key":key,
                                "check":probe(signed,test["lon"],test["lat"])}
        rec["status"]="all_required_assets_accessible" if all(
            v["check"]["status"]=="geo_tiff_sample_ok" for v in rec["roles"].values()
        ) else "E3_public_asset_access_inconclusive"
    except Exception as ex:
        rec["status"]="stac_or_signing_error"
        rec["error_type"]=type(ex).__name__
    results.append(rec)
    print(json.dumps({"era":rec["era"],"status":rec["status"],
                      "asset_statuses":{k:v["check"]["status"]
                          for k,v in rec.get("roles",{}).items()}},
                     sort_keys=True),flush=True)

passed=all(r["status"]=="all_required_assets_accessible" for r in results)
receipt={
  "analysis":"e3_landsat_pc_asset_access_preflight_v0_2",
  "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
  "access_repair":"revision/NAAMP_E3_LANDSAT_PC_ACCESS_REPAIR_V0_2.md",
  "collection":COLLECTION,
  "status":"E3_public_access_pass" if passed else "E3_public_asset_access_inconclusive",
  "frog_outcomes_read":False,
  "naamp_coordinates_used":False,
  "private_authentication_used":False,
  "test_results":results,
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"analysis":receipt["analysis"],"status":receipt["status"],
                  "tests":[{"era":x["era"],"status":x["status"],
                            "sensor":x.get("sensor")} for x in results]},
                 indent=2))
