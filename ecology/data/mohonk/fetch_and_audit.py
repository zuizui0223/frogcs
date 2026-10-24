#!/usr/bin/env python3
"""Acquire the public original Mohonk Preserve Darwin Core Archive (no NAAMP data).

Mohonk Preserve original GBIF-US IPT, DOI 10.15468/dypfbs.
Reads raw publisher archive, never invents zeros or turns phenological
overlap into predation evidence.
"""
from __future__ import annotations
import csv,hashlib,io,json,os,urllib.request,zipfile
from collections import Counter
from pathlib import Path

URL="https://ipt.gbif.us/archive.do?r=mohonk-amphibian-spring-sampling&v=1.1"
OUT=Path("data/mohonk_source")
MAX=15_000_000

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(URL,headers={"User-Agent":"frogcs-ecology-source-qc/0.1","Accept":"application/zip,*/*"})
    with urllib.request.urlopen(req,timeout=32) as resp:
        if resp.status!=200:raise RuntimeError(f"HTTP {resp.status} original archive")
        b=resp.read(MAX+1)
        content_type=resp.headers.get("Content-Type")
    if not (15_000<len(b)<MAX):raise RuntimeError("missing / too-large original archive")
    if not zipfile.is_zipfile(io.BytesIO(b)):raise RuntimeError("publisher endpoint did not return original zip")
    (OUT/"mohonk_original_dwca.zip").write_bytes(b)
    inventory=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        bad=z.testzip()
        if bad:raise RuntimeError(f"invalid original ZIP member: {bad}")
        names=z.namelist()
        if "meta.xml" not in names:raise RuntimeError("archive not Darwin Core")
        for info in z.infolist():
            inventory.append({"filename":info.filename,"size":info.file_size,
                              "compressed":info.compress_size})
        tabular={}
        for name in names:
            if not name.lower().endswith((".txt",".csv",".tsv")):continue
            raw=z.read(name)
            try:
                text=raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text=raw.decode("latin-1")
            # DwC standard tab delim; avoid forced analysis before parsing meta.xml schema.
            first=text.splitlines()[:3]
            tabular[name]={"text_lines":len(text.splitlines()),
                            "first_lines":[line[:1100] for line in first],
                            "raw_size_bytes":len(raw)}
    report={"source":"Mohonk Preserve GBIF-US IPT DwC-A original v1.1",
            "dataset_uuid":"a391a15f-033b-42fa-8bdc-b74014b05e28",
            "dataset_doi":"10.15468/dypfbs","source_url":URL,
            "bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),
            "content_type":content_type,"members":inventory,"tables":tabular,
            "actual_predation_events_observed":False,
            "outcome_interpretation":"Records can document timing/overlap, not predation or competitive displacement",
            "frogcs_naamp_counts_read":False}
    (OUT/"mohonk_source_qc.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
