#!/usr/bin/env python3
"""Fetch original Carroll-Saenz-Rudolf Oikos amphibian adult-call & tadpole data.

Source Dryad DOI 10.25338/B8G92P version 218704, original XLSX SHA256
302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f.
Only HTTPS documented original Dryad endpoints; do not bypass auth.
This script verifies original bytes, does NOT fit any ecological outcome.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

URLS=(
"https://datadryad.org/api/v2/versions/218704/download",
"https://datadryad.org/api/v2/datasets/doi%3A10.25338%2FB8G92P/download",
"https://datadryad.org/api/v2/files/2077176/download",
)
EXPECTED_SHA="302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f"
EXPECTED_SIZE=196918
MAX_BYTES=5_000_000

def extract_xlsx(raw):
    if len(raw)==EXPECTED_SIZE and hashlib.sha256(raw).hexdigest()==EXPECTED_SHA:
        return raw
    if not zipfile.is_zipfile(io.BytesIO(raw)):
        return None
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        matches=[name for name in z.namelist() if name.rsplit("/",1)[-1]=="funneltrapdata.xlsx"]
        if len(matches)!=1:return None
        candidate=z.read(matches[0])
        if len(candidate)!=EXPECTED_SIZE or hashlib.sha256(candidate).hexdigest()!=EXPECTED_SHA:
            return None
        return candidate

def run(outdir):
    p=Path(outdir);p.mkdir(parents=True,exist_ok=True)
    report={"dataset":"Carroll, Saenz & Rudolf 2023 Oikos: Tracking phenological distributions and interaction potential across life stages",
            "doi":"10.25338/B8G92P","dryad_version":218704,
            "original_filename":"funneltrapdata.xlsx","original_sha256_expected":EXPECTED_SHA,
            "original_file_size_bytes":EXPECTED_SIZE,"source_downloaded_and_sha_verified":False,
            "frog_chorus_and_larval_relationship_tested":False,
            "not_amphibian_breeding_success":True,"attempts":[]}
    for url in URLS:
        attempt={"official_url":url}
        try:
            req=urllib.request.Request(url,headers={"Accept":"application/zip,application/octet-stream,*/*",
                "User-Agent":"frogcs-independent-life-stage-research/0.1"})
            with urllib.request.urlopen(req,timeout=35) as response:
                raw=response.read(MAX_BYTES+1)
                attempt.update(http_status=int(response.status),received_bytes=len(raw),
                               content_type=response.headers.get("Content-Type"))
            if len(raw)>MAX_BYTES:raise ValueError("more than five megabytes")
            actual=extract_xlsx(raw)
            if actual is None:
                attempt["result"]="does not contain SHA-pinned original XLSX"
                attempt["response_sha256"]=hashlib.sha256(raw).hexdigest()
            else:
                target=p/"funneltrapdata.xlsx"
                target.write_bytes(actual)
                attempt["result"]="original workbook checksum matches"
                report.update(source_downloaded_and_sha_verified=True,
                    validated_source_url=url,source_content_sha256=EXPECTED_SHA)
                # Do not parse XLSX biological variables before prereadback schema audit
                with zipfile.ZipFile(target) as x:
                    report["xlsx_member_count"]=len(x.namelist())
                report["source_is_published_previous_study"]=True
                report["source_is_an_independent_pond_system_from_naamp"]=True
                report["not_an_independent_new_manipulation"]=True
            report["attempts"].append(attempt)
            if actual is not None:break
        except urllib.error.HTTPError as ex:
            attempt.update(http_status=ex.code,result="public official endpoint inaccessible")
            report["attempts"].append(attempt)
        except (urllib.error.URLError,TimeoutError,ValueError,zipfile.BadZipFile) as ex:
            attempt.update(http_status=None,result=type(ex).__name__+": "+str(ex)[:170])
            report["attempts"].append(attempt)
    if not report["source_downloaded_and_sha_verified"]:
        report["outcome"]="source_not_verified_no_phenological_calibration_allowed"
    else:report["outcome"]="original_pond_study_workbook_available_for_schema_audit"
    (p/"original_carroll_xlsx_source_receipt.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--outdir",required=True)
    p=a.parse_args()
    run(p.outdir)
