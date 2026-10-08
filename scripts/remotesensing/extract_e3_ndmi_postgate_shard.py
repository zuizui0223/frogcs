#!/usr/bin/env python3
"""Outcome-blind E3 NDMI extraction, permitted only after the frozen pixel QA gate passes.

Do not change scene, site, buffer, QA, reflectance scaling, or selection rules.
Output is RunID x physical SiteID, ready for a separately guarded M0/M_E3 test.
"""
from __future__ import annotations
import contextlib,csv,hashlib,importlib.util,io,json,math,os,time
import urllib.error,urllib.parse,urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUTDIR=ROOT/"remotesensing"/"e3_extracted"
META=Path(os.environ.get("E3_METADATA_PATH",str(ROOT/"remotesensing"/"E3_NDMI_METADATA_COVERAGE_V0_1.json")))
GATE=Path(os.environ.get("E3_PIXEL_GATE_PATH",str(ROOT/"remotesensing"/"E3_NDMI_FINAL_PIXEL_COVERAGE_V0_1.json")))
SHARD=int(os.environ.get("E3_EXTRACTION_SHARD","0"))
SHARDS=int(os.environ.get("E3_EXTRACTION_SHARDS","16"))
STAC="https://planetarycomputer.microsoft.com/api/stac/v1"
SIGN="https://planetarycomputer.microsoft.com/api/sas/v1/sign"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
ASSETS=("nir08","swir16","qa_pixel","qa_radsat")
RADIUS=500.0
VALID_MIN=.70
SCALE=.0000275
OFFSET=-.2

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader;spec.loader.exec_module(m);return m

