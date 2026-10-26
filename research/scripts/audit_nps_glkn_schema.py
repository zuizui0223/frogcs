#!/usr/bin/env python3
"""NPS Great Lakes 2016–2023 amphibian acoustic public-data access/schema audit.

This does NOT refit frogcs RC6 nor claim NPS replication. Downloads from the
official NPS DataStore source identified by data.gov resource metadata;
source file is not committed to the repository. Standardized field/temporal
QA is required before any historical site-targeting endpoint is opened.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
import io

URL = "https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505"
MAX_BYTES = 125_000_000


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="research/results/nps_glkn_schema")
    args = p.parse_args()
    request = Request(URL, headers={"User-Agent": "OpenEcologyResearch/1.0 (public-domain-data-audit)"})
    with urlopen(request, timeout=120) as r:
        h = hashlib.sha256()
        nbytes = 0
        parts = []
        while True:
            chunk = r.read(512 * 1024)
            if not chunk: break
            nbytes += len(chunk)
            if nbytes > MAX_BYTES:
                raise RuntimeError("NPS CSV larger than audited maximum")
            h.update(chunk)
            parts.append(chunk)
        raw = b"".join(parts)
        code = getattr(r,"status",200)
    if not raw.strip() or raw.lstrip()[:1] == b"<":
        raise RuntimeError("Got empty file or HTML instead of official CSV")
    # Try one canonical public CSV dialect; sniff rather than assuming comma.
    content = raw.decode("utf-8-sig",errors="replace")
    delim = csv.Sniffer().sniff(content[:8192], delimiters=",;\t").delimiter
    cr = csv.reader(io.StringIO(content), delimiter=delim)
    names = next(cr)
    if len(names) < 5: raise RuntimeError("Unexpected narrow CSV header")
    n=0
    sample=[]
    empty=collections.Counter()
    distinct={i:set() for i in range(len(names))}
    max_unique=150
    for row in cr:
        if not row: continue
        n+=1
        if n<=2: sample.append([str(x)[:75] for x in row[:30]])
        for i,x in enumerate(row[:len(names)]):
            if x.strip():
                if len(distinct[i])<max_unique:distinct[i].add(x.strip())
            else: empty[i]+=1
    report={
        "source":"NPS GLKN long-term frog recordings public-domain, 2016-2023",
        "download_url":URL,"http_status":code,"bytes":nbytes,"sha256":h.hexdigest(),
        "rows":n,"columns":names,
        "observed_nonempty_distinct_up_to150":{
            nm:len(distinct[i]) for i,nm in enumerate(names)},
        "missing_counts":{nm:int(empty[i]) for i,nm in enumerate(names) if empty[i]},
        "first_two_rows_truncated":sample,
        "stage":"blind schema and availability check, NO calling outcome analysis",
    }
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/"schema_receipt.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_NPS_SCHEMA_RECEIPT")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("END_NPS_SCHEMA_RECEIPT")


if __name__=="__main__":main()
