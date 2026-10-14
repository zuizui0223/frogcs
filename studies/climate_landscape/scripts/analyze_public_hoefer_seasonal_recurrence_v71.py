#!/usr/bin/env python3
"""v7.1 actual PUBLIC frog PAM assemblage seasonal-vs-annual recurrence analysis.

Positive detections only. Not frog occupancy, field-water effects, memory
or reproductive success. Frozen ecological design and source:
V7_1_PUBLIC_PAM_SEASONAL_RECURRENCE_FROZEN_ANALYSIS.md
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import datetime
from hashlib import sha1,sha256
from io import StringIO
from itertools import combinations
from pathlib import Path
import csv
import json
import random
import statistics
import urllib.request
import urllib.parse

URL="https://raw.githubusercontent.com/cheloniax/repo_PAM_frogs/v.2.0/data/frog_data_season.csv"
EXPECTED_BLOB="e5a419574be5e3f9922989f9aa6001fbb7f09d01"
EXPECTED_N=13577
BANDS=("A","T","P")
SEASONS={"spring","summer","autumn","winter"}
OUTPUT="studies/climate_landscape/receipts/HOEFER_2026_REAL_SEASONAL_RECURRENCE_V71.json"
DATE_SUPPORT_THRESHOLD=5
BOOTSTRAP_DRAWS=5000
BOOTSTRAP_SEED=20261013

def valid_day(s):
    v=str(s or "").strip()
    try:
        return datetime.strptime(v,"%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("INVALID_SOURCE_CALENDAR_DATE") from exc

def parse_detection_cells(contents:str,strict_source:bool=True):
    reader=csv.DictReader(StringIO(contents))
    columns=reader.fieldnames
    wanted={"date","site","plot","season","assessment.method","scientific.name"}
    if not columns or len(columns)!=len(set(columns)) or not wanted.issubset(columns):
        raise ValueError("SOURCE_SCHEMA_CHANGED")
    cells=defaultdict(set)
    cell_positive_dates=defaultdict(set)
    count=0
    methods=Counter()
    invalid=Counter()
    raw_siteplots=set()
    date_range=[]
    for row in reader:
        if None in row:raise ValueError("SOURCE_BAD_CSV_ROW_WIDTH")
        count+=1
        if count>250000:raise ValueError("SOURCE_VOLUME_CHANGED")
        method=(row.get("assessment.method") or "").strip()
        methods[method]+=1
        if method!="PAM.all":
            # The released seasonal file was source-verified to contain only
            # PAM.all; do not opportunistically pool different methods.
            raise ValueError("SOURCE_METHOD_CHANGED")
        site=(row.get("site") or "").strip()
        plot=(row.get("plot") or "").strip()
        season=(row.get("season") or "").strip().lower()
        species=(row.get("scientific.name") or "").strip()
        if not site or not plot:raise ValueError("SOURCE_LOCATION_KEY_MISSING")
        if season not in SEASONS:raise ValueError("SOURCE_SEASON_UNRECOGNISED")
        day=valid_day(row.get("date"))
        raw_siteplots.add((site,plot))
        date_range.append(day)
        if not species or species.upper() in {"NA","N/A","UNKNOWN"}:
            invalid["species_id_missing"]+=1
            continue
        # A source row is POSITIVE identification; this never adds cells
        # for unsupported zero detections or unvisited periods.
        key=(site,plot,season,day.year)
        cells[key].add(species)
        cell_positive_dates[key].add(day)
    if strict_source and (count!=EXPECTED_N or len(raw_siteplots)!=24
                          or len({s for s,p in raw_siteplots})!=6):
        raise ValueError("SOURCE_FRAME_CHANGED")
    if not cells:raise ValueError("NO_ELIGIBLE_FROG_SOURCE_DETECTIONS")
    return cells,cell_positive_dates,{
       "n_original_positive_detection_rows":count,
       "n_positive_species_missing_rows":invalid["species_id_missing"],
       "n_original_site_plot_keys":len(raw_siteplots),
       "n_calendar_years_with_any_source_positive":len({d.year for d in date_range}),
       "n_distinct_detected_taxon_labels":len({sp for names in cells.values() for sp in names}),
       "n_positive_site_plot_season_year_cells":len(cells),
       "n_positive_site_plot_season_keys":
           len({(a,b,c) for a,b,c,y in cells}),
       "n_positive_site_plot_year_keys":
           len({(a,b,y) for a,b,c,y in cells}),
       "n_positive_days_per_cell_minmedianmax":
           [min(len(v) for v in cell_positive_dates.values()),
            statistics.median(len(v) for v in cell_positive_dates.values()),
            max(len(v) for v in cell_positive_dates.values())],
       "n_detected_taxa_per_cell_minmedianmax":
           [min(map(len,cells.values())),
            statistics.median(map(len,cells.values())),
            max(map(len,cells.values()))],
       "source_record_method_counts":dict(methods),
    }

def jaccard(a,b):
    union=len(a|b)
    if not union: raise ValueError("EMPTY_SETS_MUST_NOT_ENTER")
    return len(a&b)/union

def categories(cells,dates,min_positive_days=0):
    by_site=defaultdict(lambda:{b:[] for b in BANDS})
    for site in sorted({k[0] for k in cells}):
        keys=[k for k in cells if k[0]==site
              and len(dates[k])>=min_positive_days]
        for left,right in combinations(keys,2):
            _,pl,sl,yl=left
            _,pr,sr,yr=right
            band=None
            if pl==pr and sl==sr and abs(yl-yr)==1:
                band="A"  # adjacent-year, identical season/plot
            elif pl==pr and yl==yr and sl!=sr:
                band="T"  # different seasons same year and plot
            elif yl==yr and sl==sr and pl!=pr:
                band="P"  # different plots, same season and year
            if band:
                by_site[site][band].append(jaccard(cells[left],cells[right]))
    return by_site

def percentile(vals,q):
    a=sorted(vals)
    if not a:return None
    p=(len(a)-1)*q
    low=int(p);high=min(low+1,len(a)-1)
    return a[low]+(p-low)*(a[high]-a[low])

def contrast(by_site,left,right):
    by_site_values=[];total_pairs={b:0 for b in BANDS}
    sites_w_any={b:0 for b in BANDS}
    for k,bands in by_site.items():
        for cat in BANDS:
            total_pairs[cat]+=len(bands[cat])
            sites_w_any[cat]+=bool(bands[cat])
        if bands[left] and bands[right]:
            d=statistics.mean(bands[left])-statistics.mean(bands[right])
            by_site_values.append(d)
    if len(by_site_values)<3:
        return {"status":"INSUFFICIENT_SOURCE_SITE_REPLICATION",
                "n_site_clusters_with_both":len(by_site_values),
                "n_pairs_by_axis":total_pairs,
                "n_sites_with_any_pair_by_axis":sites_w_any,
                "mean_equal_site_difference":None,
                "bootstrap_site_percentile_interval_95":None}
    # Bootstrap independent SITE summaries, never individual species detections
    # or overlapping pair scores as independent replicates.
    rng=random.Random(BOOTSTRAP_SEED+ord(left))
    n=len(by_site_values)
    draws=[statistics.mean(rng.choice(by_site_values) for _ in range(n))
           for _ in range(BOOTSTRAP_DRAWS)]
    return {
        "status":"DESCRIPTIVE_SITE_PAIRED_CONTRAST",
        "n_site_clusters_with_both":n,
        "n_pairs_by_axis":total_pairs,
        "n_sites_with_any_pair_by_axis":sites_w_any,
        "mean_similarity_by_axis_equal_sites": {
            z: round(statistics.mean(statistics.mean(b[z])
                 for b in by_site.values() if b[z]),6)
                 if sites_w_any[z] else None for z in BANDS
        },
        "mean_equal_site_difference":round(statistics.mean(by_site_values),6),
        "site_contrast_minmax":[round(min(by_site_values),6),round(max(by_site_values),6)],
        "n_sites_positive_direction":sum(x>0 for x in by_site_values),
        "n_sites_zero_difference":sum(x==0 for x in by_site_values),
        "bootstrap_site_percentile_interval_95":[round(percentile(draws,.025),6),
                                                  round(percentile(draws,.975),6)],
        "interval_caveat":"DESCRIPTIVE six-site resampling only; no source survey-design confidence level",
    }

def source_fetch():
    u=urllib.parse.urlsplit(URL)
    if u.scheme!="https" or u.hostname!="raw.githubusercontent.com":
        raise ValueError("UNAUTHORIZED_GITHUB_SOURCE")
    req=urllib.request.Request(URL,headers={"Accept":"text/csv",
                            "User-Agent":"frogcs-public-seasonal-recurrence/7.1"})
    with urllib.request.urlopen(req,timeout=45) as response:
        fin=urllib.parse.urlsplit(response.geturl())
        if fin.scheme!="https" or fin.hostname!="raw.githubusercontent.com":
            raise ValueError("UNAUTHORIZED_REDIRECT")
        raw=response.read(4_000_001)
        if response.status!=200 or len(raw)>4_000_000:
            raise ValueError("SOURCE_TOO_LARGE_OR_BAD_STATUS")
    hashval=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if hashval!=EXPECTED_BLOB:raise ValueError("SOURCE_GIT_BLOB_CHANGED")
    return raw

def synthetic_tests():
    # Testing arithmetic/program behavior only; these are deliberately NOT
    # ecology-effect simulations or alternative analysis regimes.
    mock=[
       ("X","P1","autumn",2021,{"A","B"},5),
       ("X","P1","autumn",2022,{"A","B"},5),
       ("X","P1","winter",2021,{"C"},5),
       ("X","P2","autumn",2021,{"A"},5),
       ("Y","P1","spring",2022,{"Z"},5)
    ]
    c={ (a,b,d,y):s for a,b,d,y,s,n in mock}
    dt={ (a,b,d,y):set(range(n)) for a,b,d,y,s,n in mock}
    bands=categories(c,dt)
    assert len(bands["X"]["A"])==1 and bands["X"]["A"][0]==1.0
    assert len(bands["X"]["T"])==1 and bands["X"]["T"][0]==0.0
    assert len(bands["X"]["P"])==1 and bands["X"]["P"][0]==0.5
    assert len(bands["Y"]["A"])==0
    assert contrast(bands,"A","T")["status"]=="INSUFFICIENT_SOURCE_SITE_REPLICATION"
    assert categories(c,dt,min_positive_days=6)["X"]["A"]==[]
    assert jaccard({"A","B"},{"B","C"})==1/3
    try:valid_day("not-a-date")
    except ValueError:pass
    else:raise AssertionError("invalid date accepted")
    print("PASS: fixed annual, seasonal and plot-level positive-only set pairing, no fabricated zero")

def main():
    synthetic_tests()
    raw=source_fetch()
    cells,dates,source=parse_detection_cells(raw.decode("utf-8-sig"))
    entire=categories(cells,dates,0)
    min5=categories(cells,dates,DATE_SUPPORT_THRESHOLD)
    out={
      "status":"REAL_PUBLIC_POSITIVE_DETECTION_ASSEMBLAGE_COMPARISON",
      "source":"Hoefer et al. 2026 Zenodo v2.0 / GitHub v.2.0",
      "source_file":"data/frog_data_season.csv",
      "source_git_blob_sha1":EXPECTED_BLOB,
      "source_sha256":sha256(raw).hexdigest(),
      "data_grain":"positive species detection rows collapsed to site x plot x author season x calendar year",
      "source_record_profile":source,
      "comparisons":{
        "annual_same_season_minus_within_year_different_season":
             contrast(entire,"A","T"),
        "same_season_adjacent_plot_minus_within_year_different_season":
             contrast(entire,"P","T"),
      },
      "positive_detection_day_support_ge5_sensitivity":{
        "threshold_distinct_positive_detection_dates_per_cell":DATE_SUPPORT_THRESHOLD,
        "annual_same_season_minus_within_year_different_season":
             contrast(min5,"A","T"),
        "same_season_adjacent_plot_minus_within_year_different_season":
             contrast(min5,"P","T"),
      },
      "source_has_full_recording_effort_denominators":False,
      "unlisted_species_or_unsampled_cell_inferred_absent":False,
      "calendar_year_as_original_field_not_resolved_wetland_event":True,
      "hydrological_hysteresis_or_frog_memory_tested":False,
      "site_names_taxon_names_or_coordinates_emitted":False,
      "reproductive_success_or_occupancy_estimated":False,
      "new_synthetic_ecological_model":False,
      "main_rc6_changed":False,
    }
    p=Path(OUTPUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":
    main()
