#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,importlib.util,io,json,math,re,urllib.request
from collections import Counter,defaultdict
from datetime import datetime,date,time,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import xarray as xr
from timezonefinder import TimezoneFinder

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ATMOSPHERIC_CUE_ELIGIBILITY_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-atmospheric-eligibility/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

def coords():
    raw=fetch(COORD_URL)
    if hashlib.sha256(raw).hexdigest()!=COORD_SHA:raise RuntimeError("Coordinates hash drift")
    out={}
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        sid=(r.get("SiteID") or "").strip()
        if sid:
            out[sid]=(float(r["lat"]),float(r["lon"]))
    return out

def parse_clock(x):
    s=str(x or "").strip()
    if not s:return None,None
    s2=re.sub(r"\s+"," ",s.upper().replace(".","")).strip()
    fmts=["%H:%M","%H:%M:%S","%H%M","%I:%M %p","%I:%M:%S %p","%I %p"]
    for f in fmts:
        try:
            t=datetime.strptime(s2,f).time()
            return t,f
        except Exception:pass
    # tolerate numeric hour values like 20.5 only if within day
    try:
        v=float(s2)
        if 0<=v<24:
            h=int(v); m=int(round((v-h)*60))
            if m==60:h=(h+1)%24;m=0
            return time(h,m),"decimal_hour"
    except Exception:pass
    return None,None

def route_midpoints(raw,eligible_ids,cmap):
    byrun=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip();sid=(s.get("SiteID") or "").strip()
        if rid not in eligible_ids or (s.get("SkippedStop") or "").strip()!="0":continue
        if sid in cmap:byrun[rid].append(cmap[sid])
    out={}
    for rid,pts in byrun.items():
        if len(pts)>=8:
            out[rid]=(float(np.mean([p[0] for p in pts])),float(np.mean([p[1] for p in pts])),len(pts))
    return out

def localize_midpoint(survey_date,start_t,end_t,tz):
    a=datetime.combine(survey_date,start_t)
    b=datetime.combine(survey_date,end_t)
    if b<=a:b+=timedelta(days=1)
    dur=(b-a).total_seconds()/3600
    if not 0.25<=dur<=6.0:return None,dur
    mid=a+(b-a)/2
    # zoneinfo does not raise for gaps; round-trip through UTC to verify wall time identity
    z=mid.replace(tzinfo=ZoneInfo(tz))
    rt=z.astimezone(ZoneInfo("UTC")).astimezone(ZoneInfo(tz))
    if rt.replace(tzinfo=None)!=mid:return None,dur
    return z,dur

def main():
    raw=base.load();runs,sets=base.build_runs(raw);pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    eligible=set(runs["RunID"].astype(str));cmap=coords();cent=route_midpoints(raw,eligible,cmap)
    tf=TimezoneFinder(in_memory=True)
    run_raw={str(r.get("RunID") or "").strip():r for r in raw["Runs.csv"]}
    date_by={str(r.RunID):date.fromisoformat(str(r.SurveyDate)[:10]) if re.match(r"\d{4}-\d{2}-\d{2}",str(r.SurveyDate)) else None for r in runs.itertuples(index=False)}
    # build date robustly from already validated year/doy if raw format is not ISO
    for rr in runs.itertuples(index=False):
        rid=str(rr.RunID)
        if date_by.get(rid) is None:
            date_by[rid]=date(int(rr.SurveyYear),1,1)+timedelta(days=int(rr.doy)-1)

    records={};fmt_start=Counter();fmt_end=Counter();raw_examples=[];tz_fail=0;coord_fail=0;time_fail=0;duration_fail=0
    for rid in sorted(eligible):
        row=run_raw.get(rid,{})
        st,fs=parse_clock(row.get("StartTime"));et,fe=parse_clock(row.get("EndTime"))
        if fs:fmt_start[fs]+=1
        if fe:fmt_end[fe]+=1
        if (st is None or et is None) and len(raw_examples)<25:
            raw_examples.append({"RunID":rid,"StartTime":row.get("StartTime"),"EndTime":row.get("EndTime")})
        if st is None or et is None:
            time_fail+=1;records[rid]={"eligible":False,"reason":"time_parse"};continue
        if rid not in cent:
            coord_fail+=1;records[rid]={"eligible":False,"reason":"coordinate"};continue
        lat,lon,n=cent[rid]
        tz=tf.timezone_at(lat=lat,lng=lon)
        if not tz:
            tz_fail+=1;records[rid]={"eligible":False,"reason":"timezone"};continue
        mid,dur=localize_midpoint(date_by[rid],st,et,tz)
        if mid is None:
            duration_fail+=1;records[rid]={"eligible":False,"reason":"duration_or_dst","duration_h":dur};continue
        records[rid]={"eligible":True,"lat":lat,"lon":lon,"n_coords":n,"timezone":tz,"midpoint":mid.isoformat(),"duration_h":dur}

    good=sum(v["eligible"] for v in records.values())
    pair_good=0
    for p in pairs.itertuples(index=False):
        if records.get(str(p.wet_RunID),{}).get("eligible") and records.get(str(p.dry_RunID),{}).get("eligible"):pair_good+=1

    storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True)
    repo=icechunk.Repository.open(storage);session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    vars={}
    for v in ("t2m","d2m","sp"):
        if v in ds:
            a=ds[v]
            vars[v]={"present":True,"units":str(a.attrs.get("units")),"paramId":a.attrs.get("GRIB_paramId"),"dims":list(a.dims)}
        else:vars[v]={"present":False}
    vars_pass=all(vars[v]["present"] for v in vars)
    run_frac=good/len(records);pair_frac=pair_good/len(pairs)
    passed=bool(run_frac>=.90 and pair_frac>=.90 and vars_pass)

    durations=[v["duration_h"] for v in records.values() if v.get("eligible")]
    out={
      "analysis":"naamp_atmospheric_cue_eligibility_v0_1",
      "contract":"exploration/NAAMP_ATMOSPHERIC_CUE_ELIGIBILITY_CONTRACT_V0_1.json",
      "coverage":{
        "eligible_runs_total":int(len(records)),"valid_midpoint_runs":int(good),"valid_midpoint_run_fraction":float(run_frac),
        "matched_pairs":int(len(pairs)),"valid_both_member_pairs":int(pair_good),"valid_pair_fraction":float(pair_frac),
        "time_parse_fail_runs":int(time_fail),"coordinate_fail_runs":int(coord_fail),"timezone_fail_runs":int(tz_fail),"duration_or_dst_fail_runs":int(duration_fail)
      },
      "time_formats":{"start":dict(fmt_start),"end":dict(fmt_end),"unparsed_examples":raw_examples},
      "duration_h":{"median":float(np.median(durations)) if durations else None,"q05":float(np.quantile(durations,.05)) if durations else None,"q95":float(np.quantile(durations,.95)) if durations else None},
      "era5_variables":vars,
      "eligibility_gate":{"run_fraction_pass":bool(run_frac>=.90),"pair_fraction_pass":bool(pair_frac>=.90),"era5_variables_pass":vars_pass,"overall_pass":passed},
      "interpretation_boundary":{"frog_response_read":False,"atmospheric_test_authorized":passed}
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":main()
