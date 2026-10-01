#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_header(path: Path):
    raw=path.read_bytes()
    for enc in ("utf-8-sig","utf-8","cp1252","latin-1"):
        try:
            text=raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        return {"text_readable":False,"encoding":None,"header":None,"line_count":None,"delimiter":None}

    lines=[x for x in text.splitlines() if x.strip()]
    if not lines:
        return {"text_readable":True,"encoding":enc,"header":[],"line_count":0,"delimiter":None}

    first=lines[0]
    candidates=[",","\t",";","|"]
    counts={d:first.count(d) for d in candidates}
    delim=max(counts,key=counts.get)
    if counts[delim]==0:
        header=[first.strip()]
        delim=None
    else:
        header=next(csv.reader([first],delimiter=delim))
        header=[x.strip() for x in header]

    return {
        "text_readable":True,
        "encoding":enc,
        "header":header,
        "line_count":len(text.splitlines()),
        "delimiter":delim,
    }


def zip_members(path: Path):
    rows=[]
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            data=z.read(info.filename)
            rows.append({
                "name":info.filename,
                "size":len(data),
                "sha256":hashlib.sha256(data).hexdigest(),
            })
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("files",nargs="+")
    ap.add_argument("--source",required=True,help="sender/source, e.g. WFTS staff")
    ap.add_argument("--transport",default="manual_download")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    now=datetime.now(timezone.utc).isoformat()
    receipt={
        "analysis":"wfts_raw_data_intake_v0_1",
        "status":"OUTCOME_BLIND_INTAKE_ONLY",
        "created_utc":now,
        "source":args.source,
        "transport":args.transport,
        "response_values_inspected":False,
        "files":[],
    }

    for name in args.files:
        p=Path(name)
        if not p.exists() or not p.is_file():
            raise RuntimeError(f"missing file: {p}")

        row={
            "path":str(p),
            "name":p.name,
            "size":p.stat().st_size,
            "sha256":sha256_file(p),
        }

        if zipfile.is_zipfile(p):
            row["archive"]=True
            row["members"]=zip_members(p)
            row["text"]=None
        else:
            row["archive"]=False
            row["members"]=None
            row["text"]=text_header(p)

        receipt["files"].append(row)

    Path(args.output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
