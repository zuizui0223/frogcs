#!/usr/bin/env python3
from __future__ import annotations

import argparse
import calendar
from pathlib import Path

import pandas as pd


def daymet_dates(year):
    dates=list(pd.date_range(
        pd.Timestamp(year=year,month=1,day=1),
        pd.Timestamp(year=year,month=12,day=31),
        freq="D",
    ))
    if calendar.isleap(year):
        dates=[d for d in dates if not (d.month==12 and d.day==31)]
    assert len(dates)==365
    return dates


def raw_csv(years,wet_dates=None,survey_day_wet_dates=None):
    wet=set(pd.Timestamp(x).normalize() for x in (wet_dates or []))
    surveywet=set(pd.Timestamp(x).normalize() for x in (survey_day_wet_dates or []))
    lines=[
        "# synthetic Daymet response for code QA only",
        "year,yday,prcp (mm/day),tmin (deg c),tmax (deg c)",
    ]
    for year in years:
        for yday,d in enumerate(daymet_dates(year),start=1):
            prcp=0.0
            if d in wet or d in surveywet:
                prcp=5.0
            tmin=5.0+(d.month/12.0)
            tmax=15.0+(d.month/12.0)
            lines.append(f"{year},{yday},{prcp:.1f},{tmin:.3f},{tmax:.3f}")
    return ("\n".join(lines)+"\n").encode()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",required=True)
    args=ap.parse_args()
    out=Path(args.outdir)
    raw=out/"raw"; raw.mkdir(parents=True,exist_ok=True)

    # One route, ten stations, two survey years including leap-year 2012.
    rows=[]
    surveys=[
        (2012,"2012-03-03"),
        (2013,"2013-03-03"),
    ]
    for year,date in surveys:
        for station in range(1,11):
            sid=f"R001_S{station:02d}"
            rows.append({
                "route_id":"R001",
                "survey_period":"early_spring",
                "survey_year":year,
                "survey_date":date,
                "station_order":station,
                "physical_site_id":sid,
                "latitude":43.0+station/1000,
                "longitude":-89.0-station/1000,
            })
    pd.DataFrame(rows).to_csv(out/"station_surveys.csv",index=False)

    # All sites share deterministic weather:
    # 2012 survey on Mar 3: Mar 2 wet -> dry_days=0.
    # survey-day Mar 3 is also wet to verify survey day is ignored.
    # 2013 survey on Mar 3: no wet day in previous 30 days -> cap=30.
    for station in range(1,11):
        sid=f"R001_S{station:02d}"
        raw_bytes=raw_csv(
            [2012,2013],
            wet_dates=["2012-03-02"],
            survey_day_wet_dates=["2012-03-03"],
        )
        (raw/f"{sid}.csv").write_bytes(raw_bytes)

    print({"station_surveys":len(rows),"sites":10})


if __name__=="__main__":
    main()
