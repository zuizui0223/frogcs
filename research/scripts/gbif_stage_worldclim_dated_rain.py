#!/usr/bin/env python3
"""Join full GBIF focal 1° species×stage×year×month reporting to CRU WorldClim rain.

2010–2024 historical monthly precipitation (mm), 10 arc-min raster sampled at
GBIF 1° cell centres. NOT frogcs 72h rainfall signal or frog occupancy data.
Keep full original GBIF source rows and explicit NA for offshore climate cells.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import math
import re
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile

URLS={
    "2010-2019":"https://geodata.ucdavis.edu/climate/worldclim/2_1/hist/cts4.09/wc2.1_cruts4.09_10m_prec_2010-2019.zip",
    "2020-2024":"https://geodata.ucdavis.edu/climate/worldclim/2_1/hist/cts4.09/wc2.1_cruts4.09_10m_prec_2020-2024.zip"
}
MONTH=re.compile(r"(?:19|20)\d{2}[_-]?(?:0[1-9]|1[0-2])")


def get_input(path):
    p=list(Path(path).rglob("focal_stage_1deg_month_year.csv"))
    if len(p)!=1:
        raise RuntimeError("Expected exactly one source GBIF 1° stage grid CSV, found "+str(p))
    obs=[]
    ym=collections.defaultdict(set)
    with p[0].open("r",encoding="utf8",newline="") as f:
        for r in csv.DictReader(f):
            y=int(r["year"]);m=int(r["month"])
            x=int(r["loncell"]);z=int(r["latcell"])
            n=int(r["n_records"])
            if not 2010<=y<=2024:
                continue
            if not 1<=m<=12 or not (-180<=x<180 and -90<=z<90) or n<1:
                continue
            obs.append(dict(
                species=r["species"],stage=r["stage"],loncell=x,latcell=z,
                year=y,month=m,n_records=n))
            ym[(y,m)].add((z,x))
    if len(obs)<10000:
        raise RuntimeError("Too few GBIF stage/dated rows in source")
    return obs,ym


def download_zip(url,target):
    h=hashlib.sha256()
    total=0
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-global-rain/0.1 (historical monthly CRU data scientific study)"})
    with urllib.request.urlopen(req,timeout=140) as source, open(target,"wb") as f:
        while True:
            piece=source.read(1<<20)
            if not piece:break
            total+=len(piece)
            if total>260_000_000:
                raise RuntimeError("Unexpected >260MB historical precipitation archive")
            h.update(piece)
            f.write(piece)
    if not zipfile.is_zipfile(target):
        raise RuntimeError("WorldClim precipitation archive is not ZIP")
    return dict(url=url,bytes=total,sha256=h.hexdigest())


def get_month_names(z,period):
    dat={}
    for fi in z.infolist():
        if fi.is_dir() or not fi.filename.lower().endswith((".tif",".tiff")):
            continue
        matches=MONTH.findall(fi.filename)
        # str.finditer preserving full match, e.g. 2010_01
        allm=[m.group(0) for m in MONTH.finditer(fi.filename)]
        if len(allm)!=1:
            continue
        val=allm[0].replace("-","").replace("_","")
        year,month=int(val[:4]),int(val[4:])
        if not (2010<=year<=2024 and 1<=month<=12):
            continue
        if (year,month) in dat:
            raise RuntimeError("Duplicate WorldClim year-month "+val)
        dat[(year,month)]=fi.filename
    expect=120 if period=="2010-2019" else 60
    if len(dat)!=expect:
        raise RuntimeError(f"WorldClim {period} expected {expect} TIFs, parsed {len(dat)}, examples: {list(z.namelist())[:7]}")
    if sum(x.file_size for x in z.infolist())>4_000_000_000:
        raise RuntimeError("Unexpected uncompressed size >4GB")
    return dat


def sample_month(z,filename,positions):
    # MemoryFile avoids extracting >100 global TIFFs to disk; each month
    # raster is around the size of the 10-arcmin world land grid.
    raw=z.read(filename)
    with MemoryFile(raw) as mem,mem.open() as raster:
        if raster.crs is None or raster.crs.to_epsg()!=4326:
            raise RuntimeError("Non WGS84 climate GeoTIFF "+filename)
        coords=[(lon+.5,lat+.5) for lat,lon in positions]
        vals={}
        for (lat,lon),array in zip(positions,raster.sample(coords,masked=True)):
            if len(array)<1 or np.ma.is_masked(array[0]):
                vals[(lat,lon)]=None
                continue
            p=float(array[0])
            if not math.isfinite(p) or (raster.nodata is not None and p==raster.nodata):
                vals[(lat,lon)]=None
            elif p<0 or p>25000:
                raise RuntimeError(f"Impossible monthly precipitation in {filename}: {p}")
            else:
                vals[(lat,lon)]=round(p,4)
        return vals


def write_csv(path,rows,keys):
    with Path(path).open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction="ignore")
        w.writeheader();w.writerows(rows)


def run(folder,src):
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    source,ym=get_input(src)
    weather={}
    archives=[]
    with tempfile.TemporaryDirectory() as work:
        for period,url in URLS.items():
            file=Path(work)/(period+".zip")
            receipt=download_zip(url,file)
            with zipfile.ZipFile(file) as z:
                names=get_month_names(z,period)
                receipt["included_months"]=len(names)
                receipt["raster_file_count"]=len(z.namelist())
                for key,name in sorted(names.items()):
                    pos=sorted(ym.get(key,set()))
                    if not pos:continue
                    for (lat,lon),p in sample_month(z,name,pos).items():
                        weather[(lat,lon,key[0],key[1])]=p
            archives.append(receipt)
    result=[]
    rain_by_stage=collections.defaultdict(list)
    nonnull=set()
    for r in source:
        key=(r["latcell"],r["loncell"],r["year"],r["month"])
        p=weather.get(key)
        if p is not None:
            nonnull.add(key)
            rain_by_stage[r["stage"]].append(p)
        result.append(dict(
            **r, precipitation_mm_month=p if p is not None else "",
            climate_grid_centre_latitude=r["latcell"]+.5,
            climate_grid_centre_longitude=r["loncell"]+.5,
            climate_status="ON_LAND_CRU_MONTHLY_RAIN" if p is not None
                            else "MISSING_OR_NONLAND"))
    write_csv(out/"gbif_stage_1degree_year_month_precipitation.csv",result,[
        "species","stage","loncell","latcell","year","month","n_records",
        "precipitation_mm_month","climate_grid_centre_latitude",
        "climate_grid_centre_longitude","climate_status"])
    unique=[
        dict(latcell=lat,loncell=lon,year=year,month=month,
             precipitation_mm_month=p if p is not None else "",
             status="ON_LAND" if p is not None else "NONLAND_OR_MASKED")
        for (lat,lon,year,month),p in sorted(weather.items())]
    write_csv(out/"unique_geographic_rain_exposure_cells.csv",unique,[
        "latcell","loncell","year","month","precipitation_mm_month","status"])
    summary={
        "date":"2026-10-25",
        "source_rain":"WorldClim 2.1 downscaled historical CRU-TS4.09 precipitation 10 arcmin 2010–2024",
        "source_GBIF":"Anonymous experimental 2026-08 Anura/Odonata species stage 1° month/year aggregate",
        "citations":[
            "Fick & Hijmans 2017 DOI:10.1002/joc.5086",
            "Harris et al 2020 Scientific Data 7:109",
        ],
        "source_zip_receipts":archives,
        "observed_stage_grid_rows_2010_2024":len(source),
        "observed_stage_grid_rows_with_precipitation":sum(1 for r in result if r["climate_status"]=="ON_LAND_CRU_MONTHLY_RAIN"),
        "observed_stage_grid_rows_missing_or_nonland":sum(1 for r in result if r["climate_status"]!="ON_LAND_CRU_MONTHLY_RAIN"),
        "unique_world_grid_year_month_rain_cells":len(weather),
        "unique_world_grid_year_month_cells_with_rain":
            sum(v is not None for v in weather.values()),
        "species_with_precipitation":len({
            r["species"] for r in result if r["climate_status"]=="ON_LAND_CRU_MONTHLY_RAIN"}),
        "stage_coverages":{
            stage:{"reporting_cells_with_rain":len(samples),
                   "median_mm_per_month":round(float(np.median(samples)),3),
                   "p25_mm":round(float(np.quantile(samples,.25)),3),
                   "p75_mm":round(float(np.quantile(samples,.75)),3)}
            for stage,samples in rain_by_stage.items() if samples},
        "warnings":[
            "Climatological monthly CRU downscaled to 10 arcmin within 1° GBIF-cell centroid; not actual sensor rainfall at frog chorus stations.",
            "Monthly precipitation does NOT encode 0–72 h rain pulse from NAAMP, or hydroperiod/standing-water presence.",
            "1° grid centroid may fall offshore even for a coastal onshore occurrence; masked values are kept missing.",
            "GBIF life-stage record geography is observation-effort biased and source-stage proportions do not estimate cohort demography.",
            "Rain by stage are descriptive reporting-location distributions, NOT a causal or ecological preference estimate.",
            "2025 and 2026 have no source precipitation under this version of monthly weather and were not interpolated.",
            "No aquatic predator real attacks, plant stem architecture, frog chorus or same-pond reproduction measured."
        ]
    }
    (out/"observed_results.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_GBIF_CLIMATE_MONTHLY_JOIN")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("END_GBIF_CLIMATE_MONTHLY_JOIN")


def selftest():
    import io
    assert MONTH.fullmatch("2010_01") is not None
    assert MONTH.fullmatch("2024-12") is not None
    assert (2010,1) in {(int(a[:4]),int(a[5:])) for a in ["2010_01"]}
    print("WORLDCLIM_MONTHLY_DATE_SOURCE_QA_PASS")


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--src",default="research/data/gbif_open_artifact")
    ap.add_argument("--out",default="research/results/gbif_worldclim_monthly_rain")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:selftest()
    else:run(args.out,args.src)
