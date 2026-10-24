#!/usr/bin/env python3
"""A fail-closed, independent JRC water tile-month SHARD for one NAAMP year.

Inputs are pinned original frog-outcome-free Runs/Stops/site coordinates
calendar plus official historical JRC original MonthlyHistory GeoTIFF.
No acoustic records; 0 pixels are missing observation, not dry.
A shard is a stable subset of URL SHA256 keys, never a random selection.
All shards must be combined with an exact calendar/full-key reconciliation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import tempfile
import time
from pathlib import Path
from collections import defaultdict

import rasterio
from run_jrc_prior_month_year import calendar_groups, OUTPUT_COLUMNS
from pilot_jrc_prior_month import download_bounded, water_fraction

MAX_SHARD_BYTES = 1_500_000_000

def shard_of(url,n_shards):
    if n_shards<1: raise ValueError("shard_count must be positive")
    return int.from_bytes(hashlib.sha256(url.encode("utf-8")).digest()[:8],"big")%n_shards

def partition(grouped,n_shards,shard_index):
    if not 0<=shard_index<n_shards:raise ValueError("shard index out of range")
    return {u:grouped[u] for u in sorted(grouped) if shard_of(u,n_shards)==shard_index}

def _blank(row,status):
    return {**{k:row[k] for k in ("State","RouteNumber","SiteID","SurveyYear","PreviousMonth")},
            "radius_m":500,"n_buffer_pixels":"","n_valid_pixels":"",
            "n_water_pixels":"","n_no_observation":"","valid_fraction":"",
            "water_fraction_among_observed":"","coverage_ge_50pct":False,
            "coverage_ge_80pct":False,"status":status,"source_sha256":""}

def execute_shard(year,coords,calendar_path,outdir,shard_count,shard_index):
    if not 1<=shard_count<=24:raise ValueError("shards must be between 1 and 24")
    by_source,full_visits=calendar_groups(year,coords,calendar_path)
    sources=partition(by_source,shard_count,shard_index)
    if not sources:raise RuntimeError("empty shard")
    source_rows=[];rows=[];bytes_total=0
    with tempfile.TemporaryDirectory(prefix=f"frogcs_jrc_{year}_{shard_index}_") as tmp:
        for n,(url,site_months) in enumerate(sources.items(),1):
            source={"url":url,"site_months":len(site_months),"status":"pending"}
            print(f"year={year}, shard={shard_index}/{shard_count}, "
                  f"tile-month={n}/{len(sources)}, sites={len(site_months)}",flush=True)
            target=Path(tmp)/f"jrc_{n:03d}.tif"
            try:
                for attempt in range(2):
                    try:
                        info=download_bounded(url,target)
                        break
                    except Exception:
                        if attempt:raise
                        target.unlink(missing_ok=True)
                        time.sleep(2)
                bytes_total+=info["bytes"]
                if bytes_total>MAX_SHARD_BYTES:raise RuntimeError("1.5GB shard transfer cap exceeded")
                source.update(status="loaded",sha256=info["sha256"],bytes=info["bytes"])
                with rasterio.open(target) as ds:
                    for row in site_months.values():
                        measure=water_fraction(ds,row["lat"],row["lon"],500)
                        rows.append({**{k:row[k] for k in ("State","RouteNumber","SiteID","SurveyYear","PreviousMonth")},
                                     **measure,
                                     "status":"ok" if measure["coverage_ge_50pct"] else "insufficient_clear_pixels",
                                     "source_sha256":info["sha256"]})
            except Exception as exc:
                source.update(status="unavailable",error=type(exc).__name__+": "+str(exc)[:180])
                rows.extend(_blank(row,"source_unavailable") for row in site_months.values())
            finally:
                target.unlink(missing_ok=True)
            source_rows.append(source)
    rows.sort(key=lambda r:(r["RouteNumber"],r["SiteID"],r["PreviousMonth"]))
    expected=sum(len(x) for x in sources.values())
    unique={(r["RouteNumber"],r["SiteID"],r["PreviousMonth"]) for r in rows}
    if len(rows)!=expected or len(unique)!=expected:
        raise RuntimeError("shard subset reconciliation failed")
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    prefix=f"jrc_prev_month_{year}_shard{shard_index:02d}of{shard_count:02d}"
    path=out/(prefix+"_500m_sites.csv")
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=OUTPUT_COLUMNS);w.writeheader()
        w.writerows({field:r.get(field,"") for field in OUTPUT_COLUMNS} for r in rows)
    good=[x for x in rows if x["status"]=="ok"]
    receipt={"analysis":"naamp_jrc_previous_month_source_shard_v0_1","year":year,
             "version":"JRC MonthlyHistory VER5-0","shard_count":shard_count,
             "shard_index":shard_index,"shard_rule":"first eight bytes SHA256(url) modulo shard_count",
             "all_year_station_visits":full_visits,"all_year_distinct_source_tile_months":len(by_source),
             "selected_tile_months":len(sources),"selected_site_months":len(rows),
             "source_tiles_successful":sum(s["status"]=="loaded" for s in source_rows),
             "source_tiles_unavailable":sum(s["status"]!="loaded" for s in source_rows),
             "site_months_ge50pct_observed":len(good),
             "site_months_ge80pct_observed":sum(x["coverage_ge_80pct"] for x in good),
             "site_months_water_positive":sum(x["n_water_pixels"]>0 for x in good),
             "bytes_transferred":bytes_total,
             "csv_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
             "source_receipts":source_rows,
             "previous_calendar_month_only":True,"zero_pixel_means_unobserved":True,
             "no_frog_outcomes_read":True,"ecological_hypothesis_tested":False,
             "full_year_complete":False,
             "note":"Full year is complete ONLY after all shards and exact site-month calendar keys are reconciled."}
    (out/(prefix+"_receipt.json")).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in receipt.items() if k!="source_receipts"},indent=2,sort_keys=True))
    if receipt["source_tiles_unavailable"]:
        raise RuntimeError("source tiles unavailable; investigate failed shard receipt before interpreting output")
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--accepted-coordinates",required=True)
    p.add_argument("--site-calendar",required=True)
    p.add_argument("--out-dir",required=True)
    p.add_argument("--shard-count",type=int,required=True)
    p.add_argument("--shard-index",type=int,required=True)
    a=p.parse_args()
    execute_shard(a.year,a.accepted_coordinates,a.site_calendar,a.out_dir,a.shard_count,a.shard_index)
