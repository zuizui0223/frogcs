#!/usr/bin/env python3
"""Minimal read-only XLSX OOXML decoder for the source-pinned factorial trial.

Unlike a mutable spreadsheet application, this parses original worksheet
cells only for explicitly permitted named columns; do not resave or modify
the source. The G0 caller only permits treatment/grain columns, not outcomes.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
import hashlib
import re
import zipfile

URL="https://digital.csic.es/bitstream/10261/411885/1/Delgadillo%20et%20al.%2c%20dataset_fuscus.xlsx"
SOURCE_SHA256="eb76b0ec8162278c14860fddcfe30a487ff9e8fc4b8fe40311f88dabe0fd9b25"
SOURCE_BYTES=59841
MAIN="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
OFFICE="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
ROOTSHEET="xl/worksheets/sheet1.xml"

def original_source():
    request=Request(URL,headers={
        "User-Agent":"frogcs-source-verification/1.0 (scientific, noncommercial)",
        "Accept":"application/octet-stream, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*"})
    with urlopen(request,timeout=35) as stream:
        blob=stream.read(250000)
    assert len(blob)==SOURCE_BYTES,f"Source file size drift: {len(blob)}"
    assert hashlib.sha256(blob).hexdigest()==SOURCE_SHA256,"Source SHA-256 drift"
    return blob

def colnum(address):
    m=re.match(r"^([A-Za-z]+)",address)
    if not m:return None
    idx=0
    for letter in m.group(1).upper():idx=idx*26+ord(letter)-64
    return idx-1

def decode(rows_subset,allowed_cols=None):
    """Access only specified columns (G0 no biological response access)."""
    with zipfile.ZipFile(BytesIO(rows_subset)) as z:
        names=set(z.namelist())
        assert ROOTSHEET in names,"Unexpected source workbook sheet path"
        shared=[]
        if "xl/sharedStrings.xml" in names:
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(MAIN+"si"):
                shared.append("".join(t.text or "" for t in si.iter(MAIN+"t")))
        root=ET.fromstring(z.read(ROOTSHEET))
        data=root.find(".//"+MAIN+"sheetData")
        assert data is not None,"No sheetData"
        rows=list(data.findall(MAIN+"row"))
        def get(row,cols_only):
            out={}
            for cell in row.findall(MAIN+"c"):
                i=colnum(cell.attrib.get("r",""))
                if i not in cols_only:continue
                typ=cell.attrib.get("t","")
                value=cell.find(MAIN+"v")
                raw=value.text if value is not None else None
                if typ=="s" and raw is not None:
                    raw=shared[int(raw)]
                elif typ=="inlineStr":
                    raw="".join(t.text or "" for t in cell.iter(MAIN+"t"))
                elif typ in ("n","") and raw not in (None,""):
                    try:raw=float(raw)
                    except ValueError:pass
                out[i]=raw
            return out
        if not rows:return [],[]
        header=get(rows[0],set(range(32)))
        cols=[str(header.get(i) or "").strip() for i in range(32)]
        assert len(set(cols))==len(cols), "Duplicate or blank header"
        allowed=set(cols) if allowed_cols is None else set(allowed_cols)
        assert allowed<=set(cols), "Requested column missing: "+str(allowed-set(cols))
        requested={cols.index(k):k for k in allowed}
        output=[]
        for row in rows[1:]:
            cells=get(row,set(requested))
            if not cells:continue
            output.append({name:cells.get(i) for i,name in requested.items()})
        return cols,output
