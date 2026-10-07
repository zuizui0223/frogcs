#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, time, urllib.request
from collections import defaultdict, Counter
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUTCSV=ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_COVERAGE_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

HIST_BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles"

RES=0.00025
TILEPX=40000
ORIGIN_LON=-180.0
ORIGIN_LAT=80.0
BLOCK=256
RADIUS=250
VALID_FRAC_MIN=0.50
MIN_VALID_12M=9

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-variability/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    h=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1.0,math.sqrt(h)))

def strict_routes(byroute):
    good=set()
    for route,pts in byroute.items():
        bysid=defaultdict(set)
        for sid,lat,lon in pts:
            bysid[sid].add((lat,lon))
        if any(len(v)>1 for v in bysid.values()):
            continue
        u=[]
        for sid,v in bysid.items():
            lat,lon=next(iter(v)); u.append((sid,lat,lon))
        if len(u)<8 or any(not (24<=x[1]<=50 and -125<=x[2]<=-66) for x in u):
            continue
        ds=[hav(u[i][1],u[i][2],u[j][1],u[j][2]) for i in range(len(u)) for j in range(i+1,len(u))]
        if ds and max(ds)>30:
            continue
        mlat=float(np.median([x[1] for x in u])); mlon=float(np.median([x[2] for x in u]))
        d=np.asarray([hav(x[1],x[2],mlat,mlon) for x in u],float)
        if len(d) and float(d.max())>15:
            continue
        med=float(np.median(d)) if len(d) else 0.0
        mad=float(np.median(np.abs(d-med))) if len(d) else 0.0
        if mad>0 and np.any(d>med+8*mad):
            continue
        good.add(route)
    return good

def history_url(year,month,rowoff,coloff):
    ym=f"{year:04d}_{month:02d}"
    return f"{HIST_BASE}/{year:04d}/{ym}/{ym}-{rowoff:010d}-{coloff:010d}.tif"

