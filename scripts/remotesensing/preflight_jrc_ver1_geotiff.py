#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import rasterio
from rasterio.windows import Window

URL="https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/VER1-0/tiles/2001/2001_05/2001_05-0000000000-0000000000.tif"
OUT=Path("remotesensing/JRC_VER1_GEOTIFF_PREFLIGHT_V0_1.json")

with rasterio.Env(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
):
    with rasterio.open(URL) as ds:
        h=min(20,ds.height); w=min(20,ds.width)
        a=ds.read(1,window=Window(0,0,w,h))
        vals=sorted(set(int(x) for x in a.ravel()))
        out={
            "analysis":"jrc_ver1_geotiff_preflight_v0_1",
            "url":URL,
            "crs":str(ds.crs),
            "bounds":[float(ds.bounds.left),float(ds.bounds.bottom),float(ds.bounds.right),float(ds.bounds.top)],
            "width":ds.width,
            "height":ds.height,
            "transform":[float(x) for x in ds.transform[:6]],
            "dtype":str(ds.dtypes[0]),
            "nodata":ds.nodata,
            "block_shapes":[list(x) for x in ds.block_shapes],
            "compression":str(ds.compression),
            "interleaving":ds.profile.get("interleave"),
            "sample_upper_left_values":vals,
            "raster_values_read":True,
            "frog_outcomes_read":False
        }

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
