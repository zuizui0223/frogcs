#!/usr/bin/env python3
"""Fail-closed, outcome-blind 2001-2015 JRC previous-month water panel audit.

Input: fully reconciled year CSVs and provenance receipts. Each year must
pass exact physical site/month checks before this programme runs. This script
requires NO frog Counts.csv, species names, or calling outcome fields.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

EXPECTED_TOTAL_VISITS=185221
EXPECTED_TOTAL_SITE_MONTHS=172153
YEARS=set(range(2001,2016))
FORBIDDEN={"Species","CallingIndex","Abundance","Taxon"}
COLUMNS=("State","RouteNumber","SiteID","SurveyYear","PreviousMonth","radius_m",
         "n_buffer_pixels","n_valid_pixels","n_water_pixels","n_no_observation",
         "valid_fraction","water_fraction_among_observed","coverage_ge_50pct",
         "coverage_ge_80pct","status","source_sha256")

def truth(value):
    if str(value).lower() in ("true","1"):return True
    if str(value).lower() in ("false","0"):return False
    raise ValueError("unrecognized pixel-QC flag")

def combine(year_dir,expected=None):
    expect={int(x["year"]):x for x in expected} if expected else None
    seen=set();source_hashes={};annual=[];output_rows=[]
    total_visits=0;total_sources=0
    for y in sorted(YEARS):
        files=list(Path(year_dir).rglob(f"jrc_prev_month_{y}_500m_sites_verified.csv"))
        receipts=list(Path(year_dir).rglob(f"jrc_prev_month_{y}_reconciliation.json"))
        if len(files)!=1 or len(receipts)!=1:
            raise RuntimeError(f"expected exactly one independently reconciled JRC year {y}")
        receipt=json.loads(receipts[0].read_text(encoding="utf-8"))
        if receipt.get("analysis")!="jrc_naamp_full_year_shards_reconciled_v0_1":
            raise ValueError(f"year {y} not validated by exact reconciliation")
        if receipt.get("year")!=y or receipt.get("no_frog_outcomes_read") is not True:
            raise ValueError("outcome-blind provenance drift")
        raw=files[0].read_bytes()
        if hashlib.sha256(raw).hexdigest()!=receipt.get("csv_sha256"):
            raise ValueError(f"year {y} table SHA256 mismatches receipt")
        src=receipt.get("source_original_tiff_sha256")
        if not isinstance(src,dict) or len(src)!=receipt["n_tile_months"]:
            raise ValueError(f"year {y} source hashes incomplete")
        for url,sha in src.items():
            if len(sha)!=64 or not url.startswith("https://jeodpp.jrc.ec.europa.eu/"):
                raise ValueError("unexpected source URL or TIFF SHA")
            if url in source_hashes and source_hashes[url]!=sha:
                raise ValueError("the same original JRC tile URL changed SHA across years")
            source_hashes[url]=sha
        total_sources+=len(src)
        total_visits+=int(receipt["survey_station_visits"])
        count=0;usable=0;water=0
        with files[0].open(newline="",encoding="utf-8-sig") as f:
            reader=csv.DictReader(f)
            if not reader.fieldnames or not set(COLUMNS).issubset(reader.fieldnames) or FORBIDDEN.intersection(reader.fieldnames):
                raise ValueError("incorrect JRC schema or frog outcomes leaked")
            for row in reader:
                key=(row["RouteNumber"],row["SiteID"],row["SurveyYear"],row["PreviousMonth"])
                if int(row["SurveyYear"])!=y or key in seen:
                    raise ValueError("duplicate or wrong-year JRC site-month")
                seen.add(key)
                if row["radius_m"]!="500":raise ValueError("unexpected distance")
                n=int(row["n_buffer_pixels"]);v=int(row["n_valid_pixels"])
                w=int(row["n_water_pixels"]);missing=int(row["n_no_observation"])
                if not (n>0 and 0<=w<=v<=n and v+missing==n):
                    raise ValueError("invalid observed/water/no-observation pixels")
                valid=v/n>=.5
                if valid!=truth(row["coverage_ge_50pct"]):
                    raise ValueError("50% pixel validity gate drift")
                if abs(float(row["valid_fraction"])-v/n)>1.1e-6:
                    raise ValueError("valid pixel fraction corrupted")
                if v and abs(float(row["water_fraction_among_observed"])-w/v)>1.1e-6:
                    raise ValueError("water among observed pixels inconsistent")
                if not v and row["water_fraction_among_observed"].strip():
                    raise ValueError("zero observed pixels must have missing water fraction")
                if valid:
                    usable+=1
                    if w:water+=1
                output_rows.append(row);count+=1
        if count!=receipt["n_unique_site_previous_months"] or usable!=receipt["n_500m_ge50pct_observed"] or water!=receipt["n_500m_ge50pct_with_positive_open_water"]:
            raise RuntimeError(f"year {y} receipt mismatch")
        if expect and (count!=int(expect[y]["unique_site_month"]) or receipt["n_tile_months"]!=int(expect[y]["source_tile_month"]) or receipt["survey_station_visits"]!=int(expect[y]["visits"])):
            raise RuntimeError(f"year {y} mismatch to frozen outcome-blind source workload")
        annual.append({"year":y,"site_months":count,"usable50":usable,"water_positive":water,
                      "pct_usable50":round(100*usable/count,3),
                      "pct_water_positive_among_usable":round(100*water/usable,3) if usable else None,
                      "tile_month_sources":len(src),"survey_station_visits":receipt["survey_station_visits"]})
    if set(int(x["year"]) for x in annual)!=YEARS or len(output_rows)!=EXPECTED_TOTAL_SITE_MONTHS or total_visits!=EXPECTED_TOTAL_VISITS:
        raise RuntimeError("15-year full-panel completeness failed")
    if expect and total_sources!=sum(int(v["source_tile_month"]) for v in expect.values()):
        raise RuntimeError("total source tile-month count mismatch")
    if len(seen)!=len(output_rows):raise RuntimeError("duplicate record after annual combine")
    return output_rows,{
        "analysis":"NAAMP_JRC_GSW_2001_2015_environment_only_full_panel_v0_1",
        "years":[min(YEARS),max(YEARS)],"source":"EC JRC/Google MonthlyHistory VER5-0 30m",
        "dataset_original_tiff_urls":len(source_hashes),"annual_source_requests_sum":total_sources,
        "n_station_visits":total_visits,"n_unique_site_previous_month_records":len(output_rows),
        "n_500m_usable50":sum(x["usable50"] for x in annual),
        "n_500m_detected_open_water":sum(x["water_positive"] for x in annual),
        "by_year":annual,
        "no_frog_outcomes_read":True,"ecological_effect_estimated":False,
        "no_observation_zero_is_missing":True,
        "water_observation_month":"complete previous calendar month, not day-of-survey",
        "disclaimer":"Data completeness is not hydroperiod measurement or frog-outcome evidence.",
        "original_source_hashes":source_hashes
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year-dir",required=True,type=Path)
    p.add_argument("--source-workload",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    args=p.parse_args()
    expected=json.loads(args.source_workload.read_text(encoding="utf-8"))
    rows,summary=combine(args.year_dir,expected)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    csvout=args.out_dir/"jrc_2001_2015_previous_month_500m_environment_only.csv"
    with csvout.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS);writer.writeheader()
        writer.writerows({k:r.get(k,"") for k in COLUMNS} for r in sorted(rows,key=lambda r:(int(r["SurveyYear"]),r["RouteNumber"],r["SiteID"],r["PreviousMonth"])))
    summary["combined_csv_sha256"]=hashlib.sha256(csvout.read_bytes()).hexdigest()
    (args.out_dir/"jrc_2001_2015_full_environment_manifest.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="original_source_hashes"},indent=2,sort_keys=True))

if __name__=="__main__":main()
