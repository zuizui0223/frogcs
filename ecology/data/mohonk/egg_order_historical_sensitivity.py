#!/usr/bin/env python3
"""Exploratory extension of egg first-positive records to 1931–2021.

CRITICAL: 1931–2015 Mohonk GBIF records are largely POSITIVE-ONLY and often
a single visit. They cannot establish comparable stage absences, unbiased
phenology trends or trophic interactions. This is a detection-order check.
"""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict,Counter
from datetime import date
from pathlib import Path
if __package__:
    from .analyze_egg_stage_priority import load_original
else:
    from analyze_egg_stage_priority import load_original

WOOD="Lithobates sylvaticus"
SPOT="Ambystoma maculatum"

def calculate(raw):
    visits=defaultdict(set)
    earliest={}
    for r in raw:
        d=date.fromisoformat(r["eventDate"])
        pond=(r["decimalLatitude"],r["decimalLongitude"])
        group=(pond,d.year)
        visits[group].add(d)
        if (r["scientificName"] in (WOOD,SPOT) and r["lifeStage"]=="egg"
           and int(r["individualCount"])>0):
            key=group+(r["scientificName"],)
            if key not in earliest or d<earliest[key]:earliest[key]=d
    rows=[]
    for (pond,year),dates in sorted(visits.items()):
        a=earliest.get((pond,year,WOOD))
        b=earliest.get((pond,year,SPOT))
        if a is None or b is None:continue
        n=len(dates)
        rows.append({"year":year,"survey_visits_in_year":n,
              "frog_egg_first_positive":a.isoformat(),
              "salamander_egg_first_positive":b.isoformat(),
              "spotted_minus_wood_first_detection_days":(b-a).days,
              "reporting_era":"positive_only_inconsistent" if year<=2015 else "explicit_zero_assessment_more_complete",
              "original_absence_assumed":False})
    periods=[]
    for year_min,year_max in ((1931,2015),(2016,2021),(1931,2021)):
        period=[r for r in rows if year_min<=r["year"]<=year_max]
        for visits_required in (1,2,3,4):
            kept=[r for r in period if r["survey_visits_in_year"]>=visits_required]
            gaps=[r["spotted_minus_wood_first_detection_days"] for r in kept]
            periods.append({"year_min":year_min,"year_max":year_max,
              "minimum_actual_pond_year_survey_visits":visits_required,
              "pond_years_both_species_eggs_detected":len(kept),
              "n_distinct_years":len(set(r["year"] for r in kept)),
              "wood_frog_egg_first":sum(x>0 for x in gaps),
              "same_first_survey_date":sum(x==0 for x in gaps),
              "spotted_salamander_egg_first":sum(x<0 for x in gaps),
              "not_true_oviposition_order":True})
    out={"analysis":"Mohonk_1931_2021_first_positive_egg_order_exploratory_v0_1",
        "original_archive":"GBIF-US DOI 10.15468/dypfbs source SHA256 0309abd9afa4a224287d6853d79ae1f7111a3a7bb19b0d2337f05c280ef12b34",
        "all_years_positive_detection_not_comparable_sampling":True,
        "no_egg_hatch_or_predation_outcome":True,
        "no_phenological_climate_trend_test":True,
        "no_frogcs_naamp_data":True,
        "summary_by_era_and_visit_threshold":periods}
    return rows,out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--outdir",required=True)
    a=p.parse_args()
    rows,result=calculate(load_original(a.source))
    r=next(x for x in result["summary_by_era_and_visit_threshold"]
           if x["year_min"]==1931 and x["year_max"]==2015 and x["minimum_actual_pond_year_survey_visits"]==1)
    if (r["pond_years_both_species_eggs_detected"],r["wood_frog_egg_first"],r["same_first_survey_date"],r["spotted_salamander_egg_first"])!=(129,26,98,5):
        raise RuntimeError("reproduce original pre2016 positive-only census before reporting")
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    (out/"historical_egg_first_detection_sensitivity.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    with (out/"historical_egg_order_by_pondyear.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
