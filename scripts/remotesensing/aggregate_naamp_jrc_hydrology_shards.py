#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, os, urllib.request
from collections import defaultdict, Counter
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
INDIR=Path(os.environ.get("JRC_SHARD_DIR",str(ROOT/"remotesensing"/"shard_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_V0_2.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_JRC_V1_HYDROLOGY_VARIABILITY_COVERAGE_V0_2.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-jrc-aggregate/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088;a1,a2=math.radians(lat1),math.radians(lat2);dlat=math.radians(lat2-lat1);dlon=math.radians(lon2-lon1)
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
        mlat=float(np.median([x[1] for x in u]));mlon=float(np.median([x[2] for x in u]))
        d=np.asarray([hav(x[1],x[2],mlat,mlon) for x in u],float)
        if len(d) and float(d.max())>15:continue
        med=float(np.median(d)) if len(d) else 0.;mad=float(np.median(np.abs(d-med))) if len(d) else 0.
        if mad>0 and np.any(d>med+8*mad):continue
        good.add(route)
    return good

def ym_shift(y,m,delta):
    z=y*12+(m-1)+delta
    return z//12,z%12+1

files=sorted(INDIR.glob("jrc_monthly_shard_*.csv"))
if len(files)!=8:raise RuntimeError(f"expected 8 shard csvs, found {len(files)} in {INDIR}")
monthly=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
if monthly.duplicated(["SiteID","year","month"]).any():
    dup=monthly[monthly.duplicated(["SiteID","year","month"],keep=False)].head()
    raise RuntimeError(f"duplicate monthly keys: {dup.to_dict('records')}")
water={(str(r.SiteID),int(r.year),int(r.month)):float(r.water_fraction_r250) for r in monthly.itertuples(index=False) if pd.notna(r.water_fraction_r250)}

# Coordinate authority
b=fetch(COORD_URL)
if hashlib.sha256(b).hexdigest()!=COORD_SHA:raise RuntimeError("coordinate hash drift")
coords={};byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip();rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid:continue
    lat=float(r["lat"]);lon=float(r["lon"]);coords[sid]=(rid,lat,lon);byroute[rid].append((sid,lat,lon))
safe=strict_routes(byroute)

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible)
runmeta={str(r.RunID):{
 "year":int(r.SurveyYear),"month":(date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)).month,
 "State":str(r.State),"RouteNumber":str(r.RouteNumber),"route_cluster":str(r.route_cluster),"RunNumber":str(r.RunNumber)
} for r in runs.itertuples(index=False)}

pair_specs=[];run_specs={}
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe:continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):continue
    wr,dr=str(p.wet_RunID),str(p.dry_RunID)
    if wr not in runmeta or dr not in runmeta:continue
    pair_specs.append({"route_cluster":str(p.route_cluster),"State":str(p.State),"RouteNumber":str(p.RouteNumber),"wet_RunID":wr,"dry_RunID":dr,"siteids":list(ids)})
    for rid in (wr,dr):
        spec={"RunID":rid,**runmeta[rid],"siteids":list(ids)}
        if rid in run_specs and run_specs[rid]["siteids"]!=spec["siteids"]:raise RuntimeError(f"RunID site identity drift {rid}")
        run_specs[rid]=spec

rows=[]
for rid,spec in sorted(run_specs.items()):
    y,m=int(spec["year"]),int(spec["month"])
    for sid in spec["siteids"]:
        seq=[water.get((sid,*ym_shift(y,m,-k))) for k in range(12)]
        cur=seq[0]
        recent=float(np.mean(seq[:3])) if all(v is not None for v in seq[:3]) else None
        arr=np.asarray([v for v in seq if v is not None],float)
        nvalid=len(arr)
        sd=float(np.std(arr,ddof=1)) if nvalid>=9 else None
        rng=float(arr.max()-arr.min()) if nvalid>=9 else None
        rows.append({"RunID":rid,"SiteID":sid,"State":spec["State"],"RouteNumber":spec["RouteNumber"],"route_cluster":spec["route_cluster"],"RunNumber":spec["RunNumber"],"year":y,"month":m,
                     "current_water_fraction_r250":cur,"recent_wetness_3m_r250":recent,"hydro_sd_12m_r250":sd,"hydro_range_12m_r250":rng,"valid_months_12m":nvalid})
df=pd.DataFrame(rows);OUTCSV.parent.mkdir(exist_ok=True);df.to_csv(OUTCSV,index=False,float_format="%.8g")
lookup={(str(r.RunID),str(r.SiteID)):r for r in df.itertuples(index=False)}

complete=[];fail=Counter()
for p in pair_specs:
    ok=True
    for rid in (p["wet_RunID"],p["dry_RunID"]):
        for sid in p["siteids"]:
            r=lookup.get((rid,sid))
            if r is None:fail["missing_run_site"]+=1;ok=False;break
            if pd.isna(r.current_water_fraction_r250):fail["current_missing"]+=1;ok=False;break
            if pd.isna(r.recent_wetness_3m_r250):fail["recent3_missing"]+=1;ok=False;break
            if pd.isna(r.hydro_sd_12m_r250):fail["sd12_missing"]+=1;ok=False;break
        if not ok:break
    if ok:complete.append(p)

out={
 "analysis":"naamp_jrc_v1_hydrology_variability_coverage_v0_2",
 "contract":"revision/NAAMP_DYNAMIC_HYDROLOGY_MECHANISM_EXTENSION_V0_4.md",
 "model_spec":"revision/NAAMP_DYNAMIC_HYDROLOGY_MODEL_SPEC_V0_1.md",
 "source":{"jrc":"GSW v1.0 MonthlyHistory","coordinate_sha256":COORD_SHA},
 "shards":{"count":len(files),"monthly_rows":int(len(monthly)),"nonmissing_monthly_water":int(monthly.water_fraction_r250.notna().sum())},
 "coverage":{"strict_geometry_pair_specs":len(pair_specs),"m3_complete_pairs":len(complete),"m3_complete_routes":len({p["route_cluster"] for p in complete}),
             "m3_complete_states":len({p["State"] for p in complete}),"failures":dict(fail),
             "pair_gate":1500,"route_gate":300,"state_gate":15,
             "gate_pass":bool(len(complete)>=1500 and len({p["route_cluster"] for p in complete})>=300 and len({p["State"] for p in complete})>=15)},
 "run_site_rows":int(len(df)),
 "missingness":{"current_missing_rows":int(df.current_water_fraction_r250.isna().sum()),"recent3_missing_rows":int(df.recent_wetness_3m_r250.isna().sum()),"sd12_missing_rows":int(df.hydro_sd_12m_r250.isna().sum())},
 "exposure_csv":str(OUTCSV.relative_to(ROOT)),"exposure_csv_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False,"mechanism_result_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
