#!/usr/bin/env python3
"""Outcome-blind JRC monthly surface-water pilot at historical NAAMP sites.

Uses a FULLY PRECEDING calendar month, not the month containing the frog
survey. JRC monthly detection is NOT event-day inundation, water depth,
hydroperiod, or proof of breeding-site suitability.

Data: EC JRC/Google GSW MonthlyHistory VER5-0, tiles 2000-2015.
No Counts.csv or frog outcomes are downloaded/read.
"""
from __future__ import annotations
import argparse
import calendar
import csv
import datetime as dt
import hashlib
import json
import math
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from probe_dswe_site_survey_coverage import read_sites

BASE="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER5-0/tiles"
USER_AGENT="frogcs-independent-jrc-monthly-source-pilot/0.1"
MAX_SOURCE_BYTES=90_000_000
MAX_TOTAL_BYTES=300_000_000

def preceding_month(iso_date):
    day=dt.date.fromisoformat(iso_date)
    last=day.replace(day=1)-dt.timedelta(days=1)
    return last.year,last.month

def jrc_tile(lat,lon):
    if not (24 <= lat <= 51 and -126 <= lon <= -66):
        raise ValueError("outside CONUS study region")
    north=math.ceil(lat/10.0)*10
    west=math.floor(lon/10.0)*10
    # JRC tiles are 10 x 10 degrees, 40,000 px each, from (-180,80).
    y=int(round((80-north)*4000))
    x=int(round((west+180)*4000))
    if y<0 or x<0 or y%40000 or x%40000:
        raise ValueError("JRC grid offset impossible")
    return f"{y:010d}-{x:010d}"

def source_url(year,month,lat,lon):
    if not (1984<=year<=2021 and 1<=month<=12):
        raise ValueError("unsupported JRC v1.4 history date")
    stem=f"{year}_{month:02d}"
    return f"{BASE}/{year}/{stem}/{stem}-{jrc_tile(lat,lon)}.tif"

def download_bounded(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    sha=hashlib.sha256()
    downloaded=0
    with urllib.request.urlopen(req,timeout=35) as response,open(path,"wb") as dest:
        if int(response.status)!=200:raise RuntimeError("unexpected source HTTP response")
        declared=response.headers.get("Content-Length")
        if declared and int(declared)>MAX_SOURCE_BYTES:
            raise RuntimeError("tile too large for audit")
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            downloaded+=len(chunk)
            if downloaded>MAX_SOURCE_BYTES:raise RuntimeError("tile exceeded 90 MB safety gate")
            dest.write(chunk);sha.update(chunk)
    if downloaded<100_000 or not path.exists():
        raise RuntimeError("source too small")
    return {"bytes":downloaded,"sha256":sha.hexdigest(),"url":url}

def water_fraction(ds,lat,lon,radius_m):
    """Geodesic 100/500m buffer; 0=no-observation, 1=land, 2=water."""
    import numpy as np
    from pyproj import Geod
    from rasterio.windows import from_bounds
    if ds.count!=1 or ds.crs.to_epsg()!=4326:
        raise ValueError("expected a 1-band JRC EPSG:4326 tile")
    geod=Geod(ellps="WGS84")
    deglat=radius_m/110_500 +.001
    deglon=radius_m/(111_000*math.cos(math.radians(lat)))+.001
    win=from_bounds(lon-deglon,lat-deglat,lon+deglon,lat+deglat,ds.transform)
    win=win.round_offsets().round_lengths()
    a=ds.read(1,window=win,masked=False,boundless=True,fill_value=0)
    rows,cols=np.indices(a.shape)
    xx,yy=ds.window_transform(win)*(cols+.5,rows+.5)
    _,_,d=geod.inv(np.full_like(xx,lon,dtype=float),
                    np.full_like(yy,lat,dtype=float),xx,yy)
    inside=d<=radius_m
    values=a[inside]
    if np.any(~np.isin(values,[0,1,2])):
        raise ValueError("unexpected JRC raw water values; fail closed")
    n=int(values.size)
    observed=int(np.isin(values,[1,2]).sum())
    water=int((values==2).sum())
    return {"radius_m":radius_m,"n_buffer_pixels":n,"n_valid_pixels":observed,
            "n_water_pixels":water,"n_no_observation":n-observed,
            "valid_fraction":round(observed/n,6) if n else None,
            "water_fraction_among_observed":round(water/observed,6) if observed else None,
            "coverage_ge_50pct":bool(n and observed/n>=0.5),
            "coverage_ge_80pct":bool(n and observed/n>=0.8)}

def run(coords,calendar_path,out):
    import rasterio
    nine=read_sites(coords,calendar_path)
    sites=[nine[k] for k in (0,3,6)]  # one deterministic state/event in 2001, 2008, 2015
    paths={}
    rec=[]
    transferred=0
    with tempfile.TemporaryDirectory(prefix="frogcs_jrc_pilot_") as directory:
        for site in sites:
            y,m=preceding_month(site["date"])
            url=source_url(y,m,site["lat"],site["lon"])
            row=dict(site,pre_survey_month=f"{y}-{m:02d}",source_url=url,
                     historical_jrc_version="VER5-0",no_outcomes_read=True)
            try:
                if url not in paths:
                    target=Path(directory)/(hashlib.sha256(url.encode()).hexdigest()+".tif")
                    source=download_bounded(url,target)
                    transferred+=source["bytes"]
                    if transferred>MAX_TOTAL_BYTES:raise RuntimeError("total download exceeds budget")
                    paths[url]=(target,source)
                target,source=paths[url]
                with rasterio.open(target) as ds:
                    row["source"]=source
                    row["buffers"]=[water_fraction(ds,site["lat"],site["lon"],r)
                                    for r in (100,500)]
                    row["status"]="original_pixels_read"
            except (urllib.error.URLError,TimeoutError,ValueError,RuntimeError,rasterio.errors.RasterioIOError) as exc:
                row.update(status="source_or_pixel_unavailable",
                           error=type(exc).__name__+": "+str(exc)[:240])
            rec.append(row)
    report={"analysis":"jrc_fully_prior_month_naamp_site_pilot_v0_1",
            "dataset":"JRC Global Surface Water MonthlyHistory VER5-0",
            "data_producer":"EC JRC/Google", "citation":"Pekel et al. 2016 doi:10.1038/nature20584",
            "status":"outcome_blind_environment_only", "sample_selection":"first state of each year (2001,2008,2015) from fixed 9-event DSWE metadata pilot",
            "previous_calendar_month_only":True,
            "same_month_and_future_data_excluded":True,
            "months_are_not_day_of_survey_state":True,
            "pixels_are_not_water_depth":True,
            "frog_outcomes_read":False,"n_site_surveys":len(rec),
            "n_sites_with_original_pixels":sum(x["status"]=="original_pixels_read" for x in rec),
            "n_sites_with_500m_50pct_coverage":sum(
                x["status"]=="original_pixels_read" and x["buffers"][1]["coverage_ge_50pct"]
                for x in rec),
            "bytes_transferred":transferred,"entries":rec}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="entries"},indent=2,sort_keys=True))
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accepted-coordinates",required=True)
    parser.add_argument("--site-calendar",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    run(args.accepted_coordinates,args.site_calendar,args.out)