def fetch(url,as_json=True):
    last=None
    for attempt in range(4):
        req=urllib.request.Request(url,headers={"User-Agent":"frogcs-e3-postgate/0.1","Accept":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r:b=r.read()
            return json.loads(b.decode("utf-8")) if as_json else b
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            last=e
            if isinstance(e,urllib.error.HTTPError) and e.code not in (408,429,500,502,503,504):break
            time.sleep(2*(attempt+1))
    raise last

def sign(href):
    time.sleep(1.)
    obj=fetch(SIGN+"?"+urllib.parse.urlencode({"href":href}))
    out=obj.get("href")
    if not isinstance(out,str) or not out.startswith("https://"):raise RuntimeError("invalid_signed_href")
    return out

def sensor(itemid):
    if itemid.startswith(("LT04","LT05")):return "TM"
    if itemid.startswith("LE07"):return "ETM+"
    if itemid.startswith(("LC08","LC09")):return "OLI"
    raise RuntimeError("unsupported_landsat_sensor:"+itemid)

def get_site_data(assets,itemid,sids,coords):
    s=sensor(itemid)
    bits=sum(1<<b for b in (0,1,3,4,5,7))
    if s=="OLI":bits|=1<<2
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_MULTIRANGE="YES",
                      VSI_CACHE="TRUE",VSI_CACHE_SIZE=67108864),contextlib.ExitStack() as stack:
        d={k:stack.enter_context(rasterio.open(assets[k])) for k in ASSETS}
        ref=d["nir08"]
        if any(z.crs!=ref.crs or z.transform!=ref.transform or z.width!=ref.width or z.height!=ref.height for z in d.values()):
            raise RuntimeError("e3_raster_grid_mismatch")
        pts=[coords[str(sid)] for sid in sids]
        xx,yy=transform("EPSG:4326",ref.crs,[p[1] for p in pts],[p[0] for p in pts])
        pix=min(abs(ref.transform.a),abs(ref.transform.e))
        radius_pix=int(math.ceil(RADIUS/pix))+2
        vals={}
        for sid,x,y in zip(sids,xx,yy):
            row,col=ref.index(x,y)
            win=Window(int(col)-radius_pix,int(row)-radius_pix,2*radius_pix+1,2*radius_pix+1)
            a={k:ds.read(1,window=win,boundless=True,fill_value=0) for k,ds in d.items()}
            rr,cc=np.meshgrid(np.arange(win.row_off,win.row_off+win.height,dtype=float),
                              np.arange(win.col_off,win.col_off+win.width,dtype=float),indexing="ij")
            xc=ref.transform.c+(cc+.5)*ref.transform.a+(rr+.5)*ref.transform.b
            yc=ref.transform.f+(cc+.5)*ref.transform.d+(rr+.5)*ref.transform.e
            circle=((xc-x)**2+(yc-y)**2)<=RADIUS**2
            n=int(circle.sum())
            if n==0:raise RuntimeError("zero_nominal_e3_pixels")
            nir=a["nir08"].astype(np.float32)*SCALE+OFFSET
            swir=a["swir16"].astype(np.float32)*SCALE+OFFSET
            good=(np.bitwise_and(a["qa_pixel"],bits)==0)&(a["qa_radsat"]==0)
            good&=np.isfinite(nir)&np.isfinite(swir)
            good&=(nir>0)&(nir<=1)&(swir>0)&(swir<=1)
            valid=good&circle
            fraction=float(valid.sum()/n)
            if fraction<VALID_MIN:raise RuntimeError("selected_item_qa_regression")
            ndmi=(nir[valid]-swir[valid])/(nir[valid]+swir[valid])
            if len(ndmi)==0 or not np.isfinite(ndmi).all():raise RuntimeError("nonfinite_NDMI")
            vals[str(sid)]={
               "NDMI_r500":float(np.median(ndmi)),
               "valid_pixel_fraction":fraction,
               "nominal_pixels":n,"valid_pixels":int(valid.sum())
            }
        return vals

if not GATE.exists() or not META.exists():
    raise RuntimeError("missing_frozen_pre_response_E3_receipts")
gate=json.loads(GATE.read_text())
meta_bytes=META.read_bytes()
if gate.get("classification")!="E3_pixel_QA_coverage_gate_pass":
    raise RuntimeError("E3_pixel_gate_not_passed_NDMI_must_not_be_read")
if gate.get("source_metadata_sha256")!=hashlib.sha256(meta_bytes).hexdigest():
    raise RuntimeError("E3_metadata_identity_drift")
if gate.get("NDMI_values_read") or gate.get("frog_endpoint_calculated"):
    raise RuntimeError("wrong_E3_gate_stage")
selected=gate.get("selected_run_rows") or []
if not selected:raise RuntimeError("E3_gate_pass_without_selected_runs")
if len(selected)!=len({str(z["RunID"]) for z in selected}):
    raise RuntimeError("duplicate_selected_RunID")

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem
raw,runs,pairs,pair_data,hist,pools,sampled,ss=flex.prepare_subset()
site=mem.site_map(raw,set(runs.RunID.astype(str)))
byrun={}
for p,dct in zip(pairs.itertuples(index=False),pair_data):
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:continue
    for rid in (str(p.wet_RunID),str(p.dry_RunID)):
        if rid in byrun and byrun[rid]!=list(ids):raise RuntimeError("RunID_site_identity_drift")
        byrun[rid]=list(ids)
coord_bytes=fetch(COORD_URL,as_json=False)
if hashlib.sha256(coord_bytes).hexdigest()!=COORD_SHA:raise RuntimeError("E3_coordinate_source_drift")
coords={str(r["SiteID"]).strip():(float(r["lat"]),float(r["lon"]))
        for r in csv.DictReader(io.StringIO(coord_bytes.decode("utf-8-sig"))) if r.get("SiteID")}

# Route fold is not used for image choice; this hash only assigns I/O shards.
chosen=sorted([r for r in selected
              if int(hashlib.sha256(str(r["RunID"]).encode()).hexdigest()[:8],16)%SHARDS==SHARD],
              key=lambda z:(str(z["selected_item"]),str(z["RunID"])))
byitem=defaultdict(list)
for rec in chosen:byitem[str(rec["selected_item"])].append(rec)
out=[]
for i,(itemid,recs) in enumerate(sorted(byitem.items()),1):
    item=fetch(STAC+"/collections/landsat-c2-l2/items/"+urllib.parse.quote(itemid,safe=""))
    assets=item.get("assets") or {}
    if any(k not in assets or not isinstance(assets[k].get("href"),str) for k in ASSETS):
        raise RuntimeError("incomplete_stac_assets")
    links={k:sign(assets[k]["href"]) for k in ASSETS}
    unique_sids=sorted({str(sid) for z in recs for sid in byrun.get(str(z["RunID"]),[])})
    if any(s not in coords for s in unique_sids):raise RuntimeError("unavailable_site_coordinate")
    measures=get_site_data(links,itemid,unique_sids,coords)
    for z in recs:
        rid=str(z["RunID"])
        ids=byrun.get(rid)
        if ids is None or len(ids)!=10:raise RuntimeError("selected_run_missing_ten_sites")
        vals=[measures[str(sid)] for sid in ids]
        if min(x["valid_pixel_fraction"] for x in vals)<VALID_MIN:
            raise RuntimeError("selected_run_qa_gate_drift")
        for sid,x in zip(ids,vals):
            out.append({
             "RunID":rid,"SiteID":str(sid),"NDMI_r500":x["NDMI_r500"],
             "valid_pixel_fraction":x["valid_pixel_fraction"],"nominal_pixels":x["nominal_pixels"],
             "valid_pixels":x["valid_pixels"],"selected_item":itemid,
             "acquisition_date":z["selected_date"],"lag_days":int(z["selected_lag_days"])
            })
    if i==1 or i%10==0 or i==len(byitem):
        print(json.dumps({"shard":SHARD,"item":i,"items":len(byitem),"rows":len(out)}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
frame=pd.DataFrame(out)
if len(frame)!=10*len(chosen) or frame.duplicated(["RunID","SiteID"]).any():
    raise RuntimeError("E3_extraction_rows_not_ten_per_run")
csvout=OUTDIR/f"E3_NDMI_RUN_SITE_SHARD_{SHARD:02d}.csv"
recout=OUTDIR/f"E3_NDMI_RUN_SITE_SHARD_{SHARD:02d}.json"
frame.to_csv(csvout,index=False,float_format="%.9g")
receipt={
 "analysis":"e3_ndmi_outcome_blind_extraction_shard_v0_1",
 "contract":"revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md",
 "pixel_coverage_sha256":hashlib.sha256(GATE.read_bytes()).hexdigest(),
 "metadata_sha256":hashlib.sha256(meta_bytes).hexdigest(),
 "shard":SHARD,"shards":SHARDS,"runids":len(chosen),"rows":len(frame),
 "item_count":len(byitem),"csv_sha256":hashlib.sha256(csvout.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False}
recout.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps(receipt,indent=2,sort_keys=True))
