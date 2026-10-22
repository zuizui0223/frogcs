#!/usr/bin/env python3
"""Response-blind external USGS 2024 Midwest ARMI nocturnal frog-call survey QA.

Official source CSV and XML bytes are checksum pinned to ScienceBase v1.1.
Parse ONLY visit metadata columns, NEVER Species/Number_heard/Comments.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

import pandas as pd

BASE="https://www.sciencebase.gov/catalog/file/get/68016413d4be0263cab109a8?f="
FILES={
 "survey":{
  "name":"ARMI_2024_cricket_frog_data_release_2025_v1.1.csv",
  "path":"__disk__13%2F46%2F9a%2F13469adf4b11c2b0e99797f0e5b47a992130010e",
  "bytes":235391,"MD5":"e201e24463d90e23c1f5f903e730e26c"},
 "metadata":{
  "name":"ARMI_2024_cricket_frog_data_release_2025_v1.1.xml",
  "path":"__disk__a7%2Fb9%2F9b%2Fa7b99b29ed1611b7666ec1012a0da1bef21f9c77",
  "bytes":41317,"MD5":"a5a72215d0cd2ad0a027de814edfa701"}
}
UNIT=["Project","Site","Date","Arrival_time","Observer","Method"]
COV=["Wind_Beaufort","Cloud_cover_percent"]
EXPECTED=["Species","Number_heard","Site_original","Compass_direction"]
EARLIEST="2024-06-06"
LATEST="2024-08-15"

def retrieve(p):
    url=BASE+p["path"]
    r=urllib.request.Request(url,headers={
       "User-Agent":"frogcs-USGS-Midwest-ARMI-2024-data-quality/0.1",
       "Accept":"text/csv,application/xml,text/plain,*/*"})
    with urllib.request.urlopen(r,timeout=60) as f:
        if not f.geturl().startswith("https://www.sciencebase.gov/catalog/file/get/"):
            raise RuntimeError("Official USGS source unexpectedly redirected")
        blob=f.read(2_000_000)
        if len(blob)!=p["bytes"]:
            raise RuntimeError(f"Official survey source bytes wrong: {len(blob)} != {p['bytes']}")
        if blob.lstrip().lower().startswith((b"<html",b"<!doctype")):
            raise RuntimeError("HTML source access error")
        md5=hashlib.md5(blob).hexdigest()
        if md5!=p["MD5"]:raise RuntimeError("ScienceBase official MD5 checksum mismatch")
        return blob,{
            "file_name":p["name"],"bytes":len(blob),"MD5_official":md5,
            "SHA256":hashlib.sha256(blob).hexdigest(),
            "url":url,"status":f.status,
            "official_source_verified":True}

def inspect_metadata_only(survey,xml):
    header=next(csv.reader([survey.split(b"\n")[0].decode("utf-8-sig")]))
    if len(header)<10 or len(header)!=len(set(header)):
        raise RuntimeError("Not recognizable comma-delimited USGS source")
    if not set(UNIT+COV+EXPECTED).issubset(set(header)):
        raise RuntimeError("Required survey visit/source taxonomy columns absent")
    original=pd.read_csv(io.BytesIO(survey),usecols=UNIT+COV,low_memory=False,dtype="string")
    valid=original.copy()
    for name in UNIT+COV:
        valid[name]=valid[name].str.strip()
    null={name:int(valid[name].isna().sum()|(valid[name]=="").fillna(False).sum())
          for name in []}
    null={col:int((valid[col].isna() | valid[col].fillna("").eq("")).sum()) for col in UNIT+COV}
    complete=valid.dropna(subset=UNIT).copy()
    for x in UNIT:complete=complete[complete[x].ne("")]
    dates=pd.to_datetime(complete["Date"],format="%Y-%m-%d",errors="coerce")
    good=dates.between(pd.Timestamp(EARLIEST),pd.Timestamp(LATEST))
    n_invalid_dates=int((~good).sum())
    complete=complete[good].copy()
    complete["parsed_Date"]=dates.loc[complete.index]
    # All species recorded on one visit share these 6 immutable fields.
    event=complete[UNIT].drop_duplicates()
    cnt=complete.groupby(UNIT).size()
    sites=complete[["Project","Site"]].drop_duplicates()
    bysite=event.groupby(["Project","Site"]).size()
    byproj=event.groupby("Project").size()
    unique_observer_site=event.groupby(["Project","Site"])["Observer"].nunique()
    n_repeat=int((bysite>=2).sum())
    n_events=int(len(event))
    denom=valid[UNIT].drop_duplicates().shape[0]
    n_invalid=int(len(valid)-len(complete))
    # No Species source column is read. Duplicate event rows are normal
    # (one row per audible species), not evidence of duplicate visits.
    notes=xml.decode("utf-8",errors="replace")
    check={
        "source_metadata_describes_all_species_heard":("All anurans heard were recorded" in notes or
            "All anurans heard were recorded" in notes.replace("\n"," ")),
        "source_metadata_describes_empty_survey":"No anurans were heard during this survey" in notes,
        "original_csv_header_includes_species":"Species" in header,
        "raw_detection_outcomes_not_read":True}
    # Metadata source is XML and the original stage expects the claim to
    # appear therein exactly. If not, stop before adding zeros.
    gate={
      "site_count_ge40":len(sites)>=40,
      "event_count_ge150":len(event)>=150,
      "at_least_two_projects":len(byproj)>=2,
      "sites_with_two_or_more_visits_ge20":n_repeat>=20,
      "visit_key_completeness_ge90pct":len(complete)/len(valid)>=.9,
      "metadata_documents_complete_detected_species":check["source_metadata_describes_all_species_heard"],
      "metadata_documents_explicit_empty_survey":check["source_metadata_describes_empty_survey"]
    }
    return {
       "analysis":"USGS_Midwest_ARMI_2024_pinned_source_only_v0_1",
       "data_version":"v1.1 revised 2026-04-02",
       "survey_source_format":"positive_list_per_survey_event",
       "all_column_names":header,"visit_key_columns":UNIT,
       "covariate_field_names":COV,
       "source_metadata_semantics":check,
       "n_record_rows":len(original),
       "n_valid_visit_metadata_rows":len(complete),
       "n_invalid_visit_metadata_rows":n_invalid,
       "invalid_formatted_dates":n_invalid_dates,
       "n_independent_unique_survey_visits":n_events,
       "n_project_site_groups":int(len(sites)),
       "n_coverage_project_groups":int(len(byproj)),
       "n_sites_with_repeat_visits":n_repeat,
       "visit_rows_per_event":{str(k):int(v) for k,v in cnt.value_counts().sort_index().items()},
       "site_survey_visits_quantiles":{
            str(p):float(bysite.quantile(p)) for p in (0,.25,.5,.75,1)},
       "surveys_per_project_metadata_only":{str(p):int(n) for p,n in byproj.items()},
       "n_project_sites_with_both_observers":int((unique_observer_site>=2).sum()),
       "fields_key_missing_rows":null,
       "min_date":str(complete.parsed_Date.min().date()) if len(complete) else None,
       "max_date":str(complete.parsed_Date.max().date()) if len(complete) else None,
       "pre_outcome_gates":gate,
       "source_only_eligible":bool(all(gate.values())),
       "species_detection_values_read":False,
       "number_heard_values_read":False,
       "no_RAW_USGS_file_uploaded":True}
 
def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--outdir",type=Path,default=Path("build/armi_2024_source_only"))
    cfg=arg.parse_args()
    cfg.outdir.mkdir(parents=True,exist_ok=True)
    out={"analysis":"independent_USGS_ARMI_2024_source_gate_v0_1",
         "source_item_id":"68016413d4be0263cab109a8",
         "contract":"exploration/ARMI_2024_INDEPENDENT_FROG_SOURCE_CONTRACT_V0_1.md",
         "source_release_verified":False,"frog_detection_values_read":False,
         "source_status":"not_attempted","files":{},"RC6_edited":False}
    try:
        csvdata,info=retrieve(FILES["survey"])
        out["files"]["survey"]=info
        xml,metadata_info=retrieve(FILES["metadata"])
        out["files"]["metadata"]=metadata_info
        out["source_release_verified"]=True
        out["preflight"]=inspect_metadata_only(csvdata,xml)
        out["source_status"]="source_only_preflight_verified"
    except Exception as e:
        out["source_status"]="unavailable_or_QA_failed"
        out["source_error_type"]=type(e).__name__
        out["source_error_message"]=str(e)[:600]
    (cfg.outdir/"source_only_receipt.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("ARMI_2024_SOURCE_ONLY_BEGIN",flush=True)
    print(json.dumps(out,sort_keys=True),flush=True)
    print("ARMI_2024_SOURCE_ONLY_END",flush=True)
    if out["source_status"]!="source_only_preflight_verified":
        raise SystemExit("USGS source integrity/metadata failed, no biological outcome opened")
if __name__=="__main__":
    main()
