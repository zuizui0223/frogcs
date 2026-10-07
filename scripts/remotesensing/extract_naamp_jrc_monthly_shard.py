#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, os, time, urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUTDIR=ROOT/"remotesensing"/"shards"
SHARD_INDEX=int(os.environ.get("SHARD_INDEX","0"))
SHARD_COUNT=int(os.environ.get("SHARD_COUNT","8"))

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
HIST_BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"

RES=.00025; TILEPX=40000; ORIGIN_LON=-180.; ORIGIN_LAT=80.; BLOCK=256
RADIUS=250; VALID_FRAC_MIN=.50

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-shard/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088; a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    h=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1.,math.sqrt(h)))

def strict_routes(byroute):
    good=set()
    for route,pts in byroute.items():
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
        good.add(route)
    return good

def ym_shift(y,m,delta):
    z=y*12+(m-1)+delta
    return z//12,z%12+1

def history_url(y,m,rowoff,coloff):
    ym=f"{y:04d}_{m:02d}"
    return f"{HIST_BASE}/{y:04d}/{ym}/{ym}-{rowoff:010d}-{coloff:010d}.tif"

def tile_offsets(gr,gc):
    return (gr//TILEPX)*TILEPX,(gc//TILEPX)*TILEPX

def circle_pixels(lat,lon):
    lat_rad=RADIUS/110574.; coslat=max(.15,math.cos(math.radians(lat)))
    lon_rad=RADIUS/(111320.*coslat)
    c0=math.ceil((lon-lon_rad-ORIGIN_LON)/RES-.5); c1=math.floor((lon+lon_rad-ORIGIN_LON)/RES-.5)
    r0=math.ceil((ORIGIN_LAT-(lat+lat_rad))/RES-.5); r1=math.floor((ORIGIN_LAT-(lat-lat_rad))/RES-.5)
    rows=np.arange(r0,r1+1,dtype=np.int64); cols=np.arange(c0,c1+1,dtype=np.int64)
    rr,cc=np.meshgrid(rows,cols,indexing="ij")
    plats=ORIGIN_LAT-(rr+.5)*RES; plons=ORIGIN_LON+(cc+.5)*RES
    p1=math.radians(lat); p2=np.radians(plats); dphi=p2-p1; dlambda=np.radians(plons-lon)
    a=np.sin(dphi/2)**2+math.cos(p1)*np.cos(p2)*np.sin(dlambda/2)**2
    dist=2*6371008.8*np.arcsin(np.minimum(1.,np.sqrt(a)))
    mask=dist<=RADIUS
    return rr[mask],cc[mask]

class RS:
    def __init__(self,y,m):self.y=y;self.m=m;self.ds={};self.blocks={}
    def close(self):
        for x in self.ds.values():
            try:x.close()
            except:pass
    def _ds(self,ro,co):
        k=(ro,co)
        if k not in self.ds:
            url=history_url(self.y,self.m,ro,co); last=None
            for i in range(4):
                try:self.ds[k]=rasterio.open(url);break
                except Exception as e:last=e;time.sleep(2*(i+1))
            else:raise RuntimeError(f"open failed {url}: {last}")
        return self.ds[k]
    def block(self,ro,co,br,bc):
        k=(ro,co,br,bc)
        if k not in self.blocks:
            ds=self._ds(ro,co); row0=br*BLOCK; col0=bc*BLOCK
            h=min(BLOCK,ds.height-row0);w=min(BLOCK,ds.width-col0)
            self.blocks[k]=ds.read(1,window=Window(col0,row0,w,h))
        return self.blocks[k]
    def values(self,grs,gcs):
        out=np.empty(len(grs),dtype=np.uint8); groups=defaultdict(list)
        for i,(gr,gc) in enumerate(zip(grs,gcs)):
            ro,co=tile_offsets(int(gr),int(gc)); lr=int(gr-ro);lc=int(gc-co)
            groups[(ro,co,lr//BLOCK,lc//BLOCK)].append((i,lr,lc))
        for (ro,co,br,bc),items in groups.items():
            a=self.block(ro,co,br,bc);r0=br*BLOCK;c0=bc*BLOCK
            for i,lr,lc in items:out[i]=a[lr-r0,lc-c0]
        return out

# Coordinates and strict gate
b=fetch(COORD_URL)
if hashlib.sha256(b).hexdigest()!=COORD_SHA:raise RuntimeError("coordinate hash drift")
coords={};byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip();rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid:continue
    lat=float(r["lat"]);lon=float(r["lon"]);coords[sid]=(rid,lat,lon);byroute[rid].append((sid,lat,lon))
safe=strict_routes(byroute)

# Reconstruct fixed principal pair universe and requested 12m site-months.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible)
runmeta={str(r.RunID):{"year":int(r.SurveyYear),"month":(date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)).month} for r in runs.itertuples(index=False)}
requests=defaultdict(set)
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe:continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):continue
    for rid in (str(p.wet_RunID),str(p.dry_RunID)):
        rm=runmeta.get(rid)
        if rm is None:continue
        for sid in ids:
            for k in range(12):
                yy,mm=ym_shift(rm["year"],rm["month"],-k)
                requests[(yy,mm)].add(sid)

keys=sorted(requests)
assigned=[k for i,k in enumerate(keys) if i%SHARD_COUNT==SHARD_INDEX]
rows=[]
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MULTIRANGE="YES",VSI_CACHE="TRUE",VSI_CACHE_SIZE=67108864,GDAL_CACHEMAX=256):
    for n,(yy,mm) in enumerate(assigned,1):
        rs=RS(yy,mm)
        try:
            for sid in sorted(requests[(yy,mm)]):
                _,lat,lon=coords[sid];rr,cc=circle_pixels(lat,lon);vals=rs.values(rr,cc)
                valid=(vals==1)|(vals==2);vf=float(valid.mean()) if len(vals) else 0.
                W=float((vals[valid]==2).mean()) if valid.any() and vf>=VALID_FRAC_MIN else None
                rows.append({"SiteID":sid,"year":yy,"month":mm,"water_fraction_r250":W,"valid_frac_r250":vf})
        finally:rs.close()
        if n==1 or n%5==0 or n==len(assigned):
            print(json.dumps({"shard":SHARD_INDEX,"group":n,"groups":len(assigned),"year":yy,"month":mm}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
outcsv=OUTDIR/f"jrc_monthly_shard_{SHARD_INDEX:02d}.csv"
import pandas as pd
df=pd.DataFrame(rows);df.to_csv(outcsv,index=False,float_format="%.8g")
receipt={
 "analysis":"naamp_jrc_monthly_shard_v0_1","shard_index":SHARD_INDEX,"shard_count":SHARD_COUNT,
 "assigned_year_month_groups":len(assigned),"rows":len(df),"nonmissing_water":int(df.water_fraction_r250.notna().sum()) if len(df) else 0,
 "csv_sha256":hashlib.sha256(outcsv.read_bytes()).hexdigest(),"frog_endpoint_calculated":False
}
(OUTDIR/f"jrc_monthly_shard_{SHARD_INDEX:02d}.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
