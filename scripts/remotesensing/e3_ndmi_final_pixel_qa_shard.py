#!/usr/bin/env python3
"""E3 Landsat NDMI outcome-blind FINAL pixel-quality coverage shard.

Scientific parameters are exclusively from the frozen final E3 contract.
This script reads physical coordinates, dates, and Landsat bands used for
QA and reflectance validity. It does NOT calculate NDMI or a frog endpoint.
"""
from __future__ import annotations

import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

ROOT=Path(__file__).resolve().parents[2]
META=Path(os.environ.get("E3_METADATA_PATH",
    str(ROOT/"remotesensing"/"E3_NDMI_METADATA_COVERAGE_V0_1.json")))
SHARD=int(os.environ.get("E3_PIXEL_SHARD","0"))
SHARDS=int(os.environ.get("E3_PIXEL_SHARDS","16"))
OUTDIR=ROOT/"remotesensing"/"e3_pixel_shards"
STAC="https://planetarycomputer.microsoft.com/api/stac/v1"
SIGN="https://planetarycomputer.microsoft.com/api/sas/v1/sign"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
RADIUS=500.0
VALID_MIN=.70
SCALE=.0000275
OFFSET=-.2
ASSETS=("nir08","swir16","qa_pixel","qa_radsat")
MAX_DIAGNOSTIC=int(os.environ.get("E3_DIAGNOSTIC_MAX_RUNS","0"))

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m)
    return m

def get(url,as_json=True):
    last=None
    for attempt in range(4):
        req=urllib.request.Request(url,headers={
            "User-Agent":"frogcs-e3-frozen-pixel-gate/0.1","Accept":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=110) as r:
                b=r.read()
            return json.loads(b.decode("utf-8")) if as_json else b
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            last=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in (408,429,500,502,503,504):
                break
            time.sleep(2*(attempt+1))
    raise last

def signed_href(href):
    # Single official SAS signing route for the STAC-returned asset URL.
    time.sleep(1.0)
    x=get(SIGN+"?"+urllib.parse.urlencode({"href":href}))
    s=x.get("href")
    if not isinstance(s,str) or not s.startswith("https://"):
        raise RuntimeError("signed_asset_url_missing")
    return s

def sensor(itemid):
    if itemid.startswith(("LT04","LT05")): return "TM"
    if itemid.startswith("LE07"): return "ETM+"
    if itemid.startswith(("LC08","LC09")): return "OLI"
    raise RuntimeError("unsupported_sensor")

def quality_for_item(itemid,siteids,coords):
    item=get(STAC+"/collections/landsat-c2-l2/items/"+
             urllib.parse.quote(itemid,safe=""))
    assets=item.get("assets") or {}
    if not all(k in assets and isinstance(assets[k].get("href"),str) for k in ASSETS):
        raise RuntimeError("incomplete_stac_assets")
    links={k:signed_href(assets[k]["href"]) for k in ASSETS}
    s=sensor(itemid)
    # fill,dilated_cloud,cloud,shadow,snow,water; additionally cirrus for OLI.
    bits=sum(1<<b for b in (0,1,3,4,5,7))
    if s=="OLI": bits|=1<<2
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      GDAL_HTTP_MULTIRANGE="YES",VSI_CACHE="TRUE",
                      VSI_CACHE_SIZE=67108864),contextlib.ExitStack() as stack:
        ras={k:stack.enter_context(rasterio.open(links[k])) for k in ASSETS}
        nir=ras["nir08"]
        if any(z.crs!=nir.crs or z.transform!=nir.transform or
               z.width!=nir.width or z.height!=nir.height for z in ras.values()):
            raise RuntimeError("raster_grid_mismatch")
        points=[coords[str(sid)] for sid in siteids]
        xx,yy=transform("EPSG:4326",nir.crs,[p[1] for p in points],
                         [p[0] for p in points])
        # Full nominal pixel circle is retained, including any scene-edge pixels.
        pix=min(abs(nir.transform.a),abs(nir.transform.e))
        radius_pix=int(math.ceil(RADIUS/pix))+2
        fracs=[]
        for x,y in zip(xx,yy):
            row,col=nir.index(x,y)
            win=Window(int(col)-radius_pix,int(row)-radius_pix,
                       2*radius_pix+1,2*radius_pix+1)
            grids={k:ds.read(1,window=win,boundless=True,fill_value=0)
                   for k,ds in ras.items()}
            rr,cc=np.meshgrid(
                np.arange(win.row_off,win.row_off+win.height,dtype=float),
                np.arange(win.col_off,win.col_off+win.width,dtype=float),
                indexing="ij")
            xg=nir.transform.c+(cc+.5)*nir.transform.a+(rr+.5)*nir.transform.b
            yg=nir.transform.f+(cc+.5)*nir.transform.d+(rr+.5)*nir.transform.e
            circle=((xg-x)**2+(yg-y)**2)<=RADIUS**2
            n=int(circle.sum())
            if n==0: raise RuntimeError("zero_nominal_pixels")
            q=grids["qa_pixel"]; sat=grids["qa_radsat"]
            nir_sr=grids["nir08"].astype(np.float32)*SCALE+OFFSET
            swir_sr=grids["swir16"].astype(np.float32)*SCALE+OFFSET
            valid=(np.bitwise_and(q,bits)==0)&(sat==0)
            valid&=np.isfinite(nir_sr)&np.isfinite(swir_sr)
            valid&=(nir_sr>0)&(nir_sr<=1)&(swir_sr>0)&(swir_sr<=1)
            frac=float((valid&circle).sum()/n)
            fracs.append(frac)
        return fracs

