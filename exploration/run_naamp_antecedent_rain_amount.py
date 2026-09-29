#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import xarray as xr
from timezonefinder import TimezoneFinder

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_ANTECEDENT_RAIN_AMOUNT_RECEIPT_V0_1.json"
COORD_URL="https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
COORD_SHA="f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base=loadmod("base",NAAMP/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",NAAMP/"run_naamp_spatial_taxonomic_activation_decomposition.py")
sameobs=loadmod("sameobs",NAAMP/"run_naamp_same_observer_robustness.py")

def retry(fn,label):
    last=None
    for i in range(6):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            last=e
            if getattr(e,"code",None) not in (403,429,500,502,503,504):
                raise
        except Exception as e:
            last=e
            if i>=5:
                raise
        time.sleep(2*(i+1))
    raise RuntimeError(f"{label} failed after retries: {last}")

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-rain-amount/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def load_coords():
    raw=retry(lambda:fetch_bytes(COORD_URL),"Coordinates load")
    got=hashlib.sha256(raw).hexdigest()
    if got!=COORD_SHA:
        raise RuntimeError(f"Coordinates hash drift {got}")
    out={}
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        sid=(r.get("SiteID") or "").strip()
        if sid:
            out[sid]=(float(r["lat"]),float(r["lon"]))
    return out

def parse_clock(x):
    s=str(x or "").strip()
    if not s or s.upper()=="NULL":
        return None
    s2=re.sub(r"\s+"," ",s.upper().replace(".","")).strip()
    for fmt in ("%H:%M","%H:%M:%S","%H%M","%I:%M %p","%I:%M:%S %p","%I %p"):
        try:
            return datetime.strptime(s2,fmt).time()
        except Exception:
            pass
    try:
        v=float(s2)
        if 0<=v<24:
            h=int(v); mm=int(round((v-h)*60))
            if mm==60:
                h=(h+1)%24; mm=0
            return dtime(h,mm)
    except Exception:
        pass
    return None

def build_midpoints(raw,runs):
    eligible=set(runs["RunID"].astype(str))
    cmap=load_coords()
    byrun=defaultdict(list)
    for s in raw["Stops.csv"]:
        rid=(s.get("RunID") or "").strip()
        sid=(s.get("SiteID") or "").strip()
        if rid not in eligible or (s.get("SkippedStop") or "").strip()!="0":
            continue
        if sid in cmap:
            byrun[rid].append(cmap[sid])
    centers={}
    for rid,pts in byrun.items():
        if len(pts)>=8:
            centers[rid]=(float(np.mean([p[0] for p in pts])),float(np.mean([p[1] for p in pts])))
    tf=TimezoneFinder(in_memory=True)
    runraw={str(r.get("RunID") or "").strip():r for r in raw["Runs.csv"]}
    dates={
        str(rr.RunID):date(int(rr.SurveyYear),1,1)+timedelta(days=int(rr.doy)-1)
        for rr in runs.itertuples(index=False)
    }
    rec={}
    for rid in sorted(eligible):
        row=runraw.get(rid,{})
        st=parse_clock(row.get("StartTime")); et=parse_clock(row.get("EndTime"))
        if st is None or et is None or rid not in centers:
            continue
        a=datetime.combine(dates[rid],st)
        b=datetime.combine(dates[rid],et)
        if b<=a:
            b+=timedelta(days=1)
        dur=(b-a).total_seconds()/3600
        if not 0.25<=dur<=6.0:
            continue
        lat,lon=centers[rid]
        tz=tf.timezone_at(lat=lat,lng=lon)
        if not tz:
            continue
        mid=a+(b-a)/2
        z=mid.replace(tzinfo=ZoneInfo(tz))
        rt=z.astimezone(ZoneInfo("UTC")).astimezone(ZoneInfo(tz))
        if rt.replace(tzinfo=None)!=mid:
            continue
        rec[rid]={"lat":lat,"lon":lon,"midpoint":z}
    return rec

def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by

