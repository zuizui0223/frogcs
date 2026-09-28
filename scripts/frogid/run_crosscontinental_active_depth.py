#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import icechunk
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import xarray as xr
from timezonefinder import TimezoneFinder

FROGID_URL="https://dwca-exports.ala.org.au/dr14760.zip"
FROGID_SHA="f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d"
NS={"dwc":"http://rs.tdwg.org/dwc/text/"}

TIME_CHUNK=8736
LAT_CHUNK=12
LON_CHUNK=12
WET_MM=1.0
DRY_CAP=30
NEG_TOL_M=-1e-8
EXPECTED_N=40754
EXPECTED_MULTI=18174
EXPECTED_CELLS=1623
EXPECTED_CHUNKS=470


def fetch_bytes(url: str, timeout: int=180) -> bytes:
    req=urllib.request.Request(
        url,
        headers={
            "User-Agent":"frogid-chorus-synchrony-earthmover-validation/0.1",
            "Accept":"application/json,*/*",
        },
    )
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read()


def local_term(term: str) -> str:
    return term.rsplit("/",1)[-1].rsplit("#",1)[-1] if term else ""


def decode_sep(value: str|None, default: str) -> str:
    if value is None:
        return default
    return bytes(value,"utf-8").decode("unicode_escape")


def core_rows(zf: zipfile.ZipFile):
    meta=ET.fromstring(zf.read("meta.xml"))
    core=meta.find("dwc:core",NS)
    if core is None:
        raise RuntimeError("DwC-A missing core")
    files=core.find("dwc:files",NS)
    loc=files.find("dwc:location",NS) if files is not None else None
    if loc is None or not loc.text:
        raise RuntimeError("DwC-A core missing location")
    fields={
        local_term(f.attrib.get("term","")):int(f.attrib["index"])
        for f in core.findall("dwc:field",NS)
    }
    delim=decode_sep(core.attrib.get("fieldsTerminatedBy"),"\t")
    quote=decode_sep(core.attrib.get("fieldsEnclosedBy"),'"')
    ignore=int(core.attrib.get("ignoreHeaderLines","0"))
    enc=core.attrib.get("encoding","UTF-8").replace("-","")
    reader=csv.reader(
        io.StringIO(zf.read(loc.text.strip()).decode(enc,errors="replace")),
        delimiter=delim,
        quotechar=quote or '"',
    )
    for _ in range(ignore):
        next(reader,None)
    return fields,reader


def get(row,fields,name):
    i=fields.get(name)
    return row[i].strip() if i is not None and i<len(row) else ""


def selected(event_id: str) -> bool:
    return hashlib.sha256(event_id.encode("utf-8")).digest()[0] < 16


def grid_cell(v: float) -> float:
    return round(v*4.0)/4.0


def parse_date(raw: str) -> date:
    return date.fromisoformat(str(raw or "").strip()[:10])


def parse_hour(raw: str) -> float:
    m=re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}(?:\.\d+)?))?",str(raw or "").strip())
    if not m:
        raise ValueError(raw)
    h=int(m.group(1))+int(m.group(2))/60.0
    if m.group(3):
        h+=float(m.group(3))/3600.0
    if not 0<=h<24:
        raise ValueError(raw)
    return h


def parse_aware_event_datetime(event_date, event_time: str) -> datetime:
    d=event_date.isoformat() if hasattr(event_date,"isoformat") else str(event_date).strip()[:10]
    t=str(event_time or "").strip()
    s=t if "T" in t else f"{d}T{t}"
    if s.endswith("Z"):
        s=s[:-1]+"+00:00"
    dt=datetime.fromisoformat(s)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"eventTime lacks explicit offset: {event_time!r}")
    return dt


