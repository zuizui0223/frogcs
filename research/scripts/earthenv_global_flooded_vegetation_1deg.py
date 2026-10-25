#!/usr/bin/env python3
"""Global 1° environmental BACKGROUND from EarthEnv 1-km landcover.

Tuanmu & Jetz 2014, Global Ecology and Biogeography 23:1031–1045.
https://www.earthenv.org/landcover (full v1.0; CC BY-NC 4.0).

Class 8 regularly flooded vegetation ≠ Typha/reed density,
class 12 open water ≠ event inundation, class 6 general herbaceous vegetation
≠ emergent plants. This does NOT measure a pond's actual structure.
"""
import argparse
import csv
import hashlib
import json
import os
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from rasterio.warp import reproject

BASE="https://data.earthenv.org/consensus_landcover/with_DISCover/consensus_full_class_"
CLASSES={8:"flooded_vegetation",12:"open_water",6:"generic_herbaceous"}
MAX_BYTES=150_000_000
DST_TRANSFORM=from_origin(-180,90,1,1)
DST_SHAPE=(180,360)
YEAR_REFERENCE="Composite of landcover inputs ~1992–2006, EarthEnv full v1.0"

def get(url, dest):
    expected=0
    sha=hashlib.sha256()
    h=hashlib.md5()
    tic=time.monotonic()
    request=urllib.request.Request(url,headers={
        "User-Agent":"Frogcs-EcologyMacro/1.0 (EarthEnv academic ecology reuse CC-BY-NC)",
        "Accept":"image/tiff,application/octet-stream,*/*"})
    with urllib.request.urlopen(request,timeout=180) as resp,open(dest,"wb") as f:
        while True:
            raw=resp.read(1<<20)
            if not raw:break
            expected+=len(raw)
            if expected>MAX_BYTES:
                raise RuntimeError("EarthEnv exceeds 150MB source cap")
            sha.update(raw)
            h.update(raw)
            f.write(raw)
    if expected<10_000_000:
        raise ValueError(f"Unexpectedly small EarthEnv source: {expected}")
    with open(dest,"rb") as f:
        header=f.read(8)
    if header[:4] not in (b"II*\x00",b"MM\x00*",
                         b"II+\x00",b"MM\x00+"):
        raise RuntimeError(f"EarthEnv source not TIFF; first8={header!r}")
    return dict(url=url,bytes=expected,sha256=sha.hexdigest(),
                md5=h.hexdigest(),elapsed_seconds=round(time.monotonic()-tic,2))

def aggregate_raster(filename):
    with rasterio.open(filename) as src:
        if src.count!=1:
            raise ValueError("EarthEnv raster must be single band")
        if src.crs is None:
            raise ValueError("EarthEnv raster missing coordinate system")
        if src.width<10000 or src.height<10000:
            raise ValueError("EarthEnv input not full-resolution global 1km layer")
        dest=np.full(DST_SHAPE,np.nan,dtype=np.float32)
        reproject(
            source=rasterio.band(src,1),
            destination=dest,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=DST_TRANSFORM,
            dst_crs="EPSG:4326",
            dst_nodata=np.nan,
            resampling=Resampling.average,
            num_threads=2,
            init_dest_nodata=True
        )
        finite=dest[np.isfinite(dest)]
        if finite.size<30000:
            raise RuntimeError(f"Too few EarthEnv valid 1degree cells {finite.size}")
        if np.min(finite)<-.005 or np.max(finite)>100.005:
            raise RuntimeError(f"EarthEnv consensus outside expected [0,100] "
                               f"{float(np.min(finite))}..{float(np.max(finite))}")
        audit=dict(
            crs=str(src.crs),
            width=int(src.width),height=int(src.height),
            transform=list(tuple(src.transform)[:6]),
            bounds=[src.bounds.left,src.bounds.bottom,
                    src.bounds.right,src.bounds.top],
            datatype=str(src.dtypes[0]),nodata=src.nodata,
            global_dst_valid_cells=int(finite.size),
            dst_min_pct=float(np.min(finite)),
            dst_max_pct=float(np.max(finite)),
            dst_median_pct=float(np.median(finite)),
            dst_positive_cells=int(np.sum(finite>0)),
            dst_q90_pct=float(np.quantile(finite,.9)),
        )
        return dest,audit

