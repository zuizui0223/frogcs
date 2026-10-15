#!/usr/bin/env python3
"""Response-blind C1V2 categorical forest fraction and forest-patch connectivity.

Operates only on ACTUAL categorical land-cover and confidence grids with
matching source-year, grid, CRS and provenance. No frog calling is accessed.
The full raster must cover route convex hull + 1000 m; 8-neighbour patches are
cropped only after loading the fixed domain. Proximity or buffer overlap is
NEVER used as evidence of forest connectivity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import label
from rasterio.features import geometry_mask
from rasterio.transform import Affine
from rasterio.warp import transform as warp_transform
from shapely.geometry import MultiPoint, mapping

FOREST_CLASSES=(41,42,43)
VALID_CLASSES={11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95}
BUFFER_M=300
DOMAIN_MARGIN_M=1000
PIXEL_SIZE_M=30
MIN_CLASS_VALID_FRACTION=0.70
MIN_CONFIDENCE_COVERAGE=0.95

def grid_geometry(transform,shape):
    nrows,ncols=shape
    if not isinstance(transform,Affine):
        raise ValueError("missing affine geotransform")
    if not (abs(transform.a-PIXEL_SIZE_M)<0.005 and
            abs(transform.e+PIXEL_SIZE_M)<0.005 and
            abs(transform.b)<1e-8 and abs(transform.d)<1e-8):
        raise ValueError("grid must be unrotated, square 30m equal-area pixels")
    rr,cc=np.mgrid[:nrows,:ncols]
    xs=transform.c+transform.a*(cc+0.5)
    ys=transform.f+transform.e*(rr+0.5)
    return xs,ys

def derive_features(cover,confidence,transform,stop_xy):
    cover=np.asarray(cover)
    confidence=np.asarray(confidence)
    if cover.ndim!=2 or cover.shape!=confidence.shape:
        raise ValueError("cover and confidence must be matched 2D grids")
    if len(stop_xy)!=10 or len(set(tuple(x) for x in stop_xy))!=10:
        raise ValueError("exactly ten unique physical stop centres required")
    if any(len(x)!=2 or not all(math.isfinite(float(v)) for v in x) for x in stop_xy):
        raise ValueError("invalid stop coordinates")
    xs,ys=grid_geometry(transform,cover.shape)
    poly=MultiPoint([tuple(map(float,p)) for p in stop_xy]).convex_hull.buffer(
        DOMAIN_MARGIN_M,resolution=8)
    region=geometry_mask([mapping(poly)],cover.shape,transform=transform,invert=True)
    if (not np.any(region) or region[0].any() or region[-1].any()
            or region[:,0].any() or region[:,-1].any()):
        raise ValueError("route-wide hull+1km domain truncated or outside raster")
    valid=np.isin(cover,tuple(sorted(VALID_CLASSES)))
    forest=valid & np.isin(cover,FOREST_CLASSES) & region
    patches,npatch=label(forest,structure=np.ones((3,3),dtype=int))
    fractions=[];confidence_medians=[];site_labels=[];confidence_complete=[]
    for x,y in stop_xy:
        inside=(xs-float(x))**2+(ys-float(y))**2<=(BUFFER_M**2)
        nominal=int(inside.sum())
        if nominal<250:
            raise ValueError("300m sampling circle clipped by grid edge")
        valid_here=inside&valid&region
        n_valid=int(valid_here.sum())
        if n_valid/nominal < MIN_CLASS_VALID_FRACTION:
            raise ValueError("low categorical pixel completeness at a stop")
        conf_ok=valid_here & (confidence>=1) & (confidence<=100)
        if int(conf_ok.sum())/n_valid < MIN_CONFIDENCE_COVERAGE:
            raise ValueError("class-confidence product incomplete at a stop")
        forest_here=inside&forest
        fractions.append(float(forest_here.sum()/n_valid))
        confidence_medians.append(float(np.median(confidence[conf_ok])))
        confidence_complete.append(float(conf_ok.sum()/n_valid))
        site_labels.append(set(int(v) for v in np.unique(patches[forest_here]) if v>0))
    conn=np.zeros((10,10),dtype=np.int8)
    for i in range(10):
        for j in range(i+1,10):
            if site_labels[i] & site_labels[j]:
                conn[i,j]=conn[j,i]=1
    return {
        "metric":"c1v2_routewide_actual_forest_patch_connections",
        "forest_class_codes":list(FOREST_CLASSES),
        "forest_300m_fraction":fractions,
        "class_confidence_median":confidence_medians,
        "class_confidence_valid_fraction":confidence_complete,
        "forest_patch_count_in_hullplus1km":int(npatch),
        "site_connected_forest_patch_count":[len(p) for p in site_labels],
        "connected_site_pair_count":int(np.triu(conn,k=1).sum()),
        "connected_site_pair_matrix":conn.astype(int).tolist(),
        "proximity_derived":False,"uses_frog_outcomes":False,
        "forest_connection_is_population_movement":False,
        "pixel_domain":"convex_hull_of_ten_stops_plus_1000m_8neighbor"
    }

def file_sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def run_files(cover_path,conf_path,route_json,manifest_json):
    import rasterio
    manifest=json.loads(Path(manifest_json).read_text())
    site=json.loads(Path(route_json).read_text())
    if manifest.get("collection")!="C1V2" or not (1985<=int(manifest.get("year",0))<=2025):
        raise ValueError("C1V2 product/year source manifest required")
    y=str(manifest["year"])
    for key,path,token in (("landcover",cover_path,"LndCov"),("confidence",conf_path,"LndCnf")):
        entry=manifest.get(key,{})
        # No guesses from a WMS rendering or different-version archive.
        if (entry.get("sciencebase_item_id")!=
                ("697b9279b66b0197c3043cc3" if key=="landcover" else
                 "697b92b8b66b0197c3043cc7")):
            raise ValueError("expected official ScienceBase C1V2 item identity missing")
        if not (entry.get("archive_name")==f"Annual_NLCD_{token}_{y}_CU_C1V2.zip"):
            raise ValueError("official archive/year collection token mismatch")
        if not entry.get("sha256") or entry["sha256"] != file_sha256(path):
            raise ValueError("raster SHA256 source manifest mismatch")
    with rasterio.open(cover_path) as c, rasterio.open(conf_path) as f:
        if (c.crs!=f.crs or c.transform!=f.transform or c.shape!=f.shape or
                c.count!=1 or f.count!=1):
            raise ValueError("categorical and confidence must align pixel-for-pixel")
        if (not c.crs.is_projected or c.crs.linear_units.lower() not in ("metre","meter","metres","meters")
                or c.res != (30.0,30.0)):
            raise ValueError("source raster not projected 30m metric grid")
        if c.width*c.height>5_000_000:
            raise ValueError("input must be a bounded route-window GeoTIFF, not full national raster")
        site_xy=[(float(x["lon"]),float(x["lat"])) for x in site["stops"]]
        if len(site_xy)!=10:
            raise ValueError("route source requires ten stops")
        proj_x,proj_y=warp_transform("EPSG:4326",c.crs,
                                   [xy[0] for xy in site_xy],[xy[1] for xy in site_xy])
        result=derive_features(c.read(1),f.read(1),c.transform,list(zip(proj_x,proj_y)))
    result.update({"year":int(y),"collection":"C1V2",
                   "coordinate_route_id":str(site.get("route_number")),
                   "original_cover_sha256":manifest["landcover"]["sha256"],
                   "original_conf_sha256":manifest["confidence"]["sha256"],
                   "no_anuran_counts_or_calls_accessed":True,
                   "independent_historical_fixed_station_truth":False,
                   "this_is_not_a_frog_effect":True})
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--landcover",type=Path,required=True)
    ap.add_argument("--confidence",type=Path,required=True)
    ap.add_argument("--route",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    result=run_files(a.landcover,a.confidence,a.route,a.manifest)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="connected_site_pair_matrix"},indent=2))
if __name__=="__main__":
    main()
