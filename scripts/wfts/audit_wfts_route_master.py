#!/usr/bin/env python3
"""Audit WFTS route IDs against Wisconsin county number codes.

This is a structural QA only. It does NOT classify a route as traditional,
NAAMP/protocol, valid, or eligible. Route type must come from authoritative
WFTS/DNR metadata.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def norm(x: str) -> str:
    x=x.casefold().replace("&"," and ")
    x=re.sub(r"[^a-z0-9]+"," ",x)
    return " ".join(x.split())


def load_counties(path: Path) -> dict[int,str]:
    out={}
    with path.open(encoding="utf-8",newline="") as h:
        for row in csv.DictReader(h):
            out[int(row["county_code"])]=row["county_name"]
    if set(out)!=set(range(1,73)):
        raise SystemExit("county map must contain codes 1..72 exactly")
    return out


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--route-master",required=True,type=Path)
    p.add_argument(
        "--county-map",
        type=Path,
        default=Path("revision/WISCONSIN_COUNTY_ROUTE_PREFIX_V0_1.csv"),
    )
    p.add_argument("--route-id-column",default="route_id")
    p.add_argument("--county-column",default="county")
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()

    counties=load_counties(args.county_map)
    rows=[]
    with args.route_master.open(encoding="utf-8-sig",newline="") as h:
        reader=csv.DictReader(h)
        if args.route_id_column not in (reader.fieldnames or []):
            raise SystemExit(f"missing route column {args.route_id_column}")
        if args.county_column not in (reader.fieldnames or []):
            raise SystemExit(f"missing county column {args.county_column}")
        for idx,row in enumerate(reader, start=2):
            raw=str(row[args.route_id_column]).strip()
            county=str(row[args.county_column]).strip()
            rec={"row":idx,"route_id":raw,"county":county}
            try:
                rid=int(raw)
            except ValueError:
                rec.update(status="non_numeric_route_id",expected_county=None)
                rows.append(rec); continue
            prefix=rid//10
            suffix=rid%10
            expected=counties.get(prefix)
            if expected is None or suffix==0:
                status="special_or_noncounty_route_id"
            elif norm(expected) not in norm(county):
                status="county_mismatch"
            else:
                status="county_prefix_consistent"
            rec.update(
                route_prefix=prefix,
                route_suffix=suffix,
                expected_county=expected,
                status=status,
            )
            rows.append(rec)

    counts={}
    for row in rows:
        counts[row["status"]]=counts.get(row["status"],0)+1
    out={
        "audit":"wfts_route_id_county_prefix_v0_1",
        "route_type_inferred":False,
        "response_values_read":False,
        "rows":rows,
        "counts":counts,
        "note":(
            "County-prefix consistency is an audit signal only. Traditional/protocol "
            "classification must come from WFTS/DNR metadata."
        ),
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print({"status":"PASS","rows":len(rows),"counts":counts,"response_values_read":False})


if __name__=="__main__":
    main()
