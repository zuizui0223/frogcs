#!/usr/bin/env python3
"""Independent NPS GLKN frog exact-file source-only survey-panel eligibility QA.

Reads ONLY NPS metadata/keys: FileName,ParkCode,SiteLocation,StartTime,
EventYear,ScientificName,SpeciesCode,Hydroperiod,AvgTemperature_C.
Never reads SurveyorDetectedStatus, ManualCIV, SoftwareDetectedStatus or audio
quality fields. Retains no original raw CSV/XML file in GitHub artifacts.
"""
from __future__ import annotations

import csv
import io
import hashlib
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC={
"frog":{"url":"https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505",
        "bytes":68581307,"max_bytes":90000000},
"metadata":{"url":"https://irma.nps.gov/DataStore/DownloadFile/763466?Reference=2320505",
            "bytes":131226,"sha256":"a37af87cd333168f52503f823041c4ab578b6968333c7d5f315604222ae4eb8f",
            "max_bytes":2000000},
}
FIELDS=[
"FileName","ParkCode","SiteLocation","StartTime","EventYear",
"ScientificName","SpeciesCode","Hydroperiod","AvgTemperature_C"]
RESPONSE_FIELDS=[
"SoftwareDetectedStatus","SurveyorDetectedStatus","ManualCIV",
"DurationMax_s","ScoreMax","LevelMax_dB"]
EVENT=["ParkCode","SiteLocation","FileName","StartTime"]
TAX="ScientificName"

def source(url,size,cap,sha=None):
    req=urllib.request.Request(url,headers={
        "User-Agent":"frogcs-NPS_GLKN_source_keys_only_v0.2",
        "Accept":"application/octet-stream,text/csv,application/xml,*/*"})
    with urllib.request.urlopen(req,timeout=120) as resp:
        host=urllib.parse.urlparse(resp.geturl()).hostname or ""
        if not host.endswith(".nps.gov"):
            raise RuntimeError("NPS asset redirected to an unverified host "+host)
        buf=resp.read(cap+1)
        if len(buf)>cap:raise RuntimeError("Source exceeds predeclared corrected byte cap")
        if len(buf)!=size:raise RuntimeError(f"Source size drift: {len(buf)} != {size}")
        if b"<html" in buf[:512].lower():raise RuntimeError("Source is HTML, not original NPS data")
        digest=hashlib.sha256(buf).hexdigest()
        if sha and digest!=sha:
            raise RuntimeError("Previously frozen NPS metadata SHA drift")
        receipt={"url":url,"http_status":resp.status,
                 "n_bytes":len(buf),"sha256":digest,
                 "final_host":host,"content_type":resp.headers.get("content-type"),
                 "no_raw_file_export":True}
    return buf,receipt

def read_metadata_dictionary(blob):
    text=blob.decode("utf-8-sig",errors="replace")
    out={}
    for name in FIELDS+RESPONSE_FIELDS:
        m=re.search(re.escape(name),text,re.I)
        if m:
            start=max(0,m.start()-120);end=min(len(text),m.end()+480)
            excerpt=text[start:end]
            excerpt=re.sub(r"<[^>]*>"," ",excerpt)
            excerpt=" ".join(excerpt.split())
            out[name]={"name_appears":True,"XML_context_excerpt":excerpt[:440]}
        else:
            out[name]={"name_appears":False}
    return out

