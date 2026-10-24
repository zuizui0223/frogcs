#!/usr/bin/env python3
"""Fail-closed quality check for NEW independent field measurements (never NAAMP Counts.csv)."""
from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
REQUIRED_SITE={"RouteNumber","SiteID","field_event_id","timestamp_local_iso8601","direct_water_present","water_depth_cm","flooded_area_fraction","water_measurement_method","acoustic_recorder_id","ambient_temp_c","wind_m_s","noise_dba","field_access_verified","water_missing_reason"}
REQUIRED_CALL={"RouteNumber","SiteID","field_event_id","taxon","calling_index","acoustic_start_iso8601","audio_sha256","observer_or_classifier"}

def load(path,columns):
    with open(path,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not columns.issubset(reader.fieldnames):
            raise ValueError(f"missing source columns: {sorted(columns-set(reader.fieldnames or []))}")
        return list(reader)

def value(x):
    if str(x).strip()=="":return None
    v=float(x)
    if not math.isfinite(v):raise ValueError("nonfinite field measurement")
    return v

def evaluate(site_registry,site_events,acoustic):
    registry=load(site_registry,{"RouteNumber","SiteID","latitude","longitude"})
    allowed={(r["RouteNumber"],r["SiteID"]) for r in registry}
    if len(allowed)!=len(registry):raise ValueError("duplicate physical site registry key")
    visits=load(site_events,REQUIRED_SITE)
    calls=load(acoustic,REQUIRED_CALL)
    matched=set();by_run=defaultdict(set)
    for r in visits:
        loc=(r["RouteNumber"],r["SiteID"])
        key=loc+(r["field_event_id"],)
        if loc not in allowed or key in matched:raise ValueError("unknown/duplicate field station/event")
        matched.add(key);by_run[(loc[0],r["field_event_id"])].add(loc[1])
        datetime.fromisoformat(r["timestamp_local_iso8601"])
        present=r["direct_water_present"].lower().strip()
        if present not in ("yes","no","missing"):raise ValueError("direct water must be yes/no/missing")
        depth=value(r["water_depth_cm"]);fraction=value(r["flooded_area_fraction"])
        if depth is not None and depth<0:raise ValueError("negative depth")
        if fraction is not None and not 0<=fraction<=1:raise ValueError("invalid flooded fraction")
        if present=="missing" and (depth is not None or fraction is not None or not r["water_missing_reason"].strip()):
            raise ValueError("missing water must be explicit, never 0")
        if present=="no" and ((depth is not None and depth>0) or (fraction is not None and fraction>0)):
            raise ValueError("dry water conflicts with positive depth")
        if present=="yes" and depth is None and fraction is None:raise ValueError("observed water needs depth/area")
        if r["field_access_verified"].lower().strip()!="yes":raise ValueError("field access unverified")
        if not r["water_measurement_method"].strip() or not r["acoustic_recorder_id"].strip():
            raise ValueError("measurement/source protocol missing")
        for f in ("ambient_temp_c","wind_m_s","noise_dba"):
            if r[f].strip():value(r[f])
    seen=set()
    for r in calls:
        key=(r["RouteNumber"],r["SiteID"],r["field_event_id"],r["taxon"])
        if key[:3] not in matched or key in seen:raise ValueError("unmatched/duplicate acoustic taxon record")
        seen.add(key)
        if r["calling_index"] not in ("0","1","2","3"):
            raise ValueError("CI0=assessed nondetection; CI must be 0..3")
        h=r["audio_sha256"].lower()
        if len(h)!=64 or any(c not in "0123456789abcdef" for c in h):
            raise ValueError("missing acoustic-file provenance SHA256")
        datetime.fromisoformat(r["acoustic_start_iso8601"])
    return {"n_site_events":len(visits),"n_acoustic_taxon_events":len(calls),
        "n_ten_site_complete_route_events":sum(len(v)==10 for v in by_run.values()),
        "n_route_events":len(by_run),
        "raw_naamp_outcomes_read":False,
        "interpretation":"Field quality only. Does not estimate water causality or occupancy."}

def paired_water_rank(event0,event1):
    if set(event0)!=set(event1) or len(event0)<6:raise ValueError("six same physical stations required")
    d=[float(event1[k])-float(event0[k]) for k in sorted(event0)]
    if not all(math.isfinite(x) for x in d):raise ValueError("missing water must not be 0")
    mean=sum(d)/len(d);rms=math.sqrt(sum((x-mean)**2 for x in d)/len(d))
    return {"n_sites":len(d),"route_common_change_cm":mean,
        "site_relative_change_rms_cm":rms,"site_relative_change_range_cm":max(d)-min(d),
        "nonuniform_site_change":rms>1e-12,
        "warning":"Field sensor error and recording detectability require independent validation."}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry",required=True)
    p.add_argument("--site-events",required=True)
    p.add_argument("--acoustic-detections",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    report=evaluate(a.registry,a.site_events,a.acoustic_detections)
    Path(a.out).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,indent=2))
