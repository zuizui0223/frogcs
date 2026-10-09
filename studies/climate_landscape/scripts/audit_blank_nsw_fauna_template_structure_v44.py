#!/usr/bin/env python3
"""Public OFFICIAL BLANK BioNet systematic-fauna template structure preflight v4.4.

The NSW government distributes an XLSX submission template. This program
downloads ONLY that public BLANK template, reads XLSX workbook metadata and
the first eight template rows for possible field-header labels, and prints a
bounded structural receipt. It never fetches frog records or logs into BioNet.
No Excel macros, external workbook connections, formulas or links are run.
The XLSX is interpreted as a ZIP/OpenXML document, not executed or edited.
"""
from __future__ import annotations
import json
import re
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from hashlib import sha256

URL="https://www.environment.nsw.gov.au/sites/default/files/2025-05/fauna-survey-datasheet-6000_0.xlsx"
MAX_BYTES=6_000_000
S="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P="http://schemas.openxmlformats.org/package/2006/relationships"
NS={"s":S}

def parse_template(data:bytes)->dict:
    if not data.startswith(b"PK"):
        raise ValueError("Official template is not an XLSX ZIP")
    with zipfile.ZipFile(BytesIO(data)) as z:
        names=set(z.namelist())
        if "xl/workbook.xml" not in names or "xl/_rels/workbook.xml.rels" not in names:
            raise ValueError("Workbook metadata absent")
        if len(names)>500:
            raise ValueError("Excessive archive size")
        def load(name):
            if name not in names:
                raise ValueError("Missing XML part "+name)
            info=z.getinfo(name)
            if info.file_size>2_000_000:
                raise ValueError("XML part too large")
            return ET.fromstring(z.read(name))
        book=load("xl/workbook.xml")
        rels=load("xl/_rels/workbook.xml.rels")
        targets={}
        for link in rels.findall("{"+P+"}Relationship"):
            targets[link.attrib.get("Id")]=link.attrib.get("Target")
        shared=[]
        if "xl/sharedStrings.xml" in names:
            root=load("xl/sharedStrings.xml")
            for si in root.findall("{"+S+"}si"):
                text="".join(n.text or "" for n in si.iter("{"+S+"}t"))
                shared.append(text)
        sheets=[]
        for item in book.findall("s:sheets/s:sheet",NS):
            sheet_name=item.attrib["name"]
            relid=item.attrib.get("{"+R+"}id")
            target=targets.get(relid,"")
            if target.startswith("/"):
                part=target.lstrip("/")
            elif target.startswith("xl/"):
                part=target
            else:
                part="xl/"+target
            if ".." in part.split("/") or not re.fullmatch(r"xl/worksheets/sheet\d+\.xml",part):
                raise ValueError("Unexpected external sheet target")
            root=load(part)
            previews=[]
            rows=root.findall("s:sheetData/s:row",NS)
            for row in rows[:8]:
                cells=[]
                for c in row.findall("s:c",NS)[:35]:
                    value=c.find("s:v",NS)
                    inline=c.find("s:is",NS)
                    if value is not None:
                        raw=value.text or ""
                        if c.attrib.get("t")=="s":
                            try:raw=shared[int(raw)]
                            except (IndexError,ValueError):raw="[invalid shared string]"
                        elif c.attrib.get("t") not in ("inlineStr","str"):
                            # Numeric/formula values are not field header labels.
                            raw=""
                    elif inline is not None:
                        raw="".join(x.text or "" for x in inline.iter("{"+S+"}t"))
                    else:
                        raw=""
                    raw=" ".join(raw.split())[:90]
                    if raw and not raw.startswith("="):
                        cells.append({"ref":c.attrib.get("r",""),"text":raw})
                if cells:
                    previews.append({"row":int(row.attrib.get("r","0")),"visible_texts":cells[:20]})
            sheets.append({"name":sheet_name,"first_nonempty_rows":previews[:5],
                           "number_of_rows_in_template":len(rows)})
        if not sheets:
            raise ValueError("No workbook sheets")
        return {"sheet_count":len(sheets),"sheets":sheets}

def main():
    receipt={"audit":"nsw_official_blank_fauna_survey_template_schema_v44",
             "url":URL,"public_blank_template_only":True,
             "real_frog_data_read":False,"calling_outcomes_read":False,
             "historical_343_survey_manifest_recovered":False,
             "rc6_unchanged":True}
    try:
        req=urllib.request.Request(URL,headers={
            "User-Agent":"frogcs-source-only-public-blank-template-audit/4.4",
            "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
        with urllib.request.urlopen(req,timeout=35) as r:
            data=r.read(MAX_BYTES+1)
            if r.status!=200 or len(data)>MAX_BYTES:
                raise ValueError("Unexpected source payload")
            receipt["http_status"]=r.status
            receipt["source_content_type"]=r.headers.get("content-type")
        receipt["bytes_sha256"]=sha256(data).hexdigest()
        receipt["structure"]=parse_template(data)
        receipt["status"]="OFFICIAL_BLANK_TEMPLATE_METADATA_OK"
    except urllib.error.HTTPError as e:
        receipt["status"]="HTTP_UNAVAILABLE"
        receipt["http_status"]=e.code
    except (urllib.error.URLError,TimeoutError) as e:
        receipt["status"]="NETWORK_UNAVAILABLE"
        receipt["error_type"]=type(e).__name__
    except (ValueError,ET.ParseError,zipfile.BadZipFile) as e:
        receipt["status"]="SOURCE_SCHEMA_INVALID"
        receipt["error_type"]=type(e).__name__
    out=Path("studies/climate_landscape/receipts/NSW_BIONET_BLANK_FAUNA_TEMPLATE_V44.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":receipt["status"],"http_status":receipt.get("http_status"),
        "sheet_count":receipt.get("structure",{}).get("sheet_count"),
        "sheets":[{"name":x["name"],"sample_rows":x["first_nonempty_rows"][:3]}
          for x in receipt.get("structure",{}).get("sheets",[])],
        "frog_records_read":False},sort_keys=True))

if __name__=="__main__":
    main()
