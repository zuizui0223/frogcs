#!/usr/bin/env python3
"""Quality-only diagnosis of repeat Species values under an unchanged survey key.

No bullfrog-greenfrog association, model, joint occurrence or predictive
outcome is computed. Result contains counts and diagnostic field names only.
"""
from __future__ import annotations
import csv,io,json,hashlib
from pathlib import Path
import pandas as pd
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
   "armi_original_source",ROOT/"exploration/run_armi_2024_source_only_qa_v0_1.py")
src=importlib.util.module_from_spec(spec);spec.loader.exec_module(src)
EVENT=["Project","Site","Date","Arrival_time","Observer","Method"]
INPUTS=EVENT+["Species","Number_heard","Compass_direction",
              "Wind_Beaufort","Cloud_cover_percent","Comments",
              "Latitude_WGS84","Longitude_WGS84","Site_original"]
META=["Wind_Beaufort","Cloud_cover_percent","Latitude_WGS84",
      "Longitude_WGS84","Site_original"]
REC=["Number_heard","Compass_direction","Comments"]
def main():
  b,sha=src.retrieve(src.FILES["survey"])
  assert sha["SHA256"]=="dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4"
  d=pd.read_csv(io.BytesIO(b),usecols=INPUTS,dtype="string",
                keep_default_na=False,low_memory=False)
  for c in INPUTS:d[c]=d[c].str.strip()
  extra=int(d.duplicated(EVENT+["Species"]).sum())
  exact=int(d.duplicated(INPUTS).sum())
  inconsistent_meta={}
  for c in META:
     per=d.groupby(EVENT)[c].nunique(dropna=False)
     inconsistent_meta[c]=int((per>1).sum())
  dup=d[d.duplicated(EVENT+["Species"],keep=False)].copy()
  dg=dup.groupby(EVENT+["Species"])
  varying={}
  for c in INPUTS:
     if c in EVENT+["Species"]:continue
     varying[c]=int((dg[c].nunique(dropna=False)>1).sum())
  project=dup.groupby("Project").agg(n_rows=("Species","size")).reset_index()
  by_species=dup.groupby("Species").size()
  n_repeat_events=len(dup[EVENT].drop_duplicates())
  n_repeat_specieskeys=len(dup[EVENT+["Species"]].drop_duplicates())
  # Safety: sensitive raw Site and event IDs are never logged.
  out={
    "analysis":"2024_USGS_ARMI_duplicate_species_survey_key_source_QA_v0_1",
    "source_sha":sha["SHA256"],"original_rows":len(d),
    "original_unique_visit_sixpart_keys":int(len(d[EVENT].drop_duplicates())),
    "same_species_same_survey_extra_rows":extra,
    "duplicate_survey_species_groups":n_repeat_specieskeys,
    "survey_events_with_same_species_extra_rows":n_repeat_events,
    "entire_row_exact_duplicate_extras":exact,
    "project_duplicate_rows":{
       str(r.Project):int(r.n_rows) for r in project.itertuples(index=False)},
    "species_label_duplicate_rows":{
       str(k):int(v) for k,v in by_species.items()},
    "fields_varying_among_same_species_same_survey_groups":varying,
    "within_survey_metadata_conflict_counts":inconsistent_meta,
    "number_heard_and_compass_differences_are_record_detail_not_new_surveys":None,
    "frog_pair_joint_outcomes_read":False,
    "no_species_association_test_computed":True,
    "candidate_binary_any_species_by_survey_aggregation_only_pending_contract":True
  }
  Path("build/armi_dup_audit").mkdir(parents=True,exist_ok=True)
  Path("build/armi_dup_audit/receipt.json").write_text(
      json.dumps(out,indent=2,sort_keys=True)+"\n")
  print("ARMI_DUP_QA_BEGIN",flush=True)
  print(json.dumps(out,sort_keys=True),flush=True)
  print("ARMI_DUP_QA_END",flush=True)
if __name__=="__main__":main()
