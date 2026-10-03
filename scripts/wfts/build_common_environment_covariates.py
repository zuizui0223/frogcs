#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
WFTS=ROOT/"scripts"/"wfts"
PRIMARY=WFTS/"build_daymet_covariates.py"
WINDOWS=(1,3,7)

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base=loadmod("wfts_daymet_primary",PRIMARY)

def antecedent_amounts(daymet: pd.DataFrame, survey_date: pd.Timestamp) -> dict[int,float]:
    by_date=daymet.set_index("date")
    d=pd.Timestamp(survey_date).normalize()
    out={}
    for window in WINDOWS:
        vals=[]
        for lag in range(1,window+1):
            q=d-pd.Timedelta(days=lag)
            if q not in by_date.index:
                raise RuntimeError(f"required prior Daymet date missing: {q.date()}")
            p=float(by_date.loc[q,"prcp"])
            if not np.isfinite(p) or p<0:
                raise RuntimeError(f"invalid Daymet precipitation: {q.date()} = {p}")
            vals.append(p)
        out[window]=float(np.sum(vals))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--station-surveys",required=True)
    ap.add_argument("--output-runs",required=True)
    ap.add_argument("--output-stations",required=True)
    ap.add_argument("--receipt",required=True)
    ap.add_argument("--cache-dir",required=True)
    ap.add_argument("--fixture-dir",default=None)
    args=ap.parse_args()

    input_path=Path(args.station_surveys)
    cache=Path(args.cache_dir)
    cache.mkdir(parents=True,exist_ok=True)
    x=base.validate_structure(input_path)

    station_rows=[]
    raw_hashes={}
    raw_urls={}

    for sid,g in x.groupby("physical_site_id",sort=True):
        lat=float(g.latitude.iloc[0]); lon=float(g.longitude.iloc[0])
        survey_dates=sorted(pd.Timestamp(d) for d in g.survey_date.unique())
        years=sorted(set(
            [d.year for d in survey_dates]+
            [(d-pd.Timedelta(days=max(WINDOWS))).year for d in survey_dates]
        ))
        url=base.build_url(lat,lon,years)
        cache_file=cache/f"{sid}.csv"
        if args.fixture_dir:
            src=Path(args.fixture_dir)/f"{sid}.csv"
            if not src.exists():
                raise RuntimeError(f"missing fixture Daymet file: {src}")
            raw=src.read_bytes()
        elif cache_file.exists():
            raw=cache_file.read_bytes()
        else:
            raw=base.fetch_url(url)
            cache_file.write_bytes(raw)

        if not cache_file.exists() or cache_file.read_bytes()!=raw:
            cache_file.write_bytes(raw)

        raw_hash=base.sha256_bytes(raw)
        raw_hashes[str(sid)]=raw_hash
        raw_urls[str(sid)]=url
        weather=base.parse_daymet_csv(raw)

        for row in g.itertuples(index=False):
            amounts=antecedent_amounts(weather,pd.Timestamp(row.survey_date))
            rec={
                "route_id":str(row.route_id),
                "survey_period":str(row.survey_period),
                "survey_year":int(row.survey_year),
                "survey_date":pd.Timestamp(row.survey_date).date().isoformat(),
                "station_order":int(row.station_order),
                "physical_site_id":str(row.physical_site_id),
                "latitude":float(row.latitude),
                "longitude":float(row.longitude),
                "daymet_raw_sha256":raw_hash,
            }
            for w in WINDOWS:
                rec[f"prcp_{w}d_mm"]=float(amounts[w])
                rec[f"log1p_prcp_{w}d"]=float(np.log1p(amounts[w]))
            station_rows.append(rec)

    st=pd.DataFrame(station_rows).sort_values(
        ["route_id","survey_period","survey_year","station_order"]
    ).reset_index(drop=True)

    key=["route_id","survey_period","survey_year"]
    runs=(
        st.groupby(key,as_index=False)
          .agg(
              survey_date=("survey_date","first"),
              prcp_1d_exposure=("log1p_prcp_1d","mean"),
              prcp_3d_exposure=("log1p_prcp_3d","mean"),
              prcp_7d_exposure=("log1p_prcp_7d","mean"),
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
        "analysis":"wfts_common_environment_weather_adapter_v0_1",
        "authority":"revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json",
        "daymet":{
            "doi":base.DAYMET_DOI,
            "api_base":base.API_BASE,
            "variables":list(base.VARS),
            "survey_day_precipitation_used":False,
            "windows_complete_prior_days":list(WINDOWS),
            "station_transform":"log(1 + summed precipitation mm)",
            "route_aggregation":"arithmetic mean across exactly 10 station transformed exposures",
            "primary_window_days":3,
        },
        "input_sha256":base.sha256_file(input_path),
        "output_sha256":{
            "runs":base.sha256_file(out_runs),
            "stations":base.sha256_file(out_st),
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
