#!/usr/bin/env python3
"""Outcome-blind C1V1 pipeline pilot at actual 2001 NAAMP survey SiteIDs.
Historical C1V1 is a technical pilot only; not interchangeable with C1.2.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

URL="https://usgs.osn.mghpcc.org/hytest/nlcd/annual-nlcd-cu-c1v1/mosaic/Annual_NLCD_LndCov_2001_CU_C1V1.tif"

def choose(coords_file,calendar_file,max_states=5):
    with Path(coords_file).open(newline="",encoding="utf-8-sig") as f:
        coords={(r["RouteNumber"].strip(),r["SiteID"].strip()):r
                for r in csv.DictReader(f) if r["status"].strip()=="accepted"}
    by_state=defaultdict(set)
    with Path(calendar_file).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        fields=reader.fieldnames or []
        if not {"State","RouteNumber","SiteID","SurveyYear"}.issubset(fields):
            raise ValueError("incomplete outcome-blind site calendar")
        if "Species" in fields or "CallingIndex" in fields:
            raise ValueError("refuse outcome-containing site calendar")
        for r in reader:
            if r["SurveyYear"].strip()!="2001":continue
            key=(r["RouteNumber"].strip(),r["SiteID"].strip())
            if key in coords: by_state[r["State"].strip()].add(key)
    selected=[]
    for state in sorted(by_state)[:max_states]:
        ranked=sorted(by_state[state],key=lambda k:hashlib.sha256((k[0]+":"+k[1]).encode()).hexdigest())
        route,site=ranked[0]
        pos=coords[(route,site)]
        selected.append({"State":state,"RouteNumber":route,"SiteID":site,
                         "lat":float(pos["lat"]),"lon":float(pos["lon"]),"SurveyYear":2001})
    if len(selected)<3:raise RuntimeError("insufficient 2001 outcome-blind source sites")
    return selected

def run(coords_file,calendar_file,out_file):
    import rasterio
    from extract_nlcd_buffers import extract_point
    sites=choose(coords_file,calendar_file)
    rows=[]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
        GDAL_HTTP_MAX_RETRY="0",GDAL_HTTP_TIMEOUT="12",GDAL_HTTP_CONNECTTIMEOUT="8"):
        with rasterio.open("/vsicurl/"+URL) as ds:
            if ds.count!=1:raise ValueError("original categorical raster must have one band")
            for site in sites:
                for radius in (100,500):
                    result=extract_point(ds,site["lat"],site["lon"],radius_m=radius,min_coverage=0.8)
                    rows.append({"State":site["State"],"RouteNumber":site["RouteNumber"],
                                 "SiteID":site["SiteID"],"SurveyYear":2001,**result})
    report={"analysis":"real_naamp_landcover_extraction_pilot_v0_1",
        "source_version":"Annual NLCD Collection 1.1",
        "not_final_1_2_environmental_dataset":True,"year":2001,"source_url":URL,
        "selection":"One deterministic SHA256-minimum 2001-visited site per first five states alphabetically; independent of frog outcomes",
        "n_unique_states":len(sites),"n_unique_real_naamp_sites":len(sites),
        "n_buffer_rows":len(rows),"n_buffers_with_80pct_valid_coverage":sum(r["qc_status"]=="ok" for r in rows),
        "radii_m":[100,500],"outcomes_read":False,"mosaic_downloaded_entirely":False,"rows":rows}
    out=Path(out_file)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="rows"},indent=2,sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--accepted-coordinates",required=True)
    p.add_argument("--site-calendar",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.accepted_coordinates,a.site_calendar,a.out)
