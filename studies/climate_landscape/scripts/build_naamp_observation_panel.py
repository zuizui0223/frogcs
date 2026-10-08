#!/usr/bin/env python3
"""Reconstruct response-blind 2001-2015 NAAMP surveyed stop opportunities.

Reads ONLY Runs.csv and Stops.csv; NEVER Counts.csv or species outcomes.
This matches the *run opportunity filters* from the RC6 discovery code, then
requires physical SiteID to enable (separate) independent coordinate checking.
Metadata missingness is counted rather than silently imputed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_PINS={
    "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
    "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
}

def _year(value):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(value or ""))
    return int(m.group(1)) if m else None

def _date(value):
    s=str(value or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%Y/%m/%d"):
        try:
            return pd.Timestamp(pd.to_datetime(s,format=fmt,errors="raise")).normalize()
        except (ValueError,TypeError):
            pass
    return pd.NaT

def make(runs:pd.DataFrame,stops:pd.DataFrame)->tuple[pd.DataFrame,dict]:
    run_cols={"RunID","SurveyDate","SurveyYear","UnifiedProtocol","RouteNumber","RouteType",
              "State","RunNumber","DaysSinceRain","TempScale"}
    stop_cols={"RunID","StopNumber","SkippedStop","SiteID","AirTemp"}
    for df,cols,name in ((runs,run_cols,"Runs"),(stops,stop_cols,"Stops")):
        missing=cols-set(df.columns)
        if missing:raise ValueError(f"{name} missing {sorted(missing)}")
    eligible={}; date_error=0
    for r in runs.to_dict(orient="records"):
        yr=_year(r["SurveyYear"]) or _year(r["SurveyDate"])
        survey=_date(r["SurveyDate"])
        if yr is None or pd.isna(survey) or survey.year!=yr:
            date_error+=1
            continue
        if not 2001<=yr<=2015:
            continue
        rid=str(r["RunID"]).strip()
        state=str(r["State"]).strip()
        route=str(r["RouteNumber"]).strip()
        runno=str(r["RunNumber"]).strip()
        rtype=str(r["RouteType"]).strip()
        if str(r["UnifiedProtocol"]).strip()!="1" or not rid or not state or not route or not rtype or runno not in {"1","2","3","4"}:
            continue
        try:rain=float(r["DaysSinceRain"])
        except (ValueError,TypeError):continue
        if not np.isfinite(rain) or not 0<=rain<=180:continue
        if rid in eligible:raise ValueError("duplicate RunID")
        eligible[rid]=dict(run_id=rid,state=state,route_number=route,route_id=f"{state}:{route}",
                           route_type=rtype,survey_round=int(runno),survey_year=yr,
                           survey_date=survey.strftime("%Y-%m-%d"),
                           temp_scale=str(r["TempScale"]).strip())
    grouped={r:[] for r in eligible}
    for s in stops.to_dict(orient="records"):
        rid=str(s["RunID"]).strip()
        if rid not in eligible or str(s["SkippedStop"]).strip()!="0":continue
        grouped[rid].append(s)
    output=[]
    metadata_missing=0; nonstandard_stops=0; n_run_geometry_eligible=0
    for rid,r in eligible.items():
        ss=grouped[rid]
        stop_numbers={str(s["StopNumber"]).strip() for s in ss if str(s["StopNumber"]).strip()}
        if len(stop_numbers)!=10:
            nonstandard_stops+=1
            continue
        temp=[]
        for s in ss:
            try:t=float(s["AirTemp"])
            except (ValueError,TypeError):continue
            if r["temp_scale"]=="F":t=(t-32)*5/9
            elif r["temp_scale"]!="C":continue
            if np.isfinite(t):temp.append(t)
        if len(temp)<8 or not -10 <= float(np.mean(temp)) <=45:
            continue
        # Return a separate metadata-only physical-site eligibility set.
        # DO NOT infer 0 calling from lack of positive Counts.csv rows here.
        if len(ss)!=10 or any(not str(s["SiteID"]).strip() for s in ss):
            metadata_missing+=1
            continue
        ids=[str(s["SiteID"]).strip() for s in ss]
        if len(set(ids))!=10:
            metadata_missing+=1
            continue
        for s in ss:
            stop=str(s["StopNumber"]).strip()
            output.append({**{k:v for k,v in r.items() if k!="temp_scale"},
                           "site_id":str(s["SiteID"]).strip(),
                           "stop_number":stop})
        n_run_geometry_eligible+=1
    columns=["run_id","state","route_number","route_id","route_type","survey_round",
             "survey_year","survey_date","site_id","stop_number"]
    df=pd.DataFrame(output,columns=columns)
    if not df.empty:
        if df.duplicated(["run_id","route_id","site_id"]).any():
            raise ValueError("duplicate physical-site survey opportunity")
        if df.groupby("run_id").size().ne(10).any():
            raise ValueError("not exactly ten eligible physical sites per survey run")
    receipt={"n_filtered_run_candidates_before_stop_checks":len(eligible),
             "n_complete_ten_stop_runs_with_identifiable_physical_sites":n_run_geometry_eligible,
             "n_site_visits":len(df),
             "n_distinct_route_site_keys":int(df[["route_id","site_id"]].drop_duplicates().shape[0]),
             "n_distinct_routes":df.route_id.nunique(),
             "n_invalid_date_rows":date_error,
             "n_runs_incomplete_number_of_stops":nonstandard_stops,
             "n_runs_with_missing_or_repeated_site_id":metadata_missing,
             "called_species_records_opened":False,
             "counts_csv_opened":False,
             "external_coordinate_verification_performed":False,
             "not_identical_to_published_rc6_cohort_until_crosschecked":True,
             "study":"separate climate landscape acoustic-site monitoring panel"}
    return df,receipt

def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runs",required=True)
    ap.add_argument("--stops",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--receipt",required=True)
    ap.add_argument("--allow-unpinned-source",action="store_true",help="Only for synthetic fixtures, never for publication inputs")
    a=ap.parse_args()
    names={"Runs.csv":a.runs,"Stops.csv":a.stops}
    sources={name:sha256(path) for name,path in names.items()}
    if not a.allow_unpinned_source and sources!=SOURCE_PINS:
        raise ValueError("pinned NAAMP source checksum mismatch")
    def read(p):return pd.read_csv(p,dtype=str,keep_default_na=False)
    table,receipt=make(read(a.runs),read(a.stops))
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    table.to_csv(out,index=False)
    receipt["source_sha256"]=sources
    receipt["output_sha256"]=sha256(out)
    rp=Path(a.receipt);rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(receipt,indent=2,sort_keys=True,default=int)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True,default=int))
if __name__=="__main__":main()
