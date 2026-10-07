#!/usr/bin/env python3
from __future__ import annotations
import csv, io, json, math, hashlib, urllib.request
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
OUT=Path("remotesensing/NAAMP_RS_COORDINATE_ELIGIBILITY_RECEIPT_V0_1.json")
KNOWN_FLAGGED={"270107","880113","720214","350414","270218"}

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"frogcs-rs-coordinate-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        b=r.read()
    got=hashlib.sha256(b).hexdigest()
    if got!=SHA:
        raise RuntimeError(f"coordinate source hash drift: {got}")
    return b

def hav(lat1,lon1,lat2,lon2):
    R=6371.0088
    a1,a2=math.radians(lat1),math.radians(lat2)
    dlat=math.radians(lat2-lat1)
    dlon=math.radians(lon2-lon1)
    h=math.sin(dlat/2)**2+math.cos(a1)*math.cos(a2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1.0,math.sqrt(h)))

b=fetch()
rows=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
byroute=defaultdict(list)
for r in rows:
    route=str(r.get("RouteNumber") or "").strip()
    sid=str(r.get("SiteID") or "").strip()
    if not route or not sid:
        continue
    try:
        lat=float(r["lat"]); lon=float(r["lon"])
    except Exception:
        continue
    byroute[route].append((sid,lat,lon))

route_records=[]
for route,pts in sorted(byroute.items()):
    reasons=[]
    bysid=defaultdict(set)
    for sid,lat,lon in pts:
        bysid[sid].add((lat,lon))
    conflicts={sid:sorted(v) for sid,v in bysid.items() if len(v)>1}
    unique=[]
    for sid,v in bysid.items():
        # Keep a coordinate only when physical identity is unambiguous.
        if len(v)==1:
            lat,lon=next(iter(v))
            unique.append((sid,lat,lon))
    if len(unique)<8:
        reasons.append("lt8_unambiguous_sites")
    if conflicts:
        reasons.append("siteid_coordinate_conflict")

    outside=[x for x in unique if not (24<=x[1]<=50 and -125<=x[2]<=-66)]
    if outside:
        reasons.append("outside_conus_bounds")

    inside=[x for x in unique if 24<=x[1]<=50 and -125<=x[2]<=-66]
    max_span=None
    max_to_median=None
    median_to_median=None
    mad_to_median=None
    robust_outliers=0

    if len(inside)>=2:
        ds=[]
        for i in range(len(inside)):
            for j in range(i+1,len(inside)):
                ds.append(hav(inside[i][1],inside[i][2],inside[j][1],inside[j][2]))
        max_span=float(max(ds))
        if max_span>30:
            reasons.append("route_span_gt30km")

    if inside:
        mlat=float(np.median([x[1] for x in inside]))
        mlon=float(np.median([x[2] for x in inside]))
        dmed=np.array([hav(x[1],x[2],mlat,mlon) for x in inside],float)
        median_to_median=float(np.median(dmed))
        mad_to_median=float(np.median(np.abs(dmed-median_to_median)))
        max_to_median=float(dmed.max())
        if max_to_median>15:
            reasons.append("site_gt15km_from_route_median")
        if mad_to_median>0:
            robust_limit=median_to_median+8*mad_to_median
            robust_outliers=int(np.sum(dmed>robust_limit))
            if robust_outliers:
                reasons.append("robust_geometry_outlier")

    eligible=(len(reasons)==0 and len(inside)>=8)
    route_records.append({
        "RouteNumber":route,
        "raw_rows":len(pts),
        "unambiguous_sites":len(unique),
        "inside_conus_sites":len(inside),
        "coordinate_conflict_sites":len(conflicts),
        "max_pairwise_km":max_span,
        "median_site_to_route_median_km":median_to_median,
        "mad_site_to_route_median_km":mad_to_median,
        "max_site_to_route_median_km":max_to_median,
        "robust_outliers":robust_outliers,
        "eligible":eligible,
        "reasons":sorted(set(reasons)),
        "known_previously_flagged":route in KNOWN_FLAGGED
    })

eligible=[x for x in route_records if x["eligible"]]
excluded=[x for x in route_records if not x["eligible"]]
reasons=Counter(r for x in excluded for r in x["reasons"])
spans=[x["max_pairwise_km"] for x in route_records if x["max_pairwise_km"] is not None]
maxmed=[x["max_site_to_route_median_km"] for x in route_records if x["max_site_to_route_median_km"] is not None]

result={
  "analysis":"naamp_rs_coordinate_eligibility_v0_1",
  "contract":"remotesensing/NAAMP_RS_COORDINATE_ELIGIBILITY_CONTRACT_V0_1.md",
  "source":{"sha256":SHA,"rows":len(rows),"routes":len(route_records)},
  "summary":{
    "eligible_routes":len(eligible),
    "excluded_routes":len(excluded),
    "eligible_fraction":len(eligible)/len(route_records) if route_records else None,
    "exclusion_reasons":dict(sorted(reasons.items())),
    "known_flagged_routes":{
      "total":len(KNOWN_FLAGGED),
      "eligible":[x["RouteNumber"] for x in route_records if x["known_previously_flagged"] and x["eligible"]],
      "excluded":[x["RouteNumber"] for x in route_records if x["known_previously_flagged"] and not x["eligible"]]
    }
  },
  "geometry_distributions":{
    "max_pairwise_km_quantiles":{str(q):float(np.quantile(spans,q)) for q in [0,.5,.9,.95,.99,1]} if spans else {},
    "max_site_to_route_median_km_quantiles":{str(q):float(np.quantile(maxmed,q)) for q in [0,.5,.9,.95,.99,1]} if maxmed else {}
  },
  "eligible_route_numbers":[x["RouteNumber"] for x in eligible],
  "excluded_routes":excluded,
  "outcomes_read":False,
  "coordinates_repaired":False
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps({k:result[k] for k in ["analysis","source","summary","geometry_distributions"]},indent=2))
