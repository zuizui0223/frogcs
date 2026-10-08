#!/usr/bin/env python3
"""Download only pinned, public USGS NAAMP metadata inputs on networked CI.

No Counts.csv; never upload raw source files as an artifact.
"""
from __future__ import annotations

import argparse, hashlib, json, time, urllib.parse, urllib.request
from pathlib import Path
from build_naamp_observation_panel import SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA

ITEM="583dc314e4b0d1899f9dea8d"
METADATA=f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json"
COORD_URL=("https://www.sciencebase.gov/catalog/file/get/"+ITEM+
           "?f=__disk__77%2F22%2F7e%2F77227ec46ac1c01592cd7d158d442cd8343a7536")


def fetch(url,tries=3):
    if not url.startswith("https://"):
        raise ValueError("HTTPS source is required")
    last=None
    for i in range(tries):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"NAAMP-source-QC/0.1",
                                                       "Accept":"application/json, text/csv, */*"})
            with urllib.request.urlopen(req,timeout=45) as r:
                return r.read()
        except Exception as e:
            last=e
            if i<tries-1: time.sleep(2*(i+1))
    raise RuntimeError(f"Public archive unavailable: {type(last).__name__}: {last}")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    dest=Path(args.output_dir)
    dest.mkdir(parents=True,exist_ok=True)
    meta=json.loads(fetch(METADATA).decode("utf-8"))
    byname={str(f.get("name")):f for f in meta.get("files",[])}
    receipts={}
    for name,expected in SOURCE_PINS.items():
        if name not in byname:raise RuntimeError(f"Missing official ScienceBase source {name}")
        entry=byname[name]
        url=entry.get("downloadUri") or entry.get("url") or entry.get("uri")
        if not url or urllib.parse.urlparse(url).hostname not in ("sciencebase.gov","www.sciencebase.gov"):
            raise ValueError(f"Unexpected official-source domain for {name}")
        payload=fetch(url)
        digest=hashlib.sha256(payload).hexdigest()
        if digest!=expected:raise ValueError(f"Checksum mismatch {name}: {digest}")
        (dest/name).write_bytes(payload)
        receipts[name]={"bytes":len(payload),"sha256":digest,"pinned":True}
    payload=fetch(COORD_URL)
    digest=hashlib.sha256(payload).hexdigest()
    if digest!=COORD_SHA: raise ValueError(f"Coordinate checksum mismatch: {digest}")
    (dest/"Coordinates.csv").write_bytes(payload)
    receipts["Coordinates.csv"]={"bytes":len(payload),"sha256":digest,"pinned":True}
    (dest/"pinned_source_receipt.json").write_text(json.dumps(receipts,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"source_names":list(receipts),"checksums_verified":True,
          "frog_response_data_downloaded":False},sort_keys=True))


if __name__=="__main__": main()
