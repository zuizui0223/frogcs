#!/usr/bin/env python3
"""Metadata-only HTTP HEAD availability audit for MRLC Annual NLCD GeoTIFFs.
Candidate C1V0/C1V1/C1V2 filenames are NOT asserted to be release identities.
Does not read frog calls or download raster imagery.
"""
import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

BASE="https://s3-us-west-2.amazonaws.com/mrlc"
YEARS=(2001,2008,2015)
VERSIONS=(0,1,2)

def probe(url):
    req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"frogcs-outcome-blind-nlcd-availability/0.1"})
    try:
        with urllib.request.urlopen(req,timeout=12) as response:
            return {"status":response.status,
                    "content_length":response.headers.get("Content-Length"),
                    "accept_ranges":response.headers.get("Accept-Ranges"),
                    "etag":response.headers.get("ETag"),
                    "content_type":response.headers.get("Content-Type")}
    except urllib.error.HTTPError as ex:
        return {"status":ex.code,"error":"HTTP error"}
    except (urllib.error.URLError,TimeoutError) as ex:
        return {"status":None,"error":type(ex).__name__}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[]
    for y in YEARS:
        for v in VERSIONS:
            url=f"{BASE}/Annual_NLCD_LndCov_{y}_CU_C1V{v}.tif"
            rows.append({"year":y,"candidate_version":v,"url":url,**probe(url)})
    report={"analysis":"annual_nlcd_public_url_head_feasibility_v0_1",
            "records":rows,"outcomes_read":False,"raster_downloaded":False,
            "note":"HTTP status does not establish release lineage or raw categorical pixel values. Verify collection 1.2 independently."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":main()
