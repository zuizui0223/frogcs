#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, os, re, tempfile, time, urllib.request
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
if not 2003<=YEAR<=2015:
    raise ValueError(YEAR)

PARENT="609955c9d34ea221ce33c534"
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
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-extract/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return json.loads(r.read().decode())

def fetch_bytes(url):
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-extract/0.1"})
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

# Resolve official year TIFF.
children=get_json(f"https://www.sciencebase.gov/catalog/items?parentId={PARENT}&format=json&max=100").get("items") or []
child=None
for x in children:
    if re.search(rf"\b{YEAR}\b",x.get("title") or ""):
        child=x;break
if child is None: raise RuntimeError("year child not found")
item=get_json(f"https://www.sciencebase.gov/catalog/item/{child['id']}?format=json")
tif=None
for f in item.get("files") or []:
    if (f.get("name") or "").lower().endswith(".tif"):
        tif=f;break
if tif is None: raise RuntimeError("year tif not found")
url=tif.get("downloadUri") or tif.get("url")
blob=fetch_bytes(url)
tmp=Path(tempfile.gettempdir())/f"DSWEmod_US_{YEAR}.tif"
tmp.write_bytes(blob)

# Coordinate authority.
cb=fetch_bytes(COORD_URL)
if hashlib.sha256(cb).hexdigest()!=COORD_SHA: raise RuntimeError("coordinate hash drift")
coords={}; byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(cb.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip(); rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid:continue
    lat=float(r["lat"]);lon=float(r["lon"]);coords[sid]=(rid,lat,lon);byroute[rid].append((sid,lat,lon))
safe=strict_routes(byroute)

# Frozen principal-pair RunID x physical-SiteID requests in this year.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible)
runrow={str(r.RunID):r for r in runs.itertuples(index=False)}
requests={}
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe: continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids): continue
    for runid in (str(p.wet_RunID),str(p.dry_RunID)):
        rr=runrow.get(runid)
        if rr is None or int(rr.SurveyYear)!=YEAR: continue
        month=(date(int(rr.SurveyYear),1,1)+timedelta(days=int(rr.doy)-1)).month
        spec={"RunID":runid,"RouteNumber":str(rr.RouteNumber),"route_cluster":str(rr.route_cluster),
              "State":str(rr.State),"RunNumber":str(rr.RunNumber),"year":YEAR,"month":month,"siteids":list(ids)}
        if runid in requests and requests[runid]["siteids"]!=spec["siteids"]:
            raise RuntimeError(f"RunID site identity drift {runid}")
        requests[runid]=spec

rows=[]
with rasterio.open(tmp) as ds:
    if ds.count!=12 or ds.crs is None:
        raise RuntimeError(f"DSWEmod raster identity drift count={ds.count} crs={ds.crs}")
    # Project all unique coordinates once.
    unique_sids=sorted({sid for spec in requests.values() for sid in spec["siteids"]})
    xs,ys=transform("EPSG:4326",ds.crs,[coords[s][2] for s in unique_sids],[coords[s][1] for s in unique_sids])
    xy={sid:(float(x),float(y)) for sid,x,y in zip(unique_sids,xs,ys)}
    px=float(abs(ds.transform.a))
    if not 240<=px<=260:
        raise RuntimeError(f"unexpected pixel size {px}")

    for n,(runid,spec) in enumerate(sorted(requests.items()),1):
        band=int(spec["month"])
        for sid in spec["siteids"]:
            x,y=xy[sid]
            row0,col0=ds.index(x,y)
            rec={"RunID":runid,"SiteID":sid,"RouteNumber":spec["RouteNumber"],"route_cluster":spec["route_cluster"],
                 "State":spec["State"],"RunNumber":spec["RunNumber"],"year":YEAR,"month":band}
            for radius in RADII:
                nr=int(math.ceil(radius/px))+1
                win=Window(max(0,col0-nr),max(0,row0-nr),2*nr+1,2*nr+1)
                a=ds.read(band,window=win)
                # Pixel-center geometry in projected meters.
                rows_idx=np.arange(int(win.row_off),int(win.row_off)+a.shape[0])
                cols_idx=np.arange(int(win.col_off),int(win.col_off)+a.shape[1])
                rr,cc=np.meshgrid(rows_idx,cols_idx,indexing="ij")
                pxc=ds.transform.c+(cc+0.5)*ds.transform.a
                pyc=ds.transform.f+(rr+0.5)*ds.transform.e
                mask=((pxc-x)**2+(pyc-y)**2)<=radius**2
                vals=a[mask]
                valid=np.isin(vals,[0,1,2,3,4])
                vf=float(valid.mean()) if len(vals) else 0.0
                if valid.any() and vf>=VALID_MIN:
                    vv=vals[valid]
                    rec[f"valid_frac_r{radius}"]=vf
                    rec[f"dswemod123_r{radius}"]=float(np.isin(vv,[1,2,3]).mean())
                    rec[f"dswemod1234_r{radius}"]=float(np.isin(vv,[1,2,3,4]).mean())
                    rec[f"class3_r{radius}"]=float((vv==3).mean())
                    rec[f"class4_r{radius}"]=float((vv==4).mean())
                else:
                    rec[f"valid_frac_r{radius}"]=vf
                    rec[f"dswemod123_r{radius}"]=None
                    rec[f"dswemod1234_r{radius}"]=None
                    rec[f"class3_r{radius}"]=None
                    rec[f"class4_r{radius}"]=None
            rows.append(rec)
        if n==1 or n%100==0 or n==len(requests):
            print(json.dumps({"year":YEAR,"run":n,"runs":len(requests)}),flush=True)

df=pd.DataFrame(rows)
OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/f"NAAMP_DSWEMOD_{YEAR}.csv"
jsonout=OUTDIR/f"NAAMP_DSWEMOD_{YEAR}.json"
df.to_csv(csvout,index=False,float_format="%.8g")
receipt={
 "analysis":"naamp_dswemod_year_extraction_v0_1","contract":"revision/NAAMP_MODIS_DSWEMOD_MECHANISM_CONTRACT_V0_1.md",
 "year":YEAR,"source_item":child["id"],"source_file":tif.get("name"),"downloaded_bytes":len(blob),
 "runs":len(requests),"rows":len(df),"unique_siteids":int(df.SiteID.nunique()) if len(df) else 0,
 "nonmissing_r500":int(df.dswemod123_r500.notna().sum()) if len(df) else 0,
 "nonmissing_r250":int(df.dswemod123_r250.notna().sum()) if len(df) else 0,
 "csv_sha256":hashlib.sha256(csvout.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
