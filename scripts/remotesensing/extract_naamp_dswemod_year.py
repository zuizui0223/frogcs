#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, os, re, tempfile, time, urllib.request, urllib.error, zipfile, shutil
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUTDIR=ROOT/"remotesensing"/"dswemod_years"

YEAR=int(os.environ["DSWEMOD_YEAR"])
if YEAR not in ({2003} | set(range(2005,2016))):
    raise ValueError(YEAR)

PARENT="609955c9d34ea221ce33c534"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd8343a7536"
# Correct pinned source below (kept explicit to fail closed).
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
RADII=(250,500)
VALID_MIN=.50

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-extract/0.2","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return json.loads(r.read().decode())

def fetch_bytes(url):
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-extract/0.2"})
            with urllib.request.urlopen(req,timeout=600) as r:
                return r.read()
        except Exception as e:
            last=e; time.sleep(3*(i+1))
    raise RuntimeError(f"download failed: {last}")

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088; a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    h=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1.,math.sqrt(h)))

def strict_routes(byroute):
    good=set()
    for rid,pts in byroute.items():
        bysid=defaultdict(set)
        for sid,lat,lon in pts:bysid[sid].add((lat,lon))
        if any(len(v)>1 for v in bysid.values()):continue
        u=[(sid,*next(iter(v))) for sid,v in bysid.items()]
        if len(u)<8 or any(not(24<=x[1]<=50 and -125<=x[2]<=-66) for x in u):continue
        ds=[hav(u[i][1],u[i][2],u[j][1],u[j][2]) for i in range(len(u)) for j in range(i+1,len(u))]
        if ds and max(ds)>30:continue
        mlat=float(np.median([x[1] for x in u])); mlon=float(np.median([x[2] for x in u]))
        d=np.asarray([hav(x[1],x[2],mlat,mlon) for x in u],float)
        if len(d) and float(d.max())>15:continue
        med=float(np.median(d)) if len(d) else 0.; mad=float(np.median(np.abs(d-med))) if len(d) else 0.
        if mad>0 and np.any(d>med+8*mad):continue
        good.add(rid)
    return good

def ym_shift(y,m,delta):
    z=y*12+(m-1)+delta
    return z//12,z%12+1

# Resolve official annual TIFF.
children=get_json(f"https://www.sciencebase.gov/catalog/items?parentId={PARENT}&format=json&max=100").get("items") or []
child=None
for x in children:
    if re.search(rf"\b{YEAR}\b",x.get("title") or ""):
        child=x;break
if child is None: raise RuntimeError("year child not found")
item=get_json(f"https://www.sciencebase.gov/catalog/item/{child['id']}?format=json")
tif=None
for ff in item.get("files") or []:
    if (ff.get("name") or "").lower().endswith(".tif"):
        tif=ff;break
if tif is None: raise RuntimeError("year tif not found")
url=tif.get("downloadUri") or tif.get("url")
tmp=Path(tempfile.gettempdir())/f"DSWEmod_US_{YEAR}.tif"
source_mode="child_item"
try:
    blob=fetch_bytes(url)
    tmp.write_bytes(blob)
    downloaded_bytes=len(blob)
except RuntimeError as e:
    if YEAR!=2004 or "404" not in str(e):
        raise
    # Official 2004 child file URI is broken. Fail over only to the same
    # USGS parent-release ZIP, as frozen before focal 2004 raster readback.
    parent=get_json(f"https://www.sciencebase.gov/catalog/item/{PARENT}?format=json")
    zfile=None
    for ff in parent.get("files") or []:
        if (ff.get("name") or "")=="DSWEmod_ConterminousUS_2003_2019.zip":
            zfile=ff;break
    if zfile is None:
        raise RuntimeError("official parent ZIP missing")
    zurl=zfile.get("downloadUri") or zfile.get("url")
    zpath=Path(tempfile.gettempdir())/"DSWEmod_ConterminousUS_2003_2019.zip"
    req=urllib.request.Request(zurl,headers={"User-Agent":"frogcs-dswemod-extract/0.2"})
    with urllib.request.urlopen(req,timeout=1800) as rr, zpath.open("wb") as out:
        shutil.copyfileobj(rr,out,length=1024*1024)
    downloaded_bytes=zpath.stat().st_size
    with zipfile.ZipFile(zpath) as z:
        names=[n for n in z.namelist() if Path(n).name=="DSWEmod_US_2004.tif"]
        if len(names)!=1:
            raise RuntimeError(f"expected one DSWEmod_US_2004.tif in parent ZIP, got {names}")
        with z.open(names[0]) as src, tmp.open("wb") as out:
            shutil.copyfileobj(src,out,length=1024*1024)
    source_mode="official_parent_zip_fallback"

