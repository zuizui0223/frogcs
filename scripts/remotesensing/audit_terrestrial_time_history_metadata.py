#!/usr/bin/env python3
"""Outcome-blind terrestrial time-history metadata feasibility from frozen E3 receipt.

Reads only E3 STAC scene metadata (not frog calling or Landsat pixel values).
Do not interpret scene availability as QA-qualified two-period NDMI coverage.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
from pathlib import Path

def eligible_date_span(row):
    dates=sorted(set(
        dt.date.fromisoformat(c["acquisition_date"])
        for c in row.get("candidates", [])
    ))
    span=(dates[-1]-dates[0]).days if len(dates)>1 else 0
    return len(dates), span

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--metadata",default="remotesensing/E3_NDMI_METADATA_COVERAGE_V0_1.json")
    parser.add_argument("--output",default="remotesensing/TERRESTRIAL_TIME_HISTORY_METADATA_FEASIBILITY_V0_1.json")
    args=parser.parse_args()
    source=Path(args.metadata)
    o=json.loads(source.read_text(encoding="utf-8"))
    if o.get("analysis")!="naamp_e3_ndmi_metadata_coverage_v0_1":
        raise ValueError("Unrecognized frozen E3 metadata source")
    if o.get("NDMI_values_read") or o.get("frog_endpoint_calculated"):
        raise ValueError("Expected an outcome-blind source")
    rows=o["metadata_run_rows"]
    seen=set()
    recs=[]
    for row in rows:
        rid=str(row["RunID"])
        if rid in seen: raise ValueError(f"Duplicate RunID: {rid}")
        seen.add(rid)
        n, span=eligible_date_span(row)
        year=int(row["survey_date"][:4])
        era="2001-2005" if year<=2005 else ("2006-2010" if year<=2010 else "2011-2015")
        recs.append({"RunID":rid,"route":str(row["route_cluster"]),"era":era,
                     "dates":n,"span_days":span,"two_date_ge16":n>=2 and span>=16})
    if not recs: raise ValueError("No focal RunIDs")

    n=len(recs)
    counts=collections.Counter(x["dates"] for x in recs)
    byera={}
    for era in ("2001-2005","2006-2010","2011-2015"):
        subset=[x for x in recs if x["era"]==era]
        byera[era]={
            "runids":len(subset),
            "two_dates_ge16":sum(x["two_date_ge16"] for x in subset),
            "two_date_fraction":sum(x["two_date_ge16"] for x in subset)/len(subset) if subset else None,
        }
    out={
        "analysis":"terrestrial_time_history_metadata_feasibility_v0_1",
        "contract":"revision/TERRESTRIAL_TEMPORAL_HISTORY_FEASIBILITY_V0_1.md",
        "source_metadata":str(source),
        "n_focal_runids":n,
        "n_distinct_routes":len({x["route"] for x in recs}),
        "at_least_two_scene_dates":sum(x["dates"]>=2 for x in recs),
        "at_least_three_scene_dates":sum(x["dates"]>=3 for x in recs),
        "at_least_two_dates_span_16d":sum(x["two_date_ge16"] for x in recs),
        "fraction_two_dates_span_16d":sum(x["two_date_ge16"] for x in recs)/n,
        "full_route_scene_date_count_distribution":{str(k):v for k,v in sorted(counts.items())},
        "by_survey_era":byera,
        "qa_validity_tested":False,
        "land_pixel_values_read":False,
        "frog_endpoint_calculated":False,
        "interpretation":"Necessary metadata availability only; not evidence of a QA-qualified terrestrial NDMI time series"
    }
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="full_route_scene_date_count_distribution"},indent=2))

if __name__=="__main__":
    main()