def write(out, arrays, source_audits):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    file=out/"earthenv_1deg_landcover_background.csv"
    valid=0
    both=0
    with file.open("w",newline="",encoding="utf8") as f:
        keys=["latcell","loncell","latitude_center","longitude_center",
              "regularly_flooded_vegetation_pct",
              "open_water_pct","generic_herbaceous_pct",
              "valid_layer_count","classification"]
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader()
        for iy in range(180):
            for ix in range(360):
                values={q:float(arrays[q][iy,ix])
                        if np.isfinite(arrays[q][iy,ix]) else None
                        for q in arrays}
                k=sum(v is not None for v in values.values())
                if not k:continue
                valid+=1
                if k==len(CLASSES):both+=1
                writer.writerow(dict(
                    latcell=89-iy,loncell=-180+ix,
                    latitude_center=89.5-iy,longitude_center=-179.5+ix,
                    regularly_flooded_vegetation_pct=(
                        "" if values[8] is None else round(values[8],5)),
                    open_water_pct=(
                        "" if values[12] is None else round(values[12],5)),
                    generic_herbaceous_pct=(
                        "" if values[6] is None else round(values[6],5)),
                    valid_layer_count=k,
                    classification="EARTHENV_2000s_STATIC_CONSENSUS_1DEG_NOT_EMERGENT_STEM_DENSITY"))
    summary={
        "date":"2026-10-25",
        "status":"GLOBAL_1DEG_EARTHENV_STATIC_WETLAND_CONTEXT",
        "dataset":"EarthEnv Global 1-km Consensus Land Cover v1 full (with DISCover), Tuanmu & Jetz 2014",
        "source":"https://www.earthenv.org/landcover",
        "license":"CC BY-NC 4.0. Credit original 2014 authors. No rights waived.",
        "temporal_scope":YEAR_REFERENCE,
        "aggregation":"rasterio GDAL bilinear-free area average of original percentage consensus within 1degree geographic EPSG4326 cells; not equal-area global mean",
        "download_receipts":source_audits,
        "total_world_1deg_cells":180*360,
        "at_least_one_valid_layer_cells":valid,
        "all_three_valid_layer_cells":both,
        "layer_summary":{
            str(k):source_audits[str(k)]["raster"] for k in CLASSES
        },
        "scientific_boundaries":[
            "Regularly flooded vegetation is heterogeneous wetlands including non-emergent categories, not direct Typha/Phragmites or plant stem densities.",
            "One-degree grid and old composited remote-sensing inputs do not describe event-level water depth or present-day vegetation change.",
            "Missing southern-band pixels are not vegetation absent and must not be filled with zero.",
            "Data are static historical land cover; not time-varying marsh cover or frog chorus.",
            "Grid-level percentage consensus is not exact area fraction of wetland or area-weighted latitude fraction.",
            "Independent occurrence sampling effort and matched prey controls are mandatory for ecological comparisons."
        ]
    }
    (out/"observed_results.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_EARTHENV_1DEG_WETLAND_BACKGROUND")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("END_EARTHENV_1DEG_WETLAND_BACKGROUND")

def selftest():
    srcarray=np.zeros((8,8),dtype="uint8")
    srcarray[:4,:4]=80
    trans=from_origin(0,4,.5,.5)
    with MemoryFile() as mem:
        with mem.open(driver="GTiff",width=8,height=8,count=1,dtype="uint8",
                      crs="EPSG:4326",transform=trans) as dst:
            dst.write(srcarray,1)
        with mem.open() as dataset:
            reduced=np.full((4,4),np.nan,dtype=np.float32)
            reproject(rasterio.band(dataset,1),reduced,
                dst_transform=from_origin(0,4,1,1),
                dst_crs="EPSG:4326",dst_nodata=np.nan,
                resampling=Resampling.average)
    assert np.all(reduced[:2,:2]==80)
    assert np.all(reduced[2:,2:]==0)
    assert -180+(359+.5)==179.5
    assert 89.5-179==-89.5
    print("EARTHENV_STATIC_1DEG_AGGREGATION_SYNTHETIC_QA_PASS")

def run(out):
    with tempfile.TemporaryDirectory(prefix="frogcs_earthenv_global_") as td:
        arrays={}
        receipts={}
        for k,label in CLASSES.items():
            url=f"{BASE}{k}.tif"
            source=Path(td)/f"consensus_full_class_{k}.tif"
            v=get(url,source)
            a,metadata=aggregate_raster(source)
            arrays[k]=a
            v["class_id"]=k
            v["class_description"]=label
            v["raster"]=metadata
            receipts[str(k)]=v
        write(out,arrays,receipts)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="research/results/earthenv_wetland_1deg")
    ap.add_argument("--self-test",action="store_true")
    opt=ap.parse_args()
    if opt.self_test:selftest()
    else:run(opt.out)
