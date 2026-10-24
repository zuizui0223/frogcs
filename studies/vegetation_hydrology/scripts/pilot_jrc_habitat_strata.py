#!/usr/bin/env python3
"""JRC previous-month water pixels stratified by NLCD habitat, without frog outcomes.

Nine fixed site events are selected from the already extracted 15-year USGS NLCD
Collection 1.2 panel, before inspecting any JRC pixels. Land-cover strata
reflect mapped 500-m context, not habitat ground truth. All water comparisons
remain feasibility-only. Missing pixels (0) never count as dry (1).
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import tempfile
from pathlib import Path

from pilot_jrc_prior_month import (
    preceding_month, source_url, download_bounded, water_fraction
)

MANIFEST_SHA="82b2037f88b78e3af3599fce9ff78d385c8f24611cb4bffdb8c77a299eaaa3bf"
STRATA=("open_water_ge10pct","vegetated_wetland_ge25pct","dry_context_lt5pct")
YEARS=(2001,2008,2015)
MAX_TOTAL_BYTES=450_000_000

def read_manifest(path):
    raw=Path(path).read_bytes()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=MANIFEST_SHA: raise RuntimeError(f"site sample checksum drift: {actual}")
    reader=csv.DictReader(raw.decode("utf-8-sig").splitlines())
    if not reader.fieldnames or not {"year","SurveyDate","stratum","State","RouteNumber","SiteID","lat","lon","frac_open_water","wetland_sum"}.issubset(reader.fieldnames):
        raise ValueError("missing site sampling metadata")
    if {"Species","CallingIndex"} & set(reader.fieldnames):
        raise ValueError("frog outcome fields prohibited in manifest")
    sample=[]
    for v in reader:
        year=int(v["year"])
        date=dt.date.fromisoformat(v["SurveyDate"])
        if date.year!=year or year not in YEARS or v["stratum"] not in STRATA:
            raise ValueError("site-year or habitat stratum outside fixed pilot")
        w=float(v["frac_open_water"]);wet=float(v["wetland_sum"])
        st=v["stratum"]
        if st==STRATA[0] and w<.1:raise ValueError("open-water stratum mismatch")
        if st==STRATA[1] and not(wet>=.25 and w<.01):
            raise ValueError("vegetated-wetland stratum mismatch")
        if st==STRATA[2] and not(w<.005 and wet<.05):
            raise ValueError("dry-context stratum mismatch")
        sample.append({"year":year,"state":v["State"],"route":v["RouteNumber"],
            "site":v["SiteID"],"date":date.isoformat(),
            "lat":float(v["lat"]),"lon":float(v["lon"]),"stratum":st,
            "nlcd500_open_water_fraction":w,"nlcd500_vegetated_wetland_fraction":wet})
    if len(sample)!=9 or {(r["year"],r["stratum"]) for r in sample}!={(y,s) for y in YEARS for s in STRATA}:
        raise ValueError("expected exactly one event per year-by-habitat stratum")
    return sample

def process(manifest_path,out_path):
    import rasterio
    selected=read_manifest(manifest_path)
    out=[];cached={};bytes_total=0
    with tempfile.TemporaryDirectory(prefix="frogcs_jrc_habitat_strat_") as temp:
        for site in selected:
            year,month=preceding_month(site["date"])
            url=source_url(year,month,site["lat"],site["lon"])
            record=dict(site, previous_month=f"{year}-{month:02d}",
                        source_url=url, source="EC JRC/Google GSW VER5-0",
                        outcome_data_read=False)
            try:
                if url not in cached:
                    filename=Path(temp)/(hashlib.sha256(url.encode()).hexdigest()+".tif")
                    pin=download_bounded(url,filename)
                    bytes_total+=pin["bytes"]
                    if bytes_total>MAX_TOTAL_BYTES:raise RuntimeError("450MB aggregate download limit")
                    cached[url]=(filename,pin)
                fn,pin=cached[url]
                with rasterio.open(fn) as ds:
                    record["buffers"]=[water_fraction(ds,site["lat"],site["lon"],r) for r in (100,500)]
                record["original_tiff_sha256"]=pin["sha256"]
                record["status"]="pixels_validated"
            except Exception as ex:
                record["status"]="source_or_pixel_unavailable"
                record["error"]=type(ex).__name__+": "+str(ex)[:180]
            out.append(record)
    groups=[]
    for s in STRATA:
        vals=[v for v in out if v["stratum"]==s]
        ok=[v for v in vals if v["status"]=="pixels_validated"]
        usable=[v for v in ok if v["buffers"][1]["coverage_ge_50pct"]]
        groups.append({
            "stratum":s,"events":len(vals),"pixel_successes":len(ok),
            "500m_coverage_ge_50pct":len(usable),
            "water_positive_500m":sum(v["buffers"][1]["n_water_pixels"]>0 for v in usable),
            "valid_fraction_by_event":[v["buffers"][1]["valid_fraction"] for v in usable],
            "water_fraction_by_event":[v["buffers"][1]["water_fraction_among_observed"] for v in usable],
        })
    report={"analysis":"real_naamp_vegetation_stratified_jrc_previous_month_v0_1",
            "manifest_sha256":MANIFEST_SHA,"nlcd_version":"USGS Annual NLCD Collection 1.2",
            "gsw_version":"EC JRC/Google GSW VER5-0 (monthly)",
            "source_licence":"Copernicus open use, attribution EC JRC/Google",
            "selection_on_acoustic_outcomes":False,"frog_counts_read":False,
            "response_variable_fit":False,"month_prior_to_survey_only":True,
            "direct_survey_date_hydrology_measured":False,
            "source_transfer_bytes":bytes_total,"groups":groups,"events":out}
    output=Path(out_path)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="events"},indent=2,sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    process(a.manifest,a.out)
