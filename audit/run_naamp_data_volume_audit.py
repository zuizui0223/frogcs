#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "NAAMP_DATA_VOLUME_AUDIT_RECEIPT_V0_1.json"
ITEM_ID = "583dc314e4b0d1899f9dea8d"
ITEM_URL = f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"

PINS = {
    "Runs.csv": "ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
    "Stops.csv": "28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
    "Counts.csv": "60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086",
}
POS = {"1", "2", "3"}
TEMP_LO, TEMP_HI = -10.0, 45.0
RAIN_LO, RAIN_HI = 0.0, 180.0


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "frogcs-data-volume-audit/0.1", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "frogcs-data-volume-audit/0.1"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def parse_year(x):
    m = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", str(x or ""))
    return int(m.group(1)) if m else None


def parse_doy(x):
    s = str(x or "").strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).timetuple().tm_yday
        except Exception:
            pass
    return None


def quantile(vals, q):
    x = sorted(vals)
    if not x:
        return None
    if len(x) == 1:
        return float(x[0])
    pos = (len(x) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(x[lo])
    w = pos - lo
    return float(x[lo] * (1 - w) + x[hi] * w)


def main():
    item = get_json(ITEM_URL)
    meta = {f.get("name"): f for f in (item.get("files") or []) if f.get("name")}

    raw_bytes = {}
    rows = {}
    files = {}
    for name in ("Runs.csv", "Stops.csv", "Counts.csv", "Species.csv"):
        if name not in meta:
            raise RuntimeError(f"missing ScienceBase file: {name}")
        b = get_bytes(file_url(meta[name]))
        sha = hashlib.sha256(b).hexdigest()
        if name in PINS and sha != PINS[name]:
            raise RuntimeError(f"hash drift {name}: {sha}")
        raw_bytes[name] = b
        rows[name] = list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
        files[name] = {
            "rows": len(rows[name]),
            "bytes": len(b),
            "decimal_mb": len(b) / 1_000_000,
            "mib": len(b) / (1024 ** 2),
            "sha256": sha,
            "existing_analysis_pin_verified": name in PINS,
        }

    # Replicate the current ecological-pulse eligible-run filter exactly.
    run_meta = {}
    for r in rows["Runs.csv"]:
        y = parse_year(r.get("SurveyYear")) or parse_year(r.get("SurveyDate"))
        d = parse_doy(r.get("SurveyDate"))
        if y is None or d is None or not 2001 <= y <= 2015:
            continue
        if (r.get("UnifiedProtocol") or "").strip() != "1":
            continue
        rid = (r.get("RunID") or "").strip()
        rn = (r.get("RunNumber") or "").strip()
        state = (r.get("State") or "").strip()
        route = (r.get("RouteNumber") or "").strip()
        rtype = (r.get("RouteType") or "").strip()
        if not rid or rn not in {"1", "2", "3", "4"} or not state or not route or not rtype:
            continue
        try:
            rain = float((r.get("DaysSinceRain") or "").strip())
        except Exception:
            continue
        if not math.isfinite(rain) or not RAIN_LO <= rain <= RAIN_HI:
            continue
        run_meta[rid] = {
            "RunID": rid,
            "State": state,
            "RouteNumber": route,
            "RunNumber": rn,
            "RouteType": rtype,
            "SurveyYear": y,
            "doy": d,
            "DaysSinceRain": rain,
            "TempScale": (r.get("TempScale") or "").strip(),
        }

    sampled = defaultdict(set)
    temps = defaultdict(list)
    candidate_stop_rows = 0
    for s in rows["Stops.csv"]:
        rid = (s.get("RunID") or "").strip()
        if rid not in run_meta or (s.get("SkippedStop") or "").strip() != "0":
            continue
        st = (s.get("StopNumber") or "").strip()
        if not st:
            continue
        candidate_stop_rows += 1
        sampled[rid].add(st)
        try:
            t = float((s.get("AirTemp") or "").strip())
        except Exception:
            continue
        scale = run_meta[rid]["TempScale"]
        if scale == "F":
            t = (t - 32.0) * 5.0 / 9.0
        elif scale != "C":
            continue
        if math.isfinite(t):
            temps[rid].append(t)

    eligible_ids = set()
    for rid, r in run_meta.items():
        stops = sampled.get(rid, set())
        ts = temps.get(rid, [])
        if len(stops) != 10 or len(ts) < 8:
            continue
        mt = sum(ts) / len(ts)
        if not TEMP_LO <= mt <= TEMP_HI:
            continue
        eligible_ids.add(rid)

    # Raw positive records and unique positive cells.
    raw_positive_rows = 0
    raw_positive_cells = set()
    raw_positive_taxa = set()

    eligible_positive_rows = 0
    eligible_positive_cells = set()
    eligible_active_stops = set()
    eligible_taxa = set()
    taxa_by_run = defaultdict(set)

    for c in rows["Counts.csv"]:
        rid = (c.get("RunID") or "").strip()
        st = (c.get("StopNumber") or "").strip()
        sp = (c.get("Species") or "").strip()
        ci = (c.get("CallingIndex") or "").strip()
        if ci in POS and sp:
            raw_positive_rows += 1
            raw_positive_cells.add((rid, st, sp))
            raw_positive_taxa.add(sp)

        if rid not in eligible_ids or st not in sampled.get(rid, set()) or ci not in POS or not sp:
            continue
        eligible_positive_rows += 1
        eligible_positive_cells.add((rid, st, sp))
        eligible_active_stops.add((rid, st))
        eligible_taxa.add(sp)
        taxa_by_run[rid].add(sp)

    positive_cells_by_run = Counter(rid for rid, _, _ in eligible_positive_cells)
    richness_by_run = [len(taxa_by_run.get(rid, set())) for rid in eligible_ids]

    # Reproduce adjacent-year matched-pair construction.
    groups = defaultdict(list)
    for rid in eligible_ids:
        r = run_meta[rid]
        groups[(r["State"], r["RouteNumber"], r["RunNumber"])].append(r)

    pair_rows = []
    for key, g in groups.items():
        g = sorted(g, key=lambda z: (z["SurveyYear"], z["RunID"]))
        for i in range(len(g) - 1):
            a, b = g[i], g[i + 1]
            if a["DaysSinceRain"] == b["DaysSinceRain"]:
                continue
            wet, dry = (a, b) if a["DaysSinceRain"] < b["DaysSinceRain"] else (b, a)
            pair_rows.append({
                "wet": wet["RunID"],
                "dry": dry["RunID"],
                "state": wet["State"],
                "route": wet["RouteNumber"],
                "year_gap": abs(a["SurveyYear"] - b["SurveyYear"]),
            })

    pair_run_ids = {p[k] for p in pair_rows for k in ("wet", "dry")}
    pair_positive_cells = {x for x in eligible_positive_cells if x[0] in pair_run_ids}
    pair_positive_rows = 0
    for c in rows["Counts.csv"]:
        rid = (c.get("RunID") or "").strip()
        st = (c.get("StopNumber") or "").strip()
        sp = (c.get("Species") or "").strip()
        ci = (c.get("CallingIndex") or "").strip()
        if rid in pair_run_ids and st in sampled.get(rid, set()) and ci in POS and sp:
            pair_positive_rows += 1

    eligible_stop_opportunities = sum(len(sampled[rid]) for rid in eligible_ids)
    potential_cells = eligible_stop_opportunities * len(eligible_taxa)

    era5_receipt = json.loads((ROOT / "exploration" / "NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_RECEIPT_V0_1.json").read_text())
    era = era5_receipt["coverage"]
    era_hours = int(era["weather_runs"]) * int(era5_receipt["era5"]["primary_window_hours"])

    core_names = ("Runs.csv", "Stops.csv", "Counts.csv")
    out = {
        "analysis": "naamp_data_volume_audit_v0_1",
        "contract": "audit/NAAMP_DATA_VOLUME_AUDIT_CONTRACT_V0_1.json",
        "status": "audit_only_no_scientific_endpoint_changed",
        "source": {
            "sciencebase_item_id": ITEM_ID,
            "doi": "10.5066/F7G44NG0",
            "raw_period": "1994-2015",
            "analysis_period": "2001-2015 unified protocol",
            "files": files,
            "core_frog_files_bytes": sum(files[n]["bytes"] for n in core_names),
            "core_frog_files_decimal_mb": sum(files[n]["bytes"] for n in core_names) / 1_000_000,
            "core_frog_files_mib": sum(files[n]["bytes"] for n in core_names) / (1024 ** 2),
        },
        "raw_frog_records": {
            "runs_rows": len(rows["Runs.csv"]),
            "stops_rows": len(rows["Stops.csv"]),
            "counts_rows": len(rows["Counts.csv"]),
            "species_rows": len(rows["Species.csv"]),
            "raw_positive_call_rows_ci1_3": raw_positive_rows,
            "raw_unique_positive_run_stop_taxon_cells": len(raw_positive_cells),
            "raw_positive_taxa_labels": len(raw_positive_taxa),
            "duplicate_positive_rows_beyond_unique_cells": raw_positive_rows - len(raw_positive_cells),
        },
        "eligible_frog_analysis": {
            "eligible_runs": len(eligible_ids),
            "routes": len({(run_meta[r]["State"], run_meta[r]["RouteNumber"]) for r in eligible_ids}),
            "states": len({run_meta[r]["State"] for r in eligible_ids}),
            "unique_run_stop_opportunities": eligible_stop_opportunities,
            "eligible_positive_call_rows_ci1_3": eligible_positive_rows,
            "eligible_unique_positive_run_stop_taxon_cells": len(eligible_positive_cells),
            "eligible_active_run_stop_visits": len(eligible_active_stops),
            "eligible_taxa_labels": len(eligible_taxa),
            "potential_taxon_x_stop_x_run_cells": potential_cells,
            "positive_fraction_of_potential_cells": len(eligible_positive_cells) / potential_cells if potential_cells else None,
            "positive_cells_per_run": {
                "mean": sum(positive_cells_by_run.values()) / len(eligible_ids),
                "median": median([positive_cells_by_run.get(r, 0) for r in eligible_ids]),
                "q05": quantile([positive_cells_by_run.get(r, 0) for r in eligible_ids], 0.05),
                "q95": quantile([positive_cells_by_run.get(r, 0) for r in eligible_ids], 0.95),
            },
            "taxa_per_run": {
                "mean": sum(richness_by_run) / len(richness_by_run),
                "median": median(richness_by_run),
                "q05": quantile(richness_by_run, 0.05),
                "q95": quantile(richness_by_run, 0.95),
            },
        },
        "matched_pair_use": {
            "pairs": len(pair_rows),
            "routes": len({(p["state"], p["route"]) for p in pair_rows}),
            "states": len({p["state"] for p in pair_rows}),
            "pair_side_survey_instances": 2 * len(pair_rows),
            "unique_runs_used": len(pair_run_ids),
            "unique_run_stop_opportunities": 10 * len(pair_run_ids),
            "positive_call_rows_ci1_3_in_unique_pair_runs": pair_positive_rows,
            "unique_positive_run_stop_taxon_cells_in_unique_pair_runs": len(pair_positive_cells),
            "exact_consecutive_year_pairs": sum(1 for p in pair_rows if p["year_gap"] == 1),
            "fraction_exact_consecutive_year": sum(1 for p in pair_rows if p["year_gap"] == 1) / len(pair_rows),
        },
        "rain_data_volume": {
            "naamp_days_since_rain": {
                "eligible_run_level_values": len(eligible_ids),
                "unique_runs_used_in_matched_pairs": len(pair_run_ids),
                "pair_side_values_with_run_reuse": 2 * len(pair_rows),
                "unit": "days since last reported rain",
            },
            "era5_72h_total_precipitation": {
                "weather_linked_runs": int(era["weather_runs"]),
                "weather_linked_principal_history_pairs": int(era["weather_prior_history_pairs"]),
                "routes": int(era["routes"]),
                "states": int(era["states"]),
                "derived_72h_totals": int(era["weather_runs"]),
                "hours_per_total": int(era5_receipt["era5"]["primary_window_hours"]),
                "run_hour_precipitation_values_sampled": era_hours,
                "note": "run-hour sample count; not deduplicated unique ERA5 grid-time cells",
            },
        },
        "boundaries": [
            "Counts.csv is sparse detection/calling data, not a dense zero-filled taxon matrix.",
            "potential_taxon_x_stop_x_run_cells is a matrix opportunity count, not a raw record count.",
            "pair-side survey instances count repeated use of a run if it participates in adjacent pairs; unique_runs_used removes that reuse.",
            "ERA5 run-hour count is the number of 72 hourly values sampled for each linked run, not deduplicated grid-time cells.",
            "No analysis sample, model, endpoint or inferential result is changed by this audit.",
        ],
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
