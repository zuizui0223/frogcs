#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUT=ROOT/"remotesensing"/"NAAMP_HYDROLOGY_VARIABILITY_REQUEST_MANIFEST_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-hydro-variability-manifest/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    h=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1.0,math.sqrt(h)))

def eligible_routes(byroute):
    good=set()
    for route,pts in byroute.items():
        bysid=defaultdict(set)
        for sid,lat,lon in pts:
            bysid[sid].add((lat,lon))
        unique=[]
        if any(len(v)>1 for v in bysid.values()):
            continue
        for sid,v in bysid.items():
            lat,lon=next(iter(v))
            unique.append((sid,lat,lon))
        inside=[x for x in unique if 24<=x[1]<=50 and -125<=x[2]<=-66]
        if len(inside)<8 or len(inside)!=len(unique):
            continue
        ds=[]
        for i in range(len(inside)):
            for j in range(i+1,len(inside)):
                ds.append(hav(inside[i][1],inside[i][2],inside[j][1],inside[j][2]))
        if ds and max(ds)>30:
            continue
        mlat=float(np.median([x[1] for x in inside]))
        mlon=float(np.median([x[2] for x in inside]))
        dmed=np.asarray([hav(x[1],x[2],mlat,mlon) for x in inside],float)
        if len(dmed) and float(dmed.max())>15:
            continue
        med=float(np.median(dmed)) if len(dmed) else 0.0
        mad=float(np.median(np.abs(dmed-med))) if len(dmed) else 0.0
        if mad>0 and np.any(dmed>med+8*mad):
            continue
        good.add(route)
    return good

def tile_key(lat,lon):
    xi=int(math.floor((lon+180.0)/10.0))
    yi=int(math.floor((80.0-lat)/10.0))
    xi=max(0,min(35,xi)); yi=max(0,min(12,yi))
    return xi*40000, yi*40000

def ym_shift(year,month,delta):
    z=year*12+(month-1)+delta
    return z//12,z%12+1

rawb=fetch(COORD_URL)
if hashlib.sha256(rawb).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate SHA drift")
coords={}
byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(rawb.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip()
    rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid:
        continue
    lat=float(r["lat"]); lon=float(r["lon"])
    coords[sid]=(rid,lat,lon)
    byroute[rid].append((sid,lat,lon))
safe=eligible_routes(byroute)

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str))
site=mem.site_map(raw,eligible)
runmeta={
    str(r.RunID):{
        "year":int(r.SurveyYear),
        "month":(date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)).month
    }
    for r in runs.itertuples(index=False)
}

pairs=0
routes=set()
states=set()
siteids=set()
site_months=set()
tile_month_files=set()
run_windows=set()

for p,dct in zip(psub.itertuples(index=False),dsub):
    rid=str(p.RouteNumber)
    if rid not in safe:
        continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):
        continue
    wet=runmeta.get(str(p.wet_RunID)); dry=runmeta.get(str(p.dry_RunID))
    if wet is None or dry is None:
        continue
    pairs+=1
    routes.add(str(p.route_cluster))
    states.add(str(p.State))
    for rm in (wet,dry):
        window=tuple(ym_shift(rm["year"],rm["month"],-k) for k in range(12))
        run_windows.add(window)
        for sid in ids:
            siteids.add(sid)
            _,lat,lon=coords[sid]
            x,y=tile_key(lat,lon)
            for yy,mm in window:
                site_months.add((sid,yy,mm))
                tile_month_files.add((yy,mm,x,y))

out={
  "analysis":"naamp_hydrology_variability_request_manifest_v0_1",
  "contract":"revision/NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_EXTENSION_V0_3.md",
  "strict_coordinate_routes":len(safe),
  "principal_pairs_after_strict_geometry_identity":pairs,
  "routes":len(routes),
  "states":len(states),
  "unique_siteids":len(siteids),
  "unique_site_month_requests_12m_windows":len(site_months),
  "unique_tile_month_files":len(tile_month_files),
  "year_range":[min(x[1] for x in site_months),max(x[1] for x in site_months)] if site_months else None,
  "month_range":sorted({x[2] for x in site_months}),
  "unique_12m_run_windows":len(run_windows),
  "frog_endpoint_calculated":False,
  "remote_water_values_read":False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