def tile_offsets_from_global(grow,gcol):
    # JRC filenames are ROW_OFFSET-COLUMN_OFFSET, not column-row.
    return (grow//TILEPX)*TILEPX,(gcol//TILEPX)*TILEPX

def ym_shift(year,month,delta):
    z=year*12+(month-1)+delta
    return z//12,z%12+1

def circle_pixels(lat,lon,radius_m):
    lat_rad=radius_m/110574.0
    coslat=max(0.15,math.cos(math.radians(lat)))
    lon_rad=radius_m/(111320.0*coslat)
    c0=math.ceil((lon-lon_rad-ORIGIN_LON)/RES-0.5)
    c1=math.floor((lon+lon_rad-ORIGIN_LON)/RES-0.5)
    r0=math.ceil((ORIGIN_LAT-(lat+lat_rad))/RES-0.5)
    r1=math.floor((ORIGIN_LAT-(lat-lat_rad))/RES-0.5)
    rows=np.arange(r0,r1+1,dtype=np.int64)
    cols=np.arange(c0,c1+1,dtype=np.int64)
    rr,cc=np.meshgrid(rows,cols,indexing="ij")
    plats=ORIGIN_LAT-(rr+0.5)*RES
    plons=ORIGIN_LON+(cc+0.5)*RES
    p1=math.radians(lat); p2=np.radians(plats)
    dphi=p2-p1; dlambda=np.radians(plons-lon)
    a=np.sin(dphi/2.0)**2+math.cos(p1)*np.cos(p2)*np.sin(dlambda/2.0)**2
    dist=2*6371008.8*np.arcsin(np.minimum(1.0,np.sqrt(a)))
    mask=dist<=radius_m
    return rr[mask],cc[mask]

class RemoteRasterSet:
    def __init__(self,year,month):
        self.year=year; self.month=month
        self.datasets={}; self.blocks={}
    def close(self):
        for ds in self.datasets.values():
            try: ds.close()
            except Exception: pass
    def _ds(self,xoff,yoff):
        k=(xoff,yoff)
        if k not in self.datasets:
            url=history_url(self.year,self.month,xoff,yoff)
            last=None
            for i in range(4):
                try:
                    self.datasets[k]=rasterio.open(url); break
                except Exception as e:
                    last=e; time.sleep(2*(i+1))
            else:
                raise RuntimeError(f"raster open failed {url}: {last}")
        return self.datasets[k]
    def block(self,xoff,yoff,brow,bcol):
        k=(xoff,yoff,brow,bcol)
        if k in self.blocks:
            return self.blocks[k]
        ds=self._ds(xoff,yoff)
        row0=brow*BLOCK; col0=bcol*BLOCK
        h=min(BLOCK,ds.height-row0); w=min(BLOCK,ds.width-col0)
        a=ds.read(1,window=Window(col0,row0,w,h))
        self.blocks[k]=a
        return a
    def values(self,grows,gcols):
        vals=np.empty(len(grows),dtype=np.uint8)
        groups=defaultdict(list)
        for i,(gr,gc) in enumerate(zip(grows,gcols)):
            rowoff,coloff=tile_offsets_from_global(int(gr),int(gc))
            lr=int(gr-rowoff); lc=int(gc-coloff)
            groups[(rowoff,coloff,lr//BLOCK,lc//BLOCK)].append((i,lr,lc))
        for (rowoff,coloff,br,bc),items in groups.items():
            a=self.block(rowoff,coloff,br,bc)
            r0=br*BLOCK; c0=bc*BLOCK
            for i,lr,lc in items:
                vals[i]=a[lr-r0,lc-c0]
        return vals

# Coordinate authority
cb=fetch(COORD_URL)
if hashlib.sha256(cb).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate SHA drift")
coords={}
byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(cb.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip(); rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid: continue
    lat=float(r["lat"]); lon=float(r["lon"])
    coords[sid]=(rid,lat,lon)
    byroute[rid].append((sid,lat,lon))
safe=strict_routes(byroute)

# Frozen principal population and focal physical-site identities
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str))
site_map=mem.site_map(raw,eligible)
runmeta={
    str(r.RunID):{
        "year":int(r.SurveyYear),
        "month":(date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)).month,
        "State":str(r.State),
        "RouteNumber":str(r.RouteNumber),
        "route_cluster":str(r.route_cluster),
        "RunNumber":str(r.RunNumber)
    }
    for r in runs.itertuples(index=False)
}

pair_specs=[]
run_specs={}
requests=defaultdict(set)

for p,dct in zip(psub.itertuples(index=False),dsub):
    rid=str(p.RouteNumber)
    if rid not in safe:
        continue
    ids=mem.focal_siteids(p,dct,site_map)
    if ids is None or len(ids)!=10 or any(sid not in coords for sid in ids):
        continue
    wr=str(p.wet_RunID); dr=str(p.dry_RunID)
    if wr not in runmeta or dr not in runmeta:
        continue
    pair_specs.append({
        "route_cluster":str(p.route_cluster),"State":str(p.State),"RouteNumber":rid,
        "wet_RunID":wr,"dry_RunID":dr,"siteids":list(ids)
    })
    for runid in (wr,dr):
        rm=runmeta[runid]
        spec={"RunID":runid,**rm,"siteids":list(ids)}
        if runid in run_specs and run_specs[runid]["siteids"]!=spec["siteids"]:
            raise RuntimeError(f"focal site identity drift for RunID {runid}")
        run_specs[runid]=spec
        for sid in ids:
            for k in range(12):
                yy,mm=ym_shift(rm["year"],rm["month"],-k)
                requests[(yy,mm)].add(sid)

# Extract only requested site-months
water={}
validfrac={}
with rasterio.Env(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    GDAL_HTTP_MULTIRANGE="YES",
    VSI_CACHE="TRUE",
    VSI_CACHE_SIZE=67108864,
    GDAL_CACHEMAX=256,
):
    keys=sorted(requests)
    for n,(yy,mm) in enumerate(keys,1):
        rs=RemoteRasterSet(yy,mm)
        try:
            for sid in sorted(requests[(yy,mm)]):
                _,lat,lon=coords[sid]
                rr,cc=circle_pixels(lat,lon,RADIUS)
                vals=rs.values(rr,cc)
                valid=(vals==1)|(vals==2)
                vf=float(valid.mean()) if len(vals) else 0.0
                w=float((vals[valid]==2).mean()) if valid.any() and vf>=VALID_FRAC_MIN else None
                water[(sid,yy,mm)]=w
                validfrac[(sid,yy,mm)]=vf
        finally:
            rs.close()
        if n==1 or n%25==0 or n==len(keys):
            print(json.dumps({"stage":"variability_extract","file_group":n,"file_groups_total":len(keys),"year":yy,"month":mm}),flush=True)

# Collapse monthly histories to focal RunID x SiteID metrics
rows=[]
for runid,spec in sorted(run_specs.items()):
    yy=int(spec["year"]); mm=int(spec["month"])
    for sid in spec["siteids"]:
        seq=[]
        vfs=[]
        for k in range(12):
            yk,mk=ym_shift(yy,mm,-k)
            seq.append(water.get((sid,yk,mk)))
            vfs.append(validfrac.get((sid,yk,mk)))
        cur=seq[0]
        recent3=float(np.mean(seq[:3])) if all(v is not None for v in seq[:3]) else None
        arr=np.asarray([v for v in seq if v is not None],float)
        nvalid=int(len(arr))
        sd=float(np.std(arr,ddof=1)) if nvalid>=MIN_VALID_12M else None
        rng=float(arr.max()-arr.min()) if nvalid>=MIN_VALID_12M else None
        rows.append({
            "RunID":runid,"SiteID":sid,"State":spec["State"],"RouteNumber":spec["RouteNumber"],
            "route_cluster":spec["route_cluster"],"RunNumber":spec["RunNumber"],
            "year":yy,"month":mm,
            "current_water_fraction_r250":cur,
            "recent_wetness_3m_r250":recent3,
            "hydro_sd_12m_r250":sd,
            "hydro_range_12m_r250":rng,
            "valid_months_12m":nvalid,
            "current_valid_frac_r250":vfs[0]
        })

df=pd.DataFrame(rows)
OUTCSV.parent.mkdir(exist_ok=True)
df.to_csv(OUTCSV,index=False,float_format="%.8g")
lookup={(str(r.RunID),str(r.SiteID)):r for r in df.itertuples(index=False)}

pair_complete=[]
fail=Counter()
for p in pair_specs:
    ok=True
    for runid in (p["wet_RunID"],p["dry_RunID"]):
        for sid in p["siteids"]:
            row=lookup.get((runid,sid))
            if row is None:
                fail["missing_run_site_row"]+=1; ok=False; break
            if pd.isna(row.current_water_fraction_r250):
                fail["current_missing"]+=1; ok=False; break
            if pd.isna(row.recent_wetness_3m_r250):
                fail["recent3_missing"]+=1; ok=False; break
            if pd.isna(row.hydro_sd_12m_r250):
                fail["sd12_missing"]+=1; ok=False; break
        if not ok: break
    if ok:
        pair_complete.append(p)

csv_sha=hashlib.sha256(OUTCSV.read_bytes()).hexdigest()
out={
  "analysis":"naamp_jrc_v1_hydrology_variability_coverage_v0_1",
  "contract":"revision/NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_EXTENSION_V0_3.md",
  "model_spec":"revision/NAAMP_DYNAMIC_HYDROLOGY_MODEL_SPEC_V0_1.md",
  "source":{"jrc":"GSW v1.0 MonthlyHistory","coordinate_sha256":COORD_SHA},
  "rules":{"radius_m":RADIUS,"valid_pixel_fraction_min":VALID_FRAC_MIN,"recent_months":3,"variability_months":12,"min_valid_variability_months":MIN_VALID_12M},
  "requests":{"unique_site_months":len(water),"file_groups":len(requests),"focal_runids":len(run_specs),"focal_run_site_rows":len(df)},
  "coverage":{
    "strict_geometry_pair_specs":len(pair_specs),
    "m3_complete_pairs":len(pair_complete),
    "m3_complete_routes":len({p["route_cluster"] for p in pair_complete}),
    "m3_complete_states":len({p["State"] for p in pair_complete}),
    "failures":dict(fail),
    "pair_gate":1500,"route_gate":300,"state_gate":15,
    "gate_pass":bool(len(pair_complete)>=1500 and len({p["route_cluster"] for p in pair_complete})>=300 and len({p["State"] for p in pair_complete})>=15)
  },
  "missingness":{
    "current_missing_rows":int(df["current_water_fraction_r250"].isna().sum()),
    "recent3_missing_rows":int(df["recent_wetness_3m_r250"].isna().sum()),
    "sd12_missing_rows":int(df["hydro_sd_12m_r250"].isna().sum())
  },
  "exposure_csv":"remotesensing/NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_V0_1.csv",
  "exposure_csv_sha256":csv_sha,
  "frog_endpoint_calculated":False,
  "mechanism_result_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
