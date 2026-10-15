#!/usr/bin/env python3
"""Select one source-only NAAMP technical pilot and emit MRLC Viewer AOI GeoJSON.

The selected route is the lexicographically first *eligible historical-paper*
route among the pre-fixed full ten-coordinate source cohort. No Calls, Counts,
species, rainfall-response residuals, remotely sensed pixels or frog effects
are read or used to choose it. GeoJSON AOI is route convex hull + 1000 m in
native USGS metric CRS, transformed to WGS84 for MRLC Viewer.
"""
from __future__ import annotations
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
import argparse

from pyproj import Transformer
from shapely.geometry import MultiPoint, mapping
from shapely.ops import transform as shapely_transform

import naamp_focal_metadata_geometry_join_v0_1 as join
import naamp_terrestrial_geometry_preflight_v1 as geometry

def build():
    meta=join.get_pinned_sources()
    coord_raw=geometry.download_pinned_coordinates()
    source=geometry.read_csv(coord_raw)
    panel=join.produce(meta,coord_raw,enforce_pins=True)
    chosen=panel["source_eligible_routes"]
    if not chosen or len(chosen)!=358:
        raise ValueError("unexpected frozen study cohort size")
    selected=sorted(chosen)[0]
    state,route=selected.split(":",1)
    pointmap=defaultdict(set)
    for r in source:
        if str(r.get("RouteNumber") or "").strip()==route:
            sid=str(r.get("SiteID") or "").strip()
            if sid:
                pointmap[sid].add((float(r["lon"]),float(r["lat"])))
    if len(pointmap)!=10 or any(len(v)!=1 for v in pointmap.values()):
        raise ValueError("selected route lost exactly ten coordinate identities")
    rows=[{"SiteID":sid,"lon":next(iter(vals))[0],
           "lat":next(iter(vals))[1]} for sid,vals in sorted(pointmap.items())]
    proj=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True)
    inv=Transformer.from_crs("EPSG:5070","EPSG:4326",always_xy=True)
    xy=[proj.transform(r["lon"],r["lat"]) for r in rows]
    aoi_proj=MultiPoint(xy).convex_hull.buffer(1000,resolution=16)
    km2=aoi_proj.area/1e6
    if aoi_proj.is_empty or not aoi_proj.is_valid or km2>900 or km2<1:
        raise ValueError(f"invalid/unsafe route AOI geometry area: {km2}")
    aoi_wgs=shapely_transform(inv.transform,aoi_proj)
    if not aoi_wgs.is_valid or aoi_wgs.is_empty:
        raise ValueError("projected AOI invalid")
    feature={"type":"Feature","geometry":mapping(aoi_wgs),"properties":{
            "type":"source_only_NAAMP_NLCD_C1V2_AOI",
            "route_cluster":selected,
            "selected_by":"lexicographically_first_eligible_paper_cohort_route",
            "buffer_m":1000,
            "source_coordinate_sha256":geometry.COORD_SHA256,
            "not_breeding_wetland_boundary":True,
            "historical_fixed_station_field_validation":False,
            "no_frog_outcome_selection":True}}
    geo={"type":"FeatureCollection","features":[feature]}
    receipt={"study":"naamp_landcover_official_viewer_source_only_AOI_v0_1",
             "selected_route_cluster":selected,
             "selected_route_nSiteID":len(rows),
             "source_candidate_routes":len(chosen),
             "n_focal_paper_pairs_for_selected_route":sum(
                str(p["state"])+":"+str(p["route"])==selected
                for p in panel["source_eligible_pairs"]),
             "route_aoi_km2":round(km2,5),
             "buffer_m":1000,"projection":"EPSG:5070",
             "GeoJSON_CRS":"EPSG:4326",
             "source_which":"original_pinned_Runs_Stops_coordinate_without_Counts",
             "no_frog_Counts_opened":True,
             "no_species_response_or_residual_used":True,
             "C1V2_LndCov_acquired":False,
             "C1V2_LndCnf_acquired":False,
             "source_landcover_pixel_identity_verified":False,
             "use":"Manual upload only to official MRLC Viewer as source-only technical AOI"}
    return geo,receipt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path(
       "research/output/NAAMP_SOURCE_ONLY_LANDSCAPE_MRLC_VIEWER_AOI_V0_1.geojson"))
    ap.add_argument("--receipt",type=Path,default=Path(
       "research/output/NAAMP_SOURCE_ONLY_MRLC_VIEWER_AOI_V0_1.json"))
    a=ap.parse_args();geo,receipt=build()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(geo,indent=2)+"\n",encoding="utf8")
    receipt["geojson_sha256"]=hashlib.sha256(a.out.read_bytes()).hexdigest()
    a.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=="__main__":main()
