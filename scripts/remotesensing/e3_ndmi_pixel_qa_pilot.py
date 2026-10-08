#!/usr/bin/env python3
"""Outcome-blind E3 Landsat QA/pixel-access pilot, NOT the formal coverage gate.

The source and biological metric are unchanged. This diagnostic inspects only
sensor QA and physical reflectance validity at deterministic, date-only RunIDs.
No NDMI index, CallingIndex, or concentration result is computed.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

ROOT=Path(__file__).resolve().parents[2]
META=Path(os.environ.get("E3_METADATA_PATH","remotesensing/E3_NDMI_METADATA_COVERAGE_V0_1.json"))
SHARD=int(os.environ.get("E3_PILOT_SHARD","0"))
OUT=ROOT/"remotesensing"/f"E3_NDMI_PIXEL_QA_PILOT_{SHARD}.json"
STAC="https://planetarycomputer.microsoft.com/api/stac/v1"
SIGN="https://planetarycomputer.microsoft.com/api/sas/v1/sign"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
RADIUS=500.0
SCALE=0.0000275
OFFSET=-0.2

def get(url,headers=None,decode_json=True):
    h={"User-Agent":"frogcs-e3-pixel-qa-pilot/0.1","Accept":"application/json"}
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    last=None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=100) as r:
                b=r.read()
            return json.loads(b.decode("utf-8")) if decode_json else b
        except Exception as e:
            last=e
            if attempt<2: time.sleep(3*(attempt+1))
    raise last

def sign(href):
    time.sleep(1.3)
    o=get(SIGN+"?"+urllib.parse.urlencode({"href":href}))
    signed=o.get("href")
    if not isinstance(signed,str) or not signed.startswith("https://"):
        raise RuntimeError("signed_asset_url_missing")
    return signed

def sensor(scene):
    if scene.startswith(("LT04","LT05")): return "TM"
    if scene.startswith("LE07"): return "ETM+"
    if scene.startswith(("LC08","LC09")): return "OLI"
    return "unknown"

def pick_runs(rows,era,count=6):
    lo,hi=((2001,2005),(2006,2010),(2011,2015))[era]
    good=[r for r in rows if lo<=int(r["survey_date"][:4])<=hi and r.get("candidates")]
    good.sort(key=lambda r:(hashlib.sha256(str(r["RunID"]).encode()).hexdigest(),str(r["RunID"])))
    return good[:count]

def inspect_one(run,coords):
    sc=run["candidates"][0]
    id=sc["item_id"]
    o={"RunID":str(run["RunID"]),"survey_date":run["survey_date"],
       "scene_id":id,"lag_days":sc["lag_days"],
       "qa_coverage_evaluated":False,"first_candidate_only":True}
    item=get(STAC+"/collections/landsat-c2-l2/items/"+urllib.parse.quote(id,safe=""))
    keys=["nir08","swir16","qa_pixel","qa_radsat"]
    assets=item.get("assets") or {}
    if not all(k in assets for k in keys): raise RuntimeError("missing_asset_key")
    links={k:sign(assets[k]["href"]) for k in keys}
    # Keep private signed URLs strictly in memory; never serialize/print them.
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      GDAL_HTTP_MULTIRANGE="YES",VSI_CACHE="TRUE"), contextlib.ExitStack() as stack:
        datasets={k:stack.enter_context(rasterio.open(v)) for k,v in links.items()}
        nir=datasets["nir08"]
        if any(ds.transform!=nir.transform or ds.crs!=nir.crs or
               ds.width!=nir.width or ds.height!=nir.height for ds in datasets.values()):
            raise RuntimeError("raster_grid_mismatch")
        s=sensor(id)
        if s=="unknown":raise RuntimeError("sensor_unknown")
        maskbits=sum(1<<i for i in (0,1,3,4,5,7)) | ((1<<2) if s=="OLI" else 0)
        coords_10=[coords[str(x)] for x in run["siteids"]]
        xx,yy=transform("EPSG:4326",nir.crs,
            [x[1] for x in coords_10],[x[0] for x in coords_10])
        radius_pixels=int(math.ceil(RADIUS/abs(nir.transform.a)))+2
        stops=[]
        for ix,(x,y) in enumerate(zip(xx,yy)):
            r,c=nir.index(x,y)
            row=max(0,int(r)-radius_pixels); col=max(0,int(c)-radius_pixels)
            h=min(nir.height-row,2*radius_pixels+1)
            w=min(nir.width-col,2*radius_pixels+1)
            if h<=0 or w<=0: raise RuntimeError("point_out_of_raster")
            win=Window(col,row,w,h)
            shapes={}
            for k,ds in datasets.items(): shapes[k]=ds.read(1,window=win)
            row_idx=np.arange(row,row+h);col_idx=np.arange(col,col+w)
            rr,cc=np.meshgrid(row_idx,col_idx,indexing="ij")
            xg=nir.transform.c+(cc+.5)*nir.transform.a
            yg=nir.transform.f+(rr+.5)*nir.transform.e
            circ=((xg-x)**2+(yg-y)**2)<=RADIUS**2
            n=int(circ.sum())
            if not n: raise RuntimeError("empty_circle")
            qa=shapes["qa_pixel"]
            sat=shapes["qa_radsat"]
            nir_refl=shapes["nir08"]*SCALE+OFFSET
            swir_refl=shapes["swir16"]*SCALE+OFFSET
            valid=(((qa & maskbits)==0)&(sat==0)&
                 np.isfinite(nir_refl)&np.isfinite(swir_refl)&
                 (nir_refl>0)&(nir_refl<=1)&(swir_refl>0)&(swir_refl<=1))
            frac=float((valid&circ).sum()/n)
            stops.append({"stop_index":ix+1,"valid_fraction":frac,
                          "passed_70pct":bool(frac>=.70),
                          "candidate_pixels":n})
    o["qa_coverage_evaluated"]=True
    o["all10_qa70_first_candidate"]=all(s["passed_70pct"] for s in stops)
    o["mean_valid_fraction"]=float(np.mean([s["valid_fraction"] for s in stops]))
    o["stops"]=stops
    return o

obj=json.loads(META.read_text())
if obj.get("classification")!="metadata_necessary_gate_pass":
    raise RuntimeError("metadata_necessary_gate_not_passed")
rows=obj["metadata_run_rows"]
# Reconstruct the already-frozen RunID × ten-SiteID identity without
# looking at NDMI, QA results, or the concentration endpoint.
import importlib.util
def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module
flex=loadmod("flex",ROOT/"exploration"/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",ROOT/"scripts"/"remotesensing"/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem
raw,runs,pairs,pair_data,hist,pools,sampled,ss=flex.prepare_subset()
site=mem.site_map(raw,set(runs.RunID.astype(str)))
safe=hyd.strict_routes()
byrun={}
for p,d in zip(pairs.itertuples(index=False),pair_data):
    if str(p.RouteNumber) not in safe:
        continue
    ids=mem.focal_siteids(p,d,site)
    if ids is None or len(ids)!=10:
        continue
    for runid in (str(p.wet_RunID),str(p.dry_RunID)):
        if runid in byrun and byrun[runid]!=list(ids):
            raise RuntimeError("focal_site_identity_drift")
        byrun[runid]=list(ids)
cb=get(COORD_URL,decode_json=False)
if hashlib.sha256(cb).hexdigest()!=COORD_SHA: raise RuntimeError("coordinate_sha_drift")
import csv,io
coords={str(r["SiteID"]).strip():(float(r["lat"]),float(r["lon"]))
        for r in csv.DictReader(io.StringIO(cb.decode("utf-8-sig"))) if r.get("SiteID")}
runs=pick_runs(rows,SHARD)
results=[]
for i,run in enumerate(runs,1):
    record=dict(run)
    record["siteids"]=byrun[str(run["RunID"])]
    try:
        rr=inspect_one(record,coords)
    except Exception as ex:
        rr={"RunID":str(run["RunID"]),"survey_date":run["survey_date"],
            "scene_id":run["candidates"][0]["item_id"],
            "error_type":type(ex).__name__,
            "qa_coverage_evaluated":False}
    results.append(rr)
    print(json.dumps({"era_shard":SHARD,"run":i,"runs":len(runs),
          "qa_coverage_evaluated":rr["qa_coverage_evaluated"],
          "all10_qa70_first_candidate":rr.get("all10_qa70_first_candidate")}),flush=True)
out={"analysis":"e3_ndmi_pixel_qa_pilot_v0_1","role":"diagnostic_not_formal_gate",
     "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
     "era_shard":SHARD,"sample_rule":"6 smallest SHA256 RunID per era, dates only",
     "pilot_runs":len(results),
     "qa_evaluated":sum(x["qa_coverage_evaluated"] for x in results),
     "first_candidate_full_qa":sum(x.get("all10_qa70_first_candidate",False) for x in results),
     "NDMI_computed":False,"frog_endpoint_calculated":False,
     "no_fallback_attempted":True,"records":results}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in out.items() if k!="records"},indent=2))
