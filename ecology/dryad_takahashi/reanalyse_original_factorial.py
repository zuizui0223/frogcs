#!/usr/bin/env python3
"""Reanalyse published Takahashi 2023 Dryad egg-mass factorial, n=32.

This is a REANALYSIS of an existing published experiment, NOT a new effect,
not an estimate of predation at Mohonk field sites. No NAAMP source accessed.
Original table checksum: Dryad 10.5061/dryad.bnzs7h4gn v4.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean,stdev

import numpy as np

EXPECTED_SHA="8bf8166185fb1607710bd3bfd9a81d9f82ea34c1d8ae8874f562d5bee70076db"
LEVELS=("No","Low","Medium","High")
LAYER_TYPES=("No","Yes")
SEED=2840223
BOOTSTRAP=20000

def source_data(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=EXPECTED_SHA or len(b)!=1017:
        raise RuntimeError("Takahashi original Dryad Hatch_w.csv version/file SHA256 mismatch")
    with open(path,newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        fields={"Egg","Layers","Predation","Hatching","Days"}
        if set(rd.fieldnames or [])!=fields:
            raise ValueError("unexpected original factorial fields")
        data=list(rd)
    if len(data)!=32:raise ValueError("expect 32 independent egg masses")
    converted=[]
    for r in data:
        if r["Egg"]!="White" or r["Layers"] not in LAYER_TYPES or r["Predation"] not in LEVELS:
            raise ValueError("unexpected treatment / egg-mass class")
        h=float(r["Hatching"])
        if not (0<=h<=1 and math.isfinite(h)):raise ValueError("invalid hatching proportion")
        days=None if r["Days"].lower().strip() in ("na","", "nan") else float(r["Days"])
        if (h==0 and days is not None) or (h>0 and (days is None or days<=0)):
            raise ValueError("incubation day is undefined if nothing hatches")
        converted.append({"layers":r["Layers"],"predation":r["Predation"],
                          "hatching":h,"days":days})
    bycell=defaultdict(list)
    for r in converted:bycell[(r["layers"],r["predation"])].append(r)
    if len(bycell)!=8 or any(len(v)!=4 for v in bycell.values()):
        raise ValueError("incorrect 2×4 egg-mass randomisation groups")
    return bycell,converted

def summarize(bycell,nboot=BOOTSTRAP):
    rows=[]
    for layers in ("Yes","No"):
        for pred in LEVELS:
            raw=bycell[layers,pred]
            ys=[r["hatching"] for r in raw]
            dt=[r["days"] for r in raw if r["days"] is not None]
            rows.append({
                "jelly_layer_intact":layers=="Yes","tadpole_density_treatment":pred,
                "independent_egg_masses":len(raw),"egg_masses_with_any_hatching":sum(x>0 for x in ys),
                "mean_hatching_success_pct":round(100*mean(ys),4),
                "sd_between_egg_masses_pct":round(100*stdev(ys),4),
                "mean_incubation_days_among_egg_masses_with_hatching":round(mean(dt),4) if dt else None,
                "mean_incubation_days_missing_by_design":not bool(dt),
            })
    def avg(layer,pred):return mean(r["hatching"] for r in bycell[layer,pred])
    intact_effect=avg("Yes","High")-avg("Yes","No")
    removed_effect=avg("No","High")-avg("No","No")
    interaction=intact_effect-removed_effect
    rng=np.random.default_rng(SEED)
    means={}
    for layer in LAYER_TYPES:
        for pred in ("High","No"):
            values=np.array([x["hatching"] for x in bycell[layer,pred]],float)
            means[(layer,pred)]=values[rng.integers(0,4,size=(nboot,4))].mean(axis=1)
    draws=(means["Yes","High"]-means["Yes","No"]
           -means["No","High"]+means["No","No"])*100
    return rows,{
        "analysis":"published_salamander_egg_predation_factorial_reanalysis_v0_1",
        "source":"Takahashi & Ruszala 2023 DOI 10.1002/ece3.10427; Dryad 10.5061/dryad.bnzs7h4gn v4",
        "source_raw_sha256":EXPECTED_SHA,
        "n_egg_masses":32,"treatments":8,"n_independent_egg_masses_per_cell":4,
        "published_experiment_reanalysed_not_new_observation":True,
        "mean_intact_high_minus_no_percentage_points":round(100*intact_effect,5),
        "mean_removed_high_minus_no_percentage_points":round(100*removed_effect,5),
        "mean_difference_in_differences_percentage_points":round(100*interaction,5),
        "egg_mass_stratified_bootstrap_95pct_interval_percentage_points":[round(float(q),5) for q in np.quantile(draws,[.025,.975])],
        "bootstrap_number":nboot,"bootstrap_seed":SEED,
        "bootstrap_limits":"Only n=4 egg masses per cell; percentile bootstrap is a descriptive sensitivity, not ecological replication or a field-valid uncertainty estimate.",
        "source_correction_note":"Published authors corrected one high-predation/intact estimate that exceeded 1 to exactly 1. The original published CSV was retained unchanged; the identity of that egg mass is not separately labelled.",
        "mechanism_not_measured":"Exact egg oxygen diffusion and gel thickness were not in the raw CSV; no causal path decomposition.",
        "field_Mohonk_source_read":False,
        "cannot_infer_predation_in_Mohonk":True,
        "incubation_note":"Days='na' is missing when no embryos hatch; never impute day 0."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--outdir",required=True,type=Path)
    args=p.parse_args()
    data,_=source_data(args.source)
    cells,report=summarize(data)
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"egg_mass_factorial_reanalysis_result.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with (args.outdir/"egg_mass_factorial_cell_means.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(cells[0]));w.writeheader();w.writerows(cells)
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
