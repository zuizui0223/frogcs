#!/usr/bin/env python3
"""Safely test public original-raster access candidates for Annual NLCD C1V2.
Do not try to solve access challenges, authenticate, or fetch whole mosaics.
"""
import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

YEAR=2001
STEM="Annual_NLCD_LndCov_2001_CU_C1V2"
EXPECTED_ZIP_BYTES=1351509819
UA="frogcs-independent-habitat-environment-source-probe/0.2"
URLS={
    "mrlc_public_bundle":f"https://www.mrlc.gov/downloads/sciweb1/shared/mrlc/data-bundles/{STEM}.zip",
    "usgs_s3_mosaic_zip":f"https://usgs-landcover.s3.us-west-2.amazonaws.com/annual-nlcd/c1/v2/cu/mosaic/{STEM}.zip",
    "usgs_s3_mosaic_tiff":f"https://usgs-landcover.s3.us-west-2.amazonaws.com/annual-nlcd/c1/v2/cu/mosaic/{STEM}.tif",
    "usgs_s3_collection_alias":f"https://s3.us-west-2.amazonaws.com/usgs-landcover/annual-nlcd/c1/v2/cu/mosaic/{STEM}.tif",
    "sciencebase_catalog_zip":f"https://www.sciencebase.gov/catalog/file/get/697b9279b66b0197c3043cc3?name={STEM}.zip",
}
def probe(name,url):
    out={"name":name,"url":url,"requested_range":"bytes=-2048","max_bytes_read":2048}
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":"bytes=-2048"})
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            code=int(r.status);out["http_status"]=code;out["final_url"]=r.url
            out["content_range"]=r.headers.get("Content-Range")
            out["content_type"]=r.headers.get("Content-Type")
            if code==206:
                part=r.read(2048)
                out["read_bytes"]=len(part)
                out["zip_eocd_found"]=b"PK\x05\x06" in part
                out["tiff_magic_found"]=part[:4] in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+")
                if name.endswith("zip") or "bundle" in name:
                    out["matches_sciencebase_zip_size"]=bool(out["content_range"] and out["content_range"].endswith("/"+str(EXPECTED_ZIP_BYTES)))
            else:
                out["read_bytes"]=0
                out["note"]="did not read body of 200 response"
    except urllib.error.HTTPError as e:
        out["http_status"]=e.code;out["error"]="HTTPError"
    except Exception as e:
        out["error"]=type(e).__name__
    return out
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    report={"analysis":"nlcd_c1v2_public_random_access_candidates_v0_1",
       "source_collection_verified":"USGS ScienceBase 697b9279b66b0197c3043cc3",
       "source_file":f"{STEM}.zip","source_file_size":EXPECTED_ZIP_BYTES,
       "scientific_result":False,"frog_outcomes_read":False,"whole_rasters_downloaded":False,
       "probes":[probe(name,url) for name,url in URLS.items()]}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__": main()
