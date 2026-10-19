#!/usr/bin/env python3
"""Pinned original NAAMP sample feasibility for ADULT burrowing frog group.

Predeclared biological traits (from wildlife agency and Forest Service):
Scaphiopus and Spea dig underground when inactive but usually breed and
deposit eggs in TEMPORARY SURFACE POOLS. This is intentionally NOT a
subterranean oviposition trait. No egg masses or juvenile recruitment are
available from NAAMP CallingIndex records.

This source-only QA gates any future taxon×soil interaction test. It does
not fit a relationship to ERA5, select a significant species subset or claim
that non-spadefoot taxa do not burrow.
"""
from __future__ import annotations
import importlib.util
import json
import re
import time
import urllib.error
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"research/output/NAAMP_FOSSORIAL_BREEDING_SAMPLE_COVERAGE_V0_1.json"
SRC=ROOT/"scripts/naamp/run_naamp_ecological_pulse.py"
SPADEFOOT_TRAIT={
    "genera":["Scaphiopus","Spea"],
    "adult_fossorial":True,
    "oviposition_in_water":True,
    "oviposition_in_burrow":False,
    "test_can_prove_causal_mating_or_eggs":False,
    "verification":[
        "https://www.ncwildlife.gov/species/eastern-spadefoot",
        "https://research.fs.usda.gov/feis/species-reviews/spin"
    ]
}
MIN_STRONG_STOP_RECORDS=200
MIN_ROUTES=30

def group(raw):
    s=re.sub(r"\s+"," ",str(raw or "").replace("_"," ").strip()).lower()
    if not re.fullmatch(r"[a-z]+\s+[a-z][a-z0-9.-]*",s):
        return "unresolved_taxon_label"
    g=s.split(" ")[0]
    if g in ("scaphiopus","spea"):
        return "fossorial_aquatic_breeder"
    return "other_named_taxon"

def support_gate(n_positive,n_routes):
    return n_positive>=MIN_STRONG_STOP_RECORDS and n_routes>=MIN_ROUTES

def count_support(count_rows,run_metadata,allowed_stops=None):
    groups={}
    for label in ("fossorial_aquatic_breeder","other_named_taxon","unresolved_taxon_label"):
        groups[label]={"strong_ci2plus_records":0,
                       "distinct_routes_with_strong":0,
                       "unique_taxa_with_strong":0,
                       "distinct_years_with_strong":0}
    routes=defaultdict(set);taxa=defaultdict(set);years=defaultdict(set)
    call_unknown=0;present=defaultdict(set)
    for x in count_rows:
        rid=str(x.get("RunID") or "").strip()
        if rid not in run_metadata:
            continue
        if allowed_stops is not None and str(x.get("StopNumber") or "").strip() not in allowed_stops.get(rid,set()):
            continue
        sp=str(x.get("Species") or "").strip()
        cat=group(sp)
        if not sp:
            continue
        present[cat].add(sp)
        ci=str(x.get("CallingIndex") or "").strip()
        if ci not in {"0","1","2","3"}:
            call_unknown+=1
            continue
        if ci not in ("2","3"):
            continue
        groups[cat]["strong_ci2plus_records"]+=1
        routes[cat].add(str(run_metadata[rid]["route_cluster"]))
        taxa[cat].add(sp)
        years[cat].add(int(run_metadata[rid]["SurveyYear"]))
    for cat in groups:
        groups[cat]["distinct_routes_with_strong"]=len(routes[cat])
        groups[cat]["unique_taxa_with_strong"]=len(taxa[cat])
        groups[cat]["distinct_years_with_strong"]=len(years[cat])
        groups[cat]["all_named_taxa_with_any_call"]=sorted(present[cat])
    return {"burrowing_aquatic":groups["fossorial_aquatic_breeder"],
            "other_named":groups["other_named_taxon"],
            "unresolved":groups["unresolved_taxon_label"],
            "uninterpretable_callindex_count":call_unknown}

def read_data():
    spec=importlib.util.spec_from_file_location("original_pinned_naamp",SRC)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    last=None
    for j in range(6):
        try:
            raw=mod.load()
            break
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            last=exc
            time.sleep(2*(j+1))
    else:
        raise RuntimeError("original NAAMP source unavailable; no unpinned fallback") from last
    runs,_=mod.build_runs(raw)
    if len(runs)!=7848:
        raise ValueError(f"NAAMP pinned eligible survey count changed, {len(runs)}")
    meta={str(x.RunID):{"route_cluster":str(x.route_cluster),"SurveyYear":int(x.SurveyYear)}
          for x in runs.itertuples(index=False)}
    eligible=set(meta)
    valid=defaultdict(set)
    for x in raw["Stops.csv"]:
        rid=str(x.get("RunID") or "").strip()
        if rid in eligible and str(x.get("SkippedStop") or "").strip()=="0":
            valid[rid].add(str(x.get("StopNumber") or "").strip())
    valid={rid:stops for rid,stops in valid.items() if len(stops)==10}
    if len(valid)!=len(meta):
        raise ValueError("NAAMP eligible source ten-stop support drift")
    return raw,meta,valid

def main():
    raw,meta,valid=read_data()
    outcome=count_support(raw["Counts.csv"],meta,valid)
    b=outcome["burrowing_aquatic"]
    gate=support_gate(b["strong_ci2plus_records"],b["distinct_routes_with_strong"])
    result={
      "analysis":"naamp_fossorial_genus_breeding_trait_source_coverage_v0_1",
      "source_sha256":{
        "Runs.csv":"ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730",
        "Stops.csv":"28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f",
        "Counts.csv":"60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086"
      },
      "trait_definition":SPADEFOOT_TRAIT,
      "test_scope":"full_eligible_naamp_run_species_taxon_frequency_only",
      "eligibility":{"runs":len(meta),"routes":len({v["route_cluster"] for v in meta.values()})},
      "coverage":outcome,
      "predeclared_gate":{"minimum_strong_ci2plus_records":MIN_STRONG_STOP_RECORDS,
                          "minimum_distinct_routes":MIN_ROUTES,
                          "passed":gate,
                          "if_failed":"NO FOSSORIAL SOIL INTERACTION TEST"},
      "evidence":{"spadefoots_lay_eggs_underground":False,
                  "egg_deposition_measured_by_naamp":False,
                  "population_recruitment_measured":False,
                  "soil_mechanism_causality_established":False,
                  "trait_labels_recognized_only_if_Latin_binomial":True,
                  "non_spadefoot_is_non_fossorial":False,
                  "no_new_ERA5_extraction":True,
                  "does_not_change_frozen_main":True}
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()
