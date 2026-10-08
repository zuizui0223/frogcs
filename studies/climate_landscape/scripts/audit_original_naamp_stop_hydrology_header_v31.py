#!/usr/bin/env python3
"""Source-only NAAMP 2010–2015 stop wetness/hydrology SCHEMA audit.

Reads exclusively pinned original USGS Runs.csv and Stops.csv.
No Counts.csv; no species, calling index or ecological endpoint.
The purpose is to distinguish an Iowa DNR contemporary Wet/Dry datasheet
field from what the separately released historical USGS NAAMP archive holds.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_naamp_observation_panel import SOURCE_PINS
from download_public_naamp_sources import METADATA, fetch

FILES = ("Runs.csv", "Stops.csv")
FOCAL = ("360104", "360412")
HISTORIC_YEARS = set(range(2010, 2016))
# Identify names conservatively. A field match alone is not validation of its semantics.
HYDRO_PATTERN = re.compile(
    r"wet|dry|hydro|inund|flood|water|pond|pool|moist|substrate|flow|depth",
    flags=re.IGNORECASE,
)
# Atmospheric/rainfall/temperature fields are relevant context, but are not
# automatically direct local standing-water measurements.
BROAD_WEATHER_PATTERN = re.compile(r"rain|temp|precip|weather|humidity|wind", re.I)


def extract_pinned_csv(name: str, item: dict) -> tuple[list[str], list[dict], dict]:
    byname = {str(f.get("name")): f for f in item.get("files", [])}
    if name not in byname:
        raise ValueError(f"official metadata lacks {name}")
    entry = byname[name]
    url = entry.get("downloadUri") or entry.get("url") or entry.get("uri")
    if not url or not url.startswith("https://") or not re.match(
        r"https://(?:www\.)?sciencebase\.gov/", url, re.I
    ):
        raise ValueError("untrusted source URL")
    payload = fetch(url)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != SOURCE_PINS[name]:
        raise ValueError(f"wrong USGS source hash: {name} = {digest}")
    handle = io.StringIO(payload.decode("utf-8-sig"), newline="")
    reader = csv.DictReader(handle)
    fields = list(reader.fieldnames or [])
    if not fields:
        raise ValueError("missing headers")
    rows = list(reader)
    return fields, rows, {"sha256": digest, "rows": len(rows), "bytes": len(payload)}


def study_year(row: dict) -> int | None:
    vals = (row.get("SurveyYear", ""), row.get("SurveyDate", ""))
    for value in vals:
        m = re.search(r"(?<!\d)(20\d{2})(?!\d)", str(value))
        if m:
            return int(m.group(1))
    return None


def audit(run_headers: list[str], runs: list[dict], stop_headers: list[str], stops: list[dict]) -> dict:
    for cols, need, source in (
        (run_headers, ("RunID", "State", "RouteNumber", "SurveyYear"), "Runs.csv"),
        (stop_headers, ("RunID", "StopNumber", "SiteID"), "Stops.csv"),
    ):
        if not set(need).issubset(cols):
            raise ValueError(f"missing required keys in {source}: {set(need)-set(cols)}")
    candidates = [c for c in stop_headers if HYDRO_PATTERN.search(c)]
    atmospheric = [c for c in stop_headers if BROAD_WEATHER_PATTERN.search(c)]
    # Dynamic local wet/dry indicators must not be inferred merely because AirTemp
    # or DaysSinceRain occurs at route or stop level.
    run_lookup = {}
    for r in runs:
        k = str(r["RunID"]).strip()
        if k in run_lookup:
            raise ValueError("duplicate RunID")
        run_lookup[k] = r
    route_raw = defaultdict(set)
    coverage = defaultdict(lambda: {"stop_rows": 0, "candidate_value_counts": Counter(),
                                   "candidate_observed_codes": defaultdict(Counter)})
    for s in stops:
        r = run_lookup.get(str(s.get("RunID", "")).strip())
        if not r:
            continue
        route = str(r.get("RouteNumber", "")).strip()
        if route not in FOCAL:
            continue
        yr = study_year(r)
        if yr not in HISTORIC_YEARS:
            continue
        state = str(r.get("State", "")).strip()
        route_raw[route].add(state)
        key = f"{route}/{yr}"
        coverage[key]["stop_rows"] += 1
        for col in candidates:
            value = str(s.get(col, "")).strip()
            if value and value.upper() not in ("NA", "N/A", "NULL", "."):
                coverage[key]["candidate_value_counts"][col] += 1
                coverage[key]["candidate_observed_codes"][col][value] += 1
    by_group = {}
    for key, cell in sorted(coverage.items()):
        by_group[key] = {"stop_rows": cell["stop_rows"],
                         "nonempty_by_candidate_column": dict(cell["candidate_value_counts"]),
                         "candidate_code_frequencies": {
                             col: dict(codes.most_common(30)) for col, codes in
                             cell["candidate_observed_codes"].items()
                         }}
    return {
        "analysis": "original_naamp_focal_stop_hydrology_header_audit_v31",
        "scope": "source-only historical USGS NAAMP, focal Iowa route IDs 360104/360412, 2010–2015",
        "runs_csv_columns": run_headers,
        "stops_csv_columns": stop_headers,
        "stop_level_hydrology_candidate_columns": candidates,
        "stop_level_weather_context_columns": atmospheric,
        "route_code_state_values": {key: sorted(val) for key, val in route_raw.items()},
        "focal_route_year_coverage": by_group,
        "historical_wetdry_variable_confirmed": False,
        "validation_note": "Column existence/values alone never establish that a field represents observed local standing water; interpret historical field definitions before changing this flag.",
        "counts_csv_opened": False,
        "calling_outcomes_opened": False,
        "source_era_is_current_iowa_form": False,
        "rc6_scientific_bundle_untouched": True,
        "source_selection_not_driven_by_frog_outcomes": True,
    }


def main():
    item = json.loads(fetch(METADATA).decode("utf-8"))
    run_headers, runs, run_receipt = extract_pinned_csv("Runs.csv", item)
    stop_headers, stops, stop_receipt = extract_pinned_csv("Stops.csv", item)
    result = audit(run_headers, runs, stop_headers, stops)
    result["source_receipts"] = {"Runs.csv": run_receipt, "Stops.csv": stop_receipt}
    out = Path("studies/climate_landscape/receipts/NAAMP_ORIGINAL_STOP_HYDROLOGY_HEADER_ACTUAL_V31.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_rows": run_receipt["rows"], "stop_rows": stop_receipt["rows"],
                      "stop_columns": stop_headers,
                      "hydrology_candidate_fields": result["stop_level_hydrology_candidate_columns"],
                      "focal_years": sorted(result["focal_route_year_coverage"]),
                      "calling_outcomes_opened": False,
                      "receipt_path": str(out)}, sort_keys=True))


if __name__ == "__main__":
    main()