# Coordinate authority.
cb=fetch_bytes(COORD_URL)
if hashlib.sha256(cb).hexdigest()!=COORD_SHA: raise RuntimeError("coordinate hash drift")
coords={}; byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(cb.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip(); rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid:continue
    lat=float(r["lat"]);lon=float(r["lon"]);coords[sid]=(rid,lat,lon);byroute[rid].append((sid,lat,lon))
safe=strict_routes(byroute)

# Reconstruct fixed product-period principal population and all 12-month site-month requests
# that land in this annual raster.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible)
runrow={str(r.RunID):r for r in runs.itertuples(index=False)}
requests=defaultdict(set)  # month -> SiteIDs needed in YEAR

for p,dct in zip(psub.itertuples(index=False),dsub):
    # Product availability repair: 2004 child TIFF is source-unavailable.
    allowed_years={2003} | set(range(2005,2016))
    if int(p.year_earlier) not in allowed_years or int(p.year_later) not in allowed_years:
        continue
    if str(p.RouteNumber) not in safe:
        continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):
        continue
    for runid in (str(p.wet_RunID),str(p.dry_RunID)):
        rr=runrow.get(runid)
        if rr is None:continue
        y=int(rr.SurveyYear)
        m=(date(y,1,1)+timedelta(days=int(rr.doy)-1)).month
        for k in range(12):
            yy,mm=ym_shift(y,m,-k)
            if yy==YEAR:
                requests[mm].update(ids)

rows=[]
with rasterio.open(tmp) as ds:
    if ds.count!=12 or str(ds.crs)!="EPSG:5070":
        raise RuntimeError(f"DSWEmod identity drift count={ds.count} crs={ds.crs}")
    px=float(abs(ds.transform.a))
    if not 240<=px<=260:raise RuntimeError(f"unexpected pixel size {px}")
    unique_sids=sorted({sid for sids in requests.values() for sid in sids})
    xs,ys=transform("EPSG:4326",ds.crs,[coords[s][2] for s in unique_sids],[coords[s][1] for s in unique_sids])
    xy={sid:(float(x),float(y)) for sid,x,y in zip(unique_sids,xs,ys)}

    for month in sorted(requests):
        for sid in sorted(requests[month]):
            x,y=xy[sid]
            row0,col0=ds.index(x,y)
            rec={"SiteID":sid,"year":YEAR,"month":month}
            for radius in RADII:
                nr=int(math.ceil(radius/px))+1
                row_off=max(0,row0-nr); col_off=max(0,col0-nr)
                h=min(2*nr+1,ds.height-row_off); w=min(2*nr+1,ds.width-col_off)
                if h<=0 or w<=0:
                    vals=np.asarray([],dtype=np.uint8)
                else:
                    a=ds.read(month,window=Window(col_off,row_off,w,h))
                    rows_idx=np.arange(row_off,row_off+a.shape[0])
                    cols_idx=np.arange(col_off,col_off+a.shape[1])
                    rr,cc=np.meshgrid(rows_idx,cols_idx,indexing="ij")
                    pxc=ds.transform.c+(cc+0.5)*ds.transform.a
                    pyc=ds.transform.f+(rr+0.5)*ds.transform.e
                    mask=((pxc-x)**2+(pyc-y)**2)<=radius**2
                    vals=a[mask]
                valid=np.isin(vals,[0,1,2,3,4])
                vf=float(valid.mean()) if len(vals) else 0.0
                rec[f"valid_frac_r{radius}"]=vf
                if valid.any() and vf>=VALID_MIN:
                    vv=vals[valid]
                    rec[f"dswemod123_r{radius}"]=float(np.isin(vv,[1,2,3]).mean())
                    rec[f"dswemod1234_r{radius}"]=float(np.isin(vv,[1,2,3,4]).mean())
                    rec[f"class3_r{radius}"]=float((vv==3).mean())
                    rec[f"class4_r{radius}"]=float((vv==4).mean())
                else:
                    rec[f"dswemod123_r{radius}"]=None
                    rec[f"dswemod1234_r{radius}"]=None
                    rec[f"class3_r{radius}"]=None
                    rec[f"class4_r{radius}"]=None
            rows.append(rec)
        print(json.dumps({"year":YEAR,"month":month,"sites":len(requests[month])}),flush=True)

df=pd.DataFrame(rows)
OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/f"NAAMP_DSWEMOD_MONTHLY_{YEAR}.csv"
jsonout=OUTDIR/f"NAAMP_DSWEMOD_MONTHLY_{YEAR}.json"
df.to_csv(csvout,index=False,float_format="%.8g")
receipt={
 "analysis":"naamp_dswemod_monthly_year_extraction_v0_2",
 "contract":"revision/NAAMP_MODIS_DSWEMOD_SOURCE_REPAIR_V0_3.md",
 "year":YEAR,"source_item":child["id"],"source_file":tif.get("name"),
 "source_mode":source_mode,"downloaded_bytes":downloaded_bytes,
 "extracted_tif_bytes":tmp.stat().st_size,
 "rows":len(df),"months":sorted(int(x) for x in df.month.unique()) if len(df) else [],
 "unique_siteids":int(df.SiteID.nunique()) if len(df) else 0,
 "nonmissing_r500":int(df.dswemod123_r500.notna().sum()) if len(df) else 0,
 "nonmissing_r250":int(df.dswemod123_r250.notna().sum()) if len(df) else 0,
 "csv_sha256":hashlib.sha256(csvout.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