def run_structural_preflight(raw_bytes,metadata):
    firstline=raw_bytes[:7000].decode("utf-8-sig").splitlines()[0]
    names=next(csv.reader([firstline]))
    if len(set(names))!=len(names):raise RuntimeError("Duplicate source headers")
    if not set(FIELDS+RESPONSE_FIELDS).issubset(names):
        raise RuntimeError(f"Official NPS main metadata fields missing: {set(FIELDS+RESPONSE_FIELDS)-set(names)}")
    # Strict usecols prevents reading acoustic detection values.
    d=pd.read_csv(io.BytesIO(raw_bytes),usecols=FIELDS,low_memory=False,
                  dtype={c:"string" for c in FIELDS if c!="AvgTemperature_C"})
    for col in FIELDS:
        if col not in d.columns:raise RuntimeError("Pandas source metadata projection drift")
    for name in FIELDS:
        if name!="AvgTemperature_C":
            d[name]=d[name].astype("string").str.strip()
    year=pd.to_numeric(d.EventYear,errors="coerce")
    scope=Counter()
    scope["n_raw_taxon_record_rows"]=len(d)
    for col in EVENT+[TAX,"SpeciesCode","Hydroperiod","AvgTemperature_C","EventYear"]:
        scope["null_or_empty_"+col]=int(d[col].isna().sum()) if col=="AvgTemperature_C" else int(
            (d[col].isna() | (d[col].astype("string")=="")).sum())
    valid=d.dropna(subset=EVENT+[TAX]).copy()
    for col in EVENT+[TAX]:
        valid=valid[valid[col].str.len()>0]
    valid_year=year.loc[valid.index]
    valid=valid[valid_year.between(2016,2023)]
    invalid=len(d)-len(valid)
    # A unique event×taxon row is *not assumed*. Duplicated keys indicate
    # repeated detection annotations or multiple subrecordings; do not collapse
    # them by silently using "any detected" before original field codebook QA.
    duplicate_key=EVENT+[TAX]
    dup=int(valid.duplicated(duplicate_key).sum())
    groups=valid.groupby(EVENT,sort=False,dropna=False)
    n_taxon=groups[TAX].nunique().reset_index(name="n_taxa_unique")
    num_rows=groups.size().reset_index(name="n_rows")
    joint=n_taxon.merge(num_rows,on=EVENT,validate="one_to_one")
    parks=sorted(valid.ParkCode.unique().tolist())
    species=sorted(valid.ScientificName.unique().tolist())
    # Taxon field identifiers are allowed in source-only audit, never detections.
    taxon_rows=valid[TAX].value_counts().sort_index()
    geo=valid[["ParkCode","SiteLocation"]].drop_duplicates()
    rec_park_year=valid[["ParkCode","EventYear","FileName","SiteLocation","StartTime"]].drop_duplicates()
    # Hydroperiod and temperature are the *survey-event covariate* candidates;
    # verify that within recording event they do not conflict across species.
    hydromodes=valid.groupby(EVENT,sort=False)["Hydroperiod"].nunique(dropna=False)
    tmodes=valid.groupby(EVENT,sort=False)["AvgTemperature_C"].nunique(dropna=False)
    n_total_species=len(species)
    alltax=(joint.n_taxa_unique==n_total_species)
    # Distinct species names may represent taxa not surveyed in some parks.
    group8=(joint.n_taxa_unique>=8)
    explicit=joint[(joint.n_taxa_unique==n_total_species) &
                   (joint.n_rows==n_total_species)]
    pair_names={
      "bullfrog":{"scientific_name_candidates":[x for x in species if
        "catesbeian" in x.lower()],
        "confirmed_taxon_labels":None},
      "green_frog":{"scientific_name_candidates":[x for x in species if
        "clamitans" in x.lower()],
        "confirmed_taxon_labels":None}
    }
    keygate={
      "min_total_100_recordings":int(len(joint))>=100,
      "min_20_sites":len(geo)>=20,
      "min_2_park_units":len(parks)>=2,
      "both_named_species_identifiers":all(len(x["scientific_name_candidates"])>0
                                           for x in pair_names.values()),
      "some_full_taxon_panel_recordings":len(explicit)>=80,
      "no_duplicated_event_taxon_rows":dup==0,
      "at_least_40_full_panel_sites":len(explicit[["ParkCode","SiteLocation"]].drop_duplicates())>=40,
      "consistent_hydroperiod_within_file":int((hydromodes>1).sum())==0
    }
    year_counts=rec_park_year.groupby("EventYear").size()
    q={
      "analysis":"NPS_GLKN_frog_source_key_grain_count_blind_v0_2",
      "required_columns":FIELDS,
      "all_columns":names,
      "response_values_read":False,
      "response_field_names_unread":RESPONSE_FIELDS,
      "n_rows":len(d),
      "n_invalid_event_taxon_or_year_rows":invalid,
      "original_event_key":EVENT,
      "event_taxon_key":duplicate_key,
      "n_duplicate_event_taxon_rows_excess":dup,
      "n_unique_recording_events":int(len(joint)),
      "n_site_locations_across_park":int(len(geo)),
      "n_parks":len(parks),
      "park_code_labels":parks,
      "n_taxon_units":n_total_species,
      "taxon_names":species,
      "taxon_row_counts_without_detection":{str(k):int(v) for k,v in taxon_rows.items()},
      "n_recordings_with_all_taxon_names_present":int(alltax.sum()),
      "n_recordings_with_at_least_8_taxon_rows":int(group8.sum()),
      "n_nonduplicated_full_panel_recordings":int(len(explicit)),
      "n_full_panel_sites":int(len(explicit[["ParkCode","SiteLocation"]].drop_duplicates())),
      "recording_taxon_rows_distribution":{
         str(int(k)):int(v) for k,v in joint.n_taxa_unique.value_counts().sort_index().items()},
      "recording_rows_distribution":{
         str(int(k)):int(v) for k,v in joint.n_rows.value_counts().sort_index().items()},
      "years_of_recordings":{
         str(k):int(v) for k,v in year_counts.items()},
      "n_recordings_with_conflicting_Hydroperiod_metadata":int((hydromodes>1).sum()),
      "n_recordings_with_conflicting_AvgTemperature_metadata":int((tmodes>1).sum()),
      "focal_taxon_identifiers":pair_names,
      "metadata_field_descriptions":metadata,
      "source_gates":keygate,
      "all_source_structure_gates_pass":all(keygate.values()),
      "source_schema_is_a_same_event_observation_not_NAAMP_routes":True,
      "no_detection_outcomes_imputed":True,
      "no_species_detection_data_read":True}
    return q

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"nps_glkn_source_v02")
    args=parser.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    receipt={"analysis":"NPS_GLKN_independent_source_metadata_v0_2",
            "contract":"exploration/NPS_GLKN_INDEPENDENT_SOURCE_SCOPE_EXTENSION_V0_2.md",
            "source_reference":2320505,
            "files":{},"read_detection_values":False,
            "frozen_RC6_edited":False,"source_status":"not_yet_checked"}
    try:
        frog,receipt["files"]["frog"]=source(
            SRC["frog"]["url"],SRC["frog"]["bytes"],SRC["frog"]["max_bytes"])
        metadata,receipt["files"]["metadata"]=source(
            SRC["metadata"]["url"],SRC["metadata"]["bytes"],
            SRC["metadata"]["max_bytes"],SRC["metadata"]["sha256"])
        receipt["structure"]=run_structural_preflight(
            frog,read_metadata_dictionary(metadata))
        receipt["source_status"]="source_only_metadata_and_grain_checked"
    except Exception as ex:
        receipt["source_status"]="source_only_quality_blocked"
        receipt["error"]={"type":type(ex).__name__,"message":str(ex)[:1200]}
    (args.outdir/"nps_glkn_source_v02_result.json").write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("NPS_GLKN_SOURCE_V02_BEGIN",flush=True)
    print(json.dumps(receipt,sort_keys=True),flush=True)
    print("NPS_GLKN_SOURCE_V02_END",flush=True)
    if receipt["source_status"]!="source_only_metadata_and_grain_checked":
        raise SystemExit("NPS full source and schema quality gate failed; frog response values not read")

if __name__=="__main__":main()
