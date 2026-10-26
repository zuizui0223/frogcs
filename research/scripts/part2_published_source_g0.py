#!/usr/bin/env python3
"""Frogcs Part-II exact-source eligibility (G0); read metadata, NEVER outcomes.

Standard library only. Verifies direct source files and interrogates precisely
declared original IPT/EDI/Dryad resources. No unsupported site joins, no
sex-specific inference, no tadpole mortality or predator assertions.
Only aggregate row/site/date/column coverage is output. No raw sensitive
location IDs are logged. Source downloads are transient (in-memory only).
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from io import BytesIO, StringIO, TextIOWrapper
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import urllib.request
import zipfile
from xml.etree import ElementTree as ET

URLS = {
 "mohonk_edi_species": ("https://pasta.lternet.edu/package/data/eml/edi/398/4/737389d6c2090ee27a3084898f2e7853", "csv"),
 "mohonk_edi_water": ("https://pasta.lternet.edu/package/data/eml/edi/398/4/5835a29e0fbe1ba179ee5ffe27121df6", "csv"),
 "mohonk_ipt": ("https://ipt.gbif.us/archive.do?r=mohonk-amphibian-spring-sampling&v=1.1", "dwca"),
 "inbo_chorus": ("https://ipt.inbo.be/archive.do?r=meetnetten-amphibia-roepkoren-occurrences", "dwca"),
 "inbo_larva": ("https://ipt.inbo.be/archive.do?r=meetnetten-amfibieen-larven-metamorfen-occurrences", "dwca"),
 "esgr_amphibian_workbook": ("https://datadryad.org/api/v2/files/38621/download", "xlsx"),
 "stmarks_encounter_workbook": ("https://datadryad.org/api/v2/files/51835/download", "xlsx"),
}
MAX_BYTES = 18_000_000
MD5 = {
 "esgr_amphibian_workbook":"c0c50fc176eac6e054e5f75b8c7a24d9",
 "stmarks_encounter_workbook":"12a7deaf1a8bf38fc122cb7661ee7f6c",
}
COL_INTEREST = {
 "Location","Sample_Date","SampleDate","ScientificName","ChorusCode","ChorusCount",
 "EggMass_n","TadLarv_n","Juv_n","Depth","WaterDepth","Precipitation",
 "eventID","parentEventID","locationID","eventDate","samplingProtocol",
 "scientificName","lifeStage","individualCount","occurrenceStatus",
}

def fetch(url, limit=MAX_BYTES):
    req=urllib.request.Request(url,headers={
        "User-Agent":"frogcs-source-audit/1.0 (source-blind manuscript data qualification)",
        "Accept":"text/csv, application/zip, application/octet-stream, */*",
    })
    with urllib.request.urlopen(req,timeout=22) as r:
        blob=r.read(limit+1)
        ct=r.headers.get("Content-Type","")
    if len(blob)>limit: raise ValueError("oversized source: G0 fail closed")
    return blob,ct

def xml_child(e,name):
    for obj in e:
        if obj.tag.rsplit("}",1)[-1]==name:
            return obj
    return None

def xml_children(e,name):
    return [x for x in e if x.tag.rsplit("}",1)[-1]==name]

def norm_delim(raw):
    return {"\\t":"\t","\\n":"\n","\\r":"\r","\\\"":'"'}.get(raw,raw)

def parse_dwca_part(zf,node):
    paths=xml_child(node,"files")
    if paths is None: raise ValueError("missing part/files")
    loc=xml_child(paths,"location")
    if loc is None or not loc.text: raise ValueError("missing part/location")
    filename=loc.text.strip()
    if filename not in zf.namelist(): raise ValueError("missing archive member "+filename)
    index_fields=[]
    for field in xml_children(node,"field"):
        pos=int(field.attrib["index"])
        name=field.attrib.get("term","").rsplit("/",1)[-1].rsplit("#",1)[-1]
        index_fields.append((pos,name))
    delim=norm_delim(node.attrib.get("fieldsTerminatedBy","\\t"))
    enclosure=norm_delim(node.attrib.get("fieldsEnclosedBy",'"'))
    skip=int(node.attrib.get("ignoreHeaderLines","0"))
    if len(delim)!=1: raise ValueError("invalid delimiter")
    rows=0; missing=0; site_dates=set(); sites=set(); years=set()
    spans=Counter(); labels=set()
    with zf.open(filename) as raw, TextIOWrapper(raw,encoding=node.attrib.get("encoding","UTF-8-SIG"),errors="replace",newline="") as f:
        reader=csv.reader(f,delimiter=delim,quotechar=enclosure if len(enclosure)==1 else '"')
        for k,row in enumerate(reader):
            if k<skip:continue
            rows+=1
            if rows>300000: raise ValueError("unreasonably many records")
            d={name:row[i].strip() if i<len(row) else ""
               for i,name in index_fields}
            site=d.get("locationID",""); dt=d.get("eventDate","")
            if site:
                sites.add(site)
                y=dt[:4] if re.match(r"^\d{4}",dt) else ""
                if y: years.add(y);site_dates.add((site,y,dt[:10]))
                spans[(site,y)]+=1
            else:missing+=1
            if rows==1:labels={z for _,z in index_fields}
    return {"file":filename,"rows":rows,"columns":sorted(labels),
            "important_fields":sorted(labels&COL_INTEREST),
            "location_id_nonblank_rows":rows-missing,
            "locations":len(sites),"years":sorted(years),
            "distinct_site_years":len({(s,y) for s,y,dt in site_dates}),
            "source_original_location_ids_exported":False},{
              "sites":sites,"site_dates":site_dates
            }

def audit_dwca(blob):
    if not zipfile.is_zipfile(BytesIO(blob)):raise ValueError("not a valid DwC-A zip")
    with zipfile.ZipFile(BytesIO(blob)) as z:
        if "meta.xml" not in z.namelist():raise ValueError("archive lacks meta.xml")
        root=ET.fromstring(z.read("meta.xml"))
        core=next((n for n in root if n.tag.rsplit("}",1)[-1]=="core"),None)
        if core is None:raise ValueError("no DwC core")
        core_stats,unit=parse_dwca_part(z,core)
        extensions=[]
        for ex in root:
            if ex.tag.rsplit("}",1)[-1]=="extension":
                st,_=parse_dwca_part(z,ex)
                extensions.append(st)
        report={"core":core_stats,"extensions":extensions,
                "archive_entry_count":len(z.namelist()),
                "entries":sorted(z.namelist())[:30]}
        return report,unit

def audit_csv(blob):
    text=blob.decode("utf-8-sig",errors="replace")
    sniffer=csv.Sniffer()
    try: delim=sniffer.sniff(text[:3000],delimiters=",;\t").delimiter
    except csv.Error:delim=","
    f=StringIO(text)
    r=csv.DictReader(f,delimiter=delim)
    cols=r.fieldnames or []
    if not cols:raise ValueError("CSV no header")
    count=0;sites=set();years=set();sitedates=set()
    for row in r:
        count+=1
        if count>300000:raise ValueError("very large source, G0 sampling cap")
        site=(row.get("Location") or row.get("locationID") or "").strip()
        dt=(row.get("Sample_Date") or row.get("eventDate") or "").strip()
        if site:sites.add(site)
        if re.match(r"^\d{4}",dt):
            years.add(dt[:4])
            if site:sitedates.add((site,dt[:4],dt[:10]))
    return {"rows":count,"columns":cols,
        "important_fields":sorted(set(cols)&COL_INTEREST),
        "locations":len(sites),"years":sorted(years),
        "distinct_site_dates":len(sitedates),"raw_values_retained":False}

def run_probe(name,kind,url):
    result={"id":name,"url":url,"format":kind,"status":"blocked"}
    try:
        blob,ct=fetch(url)
        result.update({"http":"200","bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest(),"content_type":ct})
        if kind=="csv":
            result["schema"]=audit_csv(blob)
        elif kind=="dwca":
            report,unit=audit_dwca(blob)
            result["schema"]=report
            # Return identifiers only inside process for exact join; never
            # put them in persisted result.
            result["status"]="verified_dwca"
            return result,unit
        elif kind=="xlsx":
            expected=MD5[name];got=hashlib.md5(blob).hexdigest()
            result["md5"]=got;result["source_md5_matches_manifest"]=(got==expected)
            if got!=expected:raise ValueError("original workbook digest mismatch")
            if not zipfile.is_zipfile(BytesIO(blob)):
                raise ValueError("invalid Excel zip container")
            with zipfile.ZipFile(BytesIO(blob)) as z:
                result["xlsx_structural_package"]={"members":len(z.namelist()),
                     "has_workbook_xml":"xl/workbook.xml" in z.namelist()}
            # Worksheet contents are deliberately not read on G0.
        result["status"]="verified_source_structure"
    except Exception as exc:
        result.update({"status":"blocked_or_invalid","reason":str(exc)[:160]})
    return result,None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    results={};private={}
    with ThreadPoolExecutor(max_workers=7) as pool:
        jobs={pool.submit(run_probe,name,kind,url):name for name,(url,kind) in URLS.items()}
        for fut in as_completed(jobs):
            name=jobs[fut]
            item,private_unit=fut.result()
            results[name]=item
            if private_unit is not None:private[name]=private_unit
    joins={"status":"NOT_AUDITED"}
    if "inbo_chorus" in private and "inbo_larva" in private:
        c=private["inbo_chorus"]["sites"];l=private["inbo_larva"]["sites"]
        cdate=private["inbo_chorus"]["site_dates"]
        ldate=private["inbo_larva"]["site_dates"]
        cm=defaultdict(list);lm=defaultdict(list)
        for site,year,dt in cdate:cm[(site,year)].append(dt)
        for site,year,dt in ldate:lm[(site,year)].append(dt)
        both=set(cm)&set(lm)
        forward=sum(any(ce<le for ce in cm[k] for le in lm[k]) for k in both)
        joins={"status":"ID_OVERLAP_CHECKED_NOT_POND_GEOMETRY",
               "exact_shared_location_ids":len(c&l),
               "exact_shared_site_years":len(both),
               "site_years_with_chorus_before_larval_census":forward,
               "coordinates_not_used":True,"source_ids_exported":False,
               "same_physical_pond_confirmed":False,
               "reproductive_success_or_predation_claim":False}
    report={
        "programme":"frogcs/part2-g0",
        "status":"RAW_SOURCE_COVERAGE_ONLY_NO_BIOLOGICAL_EFFECTS",
        "refs":results,
        "inbo_between_protocol_join":joins,
        "all_g0_g1_g2_recruitment_paper_claims":False,
        "rc6_source_modified":False,
        "source_data_redistributed":False,
        "interpretation_guard":"Source may measure calls, eggs or aquatic stages separately; true survival, predation, and summer hydroperiod resets require extra validation."
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_FROGCS_PART2_G0")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    print("END_FROGCS_PART2_G0")

if __name__=="__main__":
    main()
