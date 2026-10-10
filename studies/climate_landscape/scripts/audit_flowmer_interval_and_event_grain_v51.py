#!/usr/bin/env python3
"""v5.1 source-only actual Flow-MER RECORD GRAIN and observation-interval audit.

Only public, projected non-coordinate fields. The code processes values in
memory, writes only aggregate field schema, interval duration, duplicate-key
and coverage diagnostics, NEVER per-species records, location identifiers,
callingEvidence Y/N frequencies or CPUE effect sizes.
This is independent source QC, NOT an ecological hypothesis test.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter,defaultdict
from pathlib import Path

BASE="https://data.gov.au/data/api/3/action/datastore_search"
RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
FIELDS=("Program","SamplePoint","SampleDate","sampleDateStart",
        "sampleDateEnd(Date/Time)","speciesCode",
        "callingEvidence","CPUEAdults","CPUETadpoles")
EXPECTED=set(FIELDS)
MAX_BYTES=2_000_000
N_MAX=1500

def parse_timestamp(value):
    raw=str(value or "").strip()
    if not raw or raw.upper() in ("NA","N/A","NULL"):
        return None
    # Explicit formats; never infer day/month from locale by a fallthrough.
    text=raw.replace("Z","+00:00")
    try:
        when=dt.datetime.fromisoformat(text)
        return when.replace(tzinfo=None) if when.tzinfo is None else when.astimezone(dt.timezone.utc).replace(tzinfo=None)
    except ValueError:
        pass
    for f in ("%d/%m/%Y","%d/%m/%Y %H:%M:%S","%m/%d/%Y %H:%M:%S"):
        try:return dt.datetime.strptime(raw,f)
        except ValueError:pass
    return None

def audit(raw):
    if not isinstance(raw,dict) or raw.get("success") is not True:
        raise ValueError("invalid CKAN result")
    res=raw.get("result") or {}
    rows=res.get("records")
    meta=res.get("fields")
    if not isinstance(rows,list) or not 0<len(rows)<=N_MAX or len(rows)!=res.get("total"):
        raise ValueError("incomplete or oversized source")
    names={f.get("id") for f in meta if isinstance(f,dict)} if isinstance(meta,list) else set()
    if names!=EXPECTED:
        raise ValueError("source must contain only approved nonlocation projection")
    bad_date=Counter()
    bad_cpue=Counter()
    bad_call=0
    good_span=Counter()
    interval_kind_by_program=defaultdict(Counter)
    source_rows=Counter()
    species_by_event=defaultdict(set)
    sites_by_event=defaultdict(set)
    duplicate_species_events=Counter()
    unique_species_event=set()
    recorded_sites=defaultdict(set)
    record_day_time_differ=Counter()
    record_days=defaultdict(set)
    interval_start_days=defaultdict(set)
    months=defaultdict(set)
    source_versions=Counter()
    missing_species_code_by_program=Counter()
    for r in rows:
        if not isinstance(r,dict) or set(r)-EXPECTED-{"_id"}:
            raise ValueError("unapproved extra field")
        prog=str(r.get("Program") or "").strip()
        site=str(r.get("SamplePoint") or "").strip()
        raw_species=r.get("speciesCode")
        species=str(raw_species if raw_species is not None else "").strip()
        if not prog or not site:
            raise ValueError("source with blank program/site identity")
        if not species:
            missing_species_code_by_program[prog]+=1
        if max(len(prog),len(site),len(species))>120:
            raise ValueError("unbounded source label")
        source_rows[prog]+=1
        recorded_sites[prog].add(site)
        start=parse_timestamp(r.get("sampleDateStart"))
        end=parse_timestamp(r.get("sampleDateEnd(Date/Time)"))
        date=parse_timestamp(r.get("SampleDate"))
        for name,value in (("SampleDate",date),("sampleDateStart",start),("sampleDateEnd",end)):
            if value is None:bad_date[name]+=1
        if start is not None and end is not None:
            span_hours=(end-start).total_seconds()/3600
            if span_hours<=0:
                if span_hours==0:
                    good_span["zero_length"]+=1
                    interval_kind="ZERO_LENGTH"
                else:
                    good_span["end_before_start"]+=1
                    interval_kind="END_BEFORE_START"
            elif span_hours<=1:
                good_span["0_to_1h"]+=1
                interval_kind="0_TO_1H"
            elif span_hours<=24:
                good_span["1_to_24h"]+=1
                interval_kind="1_TO_24H"
            elif span_hours<=7*24:
                good_span["1_to_7d"]+=1
                interval_kind="1_TO_7D"
            elif span_hours<=31*24:
                good_span["7_to_31d"]+=1
                interval_kind="7_TO_31D"
            else:
                good_span["over_31d"]+=1
                interval_kind="OVER_31D"
            interval_kind_by_program[prog][interval_kind]+=1
            key=(prog,site,start.isoformat(),end.isoformat())
            if species:
                sp_key=key+(species,)
                if sp_key in unique_species_event:
                    duplicate_species_events[prog]+=1
                unique_species_event.add(sp_key)
                species_by_event[key].add(species)
            else:
                # A blank or unknown source species code does not establish
                # a species-negative row or a valid species-level join.
                species_by_event[key]
            event=(prog,start.isoformat(),end.isoformat())
            sites_by_event[event].add(site)
            months[prog].add(start.strftime("%Y-%m"))
            interval_start_days[prog].add(start.date().isoformat())
        if date is not None:
            record_days[prog].add(date.date().isoformat())
            if start is not None and start.date()!=date.date():
                record_day_time_differ[prog]+=1

        status=str(r.get("callingEvidence") or "").strip().upper()
        if status not in ("Y","N"):
            bad_call+=1
        for k in ("CPUEAdults","CPUETadpoles"):
            val=r.get(k)
            try:flt=float(val)
            except (ValueError,TypeError):bad_cpue[k]+=1;continue
            if not math.isfinite(flt) or flt<0:
                bad_cpue[k]+=1
    events_per_program=Counter(key[0] for key in species_by_event)
    spatial_by_program=defaultdict(Counter)
    for (prog,start,end),sites in sites_by_event.items():
        spatial_by_program[prog][len(sites)]+=1
    result={
        "status":"SOURCE_GRAIN_AUDIT_COMPLETE",
        "declared_total_source_records":len(rows),
        "record_counts_by_program":dict(sorted(source_rows.items())),
        "different_program_site_labels_count":{p:len(x) for p,x in sorted(recorded_sites.items())},
        "source_date_parse_fail_counts":dict(sorted(bad_date.items())),
        "interval_length_class_row_counts":dict(sorted(good_span.items())),
        "interval_length_by_program":{p:dict(sorted(c.items())) for p,c in sorted(interval_kind_by_program.items())},
        "sampleDate_record_dates_vs_interval_starts_distinct_by_program":{
            p:{"SampleDate_unique_days":len(record_days[p]),
               "interval_start_unique_days":len(interval_start_days[p]),
               "source_rows_where_calendar_dates_differ":record_day_time_differ[p],
               "interval_start_distinct_year_months":len(months[p])}
            for p in sorted(source_rows)
        },
        "n_unique_site_start_end_groups_by_program":dict(sorted(events_per_program.items())),
        "n_records_without_source_species_code_by_program":dict(sorted(missing_species_code_by_program.items())),
        "full_species_event_key_support":sum(missing_species_code_by_program.values())==0,
        "n_duplicate_species_records_same_site_and_interval_by_program":dict(sorted(duplicate_species_events.items())),
        "n_unique_interval_start_end_event_groups_by_program":{
            p:sum(c.values()) for p,c in sorted(spatial_by_program.items())},
        "n_interval_groups_with_4plus_listed_sites_by_program":{
            p:sum(n for width,n in c.items() if width>=4)
            for p,c in sorted(spatial_by_program.items())},
        "unrecognized_callingEvidence_codes_count":bad_call,
        "negative_nonnumeric_or_nonfinite_CPUE_field_counts":dict(sorted(bad_cpue.items())),
        "source_grain_warning":"Published SampleDate is unique data record timestamp; interval starts/ends may group observations for an interval rather than a night. Species records and their Y/N codes alone are NOT a complete sampling opportunity panel.",
        "no_species_names_or_raw_site_names_output":True,
        "no_coordinates_acquired":True,
        "no_CPUE_values_or_YN_counts_output":True,
        "no_effect_model_fitted":True,
        "no_Ocock_crosswalk_verified":True,
        "no_NAAMP_RC6_change":True
    }
    return result

def tests():
    fields=[{"id":v} for v in FIELDS]
    a={v:None for v in FIELDS}
    a.update({"Program":"X","SamplePoint":"internal-A","speciesCode":"frog-1",
       "SampleDate":"2018-07-06T00:00:00",
       "sampleDateStart":"2018-07-04T00:00:00",
       "sampleDateEnd(Date/Time)":"2018-07-10T00:00:00",
       "callingEvidence":"N","CPUEAdults":"0","CPUETadpoles":"0"})
    b=dict(a,speciesCode="frog-2",callingEvidence="Y")
    payload={"success":True,"result":{"records":[a,b],"total":2,"fields":fields}}
    q=audit(payload)
    assert q["n_unique_site_start_end_groups_by_program"]["X"]==1
    assert q["n_duplicate_species_records_same_site_and_interval_by_program"]=={}
    assert q["sampleDate_record_dates_vs_interval_starts_distinct_by_program"]["X"]["source_rows_where_calendar_dates_differ"]==2
    assert q["interval_length_class_row_counts"]["1_to_7d"]==2
    blank_species=json.loads(json.dumps(payload))
    blank_species["result"]["records"][0]["speciesCode"]=None
    u=audit(blank_species)
    assert u["n_records_without_source_species_code_by_program"]["X"]==1
    assert u["full_species_event_key_support"] is False
    assert q["unrecognized_callingEvidence_codes_count"]==0
    invalid=[
       {"success":True,"result":{"records":[dict(a,Latitude=-36)],"total":1,"fields":fields}},
       {"success":True,"result":{"records":[a,b],"total":3,"fields":fields}},
       {"success":True,"result":{"records":[a],"total":1,"fields":fields+[{"id":"Latitude"}]}},
    ]
    for i,bad in enumerate(invalid):
        try:audit(bad)
        except ValueError:pass
        else:raise AssertionError(f"unsafe payload {i}")
    print("PASS: interval semantics, repeated species per visit, date mismatch, zero outcome publication, reject geocoded rows")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    tests()
    if args.self_test:return
    req_url=BASE+"?"+urllib.parse.urlencode({
        "resource_id":RESOURCE,"limit":1000,"fields":",".join(FIELDS)})
    receipt={"source":"Australian Government Flow-MER Frog Abundance",
        "resource_id":RESOURCE,"requested_fields":FIELDS,
        "status":"SOURCE_UNAVAILABLE","no_RC6_change":True}
    try:
        req=urllib.request.Request(req_url,headers={"Accept":"application/json",
          "User-Agent":"frogcs-interval-only-QC-v5.1"})
        with urllib.request.urlopen(req,timeout=40) as r:
            raw=r.read(MAX_BYTES+1)
            if r.status!=200 or len(raw)>MAX_BYTES:
                raise ValueError("invalid source response length/status")
        receipt.update(audit(json.loads(raw.decode("utf-8"))))
    except urllib.error.HTTPError as ex:
        receipt.update(status="HTTP_UNAVAILABLE",http_status=ex.code)
    except (urllib.error.URLError,TimeoutError) as ex:
        receipt.update(status="NETWORK_ERROR",error_type=type(ex).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as ex:
        receipt.update(status="DATA_FORMAT_GATED",error_type=type(ex).__name__,error_text=str(ex)[:180])
    out=Path("studies/climate_landscape/receipts/FLOW_MER_INTERVAL_AND_EVENT_GRAIN_V51.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":receipt["status"],
        "error_type":receipt.get("error_type"),
        "error_text":receipt.get("error_text"),
        "interval_class_counts":receipt.get("interval_length_class_row_counts"),
        "interval_classes_by_program":receipt.get("interval_length_by_program"),
        "record_vs_interval_start_date_QC":receipt.get("sampleDate_record_dates_vs_interval_starts_distinct_by_program"),
        "duplicate_species_keys_by_program":receipt.get("n_duplicate_species_records_same_site_and_interval_by_program"),
        "source_event_groups_by_program":receipt.get("n_unique_interval_start_end_event_groups_by_program"),
        "program_event_counts":receipt.get("n_unique_site_start_end_groups_by_program"),
        "event_intervals_with_4plus_recorded_sites":receipt.get("n_interval_groups_with_4plus_listed_sites_by_program"),
        "invalid_calling_codes":receipt.get("unrecognized_callingEvidence_codes_count"),
        "missing_species_codes":receipt.get("n_records_without_source_species_code_by_program"),
        "full_species_event_key_support":receipt.get("full_species_event_key_support"),
        "invalid_cpue_counts":receipt.get("negative_nonnumeric_or_nonfinite_CPUE_field_counts"),
        "no_effect_model":True
        },sort_keys=True))

if __name__=="__main__":
    main()
