#!/usr/bin/env python3
"""Source-blind origin workbook QA for 2×2×2 frog desiccation×predator cue trial.

Source:
https://digital.csic.es/handle/10261/411885
Leptodactylus fuscus experimental tadpoles, Dry-down vs high water,
30C vs 35C, predator cue presence vs absence. 80 replicate containers
of three larvae, three original clutches; warm treatment assigned by
larger bath pools (potential nested randomization).

G0 checks package integrity, worksheet dimensions, first row STRING
column-label candidates and source hash ONLY. It deliberately never
extracts survival, metamorphosis, body size or other biological responses.
No hardcoded prediction sign, no unverified mechanism claim.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

RECORD="10261/411885"
SRC="https://digital.csic.es/bitstream/10261/411885/1/Delgadillo%20et%20al.%2c%20dataset_fuscus.xlsx"
EXPECTED_BYTES=59841
NS_M="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_P="http://schemas.openxmlformats.org/package/2006/relationships"

def get_binary():
    req=Request(SRC,headers={
        "User-Agent":"frogcs-original-data-source-audit/1.0 (biology; noncommercial)",
        "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/octet-stream, */*"
    })
    with urlopen(req,timeout=35) as res:
        payload=res.read(900000)
    if len(payload)>900000:raise ValueError("Unexpectedly large source")
    if not payload.startswith(b"PK"):raise ValueError("HTTP response not valid zip-based xlsx")
    if len(payload)!=EXPECTED_BYTES:
        raise ValueError(f"Original public-data-catalog file size drift: {len(payload)} vs {EXPECTED_BYTES}")
    return payload

def qname(name):return "{"+NS_M+"}"+name
def columns(cell_ref):
    letters=re.match(r"^([A-Za-z]+)",cell_ref or "")
    if not letters:return None
    x=0
    for c in letters[1].upper():x=x*26+(ord(c)-64)
    return x-1

def inspect(blob):
    f=zipfile.ZipFile(BytesIO(blob))
    names=set(f.namelist())
    if "xl/workbook.xml" not in names:raise ValueError("Invalid workbook structure")
    wb=ET.fromstring(f.read("xl/workbook.xml"))
    rel=ET.fromstring(f.read("xl/_rels/workbook.xml.rels"))
    targets={r.attrib["Id"]:r.attrib["Target"] for r in rel if "Id" in r.attrib}
    strings=[]
    if "xl/sharedStrings.xml" in names:
        shared=ET.fromstring(f.read("xl/sharedStrings.xml"))
        for cell in shared.findall(qname("si")):
            strings.append("".join(x.text or "" for x in cell.iter(qname("t"))))
    result=[]
    for sheet in wb.findall(".//"+qname("sheet")):
        sn=sheet.attrib["name"]
        rid=sheet.attrib.get("{"+NS_R+"}id")
        target=targets.get(rid)
        if not target:raise ValueError("Missing worksheet relationship")
        filename=target.lstrip("/")
        if not filename.startswith("xl/"):filename="xl/"+filename
        if filename not in names:raise ValueError("Missing referenced sheet: "+sn)
        tab=ET.fromstring(f.read(filename))
        rows=tab.findall(".//"+qname("sheetData")+"/"+qname("row"))
        maxrow=max([int(x.attrib.get("r",0)) for x in rows] or [0])
        maxcolumn=0
        headers=[]
        for i,row in enumerate(rows):
            cells=row.findall(qname("c"))
            for c in cells:
                index=columns(c.attrib.get("r"))
                if index is not None:maxcolumn=max(maxcolumn,index+1)
            if i>=4:continue
            labs=[]
            for cell in cells:
                typ=cell.attrib.get("t")
                pos=columns(cell.attrib.get("r"))
                if pos is None:continue
                # Purely string header candidates, never numeric biological outcomes.
                value=""
                if typ=="s":
                    val=cell.find(qname("v"))
                    if val is not None and val.text:
                        k=int(val.text)
                        if k<0 or k>=len(strings):raise ValueError("Bad shared-string index")
                        value=strings[k]
                elif typ=="inlineStr":
                    value="".join(x.text or "" for x in cell.iter(qname("t")))
                elif typ=="str":
                    val=cell.find(qname("v"))
                    value="" if val is None else val.text or ""
                if value and len(value)<=130:
                    labs.append({"column_index_1_based":pos+1,"label":value[:120]})
            headers.append({"row_1_based":int(row.attrib.get("r",i+1)),
                            "text_labels_only":labs[:150]})
        result.append({"sheet":sn,"dimension_rows_max":maxrow,
                       "dimension_columns_max":maxcolumn,
                       "first_four_rows_string_label_candidates":headers,
                       "original_outcome_values_extracted":False})
    return {"workbook_sheets":result,"zip_entries":len(names),
            "shared_string_entries":len(strings),
            "outcome_cells_read":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    result={"record":RECORD,"url":SRC,"source_type":"source-registered Excel original",
        "factorial_a_priori":["temperature_30_vs_35","water_high_vs_drydown","predator_cue_absent_vs_present"],
        "source_study_design":"80 containers, three tadpoles per container, 3 clutches; bath-pool nesting must be checked",
        "source_bytes_expected":EXPECTED_BYTES,"status":"SOURCE_NOT_READ",
        "outcome_inference_authorized":False,
        "actual_predator_consumption_measured":False,
        "natural_pond_hydroperiod_measured":False}
    try:
        b=get_binary()
        result["download_sha256"]=hashlib.sha256(b).hexdigest()
        result["download_bytes"]=len(b)
        result["schema"]=inspect(b)
        result["status"]="SOURCE_DIGEST_OBTAINED_AND_RESPONSE_BLIND_WORKBOOK_SCHEMA"
    except Exception as e:
        result["status"]="SOURCE_BLOCKED_FAIL_CLOSED"
        result["error"]=str(e)[:400]
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_FROGCS_FUSCUS_FACTORIAL_G0")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_FROGCS_FUSCUS_FACTORIAL_G0")
    if result["status"]!="SOURCE_DIGEST_OBTAINED_AND_RESPONSE_BLIND_WORKBOOK_SCHEMA":
        raise SystemExit(4)

if __name__=="__main__":
    main()