def load_frogid_sample():
    data=fetch_bytes(FROGID_URL)
    if hashlib.sha256(data).hexdigest()!=FROGID_SHA:
        raise RuntimeError("FrogID hash drift")
    zf=zipfile.ZipFile(io.BytesIO(data))
    fields,reader=core_rows(zf)
    required={
        "eventID","scientificName","eventDate","eventTime",
        "decimalLatitude","decimalLongitude","coordinateUncertaintyInMeters",
        "stateProvince","recordedBy",
    }
    missing=required-set(fields)
    if missing:
        raise RuntimeError(f"missing fields {sorted(missing)}")

    events={}
    event_species=defaultdict(set)
    for row in reader:
        eid=get(row,fields,"eventID")
        if not eid or not selected(eid):
            continue
        sp=get(row,fields,"scientificName")
        if sp:
            event_species[eid].add(sp)
        if eid in events:
            continue
        try:
            lat=float(get(row,fields,"decimalLatitude"))
            lon=float(get(row,fields,"decimalLongitude"))
            unc=float(get(row,fields,"coordinateUncertaintyInMeters"))
        except Exception:
            continue
        if not(-90<=lat<=90 and -180<=lon<=180):
            continue
        if not math.isfinite(unc) or unc>25000:
            continue

        raw_date=get(row,fields,"eventDate")
        raw_time=get(row,fields,"eventTime")
        state=get(row,fields,"stateProvince")
        recorder=get(row,fields,"recordedBy")
        if not raw_date or not raw_time or not state or not recorder:
            continue
        try:
            d=parse_date(raw_date)
            parse_aware_event_datetime(d,raw_time)
        except Exception:
            continue

        events[eid]={
            "eventID":eid,
            "event_date":d,
            "event_time_raw":raw_time,
            "state":state,
            "recorder":recorder,
            "uncertainty_m":unc,
            "lat":lat,
            "lon":lon,
            "cell_lat":grid_cell(lat),
            "cell_lon":grid_cell(lon),
        }

    rows=[]
    for eid,meta in events.items():
        richness=len(event_species.get(eid,set()))
        if richness<1:
            continue
        rows.append({
            **meta,
            "richness":richness,
            "multi":int(richness>=2),
            "year":meta["event_date"].year,
            "month":meta["event_date"].month,
            "cell_id":f"{meta['cell_lat']:.2f},{meta['cell_lon']:.2f}",
        })
    df=pd.DataFrame(rows)
    if len(df)!=EXPECTED_N:
        raise RuntimeError(f"frozen sample drift {len(df)} != {EXPECTED_N}")
    if int(df.multi.sum())!=EXPECTED_MULTI:
        raise RuntimeError("multi-species count drift")
    if int(df.cell_id.nunique())!=EXPECTED_CELLS:
        raise RuntimeError("weather cell count drift")
    return df


def zscore(values):
    x=np.asarray(values,dtype=float)
    mean=float(np.mean(x)); sd=float(np.std(x,ddof=0))
    if not math.isfinite(sd) or sd==0:
        raise RuntimeError("invalid z-score SD")
    return (x-mean)/sd,mean,sd


def fit_model(df: pd.DataFrame, cluster_col: str):
    formula="multi ~ dry_z + C(state) * C(month) + year_z + sin_hour + cos_hour"
    model=smf.glm(formula,data=df,family=sm.families.Binomial())
    fitted=model.fit(
        cov_type="cluster",
        cov_kwds={"groups":df[cluster_col]},
        maxiter=100,
    )
    b=float(fitted.params["dry_z"])
    se=float(fitted.bse["dry_z"])
    p=float(fitted.pvalues["dry_z"])
    q=1.959963984540054
    lo=b-q*se; hi=b+q*se
    return {
        "n_recordings":int(len(df)),
        "multi_species_recordings":int(df.multi.sum()),
        "n_clusters":int(df[cluster_col].nunique()),
        "formula":formula,
        "cluster":cluster_col,
        "beta":b,
        "se_cluster":se,
        "ci95_beta":[lo,hi],
        "odds_ratio_per_sd_log1p_dry_days":math.exp(b),
        "ci95_or":[math.exp(lo),math.exp(hi)],
        "p_value":p,
        "support_rule_pass":bool(b<0 and p<0.05 and hi<0),
    }


