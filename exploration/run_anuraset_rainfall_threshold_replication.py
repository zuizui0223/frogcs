#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import xarray as xr

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"exploration"/"ANURASET_RAINFALL_REPLICATION_RECEIPT_V0_1.json"
URL="https://zenodo.org/records/8342596/files/weak_labels.csv?download=1"
EXPECTED_MD5="3806a76cc7e6d6b9186a5c7bef442723"
SITE="INCT20955"
LAT=-28.163
LON=-49.47
TZ=ZoneInfo("America/Sao_Paulo")
WET_MM=1.0
DRY_CAP=30
Q=1.959963984540054


def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-anuraset-replication/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()


def zscore(x):
    a=np.asarray(x,float)
    mu=float(np.mean(a)); sd=float(np.std(a,ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise RuntimeError("invalid zscore scale")
    return (a-mu)/sd,mu,sd


def parse_weak():
    raw=fetch(URL)
    if hashlib.md5(raw).hexdigest()!=EXPECTED_MD5:
        raise RuntimeError("AnuraSet weak_labels.csv MD5 drift")
    df=pd.read_csv(io.BytesIO(raw))
    if "MONITORING_SITE" not in df or "AUDIO_FILE_ID" not in df:
        raise RuntimeError("AnuraSet schema drift")
    spp=[c for c in df.columns if c.startswith("SPECIES_")]
    if len(spp)!=42:
        raise RuntimeError(f"species-column drift: {len(spp)}")
    d=df[df["MONITORING_SITE"].astype(str)==SITE].copy()
    if d.empty:
        raise RuntimeError("no INCT20955 rows")
    parsed=[]
    for s in d["AUDIO_FILE_ID"].astype(str):
        toks=s.split("_")
        if len(toks)<3:
            parsed.append(pd.NaT); continue
        try:
            dt=datetime.strptime(toks[-2]+toks[-1],"%Y%m%d%H%M%S").replace(tzinfo=TZ)
        except Exception:
            dt=pd.NaT
        parsed.append(dt)
    d["local_dt"]=parsed
    d=d[d["local_dt"].notna()].copy().reset_index(drop=True)
    vals=d[spp].apply(pd.to_numeric,errors="coerce")
    if vals.isna().any().any():
        raise RuntimeError("missing/non-numeric CallingIndex")
    if not np.isin(vals.to_numpy(),[0,1,2,3]).all():
        raise RuntimeError("CallingIndex outside 0..3")
    d["total_ci"]=vals.sum(axis=1).astype(float)
    d["active_richness"]=(vals>0).sum(axis=1).astype(float)
    d["excess_intensity"]=np.maximum(vals.to_numpy(float)-1.0,0.0).sum(axis=1)
    err=np.max(np.abs(d["total_ci"]-d["active_richness"]-d["excess_intensity"]))
    if err>1e-12:
        raise RuntimeError(f"decomposition identity failed: {err}")
    d["event_date"]=[x.date() for x in d["local_dt"]]
    d["event_hour"]=[x.hour+x.minute/60+x.second/3600 for x in d["local_dt"]]
    d["year"]=[x.year for x in d["local_dt"]]
    d["month"]=[x.month for x in d["local_dt"]]
    return d,spp,raw


def era5_dry_days(event_dates):
    cell_lat=round(LAT*4.0)/4.0
    cell_lon=round(LON*4.0)/4.0
    storage=icechunk.s3_storage(
        bucket="earthmover-icechunk-era5",
        prefix="icechunkV2",
        region="us-east-1",
        anonymous=True,
    )
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    tp=ds["tp"]
    attrs=tp.attrs
    if attrs.get("GRIB_paramId") not in (228,"228") or str(attrs.get("units"))!="m":
        raise RuntimeError("ERA5 tp identity drift")
    if "1 hour" not in str(attrs.get("accumulation_comment","")):
        raise RuntimeError("ERA5 tp accumulation semantics drift")

    lats=np.asarray(ds.latitude.values,float)
    lons=np.asarray(ds.longitude.values,float)
    yi=int(np.abs(lats-cell_lat).argmin())
    lon360=cell_lon%360.0
    xi=int(np.abs(lons-lon360).argmin())
    if abs(lats[yi]-cell_lat)>0.126 or abs(lons[xi]-lon360)>0.126:
        raise RuntimeError("ERA5 cell mismatch")

    mind=min(event_dates)-timedelta(days=DRY_CAP+2)
    maxd=max(event_dates)
    start=np.datetime64(mind.isoformat()+"T00:00")
    end=np.datetime64((maxd+timedelta(days=1)).isoformat()+"T23:00")
    times=np.asarray(ds.valid_time.values)
    t0=max(0,int(np.searchsorted(times,start,side="left")))
    t1=min(len(times),int(np.searchsorted(times,end,side="right")))
    arr=np.asarray(tp.isel(valid_time=slice(t0,t1),latitude=yi,longitude=xi).values,dtype=np.float64).reshape(-1)
    if not np.isfinite(arr).all():
        raise RuntimeError("nonfinite ERA5 values")
    if float(arr.min()) < -1e-8:
        raise RuntimeError("ERA5 negative precipitation outside tolerance")
    arr[arr<0]=0.0
    mm=arr*1000.0
    utc_mid=pd.DatetimeIndex(times[t0:t1]).tz_localize("UTC")-pd.Timedelta(minutes=30)
    local_dates=np.asarray(utc_mid.tz_convert(TZ).date,dtype="datetime64[D]")
    unique,inverse=np.unique(local_dates,return_inverse=True)
    sums=np.bincount(inverse,weights=mm,minlength=len(unique))
    daily={date.fromisoformat(str(d)):float(v) for d,v in zip(unique,sums)}

    dry=[]
    for ed in event_dates:
        n=0
        for off in range(1,DRY_CAP+1):
            dd=ed-timedelta(days=off)
            if dd not in daily:
                raise RuntimeError(f"missing daily rain {dd}")
            if daily[dd]>=WET_MM:
                break
            n+=1
        dry.append(n)

    h=hashlib.sha256()
    for d in sorted(daily):
        h.update(f"{d.isoformat()},{daily[d]:.8f}\n".encode())
    return dry,{
        "provider":"Earthmover public Icechunk ERA5",
        "cell_requested":[cell_lat,cell_lon],
        "cell_actual":[float(lats[yi]),float(((lons[xi]+180)%360)-180)],
        "required_daily_weather_sha256":h.hexdigest(),
        "hourly_values_read":int(len(arr)),
        "daily_range":[min(daily).isoformat(),max(daily).isoformat()],
    }


def fit(df,response):
    formula=f"{response} ~ dry_z + C(month) + year_z + sin_hour + cos_hour"
    model=smf.ols(formula,data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups":df["event_date"].astype(str)},
    )
    b=float(model.params["dry_z"]); se=float(model.bse["dry_z"]); p=float(model.pvalues["dry_z"])
    return {
        "response":response,
        "formula":formula,
        "n_recordings":int(len(df)),
        "n_dates":int(df["event_date"].nunique()),
        "beta_dry_z":b,
        "se_date_cluster":se,
        "ci95":[b-Q*se,b+Q*se],
        "p_value":p,
    }


def package(df):
    models={x:fit(df,x) for x in ("total_ci","active_richness","excess_intensity")}
    bt=models["total_ci"]["beta_dry_z"]
    br=models["active_richness"]["beta_dry_z"]
    be=models["excess_intensity"]["beta_dry_z"]
    identity=float(bt-br-be)
    share=float(br/bt) if abs(bt)>1e-12 else None
    total_support=bool(bt<0 and models["total_ci"]["ci95"][1]<0)
    richness_support=bool(br<0 and models["active_richness"]["ci95"][1]<0)
    threshold=bool(
        total_support and richness_support and share is not None
        and share>0.5 and abs(br)>abs(be)
    )
    return {
        "models":models,
        "beta_identity_error":identity,
        "active_richness_share_of_total_dry_slope":share,
        "classification":{
            "recent_rain_total_activity":total_support,
            "recruitment_component":richness_support,
            "threshold_dominant":threshold,
        },
    }


def main():
    df,spp,raw=parse_weak()
    dry,era5=era5_dry_days(df["event_date"].tolist())
    df["dry_days"]=dry
    df["log1p_dry"]=np.log1p(df["dry_days"].astype(float))
    df["dry_z"],dry_mu,dry_sd=zscore(df["log1p_dry"])
    df["year_z"],year_mu,year_sd=zscore(df["year"].astype(float))
    rad=2*np.pi*df["event_hour"].astype(float)/24
    df["sin_hour"]=np.sin(rad); df["cos_hour"]=np.cos(rad)

    primary=package(df)
    active=package(df[df["total_ci"]>0].copy())

    reduced=df.copy()
    reduced["hour_bin"]=np.floor(reduced["event_hour"]).astype(int)
    reduced=reduced.sort_values("AUDIO_FILE_ID").drop_duplicates(["event_date","hour_bin"],keep="first").copy()
    reduced_diag=package(reduced)

    per_month=df.groupby(["year","month"]).size().reset_index(name="n")
    output={
        "analysis":"anuraset_inct20955_rainfall_threshold_replication_v0_1",
        "contract":"exploration/ANURASET_RAINFALL_REPLICATION_CONTRACT_V0_1.json",
        "source":{
            "weak_labels_md5":hashlib.md5(raw).hexdigest(),
            "site":SITE,
            "coordinate":[LAT,LON],
            "timezone":"America/Sao_Paulo",
            "species_columns":len(spp),
        },
        "coverage":{
            "recordings":int(len(df)),
            "dates":int(df["event_date"].nunique()),
            "date_range":[min(df["event_date"]).isoformat(),max(df["event_date"]).isoformat()],
            "zero_anuran_recordings":int((df["total_ci"]==0).sum()),
            "months":per_month.to_dict(orient="records"),
        },
        "era5":era5,
        "dryness":{
            "dry_days_histogram":{str(k):int(v) for k,v in sorted(Counter(df["dry_days"]).items())},
            "log1p_mean":dry_mu,"log1p_sd":dry_sd,
        },
        "primary_all_annotated_recordings":primary,
        "sensitivity_active_recordings_only":active,
        "sensitivity_one_recording_per_date_hour":reduced_diag,
        "interpretation_boundary":{
            "annotation_sample_is_stratified_not_continuous_effort":True,
            "spatial_boundary_replication":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        },
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
