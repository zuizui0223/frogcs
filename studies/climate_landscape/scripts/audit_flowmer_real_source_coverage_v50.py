#!/usr/bin/env python3
"""v5.0 source-only coverage for real OFFICIAL public Flow-MER frog rows.

Uses a CKAN projection that EXCLUDES coordinates, species names/codes and free
text; retains only aggregated field NONMISSINGNESS, date/site support and source
version. Never reports individual locations, species, CPUE values or call Y/N
frequencies; fits no ecological model. Source-only QC frozen in v5.0 memo.
"""
from __future__ import annotations
import csv
import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter,defaultdict
from pathlib import Path

BASE="https://data.gov.au/data/api/3/action/datastore_search"
RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
FIELDS=("Program","SamplePoint","SampleDate","sampleDateStart",
        "callingEvidence","CPUEAdults","CPUETadpoles")
EXPECTED={"Program","SamplePoint","SampleDate","sampleDateStart",
          "callingEvidence","CPUEAdults","CPUETadpoles"}
MAX_BYTES=2_000_000
N_MAX=1500

def calendar_date(text):
    s=str(text or "").strip()
    if not s:
        return None
    # Official API may publish 'YYYY-MM-DD HH:MM:SS' or 'DD/MM/YYYY'
    # as a string; avoid guessing which date is a start vs end.
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return dt.datetime.strptime(s[:26],fmt).date().isoformat()
        except ValueError:
            continue
    if len(s)>=10 and s[4]=="-" and s[7]=="-":
        try:
            return dt.date.fromisoformat(s[:10]).isoformat()
        except ValueError:
            pass
    return None

def summarize(obj):
    if not isinstance(obj,dict) or obj.get("success") is not True:
        raise ValueError("official CKAN DataStore returned error")
    result=obj.get("result") or {}
    rows=result.get("records")
    if not isinstance(rows,list) or not 0<len(rows)<=N_MAX:
        raise ValueError("expected bounded nonempty source rows")
    if len(rows)!=result.get("total"):
        raise ValueError("projection did not fetch full published source coverage")
    observed_fields={f.get("id") for f in result.get("fields",[]) if isinstance(f,dict)}
    if observed_fields!=EXPECTED:
        raise ValueError("projection returned unexpected or sensitive columns")
    counts=Counter()
    source_site_date=defaultdict(set)
    source_sites=defaultdict(set)
    nonmissing=Counter()
    unparsed=0
    years=defaultdict(Counter)
    date_source=Counter()
    for row in rows:
        if not isinstance(row,dict) or set(row)-EXPECTED-{"_id"}:
            raise ValueError("unexpected response-bearing field")
        program=str(row.get("Program") or "").strip()
        point=str(row.get("SamplePoint") or "").strip()
        if not program or not point:
            counts["missing_program_or_site"]+=1
            continue
        # Published census region names only; do not store point/coordinates.
        if len(program)>120 or len(point)>120:
            raise ValueError("unexpectedly long official region/site alias")
        counts["source_records"]+=1
        counts["nonblank_program_site_rows"]+=1
        source_sites[program].add(point)
        for name in ("callingEvidence","CPUEAdults","CPUETadpoles"):
            if row.get(name) not in (None,"","NA","N/A"):
                nonmissing[name]+=1
        if all(row.get(name) not in (None,"","NA","N/A")
               for name in ("callingEvidence","CPUETadpoles")):
            nonmissing["callingEvidence_AND_CPUETadpoles"]+=1
        start=calendar_date(row.get("sampleDateStart"))
        primary=calendar_date(row.get("SampleDate"))
        if start:
            day=start
            date_source["sampleDateStart_used"]+=1
        elif primary:
            day=primary
            date_source["SampleDate_fallback_used"]+=1
        else:
            day=None
            unparsed+=1
        if day:
            source_site_date[(program,day)].add(point)
            years[program][day[:4]]+=1
    reg_counts=Counter(str(row.get("Program") or "").strip() for row in rows)
    # Region names are already government-published administrative source labels.
    programs={}
    for program in sorted(reg_counts):
        if not program:
            continue
        widths=Counter(len(ids) for (p,d),ids in source_site_date.items() if p==program)
        programs[program]={
            "n_species_level_source_rows":reg_counts[program],
            "n_distinct_recorded_sites_NO_COMPLETENESS_CLAIM":len(source_sites[program]),
            "n_distinct_site_date_groups_WITH_AT_LEAST_ONE_RECORD":sum(widths.values()),
            "n_calendar_dates_WITH_AT_LEAST_ONE_RECORD":sum(widths.values()),
            "source_date_4plus_sites_WITH_ANY_SPECIES_RECORD":sum(v for k,v in widths.items() if k>=4),
            "source_date_2plus_sites_WITH_ANY_SPECIES_RECORD":sum(v for k,v in widths.items() if k>=2),
            "year_record_counts":dict(sorted(years[program].items()))
        }
    return {
        "data_scope":"source-only actual official CKAN projected non-sensitive columns",
        "source_row_total":result.get("total"),
        "program_record_support":programs,
        "n_nonmissing_by_published_outcome_field_ONLY":dict(nonmissing),
        "n_unparsable_or_missing_survey_dates":unparsed,
        "date_choice_counts":dict(date_source),
        "n_rows_without_public_program_or_site":counts["missing_program_or_site"],
        "source_visit_ledger_verified":False,
        "calling_YN_is_not_strong_chorus":True,
        "tadpole_CPUE_is_not_metamorph_success":True,
        "no_automatic_Ocock_site_crosswalk":True,
        "region_date_site_group_is_not_a_completed_survey_night":True,
        "specimen_locations_saved":False,
        "raw_site_names_saved":False,
        "species_records_published":False,
        "frog_values_published":False,
        "biological_model_fitted":False,
        "rc6_unchanged":True
    }