def fit_within_cell(df: pd.DataFrame):
    d=df.copy()
    month=pd.get_dummies(d["month"].astype(int),prefix="month",drop_first=True,dtype=float)
    X=pd.DataFrame({
      "dry_z":d["dry_z"].astype(float),
      "year_z":d["year_z"].astype(float),
      "sin_hour":d["sin_hour"].astype(float),
      "cos_hour":d["cos_hour"].astype(float),
    },index=d.index)
    X=pd.concat([X,month.set_axis(d.index)],axis=1)
    d["_y"]=d["multi"].astype(float)

    stats=d.groupby("cell_id").agg(n=("_y","size"),dry_min=("dry_z","min"),dry_max=("dry_z","max"))
    good=stats[(stats.n>=2) & ((stats.dry_max-stats.dry_min)>1e-12)].index
    d=d[d.cell_id.isin(good)].copy()
    X=X.loc[d.index].copy()

    groups=d["cell_id"].astype(str)
    y=d["_y"]-d.groupby("cell_id")["_y"].transform("mean")
    Xw=pd.DataFrame(index=d.index)
    for col in X.columns:
        vals=X[col].astype(float)
        Xw[col]=vals-vals.groupby(groups).transform("mean")

    fit=sm.OLS(y.astype(float),Xw.astype(float)).fit(cov_type="cluster",cov_kwds={"groups":groups})
    b=float(fit.params["dry_z"]); se=float(fit.bse["dry_z"]); p=float(fit.pvalues["dry_z"])
    q=1.959963984540054; lo=b-q*se; hi=b+q*se
    return {
      "n_recordings":int(len(d)),
      "multi_species_recordings":int(d.multi.sum()),
      "informative_weather_cells":int(d.cell_id.nunique()),
      "estimator":"within-ERA5-cell fixed-effects linear probability diagnostic",
      "beta_dry_within_probability_scale":b,
      "se_cell_cluster":se,
      "ci95_beta":[lo,hi],
      "p_value":p,
      "direction_negative":bool(b<0),
      "ci_excludes_zero_negative":bool(hi<0),
    }



def fit_depth_ols(df: pd.DataFrame, response: str, cluster_col: str):
    formula=f"{response} ~ dry_z + C(state) * C(month) + year_z + sin_hour + cos_hour"
    fit=smf.ols(formula,data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups":df[cluster_col]},
    )
    b=float(fit.params["dry_z"])
    se=float(fit.bse["dry_z"])
    p=float(fit.pvalues["dry_z"])
    q=1.959963984540054
    lo=b-q*se; hi=b+q*se
    return {
        "response":response,
        "n_recordings":int(len(df)),
        "n_clusters":int(df[cluster_col].nunique()),
        "formula":formula,
        "cluster":cluster_col,
        "beta_dry_z":b,
        "se_cluster":se,
        "ci95_beta":[lo,hi],
        "p_value":p,
        "support_negative_ci":bool(b<0 and hi<0),
    }


def fit_threeplus_logit(df: pd.DataFrame):
    formula="threeplus ~ dry_z + C(state) * C(month) + year_z + sin_hour + cos_hour"
    fit=smf.glm(formula,data=df,family=sm.families.Binomial()).fit(
        cov_type="cluster",
        cov_kwds={"groups":df["cell_id"]},
        maxiter=100,
    )
    b=float(fit.params["dry_z"])
    se=float(fit.bse["dry_z"])
    p=float(fit.pvalues["dry_z"])
    q=1.959963984540054
    lo=b-q*se; hi=b+q*se
    return {
        "response":"threeplus",
        "n_recordings":int(len(df)),
        "n_threeplus":int(df.threeplus.sum()),
        "n_clusters":int(df.cell_id.nunique()),
        "formula":formula,
        "cluster":"cell_id",
        "beta_dry_z":b,
        "se_cluster":se,
        "ci95_beta":[lo,hi],
        "odds_ratio_per_sd_log1p_dry_days":math.exp(b),
        "ci95_or":[math.exp(lo),math.exp(hi)],
        "p_value":p,
        "direction_negative":bool(b<0),
    }


def fit_within_cell_depth(df: pd.DataFrame):
    d=df.copy()
    month=pd.get_dummies(d["month"].astype(int),prefix="month",drop_first=True,dtype=float)
    X=pd.DataFrame({
      "dry_z":d["dry_z"].astype(float),
      "year_z":d["year_z"].astype(float),
      "sin_hour":d["sin_hour"].astype(float),
      "cos_hour":d["cos_hour"].astype(float),
    },index=d.index)
    X=pd.concat([X,month.set_axis(d.index)],axis=1)
    d["_y"]=d["excess_richness"].astype(float)

    stats=d.groupby("cell_id").agg(
        n=("_y","size"),
        dry_min=("dry_z","min"),
        dry_max=("dry_z","max")
    )
    good=stats[(stats.n>=2) & ((stats.dry_max-stats.dry_min)>1e-12)].index
    d=d[d.cell_id.isin(good)].copy()
    X=X.loc[d.index].copy()

    groups=d["cell_id"].astype(str)
    y=d["_y"]-d.groupby("cell_id")["_y"].transform("mean")
    Xw=pd.DataFrame(index=d.index)
    for col in X.columns:
        vals=X[col].astype(float)
        Xw[col]=vals-vals.groupby(groups).transform("mean")

    fit=sm.OLS(y.astype(float),Xw.astype(float)).fit(
        cov_type="cluster",
        cov_kwds={"groups":groups}
    )
    b=float(fit.params["dry_z"])
    se=float(fit.bse["dry_z"])
    p=float(fit.pvalues["dry_z"])
    q=1.959963984540054
    lo=b-q*se; hi=b+q*se
    return {
      "response":"excess_richness",
      "n_recordings":int(len(d)),
      "informative_weather_cells":int(d.cell_id.nunique()),
      "estimator":"within-ERA5-cell fixed-effects OLS on active-unit excess richness",
      "beta_dry_z":b,
      "se_cell_cluster":se,
      "ci95_beta":[lo,hi],
      "p_value":p,
      "support_negative_ci":bool(b<0 and hi<0),
    }


