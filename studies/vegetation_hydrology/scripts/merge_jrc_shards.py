#!/usr/bin/env python3
"""Reconcile independent JRC tile-month shards against the complete original NAAMP calendar.

Fail closed if any source URI/shard/site-month is missing, duplicated, or has
invalid original-pixel QC. No frog-response data are accepted or inspected.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter,defaultdict
from pathlib import Path

from run_jrc_prior_month_year import calendar_groups,OUTPUT_COLUMNS
from run_jrc_prior_month_shard import shard_of

FORBIDDEN={"Species","CallingIndex","Abundance","counts_csv"}
REQUIRED={"State","RouteNumber","SiteID","SurveyYear","PreviousMonth",
          "radius_m","n_buffer_pixels","n_valid_pixels","n_water_pixels",
          "n_no_observation","valid_fraction","water_fraction_among_observed",
          "coverage_ge_50pct","coverage_ge_80pct","status","source_sha256"}

def _truth(x):
    if x in (True,"True","true","1"):return True
    if x in (False,"False","false","0"):return False
    raise ValueError(f"unrecognized boolean: {x!r}")

def check_pixel_row(r):
    if r["status"] not in ("ok","insufficient_clear_pixels"):
        raise ValueError(f"cannot treat {r['status']} as successful source")
    n=int(r["n_buffer_pixels"]);v=int(r["n_valid_pixels"])
    w=int(r["n_water_pixels"]);miss=int(r["n_no_observation"])
    if n<=0 or not (0<=w<=v<=n) or n!=miss+v:
        raise ValueError("water/no-observation count inconsistency")
    vf=round(v/n,6)
    wf=round(w/v,6) if v else None
    observed_vf=float(r["valid_fraction"])
    if abs(observed_vf-vf)>1e-6:
        raise ValueError("observed fraction inconsistent with counts")
    actual_w=r["water_fraction_among_observed"]
    if (v==0 and actual_w not in ("",None)) or (v>0 and abs(float(actual_w)-wf)>1e-6):
        raise ValueError("water fraction includes unobserved pixels or differs from source counts")
    g50=(v/n)>=.5
    g80=(v/n)>=.8
    if g50!=_truth(r["coverage_ge_50pct"]) or g80!=_truth(r["coverage_ge_80pct"]):
        raise ValueError("coverage gate inconsistent with raw observation count")
    if (r["status"]=="ok")!=g50:
        raise ValueError("status inconsistent with 50 percent coverage gate")
    return {"observed":v,"water":w,"valid_50":g50,"valid_80":g80}

def merge(archives, expected_source, year, n_shards):
    """expected_source is exact calendar_groups(year,...) output mapping URL -> station months."""
    if n_shards<=0:raise ValueError("no shards")
    by_idx={};actual_source=set();collected={}
    source_hashes={}
    for path in archives:
        with zipfile.ZipFile(path) as z:
            names=z.namelist()
            receipts=[name for name in names if name.endswith("_receipt.json")]
            tables=[name for name in names if name.endswith("_500m_sites.csv")]
            if len(receipts)!=1 or len(tables)!=1:
                raise ValueError(f"one receipt + one 500m CSV required in {path}")
            receipt=json.loads(z.read(receipts[0]))
            if receipt.get("analysis")!="naamp_jrc_previous_month_source_shard_v0_1":
                raise ValueError("invalid shard type")
            if receipt.get("year")!=year or receipt.get("shard_count")!=n_shards or receipt.get("no_frog_outcomes_read") is not True:
                raise ValueError("shard identity/method drift")
            idx=int(receipt["shard_index"])
            if idx in by_idx or not 0<=idx<n_shards:raise ValueError("duplicate or invalid shard index")
            by_idx[idx]=receipt
            raw=z.read(tables[0])
            if hashlib.sha256(raw).hexdigest()!=receipt.get("csv_sha256"):
                raise ValueError("shard table checksum mismatch")
            rd=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            if not rd.fieldnames or not REQUIRED.issubset(rd.fieldnames) or FORBIDDEN.intersection(rd.fieldnames):
                raise ValueError("invalid output schema / response column")
            per_source={x["url"]:x for x in receipt["source_receipts"]}
            if len(per_source)!=len(receipt["source_receipts"]):
                raise ValueError("duplicate source receipt")
            if receipt.get("source_tiles_unavailable") or any(x["status"]!="loaded" for x in per_source.values()):
                raise ValueError("incomplete source tile: do not publish complete panel")
            for url,s in per_source.items():
                if url in actual_source or url not in expected_source or shard_of(url,n_shards)!=idx:
                    raise ValueError("source duplicate / foreign / wrong shard")
                if not isinstance(s.get("sha256"),str) or len(s["sha256"])!=64:
                    raise ValueError("source original TIFF hash missing")
                actual_source.add(url);source_hashes[url]=s["sha256"]
            by_key_source={}
            for url,site_rows in expected_source.items():
                if url in per_source:
                    for k,row in site_rows.items():
                        key=(row["RouteNumber"],row["SiteID"],row["PreviousMonth"])
                        by_key_source[key]=url
            count=0
            for r in rd:
                key=(r["RouteNumber"],r["SiteID"],r["PreviousMonth"])
                if r["SurveyYear"]!=str(year) or r["radius_m"]!="500":
                    raise ValueError("unexpected survey year or radius")
                if key in collected or key not in by_key_source:
                    raise ValueError("duplicate or foreign site-month key")
                if r["source_sha256"]!=source_hashes[by_key_source[key]]:
                    raise ValueError("site-month has wrong source tile hash")
                check_pixel_row(r)
                collected[key]=r;count+=1
            if count!=receipt["selected_site_months"] or len(per_source)!=receipt["selected_tile_months"]:
                raise ValueError("shard receipt count inconsistency")
    if set(by_idx)!=set(range(n_shards)):
        raise ValueError("missing shard indices")
    if actual_source!=set(expected_source):
        raise ValueError("missing or excess source tile-month URLs")
    expected_keys={(row["RouteNumber"],row["SiteID"],row["PreviousMonth"])
                   for sites in expected_source.values() for row in sites.values()}
    if set(collected)!=expected_keys:
        raise ValueError("site-month coverage incomplete")
    table=[collected[key] for key in sorted(collected)]
    valid=[r for r in table if _truth(r["coverage_ge_50pct"])]
    vals=[float(r["water_fraction_among_observed"]) for r in valid]
    by_state=defaultdict(lambda:Counter())
    for r in table:
        d=by_state[r["State"]];d["site_months"]+=1
        if _truth(r["coverage_ge_50pct"]):
            d["valid_ge50"]+=1
            if int(r["n_water_pixels"])>0:d["any_water"]+=1
    report={"analysis":"jrc_naamp_full_year_shards_reconciled_v0_1",
            "year":year,"n_shards":n_shards,"n_tile_months":len(actual_source),
            "n_unique_site_previous_months":len(table),
            "n_500m_ge50pct_observed":len(valid),
            "n_500m_ge80pct_observed":sum(_truth(r["coverage_ge_80pct"]) for r in table),
            "n_500m_ge50pct_with_positive_open_water":sum(x>0 for x in vals),
            "share_500m_ge50pct_observed":round(len(valid)/len(table),6),
            "share_of_usable_500m_with_open_water":round(sum(x>0 for x in vals)/len(vals),6) if vals else None,
            "state_coverage":{state:dict(counts) for state,counts in sorted(by_state.items())},
            "source_original_tiff_sha256":source_hashes,
            "no_frog_outcomes_read":True,
            "causal_or_ecological_frog_effect_estimated":False,
            "source":"EC JRC/Google Global Surface Water MonthlyHistory VER5-0",
            "water_time":"strictly previous full calendar month, not survey-day water",
            "no_observation_is_missing_not_dry":True,
            "coverage_note":"NAAMP environmental frame; not necessarily the JAE matched-pair sample."}
    return table,report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--shard-dir",type=Path,required=True)
    p.add_argument("--shard-count",type=int,required=True)
    p.add_argument("--coordinates",required=True)
    p.add_argument("--site-calendar",required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    sources,visits=calendar_groups(a.year,a.coordinates,a.site_calendar)
    archives=sorted(a.shard_dir.rglob("*.zip"))
    if len(archives)!=a.shard_count:
        raise RuntimeError("expected exact number of artifact archives")
    table,report=merge(archives,sources,a.year,a.shard_count)
    report["survey_station_visits"]=visits
    a.out_dir.mkdir(parents=True,exist_ok=True)
    csvpath=a.out_dir/f"jrc_prev_month_{a.year}_500m_sites_verified.csv"
    with csvpath.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in table:writer.writerow({k:row.get(k,"") for k in OUTPUT_COLUMNS})
    report["csv_sha256"]=hashlib.sha256(csvpath.read_bytes()).hexdigest()
    (a.out_dir/f"jrc_prev_month_{a.year}_reconciliation.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("source_original_tiff_sha256","state_coverage")},indent=2))

if __name__=="__main__":
    main()
