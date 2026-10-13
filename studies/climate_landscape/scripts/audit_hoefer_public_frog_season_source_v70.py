#!/usr/bin/env python3
"""v7.0: public Hoefer 2026 CSV SOURCE QUALITY ONLY; no frog-effect estimates.

Pre-outcome contract: V7_0_PUBLIC_FROG_OBSERVATION_SOURCE_FIRST_CONTRACT.md.
Source: Hoefer et al. 2026 Zenodo v2.0, cheloniax/repo_PAM_frogs tag v.2.0.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import csv
from datetime import datetime
from hashlib import sha1,sha256
from io import StringIO
import json
from pathlib import Path
import urllib.request,urllib.parse,urllib.error

SOURCE="https://raw.githubusercontent.com/cheloniax/repo_PAM_frogs/v.2.0/data/frog_data_season.csv"
BLOB="e5a419574be5e3f9922989f9aa6001fbb7f09d01"
CAP=4_000_000
PROFILE_FIELDS=("site","plot","season","sampling.trip","SamplingDay","assessment.method","survey.method","date","date.time")
NO_EMIT=("common.name","scientific.name","family")
EXPECTED_METHODS={"PAM.all","PAM.survey","OBM"}
OUT="studies/climate_landscape/receipts/HOEFER_2026_PUBLIC_SEASON_SOURCE_PROFILE_V70.json"

def parse_rows(raw:bytes):
    text=raw.decode("utf-8-sig")
    reader=csv.DictReader(StringIO(text))
    columns=reader.fieldnames
    if not columns or len(columns)!=len(set(columns)):
        raise ValueError("MISSING_OR_DUPLICATED_COLUMNS")
    mandatory={"site","plot","assessment.method","scientific.name","date"}
    if not mandatory.issubset(columns):
        raise ValueError("MISSING_SOURCE_DICTIONARY_COLUMNS")
    # No source row in the receipt; aggregate counts and site/plot repeated
    # positive-record support only. No date values/site labels printed.
    n=0
    methods=Counter(); seasons=Counter()
    units=defaultdict(set); trips=defaultdict(set); dates=defaultdict(set)
    site_ids=set(); plots=set(); siteplots=set(); distinct_trips=set(); observed_years=set()
    site_to_years=defaultdict(set); site_to_seasons=defaultdict(set); unit_to_years=defaultdict(set)
    bad=Counter()
    # Avoid user-supplied dates/species/site printing. No taxa used in QC.
    for row in reader:
        if None in row:
            raise ValueError("EXTRA_COLUMNS_IN_ROW")
        n+=1
        if n>250_000: raise ValueError("UNEXPECTED_SOURCE_RECORD_VOLUME")
        site=(row.get("site") or "").strip()
        plot=(row.get("plot") or "").strip()
        meth=(row.get("assessment.method") or "").strip()
        season=(row.get("season") or row.get("SamplingPeriod") or "").strip()
        trip=(row.get("sampling.trip") or row.get("Sampling.trip") or row.get("SamplingPeriod") or season).strip()
        day=(row.get("date") or "").strip()
        if not site or not plot: bad["missing_site_or_plot"]+=1;continue
        if not meth: bad["missing_assessment_method"]+=1; continue
        site_ids.add(site); plots.add(plot);siteplots.add((site,plot))
        methods[meth]+=1
        if season:seasons[season]+=1; site_to_seasons[site].add(season)
        if trip:trips[(meth,site,plot)].add(trip); distinct_trips.add(trip)
        if day:
            dates[(meth,site,plot)].add(day)
            yr=day[:4]
            if len(yr)==4 and yr.isdigit():
                observed_years.add(yr);site_to_years[site].add(yr)
                unit_to_years[(site,plot,season)].add(yr)
        if season:units[(meth,season)].add((site,plot))
        else:bad["missing_season_for_existing_detection"]+=1
    combinations={}
    for m in sorted(methods):
        pairs=[(k,len(v)) for k,v in trips.items() if k[0]==m]
        sc={s:len(units.get((m,s),())) for s in sorted(seasons)}
        multi=sum(n>=2 for _,n in pairs)
        combinations[m]={
            "n_positive_detection_rows":methods[m],
            "n_site_plot_keys_with_positive_detection":len(pairs),
            "n_site_plot_keys_in_2plus_source_periods":multi,
            "n_site_plot_season_combinations_with_positive_detection":
              sum(len(units[(mm,ss)]) for mm,ss in units if mm==m),
            "seasonal_site_plot_positive_support_counts":sc,
            "n_distinct_site_plot_source_dates_per_key_minmax":
                [min((len(v) for k,v in dates.items() if k[0]==m),default=None),
                 max((len(v) for k,v in dates.items() if k[0]==m),default=None)],
        }
    return {
        "status":"PUBLISHED_CSV_SOURCE_PROFILE_ONLY",
        "source_version":"Hoefer et al. 2026 Zenodo v2.0 public GitHub v.2.0",
        "sha256":sha256(raw).hexdigest(),
        "git_blob_sha1":BLOB,
        "source_bytes":len(raw),
        "n_source_positive_detection_rows":n,
        "source_columns":columns,
        "source_methods_positive_row_counts":dict(sorted(methods.items())),
        "n_distinct_source_site_labels":len(site_ids),
        "n_distinct_source_plot_labels":len(plots),
        "n_distinct_site_plot_label_pairs":len(siteplots),
        "n_distinct_season_labels_with_positive_rows":len(seasons),
        "n_distinct_source_trip_labels":len(distinct_trips),
        "n_distinct_calendar_year_labels":len(observed_years),
        "calendar_year_minmax": [min(observed_years,default=None),max(observed_years,default=None)],
        "n_sites_positive_records_in_2plus_calendar_years":sum(len(v)>=2 for v in site_to_years.values()),
        "n_site_plot_season_keys_with_2plus_calendar_years":sum(len(v)>=2 for v in unit_to_years.values()),
        "positive_season_labels_per_site_sorted_counts":sorted(len(v) for v in site_to_seasons.values()),
        "positive_calendar_year_labels_per_site_sorted_counts":sorted(len(v) for v in site_to_years.values()),
        "n_distinct_site_plot_season_triples_with_positive_rows":
           len({(m,s,x) for (m,s),v in units.items() for x in v}),
        "source_method_positive_only_repetition":combinations,
        "record_quality_flags":dict(bad),
        "no_animal_species_outcome_frequency_analysed":True,
        "no_species_names_site_names_or_dates_exported":True,
        "site_plot_season_coverage_is_pos_detection_not_visit_effort":True,
        "full_negative_survey_opportunities_unverified":True,
        "local_water_history_link_unverified":True,
        "read_file_only_no_archived_audio":True,
        "no_jae_rc6_change":True,
    }

def synthetic_test():
    sample="site,plot,assessment.method,scientific.name,date,season,Sampling.trip\nS1,P1,PAM.survey,SENSITIVE_TAXON,2026-01-01,wet,trip1\nS1,P1,PAM.survey,SENSITIVE_TAXON,2026-02-01,dry,trip2\nS2,P2,OBM,OTHER_TAXON,2026-03-01,wet,trip1\n"
    x=parse_rows(sample.encode())
    assert x["n_source_positive_detection_rows"]==3
    assert x["source_method_positive_only_repetition"]["PAM.survey"]["n_site_plot_keys_in_2plus_source_periods"]==1
    assert "SENSITIVE_TAXON" not in json.dumps(x) and "S1" not in json.dumps(x)
    try:
        parse_rows(sample.replace("2026-03-01,wet,trip1","2026-03-01,wet,trip1,extra").encode())
    except ValueError:pass
    else:raise AssertionError("malformed source width accepted")
    print("PASS: source-only positive detection coverage and no individual site/taxon/date disclosure")

def main():
    synthetic_test()
    report={"status":"SOURCE_UNAVAILABLE","source":SOURCE,"expected_git_blob_sha1":BLOB,
            "no_animals_or_sites_exported":True,"no_jae_rc6_change":True}
    try:
        u=urllib.parse.urlsplit(SOURCE)
        if u.scheme!="https" or u.hostname!="raw.githubusercontent.com":
            raise ValueError("UNAPPROVED_SOURCE_HOST")
        req=urllib.request.Request(SOURCE,headers={
            "Accept":"text/csv","User-Agent":"frogcs-public-ecological-source-profile/7.0"})
        with urllib.request.urlopen(req,timeout=35) as rsp:
            final=urllib.parse.urlsplit(rsp.geturl())
            if final.scheme!="https" or final.hostname!="raw.githubusercontent.com":
                raise ValueError("UNAPPROVED_SOURCE_REDIRECT")
            raw=rsp.read(CAP+1)
            if rsp.status!=200 or len(raw)>CAP:raise ValueError("SOURCE_RESPONSE_TOO_LARGE")
        digest=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if digest!=BLOB:raise ValueError("SOURCE_BLOB_SHA_MISMATCH")
        report.update(parse_rows(raw))
        report["status"]="SOURCE_PROFILE_COMPLETED"
    except urllib.error.HTTPError as e:
        report.update(status="SOURCE_HTTP_UNAVAILABLE",http_code=e.code)
    except (urllib.error.URLError,TimeoutError) as e:
        report.update(status="SOURCE_NETWORK_UNAVAILABLE",error_type=type(e).__name__)
    except (TypeError,ValueError,KeyError,UnicodeError,csv.Error) as e:
        report.update(status="SOURCE_FAILED_CLOSED",error_type=type(e).__name__,
                      safe_error_code=str(e) if str(e) in
                      {"UNAPPROVED_SOURCE_HOST","UNAPPROVED_SOURCE_REDIRECT",
                       "SOURCE_RESPONSE_TOO_LARGE","SOURCE_BLOB_SHA_MISMATCH",
                       "MISSING_OR_DUPLICATED_COLUMNS","MISSING_SOURCE_DICTIONARY_COLUMNS",
                       "UNEXPECTED_SOURCE_RECORD_VOLUME","EXTRA_COLUMNS_IN_ROW"}
                       else "SOURCE_UNKNOWN_VARIATION")
    p=Path(OUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":main()
