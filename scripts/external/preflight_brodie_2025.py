#!/usr/bin/env python3
import csv, hashlib, json, pathlib

FILES = [
    pathlib.Path("external_data/HerveyRange_frog_chorus_rawdata.csv"),
    pathlib.Path("external_data/HerveyRange_weather_aggregated.csv"),
    pathlib.Path("external_data/HerveyRange_frogchorus_weather.csv"),
]
out={"status":"schema_only_preflight","files":[]}
for p in FILES:
    b=p.read_bytes()
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader=csv.reader(f)
        header=next(reader)
    out["files"].append({
        "name":p.name,
        "size_bytes":len(b),
        "sha256":hashlib.sha256(b).hexdigest(),
        "header":header,
    })
path=pathlib.Path("external/BRODIE_2025_SCHEMA_PREFLIGHT_RECEIPT.json")
path.write_text(json.dumps(out,indent=2),encoding="utf-8")
print(path.read_text())
