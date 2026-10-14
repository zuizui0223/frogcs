#!/usr/bin/env python3
"""Outcome-blind NAAMP coordinate and landscape-opportunity preflight.

Uses ONLY the SHA256-pinned public RouteNumber/SiteID/lat/lon table.
Does not read Runs, Counts, frog taxon identities, rainfall or outcomes.
The 300 m and 1 km radii are *geometric opportunity* diagnostics only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

COORD_URL = (
    "https://www.sciencebase.gov/catalog/file/get/583dc314e4b0d1899f9dea8d"
    "?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536"
)
COORD_SHA256 = "f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83"
EXPECTED_COORD_ROWS = 12064
EXPECTED_COORD_ROUTES = 1183
EXPECTED_LEGACY_8PLUS_PASS = 1106
RADII_METRES = (300, 1000)
FOREST_CLASSES = (41, 42, 43)

def download_pinned_coordinates():
    req = urllib.request.Request(COORD_URL, headers={"User-Agent": "frogcs-landscape-source-only/1.0"})
    with urllib.request.urlopen(req, timeout=150) as response:
        blob = response.read()
    validate_sha(blob)
    return blob

def validate_sha(blob):
    actual = hashlib.sha256(blob).hexdigest()
    if actual != COORD_SHA256:
        raise ValueError(f"coordinate source identity drift: {actual} != {COORD_SHA256}")

def read_csv(blob):
    reader = csv.DictReader(io.StringIO(blob.decode("utf-8-sig")))
    required = {"RouteNumber", "SiteID", "lat", "lon"}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError(f"missing coordinate headers: {required - set(reader.fieldnames or [])}")
    return list(reader)

def km_between(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(h)))

def quantiles(items):
    data = sorted(items)
    if not data:
        return {str(p): None for p in (0, 0.25, 0.5, 0.75, 0.9, 1)}
    out = {}
    for p in (0, 0.25, 0.5, 0.75, 0.9, 1):
        z = (len(data) - 1) * p
        lo, hi = math.floor(z), math.ceil(z)
        val = data[lo] if lo == hi else data[lo] * (hi - z) + data[hi] * (z - lo)
        out[str(p)] = round(float(val), 7)
    return out

def components(n, pairs):
    root = list(range(n))
    def find(x):
        while root[x] != x:
            root[x] = root[root[x]]
            x = root[x]
        return x
    for a, b in pairs:
        ra, rb = find(a), find(b)
        root[ra] = rb
    return len({find(i) for i in range(n)})

def evaluate_route(route, original_rows):
    by_site = defaultdict(set)
    invalid = 0
    for x in original_rows:
        site = str(x.get("SiteID") or "").strip()
        if not site:
            invalid += 1
            continue
        try:
            xy = (float(x["lat"]), float(x["lon"]))
            if not all(math.isfinite(v) for v in xy):
                raise ValueError("nonfinite")
        except (ValueError, TypeError, KeyError):
            invalid += 1
            continue
        by_site[site].add(xy)
    conflicts = [site for site, vals in by_site.items() if len(vals) > 1]
    points = [(site, next(iter(vals))) for site, vals in sorted(by_site.items()) if len(vals) == 1]
    outside = [site for site, (lat, lon) in points if not (24 <= lat <= 50 and -125 <= lon <= -66)]
    inside = [(site, xy) for site, xy in points if site not in outside]
    n = len(inside)

    distances = [(i, j, km_between(inside[i][1], inside[j][1]))
                 for i in range(n) for j in range(i + 1, n)]
    max_span = max((d for _, _, d in distances), default=0)
    if inside:
        median_coord = (statistics.median(xy[0] for _, xy in inside),
                        statistics.median(xy[1] for _, xy in inside))
        distances_med = [km_between(xy, median_coord) for _, xy in inside]
        med = statistics.median(distances_med)
        mad = statistics.median(abs(d - med) for d in distances_med)
        maxmed = max(distances_med)
        robust_outlier = mad > 0 and any(d > med + 8 * mad for d in distances_med)
    else:
        med = mad = maxmed = None
        robust_outlier = False

    issues = []
    if len(points) < 8:
        issues.append("fewer_than_8_unambiguous")
    if conflicts:
        issues.append("coordinate_conflict")
    if outside:
        issues.append("outside_conus_bounds")
    if max_span > 30:
        issues.append("span_gt_30km")
    if maxmed is not None and maxmed > 15:
        issues.append("site_gt_15km_from_median")
    if robust_outlier:
        issues.append("robust_geometry_outlier")
    legacy_pass = len(issues) == 0 and n >= 8
    exact_ten = legacy_pass and n == 10 and len(points) == 10 and invalid == 0

    # Purely geometric buffer-overlap opportunities, NOT forest connectivity.
    overlap300 = [(i, j) for i, j, dist in distances if dist < 0.600]
    overlap1000 = [(i, j) for i, j, dist in distances if dist < 2.000]
    graph_edges = len(overlap1000)
    return {
        "route_number": route,
        "raw_coordinate_rows": len(original_rows),
        "unambiguous_sites": len(points),
        "inside_bounds_sites": n,
        "invalid_rows": invalid,
        "conflicting_siteids": len(conflicts),
        "legacy_8plus_geometry_pass": legacy_pass,
        "complete_10_siteid_source_pass": exact_ten,
        "issues": issues if issues else ([] if exact_ten else ["not_exactly_ten_siteids"]),
        "max_route_span_km": round(max_span, 5),
        "median_to_route_median_km": round(med, 5) if med is not None else None,
        "mad_to_route_median_km": round(mad, 5) if mad is not None else None,
        "buffer_300m_overlap_pairs": len(overlap300) if exact_ten else None,
        "buffer_1km_overlap_pairs": graph_edges if exact_ten else None,
        "buffer_1km_overlap_components": components(n, overlap1000) if exact_ten else None,
        "buffer_1km_pair_density": round(graph_edges / 45, 5) if exact_ten else None
    }

def summarize(rows, *, enforce_source_size=False):
    routes = defaultdict(list)
    for x in rows:
        route = str(x.get("RouteNumber") or "").strip()
        if route:
            routes[route].append(x)
    if enforce_source_size:
        if len(rows) != EXPECTED_COORD_ROWS or len(routes) != EXPECTED_COORD_ROUTES:
            raise ValueError("pinned coordinate table unexpectedly changed row/route counts")
    reports = [evaluate_route(key, value) for key, value in sorted(routes.items())]
    n_legacy = sum(x["legacy_8plus_geometry_pass"] for x in reports)
    if enforce_source_size and n_legacy != EXPECTED_LEGACY_8PLUS_PASS:
        raise ValueError(f"legacy outcome-blind eligibility drift: {n_legacy} != {EXPECTED_LEGACY_8PLUS_PASS}")
    selected = [x for x in reports if x["complete_10_siteid_source_pass"]]
    count_reasons = Counter(reason for x in reports if not x["complete_10_siteid_source_pass"]
                            for reason in x["issues"])
    result = {
        "study": "naamp_terrestrial_geometry_source_preflight_v1",
        "status": "source_only_not_an_effect_analysis",
        "coordinate_source": {"sha256": COORD_SHA256, "rows": len(rows), "routes": len(routes)},
        "constants": {
            "legacy_8plus_geometry_pass_expected": EXPECTED_LEGACY_8PLUS_PASS,
            "complete_10_siteid_requires_exactly_10": True,
            "forest_class_candidates_NLCD": list(FOREST_CLASSES),
            "forest_buffer_m": RADII_METRES[0],
            "landscape_context_buffer_m": RADII_METRES[1],
            "distance_pair_threshold_km": 2.0,
        },
        "summary": {
            "legacy_8plus_geometry_pass": n_legacy,
            "complete_10_siteid_source_pass": len(selected),
            "complete_10_siteid_source_fraction": len(selected) / len(routes) if routes else None,
            "source_exclusion_reasons": dict(sorted(count_reasons.items())),
            "eligible_1km_overlap_pairs_quantiles": quantiles(
                [x["buffer_1km_overlap_pairs"] for x in selected]),
            "eligible_1km_overlap_components_quantiles": quantiles(
                [x["buffer_1km_overlap_components"] for x in selected]),
            "eligible_300m_overlap_pairs_quantiles": quantiles(
                [x["buffer_300m_overlap_pairs"] for x in selected]),
            "eligible_1km_pair_density_quantiles": quantiles(
                [x["buffer_1km_pair_density"] for x in selected]),
            "routes_with_at_least_one_1km_buffer_overlap": sum(
                x["buffer_1km_overlap_pairs"] > 0 for x in selected),
            "routes_with_full_1km_overlap_graph": sum(
                x["buffer_1km_overlap_components"] == 1 for x in selected)
        },
        "boundary": {
            "landcover_pixels_downloaded": False,
            "forest_patches_or_connectivity_measured": False,
            "historical_station_continuity_verified": False,
            "frog_calling_records_read": False,
            "acoustic_event_10site_eligibility_verified": False,
            "species_environment_effect_estimated": False,
            "buffer_overlap_is_not_forest_connectivity": True,
            "source_only_route_eligibility_is_not_focal_pair_eligibility": True,
        },
        "route_records": reports,
    }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--coordinate-csv", type=Path, help="For offline tests; production verifies pinned URL and SHA")
    parser.add_argument("--output", type=Path,
                        default=Path("research/output/NAAMP_TERRESTRIAL_GEOMETRY_SOURCE_V0_1.json"))
    args = parser.parse_args()
    blob = args.coordinate_csv.read_bytes() if args.coordinate_csv else download_pinned_coordinates()
    if not args.coordinate_csv:
        validate_sha(blob)
    report = summarize(read_csv(blob), enforce_source_size=(args.coordinate_csv is None))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("study", "coordinate_source", "summary", "boundary")},
                     indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
