#!/usr/bin/env python3
"""Outcome-blind NAAMP calendar × prior-month JRC water for one survey year.

Downloads *one* EC JRC/Google original MonthlyHistory VER5-0 GeoTIFF per
10-degree tile × preceding calendar month, extracts 500-m geodesic buffers,
and discards original tiles. 0=no Landsat water observation (NOT dry),
1=observed nonwater, 2=observed water.
Never opens NAAMP Counts.csv or fits calling outcomes.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import rasterio
from pilot_jrc_prior_month import preceding_month, source_url, download_bounded, water_fraction

PIN_COORD="2dbd226a117e5d2c9c10dbd6340fb86a07320b2925aaca3249c8a307a5071afc"
PIN_CAL="e6fc079ace3642a0ed4330dc05a4b8770fdf89cefabfaca0e490dcb3fd8c45cf"
MAX_YEAR_TRANSFER=2_500_000_000
OUTPUT_COLUMNS=("State","RouteNumber","SiteID","SurveyYear","PreviousMonth",
                "radius_m","n_buffer_pixels","n_valid_pixels","n_water_pixels",
                "n_no_observation","valid_fraction","water_fraction_among_observed",
                "coverage_ge_50pct","coverage_ge_80pct","status","source_sha256")

def verify(path,sha):
    got=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if got!=sha:raise RuntimeError(f"source input checksum drift {path}: {got}")

def calendar_groups(year,coords,calendar_path):
    if not 2001<=year<=2015:raise ValueError("year outside study interval")
    verify(coords,PIN_COORD);verify(calendar_path,PIN_CAL)
    with open(coords,encoding="utf-8-sig",newline="") as f:
        p={(r["RouteNumber"],r["SiteID"]):(float(r["lat"]),float(r["lon"]))
           for r in csv.DictReader(f) if r["status"]=="accepted"}
    by_source=defaultdict(dict);visits=0
    with open(calendar_path,encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or not {"State","RouteNumber","SiteID","SurveyDate","SurveyYear"}.issubset(rd.fieldnames):
            raise ValueError("outcome-blind survey calendar incomplete")
        if {"CallingIndex","Species"} & set(rd.fieldnames):
            raise ValueError("frog outcomes forbidden in environmental input")
        for row in rd:
            if int(row["SurveyYear"])!=year:continue
            key=(row["RouteNumber"],row["SiteID"])
            if key not in p:raise RuntimeError("calendar contains unaccepted coordinate key")
            fy,fm=preceding_month(row["SurveyDate"])
            ym=f"{fy:04d}-{fm:02d}"
            lat,lon=p[key]
            url=source_url(fy,fm,lat,lon)
            ident=(row["RouteNumber"],row["SiteID"],ym)
            previous=by_source[url].get(ident)
            if previous is None:
                by_source[url][ident]={"State":row["State"],"RouteNumber":key[0],
                    "SiteID":key[1],"SurveyYear":year,"PreviousMonth":ym,
                    "lat":lat,"lon":lon}
            elif (previous["lat"],previous["lon"])!=(lat,lon):
                raise RuntimeError("same SiteID has conflicting coordinates")
            visits+=1
    if not by_source:raise RuntimeError("no observed station previous-month keys")
    return by_source,visits

def execute(year,coords,calendar_path,outdir):
    by_src,n_visits=calendar_groups(year,coords,calendar_path)
    collected=[];source_receipts=[];nbytes=0
    with tempfile.TemporaryDirectory(prefix=f"jrc_naamp_{year}_") as directory:
        for n,(url,sites) in enumerate(sorted(by_src.items()),1):
            src={"url":url,"n_site_months":len(sites),"source_status":None}
            print(f"JRC {year} source {n}/{len(by_src)}: {len(sites)} site-months",flush=True)
            try:
                target=Path(directory)/f"jrc_tile_{n:03d}.tif"
                data=None
                for attempt in range(2):
                    try:
                        data=download_bounded(url,target)
                        break
                    except Exception:
                        if attempt:raise
                        time.sleep(1)
                nbytes+=data["bytes"]
                if nbytes>MAX_YEAR_TRANSFER:raise RuntimeError("year transfer exceeded 2.5GB budget")
                src.update(source_status="loaded",sha256=data["sha256"],bytes=data["bytes"])
                with rasterio.open(target) as ds:
                    for row in sites.values():
                        area=water_fraction(ds,row["lat"],row["lon"],500)
                        status="ok" if area["coverage_ge_50pct"] else "insufficient_clear_pixels"
                        collected.append({**{k:row[k] for k in ("State","RouteNumber","SiteID","SurveyYear","PreviousMonth")},
                                          **area,"status":status,"source_sha256":data["sha256"]})
                target.unlink(missing_ok=True)
            except Exception as ex:
                src.update(source_status="unavailable",error=type(ex).__name__+": "+str(ex)[:220])
                for row in sites.values():
                    collected.append({**{k:row[k] for k in ("State","RouteNumber","SiteID","SurveyYear","PreviousMonth")},
                        "radius_m":500,"n_buffer_pixels":"","n_valid_pixels":"",
                        "n_water_pixels":"","n_no_observation":"",
                        "valid_fraction":"","water_fraction_among_observed":"",
                        "coverage_ge_50pct":False,"coverage_ge_80pct":False,
                        "status":"source_unavailable","source_sha256":""})
            source_receipts.append(src)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    collected.sort(key=lambda r:(r["RouteNumber"],r["SiteID"],r["PreviousMonth"]))
    keys={(r["RouteNumber"],r["SiteID"],r["PreviousMonth"]) for r in collected}
    expected=sum(len(s) for s in by_src.values())
    if len(keys)!=expected or len(collected)!=expected:
        raise RuntimeError("site-month rows missing/duplicated")
    file=outdir/f"jrc_prev_month_{year}_500m_sites.csv"
    with file.open("w",encoding="utf-8",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=OUTPUT_COLUMNS)
        wr.writeheader()
        wr.writerows([{c:r.get(c,"") for c in OUTPUT_COLUMNS} for r in collected])
    valid=[r for r in collected if r["status"]=="ok"]
    water=[r for r in valid if r["n_water_pixels"]>0]
    report={"analysis":"jrc_monthly_history_naamp_sites_environment_only_v0_1",
        "year":year,"source":"EC JRC/Google MonthlyHistory VER5-0",
        "previous_calendar_month_only":True,"day_of_survey_water":False,
        "zero_means_no_observation":True,"no_frog_outcomes_read":True,
        "survey_station_visits":n_visits,"unique_site_previous_months":len(collected),
        "distinct_source_tile_months":len(by_src),
        "source_tiles_downloaded":sum(x["source_status"]=="loaded" for x in source_receipts),
        "source_tiles_unavailable":sum(x["source_status"]!="loaded" for x in source_receipts),
        "site_months_with_ge50pct_valid":len(valid),
        "site_months_with_ge80pct_valid":sum(x["coverage_ge_80pct"] for x in valid),
        "site_months_with_any_open_water":len(water),
        "water_positive_share_among_valid":len(water)/len(valid) if valid else None,
        "bytes_transferred":nbytes,"output_csv_sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
        "sources":source_receipts}
    (outdir/f"jrc_prev_month_{year}_source_receipt.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="sources"},indent=2,sort_keys=True))
    if report["source_tiles_unavailable"]:
        raise RuntimeError("one or more source tile/month files unavailable; inspect receipt before use")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--accepted-coordinates",required=True)
    p.add_argument("--site-calendar",required=True)
    p.add_argument("--out-dir",required=True)
    args=p.parse_args()
    execute(args.year,args.accepted_coordinates,args.site_calendar,args.out_dir)