metadata=META.read_bytes()
obj=json.loads(metadata)
if obj.get("classification")!="metadata_necessary_gate_pass":
    raise RuntimeError("necessary_metadata_gate_not_passed")
rows=obj["metadata_run_rows"]
flex=loadmod("flex",ROOT/"exploration"/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",ROOT/"scripts"/"remotesensing"/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem
raw,runs,pairs,pair_data,hist,pools,sampled,ss=flex.prepare_subset()
site=mem.site_map(raw,set(runs.RunID.astype(str)))
safe=hyd.strict_routes()
byrun={}
for p,d in zip(pairs.itertuples(index=False),pair_data):
    if str(p.RouteNumber) not in safe: continue
    ids=mem.focal_siteids(p,d,site)
    if ids is None or len(ids)!=10: continue
    for rid in (str(p.wet_RunID),str(p.dry_RunID)):
        if rid in byrun and byrun[rid]!=list(ids):
            raise RuntimeError("focal_site_identity_drift")
        byrun[rid]=list(ids)
coordinate_bytes=get(COORD_URL,as_json=False)
if hashlib.sha256(coordinate_bytes).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate_hash_drift")
coords={str(r["SiteID"]).strip():(float(r["lat"]),float(r["lon"]))
        for r in csv.DictReader(io.StringIO(coordinate_bytes.decode("utf-8-sig")))
        if r.get("SiteID")}

assigned=[r for i,r in enumerate(sorted(rows,key=lambda z:str(z["RunID"])))
          if i%SHARDS==SHARD]
if MAX_DIAGNOSTIC:
    assigned=assigned[:MAX_DIAGNOSTIC]
out=[]
for n,run in enumerate(assigned,1):
    rid=str(run["RunID"])
    rec={"RunID":rid,"survey_date":run["survey_date"],
         "route_cluster":run["route_cluster"],"State":run["State"],
         "status":"unresolved","selected_item":None,"selected_date":None,
         "selected_lag_days":None,"candidates_count":len(run.get("candidates") or []),
         "attempted":0,"qa_evaluated":0,"source_errors":0,
         "valid_frac_min":None,"valid_frac_median":None}
    ids=byrun.get(rid)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):
        raise RuntimeError("frozen_identity_mismatch:"+rid)
    for candidate in run.get("candidates") or []:
        if not 0<=int(candidate["lag_days"])<=32:
            raise RuntimeError("candidate_outside_frozen_window")
        rec["attempted"]+=1
        try:
            fracs=quality_for_item(candidate["item_id"],ids,coords)
            rec["qa_evaluated"]+=1
        except Exception as e:
            rec["source_errors"]+=1
            rec["last_source_error"]=type(e).__name__
            if isinstance(e,urllib.error.HTTPError):
                rec["last_http_error"]=e.code
            continue
        if len(fracs)==10 and min(fracs)>=VALID_MIN:
            rec.update({"status":"qa_pass","selected_item":candidate["item_id"],
               "selected_date":candidate["acquisition_date"],
               "selected_lag_days":candidate["lag_days"],
               "valid_frac_min":float(min(fracs)),
               "valid_frac_median":float(np.median(fracs))})
            break
    if rec["status"]!="qa_pass":
        rec["status"]="source_unresolved" if rec["source_errors"] else "qa_no_valid_scene"
    out.append(rec)
    if n==1 or n%10==0 or n==len(assigned):
        print(json.dumps({"shard":SHARD,"done":n,"total":len(assigned),
            "qa_pass":sum(v["status"]=="qa_pass" for v in out),
            "source_unresolved":sum(v["status"]=="source_unresolved" for v in out)}),flush=True)
    # Small service-pacing pause, not a scientific parameter.
    time.sleep(.5)

receipt={"analysis":"e3_ndmi_final_pixel_qa_shard_v0_1",
 "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
 "source_metadata_sha256":hashlib.sha256(metadata).hexdigest(),
 "shard_index":SHARD,"shard_count":SHARDS,
 "diagnostic_run_limit":MAX_DIAGNOSTIC,"runs_assigned":len(assigned),
 "status_counts":dict(Counter(x["status"] for x in out)),
 "NDMI_computed":False,"frog_endpoint_calculated":False,"rows":out}
OUTDIR.mkdir(parents=True,exist_ok=True)
p=OUTDIR/f"e3_ndmi_final_pixel_qa_shard_{SHARD:02d}.json"
p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="rows"},indent=2))
