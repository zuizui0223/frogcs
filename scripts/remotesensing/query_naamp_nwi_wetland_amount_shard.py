#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os, time, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(os.environ["NWI_COORD_ASSIGNMENTS"])
OUTDIR=ROOT/"remotesensing"/"nwi_amount_shards"
IDX=int(os.environ.get("NWI_AMOUNT_SHARD_INDEX","0"))
COUNT=int(os.environ.get("NWI_AMOUNT_SHARD_COUNT","8"))

NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
RADIUS=500.0
MARGIN=.02
PAGE=1000

def fetch(url,timeout=120):
    last=None
    for i in range(8):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-wetland-amount/0.1"})
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(min(45.0,2.0*(i+1)))
    raise last

def signed_area(ring):
    s=0.0
    for i in range(len(ring)-1):
        x1,y1=ring[i];x2,y2=ring[i+1]
        s+=x1*y2-x2*y1
    return .5*s

def geom_from_arc(g):
    rings=[]
    for ring in (g or {}).get("rings") or []:
        if len(ring)<4:continue
        rr=[(float(x),float(y)) for x,y in ring]
        if rr[0]!=rr[-1]:rr.append(rr[0])
        try:
            p=Polygon(rr)
            if not p.is_valid:p=p.buffer(0)
            if not p.is_empty and p.area>0:rings.append((signed_area(rr),rr,p))
        except Exception:pass
    if not rings:return None
    outers=[x for x in rings if x[0]<0]
    holes=[x for x in rings if x[0]>=0]
    if not outers:
        outers=rings;holes=[]
    polys=[]
    for _,orr,op in outers:
        hs=[hrr for _,hrr,hp in holes if op.contains(hp.representative_point())]
        try:
            q=Polygon(orr,holes=hs)
            if not q.is_valid:q=q.buffer(0)
            if not q.is_empty:polys.append(q)
        except Exception:pass
    return unary_union(polys) if polys else None

def parse_features(feats):
    out=[]
    for ft in feats:
        a=ft.get("attributes") or {}
        g=geom_from_arc(ft.get("geometry") or {})
        if g is not None:
            out.append((str(a.get("OBJECTID") or ""),g))
    return out

def query_route(lons,lats):
    xmin=min(lons)-MARGIN;xmax=max(lons)+MARGIN
    ymin=min(lats)-MARGIN;ymax=max(lats)+MARGIN
    feats=[];off=0
    while True:
        params={
          "where":"1=1","geometry":f"{xmin},{ymin},{xmax},{ymax}",
          "geometryType":"esriGeometryEnvelope","inSR":"4326",
          "spatialRel":"esriSpatialRelIntersects",
          "outFields":"OBJECTID","returnGeometry":"true","outSR":"5070",
          "orderByFields":"OBJECTID","resultOffset":str(off),
          "resultRecordCount":str(PAGE),"f":"json"
        }
        obj=json.loads(fetch(NWI+"?"+urllib.parse.urlencode(params)).decode("utf-8"))
        if "error" in obj:raise RuntimeError(json.dumps(obj["error"]))
        batch=obj.get("features") or [];feats.extend(batch)
        if len(batch)<PAGE and not obj.get("exceededTransferLimit",False):break
        if not batch:break
        off+=len(batch)
    return feats

def query_point(lon,lat):
    params={
      "where":"1=1","geometry":f"{lon},{lat}",
      "geometryType":"esriGeometryPoint","inSR":"4326",
      "spatialRel":"esriSpatialRelIntersects",
      "distance":"700","units":"esriSRUnit_Meter",
      "outFields":"OBJECTID","returnGeometry":"true","outSR":"5070",
      "resultRecordCount":str(PAGE),"f":"json"
    }
    obj=json.loads(fetch(NWI+"?"+urllib.parse.urlencode(params)).decode("utf-8"))
    if "error" in obj:raise RuntimeError(json.dumps(obj["error"]))
    if obj.get("exceededTransferLimit",False):
        raise RuntimeError("point-distance candidate set exceeded transfer limit")
    return obj.get("features") or []

