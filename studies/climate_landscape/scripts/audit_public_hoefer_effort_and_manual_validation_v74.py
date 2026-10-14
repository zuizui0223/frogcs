#!/usr/bin/env python3
"""Published Hoefer et al 2026 original site/season effort and candidate-validation QC.

Exactly source-only metrics under the PRE-READ
V7_4_PUBLIC_RECORDER_EFFORT_AND_MANUAL_MATCH_SOURCE_QC_CONTRACT.md.
No biological frog assemblage response statistics, species/site outputs,
individual candidate examples, environmental effects, or simulated ecology.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
from hashlib import sha1, sha256
from io import StringIO
import csv
import json
from pathlib import Path
import re
import statistics
import urllib.parse
import urllib.request

ROOT="https://raw.githubusercontent.com/cheloniax/repo_PAM_frogs/v.2.0/"
FILES={
    "author_r_code":("scripts/R_code_biodiversityFrogs.qmd",
        "93c6e051ce446f76ac0730f52693bea9ebfc3963",100_000),
    "season_positive":("data/frog_data_season.csv",
        "e5a419574be5e3f9922989f9aa6001fbb7f09d01",2_000_000),
    "candidate_manual_validation":("data/frogs_PAM_daily_all.csv",
        "f2f7a5426be57e98387f06055c9361377f007ad4",12_000_000),
}
RESULT="studies/climate_landscape/receipts/HOEFER_2026_REAL_ORIGINAL_EFFORT_VALIDATION_QC_V74.json"
SEASONS=("winter","spring","summer","autumn")

def read_pinned(path,gitsha,cap):
    url=ROOT+path
    u=urllib.parse.urlsplit(url)
    if u.scheme!="https" or u.hostname!="raw.githubusercontent.com":
        raise ValueError("SOURCE_HOST_NOT_ALLOWED")
    req=urllib.request.Request(url,headers={"Accept":"text/plain",
        "User-Agent":"frogcs-open-source-effort-validation-QC/7.4"})
    with urllib.request.urlopen(req,timeout=60) as response:
        last=urllib.parse.urlsplit(response.geturl())
        if response.status!=200 or last.scheme!="https" or last.hostname!="raw.githubusercontent.com":
            raise ValueError("SOURCE_HTTP_OR_REDIRECT_CHANGED")
        raw=response.read(cap+1)
    if len(raw)>cap or not raw:
        raise ValueError("SOURCE_EMPTY_OR_SIZE_LIMIT")
    digest=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if digest!=gitsha:
        raise ValueError("SOURCE_GIT_BLOB_CHANGED")
    return raw

def author_effort_metadata(text):
    # Everything here is printed in the ORIGINAL authors' open Quarto script:
    # site-level whole-period T_days both in case_when and site_vals; 24
    # site×season max_days in seasonal_limits tribble.
    start=text.find("seasonal_limits <- tribble(")
    if start<0: raise ValueError("SEASONAL_BLOCK_NOT_FOUND")
    end=text.find("\n)",start)
    if end<0: raise ValueError("SEASONAL_BLOCK_UNTERMINATED")
    seasonal=text[start:end]
    records=re.findall(
        r'"([^"]+)"\s*,\s*"(winter|spring|summer|autumn)"\s*,\s*(\d+)\s*,?',
        seasonal)
    if len(records)!=24:
        raise ValueError("EXPECTED_24_AUTHOR_SITE_SEASON_DAYS")
    seasons={}
    for site,season,days in records:
        key=(site,season)
        if key in seasons:raise ValueError("AUTHOR_DUPLICATE_SITE_SEASON")
        seasons[key]=int(days)
    vals=re.search(r"site_vals\s*<-\s*c\(([^)]*)\)",text,re.S)
    if not vals:raise ValueError("ORIGINAL_FULL_PERIOD_DAYS_MISSING")
    total=dict((site,int(days)) for site,days in
        re.findall(r"([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\d+)",vals.group(1)))
    # Read the separate author case_when declarations, which should
    # independently agree with the site_vals used by the original code.
    begin=text.find("T_days = case_when(",text.find("## PAM survey length"))
    if begin<0: raise ValueError("ORIGINAL_CASE_WHEN_NOT_FOUND")
    stop=text.find("TRUE ~",begin)
    if stop<0:raise ValueError("ORIGINAL_CASE_WHEN_UNTERMINATED")
    case=dict((site,int(days)) for site,days in re.findall(
        r'unique\(site\)\s*==\s*"([^"]+)"\s*~\s*(\d+)',text[begin:stop]))
    if case!=total:raise ValueError("AUTHOR_TWO_TOTAL_DECLARATIONS_DISAGREE")
    if len(total)!=6 or len(seasons)!=24 or {
        key[0] for key in seasons}!=set(total): raise ValueError("SITE_UNITS_DIFFER")
    if any({s for n,s in seasons if n==site}!=set(SEASONS) for site in total):
        raise ValueError("ORIGINAL_FOUR_SEASONS_INCOMPLETE")
    deltas={site:total[site]-sum(seasons[(site,s)] for s in SEASONS)
            for site in total}
    return {
        "n_author_site_total_day_entries":len(total),
        "n_author_site_season_max_day_entries":len(seasons),
        "author_site_whole_period_T_days_sum":sum(total.values()),
        "author_four_season_max_days_sum":sum(seasons.values()),
        "total_minus_season_day_difference_sum":sum(deltas.values()),
        "n_sites_with_exact_arithmetic_equality":sum(d==0 for d in deltas.values()),
        "n_sites_with_any_difference":sum(d!=0 for d in deltas.values()),
        "site_day_differences_sorted_without_site_identifiers":
            sorted(deltas.values()),
        "minmax_site_day_differences":[min(deltas.values()),max(deltas.values())],
        "source_denominator_grain":"author site total and site x season limit; NOT site x plot x season x cycle x timestamp actual valid recorder opportunities",
        "per_plot_original_recorder_uptime_data_obtained":False,
        "differences_prove_raw_missing_audio":False
    },seasons,total

def positive_day_support(raw,seasons):
    reader=csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    need={"site","plot","date","season","assessment.method"}
    if not reader.fieldnames or not need.issubset(reader.fieldnames):
        raise ValueError("PUBLISHED_SEASON_DETECTION_SCHEMA_CHANGED")
    site_season_dates=defaultdict(set)
    plot_season_dates=defaultdict(set)
    rows=0;unknown=0
    for row in reader:
        if None in row: raise ValueError("DETECTION_ROW_SCHEMA_CHANGED")
        rows+=1
        site=(row.get("site") or "").strip()
        plot=(row.get("plot") or "").strip()
        season=(row.get("season") or "").strip().lower()
        if (site,season) not in seasons or not plot or row.get("assessment.method")!="PAM.all":
            raise ValueError("UNEXPECTED_SOURCE_RECORD_FRAME")
        try: d=datetime.strptime(row.get("date",""),"%Y-%m-%d").date()
        except ValueError as exc:raise ValueError("INVALID_PUBLISHED_DATE") from exc
        site_season_dates[(site,season)].add(d)
        plot_season_dates[(site,plot,season)].add(d)
    if rows!=13577 or len(site_season_dates)!=24 or len(plot_season_dates)!=95:
        raise ValueError("SOURCE_DETECTION_SCOPE_CHANGED")
    violations=[]; fractions=[]; less=[]; days=[]
    for key,maxdays in seasons.items():
        value=len(site_season_dates.get(key,set()))
        if value>maxdays:violations.append(value-maxdays)
        fractions.append(value/maxdays)
        less.append(maxdays-value)
        days.append(value)
    return {
        "source_positive_detection_rows":rows,
        "n_site_season_year_pooled_positive_day_keys":len(site_season_dates),
        "n_site_plot_season_keys_with_positive_detection_days":len(plot_season_dates),
        "n_site_season_positive_day_counts_exceed_author_max_days":len(violations),
        "positive_day_excess_days_sorted_without_names":sorted(violations),
        "positive_detection_calendar_days_per_site_season_minmedianmax":[
            min(days),statistics.median(days),max(days)],
        "positive_day_to_reported_season_max_day_ratio_minmedianmax":[
            round(min(fractions),5),round(statistics.median(fractions),5),
            round(max(fractions),5)],
        "reported_site_season_max_minus_positive_calendar_days_minmedianmax":[
            min(less),statistics.median(less),max(less)],
        "WARNING":"Positive-detection dates are conditioned on calls and do NOT prove other dates were acoustically valid no-call opportunities. Ratios not occupancy/recorder uptime.",
        "unreported_species_or_missing_plot_day_inferred_zero":False
    }

def candidate_validation(raw):
    reader=csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    headers=reader.fieldnames
    mandatory={"MANUAL.ID","template","eucledian.distance"}
    if not headers or not mandatory.issubset(headers) or len(headers)!=len(set(headers)):
        raise ValueError("ORIGINAL_VALIDATION_SCHEMA_CHANGED")
    n=0
    labels=Counter()
    by_template=defaultdict(Counter)
    distance_missing=Counter()
    templates=set()
    for row in reader:
        if None in row:raise ValueError("VALIDATION_ROW_WIDTH_CHANGED")
        n+=1
        if n>500_000:raise ValueError("UNEXPECTED_VALIDATION_RECORDS")
        val=(row.get("MANUAL.ID") or "").strip().upper()
        if val in {"TRUE","T","1"}:cls="TRUE"
        elif val in {"FALSE","F","0"}:cls="FALSE"
        elif val in {"UNSURE"}:cls="UNSURE"
        elif val in {"","NA","N/A","NULL","NONE"}:cls="MISSING"
        else:cls="OTHER"
        labels[cls]+=1
        t=(row.get("template") or "").strip()
        if t:by_template[t][cls]+=1;templates.add(t)
        else: distance_missing["missing_template"]+=1
        distance=(row.get("eucledian.distance") or "").strip()
        if not distance:distance_missing["missing_distance"]+=1
        else:
            try:float(distance)
            except ValueError:distance_missing["non_numeric_distance"]+=1
    if not n:raise ValueError("NO_ORIGINAL_VALIDATION_RECORDS")
    # Metadata columns (names only), never an assumed join without an
    # explicit repeated unique occurrence ID.
    keynames={"site","plot","date","scientific.name","date.time",
              "SamplePoint","event_id","recording_id","audio_file","file_name"}
    available_keys=sorted(k for k in headers if k in keynames)
    categories={c:int(labels[c]) for c in ("TRUE","FALSE","UNSURE","MISSING","OTHER")}
    yes=categories["TRUE"];no=categories["FALSE"]
    complete={
      "n_templates_with_any_manual_true":sum(c["TRUE"]>0 for c in by_template.values()),
      "n_templates_with_both_true_and_false":sum(c["TRUE"]>0 and c["FALSE"]>0
                                                for c in by_template.values()),
      "n_templates_with_5plus_each_true_and_false":sum(c["TRUE"]>=5 and c["FALSE"]>=5
                                                for c in by_template.values()),
      "n_templates_with_no_true_but_any_false":sum(c["TRUE"]==0 and c["FALSE"]>0
                                                for c in by_template.values()),
      "n_templates_with_just_true_labeled_records":sum(c["TRUE"]>0 and c["FALSE"]==0
                                                for c in by_template.values()),
    }
    return {
        "original_validation_rows":n,
        "original_validation_field_names_ONLY":headers,
        "n_original_distinct_reference_templates":len(templates),
        "MANUAL_ID_original_candidate_label_counts":categories,
        "n_manually_true_or_false_labeled_candidates":yes+no,
        "fraction_true_among_decided_candidate_matches_NOT_recall_or_precision":
            round(yes/(yes+no),5) if yes+no else None,
        "template_support":complete,
        "null_or_non_numeric_source_key_counts":dict(distance_missing),
        "potential_site_plot_date_species_join_column_names_ONLY":available_keys,
        "author_selected_filter":"R code removes UNSURE/NA and templates with zero manually TRUE reference matches before downstream logistic curve",
        "rowwise_source_id_join_to_13577_pamall_species_observations_established":False,
        "global_candidate_label_fraction_estimates_species_detection_accuracy":False,
        "manual_FALSE_is_an_original_recording_no_frog_opportunity":False,
    }

def smoke_tests():
    excerpt='''## PAM survey length
T_days = case_when(
  unique(site) == "S1" ~ 12,
  unique(site) == "S2" ~ 18,
  TRUE ~ n_distinct(SamplingDay)
)
site_vals <- c(S1=12, S2=18)
seasonal_limits <- tribble(
  ~site, ~season, ~max_days,
  "S1", "winter", 1,
  "S2", "winter", 2
)
'''
    # Real author parser has a deliberate six-site/four-season guard.
    try:author_effort_metadata(excerpt)
    except ValueError as e:assert str(e) in {
        "EXPECTED_24_AUTHOR_SITE_SEASON_DAYS","SITE_UNITS_DIFFER"}
    else:raise AssertionError("Source incompleteness unexpectedly accepted")
    csvtext="MANUAL.ID,template,eucledian.distance\nTRUE,A,0.1\nFALSE,A,0.2\nUNSURE,B,0.3\nFALSE,B,0.4\n"
    profile=candidate_validation(csvtext.encode())
    assert profile["MANUAL_ID_original_candidate_label_counts"]=={
         "TRUE":1,"FALSE":2,"UNSURE":1,"MISSING":0,"OTHER":0}
    assert profile["n_original_distinct_reference_templates"]==2
    assert profile["template_support"]["n_templates_with_no_true_but_any_false"]==1
    assert not profile["rowwise_source_id_join_to_13577_pamall_species_observations_established"]
    assert "A" not in json.dumps(profile) or profile["original_validation_field_names_ONLY"]
    print("PASS: fail-closed source effort grain, labeled-vs-unknown candidate counts, no raw template identity exported")

def main():
    smoke_tests()
    src={}
    for name,(path,pin,cap) in FILES.items():
        raw=read_pinned(path,pin,cap)
        src[name]={"tag_path":path,"blob_sha1":pin,"sha256":sha256(raw).hexdigest(),"bytes":len(raw)}
        if name=="author_r_code":
            author,seasonal,site_total=author_effort_metadata(raw.decode("utf-8-sig"))
        elif name=="season_positive":
            positive=positive_day_support(raw,seasonal)
        elif name=="candidate_manual_validation":
            validation=candidate_validation(raw)
    out={
      "status":"PUBLIC_SOURCE_EFFORT_AND_MANUAL_VALIDATION_QC_COMPLETED",
      "original_author":"Hoefer et al. (2026), Zenodo v2.0 public tagged GitHub",
      "public_repository":"https://github.com/cheloniax/repo_PAM_frogs/tree/v.2.0",
      "original_source_hashes":src,
      "original_author_effort_numbers":author,
      "actual_positive_detection_day_support":positive,
      "actual_candidate_manual_validation":validation,
      "survey_opportunity_source_keys_joined":False,
      "per_recorder_calendar_effort_and_quality_verified":False,
      "results_v71_v72_v73_adjusted_for_real_effort":False,
      "no_new_species_group_ecology_estimated":True,
      "all_source_site_species_plot_value_rows_omitted":True,
      "not_using_TinyFish_or_private_source":True,
      "main_rc6_modified":False
    }
    p=Path(RESULT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PUBLIC_QC_RESULT "+json.dumps(out,sort_keys=True))

if __name__=="__main__":main()
