#!/usr/bin/env python3
"""USGS ARMI 2024 original PUBLIC survey CSV v1.1 (2026) SOURCE-GRAIN ONLY.

Official ScienceBase item verified through read-only metadata. This is NOT
frog response estimation, species zero assignment, or source record release.
Individual site/coordinates/observer values never printed or saved.
"""
from __future__ import annotations
import csv,hashlib,io,json,re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen

ITEM="68016413d4be0263cab109a8"
META=f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json"
FILENAME="ARMI_2024_cricket_frog_data_release_2025_v1.1.csv"
EXPECTED_BYTES=235391
MAX_SIZE=500000
OUTPUT="studies/climate_landscape/receipts/USGS_ARMI2024_PUBLIC_ORIGINAL_CSV_GRAIN_V80.json"

def allowed(url):
    u=urlparse(url)
    h=(u.hostname or "").lower()
    return u.scheme=="https" and (
        h.endswith(".sciencebase.gov") or h=="sciencebase.gov" or
        h.endswith(".amazonaws.com")
    )

def get_public(url,cap):
    if not allowed(url):raise ValueError("DISALLOWED_ORIGINAL_URL")
    with urlopen(Request(url,headers={"User-Agent":"frogcs-open-survey-metadata/8.0",
                                      "Accept":"application/json,text/csv,text/plain"}),timeout=36) as r:
        final=r.geturl()
        if not allowed(final):raise ValueError("UNEXPECTED_PUBLIC_FILE_REDIRECT")
        if r.status!=200:raise ValueError("PUBLIC_HTTP_STATUS_NOT_200")
        raw=r.read(cap+1)
    if not raw or len(raw)>cap:raise ValueError("SOURCE_BODY_UNEXPECTED_SIZE")
    return raw

def structural_receipt(raw):
    txt=raw.decode("utf-8-sig")
    dialect=csv.Sniffer().sniff(txt[:15000],delimiters=",;\t|")
    rd=csv.DictReader(io.StringIO(txt),dialect=dialect)
    headers=rd.fieldnames
    if not headers or len(headers)!=len(set(headers)) or len(headers)>200:
        raise ValueError("SOURCE_BAD_CSV_HEADER")
    rows=0
    nonblank=Counter()
    malformed=0
    bycol_unique={h:set() for h in headers
                  if re.search(r"site|point|wetland|location|visit|survey|observer|date|time|id|method|weather",h,re.I)}
    col_minmax={h:[] for h in headers if re.search(r"date|year",h,re.I)}
    safe_numeric=Counter()
    for row in rd:
        rows+=1
        if rows>100000:raise ValueError("SOURCE_RECORD_OVER_LIMIT")
        if None in row:malformed+=1
        for col in headers:
            val=(row.get(col) or "").strip()
            if val and val.upper() not in {"NA","N/A","NULL","MISSING"}:
                nonblank[col]+=1
                if col in bycol_unique and len(bycol_unique[col])<=100001:
                    bycol_unique[col].add(val)
                if col in col_minmax:
                    # Must not print location or row values; only validate plausible date format
                    if re.fullmatch(r"\d{4}(?:[-/]\d{2}(?:[-/]\d{2})?)?",val):
                        col_minmax[col].append(val[:4])
    summary={
        "n_source_rows":rows,
        "n_source_fields":len(headers),
        "source_field_names_only":headers,
        "full_nonblank_counts_by_field":dict(nonblank),
        "nonidentifying_distinct_counts_for_keylike_fields":{
            col:len(vals) for col,vals in bycol_unique.items()},
        "date_field_year_scope_only":{
            h:{"min_year":min(v),"max_year":max(v),"parsed_count":len(v)}
            for h,v in col_minmax.items() if v},
        "malformed_csv_rows":malformed,
        "no_raw_source_rows_or_ids_emitted":True,
        "source_file_has_complete_survey_opportunity_ledger":"NOT_YET_AUTHENTICATED",
        "source_zeros_are_valid_nondetections":"NOT_YET_AUTHENTICATED",
        "no_species_detection_rates_computed":True,
        "no_spatial_coordinates_emitted":True,
    }
    return summary

def tests():
    mock=("SurveyID,siteID,observerID,SampleDate,speciesCall\n"
          "A,SENSITIVE_SITE,PERSON_1,2024-06-09,0\n"
          "B,SENSITIVE_SITE,PERSON_2,2024-06-09,2\n").encode()
    q=structural_receipt(mock)
    assert q["n_source_rows"]==2
    assert q["nonidentifying_distinct_counts_for_keylike_fields"]["siteID"]==1
    assert q["nonidentifying_distinct_counts_for_keylike_fields"]["observerID"]==2
    assert "SENSITIVE_SITE" not in json.dumps(q) and "PERSON_1" not in json.dumps(q)
    print("PASS: no individual survey IDs, site coordinates, observer labels or frog response values exported")

def main():
    tests()
    metadata=json.loads(get_public(META,1000000).decode("utf-8"))
    if metadata.get("id")!=ITEM:
        raise ValueError("OFFICIAL_ITEM_ID_NOT_EXPECTED")
    matches=[f for f in metadata.get("files",[])
             if f.get("name")==FILENAME and f.get("contentType")=="text/csv"]
    if len(matches)!=1:raise ValueError("SOURCE_FILE_NOT_UNIQUE")
    file=matches[0]
    if file.get("size")!=EXPECTED_BYTES:raise ValueError("SOURCE_FILE_SIZE_CHANGED")
    url=file.get("downloadUri") or ""
    if urlparse(url).hostname!="www.sciencebase.gov":
        raise ValueError("SOURCE_DOWNLOAD_NOT_OFFICIAL")
    raw=get_public(url,MAX_SIZE)
    if len(raw)!=EXPECTED_BYTES:raise ValueError("PUBLIC_CSV_BODY_MISMATCH")
    profile=structural_receipt(raw)
    rec={
        "status":"OFFICIAL_OPEN_USGS_ARMI_2024_CSV_SCHEMA_PROFILE",
        "official_release":"USGS Roth et al 2025, April 2026 ver 1.1",
        "doi":"https://doi.org/10.5066/P19ZCGWM",
        "item_id":ITEM,
        "raw_csv_original_filename":FILENAME,
        "raw_csv_size_bytes":len(raw),
        "raw_csv_sha256":hashlib.sha256(raw).hexdigest(),
        "source_retrieval":"unaltered public USGS ScienceBase metadata->file downloadUri; HTTPS only",
        "published_data_but_no_row_values_redistributed":True,
        "result":profile,
        "independent_from_frogcs_naamp_and_hoefer":True,
        "no_model_or_ecological_effect_calculated":True,
        "no_CEWH_email_sent":True,
        "rc6_main_not_modified":True,
    }
    dst=Path(OUTPUT)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    print("USGS_ARMI2024_SOURCE_SCHEMA "+json.dumps(rec,sort_keys=True))

if __name__=="__main__":main()
