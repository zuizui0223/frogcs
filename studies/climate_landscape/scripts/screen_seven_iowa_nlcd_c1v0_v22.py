#!/usr/bin/env python3
"""Source-only 7-route Annual NLCD C1V0 pixel screening (2011–2013).

Route population fixed by earlier Runs/Stops/coordinate-only independent QC.
DOES NOT open NAAMP Counts.csv, infer an amphibian effect, verify field
station continuity, or treat C1V0 classifications as C1.2 truth.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from rasterio.io import MemoryFile
from rasterio.warp import transform as project

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
import arcgis_c1v0_full_aoi as src
from audit_coordinates import audit as geometry_audit
from build_naamp_observation_panel import make as panel_make, SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA

ROUTES=("360104","360110","360125","360213","360219","360316","360412")
YEARS=(2011,2012,2013)
RADII=(250,1000)
CODES={11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95}
FOREST={41,42,43}; AGRI={81,82}; DEV={21,22,23,24}
MAX_PIXELS_PER_CROP=2_000_000

def sha(raw):return hashlib.sha256(raw).hexdigest()

def fixed_sources(runs,stops,coords):
    panel,cohort=panel_make(runs,stops)
    geo,geom=geometry_audit(coords)
    geo=geo.rename(columns={"route_id":"route_number"})
    selected=panel[panel.state.eq("Iowa") & panel.route_number.isin(ROUTES)].copy()
    if set(selected.route_number)!=set(ROUTES):
        raise ValueError("Frozen 7-route source-only population not present")
    selected["stop_no"]=pd.to_numeric(selected.stop_number,errors="raise").astype(int)
    rows=[]
    for route,sub in selected.groupby("route_number",sort=True):
        if sub.run_id.nunique()<10 or sub.survey_year.nunique()<5:
            raise ValueError(f"Unqualified source history {route}")
        relation=sub.groupby("stop_no").site_id.nunique()
        inverse=sub.groupby("site_id").stop_no.nunique()
        if set(relation.index)!=set(range(1,11)) or relation.ne(1).any() or inverse.ne(1).any():
            raise ValueError(f"Unstable SiteID-StopNumber mapping {route}")
        once=sub[["stop_no","site_id"]].drop_duplicates()
        g=geo[geo.route_number.eq(route)][["site_id","latitude","longitude","geometry_qc_status"]]
        joined=once.merge(g,on="site_id",how="left",validate="one_to_one")
        if len(joined)!=10 or not joined.geometry_qc_status.eq("pass_unverified").all():
            raise ValueError(f"Unverified geometry in route {route}; no auto repairs")
        for x in joined.itertuples(index=False):
            rows.append({"route_id":route,"site_id":str(x.site_id),"stop_number":int(x.stop_no),
              "latitude":float(x.latitude),"longitude":float(x.longitude),
              "independently_field_verified":False})
    return pd.DataFrame(rows).sort_values(["route_id","stop_number"]),cohort

def shared_grid(stops):
    px,py=project("EPSG:4326","EPSG:5070",stops.longitude.tolist(),stops.latitude.tolist())
    west=30*math.floor((min(px)-1100)/30)
    east=30*math.ceil((max(px)+1100)/30)
    south=30*math.floor((min(py)-1100)/30)
    north=30*math.ceil((max(py)+1100)/30)
    width=int((east-west)/30);height=int((north-south)/30)
    if width<=0 or height<=0 or width*height>MAX_PIXELS_PER_CROP:
        raise ValueError(f"Route AOI too broad; fail closed, area cells {width*height}")
    return (west,south,east,north),width,height

def source_year(year,bbox,width,height):
    if year not in YEARS:raise ValueError("Not a frozen year")
    info,query_sha=src.source_identity_for_year(year)
    rule={"mosaicMethod":"esriMosaicByAttribute",
          "where":f"OBJECTID={info['OBJECTID']} AND Year={year}",
          "sortField":"Year","sortValue":year,"ascending":True}
    params={"bbox":",".join(map(str,bbox)),"bboxSR":"5070","imageSR":"5070",
       "size":f"{width},{height}","format":"tiff","pixelType":"U8",
       "interpolation":"RSP_NearestNeighbor",
       "mosaicRule":json.dumps(rule,separators=(",",":")),
       "renderingRule":json.dumps({"rasterFunction":"None"}),"f":"image"}
    raw,mime=src.source_request("/exportImage",params,limit=14_000_000)
    with MemoryFile(raw) as memory:
        with memory.open() as ds:
            tf=ds.transform
            expected=(30,0,bbox[0],0,-30,bbox[3])
            observed=(tf.a,tf.b,tf.c,tf.d,tf.e,tf.f)
            if (ds.count!=1 or ds.crs is None or ds.crs.to_epsg()!=5070
                or (ds.width,ds.height)!=(width,height)
                or not np.allclose(observed,expected,atol=1e-7,rtol=0)):
                raise ValueError("ImageServer returned unexpected grid/band/CRS")
            arr=ds.read(1)
            if ds.nodata is None:
                valid=np.isin(arr,sorted(CODES))
            else:
                valid=(arr!=ds.nodata)&np.isin(arr,sorted(CODES))
            illegal=set(map(int,np.unique(arr[~valid])))-{0,255}
            if illegal:raise ValueError(f"Unexpected raw NLCD codes {illegal}")
    return arr,valid,{"source_sha256":sha(raw),"bytes":len(raw),
        "catalog_identity":info,"catalog_response_sha256":query_sha,
        "categorical_codes":sorted(set(map(int,np.unique(arr[valid])))),
        "valid_fraction":float(valid.mean()),"year":year}

def analyze(stops,rasters,bbox):
    if set(rasters)!=set(YEARS):raise ValueError("Incomplete raster years")
    shape=next(iter(rasters.values()))[0].shape
    if any(v[0].shape!=shape for v in rasters.values()):
        raise ValueError("Raster dimensions drifted")
    rr,cc=np.indices(shape)
    xg=bbox[0]+30*(cc+.5);yg=bbox[3]-30*(rr+.5)
    px,py=project("EPSG:4326","EPSG:5070",stops.longitude.tolist(),stops.latitude.tolist())
    out=[]
    for station,x,y in zip(stops.itertuples(index=False),px,py):
        for radius in RADII:
            mask=(xg-x)**2+(yg-y)**2<=radius**2
            nominal=int(mask.sum())
            if nominal<40:raise ValueError("Not enough full pixels in circle")
            annual={}
            for year,(img,valid) in rasters.items():
                good=valid&mask
                n=int(good.sum())
                annual[str(year)]={"valid_pixels":n,"valid_fraction":n/nominal,
                  "forest_pct":float(100*(good & np.isin(img,list(FOREST))).sum()/n) if n else None,
                  "agri_pct":float(100*(good & np.isin(img,list(AGRI))).sum()/n) if n else None,
                  "developed_pct":float(100*(good & np.isin(img,list(DEV))).sum()/n) if n else None}
            a,v1=rasters[2011];b,v2=rasters[2012];c,v3=rasters[2013]
            paired=mask&v1&v2&v3
            n=int(paired.sum());pass80=n>=0.8*nominal
            f_before=np.isin(a,list(FOREST))
            f_after=np.isin(b,list(FOREST))
            loss=(paired&f_before&~f_after)
            persisted=(paired&f_before&~f_after&~np.isin(c,list(FOREST)))
            out.append({"route_id":str(station.route_id),"site_id":str(station.site_id),
             "stop_number":int(station.stop_number),"radius_m":radius,
             "n_nominal_pixels":nominal,"paired_valid_fraction":n/nominal,
             "passes_80pct":bool(pass80),"annual":annual,
             "2011_to_2012_transition":{
               "forest_loss_pixels":int(loss.sum()) if pass80 else None,
               "forest_to_developed_pixels":int((loss & np.isin(b,list(DEV))).sum()) if pass80 else None,
               "forest_to_agriculture_pixels":int((loss & np.isin(b,list(AGRI))).sum()) if pass80 else None,
               "2012_loss_class_persists_2013_pixels":int(persisted.sum()) if pass80 else None,
               "forest_gain_pixels":int((paired&~f_before&f_after).sum()) if pass80 else None,
               "fine_class_changed_pixels":int((paired&(a!=b)).sum()) if pass80 else None},
             "historic_station_independently_confirmed":False})
    if len(out)!=20:raise ValueError("Expect 10 sites x two radii")
    return out

def main():
    p=argparse.ArgumentParser()
    for k in ("runs","stops","coords","out_dir"):p.add_argument("--"+k.replace("_","-"),required=True)
    a=p.parse_args()
    root=Path(a.out_dir);root.mkdir(parents=True,exist_ok=True)
    srcs={"Runs.csv":Path(a.runs),"Stops.csv":Path(a.stops),"Coordinates.csv":Path(a.coords)}
    digests={name:sha(path.read_bytes()) for name,path in srcs.items()}
    if digests!={**SOURCE_PINS,"Coordinates.csv":COORD_SHA}:
        raise ValueError("Pinned NAAMP metadata hashes drifted")
    df,cohort=fixed_sources(pd.read_csv(a.runs,dtype=str,keep_default_na=False),
                            pd.read_csv(a.stops,dtype=str,keep_default_na=False),
                            pd.read_csv(a.coords,dtype={"RouteNumber":str,"SiteID":str}))
    result={"analysis":"seven_iowa_routes_nlcd_c1v0_2011_2012_2013_source_only_v22",
       "status":"SOURCE_SCREEN_RUNNING","routes_requested":list(ROUTES),
       "years":list(YEARS),"n_historical_sites_independently_verified":0,
       "new_route_frog_counts_read":False,
       "derived_from_exploratory_360417_2012_land_class_change":True,
       "not_confirmation_of_2012_region_wide_treatment":True,
       "collection_version":"C1V0_Not_C1V2",
       "category_confidence_layer_used":False,
       "original_usgs_metadata_sha256":digests,"route_results":[],
       "failure_records":[]}
    outfile=root/"environment_source_receipt.json"
    for route,group in df.groupby("route_id",sort=True):
        bbox,width,height=shared_grid(group)
        route_dir=root/route;route_dir.mkdir(parents=True,exist_ok=True)
        layers={};yrs={}
        try:
            for year in YEARS:
                img,valid,record=source_year(year,bbox,width,height)
                layers[year]=(img,valid);yrs[str(year)]=record
                print(json.dumps({"route":route,"year":year,"valid_fraction":record["valid_fraction"]}),flush=True)
            sites=analyze(group,layers,bbox)
            result["route_results"].append({"route_id":route,"n_stops":len(group),
                "bbox_epsg5070":list(bbox),"image_grid":[width,height],
                "image_year_provenance":yrs,"buffers":sites,
                "n_250m_stops_with_detected_forest_loss":sum(
                    s["2011_to_2012_transition"]["forest_loss_pixels"]>0 for s in sites
                    if s["radius_m"]==250 and s["passes_80pct"]),
                "n_buffer_records_passing_coverage":sum(s["passes_80pct"] for s in sites)})
        except Exception as e:
            result["failure_records"].append({"route_id":route,
                     "error_type":type(e).__name__,"error":str(e)[:400]})
        outfile.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    result["status"]="COMPLETE_SEVEN_ROUTE_SOURCE_SCREEN" if not result["failure_records"] else "PARTIAL_SOURCE_SCREEN_WITH_FAILURES"
    result["n_routes_complete"]=len(result["route_results"])
    result["n_routes_failed"]=len(result["failure_records"])
    outfile.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"n_routes_complete":result["n_routes_complete"],
         "n_routes_failed":result["n_routes_failed"]}),flush=True)
    if result["n_routes_complete"]<1:
        raise RuntimeError("No route had enough source data for any screening")
if __name__=="__main__":main()
