#!/usr/bin/env python3
"""One-year real NAAMP × annual NLCD Collection 1.2 land-cover extraction.

Downloads precisely one validated public MRLC year archive into temporary
runner disk, extracts TIFF once, then exports ONLY small site-year CSV + QC
receipt. Reads Runs, Stops, physical site IDs, and official metadata; NEVER
reads Counts.csv or calling outcomes. No scientific effect inference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import shutil
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from probe_official_nlcd_c1v2 import list_c1v2
from extract_nlcd_buffers import run as raster_extract

BASE="https://www.mrlc.gov/downloads/sciweb1/shared/mrlc/data-bundles/"
MAX_ARCHIVE_BYTES=1_600_000_000
UA="frogcs-nlcd-annual-c1v2-one-year-extraction/0.1"

def stream_source(url,outfile,expected):
    """Stream one archive; never buffer image bytes in RAM."""
    if not 100_000_000<expected<MAX_ARCHIVE_BYTES:
        raise ValueError("unexpected archive size")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":f"bytes=0-{expected-1}"})
    t0=time.monotonic();total=0
    digest=hashlib.sha256()
    with urllib.request.urlopen(req,timeout=120) as resp:
        if resp.status not in (200,206):
            raise RuntimeError(f"download returned status {resp.status}")
        rng=resp.headers.get("Content-Range")
        if resp.status==206 and rng!=f"bytes 0-{expected-1}/{expected}":
            raise RuntimeError(f"unexpected Content-Range: {rng}")
        clen=resp.headers.get("Content-Length")
        if clen is not None and int(clen)!=expected:
            raise RuntimeError(f"unexpected Content-Length: {clen}")
        with open(outfile,"wb") as f:
            while True:
                part=resp.read(1024*1024*4)
                if not part:break
                total+=len(part)
                if total>expected:raise RuntimeError("archive exceeds pinned size")
                digest.update(part); f.write(part)
                if time.monotonic()-t0>1200:
                    raise RuntimeError("bounded download time exceeded")
    if total!=expected:raise RuntimeError(f"incomplete archive: got {total}, expected {expected}")
    return {"bytes":total,"sha256":digest.hexdigest(),
            "download_seconds":round(time.monotonic()-t0,3),"http_status":resp.status}

def extract_verified_tiff(zipfile_path,year,output_path):
    stem=f"Annual_NLCD_LndCov_{year}_CU_C1V2"
    with zipfile.ZipFile(zipfile_path) as archive:
        candidates=[info for info in archive.infolist() if info.filename==stem+".tif"]
        if len(candidates)!=1:raise RuntimeError(f"expected one C1V2 original TIFF for {year}")
        info=candidates[0]
        if info.file_size<=100_000_000:raise RuntimeError("unexpected small source GeoTIFF")
        sha=hashlib.sha256()
        with archive.open(info,"r") as src,open(output_path,"wb") as dest:
            while True:
                chunk=src.read(1024*1024*4)
                if not chunk:break
                sha.update(chunk);dest.write(chunk)
        if output_path.stat().st_size!=info.file_size:
            raise RuntimeError("decompressed original TIFF byte count mismatch")
        return {"zip_member":info.filename,"zip_method":info.compress_type,
                "tiff_bytes":info.file_size,"tiff_crc32":format(info.CRC,"08x"),
                "tiff_sha256":sha.hexdigest()}

def check_raster(path):
    import rasterio
    with rasterio.open(path) as ds:
        if ds.count!=1 or ds.crs is None or not ds.crs.is_projected:
            raise RuntimeError("unusable non-categorical or unprojected source")
        if not (abs(ds.res[0]-30)<0.01 and abs(ds.res[1]-30)<0.01):
            raise RuntimeError(f"source resolution not 30m: {ds.res}")
        if ds.dtypes[0] not in ("uint8","uint16"):
            raise RuntimeError(f"unexpected NLCD categorical dtype {ds.dtypes[0]}")
        return {"width":ds.width,"height":ds.height,
                "pixel_size_m":[round(v,5) for v in ds.res],
                "dtype":ds.dtypes[0],"nodata":ds.nodata,"crs":str(ds.crs)[:300]}

def run(year,coords,calendar,outdir):
    if not 2001<=year<=2015:raise ValueError("out of scope year")
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    official=list_c1v2()[year]
    url=BASE+official["file"]
    expected=official["bytes"]
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix=f"frogcs_c1v2_{year}_") as temp:
        t=Path(temp); zip_path=t/(official["file"])
        download=stream_source(url,zip_path,expected)
        tif_path=t/(f"annual_{year}.tif")
        member=extract_verified_tiff(zip_path,year,tif_path)
        zip_path.unlink()
        raster=check_raster(tif_path)
        csv_out=outdir/f"nlcd_c1v2_{year}_site_year_buffers.csv"
        rows=raster_extract(coords,str(t/"annual_{year}.tif"),[year],
                           [100,500],csv_out,0.8,calendar)
    receipt={"analysis":"real_naamp_annual_nlcd_c1v2_{year}_outcome_blind".format(year=year),
             "year":year,"version":"USGS Annual NLCD Collection 1.2",
             "usgs_official_item":"697b9279b66b0197c3043cc3",
             "usgs_nlcd_doi":"10.5066/P94UXNTS",
             "mrlc_original_zip_url":url,"official_zip_bytes":expected,
             "archive":download,"tiff":member,"raster":raster,
             "buffers":rows,
             "elapsed_seconds":round(time.monotonic()-start,2),
             "counts_csv_downloaded":False,"frog_outcomes_read":False,
             "independent_replication":False,"ecological_effects_estimated":False}
    receipt_out=outdir/f"nlcd_c1v2_{year}_receipt.json"
    receipt_out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True,indent=2))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year",required=True,type=int)
    p.add_argument("--accepted-coordinates",required=True)
    p.add_argument("--site-calendar",required=True)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    run(a.year,a.accepted_coordinates,a.site_calendar,a.out_dir)
