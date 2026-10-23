#!/usr/bin/env python3
"""Compile *pre-survey* DSWE scene-level water coverage; no acoustic outcomes.

Input scene summaries must have QA-filtered valid_pixel_n and water_pixel_n
computed from the documented DSWE band/class configuration at each SiteID.
Clouds/no-data are never equivalent to dry land. No scene after the survey date
may contribute, including the remainder of the survey's calendar month.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REQUIRED_SCENE = {"RouteNumber", "SiteID", "scene_id", "acquisition_date", "valid_pixel_n", "water_pixel_n", "radius_m"}
REQUIRED_VISIT = {"RunID", "RouteNumber", "SiteID", "SurveyDate"}
OUTPUT = ["RunID", "RouteNumber", "SiteID", "SurveyDate", "radius_m", "lookback_days", "scene_n", "valid_pixel_n",
          "water_pixel_n", "water_fraction", "days_since_last_valid_scene", "qc_status"]


def read_csv(p, required):
    with Path(p).open(newline="", encoding="utf-8-sig") as f:
        d = csv.DictReader(f)
        if not d.fieldnames or not required.issubset(d.fieldnames):
            raise ValueError(f"{Path(p).name}: missing columns {required-set(d.fieldnames or [])}")
        return list(d)


def summarize(visits, scenes, lookback_days=30, min_valid_pixels=50, radius_m=500):
    if not 1 <= lookback_days <= 120 or min_valid_pixels < 1 or radius_m <= 0:
        raise ValueError("1 <= lookback_days <= 120 and min_valid_pixels >= 1")
    indexed = defaultdict(list)
    scene_id_seen = set()
    for row in scenes:
        route, site = row["RouteNumber"].strip(), row["SiteID"].strip()
        scene_id = row["scene_id"].strip()
        if not scene_id:
            raise ValueError("blank scene_id")
        scene_radius = int(row["radius_m"])
        if scene_radius != radius_m:
            continue
        scene_key = (route, site, scene_id)
        if scene_key in scene_id_seen:
            raise ValueError(f"duplicate scene summary: {scene_key}")
        scene_id_seen.add(scene_key)
        acquired = date.fromisoformat(row["acquisition_date"])
        valid, water = int(row["valid_pixel_n"]), int(row["water_pixel_n"])
        if valid < 0 or not 0 <= water <= valid:
            raise ValueError("scene pixel counts invalid")
        indexed[(route, site)].append((acquired, valid, water))
    output = []
    counts = Counter()
    visitkeys = set()
    for v in visits:
        rid, route, site = v["RunID"].strip(), v["RouteNumber"].strip(), v["SiteID"].strip()
        survey_date = date.fromisoformat(v["SurveyDate"])
        key = (rid, route, site)
        if key in visitkeys:
            raise ValueError(f"duplicate survey-site key {key}")
        visitkeys.add(key)
        # Strictly earlier calendar dates only; same-day acquisitions excluded.
        eligible = [(when, valid, water) for when, valid, water in indexed.get((route, site), [])
                    if 1 <= (survey_date - when).days <= lookback_days and valid > 0]
        n = sum(x[1] for x in eligible)
        w = sum(x[2] for x in eligible)
        status = "ok" if n >= min_valid_pixels else ("no_valid_scene" if not eligible else "insufficient_valid_pixels")
        counts[status] += 1
        output.append({"RunID": rid, "RouteNumber": route, "SiteID": site, "SurveyDate": survey_date.isoformat(),
                       "radius_m": radius_m, "lookback_days": lookback_days, "scene_n": len(eligible), "valid_pixel_n": n,
                       "water_pixel_n": w, "water_fraction": f"{w/n:.6f}" if status == "ok" else "",
                       "days_since_last_valid_scene": min(((survey_date - x[0]).days for x in eligible), default=""),
                       "qc_status": status})
    report = {"n_visits": len(output), "scene_rows": len(scenes), "lookback_days": lookback_days,
              "min_valid_pixels": min_valid_pixels, "radius_m": radius_m, "qc_status_counts": dict(sorted(counts.items())),
              "frog_outcomes_read": False, "after_survey_scenes_used": False,
              "note": "pixel-count-weighted remote-sensing water detection, not a direct water-level measurement"}
    return output, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--site-calendar", required=True)
    p.add_argument("--dswe-scenes", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--lookback-days", type=int, default=30)
    p.add_argument("--min-valid-pixels", type=int, default=50)
    p.add_argument("--radius-m", type=int, default=500)
    a = p.parse_args()
    visits = read_csv(a.site_calendar, REQUIRED_VISIT)
    scenes = read_csv(a.dswe_scenes, REQUIRED_SCENE)
    rows, report = summarize(visits, scenes, a.lookback_days, a.min_valid_pixels, a.radius_m)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT)
        writer.writeheader()
        writer.writerows(rows)
    out.with_suffix(".audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
