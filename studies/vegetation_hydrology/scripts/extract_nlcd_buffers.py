#!/usr/bin/env python3
"""Extract annual NLCD land-cover composition around geometry-QC-passed NAAMP sites.

Requires georeferenced local GeoTIFFs. This program never accesses frog outcomes.
For exact reproducibility, pin source raster checksums externally in the data manifest.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

# Annual NLCD categories; no canopy-percentage or habitat-ground-truth claims.
CLASSES = {
    "forest": {41, 42, 43},
    "woody_wetland": {90},
    "emergent_wetland": {95},
    "open_water": {11},
    "developed": {21, 22, 23, 24},
    "shrub": {52},
    "grass_herb": {71, 72},
    "agriculture": {81, 82},
}
METRIC_NAMES = [f"frac_{name}" for name in CLASSES]


def _dependencies():
    try:
        import rasterio
        from rasterio.features import geometry_mask
        from rasterio.windows import from_bounds
        from rasterio.warp import transform as coord_transform
        from shapely.geometry import Point, mapping
    except ImportError as exc:
        raise RuntimeError("install rasterio and shapely to run geospatial extraction") from exc
    return rasterio, geometry_mask, from_bounds, coord_transform, Point, mapping


def extract_point(ds, lat, lon, radius_m=500, min_coverage=0.8):
    """Returns pixel-center buffer fractions; never treats nodata as land.

    Pixel resolution and window are from the raster, not hard-coded to 30m.
    The raster's projected CRS must use meters, not geographic degrees.
    """
    rasterio, geometry_mask, from_bounds, coord_transform, Point, mapping = _dependencies()
    if not ds.crs or not ds.crs.is_projected:
        raise ValueError("raster CRS must be projected (metres), not lat/lon")
    # Rasterio UTM/Albers metre CRS check; fail closed on non-metre projections.
    units = str(ds.crs.linear_units).lower()
    if "metre" not in units and "meter" not in units:
        raise ValueError(f"raster CRS linear units not metres: {units}")
    x, y = coord_transform("EPSG:4326", ds.crs, [lon], [lat])
    geom = Point(x[0], y[0]).buffer(radius_m)
    win = from_bounds(*geom.bounds, transform=ds.transform).round_offsets().round_lengths()
    arr = ds.read(1, window=win, boundless=True, masked=True)
    inside = geometry_mask([mapping(geom)], out_shape=arr.shape, transform=ds.window_transform(win), invert=True, all_touched=False)
    n_total = int(inside.sum())
    values = arr.data
    valid = inside & ~__import__('numpy').ma.getmaskarray(arr)
    if ds.nodata is not None:
        valid &= values != ds.nodata
    n_valid = int(valid.sum())
    coverage = float(n_valid / n_total) if n_total else 0.0
    result = {"radius_m": radius_m, "n_buffer_pixels": n_total, "n_valid_pixels": n_valid,
              "coverage_fraction": round(coverage, 6),
              "qc_status": "ok" if coverage >= min_coverage and n_valid else "low_coverage"}
    for col in METRIC_NAMES:
        result[col] = ""
    if result["qc_status"] == "ok":
        import numpy as np
        for category, codes in CLASSES.items():
            count = np.count_nonzero(np.isin(values[valid], list(codes)))
            result[f"frac_{category}"] = round(float(count / n_valid), 6)
    return result


def run(coords_csv, raster_template, years, radii, output, min_coverage=0.8):
    rasterio, *_ = _dependencies()
    with Path(coords_csv).open(newline="", encoding="utf-8-sig") as f:
        sites = list(csv.DictReader(f))
    required = {"RouteNumber", "SiteID", "lat", "lon", "status"}
    if not sites or not required.issubset(sites[0]):
        raise ValueError("need nonempty accepted_coordinates.csv with RouteNumber,SiteID,lat,lon,status")
    if any(r["status"] != "accepted" for r in sites):
        raise ValueError("refuse to extract from non-accepted site coordinates")
    keys = [(r["RouteNumber"], r["SiteID"]) for r in sites]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate RouteNumber × SiteID entries")
    columns = ["RouteNumber", "SiteID", "year", "radius_m", "n_buffer_pixels", "n_valid_pixels", "coverage_fraction", "qc_status"] + METRIC_NAMES
    # Preflight all rasters before writing any output rows.
    if any(y < 2001 or y > 2015 for y in years):
        raise ValueError("years outside frozen NAAMP study period 2001–2015")
    for year in years:
        raster_path = Path(raster_template.format(year=year))
        if not raster_path.exists():
            raise FileNotFoundError(f"no NLCD raster for {year}: {raster_path}")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    nrows = 0
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for year in years:
            if not 2001 <= year <= 2015:
                raise ValueError("year outside frozen NAAMP study period 2001–2015")
            raster_path = Path(raster_template.format(year=year))
            if not raster_path.exists():
                raise FileNotFoundError(f"no NLCD raster for {year}: {raster_path}")
            with rasterio.open(raster_path) as ds:
                if ds.count != 1:
                    raise ValueError(f"single-band categorical raster required: {raster_path}")
                for site in sites:
                    lat, lon = float(site["lat"]), float(site["lon"])
                    if not (math.isfinite(lat) and math.isfinite(lon) and 24<=lat<=51 and -126<=lon<=-66):
                        raise ValueError("coordinates outside study region")
                    for radius in radii:
                        result = extract_point(ds, lat, lon, radius, min_coverage)
                        writer.writerow({"RouteNumber": site["RouteNumber"], "SiteID": site["SiteID"], "year": year, **result})
                        nrows += 1
    return {"rows": nrows, "unique_sites": len(sites), "years": list(years), "radii_m": list(radii),
            "min_coverage": min_coverage, "outcomes_read": False, "output": str(output)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--accepted-coordinates", required=True)
    p.add_argument("--raster-template", required=True, help="e.g. '/data/nlcd/nlcd_{year}.tif'")
    p.add_argument("--out", required=True)
    p.add_argument("--years", required=True, nargs="+", type=int)
    p.add_argument("--radii-m", nargs="+", type=int, default=[100, 500])
    p.add_argument("--min-coverage", type=float, default=0.8)
    args = p.parse_args()
    if any(r <= 0 for r in args.radii_m) or not 0 < args.min_coverage <= 1:
        p.error("radii > 0 and 0 < min-coverage <= 1 required")
    print(json.dumps(run(args.accepted_coordinates, args.raster_template, args.years, args.radii_m, args.out, args.min_coverage), indent=2))


if __name__ == "__main__":
    main()
