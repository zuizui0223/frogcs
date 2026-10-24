#!/usr/bin/env python3
"""Acquire original public Takahashi 2023 egg-mass CSV from OFFICIAL Dryad only.
Return a source-audit JSON; never interpret HTML/login errors as original data.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

EXPECTED_SHA="8bf8166185fb1607710bd3bfd9a81d9f82ea34c1d8ae8874f562d5bee70076db"
EXPECTED_BYTES=1017
URLS=(
    "https://datadryad.org/stash/downloads/file_stream/2551841",
    "https://datadryad.org/api/v2/files/2551841/download",
    "https://datadryad.org/api/v2/versions/253812/download",
    "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.bnzs7h4gn/download",
)
MAX_BYTES=5000000

def validated(original):
    if len(original)!=EXPECTED_BYTES:return False
    return hashlib.sha256(original).hexdigest()==EXPECTED_SHA

def extract_original(contents):
    if validated(contents):return contents
    if not zipfile.is_zipfile(io.BytesIO(contents)):return None
    with zipfile.ZipFile(io.BytesIO(contents)) as z:
        files=[n for n in z.namelist() if n.endswith("Hatch_w.csv")]
        if len(files)!=1:return None
        inside=z.read(files[0])
        return inside if validated(inside) else None

def acquire(outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    attempts=[]
    result={"source":"Takahashi (2023), Dryad 10.5061/dryad.bnzs7h4gn, version 4",
        "file_id":2551841,"filename":"Hatch_w.csv",
        "expected_sha256":EXPECTED_SHA,"expected_bytes":EXPECTED_BYTES,
        "raw_source_verified":False,"lab_effect_reestimated":False,
        "independent_amphibian_monitoring":False,"attempts":attempts}
    for url in URLS:
        attempt={"url":url}
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"frog-eco-Dryad-public-data-validation/0.1",
                                                     "Accept":"text/csv,application/zip,application/octet-stream,*/*"})
            with urllib.request.urlopen(req,timeout=15) as response:
                status=int(response.status)
                raw=response.read(MAX_BYTES+1)
                attempt.update(status=status,final_url=response.url,
                    content_type=response.headers.get("Content-Type"),returned_bytes=len(raw))
            if len(raw)>MAX_BYTES:raise ValueError("original exceeds 5MB safety cap")
            source=extract_original(raw)
            if source is None:
                attempt["reason"]="byte content SHA256 differs from original Dryad file"
                attempt["returned_sha256"]=hashlib.sha256(raw).hexdigest()
            else:
                out.joinpath("Hatch_w.csv").write_bytes(source)
                header=next(csv.reader(io.StringIO(source.decode("utf-8-sig"))))
                result.update(raw_source_verified=True,validated_download_url=url,
                    original_bytes=len(source),original_sha256=EXPECTED_SHA,
                    original_column_names=header)
                attempt["original_digest_matched"]=True
                attempts.append(attempt)
                break
        except urllib.error.HTTPError as error:
            attempt.update(status=error.code,reason="HTTP_ERROR_no_bypass")
        except Exception as error:
            attempt.update(status=None,reason=type(error).__name__+": "+str(error)[:170])
        attempts.append(attempt)
    if not result["raw_source_verified"]:
        result.update(outcome="official_source_download_blocked",
                      inference="No egg-mass-level inference was made. Do not replace with published cell means.")
    else:
        result["outcome"]="validated_original_experimental_csv_downloaded"
    out.joinpath("source_audit.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir",required=True,type=Path)
    a=p.parse_args()
    acquire(a.outdir)
