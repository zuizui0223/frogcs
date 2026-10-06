#!/usr/bin/env python3
from __future__ import annotations
import csv, io, json, re, urllib.request
from pathlib import Path

LAMP_ITEM_ID="600789c4d34e162231fb1cdb"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{LAMP_ITEM_ID}?format=json"
MAX_TEXT_BYTES=131072

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-lamp-preflight/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")

def range_text(url, n=MAX_TEXT_BYTES):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-lamp-preflight/0.1","Range":f"bytes=0-{n-1}"})
    with urllib.request.urlopen(req,timeout=60) as r:
        b=r.read(n)
    return b.decode("utf-8-sig",errors="replace")

def norm(s):
    return re.sub(r"[^a-z0-9]+","",str(s).lower())

def header_info(f):
    name=f.get("name") or ""
    url=file_url(f)
    out={"name":name,"size":f.get("size"),"contentType":f.get("contentType"),"url_present":bool(url)}
    low=name.lower()
    if url and low.endswith((".csv",".txt",".tsv")):
        try:
            txt=range_text(url)
            first=txt.splitlines()[0] if txt.splitlines() else ""
            delim="\t" if low.endswith(".tsv") else ","
            cols=next(csv.reader([first],delimiter=delim))
            out["header_columns"]=cols
            out["header_only"]=True
        except Exception as e:
            out["header_error"]=type(e).__name__+": "+str(e)[:200]
    return out

item=get_json(ITEM_URL)
files=[header_info(f) for f in (item.get("files") or [])]

# This checks only frozen reader-facing documents, not raw response outcomes.
repo_text=""
for p in ["paper/manuscript.md","paper/supporting_information.md",
          "submission/RC6_FINAL_PROJECT_CLOSURE_2026-10-05.md"]:
    q=Path(p)
    if q.exists():
        repo_text += "\n"+q.read_text(encoding="utf-8",errors="replace")
mentions_louisiana = bool(re.search(r"(?i)\\bLouisiana\\b", repo_text))

all_cols=[]
for f in files:
    all_cols.extend(f.get("header_columns") or [])
N={norm(x) for x in all_cols}

def has_any(parts):
    return any(any(p in c for p in parts) for c in N)

structural={
    "route":has_any(["route"]),
    "stop":has_any(["stop","station"]),
    "run":has_any(["run","surveyperiod","season"]),
    "date_or_year":has_any(["date","year"]),
    "taxon":has_any(["species","taxon","frog"]),
    "call_index":has_any(["callindex","callingindex","calling","call"]),
    "rain_or_precip":has_any(["rain","precip"]),
}
plain_header_files=sum(1 for f in files if f.get("header_columns"))
if plain_header_files and all(structural.values()):
    classification="HEADER_SCHEMA_PASS"
elif plain_header_files:
    classification="HEADER_SCHEMA_INCOMPLETE"
else:
    classification="NO_PLAIN_TABULAR_HEADER_READ"

result={
    "analysis":"lamp_public_holdout_header_preflight_v0_1",
    "item_id":LAMP_ITEM_ID,
    "title":item.get("title"),
    "file_count":len(files),
    "files":files,
    "structural_fields_detected_across_plain_headers":structural,
    "classification":classification,
    "current_rc6_reader_docs_mention_louisiana":mentions_louisiana,
    "outcome_values_read":False,
    "note":"Only ScienceBase item metadata and first header line(s) of plain-text tabular files were inspected. No species/call-index outcome values were parsed."
}
print(json.dumps(result,indent=2,ensure_ascii=False))
