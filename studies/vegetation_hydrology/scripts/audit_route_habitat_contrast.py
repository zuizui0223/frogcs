#!/usr/bin/env python3
"""Route-balanced, outcome-blind NLCD habitat contrast audit.

Use original-year 500-m site land-cover; average surveyed years within
each physical SiteID before route comparisons. Contrasts describe the
available within-route environmental variation, not frog habitat choice.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import median

PIN_SHA="137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a"
METRICS=("wetland","open_water","forest","developed","agriculture")
THRESHOLDS=(.10,.25)

def audit(rows,min_stations=8,strict=False):
    by_site=defaultdict(list); by_routeyear=defaultdict(list); seen=set()
    n500=0
    for row in rows:
        if int(row["radius_m"])!=500:continue
        key=(row["RouteNumber"],row["SiteID"],int(row["year"]))
        if key in seen:raise ValueError(f"duplicate 500m site-year key {key}")
        seen.add(key)
        if row["qc_status"]!="ok":raise ValueError("non-QC 500m row")
        metrics={
            "wetland":float(row["frac_woody_wetland"])+float(row["frac_emergent_wetland"]),
            "open_water":float(row["frac_open_water"]),
            "forest":float(row["frac_forest"]),
            "developed":float(row["frac_developed"]),
            "agriculture":float(row["frac_agriculture"])}
        if not all(0<=v<=1.00001 for v in metrics.values()):
            raise ValueError("invalid class fraction")
        by_site[key[:2]].append(metrics)
        by_routeyear[(key[0],key[2])].append(metrics)
        n500+=1
    if strict and (n500!=64779 or len(by_site)!=11588):
        raise ValueError("unexpected full-panel coverage")
    if not by_site:raise ValueError("empty 500m source")
    route_site=defaultdict(list)
    site_mean={}
    for key,site_years in by_site.items():
        m={k:sum(v[k] for v in site_years)/len(site_years) for k in METRICS}
        site_mean[key]=m
        route_site[key[0]].append(m)

    def contrasts(data):
        kept=[s for s in data.values() if len(s)>=min_stations]
        out={"n_groups":len(kept),"min_stations":min_stations,
             "median_n_stations":median(len(s) for s in kept) if kept else None}
        for metric in METRICS:
            spread=[max(x[metric] for x in s)-min(x[metric] for x in s)
                    for s in kept]
            out[metric]={
                "median_range_pp":round(100*median(spread),3) if spread else None,
                "ge_10pp_count":sum(x>=THRESHOLDS[0] for x in spread),
                "ge_10pp_share":round(sum(x>=THRESHOLDS[0] for x in spread)/len(spread),6) if spread else None,
                "ge_25pp_count":sum(x>=THRESHOLDS[1] for x in spread),
                "ge_25pp_share":round(sum(x>=THRESHOLDS[1] for x in spread)/len(spread),6) if spread else None}
        return out

    route=contrasts(route_site)
    route_year=contrasts(by_routeyear)
    n_sites=len(site_mean)
    wet_no_open=sum(s["wetland"]>=.1 and s["open_water"]<.01 for s in site_mean.values())
    return {
        "study":"naamp_nlcd_c1v2_outcome_blind_route_habitat_contrast_v0_1",
        "source":"USGS Annual NLCD Collection 1.2 2001-2015; 500-m",
        "site_years_500m":n500, "physical_sites":n_sites,
        "route_balanced_once_per_route":route,
        "route_year_descriptive_not_independent":route_year,
        "site_level_veg_wetland_ge10pct_and_open_water_lt1pct":{
             "sites":wet_no_open,"fraction":round(wet_no_open/n_sites,6)},
        "no_frog_outcomes_accessed":True,
        "not_evidence_of_frog_habitat_selection":True,
        "boundary":"Repeated route-year rows are not independent; geographic survey selection and annual-cover timing may bias habitat estimates."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nlcd-csv",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--allow-partial",action="store_true")
    args=p.parse_args()
    sha=hashlib.sha256(args.nlcd_csv.read_bytes()).hexdigest()
    if not args.allow_partial and sha!=PIN_SHA:
        raise ValueError(f"original panel file checksum drift: {sha}")
    with args.nlcd_csv.open(newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        fields=rd.fieldnames or []
        needed={"RouteNumber","SiteID","year","radius_m","qc_status","frac_woody_wetland",
                "frac_emergent_wetland","frac_open_water","frac_forest","frac_developed","frac_agriculture"}
        if not needed.issubset(fields) or {"Species","CallingIndex"}.intersection(fields):
            raise ValueError("wrong land-cover input or forbidden frog response fields")
        report=audit(rd,strict=not args.allow_partial)
    report["source_csv_sha256"]=sha
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
