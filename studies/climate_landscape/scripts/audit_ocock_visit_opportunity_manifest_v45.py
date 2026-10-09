#!/usr/bin/env python3
"""Ocock original 343-visit opportunity contract v4.5 — METADATA ONLY.

Never reads frog species, calls, eggs, metamorphs, locations, observers or
hydrology values. Authorized-only source manifests are run locally, not
committed. A count match is structural, NOT source provenance or replication.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path

FIELDS=("physical_wetland_alias","survey_night_alias","survey_visit_alias",
        "survey_date","survey_status","audio_method",
        "auditory_effort_minutes","source_form_version")
STATUS={"COMPLETED","NOT_VISITED","ABORTED"}
METHODS={"FIVE_MIN_LISTEN","OTHER","NOT_ASSESSED"}
EXPECTED={"sites":29,"completed_visits":343,"nights":95}
MISSING={"","NA","N/A","UNKNOWN"}

def audit(raw:str)->dict:
    rd=csv.DictReader(io.StringIO(raw))
    heads=rd.fieldnames or []
    if len(set(heads))!=len(heads) or set(heads)!=set(FIELDS):
        raise ValueError("metadata-only exact header contract; no species/call/location fields")
    rows=list(rd)
    if not rows:
        raise ValueError("empty source opportunity panel")
    unique_keys=set()
    sites=set()
    nights=set()
    outcomes=Counter()
    complete=set()
    visit_ids=set()
    unknown_5min=0
    outside=0
    for r in rows:
        if None in r or any(v is None for v in r.values()):
            raise ValueError("ragged CSV row")
        site=r["physical_wetland_alias"].strip()
        night=r["survey_night_alias"].strip()
        visit=r["survey_visit_alias"].strip()
        date=r["survey_date"].strip()
        status=r["survey_status"].strip()
        method=r["audio_method"].strip()
        version=r["source_form_version"].strip()
        if not all((site,night,visit,version)):
            raise ValueError("incomplete source-defined alias or original form version")
        if any(len(s)>100 for s in (site,night,visit,version)):
            raise ValueError("unexpected ID length")
        try:
            d=dt.date.fromisoformat(date)
        except ValueError as e:
            raise ValueError("survey_date must be ISO date") from e
        if not 2015<=d.year<=2020:
            outside+=1
        if status not in STATUS or method not in METHODS:
            raise ValueError("unrecognized survey state or auditory method")
        if visit in visit_ids:
            raise ValueError("duplicate original visit key; no counting multiple species as visits")
        visit_ids.add(visit)
        key=(site,night,visit)
        if key in unique_keys:
            raise ValueError("duplicate site-night-visit opportunity")
        unique_keys.add(key)
        sites.add(site)
        nights.add(night)
        outcomes[status]+=1
        if status=="COMPLETED":
            if method!="FIVE_MIN_LISTEN":
                raise ValueError("completed original acoustic study visits must be source-verified FIVE_MIN_LISTEN")
            effort=r["auditory_effort_minutes"].strip()
            if effort.upper() in MISSING:
                unknown_5min+=1
            else:
                try:e=float(effort)
                except ValueError as x:raise ValueError("bad auditory effort") from x
                if not math.isfinite(e) or e<=0:
                    raise ValueError("invalid auditory effort")
                if abs(e-5.0)>0.001:
                    raise ValueError("cannot silently pool other acoustic protocols into published 5-min design")
            complete.add(visit)
        elif method=="FIVE_MIN_LISTEN" and status=="NOT_VISITED":
            raise ValueError("not-visited cannot be recorded as completed frog listening method")
        if status!="COMPLETED" and r["auditory_effort_minutes"].strip().upper() not in MISSING:
            raise ValueError("aborted or missed effort not a complete 5-min visit")
    count={"sites":len(sites),"completed_visits":len(complete),"nights":len(nights)}
    status="STRUCTURAL_MATCH_TO_PUBLISHED_COUNTS" if count==EXPECTED else "INCOMPLETE_OR_DIFFERENT_VERSION"
    if unknown_5min:
        status="EFFORT_INCOMPLETE"
    if outside:
        status="OUTSIDE_PUBLISHED_YEAR_FRAME"
    return {
        "analysis":"ocock_2024_original_survey_opportunity_structure_v45",
        "source":"source-extract metadata-only format, not publication response values",
        "published_denominator_targets":EXPECTED,
        "observed_opportunity_counts":count,
        "n_rows":len(rows),
        "status_counts":dict(outcomes),
        "completed_visits_missing_quantified_5min_effort":unknown_5min,
        "outside_2015_2020_years":outside,
        "status":status,
        "raw_source_provenance_verified":False,
        "original_frog_category_codebook_verified":False,
        "sighted_absence_equates_acoustic_zero_verified":False,
        "physical_wetland_continuity_verified":False,
        "hydroperiod_and_metamorph_linkage_verified":False,
        "model_or_effect_calculated":False,
        "frog_response_read":False,
        "sensitive_identifiers_in_receipt":False,
        "rc6_unchanged":True,
        "note":"Count match alone never certifies original 343 real surveys; attestation and independent source crosswalk required."
    }

def synthetic_tests():
    h=",".join(FIELDS)+"\n"
    dates=[(dt.date(2015,9,1)+dt.timedelta(days=k)).isoformat() for k in range(95)]
    rows=[
        f"S{i%29},N{i%95},V{i},{dates[i%95]},COMPLETED,FIVE_MIN_LISTEN,5,original_form"
        for i in range(343)]
    src=h+"\n".join(rows)+"\n"
    z=audit(src)
    assert z["status"]=="STRUCTURAL_MATCH_TO_PUBLISHED_COUNTS"
    assert z["observed_opportunity_counts"]==EXPECTED
    assert z["raw_source_provenance_verified"] is False
    negatives=[
        src.replace("V0,","V1,",1),
        src.replace("COMPLETED,FIVE_MIN_LISTEN,5","COMPLETED,FIVE_MIN_LISTEN,6",1),
        src.replace("COMPLETED,FIVE_MIN_LISTEN,5","COMPLETED,FIVE_MIN_LISTEN,0",1),
        src.replace("COMPLETED,FIVE_MIN_LISTEN,5","COMPLETED,FIVE_MIN_LISTEN,nan",1),
        src.replace("2015-09-01","2014-09-01",1),
        h.replace("source_form_version","species,source_form_version")+
            "S0,N0,V0,2015-09-01,COMPLETED,FIVE_MIN_LISTEN,5,Frog,form\n",
        src.replace("COMPLETED,FIVE_MIN_LISTEN,5",
                    "NOT_VISITED,FIVE_MIN_LISTEN,5",1),
        src.replace("COMPLETED,FIVE_MIN_LISTEN,5",
                    "ABORTED,NOT_ASSESSED,5",1),
    ]
    # First duplicate/error/invalid inputs must fail or produce explicit
    # NOT-MATCH status, never a false source-authenticated pass.
    for i,bad in enumerate(negatives):
        try:
            v=audit(bad)
            if v["status"]=="STRUCTURAL_MATCH_TO_PUBLISHED_COUNTS":
                raise AssertionError(f"negative fixture {i} matched")
        except ValueError:
            pass
    # A missing completed visit is NOT a biological zero and cannot match.
    partial=audit(h+"\n".join(rows[:-1])+"\n")
    assert partial["status"]=="INCOMPLETE_OR_DIFFERENT_VERSION"
    # An unsurveyed record can be listed but must not count as acoustic visit.
    extra=audit(src+"S28,N94,Vextra,2015-12-10,NOT_VISITED,NOT_ASSESSED,,original_form\n")
    assert extra["observed_opportunity_counts"]==EXPECTED
    assert extra["status_counts"]["NOT_VISITED"]==1
    print("PASS: 343 synthetic completed / 29 site / 95 survey-night opportunity check; "
          "8 invalid fixtures, missing visit, and unsurveyed visit; no frog outcomes")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--synthetic-test",action="store_true")
    ap.add_argument("--source-authorized-metadata-csv",type=Path)
    ap.add_argument("--receipt",type=Path)
    args=ap.parse_args()
    if args.synthetic_test:
        synthetic_tests()
        return
    if not (args.source_authorized_metadata_csv and args.receipt):
        ap.error("Provide both authorized source metadata file and receipt, or --synthetic-test")
    raw=args.source_authorized_metadata_csv.read_bytes()
    result=audit(raw.decode("utf-8-sig"))
    result["provided_metadata_only_sha256"]=hashlib.sha256(raw).hexdigest()
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "observed_opportunity_counts":result["observed_opportunity_counts"],
                      "frog_response_read":False},sort_keys=True))

if __name__=="__main__":
    main()
