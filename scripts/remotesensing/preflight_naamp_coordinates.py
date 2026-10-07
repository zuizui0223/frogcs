#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, time, urllib.request
from collections import defaultdict
from pathlib import Path

URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
OUT=Path("remotesensing/NAAMP_COORDINATE_REMOTE_SENSING_PREFLIGHT_V0_1.json")

def fetch():
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(URL,headers={"User-Agent":"frogcs-dynamic-hydrology-preflight/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except Exception as e:
            last=e
            time.sleep(2*(i+1))
    raise RuntimeError(f"coordinate download failed: {last}")

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088
    p1=math.radians(lat1); p2=math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(min(1.0,math.sqrt(a)))

raw=fetch()
got=hashlib.sha256(raw).hexdigest()
if got!=SHA:
    raise RuntimeError(f"coordinate SHA drift: {got}")

rows=[]
for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
    rid=(r.get("RouteNumber") or "").strip()
    sid=(r.get("SiteID") or "").strip()
    try:
        lat=float(r["lat"]); lon=float(r["lon"])
    except Exception:
        lat=float("nan"); lon=float("nan")
    rows.append((rid,sid,lat,lon))

by=defaultdict(list)
for rid,sid,lat,lon in rows:
    by[rid].append((sid,lat,lon))

route_audit=[]
unsafe=[]
for rid,pts in sorted(by.items()):
    finite=all(math.isfinite(lat) and math.isfinite(lon) for _,lat,lon in pts)
    bounds=finite and all(24<=lat<=50 and -125<=lon<=-66 for _,lat,lon in pts)
    dmax=None
    if finite and len(pts)>=2:
        ds=[]
        for i in range(len(pts)):
            for j in range(i+1,len(pts)):
                ds.append(hav(pts[i][1],pts[i][2],pts[j][1],pts[j][2]))
        dmax=max(ds) if ds else 0.0
    safe=bool(finite and bounds and dmax is not None and dmax<=100.0)
    reasons=[]
    if not finite: reasons.append("nonfinite_coordinate")
    if finite and not bounds: reasons.append("outside_conus_bounds")
    if dmax is None: reasons.append("insufficient_geometry")
    elif dmax>100: reasons.append("route_span_gt_100km")
    if not safe:
        unsafe.append(rid)
    route_audit.append({
        "RouteNumber":rid,
        "n_siteids":len(pts),
        "max_pairwise_km":dmax,
        "safe":safe,
        "reasons":reasons,
    })

maxes=[x["max_pairwise_km"] for x in route_audit if x["max_pairwise_km"] is not None]
out={
    "analysis":"naamp_coordinate_remote_sensing_preflight_v0_1",
    "coordinate_source_sha256":got,
    "n_coordinate_rows":len(rows),
    "n_routes":len(by),
    "rules":{
        "latitude_bounds":[24,50],
        "longitude_bounds":[-125,-66],
        "maximum_route_span_km":100,
        "manual_coordinate_repair":False
    },
    "summary":{
        "safe_routes":sum(x["safe"] for x in route_audit),
        "unsafe_routes":sum(not x["safe"] for x in route_audit),
        "safe_fraction":sum(x["safe"] for x in route_audit)/len(route_audit),
        "routes_outside_bounds":sum("outside_conus_bounds" in x["reasons"] for x in route_audit),
        "routes_span_gt_100km":sum("route_span_gt_100km" in x["reasons"] for x in route_audit),
        "max_route_span_km":max(maxes) if maxes else None,
    },
    "unsafe_routes":[x for x in route_audit if not x["safe"]],
    "geometry_quantiles_km":{
        "q50":None,"q90":None,"q95":None,"q99":None
    }
}
if maxes:
    import statistics
    xs=sorted(maxes)
    def q(p):
        if not xs: return None
        z=(len(xs)-1)*p
        lo=int(math.floor(z)); hi=int(math.ceil(z))
        if lo==hi:return xs[lo]
        return xs[lo]*(hi-z)+xs[hi]*(z-lo)
    out["geometry_quantiles_km"]={"q50":q(.5),"q90":q(.9),"q95":q(.95),"q99":q(.99)}

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2,sort_keys=True))
