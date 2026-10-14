#!/usr/bin/env python3
"""v7.2 actual original public frog detections: correct southern summer and test
within- vs between nominal author-labelled Dry/Wet acoustic plot assemblages.

Frozen pre-new-result in V7_2_PUBLIC_FROG_SOUTHERN_SUMMER_REPAIR_AND_PLOT_LABEL_CONTRACT.md
Exploratory. Positive detection lists only; NOT event-wide valid negatives,
wetland hydrological control, causal memory or actual occupancy.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import datetime
from io import StringIO
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import csv,json,random,statistics

import analyze_public_hoefer_seasonal_recurrence_v71 as base

LABELS={"DryA","DryB","WetA","WetB"}
MONTHS={"summer":{12,1,2},"autumn":{3,4,5},
        "winter":{6,7,8},"spring":{9,10,11}}
OUTPUT="studies/climate_landscape/receipts/HOEFER_2026_REAL_SOUTHERN_SUMMER_AND_DRY_WET_PLOT_V72.json"
SEED=20261013+72
B=5000

def season_cycle(date,season):
    dt=base.valid_day(date)
    if season not in MONTHS or dt.month not in MONTHS[season]:
        raise ValueError("SOURCE_AUTHOR_SEASON_DATE_MISMATCH")
    # Native southern summer Dec 2019–Feb 2020 is ONE summer of cycle 2020.
    return dt.year+int(season=="summer" and dt.month==12),dt

def biological_cells(raw):
    reader=csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    need={"site","plot","assessment.method","date","season","scientific.name"}
    if not reader.fieldnames or not need.issubset(reader.fieldnames):
        raise ValueError("SOURCE_COLUMNS_NOT_VERIFIED")
    cells=defaultdict(set); dates=defaultdict(set)
    sites=defaultdict(set); rows=0; nonblank=0
    for row in reader:
        rows+=1
        if None in row or len(row)!=len(reader.fieldnames):
            raise ValueError("SOURCE_ROW_WIDTH_CHANGED")
        if row["assessment.method"]!="PAM.all":raise ValueError("SOURCE_METHOD_CHANGED")
        site=row["site"].strip(); plot=row["plot"].strip()
        season=row["season"].strip().lower()
        if not site or plot not in LABELS:raise ValueError("UNRECOGNISED_AUTHOR_PLOT")
        cy,day=season_cycle(row["date"],season)
        sites[site].add(plot)
        species=row["scientific.name"].strip()
        if species and species.upper() not in {"NA","N/A","UNKNOWN"}:
            key=(site,plot,season,cy)
            cells[key].add(species)
            dates[key].add(day)
            nonblank+=1
    if rows!=13577 or len(sites)!=6 or len(cells)!=197 or any(ps!=LABELS for ps in sites.values()):
        raise ValueError("ORIGINAL_SOURCE_SCOPE_CHANGED")
    return cells,dates,{
        "source_positive_detection_rows":rows,
        "n_nonblank_taxon_detection_rows":nonblank,
        "n_author_sites":len(sites),
        "source_plot_classes":["DryA","DryB","WetA","WetB"],
        "n_positive_site_plot_season_biological_year_cells":len(cells),
        "source_cell_without_positive_records_not_fabricated":True,
        "n_distinct_detected_taxon_labels":
             len({sp for species in cells.values() for sp in species}),
    }

def pair_class(a,b):
    aa=a[:3] if a.startswith("Dry") else a[:3]
    bb=b[:3] if b.startswith("Dry") else b[:3]
    return "WITHIN" if aa==bb else "BETWEEN"

def typed_pairs(cells,dates,min_days=0):
    # Same source site, same author season, same CORRECTED cycle-year.
    groups=defaultdict(dict)
    for (site,plot,season,cycle),species in cells.items():
        if len(dates[(site,plot,season,cycle)])>=min_days:
            groups[(site,season,cycle)][plot]=species
    out=defaultdict(lambda:{"WITHIN":[],"BETWEEN":[]})
    for (site,_,_),ps in groups.items():
        for (a,b) in combinations(sorted(ps),2):
            if a not in LABELS or b not in LABELS:raise ValueError("INVALID_PLOT_PAIR")
            out[site][pair_class(a,b)].append(base.jaccard(ps[a],ps[b]))
    return out

def type_summary(by_site):
    vals=[]
    totals={k:sum(len(v[k]) for v in by_site.values()) for k in ("WITHIN","BETWEEN")}
    n_any={k:sum(bool(v[k]) for v in by_site.values()) for k in ("WITHIN","BETWEEN")}
    for site,d in by_site.items():
        if d["WITHIN"] and d["BETWEEN"]:
            vals.append(statistics.mean(d["WITHIN"])-statistics.mean(d["BETWEEN"]))
    if len(vals)<3:
        return {"status":"INSUFFICIENT_SITE_REPLICATION",
                "n_sites_with_both":len(vals),
                "n_pairs":totals,"mean_site_difference":None,"site_bootstrap95":None}
    site_means={k:statistics.mean(statistics.mean(v[k]) for v in by_site.values() if v[k])
                for k in ("WITHIN","BETWEEN")}
    rng=random.Random(SEED)
    draws=[statistics.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(B)]
    return {
        "status":"EXPLORATORY_AUTHOR_PLOT_LABEL_SIMILARITY",
        "n_sites_with_both":len(vals),
        "n_pairs":totals,
        "n_sites_with_any_pairs":n_any,
        "mean_similarity_equal_site":{k:round(v,6) for k,v in site_means.items()},
        "mean_site_difference":round(statistics.mean(vals),6),
        "n_sites_positive":sum(d>0 for d in vals),
        "n_sites_negative":sum(d<0 for d in vals),
        "site_difference_minmax":[round(min(vals),6),round(max(vals),6)],
        "site_bootstrap95":[round(base.percentile(draws,.025),6),
                            round(base.percentile(draws,.975),6)],
        "uncertainty_warning":"Six original sites only; not randomised habitat classes or effort-standardized acoustic opportunity",
    }

def tests():
    assert season_cycle("2019-12-31","summer")[0]==2020
    assert season_cycle("2020-01-01","summer")[0]==2020
    assert season_cycle("2020-02-29","summer")[0]==2020
    assert season_cycle("2020-03-01","autumn")[0]==2020
    assert season_cycle("2020-11-30","spring")[0]==2020
    try:season_cycle("2020-03-01","summer")
    except ValueError:pass
    else:raise AssertionError("unexpected date–season accepted")
    assert pair_class("DryA","DryB")=="WITHIN"
    assert pair_class("WetA","WetB")=="WITHIN"
    assert pair_class("DryA","WetB")=="BETWEEN"
    cs={("S","DryA","summer",2020):{"Sp1","Sp2"},
        ("S","DryB","summer",2020):{"Sp1"},
        ("S","WetA","summer",2020):{"Sp3"},
        ("S","WetB","summer",2020):{"Sp3"}}
    dt={k:{1,2,3,4,5} for k in cs}
    t=typed_pairs(cs,dt)
    assert len(t["S"]["WITHIN"])==2 and len(t["S"]["BETWEEN"])==4
    assert t["S"]["WITHIN"]==[.5,1.]
    assert all(x==0 for x in t["S"]["BETWEEN"])
    assert typed_pairs(cs,dt,min_days=6)=={}
    sample="site,plot,date,season,assessment.method,scientific.name\nS,DryA,2019-12-31,summer,PAM.all,Frog1\nS,DryA,2020-01-01,summer,PAM.all,Frog1\n"
    # Test grouping rule separately because actual published source-size guard must
    # never be weakened merely to make tiny tests pass.
    rr=list(csv.DictReader(StringIO(sample)))
    assert season_cycle(rr[0]["date"],rr[0]["season"])[0]==season_cycle(rr[1]["date"],rr[1]["season"])[0]
    print("PASS: summer cycle, author plot type, 2 within/4 cross pairs, invalid-season stop and no fabricated zeros")

def run():
    tests()
    raw=base.source_fetch()
    old,old_dates,prior_source=base.parse_detection_cells(raw.decode("utf-8-sig"))
    assert len(old)==216
    original=base.contrast(base.categories(old,old_dates,0),"A","T")
    if abs(original["mean_equal_site_difference"]-0.03131)>1e-6:
        raise ValueError("V71_REFERENCE_RESULT_NOT_REPRODUCED")
    cells,dates,source=biological_cells(raw)
    bands=base.categories(cells,dates,0)
    bands5=base.categories(cells,dates,5)
    types=typed_pairs(cells,dates)
    types5=typed_pairs(cells,dates,5)
    out={
        "status":"ACTUAL_PUBLISHED_PUBLIC_FROG_SUMMER_REPAIR_AND_NOMINAL_PLOT_CATEGORY_ANALYSED",
        "source":"Hoefer et al. 2026 Zenodo v2.0 public original frog_data_season.csv",
        "original_git_blob_sha1":base.EXPECTED_BLOB,
        "original_source_sha256":sha256(raw).hexdigest(),
        "frozen_contract":"studies/climate_landscape/V7_2_PUBLIC_FROG_SOUTHERN_SUMMER_REPAIR_AND_PLOT_LABEL_CONTRACT.md",
        "original_author_r_code":"https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/scripts/R_code_biodiversityFrogs.qmd",
        "source_profile":source,
        "calendar_old_cell_count":len(old),
        "biological_summer_corrected_cell_count":len(cells),
        "calendar_v71_primary_reference_reproduced":original["mean_equal_site_difference"],
        "corrected_temporal":{
            "annual_same_season_vs_cross_season":base.contrast(bands,"A","T"),
            "different_plots_vs_cross_season":base.contrast(bands,"P","T"),
        },
        "corrected_temporal_positive_dates_ge5":{
            "annual_same_season_vs_cross_season":base.contrast(bands5,"A","T"),
            "different_plots_vs_cross_season":base.contrast(bands5,"P","T"),
        },
        "nominal_author_DryWet_plot_category":{
            "all_positive_detected_cells":type_summary(types),
            "positive_detected_dates_ge5":type_summary(types5),
        },
        "source_opportunities_including_valid_silent_recordings_verified":False,
        "nominal_DryWet_labels_as_measured_local_water":False,
        "habitat_treatment_randomized":False,
        "calendar_versus_biological_cycle_rule":"summer Dec->following year, all others ordinary year",
        "hydrological_hysteresis_or_memory_tested":False,
        "site_species_coordinates_and_raw_rows_exported":False,
        "source_licence_for_audio_or_raw_file_redistribution_claimed":False,
        "v72_results_are_after_v71_aggregate_exploration":True,
        "rc6_main_modified":False
    }
    p=Path(OUTPUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":run()
