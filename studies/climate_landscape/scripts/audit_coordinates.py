#!/usr/bin/env python3
"""Response-blind audit of NAAMP route/physical SiteID coordinates.

Geometry checks do NOT verify a field station. Output pass_unverified MUST NOT
be converted into verified_external without independent route documentation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

COLUMNS = {"RouteNumber", "SiteID", "lat", "lon"}
BBOX = (-125.0, -66.0, 24.0, 50.0)
FLAG_ROUTE_MAX_KM = 50.0
FLAG_SITE_NEAREST_KM = 25.0


def km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = (np.radians(x) for x in (lat1, lon1, lat2, lon2))
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 6371.0088 * 2*np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def audit(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    absent = COLUMNS - set(raw.columns)
    if absent:
        raise ValueError(f"Missing coordinate columns {sorted(absent)}")
    data = raw[list(sorted(COLUMNS))].copy()
    for c in ("RouteNumber", "SiteID"):
        data[c] = data[c].astype("string").str.strip()
        if data[c].isna().any() or data[c].eq("").any():
            raise ValueError(f"Empty {c}")
    for c in ("lat", "lon"):
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data["domain_ok"] = (np.isfinite(data.lat) & np.isfinite(data.lon) &
        data.lat.between(BBOX[2], BBOX[3]) & data.lon.between(BBOX[0], BBOX[1]))

    out = []
    for (route, site), g in data.groupby(["RouteNumber", "SiteID"], dropna=False, sort=True):
        unique = g[["lat", "lon"]].drop_duplicates()
        row = {"route_id":str(route), "site_id":str(site),
               "source_rows":int(len(g)), "distinct_locations":int(len(unique)),
               "latitude":float(g.lat.iloc[0]), "longitude":float(g.lon.iloc[0]),
               "domain_ok":bool(g.domain_ok.all()),
               "route_max_km":np.nan, "nearest_route_site_km":np.nan,
               "geometry_qc_status":"pass_unverified"}
        if not bool(g.domain_ok.all()):
            row["geometry_qc_status"] = "failed_domain"
        elif len(unique) > 1:
            row["geometry_qc_status"] = "conflicting_site_coordinates"
        out.append(row)
    audit_table = pd.DataFrame(out)
    if len(audit_table) == 0:
        raise ValueError("Empty coordinates")
    for route, g in audit_table.groupby("route_id", sort=True):
        valid = g[(g.domain_ok) & (g.distinct_locations == 1)]
        ix = valid.index.to_numpy()
        if len(ix) < 2:
            continue
        lat = valid.latitude.to_numpy(float)
        lon = valid.longitude.to_numpy(float)
        d = km(lat[:,None], lon[:,None], lat[None,:], lon[None,:])
        np.fill_diagonal(d, np.inf)
        nearest = d.min(axis=1)
        route_max = float(np.max(d[np.isfinite(d)]))
        audit_table.loc[ix, "route_max_km"] = route_max
        audit_table.loc[ix, "nearest_route_site_km"] = nearest
        suspect = (nearest > FLAG_SITE_NEAREST_KM) | (route_max > FLAG_ROUTE_MAX_KM)
        for i, flag in zip(ix, suspect):
            if bool(flag) and audit_table.at[i,"geometry_qc_status"] == "pass_unverified":
                audit_table.at[i,"geometry_qc_status"] = "review_geometry"

    audit_table["coordinate_qc_status"] = "UNVERIFIED_DO_NOT_EXTRACT"
    audit_table = audit_table.sort_values(["route_id", "site_id"]).reset_index(drop=True)
    statuses = {str(k):int(v) for k,v in audit_table.geometry_qc_status.value_counts().items()}
    summary = {"source_rows":int(len(data)), "distinct_route_site_keys":int(len(audit_table)),
               "routes":int(audit_table.route_id.nunique()), "status_counts":statuses,
               "coordinates_independently_verified":0,
               "bbox_conus":BBOX, "route_max_review_km":FLAG_ROUTE_MAX_KM,
               "nearest_site_review_km":FLAG_SITE_NEAREST_KM,
               "does_not_read_frog_response":True,
               "meaning":"Geometry flagging only; even pass_unverified requires independent verification"}
    return audit_table, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--expect-sha256")
    a = ap.parse_args()
    payload = Path(a.coords).read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if a.expect_sha256 and sha != a.expect_sha256:
        raise ValueError(f"Coordinate source SHA256 mismatch, got {sha}")
    output, summary = audit(pd.read_csv(a.coords,
                                 dtype={"RouteNumber":"string","SiteID":"string"}))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(out, index=False)
    summary["input_sha256"] = sha
    summary["output_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    rec = Path(a.receipt)
    rec.parent.mkdir(parents=True, exist_ok=True)
    rec.write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
