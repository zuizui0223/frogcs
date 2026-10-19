#!/usr/bin/env python3
"""Post-observation taxon-list nuance: terrestrial oviposition is uncommon but real.

This second SOURCE COVERAGE report was added after viewing original NAAMP
taxon names. It is therefore explicitly post hoc and MUST NOT be treated as
a predeclared trait×soil test. Eggs, mate selection and recruitment are NOT
present in the acoustic dataset. Use pinned original three CSVs.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json
import naamp_fossorial_breeding_coverage_v0_1 as base

OUT=Path(__file__).resolve().parents[1]/"output/NAAMP_REPRODUCTIVE_MODE_SOURCE_COVERAGE_V0_1.json"
SPADEFOOT={"Scaphiopus couchii","Scaphiopus holbrookii",
           "Scaphiopus hurterii","Spea bombifrons"}
MODE={
    "Eleutherodactylus planirostris":"terrestrial_eggs_direct_development",
    **{s:"burrowing_adult_aquatic_eggs" for s in SPADEFOOT},
    "Pseudacris streckeri":"burrowing_adult_aquatic_eggs"
}
EGGS_OBSERVED=False
AUTHORITY={
  "Eleutherodactylus planirostris":"https://ask.ifas.ufl.edu/publication/UW527",
  "Pseudacris streckeri":"https://oaj.fupress.net/index.php/ah/article/view/1735",
  "spadefoot":"https://www.ncwildlife.gov/species/eastern-spadefoot"
}

def summary(rows,runs,valid_stops=None):
    labels=set(MODE.values())
    output={k:{"strong_record_count":0,
               "any_ci1plus_record_count":0,
               "distinct_routes_with_strong":0,
               "unique_taxa_with_strong":0,
               "distinct_years_with_strong":0,
               "strong_records_by_taxon":{}} for k in labels}
    byroute=defaultdict(set);bytaxa=defaultdict(set);byyear=defaultdict(set)
    for r in rows:
        rid=str(r.get("RunID") or "").strip()
        taxon=str(r.get("Species") or "").strip()
        if rid not in runs or taxon not in MODE:
            continue
        if valid_stops is not None and str(r.get("StopNumber") or "").strip() not in valid_stops.get(rid,set()):
            continue
        ci=str(r.get("CallingIndex") or "").strip()
        cat=MODE[taxon]
        if ci in {"1","2","3"}:
            output[cat]["any_ci1plus_record_count"]+=1
        if ci not in {"2","3"}:
            continue
        output[cat]["strong_record_count"]+=1
        byroute[cat].add(str(runs[rid]["route_cluster"]))
        bytaxa[cat].add(taxon)
        byyear[cat].add(int(runs[rid]["SurveyYear"]))
        dic=output[cat]["strong_records_by_taxon"]
        dic[taxon]=dic.get(taxon,0)+1
    for key,d in output.items():
        d["distinct_routes_with_strong"]=len(byroute[key])
        d["unique_taxa_with_strong"]=len(bytaxa[key])
        d["distinct_years_with_strong"]=len(byyear[key])
    return output

def main():
    raw,runs,valid=base.read_data()
    out=summary(raw["Counts.csv"],runs,valid)
    records={}
    for name,cat in MODE.items():
        records[name]={"mode":cat,
                       "strong_records":out[cat]["strong_records_by_taxon"].get(name,0)}
    payload={
        "study":"NAAMP_terrestrial_egg_and_burrowing_aquatic_egg_lifehistory_coverage_v0_1",
        "status":"POST_HOC_AFTER_SPECIES_LIST_INSPECTION_SOURCE_COUNTS_ONLY",
        "source_pins":base.read_data.__doc__ if False else {
          "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
          "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
          "Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086"},
        "records":records,
        "groups":out,
        "literature":AUTHORITY,
        "biology":{
          "greenhouse_frog_has_terrestrial_eggs_and_direct_development":True,
          "spadefoot_and_strecker_burrow_as_adults_but_deposit_eggs_in_water":True,
          "no_egg_or_tadpole_measurements_in_original_NAAMP":True,
          "acoustic_detectability_varies_by_taxon":True,
          "not_a_fossorial_vs_non_fossorial_causal_contrast":True,
          "soil_water_measured_at_route_not_burrow":True},
        "no_frog_soil_regression_computed":True,
        "do_not_modify_main":True
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False))
if __name__=="__main__":main()
