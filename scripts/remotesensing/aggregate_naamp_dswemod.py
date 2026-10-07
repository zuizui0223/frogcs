#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, os, urllib.request
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
INDIR=Path(os.environ.get("DSWEMOD_YEAR_DIR",str(ROOT/"remotesensing"/"dswemod_inputs")))
OUTCSV=ROOT/"remotesensing"/"NAAMP_DSWEMOD_EXPOSURES_V0_1.csv"
OUTJSON=ROOT/"remotesensing"/"NAAMP_DSWEMOD_COVERAGE_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswemod-aggregate/0.1"})
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

files=sorted(INDIR.glob("NAAMP_DSWEMOD_20*.csv"))
years=sorted(int(p.stem.rsplit("_",1)[1]) for p in files)
if years!=list(range(2003,2016)):
    raise RuntimeError(f"expected years 2003-2015, got {years}")
df=pd.concat([pd.read_csv(p) for p in files],ignore_index=True)
if df.duplicated(["RunID","SiteID"]).any():
    raise RuntimeError("duplicate RunID/SiteID exposure keys")
OUTCSV.parent.mkdir(exist_ok=True)
df.to_csv(OUTCSV,index=False,float_format="%.8g")
lookup={(str(r.RunID),str(r.SiteID)):r for r in df.itertuples(index=False)}

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
counts={}
for radius in (500,250):
    complete=[];fail=Counter()
    for p,dct in zip(psub.itertuples(index=False),dsub):
        if int(p.year_earlier)<2003 or int(p.year_later)>2015:
            fail["outside_product_period"]+=1;continue
        if str(p.RouteNumber) not in safe:
            fail["strict_geometry"]+=1;continue
        ids=mem.focal_siteids(p,dct,site)
        if ids is None or len(ids)!=10:
            fail["siteid_identity"]+=1;continue
        ok=True
        for runid in (str(p.wet_RunID),str(p.dry_RunID)):
            for sid in ids:
                r=lookup.get((runid,sid))
                if r is None:
                    fail["missing_run_site"]+=1;ok=False;break
                v=getattr(r,f"dswemod123_r{radius}")
                if pd.isna(v):
                    fail["invalid_dswemod"]+=1;ok=False;break
            if not ok:break
        if ok:complete.append({"route_cluster":str(p.route_cluster),"State":str(p.State)})
    counts[str(radius)]={
      "complete_pairs":len(complete),"routes":len({x["route_cluster"] for x in complete}),
      "states":len({x["State"] for x in complete}),"failures":dict(fail),
      "gate_pass":bool(len(complete)>=1500 and len({x["route_cluster"] for x in complete})>=300 and len({x["State"] for x in complete})>=15)
    }

out={
 "analysis":"naamp_dswemod_coverage_v0_1",
 "contract":"revision/NAAMP_MODIS_DSWEMOD_MECHANISM_CONTRACT_V0_1.md",
 "source":{"years":years,"product":"USGS DSWEmod monthly MODIS DSWE","resolution_m":250},
 "rows":int(len(df)),"runids":int(df.RunID.nunique()),"siteids":int(df.SiteID.nunique()),
 "coverage":{"primary_r500":counts["500"],"sensitivity_r250":counts["250"]},
 "exposure_csv":"remotesensing/NAAMP_DSWEMOD_EXPOSURES_V0_1.csv",
 "exposure_csv_sha256":hashlib.sha256(OUTCSV.read_bytes()).hexdigest(),
 "frog_endpoint_calculated":False,"mechanism_result_calculated":False
}
OUTJSON.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
