#!/usr/bin/env python3
"""Read small 500-m INWAM categorical windows for three actual pre-survey sites.

Input: outcome-blind STAC metadata receipt from probe_dswe_site_survey_coverage.py.
No other raster is downloaded, no frog outcomes are accessed. This is a
technical cloud/QA feasibility pilot, not a hydrological causality result.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import transform

RADIUS=500
# USGS C2 INWAM: 0 no water; 1–4 surface-water confidence classes;
# 9 cloud/cloud shadow; 255 fill. Masked / uncertain classes >4 excluded.
VALID={0,1,2,3,4}
WATER={1,2,3,4}
COG_DOMAIN="https://landsatlook.usgs.gov/level-3/collection02/DSWE/"

def read_window(url,lon,lat):
    if not url.startswith(COG_DOMAIN) or not url.upper().endswith("_INWAM.TIF"):
        raise ValueError("unexpected remote DSWE C2 INWAM asset URL")
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.tif",
                      GDAL_HTTP_CONNECTTIMEOUT="9",GDAL_HTTP_TIMEOUT="22",
                      GDAL_HTTP_MAX_RETRY="1"):
        with rasterio.open("/vsicurl/"+url) as ds:
            if ds.count!=1 or ds.crs is None or not ds.crs.is_projected:
                raise RuntimeError("unsupported source raster/CRS")
            if ds.dtypes[0] != "uint8":
                raise RuntimeError("INWAM expects uint8")
            if not (abs(ds.res[0]-30)<.01 and abs(ds.res[1]-30)<.01):
                raise RuntimeError("unexpected DSWE resolution")
            x,y=transform("EPSG:4326",ds.crs,[lon],[lat])
            x,y=x[0],y[0]
            row,col=ds.index(x,y)
            radius_px=math.ceil(RADIUS/30)+3
            w=radius_px*2+1
            window=Window(col-radius_px,row-radius_px,w,w)
            values=ds.read(1,window=window,boundless=True,fill_value=255)
            aff=ds.window_transform(window)
            xx=aff.c+(np.arange(w)+.5)*aff.a
            yy=aff.f+(np.arange(w)+.5)*aff.e
            circle=(xx[None,:]-x)**2+(yy[:,None]-y)**2<=RADIUS*RADIUS
            n_pixels=int(circle.sum())
            valid=circle & np.isin(values,list(VALID))
            n_valid=int(valid.sum())
            water=valid & np.isin(values,list(WATER))
            allmask={}
            for value in [0,1,2,3,4,9,255]:
                allmask[str(value)]=int((circle & (values==value)).sum())
            return {"n_buffer_pixels":n_pixels,"valid_pixel_n":n_valid,
                    "valid_pixel_fraction":round(n_valid/n_pixels,5) if n_pixels else None,
                    "water_pixel_n":int(water.sum()),
                    "water_fraction_of_valid":round(float(water.sum()/n_valid),5) if n_valid else None,
                    "open_moderate_water_n":int((circle & np.isin(values,[1,2])).sum()),
                    "partial_low_water_n":int((circle & np.isin(values,[3,4])).sum()),
                    "class_counts":allmask,
                    "raster_width":ds.width,"raster_height":ds.height,
                    "raster_crs":str(ds.crs)[:100],
                    "meets_50_valid_pixel_rule":n_valid>=50}

def audit(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    if d.get("analysis")!="naamp_pre_survey_dswe_stac_feasibility_v0_1" or not d.get("no_frog_calling_outcomes_read"):
        raise ValueError("unexpected STAC source receipt")
    queries=d["queries"]
    selected=[]
    for year in [2001,2008,2015]:
        matches=sorted((r for r in queries if r["year"]==year),key=lambda r:r["state"])
        if not matches:raise ValueError("missing source year")
        selected.append(matches[0])
    rows=[]
    for q in selected:
        row={k:q[k] for k in ["year","state","route","site","date","lat","lon"]}
        row.update({"years_prior":None,"scene_ids":[],"asset_attempts":[]})
        assets=q.get("sample_scene_assets") or []
        if not assets:row["status"]="no_scene_metadata"
        for item in assets[:2]:
            result={"id":item["id"],"acquisition_date":item["acquisition_date"]}
            try:
                p=read_window(item["inwam_url"],q["lon"],q["lat"])
                result.update(p)
                result["status"]="enough_pixels" if p["meets_50_valid_pixel_rule"] else "insufficient_clear_pixels"
            except Exception as ex:
                result["status"]="read_error";result["error"]=type(ex).__name__+": "+str(ex)[:300]
            row["asset_attempts"].append(result)
        row["status"]="pixel_read_attempted" if row["asset_attempts"] else row.get("status","none")
        rows.append(row)
    return {"analysis":"naamp_dswe_strictly_prior_C2_INWAM_500m_pixel_pilot_v0_1",
            "source":"USGS Landsat Collection 2 L3 DSWE INWAM",
            "source_receipt":str(path),"sites":len(rows),
            "scene_attempts":sum(len(x["asset_attempts"]) for x in rows),
            "successful_pixel_reads":sum(z.get("status") in ("enough_pixels","insufficient_clear_pixels")
                                         for x in rows for z in x["asset_attempts"]),
            "site_years_with_ge_50_valid_pixels":sum(any(z.get("meets_50_valid_pixel_rule") for z in x["asset_attempts"]) for x in rows),
            "counts_csv_read":False,"frog_outcomes_read":False,
            "not_estimated":"This is not survey-night hydrology, breeding habitat use or any frog response",
            "sample":rows}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stac-receipt",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    a=parser.parse_args()
    r=audit(a.stac_receipt)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
if __name__=="__main__":main()
