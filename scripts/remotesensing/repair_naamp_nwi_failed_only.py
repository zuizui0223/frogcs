#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, os, time, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(os.environ["NWI_BASE_ASSIGNMENTS"])
OUTDIR=ROOT/"remotesensing"/"nwi_repair_shards"
IDX=int(os.environ.get("NWI_REPAIR_SHARD_INDEX","0"))
COUNT=int(os.environ.get("NWI_REPAIR_SHARD_COUNT","8"))

NWI="https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query"
RADIUS=500.0
MARGIN=.01
PAGE=1000

def fetch(url,timeout=20):
    # Retrieval-only fast-fail policy. Scientific geometry and coverage gates are unchanged.
    # Isolated v0.4 runner; retrieval semantics identical to the frozen repair.
    last=None
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nwi-failed-only-repair/0.2"})
            with urllib.request.urlopen(req,timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(1.0*(i+1))
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
    outers=[x for x in rings if x[0]<0]; holes=[x for x in rings if x[0]>=0]
    if not outers:outers=rings;holes=[]
    polys=[]
    for _,orr,op in outers:
        hs=[hrr for _,hrr,hp in holes if op.contains(hp.representative_point())]
        try:
            q=Polygon(orr,holes=hs)
            if not q.is_valid:q=q.buffer(0)
            if not q.is_empty:polys.append(q)
        except Exception:pass
    return unary_union(polys) if polys else None

def query_site(lon,lat):
    params={
      "where":"1=1",
      "geometry":f"{lon},{lat}",
      "geometryType":"esriGeometryPoint",
      "inSR":"4326",
      "spatialRel":"esriSpatialRelIntersects",
      "distance":"700",
      "units":"esriSRUnit_Meter",
      "outFields":"OBJECTID,ATTRIBUTE,WETLAND_TYPE",
      "returnGeometry":"true",
      "outSR":"5070",
      "resultRecordCount":str(PAGE),
      "f":"json"
    }
    obj=json.loads(fetch(NWI+"?"+urllib.parse.urlencode(params),20).decode("utf-8"))
    if "error" in obj:
        raise RuntimeError(json.dumps(obj["error"]))
    if obj.get("exceededTransferLimit",False):
        raise RuntimeError("point-distance candidate set exceeded transfer limit")
    return obj.get("features") or []

def fetch_code_table():
    rows=[];offset=0
    while True:
        params={
          "where":"1=1",
          "outFields":"OBJECTID,ATTRIBUTE,WATER_REGIME,WATER_REGIME_NAME,WATER_REGIME_SUBGROUP,SYSTEM_NAME,CLASS_NAME",
          "returnGeometry":"false","orderByFields":"OBJECTID",
          "resultOffset":str(offset),"resultRecordCount":"500","f":"json"
        }
        obj=json.loads(fetch(NWI_CODES+"?"+urllib.parse.urlencode(params)).decode("utf-8"))
        if "error" in obj:raise RuntimeError(json.dumps(obj["error"]))
        batch=[z.get("attributes") or {} for z in (obj.get("features") or [])]
        rows.extend(batch)
        if len(batch)<500 and not obj.get("exceededTransferLimit",False):break
        if not batch:break
        offset+=len(batch)
    out={}
    for a in rows:
        attr=str(a.get("ATTRIBUTE") or "").strip()
        if attr:
            out[attr]={k:str(a.get(k) or "").strip() for k in [
              "WATER_REGIME","WATER_REGIME_NAME","WATER_REGIME_SUBGROUP","SYSTEM_NAME","CLASS_NAME"
            ]}
    if not out:raise RuntimeError("empty NWI code table")
    return out

df=pd.read_csv(BASE,dtype={"SiteID":str,"RouteNumber":str})
qs=df["query_success"].map(lambda x:str(x).strip().lower() in ("true","1","yes"))
fail=df.loc[~qs].copy()
fail=fail[
  fail["SiteID"].astype(str).map(lambda s:int(hashlib.sha256(s.encode()).hexdigest()[:8],16)%COUNT==IDX)
].copy()

tf=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True)
rows=[]
for n,r in enumerate(fail.itertuples(index=False),1):
    sid=str(r.SiteID);rid=str(r.RouteNumber);lat=float(r.lat);lon=float(r.lon)
    rec={"SiteID":sid,"RouteNumber":rid,"lat":lat,"lon":lon,
         "query_success":False,"code_join_success":False,
         "retrieval_mode":"failed_only_point_distance_700m",
         "ATTRIBUTE":None,"WETLAND_TYPE":None,
         "WATER_REGIME":None,"WATER_REGIME_NAME":None,"WATER_REGIME_SUBGROUP":None,
         "SYSTEM_NAME":None,"CLASS_NAME":None,
         "distance_m":None,"area_in_500m_m2":None}
    try:
        parsed=[]
        for ft in query_site(lon,lat):
            a=ft.get("attributes") or {};g=geom_from_arc(ft.get("geometry") or {})
            if g is not None:parsed.append((a,g))
        x,y=tf.transform(lon,lat);pt=Point(x,y);circle=pt.buffer(RADIUS)
        choices=[]
        for a,g in parsed:
            dist=float(pt.distance(g))
            if dist<=RADIUS:
                area=float(g.intersection(circle).area)
                choices.append((dist,-area,str(a.get("ATTRIBUTE") or ""),a))
        rec["query_success"]=True
        if not choices:
            rec.update({
              "ATTRIBUTE":"no_NWI_wetland_500m","WETLAND_TYPE":"no_NWI_wetland_500m",
              "WATER_REGIME":"no_NWI_wetland_500m","WATER_REGIME_NAME":"no_NWI_wetland_500m",
              "WATER_REGIME_SUBGROUP":"no_NWI_wetland_500m","SYSTEM_NAME":"no_NWI_wetland_500m",
              "CLASS_NAME":"no_NWI_wetland_500m","code_join_success":True,"area_in_500m_m2":0.0
            })
        else:
            choices.sort(key=lambda z:(z[0],z[1],z[2]))
            dist,negarea,attr,a=choices[0]
            rec.update({"ATTRIBUTE":attr,"WETLAND_TYPE":str(a.get("WETLAND_TYPE") or ""),
                        "distance_m":dist,"area_in_500m_m2":-negarea})
            # Official WATER_REGIME join is intentionally deferred to the
            # single aggregate job to avoid multiplying code-table API load.
            rec["code_join_success"]=False
    except Exception as e:
        rec["error"]=type(e).__name__+": "+str(e)[:240]
    rows.append(rec)
    if n==1 or n%10==0 or n==len(fail):
        print(json.dumps({"shard":IDX,"done":n,"total":len(fail)}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
outcsv=OUTDIR/f"NWI_FAILED_REPAIR_SHARD_{IDX:02d}.csv"
outjson=OUTDIR/f"NWI_FAILED_REPAIR_SHARD_{IDX:02d}.json"
pd.DataFrame(rows).to_csv(outcsv,index=False)
receipt={
 "analysis":"naamp_nwi_failed_only_repair_shard_v0_1",
 "contract":"revision/NAAMP_NWI_POINT_DISTANCE_REPAIR_V0_4.md",
 "shard_index":IDX,"shard_count":COUNT,
 "input_failed_rows":int(len(fail)),
 "recovered_query_success":int(sum(bool(x.get("query_success")) for x in rows)),
 "recovered_query_success":int(sum(bool(x.get("query_success")) for x in rows)),
 "explicit_no_wetland_complete":int(sum(bool(x.get("query_success")) and x.get("WETLAND_TYPE")=="no_NWI_wetland_500m" for x in rows)),
 "frog_endpoint_calculated":False
}
outjson.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
