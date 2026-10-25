#!/usr/bin/env python3
"""Download original Carter 2018 eight-pond daily frog calling XLSX from Dryad.

Source DOI 10.5061/dryad.84fq2vh, version 26703 (not Carroll 2023 funnel traps).
MD5 is published original digest; compute additional SHA256.
Does not equate male calls with oviposition or breeding success.
"""
from __future__ import annotations
import argparse,hashlib,io,json,urllib.error,urllib.request,zipfile
from pathlib import Path

URLS=("https://datadryad.org/api/v2/versions/26703/download",
      "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.84fq2vh/download")
EXPECTED_MD5="37dd4dc8289f0c1ce8d249791b3df558"
EXPECTED_SIZE=14777689
MAX_BYTES=35_000_000

def matching_original(raw):
    if len(raw)==EXPECTED_SIZE and hashlib.md5(raw).hexdigest()==EXPECTED_MD5:
        return raw
    if not zipfile.is_zipfile(io.BytesIO(raw)):return None
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files=[v for v in z.namelist() if v.rsplit("/",1)[-1]=="dailycalls_dryad.xlsx"]
        if len(files)!=1:return None
        actual=z.read(files[0])
        if len(actual)!=EXPECTED_SIZE or hashlib.md5(actual).hexdigest()!=EXPECTED_MD5:
            return None
        return actual

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir",type=Path,required=True)
    args=parser.parse_args()
    out=args.outdir;out.mkdir(parents=True,exist_ok=True)
    report={"study":"Carter et al 2018 adult male acoustic calls original daily observations",
       "source_doi":"10.5061/dryad.84fq2vh","source_version":26703,
       "original_file":"dailycalls_dryad.xlsx","expected_md5":EXPECTED_MD5,
       "expected_bytes":EXPECTED_SIZE,"verified":False,"attempts":[],
       "not_direct_oviposition_or_breeding_success":True}
    for url in URLS:
        attempt={"official_url":url}
        try:
            q=urllib.request.Request(url,headers={"User-Agent":"frogcs-stage-macro-original-acoustic-source/0.1",
                        "Accept":"application/zip,application/octet-stream,*/*"})
            with urllib.request.urlopen(q,timeout=65) as response:
                b=response.read(MAX_BYTES+1)
                attempt.update(http_status=int(response.status),bytes_downloaded=len(b),
                    content_type=response.headers.get("Content-Type"))
            if len(b)>MAX_BYTES:raise RuntimeError("original source transfer exceeds 35MB bound")
            v=matching_original(b)
            if v is None:
                attempt["failure"]="incorrect or inaccessible original workbook contents"
                attempt["downloaded_sha256"]=hashlib.sha256(b).hexdigest()
            else:
                (out/"dailycalls_dryad.xlsx").write_bytes(v)
                attempt["status"]="source_digest_matched"
                report.update(verified=True,source_download_url=url,
                     source_sha256=hashlib.sha256(v).hexdigest(),
                     original_md5=hashlib.md5(v).hexdigest(),
                     original_xlsx_zip_members=len(zipfile.ZipFile(io.BytesIO(v)).namelist()))
            report["attempts"].append(attempt)
            if v is not None:break
        except urllib.error.HTTPError as e:
            attempt.update(http_status=e.code,failure="official_source_http_error_no_bypass")
            report["attempts"].append(attempt)
        except Exception as e:
            attempt.update(failure=type(e).__name__+": "+str(e)[:150])
            report["attempts"].append(attempt)
    report["outcome"]="source_verified" if report["verified"] else "source_unavailable_not_estimated"
    (out/"original_carter_daily_call_source_receipt.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":main()