def fake_test():
    projected=[{"id":f,"type":"text"} for f in FIELDS]
    rows=[
        {"Program":"Gwydir","SamplePoint":"A","SampleDate":"2016-09-01",
         "sampleDateStart":"2016-09-01","callingEvidence":"Y",
         "CPUEAdults":None,"CPUETadpoles":"0"},
        {"Program":"Gwydir","SamplePoint":"B","SampleDate":"2016-09-01",
         "sampleDateStart":"2016-09-01","callingEvidence":"N",
         "CPUEAdults":"2","CPUETadpoles":None},
    ]
    good={"success":True,"result":{"records":rows,"total":2,"fields":projected}}
    s=summarize(good)
    assert s["program_record_support"]["Gwydir"]["n_distinct_recorded_sites_NO_COMPLETENESS_CLAIM"]==2
    assert s["n_nonmissing_by_published_outcome_field_ONLY"]["callingEvidence"]==2
    for bad in (
        {"success":True,"result":{"records":rows,"total":3,"fields":projected}},
        {"success":True,"result":{"records":[dict(rows[0],Latitude=-33)],"total":1,"fields":projected}},
        {"success":True,"result":{"records":rows,"total":2,
                                    "fields":projected+[{"id":"Latitude"}]}},
    ):
        try:summarize(bad)
        except ValueError:pass
        else:raise AssertionError("source governance violation passed")
    print("PASS: bounded real-source projection aggregation and strict no-coordinate field tests")

def main():
    params=urllib.parse.urlencode({"resource_id":RESOURCE,"limit":1000,
                                    "fields":",".join(FIELDS)})
    url=BASE+"?"+params
    receipt={
        "audit":"flowmer_real_public_projected_source_coverage_v50",
        "official_dataset":"https://data.gov.au/data/dataset/flow-mer-frog-abundance",
        "ckan_resource_id":RESOURCE,
        "only_selected_columns":FIELDS,
        "source_only":True,
        "status":"SOURCE_UNAVAILABLE",
        "not_released_any_site_species_data":True,
        "rc6_unchanged":True
    }
    try:
        req=urllib.request.Request(url,headers={
            "Accept":"application/json",
            "User-Agent":"frogcs-FlowMER-non-sensitive-source-coverage/5.0"})
        with urllib.request.urlopen(req,timeout=40) as response:
            buf=response.read(MAX_BYTES+1)
            if response.status!=200 or len(buf)>MAX_BYTES:
                raise ValueError("source response not bounded")
        payload=json.loads(buf.decode("utf-8"))
        receipt.update(summarize(payload))
        receipt["status"]="SOURCE_COVERAGE_CHECKED"
    except urllib.error.HTTPError as ex:
        receipt.update(status="HTTP_BLOCKED",http_status=ex.code)
    except (urllib.error.URLError,TimeoutError) as ex:
        receipt.update(status="NETWORK_UNAVAILABLE",error_type=type(ex).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as ex:
        receipt.update(status="FAILED_CLOSED_SOURCE_SCHEMA",error_type=type(ex).__name__,
                       error_detail=str(ex)[:220])
    path=Path("studies/climate_landscape/receipts/FLOW_MER_REAL_NON_SENSITIVE_SOURCE_COVERAGE_V50.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":receipt["status"],
                      "source_row_total":receipt.get("source_row_total"),
                      "program_record_support":receipt.get("program_record_support"),
                      "field_nonmissing_counts":receipt.get("n_nonmissing_by_published_outcome_field_ONLY"),
                      "raw_locations_or_species_values_printed":False,
                      "ecological_model_fitted":False},sort_keys=True))

if __name__=="__main__":
    fake_test()
    main()
