#!/usr/bin/env python3
"""Response-blind original-source access audit for USGS Atchafalaya amphibian data.

Do NOT inspect species responses in this phase. Do NOT infer ecological null
results from inaccessible data. Public DOI 10.5066/P9T71JCO, CC0.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,time,urllib.request,urllib.error,zipfile
from pathlib import Path
from urllib.parse import urlparse

ITEM="5eb5880c82ce25b5135ae784"
DOI="10.5066/P9T71JCO"
URLS=(
    f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json",
    f"https://www.sciencebase.gov/catalog/item/{ITEM}",
    f"https://api.sciencebase.gov/catalog/item/{ITEM}?format=json",
)
USGSXML=f"https://data.usgs.gov/datacatalog/metadata/USGS.{ITEM}.xml"
MAX_METADATA=5_000_000
MAX_FILE=50_000_000
SUFFIXES=(".csv",".tsv",".txt",".xlsx",".xls",".zip")
HEADERS={"User-Agent":"frogcs-open-original-source-schema-check/1.0 (academic research; USGS DOI P9T71JCO)",
         "Accept":"application/json, application/xml, text/plain, */*"}

def http_get(url,max_bytes,timeout=24):
    req=urllib.request.Request(url,headers=HEADERS)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as f:
            status=getattr(f,"status",200)
            typ=f.headers.get("Content-Type","")
            raw=f.read(max_bytes+1)
            return dict(ok=len(raw)<=max_bytes,status=status,content_type=typ,
                        bytes=len(raw),raw=raw[:max_bytes],
                        etag=f.headers.get("ETag"),
                        original_url=f.url)
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
            ConnectionError,OSError) as e:
        return dict(ok=False,status=getattr(e,"code",None),error=str(e)[:400],
                    original_url=url)

def parse_sbjson(raw):
    try:
        j=json.loads(raw.decode("utf-8-sig"))
        if not isinstance(j,dict) or (j.get("id")!=ITEM and ITEM not in str(j.get("link",""))):
            return None
        return j
    except (UnicodeDecodeError,json.JSONDecodeError):
        return None

def original_file_manifest(j):
    files=[]
    for v in j.get("files",[]):
        name=v.get("name") or ""
        if not name:continue
        files.append(dict(name=name,content_type=v.get("contentType"),
            size=v.get("size"),md5=v.get("md5"),url=v.get("downloadUri") or v.get("url"),
            original_processing_note=v.get("description"),
            qualifying_file=Path(name).suffix.lower() in SUFFIXES))
    return files

def member_headers(name,raw):
    out=[]
    ext=Path(name).suffix.lower()
    if ext==".zip" and zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for item in z.infolist():
                if item.is_dir():continue
                e=Path(item.filename).suffix.lower()
                entry=dict(original_path=item.filename,uncompressed_bytes=item.file_size)
                if e in (".csv",".tsv",".txt"):
                    with z.open(item) as fh:
                        line=fh.readline(8192)
                    try:
                        sep="\t" if e==".tsv" else ","
                        entry["header"]=next(csv.reader([line.decode("utf-8-sig")],delimiter=sep))
                    except Exception:
                        entry["header_status"]="UNREADABLE"
                out.append(entry)
    elif ext in (".csv",".tsv",".txt"):
        first=raw.splitlines()[0] if raw else b""
        try:
            sep="\t" if ext==".tsv" else ","
            out.append(dict(original_path=name,
                header=next(csv.reader([first.decode("utf-8-sig")],delimiter=sep)),
                line_count_raw_newlines=raw.count(b"\n")))
        except Exception:
            out.append(dict(original_path=name,header_status="UNREADABLE"))
    elif ext in (".xlsx",".xls"):
        out.append(dict(original_path=name,
                        header_status="SPREADSHEET_SHEET_SCHEMA_NOT_INSPECTED"))
    return out

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    attempts=[];j=None;metadata_url=None
    for url in URLS:
        res=http_get(url,MAX_METADATA)
        raw=res.pop("raw",b"")
        candidate=parse_sbjson(raw) if res["ok"] else None
        attempts.append({**res,"parsed_usable_item":candidate is not None})
        if candidate is not None:
            j=candidate;metadata_url=url;break
    if j is None:
        xml=http_get(USGSXML,MAX_METADATA)
        xmlbytes=xml.pop("raw",b"")
        attempts.append({**xml,"parsed_usable_item":False,
                         "xml_metadata_available":bool(xml["ok"] and
                           b"<" in xmlbytes[:100])})
    files=original_file_manifest(j) if j is not None else []
    downloads=[]
    headers=[]
    if j is not None:
        for i,info in enumerate(files):
            entry={k:info[k] for k in
                    ("name","size","md5","content_type","qualifying_file")}
            entry["original_index"]=i
            if not info["qualifying_file"]:
                entry["status"]="NON_DATA_FILE"
            elif info["url"] is None:
                entry["status"]="NO_ORIGINAL_DOWNLOAD_LINK"
            elif info["size"] is not None and int(info["size"])>MAX_FILE:
                entry["status"]="ABOVE_ORIGINAL_DATA_BYTE_CAP"
            else:
                r=http_get(info["url"],MAX_FILE,timeout=75)
                raw=r.pop("raw",b"")
                if r["ok"] and raw[:80].lstrip().lower().startswith((
                    b"<!doctype html",b"<html",b"<?xml")):
                    r["ok"]=False;r["error"]="HTML_OR_XML_NOT_SOURCE_FILE"
                if r["ok"] and len(raw)>0:
                    entry["sha256"]=hashlib.sha256(raw).hexdigest()
                    entry["md5_calculated"]=hashlib.md5(raw).hexdigest()
                    if info["md5"]:
                        entry["original_md5_matches"]=(
                            entry["md5_calculated"].lower()==str(info["md5"]).lower())
                    filename=f"USGS_original_{i:02d}_"+Path(info["name"]).name
                    # Source bytes kept in transient Actions artifact ONLY;
                    # publish no original potentially sensitive coordinates by default.
                    folder=out/"original_ephemeral";folder.mkdir(exist_ok=True)
                    (folder/filename).write_bytes(raw)
                    entry["ephemeral_original_path"]=str(folder/filename)
                    entry["status"]="DOWNLOADED_ORIGINAL"
                    for h in member_headers(info["name"],raw):
                        headers.append({"source_file":info["name"],**h})
                else:
                    entry["status"]="ORIGINAL_DOWNLOAD_FAILED"
                    entry["error"]=r.get("error") or "Invalid source response"
                    entry["http_status"]=r.get("status")
            downloads.append(entry)
    is_schema=any("header" in h for h in headers)
    status=("SCHEMA_READY" if is_schema else
            "METADATA_READY" if j is not None else
            "ACCESS_BLOCKED_OR_SCHEMA_UNKNOWN")
    # A source-access/absence of metadata is NOT a negative ecology result.
    receipt=dict(
        status=status,source="USGS ScienceBase original item metadata and source files",
        source_doi=DOI,source_item_id=ITEM,
        source_title=j.get("title") if j else None,
        original_dates="2008-02-19 through 2016-07-13",
        source_license="CC0 (as described by USGS data release landing page)",
        source_original_release_url="https://doi.org/"+DOI,
        item_metadata_success=j is not None,
        item_metadata_url=metadata_url,
        item_original_files_listed=len(files),
        original_data_files_downloaded=sum(x.get("status")=="DOWNLOADED_ORIGINAL" for x in downloads),
        original_data_tables_with_csv_headers=len(headers),
        metadata_attempts=attempts,
        source_file_manifest=downloads,
        source_schema_without_response_values=headers,
        adult_call_to_larva_stage_link_eligible=None,
        matched_taxon_site_sample_date_opportunities_verified=False,
        taxon_species_stage_response_values_inspected=False,
        no_field_ABCs_or_new_biology=True,
        no_natural_trophic_mechanism_identified=True,
        not_field_mechanism_nonreplication=not is_schema,
    )
    (out/"G18_USGS_SOURCE_ACCESS_PREFLIGHT.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("G18_RESPONSE_BLIND_USGS_ORIGINAL_SOURCE_ACCESS "+json.dumps({
        "status":status,"files_listed":len(files),
        "original_downloads":receipt["original_data_files_downloaded"],
        "original_file_headers":len(headers),
        "attempts":[{k:v for k,v in item.items() if
                     k in ("original_url","status","error","parsed_usable_item","bytes")}
                    for item in attempts],
        "schema":headers[:8],
    },ensure_ascii=False),flush=True)
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    run(a.out)
