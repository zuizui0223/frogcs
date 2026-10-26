#!/usr/bin/env python3
"""Blind source schema audit: BioFresh Pond Data v2.2 (CC0, DOI 10.13148/bf76).

Archive lists 17,532 records from 460 European ponds, mainly amphibians,
macrophytes and invertebrates. This script tests whether records can be
joined within REAL pond IDs and whether multiple trophic groups were surveyed.
NO inferred species absences or novel plant/amphibian effects are estimated.
Publication advisory from source metadata: notify data contributors 45 days
in advance and respect their 30-day review/objection opportunity.
"""
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

URL="https://data.freshwaterbiodiversity.eu/ipt/archive.do?r=bf76&v=2.2"
LIMIT_BYTES=20_000_000
LABELS=["locationID","locality","decimalLatitude","decimalLongitude","class",
        "order","family","kingdom","phylum","scientificName","taxonRank",
        "eventDate","year","datasetName","basisOfRecord","occurrenceID",
        "eventID","country","samplingProtocol","occurrenceStatus",
        "individualCount","organismQuantity","organismQuantityType"]

def read_archive():
    req=Request(URL,headers={"User-Agent":"BioFreshMetadataQC/1.0 (open public biodiversity data)"})
    with urlopen(req,timeout=90) as r:
        n=0; data=[]
        for block in iter(lambda:r.read(1<<19),b""):
            n+=len(block)
            if n>LIMIT_BYTES: raise ValueError("IPT archive exceeds safety cap")
            data.append(block)
        zip_bytes=b"".join(data)
    if not zip_bytes[:2]==b"PK":
        raise ValueError("Not a valid zip download")
    return zip_bytes

def read_meta(z):
    xml_names=[n for n in z.namelist() if n.lower().endswith("meta.xml")]
    if not xml_names: raise ValueError("Missing DwC-A meta.xml")
    root=ET.fromstring(z.read(xml_names[0]))
    core=root.find(".//{*}core")
    if core is None: raise ValueError("Missing Darwin Core Archive core")
    files=core.findall(".//{*}files/{*}location")
    if not files: raise ValueError("Missing core data location")
    core_path=files[0].text
    schema={}
    for f in core.findall("{*}field"):
        idx=int(f.attrib["index"])
        term=f.attrib.get("term","").rsplit("/",1)[-1]
        schema[idx]=term
    return core_path, schema, root, core

def parse_core(z,path,cols,core):
    opts=core.attrib
    enc=opts.get("encoding","UTF-8")
    delimiter=opts.get("fieldsTerminatedBy","\\t").replace("\\t","\t")
    quotechar=opts.get("fieldsEnclosedBy",'"')
    raw=z.read(path).decode(enc,"replace")
    reader=csv.reader(io.StringIO(raw),delimiter=delimiter,quotechar=quotechar or '"')
    lines_ignored=int(opts.get("ignoreHeaderLines","0"))
    for i in range(lines_ignored):next(reader)
    count=0;out=[]
    for row in reader:
        if not row:continue
        count+=1
        out.append({value:row[j].strip() if j<len(row) else ""
                    for j,value in cols.items()})
    return out

def audit():
    data=read_archive()
    z=zipfile.ZipFile(io.BytesIO(data))
    path,columns,root,core=read_meta(z)
    if path not in z.namelist():
        path=next((n for n in z.namelist() if n.endswith("/"+path)),path)
    if path not in z.namelist(): raise ValueError(f"core absent: {path}")
    rows=parse_core(z,path,columns,core)
    check={k:sum(bool(r.get(k)) for r in rows) for k in LABELS}
    examples={k:sorted({r.get(k) for r in rows if r.get(k)})[:15]
              for k in LABELS if check[k]}
    group=Counter()
    sites=defaultdict(set)
    sourceSites=defaultdict(set)
    identities=[]
    for row in rows:
        order=(row.get("order","") or "").lower()
        clazz=(row.get("class","") or "").lower()
        family=row.get("family","")
        kingdom=(row.get("kingdom","") or "").lower()
        if clazz=="amphibia" or order in ["anura","caudata"]:
            g="amphibia"
        elif order=="odonata":
            g="odonata"
        elif kingdom in ["plantae","viridiplantae"] or "spermatophyta" in row.get("phylum","").lower():
            g="macrophyte"
        elif clazz in ["insecta","mollusca","branchiopoda","malacostraca"] or order in ["ephemeroptera","trichoptera"]:
            g="other_invertebrates"
        else:g="unresolved_other"
        group[g]+=1
        ident=(row.get("locationID") or row.get("locality") or "").strip()
        if ident:sites[ident].add(g)
        ds=row.get("datasetName","").strip()
        if ds and ident:sourceSites[ds].add(ident)
        if len(identities)<12:
            identities.append(dict(locality=ident,loc_id=row.get("locationID"),
                                   year=row.get("year"),dataset=ds,
                                   group=g,name=row.get("scientificName")))
    counters=Counter()
    for groups in sites.values():
        counters["all_known_sites"]+=1
        for g in group:
            if g in groups: counters[f"site_has_{g}"]+=1
        if "amphibia" in groups and "macrophyte" in groups:
            counters["site_amphibia_and_plants"]+=1
        if "amphibia" in groups and "odonata" in groups:
            counters["site_amphibia_and_odonata"]+=1
        if len(groups)>=3:counters["site_three_or_more_groups"]+=1
    return {
        "doi":"10.13148/bf76",
        "publisher":"BioFresh, CC0 v2.2 (2017-09-08)",
        "source_url":URL,
        "archive_sha256":hashlib.sha256(data).hexdigest(),
        "archive_bytes":len(data),
        "archive_files":z.namelist(),
        "core_path":path,
        "mapped_fields":columns,
        "core_rows":len(rows),
        "reported_records_in_metadata":17532,
        "nonempty_fields":check,
        "examples_of_identifiers":examples,
        "taxon_classification_counts":dict(group),
        "locality_group_overlap":dict(counters),
        "source_study_ids":len(sourceSites),
        "first_sample_identity_rows":identities,
        "data_access_advisory":"Source metadata asks publication advance notice to data owners 45 days and grants 30-day objection period. Respect if preparing publication.",
        "analysis_boundary":"Locality strings may not be unique across source studies; no pooled occurrence-vs-absence claim before verifying study sampling and wetland IDs.",
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="research/results/biofresh_ponds_source_audit")
    args=p.parse_args()
    d=audit()
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"schema_receipt.json").write_text(
        json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("BEGIN_BIOFRESH_POND_SCHEMA")
    print(json.dumps(d,indent=2,ensure_ascii=False))
    print("END_BIOFRESH_POND_SCHEMA")
