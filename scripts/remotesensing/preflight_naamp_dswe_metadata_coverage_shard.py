#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, importlib.util, io, json, math, os, time, urllib.request, urllib.error
from collections import defaultdict
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/"exploration"
RS=ROOT/"scripts"/"remotesensing"
OUTDIR=ROOT/"remotesensing"/"dswe_coverage_shards"

SHARD_INDEX=int(os.environ.get("SHARD_INDEX","0"))
SHARD_COUNT=int(os.environ.get("SHARD_COUNT","16"))
LOOKBACK=16
API="https://landsatlook.usgs.gov/stac-server/search"
COLLECTION="landsat-c2l3-dswe"

COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

flex=loadmod("flex",EXP/"run_naamp_flexible_common_environment_null.py")
hyd=loadmod("hyd",RS/"run_naamp_dynamic_hydrology_mechanism.py")
mem=flex.mem

def fetch_bytes(url):
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frogcs-dswe-coverage/0.1"})
            with urllib.request.urlopen(req,timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (403,429,500,502,503,504):
                raise
        except (urllib.error.URLError,TimeoutError) as e:
            last=e
        time.sleep(2*(i+1))
    raise RuntimeError(f"coordinate fetch failed after retries: {last}")

def post_search(body):
    raw=json.dumps(body).encode()
    last=None
    for i in range(6):
        try:
            req=urllib.request.Request(
                API,data=raw,method="POST",
                headers={"Content-Type":"application/json","Accept":"application/geo+json","User-Agent":"frogcs-dswe-coverage/0.1"}
            )
            with urllib.request.urlopen(req,timeout=90) as r:
                return json.loads(r.read().decode())
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            last=e
            time.sleep(2*(i+1))
    raise RuntimeError(f"STAC search failed after retries: {last}")

def survey_date_map(runs):
    return {
        str(r.RunID): date(int(r.SurveyYear),1,1)+timedelta(days=int(r.doy)-1)
        for r in runs.itertuples(index=False)
    }

def point_in_bbox(lat,lon,b):
    return len(b)>=4 and b[0] <= lon <= b[2] and b[1] <= lat <= b[3]

# Coordinate authority.
b=fetch_bytes(COORD_URL)
if hashlib.sha256(b).hexdigest()!=COORD_SHA:
    raise RuntimeError("coordinate hash drift")
coords={}
for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
    sid=(r.get("SiteID") or "").strip()
    if sid:
        coords[sid]=(str(r.get("RouteNumber") or "").strip(),float(r["lat"]),float(r["lon"]))

# Frozen principal population; no focal effect values are emitted.
raw,runs,psub,dsub,hsub,pools,sampled,ss=flex.prepare_subset()
eligible=set(runs.RunID.astype(str))
site=mem.site_map(raw,eligible)
safe=hyd.strict_routes()
dates=survey_date_map(runs)

run_specs={}
pair_specs=[]
for p,dct in zip(psub.itertuples(index=False),dsub):
    route=str(p.RouteNumber)
    if route not in safe:
        continue
    ids=mem.focal_siteids(p,dct,site)
    if ids is None or len(ids)!=10 or any(s not in coords for s in ids):
        continue
    wr,dr=str(p.wet_RunID),str(p.dry_RunID)
    if wr not in dates or dr not in dates:
        continue
    pair_specs.append({
        "pair_key":f"{p.State}|{p.RouteNumber}|{p.RunNumber}|{p.year_earlier}|{p.year_later}",
        "route_cluster":str(p.route_cluster),"State":str(p.State),
        "wet_RunID":wr,"dry_RunID":dr
    })
    for rid in (wr,dr):
        spec={"RunID":rid,"route_cluster":str(p.route_cluster),"State":str(p.State),
              "RouteNumber":route,"date":dates[rid].isoformat(),"siteids":list(ids)}
        if rid in run_specs and run_specs[rid]["siteids"]!=spec["siteids"]:
            raise RuntimeError(f"site identity drift {rid}")
        run_specs[rid]=spec

keys=sorted(run_specs)
assigned=[rid for i,rid in enumerate(keys) if i%SHARD_COUNT==SHARD_INDEX]
rows=[]

for n,rid in enumerate(assigned,1):
    spec=run_specs[rid]
    pts=[coords[s] for s in spec["siteids"]]
    lats=[x[1] for x in pts]; lons=[x[2] for x in pts]
    margin=.01
    bbox=[min(lons)-margin,min(lats)-margin,max(lons)+margin,max(lats)+margin]
    d=date.fromisoformat(spec["date"])
    start=d-timedelta(days=LOOKBACK)
    body={
      "collections":[COLLECTION],
      "bbox":bbox,
      "datetime":f"{start.isoformat()}T00:00:00Z/{d.isoformat()}T23:59:59Z",
      "limit":200
    }
    obj=post_search(body)
    feats=obj.get("features") or []
    if len(feats)>=200:
        # Fail closed rather than silently truncating an unexpectedly large query.
        raise RuntimeError(f"STAC query reached limit for RunID {rid}")
    site_counts={}
    nearest_days={}
    candidate_ids={}
    for sid in spec["siteids"]:
        _,lat,lon=coords[sid]
        cand=[]
        for f in feats:
            bb=f.get("bbox") or []
            if not point_in_bbox(lat,lon,bb):
                continue
            dt=(f.get("properties") or {}).get("datetime")
            if not dt:
                continue
            try:
                acq=datetime.fromisoformat(dt.replace("Z","+00:00")).date()
            except Exception:
                continue
            lag=(d-acq).days
            if 0<=lag<=LOOKBACK and "inwam" in (f.get("assets") or {}):
                cand.append((lag,str(f.get("id") or "")))
        cand=sorted(cand)
        site_counts[sid]=len(cand)
        nearest_days[sid]=cand[0][0] if cand else None
        candidate_ids[sid]=cand[0][1] if cand else None

    rows.append({
      "RunID":rid,"route_cluster":spec["route_cluster"],"State":spec["State"],
      "RouteNumber":spec["RouteNumber"],"survey_date":spec["date"],
      "stac_items_returned":len(feats),
      "sites_with_candidate":sum(v>0 for v in site_counts.values()),
      "all10_metadata_candidate":all(v>0 for v in site_counts.values()),
      "site_candidate_counts":site_counts,
      "nearest_lag_days":nearest_days,
      "nearest_item_ids":candidate_ids
    })
    if n==1 or n%10==0 or n==len(assigned):
        print(json.dumps({"shard":SHARD_INDEX,"run":n,"runs":len(assigned),"RunID":rid}),flush=True)

OUTDIR.mkdir(parents=True,exist_ok=True)
out=OUTDIR/f"dswe_metadata_coverage_shard_{SHARD_INDEX:02d}.json"
payload={
 "analysis":"naamp_dswe_metadata_coverage_shard_v0_1",
 "contract":"revision/NAAMP_LANDSAT_DSWE_MECHANISM_CONTRACT_V0_1.md",
 "shard_index":SHARD_INDEX,"shard_count":SHARD_COUNT,
 "lookback_days":LOOKBACK,
 "runs_total_frozen":len(keys),"runs_assigned":len(assigned),
 "runs_all10_metadata_candidate":sum(bool(r["all10_metadata_candidate"]) for r in rows),
 "rows":rows,
 "frog_endpoint_values_emitted":False,
 "dswe_raster_values_read":False
}
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:payload[k] for k in payload if k!="rows"},indent=2,sort_keys=True))
