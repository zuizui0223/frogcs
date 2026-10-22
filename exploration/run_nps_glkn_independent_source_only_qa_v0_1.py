#!/usr/bin/env python3
"""Audit official NPS GLKN 2016–2023 frog acoustic and temperature files.

Source-only profile. Do not inspect values in any frog detection, calling-index,
abundance, frequency, or species×survey outcome columns. Write only aggregate
key coverage, schema, official asset provenance and content hashes; never
redistribute raw downloaded data in GitHub Actions artifacts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path
from collections import Counter

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE="https://irma.nps.gov/DataStore/Reference/Profile/2320505"
FILES={
"GLKN_AmphibianMonitoringData_2016-2023.csv":"https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505",
"GLKN_AmphibianTemperatureData_2016-2023.csv":"https://irma.nps.gov/DataStore/DownloadFile/763378?Reference=2320505",
"GLKN_Amphibians_2016-2023_metadata.xml":"https://irma.nps.gov/DataStore/DownloadFile/763466?Reference=2320505"
}
CAP=60_000_000
REQ_HEADERS={
    "User-Agent":"frogcs-NPS-frog-acoustic-source-quality-check/0.1",
    "Accept":"text/csv,text/xml,application/octet-stream,*/*",
}
NORM=lambda x:re.sub(r"[^a-z0-9]","",str(x or "").lower().strip())

def select(fields,options):
    by={NORM(z):z for z in fields}
    for opt in options:
        if NORM(opt) in by:return by[NORM(opt)]
    return None

def retr(url):
    request=urllib.request.Request(url,headers=REQ_HEADERS)
    with urllib.request.urlopen(request,timeout=65) as response:
        final=response.geturl()
        host=urllib.parse.urlparse(final).hostname
        if not(host and host.endswith((".nps.gov",".gov",".amazonaws.com"))):
            raise RuntimeError("Unexpected NPS resource redirect host "+str(host))
        data=response.read(CAP+1)
        if len(data)>CAP:
            raise RuntimeError("Source file exceeds 60MB quality audit byte cap")
        if len(data)<150:
            raise RuntimeError("Source is too small to contain a valid survey")
        head=data[:350].lower().lstrip()
        if (b"<html" in head or b"<!doctype html" in head
           or b"captcha" in head or b"<title>" in head):
            raise RuntimeError("NPS resource resolves to HTML rather than data")
        return data,{"url":url,"http":response.status,
                     "byte_size":len(data),
                     "sha256":hashlib.sha256(data).hexdigest(),
                     "final_host":host,
                     "content_type":response.headers.get("Content-Type","unknown"),
                     "verified_not_HTML":True}

def header_csv(blob):
    try:
        decoded=blob[:50_000].decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded=blob[:50_000].decode("latin-1")
    first=decoded.splitlines()[0]
    cols=next(csv.reader([first]))
    if len(cols)<2 or len(set(cols))!=len(cols):
        raise RuntimeError("CSV duplicate or insufficient field names")
    return cols

def source_structure(main_bytes,temp_bytes):
    columns=header_csv(main_bytes)
    tempcols=header_csv(temp_bytes)
    fields={
        "park":select(columns,["ParkCode","Park","Park_Unit","ParkUnit","Unit_Code","Park_ID"]),
        "station":select(columns,["StationID","Station_ID","SiteID","Site_ID","LocationID",
                                  "Site","Station","Wetland_ID","MonitoringSiteID"]),
        "date":select(columns,["Date","SurveyDate","SampleDate","RecordingDate","ObsDate","DateTime"]),
        "time":select(columns,["Time","SurveyTime","RecordingTime","DateTime","StartDateTime"]),
        "year":select(columns,["Year","SurveyYear","CalendarYear"]),
        "event":select(columns,["SurveyID","VisitID","SampleID","RecordingID","EventID","RecordID","DeploymentID"]),
        "taxon":select(columns,["Species","Taxon","TaxonName","ScientificName",
                                 "SpeciesName","SpeciesCode","TaxonCode"]),
        "latitude":select(columns,["Latitude","Lat","DECIMAL_LATITUDE"]),
        "longitude":select(columns,["Longitude","Lon","Long","DECIMAL_LONGITUDE"]),
    }
    likely_outcomes=[z for z in columns if re.search(
        r"(^CI$|callindex|calling|detec|occur|count|presence|abund|frogcall|intens|amplitud)",
        z,re.I)]
    nonout=[z for k,z in fields.items() if z and z not in likely_outcomes]
    # Do not read any response field. Avoid using NPS per-station temperature
    # until metadata establishes whether it precedes or follows the frog survey.
    if not nonout:
        return {"status":"schema_unidentifiable",
                "frog_columns":columns,"temperature_columns":tempcols,
                "field_map":fields,"response_columns_not_read":True}
    # Entire source CSV is parsed with a strict USECOLS list of metadata
    # only. No acoustic outcome or numeric call intensity is materialized.
    data=pd.read_csv(io.BytesIO(main_bytes),usecols=nonout,low_memory=False,
                     encoding="utf-8-sig")
    tdata=pd.read_csv(io.BytesIO(temp_bytes),nrows=4,usecols=lambda name:True,
                      low_memory=False,encoding="utf-8-sig")
    # The temperature sample is not frog response. Summary exposes fields only.
    del tdata
    yearkey=fields["year"]
    datekey=fields["date"]
    year=None
    if yearkey:
        year=pd.to_numeric(data[yearkey],errors="coerce")
    elif datekey:
        year=pd.to_datetime(data[datekey],errors="coerce",utc=True).dt.year
    if year is None:
        years={"status":"missing_year"}
    else:
        years={
            "valid_rows_2016_2023":int(year.between(2016,2023).sum()),
            "year_range":[int(year.min()),int(year.max())] if year.notna().any() else None,
            "counts_by_year":{str(y):int(z) for y,z in
                              year.dropna().astype(int).value_counts().sort_index().items()},
            "missing_year_rows":int(year.isna().sum())
        }
    parks={"status":"unknown"}
    if fields["park"]:
        p=data[fields["park"]].dropna().astype(str)
        parks={"unique":int(p.nunique()),"labels":sorted(p.unique())[:30],
               "missing":int(data[fields["park"]].isna().sum())}
    station={"status":"unknown"}
    if fields["station"]:
        p=data[fields["station"]].dropna().astype(str)
        station={"unique":int(p.nunique()),"missing":int(data[fields["station"]].isna().sum())}
    species={"status":"wide_or_unresolved_taxon_schema"}
    if fields["taxon"]:
        ss=data[fields["taxon"]].dropna().astype(str).str.strip()
        species={"n":int(ss.nunique()),"labels":sorted(ss.unique())[:50],
                 "missing":int(data[fields["taxon"]].isna().sum())}
    # Candidate granularity: park × station × date × species; report
    # duplicate rate because multiple species and visits may coexist.
    key=[fields[k] for k in ["park","station","date","event","taxon"]
         if fields[k] is not None]
    if key:
        kframe=data[key].astype(str)
        duplicates=int(kframe.duplicated().sum())
    else:duplicates=None
    parks_sites=None
    if fields["park"] and fields["station"]:
        parks_sites=int(data[[fields["park"],fields["station"]]].drop_duplicates().shape[0])
    nrows=len(data)
    gatetaxa=species.get("labels",[])
    gate_names={
        "Lithobates clamitans":any("clamitans" in x.lower() for x in gatetaxa),
        "Lithobates catesbeianus":any(
             ("catesbeiana" in x.lower() or "catesbeianus" in x.lower())
             for x in gatetaxa)
    }
    out={
        "status":"source_grain_profiled",
        "main_n_rows":nrows,
        "frog_columns":columns,
        "temperature_columns":tempcols,
        "schema_field_map":fields,
        "response_candidate_columns_NOT_READ":likely_outcomes,
        "source_fields_read_only":sorted(nonout),
        "taxon_identifiers_only":species,
        "park_summary":parks,
        "station_summary":station,
        "park_station_count":parks_sites,
        "calendar":years,
        "candidate_key":key,
        "duplicate_candidate_key_extra":duplicates,
        "nps_source_14_taxa_expected_from_catalog":14,
        "focal_named_taxa_available_under_exact_names":gatetaxa if False else gate_names,
        "no_species_acoustic_response_values_read":True,
        "no_detection_absences_imputed":True,
        "no_multi_stop_or_same_night_assumptions":True,
        "source_model_readiness":"needs_response_blind_row_grain_finalization"
    }
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"nps_glkn_frog_source_only")
    args=parser.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    audit={"analysis":"nps_glkn_independent_amphibian_source_only_quality_v0_1",
           "source_title":"Great Lakes Amphibian Monitoring Bioacoustics Data Package",
           "NPS_reference":2320505,"published_date":"2026-09-30",
           "download_sources":FILES,"retrieved_files":{},"errors":{},
           "read_frog_detection_outcomes":False,
           "frozen_JAE_RC6_edited":False,
           "source_status":"not_checked"}
    blobs={}
    for name,url in FILES.items():
        try:
            blob,receipt=retr(url)
            blobs[name]=blob
            audit["retrieved_files"][name]=receipt
        except Exception as ex:
            audit["errors"][name]={"type":type(ex).__name__,
                                   "message":str(ex)[:600]}
    if all(name in blobs for name in FILES):
        try:
            audit["structure"]=source_structure(
                blobs["GLKN_AmphibianMonitoringData_2016-2023.csv"],
                blobs["GLKN_AmphibianTemperatureData_2016-2023.csv"])
            audit["source_status"]="source_schema_profiled_no_outcome"
        except Exception as ex:
            audit["source_status"]="source_schema_blocked"
            audit["schema_error"]={"type":type(ex).__name__,
                                   "message":str(ex)[:1000]}
    else:
        audit["source_status"]="official_source_unavailable"
    (args.outdir/"nps_glkn_source_only_result.json").write_text(
        json.dumps(audit,indent=2,sort_keys=True)+"\n")
    print("NPS_GLKN_SOURCE_AUDIT_BEGIN",flush=True)
    print(json.dumps(audit,sort_keys=True),flush=True)
    print("NPS_GLKN_SOURCE_AUDIT_END",flush=True)
    if audit["source_status"]!="source_schema_profiled_no_outcome":
        raise SystemExit("NPS independent detection source not ready; no frog biological result permitted")

if __name__=="__main__":
    main()
