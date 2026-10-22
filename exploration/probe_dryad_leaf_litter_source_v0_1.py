#!/usr/bin/env python3
"""Dryad source-only, outcome-blind QA for American-toad litter experiments.

Only validates public DOI/version/files and spreadsheet sheet/header metadata.
Never opens numeric biological responses or stores/re-distributes raw third-party files.
"""
import argparse,hashlib,io,json,re,urllib.parse,urllib.request,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

DOI="doi:10.5061/dryad.np5hqbztq"
BASE="https://datadryad.org"
BASEAPI=BASE+"/api/v2"
P="https://datadryad.org/dataset/doi%3A10.5061/dryad.np5hqbztq"
DOC="10.1007/s10452-021-09893-y"
EXPECTED={"Litter_Toad_Ecology_DiGiacopo_Hua_2021.xlsx","LITTER_TOAD_ECOLOGY_readme.txt"}
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PR="{http://schemas.openxmlformats.org/package/2006/relationships}"

def fetch(path,maximum=4000000):
    uri=path if path.startswith("https://") else BASEAPI+path
    q=urllib.request.Request(uri,headers={"User-Agent":"frogcs-reproducibility-source-audit-v0.1 (public academic metadata)","Accept":"application/json,application/octet-stream,*/*"})
    with urllib.request.urlopen(q,timeout=55) as resp:
        data=resp.read(maximum+1)
        status=resp.status
        endpoint=resp.url
    if len(data)>maximum:raise ValueError("Unexpectedly large source; fail-closed")
    if status!=200:raise RuntimeError("HTTP not OK: "+str(status))
    return data,endpoint

def api(path):
    data,_=fetch(path)
    return json.loads(data)

def find_embedded_rows(obj):
    embedded=obj.get("_embedded",{}) if isinstance(obj,dict) else {}
    for key,v in embedded.items():
        if isinstance(v,list) and all(isinstance(x,dict) for x in v):
            return v
    if isinstance(obj,dict):
        for key,v in obj.items():
            if isinstance(v,list) and v and all(isinstance(x,dict) for x in v):
                return v
    return []

def xlsx_header_inventory(raw):
    z=zipfile.ZipFile(io.BytesIO(raw))
    if z.testzip() is not None: raise ValueError("Corrupted source XLSX")
    ss=[]
    if "xl/sharedStrings.xml" in z.namelist():
        doc=ET.fromstring(z.read("xl/sharedStrings.xml"))
        ss=["".join(t.text or "" for t in si.iter() if t.tag==NS+"t") for si in doc.findall(NS+"si")]
    book=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    paths={}
    for r in rel.findall(PR+"Relationship"):
        target=r.attrib.get("Target","")
        paths[r.attrib["Id"]]=target.lstrip("/") if target.startswith("/") else (
            target if target.startswith("xl/") else "xl/"+target)
    sheets=[]
    for s in book.findall(".//"+NS+"sheet"):
        p=paths[s.attrib[RID+"id"]]
        # XML streaming parse uses element tree but inspects only first row; no numeric outcomes read.
        root=ET.fromstring(z.read(p))
        dim=root.find(NS+"dimension")
        rows=root.findall(".//"+NS+"sheetData/"+NS+"row")
        header={}
        if rows:
            for c in rows[0].findall(NS+"c"):
                addr=c.attrib.get("r","")
                col=re.match("[A-Z]+",addr)
                if not col:continue
                typ=c.attrib.get("t")
                v=c.find(NS+"v")
                if typ=="s" and v is not None: label=ss[int(v.text)]
                elif typ=="inlineStr":label="".join(t.text or "" for t in c.iter() if t.tag==NS+"t")
                else:label=v.text if v is not None else ""
                header[col.group()]=label
        sheets.append({"sheet":s.attrib["name"],"range":dim.attrib.get("ref") if dim is not None else None,
                       "header_columns":header,"numeric_response_cells_read":False})
    return sheets

def run():
    encoded=urllib.parse.quote(DOI,safe="")
    ds=api("/datasets/"+encoded)
    if DOI.lower() not in json.dumps(ds,ensure_ascii=True).lower():
        raise ValueError("Dryad metadata does not match DOI")
    versions=api("/datasets/"+encoded+"/versions")
    vs=find_embedded_rows(versions)
    if not vs:raise RuntimeError("Published Dryad dataset version records not returned")
    def get_version_id(v):
        if v.get("id") is not None:
            return int(v["id"])
        for link in (v.get("_links") or {}).values():
            href=link.get("href","") if isinstance(link,dict) else ""
            m=re.search(r"/versions/(\\d+)(?:$|[/?#])",href)
            if m:return int(m.group(1))
        return None
    ids=[(get_version_id(v),v) for v in vs]
    ids=[x for x in ids if x[0] is not None]
    if not ids:raise RuntimeError("No version with stable ID or version link: "+str(vs[0].keys()))
    version_id,latest=max(ids,key=lambda x:(int(x[1].get("versionNumber",0)),x[0]))
    files=api("/versions/"+str(version_id)+"/files")
    entries=find_embedded_rows(files)
    if not entries:raise RuntimeError("Dryad file list empty")
    manifest=[]
    for f in entries:
        name=f.get("path") or f.get("name") or f.get("filename") or ""
        manifest.append({"id":f.get("id"),"name":name,"size":f.get("size"),
                         "digest":f.get("digest"),"digestType":f.get("digestType"),
                         "mimeType":f.get("mimeType")})
    names={x["name"].split("/")[-1] for x in manifest}
    if not EXPECTED.issubset(names):raise RuntimeError("Published Dryad workbook/readme not found: "+str(names))
    sample=next(x for x in manifest if x["name"].split("/")[-1].lower().endswith(".xlsx"))
    if not isinstance(sample["id"],int):raise RuntimeError("No DOI-pinned workbook file ID")
    raw,_=fetch("/files/"+str(sample["id"])+"/download",maximum=3000000)
    if not raw.startswith(b"PK"):raise RuntimeError("Workbook downloaded but not XLSX ZIP")
    digest=hashlib.md5(raw).hexdigest()
    stated=sample.get("digest")
    typ=str(sample.get("digestType","")).lower()
    if stated and typ=="md5" and stated.lower()!=digest:
        raise RuntimeError("Source MD5 changed from official Dryad metadata")
    out={"status":"source_schema_verified_no_responses_read","source_type":"published third-party dataset",
         "study_doi":DOC,"dataset_doi":DOI,"version_id":version_id,
         "version_number":latest.get("versionNumber"),"file_manifest":manifest,
         "workbook_md5":digest,"workbook_sha256":hashlib.sha256(raw).hexdigest(),
         "workbook_bytes":len(raw),"sheets":xlsx_header_inventory(raw),
         "response_numeric_values_inspected":False,"raw_data_committed":False,
         "causal_higher_order_effect_estimated":False}
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("build/leaf_litter_source_schema.json"))
    a=p.parse_args()
    try:result=run()
    except Exception as ex:
        result={"status":"BLOCKED_source_qa","error_type":type(ex).__name__,
                "error":str(ex)[:700],"response_numeric_values_inspected":False,
                "raw_data_committed":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("DRYAD_LEAF_LITTER_SOURCE_RECEIPT_BEGIN")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    print("DRYAD_LEAF_LITTER_SOURCE_RECEIPT_END")
    if result["status"]!="source_schema_verified_no_responses_read":raise SystemExit(1)

if __name__=="__main__":main()
