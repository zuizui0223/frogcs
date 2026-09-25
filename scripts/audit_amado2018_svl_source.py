#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URLS=[
    "https://www.ecography.org/sites/ecography.org/files/appendix/ecog-03889.zip",
    "https://nso-journals.org/ecographysites/ecography.org/files/appendix/ecog-03889.zip",
    "https://datadryad.org/downloads/file_stream/47038",
    "https://datadryad.org/stash/downloads/file_stream/47038",
]
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}

def fetch():
    last=None
    for url in URLS:
        req=urllib.request.Request(
            url,
            headers={
                "User-Agent":"Mozilla/5.0 frogcs-source-audit/0.1",
                "Accept":"application/zip,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream,*/*",
                "Referer":"https://www.ecography.org/readers/appendix"
            }
        )
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                b=r.read()
            if len(b)>10000:
                return b,url
            last=f"short download {len(b)} bytes"
        except Exception as e:
            last=repr(e)
    raise SystemExit("Amado source download failed: "+str(last))

def norm(x):
    toks=str(x or "").strip().split()
    if len(toks)>=2:
        return " ".join(toks[:2])
    return str(x or "").strip()

def candidates(sp):
    out=[sp]
    toks=sp.split()
    if len(toks)==2 and toks[0] in ALIASES:
        out.append(ALIASES[toks[0]]+" "+toks[1])
    return out

def main():
    source=Path("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json")
    if not source.is_file():
        raise SystemExit("species response receipt missing")
    obj=json.loads(source.read_text(encoding="utf-8"))
    spp=sorted({norm(x["species_code"]) for x in obj["species_results"]})
    if len(spp)!=29:
        raise SystemExit(f"species family drift: {len(spp)}")

    b,url=fetch()
    sha=hashlib.sha256(b).hexdigest()
    archive_members=[]
    selected_member=None
    workbook_bytes=b
    if b[:4] == b"PK\\x03\\x04":
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            archive_members=z.namelist()
            matches=[x for x in archive_members if Path(x).name=="SVL_Amadoetal2018.xlsx"]
            if len(matches)!=1:
                raise SystemExit(f"expected one SVL_Amadoetal2018.xlsx in archive, found {matches}")
            selected_member=matches[0]
            workbook_bytes=z.read(selected_member)
    xls=pd.ExcelFile(io.BytesIO(workbook_bytes),engine="openpyxl")
    sheets=[]
    best=None
    for sheet in xls.sheet_names:
        d=pd.read_excel(xls,sheet_name=sheet,engine="openpyxl")
        cols=[str(c) for c in d.columns]
        textcols=[str(c) for c in d.columns if d[c].dtype=="object"]
        svl_like=[c for c in cols if ("svl" in c.lower() or ("snout" in c.lower() and "vent" in c.lower()))]
        column_audits=[]
        for col in textcols:
            vals={norm(v) for v in d[col].dropna().tolist()}
            matched=[]
            for sp in spp:
                if any(c in vals for c in candidates(sp)):
                    matched.append(sp)
            column_audits.append({
                "column":col,
                "matched_count":len(matched),
                "matched_species":matched,
                "unmatched_species":[sp for sp in spp if sp not in matched]
            })
            rec=(len(matched),sheet,col,matched,[sp for sp in spp if sp not in matched])
            if best is None or rec[0]>best[0]:
                best=rec
        sheets.append({
            "sheet":sheet,
            "n_rows":int(len(d)),
            "n_columns":int(len(cols)),
            "columns":cols,
            "text_columns":textcols,
            "svl_like_columns":svl_like,
            "taxon_column_audits":column_audits
        })

    best_count,best_sheet,best_col,best_match,best_unmatched=best if best else (0,None,None,[],spp)
    selected_sheet=next((x for x in sheets if x["sheet"]==best_sheet),None)
    usable=bool(
        best_count>=15 and selected_sheet is not None and
        len(selected_sheet["svl_like_columns"])>=1
    )
    result={
        "audit":"amado2018_svl_source_audit_v0_1",
        "contract":"AMADO2018_SVL_SOURCE_AUDIT_CONTRACT_V0_1.json",
        "transport_repair_contract":"AMADO2018_SVL_SOURCE_AUDIT_REPAIR_V0_1_1.json",
        "download_url_used":url,
        "archive_members":archive_members,
        "selected_archive_member":selected_member,
        "file_name":"SVL_Amadoetal2018.xlsx",
        "byte_size":len(b),
        "sha256":sha,
        "sheet_names":xls.sheet_names,
        "sheets":sheets,
        "best_species_structure":{
            "sheet":best_sheet,
            "column":best_col,
            "matched_count":best_count,
            "matched_species":best_match,
            "unmatched_species":best_unmatched
        },
        "usable_for_frozen_validation":usable,
        "effect_values_opened":False
    }
    Path("AMADO2018_SVL_SOURCE_AUDIT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