def main():
    df=load_frogid_sample()

    tf=TimezoneFinder(in_memory=True)
    tz_cache={}
    event_tz=[]
    for r in df.itertuples(index=False):
        key=(float(r.lat),float(r.lon))
        if key not in tz_cache:
            tz=tf.timezone_at(lng=key[1],lat=key[0])
            if not tz:
                raise RuntimeError(f"timezone unresolved {key}")
            tz_cache[key]=tz
        event_tz.append(tz_cache[key])
    df=df.copy()
    df["timezone"]=event_tz

    # Frozen timezone-aware repair: use the represented instant converted to
    # the coordinate-derived timezone for both event date and cyclic hour.
    repaired_dates=[]
    repaired_hours=[]
    hour_changed=0
    date_changed=0
    for r in df.itertuples(index=False):
        dt=parse_aware_event_datetime(r.event_date,r.event_time_raw)
        local=dt.astimezone(ZoneInfo(str(r.timezone)))
        raw_hour=parse_hour(r.event_time_raw)
        local_hour=local.hour+local.minute/60.0+local.second/3600.0+local.microsecond/3.6e9
        diff=abs(raw_hour-local_hour)%24.0
        diff=min(diff,24.0-diff)
        if diff>1e-9:
            hour_changed+=1
        if local.date()!=r.event_date:
            date_changed+=1
        repaired_dates.append(local.date())
        repaired_hours.append(local_hour)

    df["event_date"]=repaired_dates
    df["event_hour"]=repaired_hours
    df["year"]=[d.year for d in repaired_dates]
    df["month"]=[d.month for d in repaired_dates]

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
    if attrs.get("GRIB_paramId") not in (228,"228"):
        raise RuntimeError("tp parameter identity drift")
    if str(attrs.get("units"))!="m":
        raise RuntimeError("tp units drift")
    if "1 hour" not in str(attrs.get("accumulation_comment","")):
        raise RuntimeError("tp accumulation semantics drift")

    lats=np.asarray(ds.latitude.values,dtype=float)
    lons=np.asarray(ds.longitude.values,dtype=float)
    times=np.asarray(ds.valid_time.values)

    cell_indices={}
    for r in df.itertuples(index=False):
        key=(float(r.cell_lat),float(r.cell_lon))
        if key in cell_indices:
            continue
        yi=int(np.abs(lats-key[0]).argmin())
        lon360=key[1]%360.0
        xi=int(np.abs(lons-lon360).argmin())
        if abs(lats[yi]-key[0])>0.126 or abs(lons[xi]-lon360)>0.126:
            raise RuntimeError(f"ERA5 nearest-cell mismatch {key}")
        cell_indices[key]=(yi,xi)

    needed_dates=defaultdict(set)
    chunk_requirements=defaultdict(set)

    for r in df.itertuples(index=False):
        cell=(float(r.cell_lat),float(r.cell_lon))
        combo=(cell[0],cell[1],str(r.timezone))
        for off in range(1,DRY_CAP+1):
            needed_dates[combo].add(r.event_date-timedelta(days=off))

        yi,xi=cell_indices[cell]
        start=np.datetime64(r.event_date-timedelta(days=32),"h")
        end=np.datetime64(r.event_date+timedelta(days=1),"h")
        i0=int(np.searchsorted(times,start,side="left"))
        i1=max(i0,int(np.searchsorted(times,end,side="right")-1))
        i0=max(0,i0); i1=min(len(times)-1,i1)
        for tc in range(i0//TIME_CHUNK,i1//TIME_CHUNK+1):
            chunk_requirements[(tc,yi//LAT_CHUNK,xi//LON_CHUNK)].add(combo)

    if len(chunk_requirements)>480:
        raise RuntimeError(f"repaired chunk footprint exceeds frozen maximum: {len(chunk_requirements)} > 480")

    # Only the daily values actually needed by retained events are kept.
    daily=defaultdict(float)
    normalized_hash=hashlib.sha256()
    local_date_cache={}
    chunk_min=math.inf
    chunk_max=-math.inf
    hourly_values_read=0

    for chunk_no,cid in enumerate(sorted(chunk_requirements),start=1):
        tc,yc,xc=cid
        t0=tc*TIME_CHUNK; t1=min((tc+1)*TIME_CHUNK,len(times))
        y0=yc*LAT_CHUNK; y1=min((yc+1)*LAT_CHUNK,len(lats))
        x0=xc*LON_CHUNK; x1=min((xc+1)*LON_CHUNK,len(lons))

        arr=np.asarray(
            tp.isel(
                valid_time=slice(t0,t1),
                latitude=slice(y0,y1),
                longitude=slice(x0,x1),
            ).values,
            dtype=np.float64,
        )
        if arr.shape!=(t1-t0,y1-y0,x1-x0):
            raise RuntimeError(f"chunk shape mismatch {cid}: {arr.shape}")
        if not np.isfinite(arr).all():
            raise RuntimeError(f"nonfinite tp in required chunk {cid}")
        amin=float(arr.min()); amax=float(arr.max())
        chunk_min=min(chunk_min,amin); chunk_max=max(chunk_max,amax)
        if amin<NEG_TOL_M:
            raise RuntimeError(f"tp below frozen negative tolerance {cid}: {amin}")
        if amin<0:
            arr[arr<0]=0.0
        hourly_values_read+=int(arr.size)

        utc_mid=pd.DatetimeIndex(times[t0:t1]).tz_localize("UTC")-pd.Timedelta(minutes=30)

        for lat,lon,tzname in sorted(chunk_requirements[cid]):
            yi,xi=cell_indices[(lat,lon)]
            vals=arr[:,yi-y0,xi-x0]*1000.0
            cache_key=(tc,tzname)
            if cache_key not in local_date_cache:
                local_dates=np.asarray(
                    utc_mid.tz_convert(ZoneInfo(tzname)).date,
                    dtype="datetime64[D]",
                )
                local_date_cache[cache_key]=local_dates
            else:
                local_dates=local_date_cache[cache_key]

            unique_days,inverse=np.unique(local_dates,return_inverse=True)
            sums=np.bincount(inverse,weights=vals,minlength=len(unique_days))
            wanted=needed_dates[(lat,lon,tzname)]
            for d64,total in zip(unique_days,sums):
                d=date.fromisoformat(str(d64))
                if d in wanted:
                    daily[(lat,lon,tzname,d)]+=float(total)

    dry=[]
    for r in df.itertuples(index=False):
        combo=(float(r.cell_lat),float(r.cell_lon),str(r.timezone))
        n=0
        for off in range(1,DRY_CAP+1):
            d=r.event_date-timedelta(days=off)
            key=(*combo,d)
            if key not in daily:
                raise RuntimeError(f"missing required local daily precipitation {key}")
            p=float(daily[key])
            if not math.isfinite(p) or p<0:
                raise RuntimeError(f"invalid daily precipitation {key}: {p}")
            if p>=WET_MM:
                break
            n+=1
        dry.append(n)

    # Hash only required daily exposure values in canonical order.
    for key in sorted(daily,key=lambda x:(x[0],x[1],x[2],x[3].isoformat())):
        p=daily[key]
        normalized_hash.update(
            f"{key[0]:.2f},{key[1]:.2f},{key[2]},{key[3].isoformat()},{p:.8f}\\n".encode()
        )

    df["dry_days"]=dry
    df["log1p_dry"]=np.log1p(df.dry_days.astype(float))
    df["dry_z"],dry_mean,dry_sd=zscore(df.log1p_dry)
    df["year_z"],year_mean,year_sd=zscore(df.year.astype(float))
    rad=2.0*math.pi*df.event_hour.astype(float)/24.0
    df["sin_hour"]=np.sin(rad)
    df["cos_hour"]=np.cos(rad)

    df["excess_richness"]=df.richness.astype(float)-1.0
    df["threeplus"]=(df.richness.astype(int)>=3).astype(int)
    df["excess_beyond_two"]=np.maximum(df.richness.astype(float)-2.0,0.0)

    required=[
        "richness","excess_richness","threeplus","excess_beyond_two",
        "dry_z","state","month","year_z","sin_hour","cos_hour",
        "cell_id","recorder","uncertainty_m",
    ]
    if df[required].isna().any().any():
        raise RuntimeError("missing modeled value after frozen construction")
    if float(df.excess_richness.min())<0:
        raise RuntimeError("active-unit excess richness must be nonnegative")

    primary=fit_depth_ols(df,"excess_richness","cell_id")
    recorder=fit_depth_ols(df,"excess_richness","recorder")
    within_cell=fit_within_cell_depth(df)
    secondary_threeplus=fit_threeplus_logit(df)
    secondary_excess_two=fit_depth_ols(df,"excess_beyond_two","cell_id")

    dry_hist=Counter(int(x) for x in df.dry_days)
    timezone_counts=Counter(df.timezone.astype(str))

    naamp={
        "system":"NAAMP",
        "response":"mean species richness per active stop; excess richness = alpha_active - 1",
        "source":"provenance/summaries/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json",
        "rainfall_contrast_beta":0.07941491576879688,
        "ci95":[0.023119819091079956,0.1357100124465138],
        "support_positive_ci":True,
    }
    australia_primary_pass=bool(primary["support_negative_ci"])
    australia_strong_pass=bool(
        primary["support_negative_ci"]
        and recorder["support_negative_ci"]
        and within_cell["support_negative_ci"]
    )
    cross_pass=bool(naamp["support_positive_ci"] and australia_primary_pass)
    cross_strong=bool(naamp["support_positive_ci"] and australia_strong_pass)

    result={
        "analysis":"crosscontinental_active_unit_taxonomic_depth_v0_1",
        "contract":"provenance/contracts/CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json",
        "unfreeze":"provenance/submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json",
        "frogid_source_sha256":FROGID_SHA,
        "era5_source":{
            "provider":"Earthmover public Icechunk ERA5",
            "bucket":"earthmover-icechunk-era5",
            "prefix":"icechunkV2",
            "branch":"main",
            "group":"single/temporal",
            "variable":"tp",
            "units":"m",
            "accumulation":"1 hour ending at valid_time",
            "chunks_read":len(chunk_requirements),
            "hourly_grid_values_read":hourly_values_read,
            "required_daily_weather_sha256":normalized_hash.hexdigest(),
            "required_tp_min_m_before_small_negative_clamp":chunk_min,
            "required_tp_max_m":chunk_max,
        },
        "frozen_sample":{
            "recordings":int(len(df)),
            "multi_species_recordings":int(df.multi.sum()),
            "threeplus_recordings":int(df.threeplus.sum()),
            "weather_cells":int(df.cell_id.nunique()),
            "recorders":int(df.recorder.nunique()),
            "timezones":dict(sorted(timezone_counts.items())),
            "mean_species_richness":float(df.richness.mean()),
            "mean_excess_richness":float(df.excess_richness.mean()),
        },
        "exposure":{
            "dry_days_histogram":{str(k):int(v) for k,v in sorted(dry_hist.items())},
            "log1p_dry_mean":dry_mean,
            "log1p_dry_sd":dry_sd,
            "calendar_year_mean":year_mean,
            "calendar_year_sd":year_sd,
        },
        "north_america_frozen":naamp,
        "australia":{
            "primary_continuous_depth":primary,
            "sensitivities":{
                "recorder_cluster":recorder,
                "within_cell":within_cell,
            },
            "secondary_no_gate":{
                "threeplus":secondary_threeplus,
                "excess_beyond_two":secondary_excess_two,
            },
        },
        "cross_system_decision":{
            "pass":cross_pass,
            "strong_pass":cross_strong,
            "authorized_wording":(
                "cross-continental consistency in rainfall-associated taxonomic deepening within already-active acoustic units"
                if cross_pass else
                "no cross-continental taxonomic-deepening claim authorized"
            ),
            "worldwide_universality_authorized":False,
            "pooled_effect_size_authorized":False,
        },
        "time_alignment_repair":{
            "contract":"provenance/contracts/FROGID_TIMEZONE_REPAIR_CONTRACT_V0_1.json",
            "events_with_hour_changed":hour_changed,
            "events_with_date_changed":date_changed,
            "required_unique_tp_chunks":len(chunk_requirements),
        },
        "naamp_primary_replaced":False,
        "historical_two_plus_result_replaced":False,
        "causal_claim_authorized":False,
        "worldwide_generality_claim_authorized":False,
        "post_opening_retuning_performed":False,
    }

    ds.close()
    out=Path("CROSSCONTINENTAL_ACTIVE_DEPTH_RECEIPT_V0_1.json")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
