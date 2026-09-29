#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
NAAMP=ROOT/"scripts"/"naamp"
OUT=ROOT/"exploration"/"NAAMP_STRONG_NEW_ACTIVATION_DETECTION_QUALITY_RECEIPT_V0_1.json"


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


detect=loadmod("detect_base",NAAMP/"run_naamp_detection_quality_robustness.py")
base=detect.base
spatial=detect.spatial


def build_ci(raw,eligible,sampled):
    vals=defaultdict(list)
    for r in raw["Counts.csv"]:
        rid=(r.get("RunID") or "").strip()
        st=(r.get("StopNumber") or "").strip()
        sp=(r.get("Species") or "").strip()
        if rid not in eligible or st not in sampled.get(rid,set()) or not sp:
            continue
        try:
            ci=int(float((r.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci in (1,2,3):
            vals[(rid,st,sp)].append(ci)
    by=defaultdict(dict)
    for (rid,st,sp),v in vals.items():
        by[(rid,st)][sp]=max(v)
    return by


def strong_new_score(pair,sampled,by):
    wet=str(pair.wet_RunID); dry=str(pair.dry_RunID)
    stops=sorted(sampled[wet])
    if len(stops)!=10 or set(stops)!=set(sampled[dry]):
        raise RuntimeError("stop alignment failed")
    score=0.0
    for st in stops:
        wm=by.get((wet,st),{}); dm=by.get((dry,st),{})
        for sp in set(wm)|set(dm):
            w=int(wm.get(sp,0)); d=int(dm.get(sp,0))
            if d==0 and w>=2:
                score+=w
    return score


def main():
    raw=base.load()
    runs,pairs,metrics=detect.enrich_pairs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    by=build_ci(raw,eligible,sampled)
    pairs=pairs.copy()
    pairs["strong_new_score"]=[
        strong_new_score(p,sampled,by)
        for p in pairs.itertuples(index=False)
    ]

    primary=detect.complete_sample(pairs,detect.BASE_COVARS)
    if not detect.gate(primary,1500,300):
        raise SystemExit(f"primary gate failed pairs={len(primary)} routes={primary.route_cluster.nunique()}")
    pmodel=detect.fit(primary,"strong_new_score",detect.BASE_COVARS)

    exact=primary[primary["year_gap"]==1].copy()
    emodel=detect.fit(exact,"strong_new_score",detect.BASE_COVARS) if len(exact)>=100 else None

    car_covars=detect.BASE_COVARS+["car_count_difference"]
    car=detect.complete_sample(pairs,car_covars)
    car_report={
        "gate_pass":bool(detect.gate(car,750,200)),
        "n_pairs":int(len(car)),
        "n_routes":int(car.route_cluster.nunique())
    }
    if car_report["gate_pass"]:
        car_report["model"]=detect.fit(car,"strong_new_score",car_covars)

    mass_covars=[
        "rain_contrast","temp_difference","doy_difference","year_gap",
        "mass_noise_difference","timeout_difference","wind_difference"
    ]
    mass=detect.complete_sample(pairs,mass_covars)
    mass_report={
        "gate_pass":bool(detect.gate(mass,300,75)),
        "n_pairs":int(len(mass)),
        "n_routes":int(mass.route_cluster.nunique())
    }
    if mass_report["gate_pass"]:
        mass_report["model"]=detect.fit(mass,"strong_new_score",mass_covars)

    primary_pass=bool(pmodel["ci95"][0]>0)
    car_pass=(not car_report["gate_pass"]) or bool(car_report["model"]["ci95"][0]>0)
    mass_pass=(not mass_report["gate_pass"]) or bool(mass_report["model"]["ci95"][0]>0)

    output={
        "analysis":"naamp_strong_new_activation_detection_quality_v0_1",
        "contract":"exploration/NAAMP_STRONG_NEW_ACTIVATION_DETECTION_QUALITY_CONTRACT_V0_1.json",
        "primary":{
            "n_pairs":int(len(primary)),
            "n_routes":int(primary.route_cluster.nunique()),
            "model":pmodel,
        },
        "exact_consecutive_year":{
            "n_pairs":int(len(exact)),
            "n_routes":int(exact.route_cluster.nunique()),
            "model":emodel,
        },
        "car_count_sensitivity":car_report,
        "mass_noise_sensitivity":mass_report,
        "classification":{
            "primary_positive_ci":primary_pass,
            "all_available_detection_sensitivities_positive_ci":bool(primary_pass and car_pass and mass_pass)
        },
        "interpretation_boundary":{
            "recorded_detection_conditions_explain_result":False if primary_pass else None,
            "all_detectability_bias_eliminated":False,
            "causal_rainfall_claim":False
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
