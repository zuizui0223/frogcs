#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
BASE=EXP/"run_anuraset_rainfall_threshold_replication.py"
OUT=EXP/"ANURASET_INCT41_COORDINATE_UNCERTAINTY_RECEIPT_V0_1.json"
CANDIDATES=[
    (-17.75,-48.75),
    (-17.75,-48.50),
]


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base=loadmod("anura_base",BASE)


def run_cell(lat,lon):
    base.SITE="INCT41"
    base.LAT=float(lat)
    base.LON=float(lon)
    df,spp,raw=base.parse_weak()
    dry,era5=base.era5_dry_days(df["event_date"].tolist())
    df=df.copy()
    df["dry_days"]=dry
    df["log1p_dry"]=np.log1p(df["dry_days"].astype(float))
    df["dry_z"],dry_mu,dry_sd=base.zscore(df["log1p_dry"])
    df["year_z"],year_mu,year_sd=base.zscore(df["year"].astype(float))
    rad=2*np.pi*df["event_hour"].astype(float)/24
    df["sin_hour"]=np.sin(rad)
    df["cos_hour"]=np.cos(rad)

    primary=base.package(df)
    active=base.package(df[df["total_ci"]>0].copy())

    reduced=df.copy()
    reduced["hour_bin"]=np.floor(reduced["event_hour"]).astype(int)
    reduced=reduced.sort_values("AUDIO_FILE_ID").drop_duplicates(
        ["event_date","hour_bin"],keep="first"
    ).copy()
    reduced_diag=base.package(reduced)

    return {
        "candidate_cell":[float(lat),float(lon)],
        "coverage":{
            "recordings":int(len(df)),
            "dates":int(df["event_date"].nunique()),
            "date_range":[min(df["event_date"]).isoformat(),max(df["event_date"]).isoformat()],
            "zero_anuran_recordings":int((df["total_ci"]==0).sum()),
            "species_columns":int(len(spp)),
        },
        "era5":era5,
        "dryness":{
            "dry_days_histogram":{str(k):int(v) for k,v in sorted(Counter(df["dry_days"]).items())},
            "log1p_mean":float(dry_mu),
            "log1p_sd":float(dry_sd),
        },
        "primary_all_annotated_recordings":primary,
        "sensitivity_active_recordings_only":active,
        "sensitivity_one_recording_per_date_hour":reduced_diag,
    }


def signs(result):
    m=result["primary_all_annotated_recordings"]["models"]
    return {
        x:int(np.sign(float(m[x]["beta_dry_z"])))
        for x in ("total_ci","active_richness","excess_intensity")
    }


def main():
    results=[run_cell(*c) for c in CANDIDATES]
    classes=[
        bool(x["primary_all_annotated_recordings"]["classification"]["threshold_dominant"])
        for x in results
    ]
    sigs=[signs(x) for x in results]
    robust=bool(
        len(set(classes))==1
        and all(s==sigs[0] for s in sigs[1:])
    )
    output={
        "analysis":"anuraset_inct41_coordinate_uncertainty_replication_v0_1",
        "contract":"exploration/ANURASET_RAINFALL_REPLICATION_CONTRACT_V0_1.json#inct41_coordinate_uncertainty_replication",
        "site":"INCT41",
        "biome":"Cerrado",
        "public_locality_bbox":{
            "south":-17.87,"west":-48.78,"north":-17.70,"east":-48.61
        },
        "candidate_cells":results,
        "coordinate_robust":{
            "classification_same":bool(len(set(classes))==1),
            "slope_signs_same":bool(all(s==sigs[0] for s in sigs[1:])),
            "robust_replication_classification":robust,
            "threshold_dominant_all_cells":bool(all(classes)),
            "primary_slope_signs":sigs,
        },
        "interpretation_boundary":{
            "point_coordinate_invented":False,
            "bounding_box_propagated_to_candidate_era5_cells":True,
            "spatial_boundary_replication":False,
            "causal_rainfall_claim":False,
            "submission_story_change_authorized":False,
        }
    }
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
