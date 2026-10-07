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
COORD_SHA="f71a87df9fc252d283f223a1ada41f2771136acf69b25726ca4895ef90f7f0d"
# Correct pinned coordinate hash from the archived audit.
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
RADIUS=500.0
RETRIEVAL_MARGIN_DEG=0.02
PAGE=1000

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def fetch(url,timeout=180):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-preflight/0.2"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()

def geom_from_arc(g):
    if not g or not g.get("rings"): return None
    polys=[]
    for ring in g["rings"]:
        if len(ring)<4: continue
        try:
            p=Polygon(ring)
            if not p.is_valid: p=p.buffer(0)
            if not p.is_empty and p.area>0: polys.append(p)
        except Exception:
            pass
    if not polys:return None
    return unary_union(polys)

def query_route_envelope(lons,lats):
    xmin=min(lons)-RETRIEVAL_MARGIN_DEG; xmax=max(lons)+RETRIEVAL_MARGIN_DEG
    ymin=min(lats)-RETRIEVAL_MARGIN_DEG; ymax=max(lats)+RETRIEVAL_MARGIN_DEG
    feats=[]; offset=0
    while True:
        params={
          "where":"1=1",
          "geometry":f"{xmin},{ymin},{xmax},{ymax}",
          "geometryType":"esriGeometryEnvelope",
          "inSR":"4326",
          "spatialRel":"esriSpatialRelIntersects",
          "outFields":"OBJECTID,ATTRIBUTE,WETLAND_TYPE",
          "returnGeometry":"true",
          "outSR":"3857",
          "orderByFields":"OBJECTID",
          "resultOffset":str(offset),
          "resultRecordCount":str(PAGE),
          "f":"json"
        }
        url=NWI+"?"+urllib.parse.urlencode(params)
        last=None
        for i in range(5):
            try:
                obj=json.loads(fetch(url,120).decode("utf-8"))
                if "error" in obj: raise RuntimeError(json.dumps(obj["error"]))
                break
            except Exception as e:
                last=e; time.sleep(1.5*(i+1))
        else:
            raise RuntimeError(f"NWI route query failed: {last}")
        batch=obj.get("features") or []
        feats.extend(batch)
        if len(batch)<PAGE and not obj.get("exceededTransferLimit",False): break
        offset+=len(batch)
        if not batch: break
    return feats

# Coordinate authority.
b=fetch(COORD_URL)
if hashlib.sha256(b).hexdigest()!=COORD_SHA: raise RuntimeError("coordinate SHA drift")
coords={}; byroute=defaultdict(list)
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip(); rid=(r.get("RouteNumber") or "").strip()
    if not sid or not rid:continue
    lat=float(r["lat"]);lon=float(r["lon"]);coords[sid]=(rid,lat,lon);byroute[rid].append((sid,lat,lon))
safe=hyd.strict_routes()

# Frozen principal universe -> route-specific focal SiteIDs.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str)); site=mem.site_map(raw,eligible)
route_sites=defaultdict(set)
for p,dct in zip(psub.itertuples(index=False),dsub):
    rid=str(p.RouteNumber)
    if rid not in safe:continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):continue
    route_sites[rid].update(ids)

assigned_routes=[
 rid for rid in sorted(route_sites)
 if int(hashlib.sha256(rid.encode()).hexdigest()[:8],16)%SHARD_COUNT==SHARD_INDEX
]
tf=Transformer.from_crs("EPSG:4326","EPSG:3857",always_xy=True)
rows=[]
for n,rid in enumerate(assigned_routes,1):
    sids=sorted(route_sites[rid])
    lats=[coords[s][1] for s in sids]; lons=[coords[s][2] for s in sids]
    try:
        feats=query_route_envelope(lons,lats)
        parsed=[]
        for ft in feats:
            a=ft.get("attributes") or {}
            g=geom_from_arc(ft.get("geometry") or {})
            if g is None:continue
            parsed.append((a,g))
        for sid in sids:
            _,lat,lon=coords[sid];x,y=tf.transform(lon,lat);pt=Point(x,y);circle=pt.buffer(RADIUS)
            choices=[]
            for a,g in parsed:
                dist=float(pt.distance(g))
                if dist>RADIUS:continue
                area=float(g.intersection(circle).area)
                choices.append((dist,-area,str(a.get("ATTRIBUTE") or ""),a))
            rec={"SiteID":sid,"RouteNumber":rid,"lat":lat,"lon":lon,
                 "query_success":True,"route_feature_count":len(feats),
                 "ATTRIBUTE":None,"WETLAND_TYPE":None,"distance_m":None,"area_in_500m_m2":None}
            if not choices:
                rec.update({"ATTRIBUTE":"no_NWI_wetland_500m","WETLAND_TYPE":"no_NWI_wetland_500m","area_in_500m_m2":0.0})
            else:
                choices.sort(key=lambda z:(z[0],z[1],z[2]))
                dist,negarea,attr,a=choices[0]
                rec.update({"ATTRIBUTE":str(a.get("ATTRIBUTE") or ""),"WETLAND_TYPE":str(a.get("WETLAND_TYPE") or ""),
                            "distance_m":dist,"area_in_500m_m2":-negarea})
            rows.append(rec)
    except Exception as e:
        for sid in sids:
            _,lat,lon=coords[sid]
            rows.append({"SiteID":sid,"RouteNumber":rid,"lat":lat,"lon":lon,
                         "query_success":False,"route_feature_count":None,"ATTRIBUTE":None,"WETLAND_TYPE":None,
                         "distance_m":None,"area_in_500m_m2":None,
                         "error":type(e).__name__+": "+str(e)[:240]})
    if n==1 or n%5==0 or n==len(assigned_routes):
        print(json.dumps({"shard":SHARD_INDEX,"route":n,"routes":len(assigned_routes),"RouteNumber":rid}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/f"NWI_SITE_ASSIGNMENTS_SHARD_{SHARD_INDEX:02d}.csv"
jsonout=OUTDIR/f"NWI_SITE_ASSIGNMENTS_SHARD_{SHARD_INDEX:02d}.json"
df=pd.DataFrame(rows);df.to_csv(csvout,index=False)
receipt={
 "analysis":"naamp_nwi_site_assignment_shard_v0_2",
 "contract":"revision/NAAMP_NWI_RAIN_FILTER_MECHANISM_CONTRACT_V0_1.md",
 "shard_index":SHARD_INDEX,"shard_count":SHARD_COUNT,
 "assigned_routes":len(assigned_routes),"assigned_siteids":len(df),
 "query_success":int(df.query_success.fillna(False).sum()) if len(df) else 0,
 "no_wetland_500m":int((df.WETLAND_TYPE=="no_NWI_wetland_500m").sum()) if len(df) else 0,
 "wetland_type_counts":{str(k):int(v) for k,v in df.WETLAND_TYPE.value_counts(dropna=True).to_dict().items()} if len(df) else {},
 "retrieval_margin_deg":RETRIEVAL_MARGIN_DEG,
 "scientific_distance_m":RADIUS,
 "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
print(json.dumps(receipt,indent=2,sort_keys=True))
