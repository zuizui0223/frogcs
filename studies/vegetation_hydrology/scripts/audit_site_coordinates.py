#!/usr/bin/env python3
"""Outcome-blind QC of the public NAAMP RouteNumber × SiteID coordinate table.

No frog-detection or CallingIndex data are read by this program.
A site is not 'repaired' from other sites' geography or from its outcome.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

PUBLISHED_COORD_SHA256 = "f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
COLUMNS = ("RouteNumber", "SiteID", "lat", "lon")


def km_distance(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    q = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0088 * (2 * math.atan2(math.sqrt(q), math.sqrt(max(0, 1 - q))))


def parse_coordinates(raw):
    errors = []
    for col in COLUMNS:
        if col not in raw:
            raise ValueError(f"missing required column {col}")
    route, site = str(raw["RouteNumber"]).strip(), str(raw["SiteID"]).strip()
    if not route or not site:
        return (route, site), None, ["missing_route_or_site_id"]
    try:
        lat, lon = float(raw["lat"]), float(raw["lon"])
    except (ValueError, TypeError):
        return (route, site), None, ["non_numeric_coordinate"]
    if not (math.isfinite(lat) and math.isfinite(lon)):
        errors.append("non_finite_coordinate")
    elif not (24 <= lat <= 51 and -126 <= lon <= -66):
        errors.append("outside_conus_bounds")
    return (route, site), (lat, lon), errors


def audit(path, *, expected_sha=None, review_km=25.0, quarantine_km=50.0):
    """Site statuses: accepted | review | quarantine. Review rows are excluded.

    Distances are *geometry flags*, not assertions that long legitimate routes
    cannot exist. Manual independent verification can reinstate held routes.
    """
    if review_km <= 0 or quarantine_km <= review_km:
        raise ValueError("require 0 < review_km < quarantine_km")
    rawbytes = Path(path).read_bytes()
    sha = hashlib.sha256(rawbytes).hexdigest()
    if expected_sha and sha.lower() != expected_sha.lower():
        raise ValueError(f"source SHA256 mismatch: expected {expected_sha}; got {sha}")
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or any(n not in reader.fieldnames for n in COLUMNS):
            raise ValueError(f"required columns: {', '.join(COLUMNS)}")
        raw_rows = list(reader)

    grouped = defaultdict(list)
    for row in raw_rows:
        key, pos, errors = parse_coordinates(row)
        grouped[key].append((pos, errors))
    records = {}
    routepoints = defaultdict(list)
    for key, readings in grouped.items():
        errs = {reason for _, rr in readings for reason in rr}
        pts = [p for p, rr in readings if p is not None and not rr]
        # A site with any invalid duplicate is not treated as repaired.
        if pts and len(pts) > 1 and any(km_distance(pts[0], p) > 0.03 for p in pts[1:]):
            errs.add("conflicting_duplicate_coordinates")
        pos = pts[0] if pts and not errs else None
        records[key] = {"route": key[0], "site": key[1], "pos": pos, "reasons": set(errs)}
        if pos is not None:
            routepoints[key[0]].append((key[1], pos))

    route_spans = {}
    for route, entries in routepoints.items():
        points = [p for _, p in entries]
        span = max((km_distance(a, b) for i, a in enumerate(points) for b in points[i + 1:]), default=0.0)
        route_spans[route] = span
        if span > quarantine_km:
            for key, rec in records.items():
                if key[0] == route:
                    rec["reasons"].add("route_span_gt_quarantine_km")
        elif span > review_km:
            for key, rec in records.items():
                if key[0] == route:
                    rec["reasons"].add("route_span_gt_review_km")
        # Near-identical GPS coordinates for *different* sites warrant review.
        for i, (a, pa) in enumerate(entries):
            for b, pb in entries[i + 1:]:
                if km_distance(pa, pb) < 0.05:
                    records[(route, a)]["reasons"].add("distinct_sites_nearly_coincident")
                    records[(route, b)]["reasons"].add("distinct_sites_nearly_coincident")

    accepted, held = [], []
    for key, rec in sorted(records.items()):
        reasons = sorted(rec["reasons"])
        status = "accepted" if not reasons else (
            "quarantine" if any(r in {"missing_route_or_site_id", "non_numeric_coordinate", "non_finite_coordinate", "outside_conus_bounds", "conflicting_duplicate_coordinates", "route_span_gt_quarantine_km"} for r in reasons)
            else "review"
        )
        p = rec["pos"]
        out = {"RouteNumber": rec["route"], "SiteID": rec["site"],
               "lat": "" if p is None else format(p[0], ".8f"),
               "lon": "" if p is None else format(p[1], ".8f"),
               "status": status, "reasons": ";".join(reasons)}
        (accepted if status == "accepted" else held).append(out)

    return {
        "accepted": accepted, "held": held,
        "report": {
            "source_file": Path(path).name,
            "source_sha256": sha,
            "matches_previously_pinned_coordinates": sha == PUBLISHED_COORD_SHA256,
            "input_rows": len(raw_rows), "unique_route_site_keys": len(records),
            "n_routes_with_parseable_site_coordinates": len(route_spans),
            "max_route_span_km_unfiltered": max(route_spans.values(), default=None),
            "route_span_over_review": sum(s > review_km for s in route_spans.values()),
            "route_span_over_quarantine": sum(s > quarantine_km for s in route_spans.values()),
            "accepted_sites": len(accepted), "held_sites": len(held),
            "held_reason_counts": dict(sorted(Counter(r for record in held for r in record["reasons"].split(";") if r).items())),
            "review_span_threshold_km": review_km,
            "quarantine_span_threshold_km": quarantine_km,
            "outcome_records_read": False,
            "geometry_is_ground_truth": False,
        },
    }


def write_output(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    cols = ("RouteNumber", "SiteID", "lat", "lon", "status", "reasons")
    for filename, key in (("accepted_coordinates.csv", "accepted"), ("held_coordinates.csv", "held")):
        with (output / filename).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(result[key])
    (output / "coordinate_qc_report.json").write_text(json.dumps(result["report"], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coordinates", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected-sha256", default=None, help="Optional exact pin. Do not silently accept drift.")
    parser.add_argument("--review-km", type=float, default=25)
    parser.add_argument("--quarantine-km", type=float, default=50)
    a = parser.parse_args()
    result = audit(a.coordinates, expected_sha=a.expected_sha256, review_km=a.review_km, quarantine_km=a.quarantine_km)
    write_output(result, a.out)
    print(json.dumps(result["report"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
