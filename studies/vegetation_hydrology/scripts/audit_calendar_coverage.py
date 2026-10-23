#!/usr/bin/env python3
"""Outcome-blind physical-site/year coverage audit. Reads no frog calls."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

REQUIRED = {"State", "RouteNumber", "SiteID", "RunID", "SurveyYear", "SurveyDate"}

def summarize(rows):
    site_years = defaultdict(set)
    sy_sites, sy_runs, sy_visits = defaultdict(set), defaultdict(set), Counter()
    route_states, site_states = defaultdict(set), defaultdict(set)
    visits, runs = set(), set()
    total = 0
    for r in rows:
        state, route, site, run = (str(r[k]).strip() for k in ("State","RouteNumber","SiteID","RunID"))
        year = int(r["SurveyYear"])
        if not (state and route and site and run and 2001<=year<=2015):
            raise ValueError("Invalid identity, state or study year")
        if not str(r["SurveyDate"]).startswith(str(year)+"-"):
            raise ValueError("SurveyDate inconsistent with SurveyYear")
        key = (route,site)
        event=(run,route,site)
        if event in visits:
            raise ValueError(f"duplicate RunID x physical SiteID: {event}")
        visits.add(event)
        runs.add(run)
        route_states[route].add(state)
        site_states[key].add(state)
        site_years[key].add(year)
        sy_sites[(state,year)].add(key)
        sy_runs[(state,year)].add(run)
        sy_visits[(state,year)] += 1
        total += 1
    if any(len(v)!=1 for v in route_states.values()) or any(len(v)!=1 for v in site_states.values()):
        raise ValueError("RouteNumber/site identities cross State: investigate join")
    ny = [len(v) for v in site_years.values()]
    pairs=sum(ny)
    ssc=Counter(next(iter(site_states[k])) for k in site_years)
    by_sy=[{"State":s,"SurveyYear":y,"unique_site_years":len(sy_sites[s,y]),
            "unique_runs":len(sy_runs[s,y]),"site_visits":sy_visits[s,y]}
           for s,y in sorted(sy_sites)]
    result={"analysis":"naamp_outcome_blind_site_year_coverage_v0_1",
            "total_station_visits":total,"unique_runs":len(runs),"unique_routes":len(route_states),
            "unique_physical_sites":len(site_years),"unique_site_years":pairs,
            "full_site_year_grid_2001_2015":len(site_years)*15,
            "fraction_full_grid_observed":round(pairs/(len(site_years)*15),6) if site_years else None,
            "median_surveyed_years_per_site":median(ny) if ny else None,
            "sites_observed_ge_2_years":sum(v>=2 for v in ny),
            "sites_observed_ge_3_years":sum(v>=3 for v in ny),
            "sites_observed_ge_5_years":sum(v>=5 for v in ny),
            "n_states":len(ssc),"sites_by_state":dict(sorted(ssc.items())),
            "counts_csv_read":False,"frog_outcomes_accessed":False,
            "interpretation":"Geospatial availability calendar, not the manuscript matched-pair sample"}
    return by_sy,result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--site-calendar",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    args=p.parse_args()
    with args.site_calendar.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or not REQUIRED.issubset(rd.fieldnames):
            raise ValueError("missing required fields")
        sy,report=summarize(rd)
    report["calendar_sha256"]=hashlib.sha256(args.site_calendar.read_bytes()).hexdigest()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    with (args.out_dir/"site_year_coverage_by_state.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=["State","SurveyYear","unique_site_years","unique_runs","site_visits"])
        wr.writeheader()
        wr.writerows(sy)
    (args.out_dir/"site_year_coverage.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True,indent=2))
if __name__=="__main__":
    main()
