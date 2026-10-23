#!/usr/bin/env python3
"""Combine annual C1V2 site-year CSV artifacts and audit vegetation variability.

Descriptive environment-side QC only. Does not load Counts.csv, CallingIndex,
species or any frog response. Refuses incomplete panels unless --allow-partial.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import statistics
import zipfile
from collections import defaultdict
from pathlib import Path

FRACTIONS=("forest","woody_wetland","emergent_wetland","open_water",
           "developed","shrub","grass_herb","agriculture")
PATTERN=re.compile(r"nlcd_c1v2_(\d{4})_site_year_buffers\.csv$")

def quantile(vals,p):
    a=sorted(vals)
    if not a:return None
    x=(len(a)-1)*p;lo=int(x);hi=min(lo+1,len(a)-1)
    return round(a[lo]+(a[hi]-a[lo])*(x-lo),5)

def ingest(path):
    with zipfile.ZipFile(path) as z:
        csvnames=[n for n in z.namelist() if PATTERN.search(n)]
        if len(csvnames)!=1:raise ValueError(f"{path}: expected one NLCD original CSV")
        y=int(PATTERN.search(csvnames[0]).group(1))
        receipts=[n for n in z.namelist() if n.endswith(f"nlcd_c1v2_{y}_receipt.json")]
        if len(receipts)!=1:raise ValueError(f"{path}: missing receipt")
        receipt=json.loads(z.read(receipts[0]))
        if (receipt.get("version")!="USGS Annual NLCD Collection 1.2" or
            receipt.get("year")!=y or
            receipt.get("counts_csv_downloaded") is not False or
            receipt.get("frog_outcomes_read") is not False or
            receipt.get("ecological_effects_estimated") is not False):
            raise ValueError(f"{path}: unverified source or outcome exposure")
        text=z.read(csvnames[0]).decode("utf-8-sig")
        csvrows=list(csv.DictReader(io.StringIO(text)))
        if len(csvrows)!=receipt["buffers"]["rows"]:
            raise ValueError(f"{path}: mismatch receipt row count")
        if not csvrows:raise ValueError(f"{path}: empty")
        forbidden={"Species","CallingIndex","Counts.csv","rain_contrast","wet_RunID","dry_RunID"}
        if any(c in forbidden for c in csvrows[0]):
            raise ValueError("frog outcome columns forbidden")
        for r in csvrows:
            if int(r["year"])!=y:raise ValueError("year drift in CSV")
            if int(r["radius_m"]) not in (100,500):raise ValueError("unknown buffer size")
            if r["qc_status"] not in ("ok","low_coverage"):raise ValueError("unknown QC label")
            n=int(r["n_buffer_pixels"]);v=int(r["n_valid_pixels"])
            if n<=0 or not 0<=v<=n:raise ValueError("pixel denominator invalid")
            if abs(float(r["coverage_fraction"])-v/n)>1e-5:raise ValueError("coverage mismatch")
            if r["qc_status"]=="ok":
                vals=[float(r[f"frac_{k}"]) for k in FRACTIONS]
                if any(not 0<=f<=1 for f in vals) or sum(vals)>1.00002:
                    raise ValueError("invalid categorical fractions")
            elif any(r[f"frac_{k}"].strip() for k in FRACTIONS):
                raise ValueError("nonempty fractions on low-coverage row")
        return y,csvrows,receipt

def aggregate(paths,years,expected_site_years=None,require_complete=True):
    rows=[];seen=set();receipts={};source_sha={}
    for path in sorted(paths):
        year,records,receipt=ingest(Path(path))
        if year in receipts:raise ValueError("duplicate annual source")
        receipts[year]=receipt
        source_sha[year]=hashlib.sha256(Path(path).read_bytes()).hexdigest()
        for r in records:
            key=(r["RouteNumber"],r["SiteID"],int(r["year"]),int(r["radius_m"]))
            if key in seen:raise ValueError("duplicate site-year-radius key")
            seen.add(key);rows.append(r)
    years=set(years)
    absent=sorted(years-set(receipts))
    if require_complete and absent:raise ValueError(f"missing years: {absent}")
    siteyears={(r["RouteNumber"],r["SiteID"],int(r["year"])) for r in rows}
    if require_complete and expected_site_years is not None and len(siteyears)!=expected_site_years:
        raise ValueError(f"site-year count mismatch {len(siteyears)} versus {expected_site_years}")
    if len(rows)!=2*len(siteyears):
        raise ValueError("missing 100/500m pair for some site-years")
    counts=defaultdict(int);metrics={}
    for radius in (100,500):
        group=[r for r in rows if int(r["radius_m"])==radius]
        ok=[r for r in group if r["qc_status"]=="ok"]
        counts[radius]=len(ok)
        means={}
        for name in FRACTIONS:
            values=[float(r[f"frac_{name}"]) for r in ok]
            means[name]={"mean":round(statistics.fmean(values),5) if values else None,
                         "p10":quantile(values,.1),"median":quantile(values,.5),
                         "p90":quantile(values,.9),
                         "fraction_zero":round(sum(v==0 for v in values)/len(values),5) if values else None}
        metrics[radius]={"n_site_years":len(group),"n_ok":len(ok),
                         "valid_fraction":round(len(ok)/len(group),5) if group else None,
                         "fractions":means}
    # Descriptive changes over the first and last sampled year at the same SiteID.
    time_series=defaultdict(list)
    for r in rows:
        if r["qc_status"]=="ok":
            time_series[(r["RouteNumber"],r["SiteID"],int(r["radius_m"]))].append(r)
    changes={}
    for rad in (100,500):
        sample=[]
        for (route,site,radius),v in time_series.items():
            if radius!=rad or len(v)<2:continue
            v=sorted(v,key=lambda r:int(r["year"]))
            if int(v[-1]["year"])-int(v[0]["year"])<5:continue
            sample.append((v[0],v[-1]))
        changes[rad]={"n_sites_span_ge_5y":len(sample)}
        for k in ("forest","woody_wetland","emergent_wetland","developed","agriculture"):
            ds=[abs(float(b[f"frac_{k}"])-float(a[f"frac_{k}"])) for a,b in sample]
            changes[rad][k]={"median_absolute_fraction_change":quantile(ds,.5),
                             "p90_absolute_fraction_change":quantile(ds,.9),
                             "share_with_10pp_or_more_change":round(sum(d>=.1 for d in ds)/len(ds),5) if ds else None}
    return rows,{"study":"outcome_blind_naamp_nlcd_c1v2_2001_2015_panel_v0_1",
                "source":"USGS Annual NLCD Collection 1.2",
                "no_frog_outcomes_read":True,
                "ecological_effect_estimated":False,
                "required_years":sorted(years),
                "years_present":sorted(receipts),
                "missing_years":absent,
                "is_complete_panel":not absent,
                "n_site_years":len(siteyears),
                "n_buffer_rows":len(rows),
                "unique_physical_sites":len({(k[0],k[1]) for k in siteyears}),
                "site_years_by_year":{str(y):sum(k[2]==y for k in siteyears) for y in sorted(receipts)},
                "source_artifact_sha256":source_sha,
                "coverage_metrics":metrics,
                "earliest_latest_within_site_change":changes}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    p.add_argument("--allow-partial",action="store_true")
    p.add_argument("--expected-site-years",type=int,default=64779)
    a=p.parse_args()
    archives=list(a.artifact_dir.glob("*.zip"))
    if not archives:raise RuntimeError("no C1V2 source archives")
    rows,summary=aggregate(archives,range(2001,2016),
                           a.expected_site_years,require_complete=not a.allow_partial)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    with (a.out_dir/"nlcd_c1v2_2001_2015_site_year_buffers.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=rows[0].keys())
        wr.writeheader();wr.writerows(sorted(rows,key=lambda r:(int(r["year"]),r["RouteNumber"],r["SiteID"],int(r["radius_m"]))))
    (a.out_dir/"nlcd_c1v2_vegetation_coverage_and_change.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=="__main__":main()
