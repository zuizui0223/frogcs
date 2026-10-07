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
INDIR=Path(os.environ.get("DSWEMOD_YEAR_DIR",str(ROOT/"remotesensing"/"dswemod_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_DSWEMOD_RUN_SITE_METRICS_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_DSWEMOD_COVERAGE_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-aggregate/0.2"})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088;a1,a2=math.radians(lat1),math.radians(lat2);dlat=math.radians(lat2-lat1);dlon=math.radians(lon2-lon1)
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
        mlat=float(np.median([x[1] for x in u]));mlon=float(np.median([x[2] for x in u]))
        d=np.asarray([hav(x[1],x[2],mlat,mlon) for x in u],float)
        if len(d) and float(d.max())>15:continue
        med=float(np.median(d)) if len(d) else 0.;mad=float(np.median(np.abs(d-med))) if len(d) else 0.
        if mad>0 and np.any(d>med+8*mad):continue
        good.add(rid)
    return good

def ym_shift(y,m,delta):
    z=y*12+(m-1)+delta
    return z//12,z%12+1

files=sorted(INDIR.glob("NAAMP_DSWEMOD_MONTHLY_20*.csv"))
years=sorted(int(p.stem.rsplit("_",1)[1]) for p in files)
if years!=list(range(2003,2016)):
    raise RuntimeError(f"expected years 2003-2015, got {years}")
monthly=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
if monthly.duplicated(["SiteID","year","month"]).any():
    raise RuntimeError("duplicate SiteID/year/month DSWEmod keys")

lookups={}
for radius in (500,250):
    lookups[radius]={
      (str(r.SiteID),int(r.year),int(r.month)):float(getattr(r,f"dswemod123_r{radius}"))
      for r in monthly.itertuples(index=False)
      if pd.notna(getattr(r,f"dswemod123_r{radius}"))
    }

# strict route authority
b=fetch(COORD_URL)
if hashlib.sha256(b).hexdigest()!=COORD_SHA:raise RuntimeError("coordinate hash drift")
byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    rid=(r.get("RouteNumber") or "").strip();sid=(r.get("SiteID") or "").strip()
    if rid and sid:byroute[rid].append((sid,float(r["lat"]),float(r["lon"])))
safe=strict_routes(byroute)

raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str));site=mem.site_map(raw,eligible)
runrow={str(r.RunID):r for r in runs.itertuples(index=False)}

# Fixed product-period focal pair universe and unique RunID x SiteID rows.
pair_specs=[]
run_specs={}
for p,dct in zip(psub.itertuples(index=False),dsub):
    if int(p.year_earlier)<2003 or int(p.year_later)>2015:
        continue
    if str(p.RouteNumber) not in safe:
        continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:
        continue
    pair_specs.append({"route_cluster":str(p.route_cluster),"State":str(p.State),"RouteNumber":str(p.RouteNumber),
                       "wet_RunID":str(p.wet_RunID),"dry_RunID":str(p.dry_RunID),"siteids":list(ids)})
    for runid in (str(p.wet_RunID),str(p.dry_RunID)):
        rr=runrow[runid]
        y=int(rr.SurveyYear);m=(date(y,1,1)+timedelta(days=int(rr.doy)-1)).month
        spec={"RunID":runid,"State":str(rr.State),"RouteNumber":str(rr.RouteNumber),"route_cluster":str(rr.route_cluster),
              "RunNumber":str(rr.RunNumber),"year":y,"month":m,"siteids":list(ids)}
        if runid in run_specs and run_specs[runid]["siteids"]!=spec["siteids"]:
            raise RuntimeError(f"RunID site identity drift {runid}")
        run_specs[runid]=spec

rows=[]
for runid,spec in sorted(run_specs.items()):
    y=int(spec["year"]);m=int(spec["month"])
    for sid in spec["siteids"]:
        rec={"RunID":runid,"SiteID":sid,"State":spec["State"],"RouteNumber":spec["RouteNumber"],
             "route_cluster":spec["route_cluster"],"RunNumber":spec["RunNumber"],"year":y,"month":m}
        for radius in (500,250):
            lk=lookups[radius]
            seq=[lk.get((sid,*ym_shift(y,m,-k))) for k in range(12)]
            cur=seq[0]
            recent=float(np.mean(seq[:3])) if all(v is not None for v in seq[:3]) else None
            arr=np.asarray([v for v in seq if v is not None],float)
            nvalid=int(len(arr))
            sd=float(np.std(arr,ddof=1)) if nvalid>=9 else None
            rng=float(arr.max()-arr.min()) if nvalid>=9 else None
            rec[f"current_D_r{radius}"]=cur
            rec[f"recent_D_3m_r{radius}"]=recent
            rec[f"DSWE_sd_12m_r{radius}"]=sd
            rec[f"DSWE_range_12m_r{radius}"]=rng
            rec[f"valid_months_12m_r{radius}"]=nvalid
        rows.append(rec)

df=pd.DataFrame(rows)
OUTCSV.parent.mkdir(exist_ok=True)
df.to_csv(OUTCSV,index=False,float_format="%.8g")
lookup_run={(str(r.RunID),str(r.SiteID)):r for r in df.itertuples(index=False)}

def pair_coverage(radius,full):
    complete=[];fail=Counter()
    for p in pair_specs:
        ok=True
        for runid in (p["wet_RunID"],p["dry_RunID"]):
            for sid in p["siteids"]:
                r=lookup_run.get((runid,sid))
                if r is None:
                    fail["missing_run_site"]+=1;ok=False;break
                if pd.isna(getattr(r,f"current_D_r{radius}")):
                    fail["current_missing"]+=1;ok=False;break
                if full and (
                    pd.isna(getattr(r,f"recent_D_3m_r{radius}")) or
                    pd.isna(getattr(r,f"DSWE_sd_12m_r{radius}"))
                ):
                    fail["M3_missing"]+=1;ok=False;break
            if not ok:break
        if ok:complete.append(p)
    return {
      "pairs":len(complete),"routes":len({x["route_cluster"] for x in complete}),
      "states":len({x["State"] for x in complete}),"failures":dict(fail),
      "gate_pass":bool(len(complete)>=1500 and len({x["route_cluster"] for x in complete})>=300 and len({x["State"] for x in complete})>=15)
    }

coverage={
 "primary_r500_M1":pair_coverage(500,False),
 "primary_r500_M3":pair_coverage(500,True),
 "sensitivity_r250_M1":pair_coverage(250,False)
}
out={
 "analysis":"naamp_dswemod_coverage_v0_2",
 "contract":"revision/NAAMP_MODIS_DSWEMOD_MECHANISM_EXTENSION_V0_2.md",
 "source":{"years":years,"product":"USGS monthly MODIS DSWEmod","resolution_m":250},
 "monthly_rows":int(len(monthly)),"monthly_siteids":int(monthly.SiteID.nunique()),
 "run_site_rows":int(len(df)),"runids":int(df.RunID.nunique()),
 "coverage":coverage,
 "run_site_metrics_csv":"remotesensing/NAAMP_DSWEMOD_RUN_SITE_METRICS_V0_1.csv",
 "run_site_metrics_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False,"mechanism_result_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
