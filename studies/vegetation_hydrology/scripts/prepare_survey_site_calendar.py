#!/usr/bin/env python3
"""Build an outcome-blind NAAMP survey-site calendar from Runs.csv + Stops.csv.

No Counts.csv is opened. This is a coverage universe, not the paper's
canonical 7,848-run eligibility set. Never label it 'paper sample'.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

PIN_RUNS = "ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730"
PIN_STOPS = "28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f"

OUTPUT_COLUMNS = ["RunID", "State", "RouteNumber", "SiteID", "StopNumber", "SurveyDate", "SurveyYear"]


def read_csv(path, needed):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(needed).issubset(reader.fieldnames):
            raise ValueError(f"{Path(path).name}: missing {set(needed) - set(reader.fieldnames or [])}")
        return list(reader)


def parse_date(raw):
    text = (raw or "").strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def build(runs_file, stops_file, accepted_file):
    coords = read_csv(accepted_file, ["RouteNumber", "SiteID", "status"])
    accepted = {(r["RouteNumber"].strip(), r["SiteID"].strip()) for r in coords if r["status"].strip() == "accepted"}
    if len(accepted) != len(coords):
        raise ValueError("accepted file contains held sites or duplicate keys")
    runs = {}
    dropped = Counter()
    for r in read_csv(runs_file, ["RunID", "State", "RouteNumber", "SurveyDate", "UnifiedProtocol"]):
        d = parse_date(r["SurveyDate"])
        if d is None or not 2001 <= d.year <= 2015:
            dropped["invalid_or_out_of_period_run_date"] += 1
            continue
        if str(r["UnifiedProtocol"]).strip() != "1":
            dropped["not_unified_protocol"] += 1
            continue
        rid = r["RunID"].strip()
        if not rid or not r["RouteNumber"].strip():
            dropped["run_missing_key"] += 1
            continue
        if rid in runs:
            raise ValueError(f"duplicate RunID {rid}")
        runs[rid] = {"RunID": rid, "State": r["State"].strip(), "RouteNumber": r["RouteNumber"].strip(),
                     "SurveyDate": d.isoformat(), "SurveyYear": d.year}
    station_visits = {}
    n_stop_rows = 0
    for s in read_csv(stops_file, ["RunID", "SiteID", "StopNumber", "SkippedStop"]):
        n_stop_rows += 1
        rid = s["RunID"].strip()
        if rid not in runs:
            dropped["stop_run_not_eligible_for_calendar"] += 1
            continue
        if s["SkippedStop"].strip() != "0":
            dropped["skipped_stop"] += 1
            continue
        route = runs[rid]["RouteNumber"]
        sid = s["SiteID"].strip()
        if (route, sid) not in accepted:
            dropped["no_accepted_site_coordinate"] += 1
            continue
        key = (rid, sid)
        if key in station_visits:
            raise ValueError(f"duplicate run + physical SiteID visit {key}")
        station_visits[key] = {**runs[rid], "SiteID": sid, "StopNumber": s["StopNumber"].strip()}
    rows = [station_visits[k] for k in sorted(station_visits)]
    return rows, {"input_stop_rows": n_stop_rows, "calendar_station_visits": len(rows),
                  "calendar_unique_runs": len({r["RunID"] for r in rows}),
                  "calendar_unique_physical_sites": len({(r["RouteNumber"], r["SiteID"]) for r in rows}),
                  "exclusion_counts": dict(sorted(dropped.items())), "counts_csv_opened": False,
                  "matches_manuscript_eligibility": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", required=True)
    p.add_argument("--stops", required=True)
    p.add_argument("--accepted-coordinates", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    for path, expected in ((a.runs, PIN_RUNS), (a.stops, PIN_STOPS)):
        got = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if got != expected:
            raise ValueError(f"source SHA256 drift: {Path(path).name}: {got} != {expected}")
    rows, report = build(a.runs, a.stops, a.accepted_coordinates)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    out.with_suffix(".audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
