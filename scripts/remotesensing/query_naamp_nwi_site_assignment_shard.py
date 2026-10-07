#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, os, time, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
OUTDIR=ROOT/"remotesensing"/"nwi_shards"
SHARD_INDEX=int(os.environ.get("NWI_SHARD_INDEX","0"))
SHARD_COUNT=int(os.environ.get("NWI_SHARD_COUNT","16"))

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
RADIUS=500.0

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def fetch(url,timeout=180):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-preflight/0.1"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def query_nwi(lon,lat):
    params={
      "where":"1=1",
      "geometry":f"{lon},{lat}",
      "geometryType":"esriGeometryPoint",
      "inSR":"4326",
      "spatialRel":"esriSpatialRelIntersects",
      "distance":"500",
      "units":"esriSRUnit_Meter",
      "outFields":"ATTRIBUTE,WETLAND_TYPE",
      "returnGeometry":"true",
      "outSR":"3857",
      "f":"json"
    }
    url=NWI+"?"+urllib.parse.urlencode(params)
    last=None
    for i in range(5):
        try:
            obj=json.loads(fetch(url,120).decode("utf-8"))
            if "error" in obj:
                raise RuntimeError(json.dumps(obj["error"]))
            return obj
        except Exception as e:
            last=e; time.sleep(1.5*(i+1))
    raise RuntimeError(f"NWI query failed: {last}")

def geom_from_arc(g):
    if not g or not g.get("rings"): return None
    polys=[]
    for ring in g["rings"]:
        if len(ring)>=4:
            try:
                p=Polygon(ring)
                if not p.is_empty and p.is_valid and p.area>0:
                    polys.append(p)
                elif not p.is_empty:
                    q=p.buffer(0)
                    if not q.is_empty: polys.append(q)
            except Exception:
                pass
    if not polys: return None
    return unary_union(polys)

# Coordinate authority.
b=fetch(COORD_URL)
if hashlib.sha256(b).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate SHA drift")
coords={}; byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip(); rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid: continue
    lat=float(r["lat"]); lon=float(r["lon"])
    coords[sid]=(rid,lat,lon); byroute[rid].append((sid,lat,lon))

# Existing strict geometry gate.
safe=hyd.strict_routes()

# Frozen principal pair universe -> unique physical SiteIDs.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible)
siteids=set()
pair_siteids=[]
for p,dct in zip(psub.itertuples(index=False),dsub):
    if str(p.RouteNumber) not in safe: continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids): continue
    pair_siteids.append((str(p.route_cluster),str(p.State),list(ids)))
    siteids.update(ids)

assigned=[sid for sid in sorted(siteids) if int(hashlib.sha256(sid.encode()).hexdigest()[:8],16)%SHARD_COUNT==SHARD_INDEX]
tf=Transformer.from_crs("EPSG:4326","EPSG:3857",always_xy=True)
rows=[]
for n,sid in enumerate(assigned,1):
    rid,lat,lon=coords[sid]
    rec={"SiteID":sid,"RouteNumber":rid,"lat":lat,"lon":lon,
         "query_success":False,"n_features":None,"ATTRIBUTE":None,"WETLAND_TYPE":None,
         "distance_m":None,"area_in_500m_m2":None}
    try:
        obj=query_nwi(lon,lat)
        feats=obj.get("features") or []
        rec["query_success"]=True; rec["n_features"]=len(feats)
        if not feats:
            rec["ATTRIBUTE"]="no_NWI_wetland_500m"
            rec["WETLAND_TYPE"]="no_NWI_wetland_500m"
            rec["distance_m"]=None
            rec["area_in_500m_m2"]=0.0
        else:
            x,y=tf.transform(lon,lat); pt=Point(x,y); circle=pt.buffer(RADIUS)
            choices=[]
            for f in feats:
                a=f.get("attributes") or {}
                g=geom_from_arc(f.get("geometry") or {})
                if g is None: continue
                dist=float(pt.distance(g))
                area=float(g.intersection(circle).area)
                choices.append((dist,-area,str(a.get("ATTRIBUTE") or ""),a,g))
            if choices:
                choices.sort(key=lambda z:(z[0],z[1],z[2]))
                dist,negarea,attr,a,g=choices[0]
                rec["ATTRIBUTE"]=str(a.get("ATTRIBUTE") or "")
                rec["WETLAND_TYPE"]=str(a.get("WETLAND_TYPE") or "")
                rec["distance_m"]=dist
                rec["area_in_500m_m2"]=-negarea
            else:
                # Query succeeded but returned unusable geometry: this is missing, not no-wetland.
                rec["query_success"]=False
                rec["geometry_parse_failure"]=True
    except Exception as e:
        rec["error"]=type(e).__name__+": "+str(e)[:240]
    rows.append(rec)
    if n==1 or n%25==0 or n==len(assigned):
        print(json.dumps({"shard":SHARD_INDEX,"site":n,"sites":len(assigned),"SiteID":sid}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/f"NWI_SITE_ASSIGNMENTS_SHARD_{SHARD_INDEX:02d}.csv"
jsonout=OUTDIR/f"NWI_SITE_ASSIGNMENTS_SHARD_{SHARD_INDEX:02d}.json"
df=pd.DataFrame(rows); df.to_csv(csvout,index=False)
receipt={
  "analysis":"naamp_nwi_site_assignment_shard_v0_1",
  "contract":"revision/NAAMP_NWI_RAIN_FILTER_MECHANISM_CONTRACT_V0_1.md",
  "shard_index":SHARD_INDEX,"shard_count":SHARD_COUNT,
  "principal_strict_siteids_total":len(siteids),
  "assigned_siteids":len(assigned),
  "query_success":int(df.query_success.fillna(False).sum()) if len(df) else 0,
  "no_wetland_500m":int((df.WETLAND_TYPE=="no_NWI_wetland_500m").sum()) if len(df) else 0,
  "wetland_type_counts":{str(k):int(v) for k,v in df.WETLAND_TYPE.value_counts(dropna=True).to_dict().items()} if len(df) else {},
  "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps(receipt,indent=2,sort_keys=True))
