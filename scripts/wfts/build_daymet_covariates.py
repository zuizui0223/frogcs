#!/usr/bin/env python3
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DAYMET_DOI="10.3334/ORNLDAAC/2129"
API_BASE="https://daymet.ornl.gov/single-pixel/api/data"
VARS=("prcp","tmin","tmax")
THRESHOLD_MM=1.0
DRY_CAP=30

STRUCT_COLS=[
    "route_id","survey_period","survey_year","survey_date",
    "station_order","physical_site_id","latitude","longitude",
]
FORBIDDEN_TOKENS=(
    "taxon","species","call_index","calling","richness",
    "concentration","occupancy","presence","absence",
)


def sha256_bytes(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def daymet_calendar_dates(year: int) -> list[pd.Timestamp]:
    start=pd.Timestamp(year=year,month=1,day=1)
    end=pd.Timestamp(year=year,month=12,day=31)
    dates=list(pd.date_range(start,end,freq="D"))
    if calendar.isleap(year):
        dates=[d for d in dates if not (d.month==12 and d.day==31)]
    if len(dates)!=365:
        raise RuntimeError(f"Daymet calendar reconstruction failed for {year}: {len(dates)}")
    return dates


def normalize_col(name: str) -> str:
    x=name.strip().lower()
    x=re.sub(r"\s*\([^)]*\)\s*","",x)
    x=re.sub(r"[^a-z0-9]+","_",x).strip("_")
    return x


def parse_daymet_csv(raw: bytes) -> pd.DataFrame:
    text=raw.decode("utf-8-sig")
    lines=text.splitlines()
    # Daymet may prepend metadata comments. Find first comma-delimited header
    # containing year and yday.
    header_idx=None
    for i,line in enumerate(lines):
        low=line.lower()
        if "," in line and "year" in low and "yday" in low:
            header_idx=i
            break
    if header_idx is None:
        raise RuntimeError("Daymet CSV header with year/yday not found")

    df=pd.read_csv(io.StringIO("\n".join(lines[header_idx:])))
    df.columns=[normalize_col(c) for c in df.columns]

    # Accept unit-suffixed names after normalization by prefix.
    rename={}
    for col in df.columns:
        if col=="year" or col.startswith("year_"):
            rename[col]="year"
        elif col=="yday" or col.startswith("yday_"):
            rename[col]="yday"
        elif col=="prcp" or col.startswith("prcp_"):
            rename[col]="prcp"
        elif col=="tmin" or col.startswith("tmin_"):
            rename[col]="tmin"
        elif col=="tmax" or col.startswith("tmax_"):
            rename[col]="tmax"
    df=df.rename(columns=rename)

    required={"year","yday","prcp","tmin","tmax"}
    if not required<=set(df.columns):
        raise RuntimeError(f"Daymet CSV missing variables: {sorted(required-set(df.columns))}")

    df=df[list(required)].copy()
    for col in required:
        df[col]=pd.to_numeric(df[col],errors="raise")
    df["year"]=df["year"].astype(int)
    df["yday"]=df["yday"].astype(int)

    chunks=[]
    for year,g in df.groupby("year",sort=True):
        g=g.sort_values("yday").reset_index(drop=True)
        if len(g)!=365 or g.yday.tolist()!=list(range(1,366)):
            raise RuntimeError(f"Daymet year {year} is not complete yday 1..365")
        gg=g.copy()
        gg["date"]=daymet_calendar_dates(int(year))
        chunks.append(gg)
    out=pd.concat(chunks,ignore_index=True)
    if out.date.duplicated().any():
        raise RuntimeError("duplicate reconstructed Daymet dates")
    return out.sort_values("date").reset_index(drop=True)


def build_url(lat: float, lon: float, years: list[int]) -> str:
    params={
        "lat":f"{float(lat):.6f}",
        "lon":f"{float(lon):.6f}",
        "vars":",".join(VARS),
        "years":",".join(str(int(y)) for y in sorted(set(years))),
    }
    return API_BASE+"?"+urllib.parse.urlencode(params,safe=",")


def fetch_url(url: str, timeout: int=120) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-wfts-prospective-replication/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as resp:
        return resp.read()


def station_exposure(daymet: pd.DataFrame, survey_date: pd.Timestamp) -> tuple[int,float]:
    by_date=daymet.set_index("date")
    d=pd.Timestamp(survey_date).normalize()
    if d not in by_date.index:
        raise RuntimeError(f"survey date missing in Daymet data: {d.date()}")

    today=by_date.loc[d]
    tmean=(float(today["tmin"])+float(today["tmax"]))/2.0

    dry=0
    for lag in range(1,DRY_CAP+1):
        q=d-pd.Timedelta(days=lag)
        if q not in by_date.index:
            raise RuntimeError(f"required prior Daymet date missing: {q.date()}")
        prcp=float(by_date.loc[q,"prcp"])
        if not np.isfinite(prcp):
            raise RuntimeError(f"nonfinite Daymet precipitation: {q.date()}")
        if prcp>=THRESHOLD_MM:
            break
        dry+=1
    return int(dry),float(tmean)


def validate_structure(path: Path) -> pd.DataFrame:
    header=pd.read_csv(path,nrows=0)
    lower={c.lower():c for c in header.columns}
    for token in FORBIDDEN_TOKENS:
        if any(token in c.lower() for c in header.columns):
            raise RuntimeError(f"response-like column forbidden in weather input: {token}")

    missing=[c for c in STRUCT_COLS if c not in header.columns]
    if missing:
        raise RuntimeError(f"structural weather input missing columns: {missing}")

    x=pd.read_csv(path,usecols=STRUCT_COLS)
    x["route_id"]=x.route_id.astype(str)
    x["survey_period"]=x.survey_period.astype(str)
    x["survey_year"]=x.survey_year.astype(int)
    x["survey_date"]=pd.to_datetime(x.survey_date,errors="raise").dt.normalize()
    x["station_order"]=x.station_order.astype(int)
    x["physical_site_id"]=x.physical_site_id.astype(str)
    x["latitude"]=pd.to_numeric(x.latitude,errors="raise")
    x["longitude"]=pd.to_numeric(x.longitude,errors="raise")

    if not set(x.station_order.unique())<=set(range(1,11)):
        raise RuntimeError("station_order outside 1..10")

    key=["route_id","survey_period","survey_year"]
    counts=x.groupby(key).station_order.nunique()
    if (counts!=10).any():
        raise RuntimeError("each route-period-year must have exactly 10 unique station orders")
    dup=x.duplicated(key+["station_order"])
    if dup.any():
        raise RuntimeError("duplicate route-period-year-station rows")

    coord=x.groupby("physical_site_id")[["latitude","longitude"]].nunique()
    if (coord>1).any(axis=None):
        bad=coord[(coord>1).any(axis=1)].index.tolist()[:10]
        raise RuntimeError(f"physical_site_id maps to multiple coordinates: {bad}")

    # One date per route-run.
    if (x.groupby(key).survey_date.nunique()!=1).any():
        raise RuntimeError("multiple survey dates within route-period-year")
    return x


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--station-surveys",required=True)
    ap.add_argument("--output-runs",required=True)
    ap.add_argument("--output-stations",required=True)
    ap.add_argument("--receipt",required=True)
    ap.add_argument("--cache-dir",required=True)
    ap.add_argument("--fixture-dir",default=None,
                    help="offline QA: directory of <physical_site_id>.csv raw Daymet responses")
    args=ap.parse_args()

    input_path=Path(args.station_surveys)
    cache=Path(args.cache_dir)
    cache.mkdir(parents=True,exist_ok=True)
    x=validate_structure(input_path)

    station_rows=[]
    raw_hashes={}
    raw_urls={}

    for sid,g in x.groupby("physical_site_id",sort=True):
        lat=float(g.latitude.iloc[0]); lon=float(g.longitude.iloc[0])
        survey_dates=sorted(pd.Timestamp(d) for d in g.survey_date.unique())
        years=sorted(set(
            [d.year for d in survey_dates]+
            [(d-pd.Timedelta(days=DRY_CAP)).year for d in survey_dates]
        ))
        url=build_url(lat,lon,years)

        cache_file=cache/f"{sid}.csv"
        if args.fixture_dir:
            src=Path(args.fixture_dir)/f"{sid}.csv"
            if not src.exists():
                raise RuntimeError(f"missing fixture Daymet file: {src}")
            raw=src.read_bytes()
        elif cache_file.exists():
            raw=cache_file.read_bytes()
        else:
            raw=fetch_url(url)
            cache_file.write_bytes(raw)

        # Always preserve bytes used for the analysis in cache.
        if not cache_file.exists() or cache_file.read_bytes()!=raw:
            cache_file.write_bytes(raw)

        raw_hash=sha256_bytes(raw)
        raw_hashes[str(sid)]=raw_hash
        raw_urls[str(sid)]=url
        weather=parse_daymet_csv(raw)

        for row in g.itertuples(index=False):
            dry,tmean=station_exposure(weather,pd.Timestamp(row.survey_date))
            station_rows.append({
                "route_id":str(row.route_id),
                "survey_period":str(row.survey_period),
                "survey_year":int(row.survey_year),
                "survey_date":pd.Timestamp(row.survey_date).date().isoformat(),
                "station_order":int(row.station_order),
                "physical_site_id":str(row.physical_site_id),
                "latitude":float(row.latitude),
                "longitude":float(row.longitude),
                "dry_days":dry,
                "log_dry_days":float(np.log1p(dry)),
                "tmean":tmean,
                "daymet_raw_sha256":raw_hash,
            })

    st=pd.DataFrame(station_rows).sort_values(
        ["route_id","survey_period","survey_year","station_order"]
    ).reset_index(drop=True)

    key=["route_id","survey_period","survey_year"]
    runs=(
        st.groupby(key,as_index=False)
          .agg(
              survey_date=("survey_date","first"),
              rain_recency=("log_dry_days","mean"),
              tmean_run=("tmean","mean"),
          )
          .sort_values(key)
          .reset_index(drop=True)
    )

    out_runs=Path(args.output_runs); out_st=Path(args.output_stations)
    out_runs.parent.mkdir(parents=True,exist_ok=True)
    out_st.parent.mkdir(parents=True,exist_ok=True)
    runs.to_csv(out_runs,index=False)
    st.to_csv(out_st,index=False)

    receipt={
        "analysis":"wfts_daymet_weather_adapter_v0_1",
        "spec":"revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md",
        "daymet":{
            "doi":DAYMET_DOI,
            "api_base":API_BASE,
            "variables":list(VARS),
            "dry_day_threshold_mm":THRESHOLD_MM,
            "dry_day_cap":DRY_CAP,
            "survey_day_precipitation_used":False,
        },
        "input_sha256":sha256_file(input_path),
        "output_sha256":{
            "runs":sha256_file(out_runs),
            "stations":sha256_file(out_st),
        },
        "raw_daymet_sha256":raw_hashes,
        "raw_daymet_request_urls":raw_urls,
        "counts":{
            "station_surveys":int(len(st)),
            "route_runs":int(len(runs)),
            "physical_sites":int(st.physical_site_id.nunique()),
        },
        "fixture_mode":bool(args.fixture_dir),
        "response_columns_read":False,
    }
    Path(args.receipt).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