base=pd.read_csv(BASE,dtype={"SiteID":str,"RouteNumber":str})
need={"SiteID","RouteNumber","lat","lon"}
if not need.issubset(base.columns):
    raise RuntimeError(f"assignment artifact lacks columns {sorted(need-set(base.columns))}")
base=base.drop_duplicates(["SiteID"]).copy()
routes=sorted(base.RouteNumber.dropna().astype(str).unique())
routes=[r for r in routes if int(hashlib.sha256(r.encode()).hexdigest()[:8],16)%COUNT==IDX]

tf=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True)
rows=[]
for n,rid in enumerate(routes,1):
    d=base.loc[base.RouteNumber.astype(str)==rid,["SiteID","lat","lon"]].drop_duplicates("SiteID").copy()
    route_parsed=None
    try:
        route_parsed=parse_features(query_route(d.lon.astype(float).tolist(),d.lat.astype(float).tolist()))
    except Exception:
        route_parsed=None

    for z in d.itertuples(index=False):
        sid=str(z.SiteID);lat=float(z.lat);lon=float(z.lon)
        rec={"SiteID":sid,"RouteNumber":rid,"lat":lat,"lon":lon,
             "query_success":False,"retrieval_mode":None,
             "wetland_area_fraction_500m":None,
             "wetland_patch_count_500m":None,
             "nearest_wetland_distance_m":None}
        try:
            parsed=route_parsed
            mode="route_envelope"
            if parsed is None:
                parsed=parse_features(query_point(lon,lat))
                mode="point_distance_fallback"
            x,y=tf.transform(lon,lat);pt=Point(x,y);circle=pt.buffer(RADIUS)
            clips=[];oids=set();nearest=None
            for oid,g in parsed:
                dist=float(pt.distance(g))
                if nearest is None or dist<nearest:nearest=dist
                if dist>RADIUS:continue
                q=g.intersection(circle)
                if q.is_empty or q.area<=0:continue
                clips.append(q);oids.add(oid)
            if clips:
                u=unary_union(clips)
                frac=float(u.area/circle.area)
                frac=max(0.0,min(1.0,frac))
                patch=int(len(oids))
                nd=float(nearest) if nearest is not None and nearest<=RADIUS else None
            else:
                frac=0.0;patch=0;nd=None
            rec.update({
              "query_success":True,"retrieval_mode":mode,
              "wetland_area_fraction_500m":frac,
              "wetland_patch_count_500m":patch,
              "nearest_wetland_distance_m":nd
            })
        except Exception as e:
            rec["error"]=type(e).__name__+": "+str(e)[:240]
        rows.append(rec)
    if n==1 or n%10==0 or n==len(routes):
        print(json.dumps({"shard":IDX,"route":n,"routes":len(routes),"RouteNumber":rid}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
csvout=OUTDIR/f"NWI_WETLAND_AMOUNT_SHARD_{IDX:02d}.csv"
jsonout=OUTDIR/f"NWI_WETLAND_AMOUNT_SHARD_{IDX:02d}.json"
df=pd.DataFrame(rows);df.to_csv(csvout,index=False)
receipt={
 "analysis":"naamp_nwi_wetland_amount_shard_v0_1",
 "contract":"revision/NAAMP_NWI_WETLAND_AMOUNT_RAIN_MECHANISM_CONTRACT_V0_1.md",
 "shard_index":IDX,"shard_count":COUNT,
 "routes":len(routes),"rows":len(df),
 "query_success":int(df.query_success.fillna(False).sum()) if len(df) else 0,
 "zero_wetland":int((df.wetland_area_fraction_500m==0).sum()) if len(df) else 0,
 "frog_endpoint_calculated":False
}
jsonout.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