def strong_metrics(p,sampled,by):
    w=str(p.wet_RunID); d=str(p.dry_RunID)
    score=0.0; count=0.0
    for st in sorted(sampled[w]):
        wm=by.get((w,st),{}); dm=by.get((d,st),{})
        for sp in set(wm)|set(dm):
            wi=int(wm.get(sp,0)); di=int(dm.get(sp,0))
            if di==0 and wi>=2:
                score+=wi; count+=1
    return score,count

def antecedent_amounts(records):
    ids=sorted(records)
    storage=icechunk.s3_storage(
        bucket="earthmover-icechunk-era5",prefix="icechunkV2",
        region="us-east-1",anonymous=True
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    tp=ds["tp"]
    if tp.attrs.get("GRIB_paramId") not in (228,"228") or str(tp.attrs.get("units"))!="m":
        raise RuntimeError("ERA5 tp identity drift")
    if "1 hour" not in str(tp.attrs.get("accumulation_comment","")):
        raise RuntimeError("ERA5 tp accumulation semantics drift")

    out={}
    h=hashlib.sha256()
    BATCH=250
    for b0 in range(0,len(ids),BATCH):
        batch=ids[b0:b0+BATCH]
        n=len(batch)
        lat=np.asarray([records[r]["lat"] for r in batch],float)
        lon=np.asarray([records[r]["lon"]%360 for r in batch],float)
        ends=[]
        for r in batch:
            utc=records[r]["midpoint"].astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            ts=pd.Timestamp(utc).floor("h")
            ends.append(np.datetime64(ts.to_datetime64(),"ns"))
        ends=np.asarray(ends)
        offsets=np.arange(71,-1,-1,dtype="timedelta64[h]")
        times=ends[:,None]-offsets[None,:]
        flat_lat=np.repeat(lat,72)
        flat_lon=np.repeat(lon,72)
        flat_time=times.reshape(-1)
        sel=tp.sel(
            latitude=xr.DataArray(flat_lat,dims="point"),
            longitude=xr.DataArray(flat_lon,dims="point"),
            valid_time=xr.DataArray(flat_time,dims="point"),
            method="nearest"
        )
        vals=np.asarray(sel.values,float).reshape(n,72)
        if not np.isfinite(vals).all():
            raise RuntimeError("nonfinite tp")
        if float(vals.min())<-1e-8:
            raise RuntimeError(f"tp below negative tolerance {float(vals.min())}")
        vals[vals<0]=0.0
        mm=vals*1000.0
        sum72=mm.sum(axis=1)
        sum24=mm[:,-24:].sum(axis=1)
        slat=np.asarray(sel["latitude"].values,float).reshape(n,72)[:,0]
        slon=np.asarray(sel["longitude"].values,float).reshape(n,72)[:,0]
        stime=np.asarray(sel["valid_time"].values).reshape(n,72)
        if np.max(np.abs(slat-lat))>0.126:
            raise RuntimeError("tp latitude mismatch")
        lon_delta=np.minimum(np.abs(slon-lon),360-np.abs(slon-lon))
        if np.max(lon_delta)>0.126:
            raise RuntimeError("tp longitude mismatch")
        if not np.array_equal(stime.astype("datetime64[h]"),times.astype("datetime64[h]")):
            raise RuntimeError("tp hourly-time mismatch")
        for i,rid in enumerate(batch):
            out[rid]={
                "rain72_mm":float(sum72[i]),
                "rain24_mm":float(sum24[i]),
                "era5_lat":float(slat[i]),
                "era5_lon":float(((slon[i]+180)%360)-180),
                "end_hour_utc":str(ends[i])
            }
            h.update(f"{rid},{slat[i]:.4f},{slon[i]:.4f},{str(ends[i])},{sum72[i]:.8f},{sum24[i]:.8f}\n".encode())
        print(json.dumps({"weather_runs_processed":min(b0+BATCH,len(ids)),"weather_runs_total":len(ids)}),flush=True)
    return out,h.hexdigest()

def zscore(a):
    x=np.asarray(a,float); mu=float(np.mean(x)); sd=float(np.std(x,ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise RuntimeError("invalid zscore")
    return (x-mu)/sd,mu,sd

def fit(df,response,amount_col):
    formula=f"{response} ~ rain_contrast + {amount_col} + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(formula,data=df).fit(cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
    def term(x):
        b=float(m.params[x]); se=float(m.bse[x])
        return {"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(m.pvalues[x])}
    return {
        "response":response,"formula":formula,
        "n_pairs":int(len(df)),"n_routes":int(df.route_cluster.nunique()),
        "rain_contrast":term("rain_contrast"),
        "amount_contrast":term(amount_col)
    }

def main():
    raw=retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    mid=build_midpoints(raw,runs)
    if len(mid)<7500:
        raise RuntimeError(f"midpoint coverage drift {len(mid)}")
    weather,weather_sha=antecedent_amounts(mid)

    sampled,_=spatial.stop_matrix(raw,eligible)
    by=build_ci(raw,eligible,sampled)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        score,count=strong_metrics(p,sampled,by)
        row=p._asdict()
        row.update({
            "strong_new_score":score,"strong_new_count":count,
            "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
            "rain24_log_difference":float(np.log1p(weather[w]["rain24_mm"])-np.log1p(weather[d]["rain24_mm"]))
        })
        rows.append(row)
    df=pd.DataFrame(rows)
    if len(df)!=4108:
        raise RuntimeError(f"eligible pair drift {len(df)} != 4108")
    df["rain72_amount_difference_z"],m72,s72=zscore(df["rain72_log_difference"])
    df["rain24_amount_difference_z"],m24,s24=zscore(df["rain24_log_difference"])

    primary=fit(df,"strong_new_score","rain72_amount_difference_z")
    count=fit(df,"strong_new_count","rain72_amount_difference_z")
    rain24=fit(df,"strong_new_score","rain24_amount_difference_z")
    exact=fit(df[df["year_gap"]==1].copy(),"strong_new_score","rain72_amount_difference_z")
    allpairs,same=sameobs.same_observer_pairs(raw,runs,sets)
    sameids={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    dsame=df[[(str(p.wet_RunID),str(p.dry_RunID)) in sameids for p in df.itertuples(index=False)]].copy()
    same_report=fit(dsame,"strong_new_score","rain72_amount_difference_z")

    corr=float(np.corrcoef(df["rain_contrast"],df["rain72_log_difference"])[0,1])
    amt=primary["amount_contrast"]; rain=primary["rain_contrast"]
    out={
        "analysis":"naamp_antecedent_rain_amount_strong_activation_v0_1",
        "contract":"exploration/NAAMP_ANTECEDENT_RAIN_AMOUNT_CONTRACT_V0_1.json",
        "coverage":{"eligible_pairs":int(len(df)),"routes":int(df.route_cluster.nunique()),"same_observer_pairs":int(len(dsame))},
        "era5":{"required_antecedent_amount_sha256":weather_sha,"weather_runs":int(len(weather))},
        "standardization":{
            "rain72_log_difference_mean":m72,"rain72_log_difference_sd":s72,
            "rain24_log_difference_mean":m24,"rain24_log_difference_sd":s24,
            "rain_contrast_rain72_log_difference_correlation":corr
        },
        "primary_72h_strong_new_score":primary,
        "secondary_72h_strong_new_count":count,
        "sensitivity_24h":rain24,
        "sensitivity_exact_consecutive_year":exact,
        "sensitivity_same_observer":same_report,
        "classification":{
            "pulse_magnitude_support":bool(amt["beta"]>0 and amt["ci95"][0]>0),
            "recency_robustness":bool(rain["beta"]>0 and rain["ci95"][0]>0)
        },
        "interpretation_boundary":{
            "hydrological_mediation_established":False,
            "era5_precipitation_is_local_gauge":False,
            "submission_story_change_authorized":False
        }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
