#!/usr/bin/env python3
"""Bounded ORIGINAL USGS OGC WCS GeoTIFF technical access check, NO frogs.

Proof of WCS GeoTIFF access is *not* proof of NLCD Collection 1.2.
This non-NAAMP canary AOI is a fixed 64×64-pixel Iowa-centred square,
not selected after inspecting calling or ecological endpoints.
All fetched bytes are capped at 4 MiB, and status/mime/TIFF identity checked.
No requester-pays, client cloud credentials, or site dataset involved.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from pyproj import Transformer
import rasterio
from rasterio.io import MemoryFile

HOST="dmsdata.cr.usgs.gov"
WORKSPACES={
    "landcover":"mrlc_Land-Cover-Native_conus_year_data",
    "confidence":"mrlc_Land-Cover-Confidence-Native_conus_year_data"
}
SOURCE_YEAR=2012
AOI_POINT_WGS84=(-93.0,42.0)  # arbitrary SOURCE-ONLY technical canary; not NAAMP selected
GRID=30.
WIDTH=64
HEIGHT=64
LIMIT=4_000_000
FOREST={41,42,43}
CODES={11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95}

def bbox5070():
    transformer=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True)
    x,y=transformer.transform(*AOI_POINT_WGS84)
    origin_x=round(x/GRID)*GRID
    origin_y=round(y/GRID)*GRID
    return (origin_x-WIDTH*GRID/2,origin_y-HEIGHT*GRID/2,
            origin_x+WIDTH*GRID/2,origin_y+HEIGHT*GRID/2)

def coverage_name(workspace):
    # Exact ID read in official 2026-10-15 WCS2 GetCapabilities / DescribeCoverage.
    return workspace+"__"+workspace.removeprefix("mrlc_")

def url_for_workspace(workspace):
    base=f"https://{HOST}/geoserver/{workspace}/wcs"
    xmin,ymin,xmax,ymax=bbox5070()
    parms=[
      ("SERVICE","WCS"),("VERSION","2.0.1"),("REQUEST","GetCoverage"),
      ("COVERAGEID",coverage_name(workspace)),("FORMAT","image/tiff"),
      ("SUBSET",f"X({xmin:.2f},{xmax:.2f})"),
      ("SUBSET",f"Y({ymin:.2f},{ymax:.2f})"),
      ("SUBSET",f'time("{SOURCE_YEAR}-01-01T00:00:00.000Z")')]
    return base+"?"+urllib.parse.urlencode(parms)

def bounded_get(url):
    u=urllib.parse.urlsplit(url)
    if u.scheme!="https" or u.hostname!=HOST:
        raise ValueError("nonofficial host")
    req=urllib.request.Request(url,headers={
        "User-Agent":"frogcs-C1V2-WCS-bounded-technical-canary/0.1"})
    with urllib.request.urlopen(req,timeout=75) as r:
        raw=r.read(LIMIT+1)
        status=r.status
        mime=r.headers.get("Content-Type","")
        final=urllib.parse.urlsplit(r.geturl())
    if final.hostname!=HOST or len(raw)>LIMIT:
        raise ValueError("unexpected redirect or unbounded response")
    return raw,mime,status

def inspect_numeric_raster(raw,mime):
    if not (raw.startswith(b"II\x2a\x00") or raw.startswith(b"MM\x00\x2a") or
            raw.startswith(b"II\x2b\x00") or raw.startswith(b"MM\x00\x2b")):
        if raw.lstrip().startswith(b"<"):
            try:
                root=ET.fromstring(raw)
                err="; ".join(x.text.strip() for x in root.iter()
                    if x.tag.rsplit("}",1)[-1] in ("ServiceException","ExceptionText")
                    and x.text and x.text.strip())
                if err:
                    raise ValueError("WCS service exception: "+err[:400])
            except ET.ParseError:
                pass
        raise ValueError("WCS returned non-TIFF payload; no image label extraction")
    if not any(x in mime.lower() for x in ("tiff","octet-stream")):
        raise ValueError("WCS MIME not GeoTIFF")
    with MemoryFile(raw) as mem:
        with mem.open() as tif:
            if tif.count!=1 or tif.width!=WIDTH or tif.height!=HEIGHT:
                raise ValueError("unexpected WCS raster dimensions")
            if tif.crs is None or not tif.crs.is_projected:
                raise ValueError("WCS raster missing projected CRS")
            a=tif.read(1)
            nodata=tif.nodata
            valid=a[np.isfinite(a)&(a!=nodata)] if nodata is not None else a[np.isfinite(a)]
            if len(valid)==0:
                raise ValueError("empty WCS numeric raster")
            vals,counts=np.unique(valid,return_counts=True)
            return {
               "sampled_AOI":"NON_NAAMP_Iowa_centre",
               "bbox_5070":list(bbox5070()),
               "crs":tif.crs.to_string(),
               "shape":[tif.height,tif.width],"dtype":str(a.dtype),
               "res":[float(x) for x in tif.res],
               "transform":[float(x) for x in tuple(tif.transform)[:6]],
               "nodata":float(nodata) if nodata is not None else None,
               "valid_pixels":int(len(valid)),
               "unique_values":{str(int(k)):int(v) for k,v in zip(vals,counts)}
            }

def run():
    outputs={}
    for kind,workspace in WORKSPACES.items():
        row={"source_product":kind,"collection_identity":"NOT_ESTABLISHED_C1V2",
             "requested_year":SOURCE_YEAR,"technical_categorical_WCS":"NOT_OBTAINED",
             "canary_non_NAAMP":True}
        url=url_for_workspace(workspace)
        try:
            raw,mime,status=bounded_get(url)
            row.update({"http_status":status,"mime":mime,
                        "bytes":len(raw),"payload_sha256":hashlib.sha256(raw).hexdigest()})
            row["numeric_raster"]=inspect_numeric_raster(raw,mime)
            row["technical_categorical_WCS"]="NUMERIC_GEOTIFF_OBTAINED_VERSION_UNRESOLVED"
            values={int(k) for k in row["numeric_raster"]["unique_values"]}
            row["values_plausible"]=(bool(values)&
                (values.issubset(CODES) if kind=="landcover"
                 else all(1<=x<=100 for x in values)))
        except Exception as e:
            row.update({"error_type":type(e).__name__,"error":str(e)[:270]})
        outputs[kind]=row
        print(json.dumps({k:v for k,v in row.items() if k!="numeric_raster"},
                         indent=2,sort_keys=True),flush=True)
    complete=all(r["technical_categorical_WCS"]=="NUMERIC_GEOTIFF_OBTAINED_VERSION_UNRESOLVED"
                  and r.get("values_plausible") for r in outputs.values())
    if complete:
        cover,conf=(outputs[v]["numeric_raster"] for v in ("landcover","confidence"))
        same=(cover["crs"]==conf["crs"] and cover["shape"]==conf["shape"] and
              cover["transform"]==conf["transform"])
    else:
        same=False
    return {"analysis":"official_mrlc_wcs_2012_original_tiff_technical_canary_v0_1",
            "wcs_numeric_raster_pair_retrievable":bool(complete and same),
            "same_pixel_grid":bool(same),
            "C1V2_source_identity_confirmed":False,
            "permission_to_use_as_C1V2_exposure":False,
            "no_frog_outcomes_read":True,
            "no_C1V2_ecological_effect_computed":True,
            "records":outputs}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
        default=Path("research/output/MRLC_WCS_NUMERIC_CANARY_V0_1.json"))
    args=p.parse_args()
    obj=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({k:obj[k] for k in
        ("analysis","wcs_numeric_raster_pair_retrievable",
         "same_pixel_grid","C1V2_source_identity_confirmed")},indent=2))
if __name__=="__main__":main()
