#!/usr/bin/env python3
"""Dryad-pinned independent GLCWMP frog survey data quality & eligibility audit.

Does NOT access species detection/occurrence outcome fields. The source CSV
and README are downloaded into only temporary memory, never committed or
uploaded as GitHub artifacts. Aggregate anonymized source-availability and
key-structure diagnostics only. Fail closed on source hash/version drift.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DOI="10.5061/dryad.hmgqnk9v8"
DATASET_VERSION=350431
DATASET_ID=151710
FILE={
    "CWMP_MaxOcc.csv":{
        "file_id":3932974,
        "bytes":4004194,
        "sha256":"9b6e1b11d371a6bfac2b49e0aee369a57ed4fdeaeb7378c81ea79dc92c9b2587"},
    "README.md":{
        "file_id":3932975,
        "bytes":13021,
        "sha256":"70a0753ddcfbde7fd41178045843c68333136495d4b64f63b3af6c579865c7e8"}
}
HEADER={"User-Agent":"frogcs-cross-dataset-source-audit/0.1 (+https://github.com/zuizui0223/frogcs)",
        "Accept":"*/*"}
BASE="https://datadryad.org"
ZIPPED="https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.hmgqnk9v8/download"
ATTRS=("site_id","point_id","year","lat","long")
SPECIES_CANDIDATES=("species","spp","taxon","taxa","sp","species_name","species_group","scientificname","sci_name")
RESPONSE_RE=re.compile("occ|detect|presence|absen|call|response|observed|max",re.I)
EARLY_NO_OUTCOME=True

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def retrieve(url,ntries=2):
    errors=[]
    for i in range(ntries):
        try:
            req=urllib.request.Request(url,headers=HEADER)
            with urllib.request.urlopen(req,timeout=65) as rsp:
                length=rsp.headers.get("content-length")
                data=rsp.read(12_000_000)
                if len(data)>=12_000_000:
                    raise RuntimeError("Exceeded read cap while retrieving source")
                return data,{"url":url,"http":int(rsp.status),
                             "content_length":length,"sha256":digest(data),
                             "n_bytes":len(data)}
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as ex:
            if isinstance(ex,urllib.error.HTTPError):
                message=f"HTTP {ex.code} {ex.reason}"
            else: message=type(ex).__name__+" "+str(ex)[:180]
            errors.append(message)
            if i<ntries-1:time.sleep(2)
    raise RuntimeError("; ".join(errors))

def check_blob(blob,name):
    entry=FILE[name]
    d=digest(blob)
    if len(blob)!=entry["bytes"] or d!=entry["sha256"]:
        raise RuntimeError(f"Dryad official {name} content drift: bytes={len(blob)} SHA={d}")
    return {"filename":name,"n_bytes":len(blob),"sha256":d,
            "dryad_file_id":entry["file_id"],"verification":"PASS"}

def official_download():
    failures=[]
    found={}
    receipts=[]
    # 1. Dryad API routes, locked by file ID / dataset DOI.
    for name,v in FILE.items():
        url=f"{BASE}/api/v2/files/{v['file_id']}/download"
        try:
            blob,rc=retrieve(url,ntries=1)
            check_blob(blob,name)
            found[name]=blob
            receipts.append({"file":name,"route":"official_Dryad_API_file",**rc})
        except Exception as ex:
            failures.append({"route":"official_Dryad_API_file","file":name,
                             "error":str(ex)})
    if len(found)!=len(FILE):
        try:
            blob,rc=retrieve(ZIPPED,ntries=1)
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                for name in FILE:
                    options=[f for f in z.namelist() if
                             Path(f).name==name and ".." not in Path(f).parts
                             and not f.startswith("/")]
                    if len(options)!=1:
                        raise RuntimeError(f"Official ZIP missing unique pinned {name}")
                    d=z.read(options[0])
                    check_blob(d,name)
                    found[name]=d
            receipts.append({"route":"official_Dryad_API_zip",**rc})
        except Exception as ex:
            failures.append({"route":"official_Dryad_API_zip",
                             "error":str(ex)})
    # 2. ONE documented official public UI alternative. The source version,
    # exact file IDs and SHA256 digests are identical. This is not an attempt
    # to bypass rate limits, anti-bot validation, or API authentication.
    if len(found)!=len(FILE):
        for name,v in FILE.items():
            if name in found:continue
            url=f"{BASE}/downloads/file_stream/{v['file_id']}"
            try:
                blob,rc=retrieve(url,ntries=1)
                check_blob(blob,name)
                found[name]=blob
                receipts.append({"route":"official_Dryad_public_UI",
                                 "file":name,**rc})
            except Exception as ex:
                failures.append({"route":"official_Dryad_public_UI",
                                 "file":name,"error":str(ex)})
    if len(found)!=len(FILE):
        raise RuntimeError("All permitted official Dryad API/UI byte channels blocked "
                           "or mismatched pinned source: "+json.dumps(failures))
    verifications=[check_blob(found[name],name) for name in FILE]
    return found,{"retrieval":receipts,"direct_errors":failures,
                  "pinned_verification":verifications}

def normalize_field(name):
    return re.sub(r"[^a-z0-9]","",str(name or "").strip().lower())

def choose_column(cols,possible):
    d={normalize_field(c):c for c in cols}
    found=[d.get(normalize_field(v)) for v in possible if normalize_field(v) in d]
    return found[0] if found else None

def description_of_schema(blob):
    # Validate CSV header grammar and intended response exclusion BEFORE
    # opening any body rows, then usecols restrict body to key metadata only.
    head=blob[:8000].decode("utf-8-sig",errors="strict").splitlines()[0]
    names=next(csv.reader([head]))
    if not names or len(set(names))!=len(names):
        raise RuntimeError("CSV has empty or duplicate column names")
    targets={q:choose_column(names,[q]) for q in ATTRS}
    taxa=choose_column(names,SPECIES_CANDIDATES)
    targets["taxon"]=taxa
    if any(z is None for k,z in targets.items() if k in ("site_id","point_id","year")):
        raise RuntimeError(f"Required original wetland-site×point×year columns missing: {targets}")
    if taxa is None:
        # Fail closed on identifying taxonomic grain rather than assuming
        # that a species indicator is one of eight from a wide layout.
        return names,targets,{"type":"unresolved_taxon_field","needs_schema_alignment":True}
    if any(RESPONSE_RE.search(q) for q in [targets["site_id"],targets["point_id"],targets["year"],taxa]):
        raise RuntimeError("Source key unexpectedly looks like detection outcome")
    return names,targets,{"type":"long_taxon_rows","needs_schema_alignment":False}

def structural_audit(csv_blob,readme_blob):
    cols,found,layout=description_of_schema(csv_blob)
    # The response column is never read, even for NA rows. This is solely
    # spatial/survey sampling structure and taxonomic eligibility.
    if layout["needs_schema_alignment"]:
        return {"layout":layout,"columns":cols,
                "field_map":found,"response_data_read":False}
    use={v for v in found.values() if v is not None}
    meta=pd.read_csv(io.BytesIO(csv_blob),usecols=list(use),low_memory=False,
                     dtype={found["site_id"]:"string",
                            found["point_id"]:"string",
                            found["taxon"]:"string"})
    # Coordinate columns are not used in joins and are not revealed at row level.
    ren={v:k for k,v in found.items() if v is not None}
    t=meta.rename(columns=ren)
    before=len(t)
    valid=t.dropna(subset=["site_id","point_id","year","taxon"]).copy()
    for c in ("site_id","point_id","taxon"):
        valid[c]=valid[c].str.strip()
    valid["year"]=pd.to_numeric(valid.year,errors="coerce")
    valid=valid[valid.site_id.ne("")&valid.point_id.ne("")&valid.taxon.ne("")&
                valid.year.between(2011,2023)].copy()
    valid["year"]=valid.year.astype(int)
    # SiteID may only be unique within a lake: use the dataset's original
    # wetland ID and audit whether geographic lakes require an extended key.
    key=["site_id","point_id","year","taxon"]
    collisions=valid.duplicated(key,keep=False)
    exact=valid.duplicated(key).sum()
    pointkey=["site_id","point_id","year"]
    points=valid.groupby(pointkey,dropna=False).taxon.nunique().reset_index(name="n_taxa_rows")
    pkeys=points.groupby(["site_id","year"]).point_id.nunique().reset_index(name="n_points")
    ids=sorted(valid.taxon.dropna().unique().astype(str).tolist())
    combos=pkeys.groupby("site_id").n_points.max()
    n_taxa=int(valid.taxon.nunique())
    complete=(points.n_taxa_rows==n_taxa).sum()
    # More precise opportunity count: point-year key may be repeated or
    # duplicated, and the max species count need not imply no missing species.
    n_full=(valid.groupby(pointkey).taxon.nunique()==n_taxa).sum()
    doc=readme_blob.decode("utf-8-sig",errors="replace")
    # Report just source keys and field design, no raw response measurements.
    out={
        "layout":layout,
        "schema":{"n_columns":len(cols),"all_column_names":cols,
                  "mapping":found,
                  "likely_response_fields":[c for c in cols if RESPONSE_RE.search(c)],
                  "readme_utf8_bytes":len(readme_blob),
                  "readme_mentions_point_id":"point_id" in doc,
                  "readme_mentions_vegetation":"vegetation" in doc.lower()},
        "grain":{
            "n_rows":before,
            "n_valid_key_rows":int(len(valid)),
            "n_invalid_key_year_rows":int(before-len(valid)),
            "n_duplicate_composite_keys_extra":int(exact),
            "n_rows_in_duplicate_composite_keys":int(collisions.sum()),
            "n_distinct_taxon_units":n_taxa,
            "taxon_names":ids,
            "n_wetlands":int(valid.site_id.nunique()),
            "n_point_year_groups":int(len(points)),
            "n_distinct_point_locations":int(valid[["site_id","point_id"]].drop_duplicates().shape[0]),
            "year_range":[int(valid.year.min()),int(valid.year.max())] if len(valid) else [],
            "n_sampled_wetland_year_groups":int(len(pkeys)),
            "n_siteyears_ge2points":int((pkeys.n_points>=2).sum()),
            "n_siteyears_ge3points":int((pkeys.n_points>=3).sum()),
            "n_wetlands_ever_ge3points":int((combos>=3).sum()),
            "n_pointyears_with_all_taxa_rows":int(n_full),
            "fraction_pointyears_all_taxa_rows":float(n_full/len(points)) if len(points) else 0.,
            "year_by_distinct_wetlands":{str(year):int(k.site_id.nunique())
                 for year,k in valid.groupby("year")},
            "year_by_pointyears":{str(year):int(k[["site_id","point_id"]].drop_duplicates().shape[0])
                 for year,k in valid.groupby("year")},
            "source_columns_examined_only":sorted(use),
            "frog_detection_outcome_values_read":False
        }}
    # A nonzero response column may encode occurrence of >=1 calling event.
    # Keep this invisible until source quality gate is reviewed and
    # preregistered outcome model is chosen.
    out["preflight_gates"]={
        "source_digest":True,
        "composite_key_unique":int(exact)==0,
        "at_least_80_wetland_year_groups_ge3_points":int((pkeys.n_points>=3).sum())>=80,
        "at_least_40_wetlands_ever_ge3_points":int((combos>=3).sum())>=40,
        "all_8_taxon_rows_per_pointyear":n_taxa==8 and len(points)>0 and n_full==len(points),
        "bullfrog_and_greenfrog_available":any("catesbeian" in z.lower() for z in ids)
                                  and any("clamitans" in z.lower() for z in ids)}
    out["feasible_conditional_testing_if_response_has_variation"] = bool(all(out["preflight_gates"].values()))
    return out

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--outdir",type=Path,default=ROOT/"build"/"glcwmp_source_qa")
    a=arg.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True)
    receipt={"analysis":"independent_GLCWMP_source_only_qa_v0_1",
             "source":"Tozer et al. 2025 / Dryad doi:10.5061/dryad.hmgqnk9v8",
             "dryad_version_id":DATASET_VERSION,
             "source_frozen_expected_SHA":{x:q["sha256"] for x,q in FILE.items()},
             "source_status":"not_yet_checked",
             "frog_detection_outcomes_read":False}
    try:
        blobs,download=official_download()
        receipt["download"]=download
        receipt["source_status"]="pinned_source_verified"
        receipt["pre_outcome_structure"]=structural_audit(
            blobs["CWMP_MaxOcc.csv"],blobs["README.md"])
        receipt["source_status"]="source_structure_checked"
    except Exception as ex:
        receipt["source_status"]="blocked_or_invalid"
        receipt["failure_class"]=type(ex).__name__
        receipt["failure_message"]=str(ex)[:1200]
        receipt["analysis_permitted"]=False
    receipt["frog_detection_outcomes_read"]=False
    receipt["frozen_RC6_modified"]=False
    (a.outdir/"source_only_result.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("GLCWMP_SOURCE_AUDIT_BEGIN",flush=True)
    print(json.dumps(receipt,sort_keys=True),flush=True)
    print("GLCWMP_SOURCE_AUDIT_END",flush=True)
    # Fail closed: missing public source or invalid observed schema is not
    # scientific evidence.
    if receipt["source_status"]!="source_structure_checked":
        raise SystemExit("Official SHA-pinned Dryad source could not be verified")
    if receipt["pre_outcome_structure"]["layout"]["needs_schema_alignment"]:
        raise SystemExit("Taxonomic grain unresolved; no biological result permitted")

if __name__=="__main__":
    main()
