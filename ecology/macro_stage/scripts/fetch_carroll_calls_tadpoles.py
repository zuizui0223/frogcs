#!/usr/bin/env python3
"""Retrieve ORIGINAL Carroll/Saenz/Rudolf amphibian calls + tadpoles workbook.

Carroll et al. (2023), Dryad DOI 10.25338/B8G92P, original version 218704,
XLSX "funneltrapdata.xlsx", SHA256 302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f.
Source-only retrieval; no pseudo-zero call records or interpretation of columns.
"""
from __future__ import annotations
import argparse,hashlib,io,json,urllib.error,urllib.request,zipfile
from pathlib import Path

VERSION_URL="https://datadryad.org/api/v2/versions/218704/download"
EXPECTED_SHA="302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f"
EXPECTED_SIZE=196918

def get_original(outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(VERSION_URL,headers={
        "Accept":"application/zip,application/octet-stream,*/*",
        "User-Agent":"frogcs-independent-amphibian-phenology-original/0.1"})
    with urllib.request.urlopen(req,timeout=35) as resp:
        z=resp.read(5_000_001)
        if len(z)>5_000_000:raise RuntimeError("source archive >5MB")
        status=resp.status
    if not zipfile.is_zipfile(io.BytesIO(z)):
        raise RuntimeError("original Dryad endpoint did not return ZIP")
    with zipfile.ZipFile(io.BytesIO(z)) as arch:
        xs=[n for n in arch.namelist() if n.endswith("funneltrapdata.xlsx")]
        if len(xs)!=1:raise RuntimeError("original workbook missing or duplicated")
        data=arch.read(xs[0])
    digest=hashlib.sha256(data).hexdigest()
    if digest!=EXPECTED_SHA or len(data)!=EXPECTED_SIZE:
        raise RuntimeError("unrecognised workbook bytes: "+digest)
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise RuntimeError("XLSX OOXML container corrupt")
    out.joinpath("funneltrapdata.xlsx").write_bytes(data)
    receipt={"source":"Carroll et al. 2023 Dryad 10.25338/B8G92P version 218704",
       "original_filename":"funneltrapdata.xlsx","source_url":VERSION_URL,
       "original_workbook_sha256":digest,"original_workbook_bytes":len(data),
       "http_status":status,"source_verified":True,
       "data_paper_units":"8 Southeast Texas ponds × 6 years; daily acoustic calls, weekly aquatic larval trap samples",
       "column_types_and_sampling_effort_not_yet_validated":True,
       "frog_calls_mean_mating_behaviour_not_oviposition_success":True,
       "no_naamp_or_mohonk_data_read":True}
    out.joinpath("original_source_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    args=p.parse_args();get_original(args.out)
