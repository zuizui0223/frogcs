#!/usr/bin/env python3
"""Response-blind factorial treatment and unit-of-randomization eligibility QA.

Read ONLY first eight treatment/grain columns of original 2026 CSIC workbook.
No survival, morphology, time, speed or other response values accessed.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from fuscus_pinned_ooxml import original_source,decode,SOURCE_SHA256

PREDICTORS=["Temperature","Pool","Predator","water_level",
            "Nest","Replicate","ID_tadpole","tadpole_density"]

def key(v):
    if v is None:return ""
    if isinstance(v,float) and v.is_integer():return str(int(v))
    return str(v).strip()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    cols,rows=decode(original_source(),PREDICTORS)
    categories=defaultdict(Counter)
    units=defaultdict(list)
    pools=defaultdict(set)
    nests=defaultdict(set)
    ids=set()
    missing=Counter()
    for r in rows:
        x={k:key(r.get(k)) for k in PREDICTORS}
        for k in PREDICTORS:
            if not x[k]:missing[k]+=1
        if not all(x[k] for k in ("Pool","Temperature","Predator","water_level","Replicate","ID_tadpole")):continue
        treatment=(x["Temperature"],x["Predator"],x["water_level"])
        for k in ("Temperature","Predator","water_level","Nest","Pool"):
            categories[k][x[k]]+=1
        units[x["Replicate"]].append(x)
        pools[x["Pool"]].add(x["Temperature"])
        nests[x["Nest"]].add(x["Replicate"])
        if x["ID_tadpole"] in ids:raise ValueError("Repeated individual ID: "+x["ID_tadpole"])
        ids.add(x["ID_tadpole"])
    combos=defaultdict(list)
    for u,rr in units.items():
        states={(x["Temperature"],x["Pool"],x["Predator"],x["water_level"],x["Nest"]) for x in rr}
        if len(states)!=1:raise ValueError("Conflicting assignment within replicate container")
        (temp,pool,pred,water,nest)=next(iter(states))
        combos[(temp,pred,water)].append(u)
    if any(len(v)!=1 for v in pools.values()):
        raise ValueError("Temperature assignment conflicts within large bath pool")
    result={
      "status":"RESPONSE_BLIND_ASSIGNMENT_ELIGIBILITY",
      "dataset":"Leptodactylus fuscus 2×2×2 water-level×predator cue×temperature trial",
      "source":"http://hdl.handle.net/10261/411885",
      "source_sha256":SOURCE_SHA256,
      "columns":cols,
      "analyzed_treatment_columns":PREDICTORS,
      "data_rows":len(rows),
      "distinct_individual_ids":len(ids),
      "distinct_small_replicate_containers":len(units),
      "distinct_large_temperature_bath_pools":len(pools),
      "treatment_value_observed":{k:dict(v) for k,v in categories.items()},
      "small_containers_per_factorial_cell":{
         "|".join(k):len(v) for k,v in sorted(combos.items())},
      "individuals_per_container_range":[min(len(x) for x in units.values()),max(len(x) for x in units.values())],
      "containers_with_less_than_three_source_rows":sum(len(x)<3 for x in units.values()),
      "empty_or_missing_predictor_field_rows":dict(missing),
      "one_temperature_per_large_pool":True,
      "source_target_protocol":"80 small containers randomized over eight treatment combos; up to three tadpoles/container; temperature assigned within eight water bath pools",
      "source_has_actual_survival_count_denominator_verified":False,
      "source_has_treatment_interaction_estimable":len(combos)==8,
      "source_has_3_predator_cue_factorial_levels":False,
      "outcome_columns_read":False,
      "original_raw_data_redistributed":False,
      "lab_predator_cue_is_predator_consumption":False,
      "controlled_drydown_is_observed_natural_pond_drought":False
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_FUSCUS_FACTORIAL_ASSIGNMENT_G0")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print("END_FUSCUS_FACTORIAL_ASSIGNMENT_G0")

if __name__=="__main__":
    main()
