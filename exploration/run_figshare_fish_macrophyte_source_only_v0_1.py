#!/usr/bin/env python3
"""Verify figshare 16627561.v2 xlsx; parse only schema/worksheet headers, never outcomes.

The scientific question concerns 2x3 randomized macrophyte/fish treatments;
the source must contain experimental unit/occasion/animal counts before
outcome interpretation. No raw dataset is redistributed in Actions artifacts.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

URL="https://ndownloader.figshare.com/files/30796897"
ITEM_ID=16627561
FILE_ID=30796897
VERSION=2
SIZE=70127
MD5="e2d27edffb6c75b7208a609fafc79447"
SSNS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
PKNS="http://schemas.openxmlformats.org/package/2006/relationships"
RELNS="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
U="{" + SSNS + "}"

def text_of(e):
    return "".join(t.text or "" for t in e.iter()
                   if t.tag in (U+"t",))

def workbook_schema(data):
    z=zipfile.ZipFile(io.BytesIO(data))
    files=set(z.namelist())
    for p in ("xl/workbook.xml","xl/_rels/workbook.xml.rels","[Content_Types].xml"):
        if p not in files:raise RuntimeError(f"Broken workbook; missing {p}")
    # Shared strings are never used below for numeric outcome rows; inspect
    # only literal header rows 1-3, not any dependent-variable cells.
    shared=[]
    if "xl/sharedStrings.xml" in files:
        ss=ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared=[text_of(elem) for elem in ss.findall(U+"si")]
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    mapping={}
    for item in rel.findall("{"+PKNS+"}Relationship"):
        target=item.attrib.get("Target","")
        if target.startswith("/"): path=target.lstrip("/")
        elif target.startswith("xl/"):path=target
        else:path="xl/"+target
        mapping[item.attrib.get("Id")]=path
    book=ET.fromstring(z.read("xl/workbook.xml"))
    out=[]
    for sheet in book.findall(".//"+U+"sheet"):
        name=sheet.attrib.get("name")
        id=sheet.attrib.get("{"+RELNS+"}id")
        path=mapping.get(id)
        if not path or path not in files:raise RuntimeError("Missing actual worksheet XML "+str(name))
        elem=ET.fromstring(z.read(path))
        dim=elem.find(U+"dimension")
        ref=dim.attrib.get("ref") if dim is not None else None
        header=[]
        for row in elem.findall(".//"+U+"sheetData/"+U+"row"):
            n=int(row.attrib.get("r","0"))
            if n>3: break
            items=[]
            for cell in row.findall(U+"c"):
                pos=cell.attrib.get("r")
                typ=cell.attrib.get("t")
                value=cell.find(U+"v")
                if typ=="s" and value is not None:
                    x=shared[int(value.text)]
                elif typ=="inlineStr":
                    x=text_of(cell)
                elif typ in ("str","e") and value is not None:
                    x=value.text
                else:
                    # Numeric data are not included even on a header row.
                    continue
                if x is not None and str(x).strip():
                    items.append({"col":re.match("[A-Z]+",pos).group(),
                                  "field":str(x).strip()[:80]})
            header.append({"row":n,"field_labels_only":items})
        out.append({"sheet":name,"dimension":ref,
                    "headers_first_three_rows_text_only":header,
                    "xml_bytes":len(z.read(path)),
                    "no_numeric_response_values_read":True})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=Path("build/figshare_fish_plant_source"))
    a=p.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    result={"analysis":"figshare_16627561_v2_2x3_fish_macrophyte_schema_source_only_v0_1",
            "source":{"item_id":ITEM_ID,"version":VERSION,"file_id":FILE_ID,
                      "official_url":URL,"size_expected":SIZE,"MD5_expected":MD5},
            "status":"not_checked","frog_outcomes_read":False,
            "all_numeric_choice_outcomes_read":False,"RC6_modified":False}
    try:
        request=urllib.request.Request(URL,headers={
           "User-Agent":"frogcs-fish-macrophyte-randomized-source-QA/0.1",
           "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"})
        with urllib.request.urlopen(request,timeout=65) as r:
            blob=r.read(5_000_000)
            result["source"].update({"download_status":r.status,
                "content_type":r.headers.get("Content-Type"),
                "final_url":r.geturl()})
        checksum=hashlib.md5(blob).hexdigest()
        sha=hashlib.sha256(blob).hexdigest()
        if len(blob)!=SIZE or checksum!=MD5:
            raise RuntimeError(f"Source version/checksum mismatch: bytes {len(blob)} md5 {checksum}")
        result["source"].update({"actual_bytes":len(blob),
                                "actual_MD5":checksum,"actual_SHA256":sha,
                                "source_checksum_VERIFIED":True})
        result["sheets"]=workbook_schema(blob)
        result["status"]="official_figshare_source_schema_verified"
    except Exception as ex:
        result["status"]="source_unavailable_or_structure_invalid"
        result["error"]={"type":type(ex).__name__,"message":str(ex)[:550]}
    (a.outdir/"source_only_schema.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("FIGSHARE_FISH_PLANT_SCHEMA_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("FIGSHARE_FISH_PLANT_SCHEMA_END",flush=True)
    if result["status"]!="official_figshare_source_schema_verified":
        raise SystemExit("Pinned experiment source not verified; stop before all experimental responses")
if __name__=="__main__":main()
