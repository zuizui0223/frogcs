#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, math, urllib.request
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
OUT=ROOT/"remotesensing"/"NAAMP_HYDROLOGY_REQUEST_MANIFEST_V0_1.json"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
UNSAFE={"270107","270218","350414","720214","880113"}

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
mem=flex.mem

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-hydrology-manifest/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def tile_key(lat,lon):
    # JRC VER1-0 global grid: 10-degree tiles, 40,000 pixels/tile, origin (-180,80).
    xi=int(math.floor((lon+180.0)/10.0))
    yi=int(math.floor((80.0-lat)/10.0))
    # Boundary-safe clamps for exact grid edges.
    xi=max(0,min(35,xi))
    yi=max(0,min(12,yi))
    return xi*40000, yi*40000

rawb=fetch(COORD_URL)
if hashlib.sha256(rawb).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate SHA drift")
coords={}
for r in csv.DictReader(io.StringIO(rawb.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip()
    rid=(r.get("RouteNumber") or "").strip()
    if not sid:
        continue
    coords[sid]=(rid,float(r["lat"]),float(r["lon"]))

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

pairs_safe=0
pair_fail=Counter()
unique_siteids=set()
current_requests=set()
current_files=set()
needed_months=set()
tile_ids=set()
route_ids=set()

for p,dct in zip(psub.itertuples(index=False),dsub):
    rid=str(p.RouteNumber)
    if rid in UNSAFE:
        pair_fail["unsafe_route_geometry"]+=1
        continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10:
        pair_fail["siteid_identity_missing"]+=1
        continue
    missing=[sid for sid in ids if sid not in coords]
    if missing:
        pair_fail["coordinate_missing"]+=1
        continue
    if any(coords[sid][0] in UNSAFE for sid in ids):
        pair_fail["unsafe_coordinate_route"]+=1
        continue
    wet=runmeta.get(str(p.wet_RunID)); dry=runmeta.get(str(p.dry_RunID))
    if wet is None or dry is None:
        pair_fail["run_date_missing"]+=1
        continue

    pairs_safe+=1
    route_ids.add(rid)
    for sid in ids:
        crid,lat,lon=coords[sid]
        unique_siteids.add(sid)
        xoff,yoff=tile_key(lat,lon)
        tile_ids.add((xoff,yoff))
        for rm in (wet,dry):
            year=int(rm["year"]); month=int(rm["month"])
            needed_months.add(month)
            current_requests.add((sid,year,month))
            current_files.add((year,month,xoff,yoff))

baseline_files=set()
for month in needed_months:
    for xoff,yoff in tile_ids:
        for year in range(1984,2001):
            baseline_files.add((year,month,xoff,yoff))

month_counts=Counter()
for sid,year,month in current_requests:
    month_counts[str(month)]+=1

out={
    "analysis":"naamp_hydrology_request_manifest_v0_1",
    "frozen_principal_pairs":int(len(psub)),
    "frozen_principal_routes":int(psub.route_cluster.nunique()),
    "coordinate_unsafe_routes":sorted(UNSAFE),
    "safe_intersection":{
        "pairs":pairs_safe,
        "routes":len(route_ids),
        "pair_failures":dict(pair_fail),
        "coverage_gate_pair_threshold":1500,
        "coverage_gate_route_threshold":300,
        "geometry_only_gate_pass":bool(pairs_safe>=1500 and len(route_ids)>=300)
    },
    "remote_request_scale":{
        "unique_siteids":len(unique_siteids),
        "unique_jrc_tiles":len(tile_ids),
        "jrc_tile_offsets":[{"x":x,"y":y} for x,y in sorted(tile_ids)],
        "survey_months":sorted(needed_months),
        "unique_current_site_month_requests":len(current_requests),
        "unique_current_tile_month_files":len(current_files),
        "pre2001_baseline_tile_month_files_if_all_needed_months":len(baseline_files),
        "current_request_month_counts":dict(sorted(month_counts.items(),key=lambda kv:int(kv[0])))
    },
    "jrc_filename_rule":"YYYY_MM-{xoff:010d}-{yoff:010d}.tif",
    "frog_endpoint_values_emitted":False,
    "note":"The already-frozen principal pair membership was reconstructed, but no frog endpoint or effect value is emitted or used to choose remote-sensing coverage rules."
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
