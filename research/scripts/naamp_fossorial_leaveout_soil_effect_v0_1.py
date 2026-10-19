#!/usr/bin/env python3
"""Existing NAAMP+ERA5 strong-chorus soil slope sensitivity to reproductive modes.

Tests one very specific proposed mechanism: does the pooled soil association
depend on identifiable burrowing adult frogs with AQUATIC eggs, or the
terrestrial-egg direct developer? Named taxa are drawn from literature
and a prior documented post hoc species-list inspection.

SOURCE controls: official NAAMP Runs/Stops/Counts hashes checked by unchanged
loader; entire original 4108-pair outcome reconstructed exactly before
dropping a single taxon. Same 4045 stable-SiteID pairs, frozen route-FE
and CR1 covariates/units as earlier analysis. Zero environmental retuning.
No claim that the remaining taxa never burrow; no eggs/juveniles observed.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
import importlib.util
import json
import time
import urllib.error

import numpy as np
import pandas as pd
import environment_within_route as study

ROOT=Path(__file__).resolve().parents[2]
LOADER=ROOT/"scripts/naamp/run_naamp_ecological_pulse.py"
FOSSORIAL_AQUATIC=frozenset({
    "Scaphiopus couchii","Scaphiopus holbrookii",
    "Scaphiopus hurterii","Spea bombifrons","Pseudacris streckeri"
})
TERRESTRIAL_EGGS=frozenset({"Eleutherodactylus planirostris"})
RESULT_NAME="OTHER_NAAMP_TAXA_NOT_NECESSARILY_NONFOSSORIAL"
CAN_DETECT_OVIPOSITION=False
EXPECTED_REFERENCE_SOIL_COEFFICIENT_PER001=0.099073

def event_count(wet,dry,stops,events):
    counts={"all":0,"burrowers_water_eggs":0,
            "terrestrial_egg_direct_developer":0,
            "all_excluding_named_special_modes":0}
    for stop in stops:
        w=events.get((wet,stop),{})
        d=events.get((dry,stop),{})
        for sp,ci in w.items():
            if ci<2 or d.get(sp,0)>0:
                continue
            counts["all"]+=1
            if sp in FOSSORIAL_AQUATIC:
                counts["burrowers_water_eggs"]+=1
            elif sp in TERRESTRIAL_EGGS:
                counts["terrestrial_egg_direct_developer"]+=1
            else:
                counts["all_excluding_named_special_modes"]+=1
    if sum(counts[k] for k in ("burrowers_water_eggs","terrestrial_egg_direct_developer",
                              "all_excluding_named_special_modes"))!=counts["all"]:
        raise AssertionError("taxon mode partition not exhaustive")
    return counts

def official_naamp_raw():
    spec=importlib.util.spec_from_file_location("pinned_naamp_reader",LOADER)
    mod=importlib.util.module_from_spec(spec);assert spec.loader
    spec.loader.exec_module(mod)
    last=None
    for i in range(6):
        try:
            out=mod.load()
            return out,mod
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
            last=e
            time.sleep(2*(i+1))
    raise RuntimeError("pinned NAAMP original source unavailable") from last

def run(cache_path:Path,out_path:Path):
    df=pd.read_csv(cache_path,compression="gzip",dtype={
         "wet_RunID":"string","dry_RunID":"string"})
    if len(df)!=4108 or df.duplicated(["wet_RunID","dry_RunID"]).any():
        raise ValueError("environment paired dataset drift or duplicate")
    raw,reader=official_naamp_raw()
    runs,sets=reader.build_runs(raw)
    if len(runs)!=7848:raise ValueError("eligible survey count changed")
    eligible=set(runs.RunID.astype(str))
    selected=set(df.wet_RunID.astype(str))|set(df.dry_RunID.astype(str))
    if not selected.issubset(eligible):
        raise ValueError("environment cache contains survey outside original NAAMP")

    stops=defaultdict(set)
    for row in raw["Stops.csv"]:
        rid=str(row.get("RunID") or "").strip()
        if rid in selected and str(row.get("SkippedStop") or "").strip()=="0":
            st=str(row.get("StopNumber") or "").strip()
            if st:stops[rid].add(st)
    if any(len(stops[rid])!=10 for rid in selected):
        raise ValueError("10-stop support incomplete; never treat missing as zero")
    events=defaultdict(dict)
    for row in raw["Counts.csv"]:
        rid=str(row.get("RunID") or "").strip()
        if rid not in selected:
            continue
        st=str(row.get("StopNumber") or "").strip()
        if st not in stops[rid]:
            continue
        taxon=str(row.get("Species") or "").strip()
        ci=str(row.get("CallingIndex") or "").strip()
        if taxon and ci in {"1","2","3"}:
            events[(rid,st)][taxon]=max(int(ci),events[(rid,st)].get(taxon,0))

    vals=[event_count(str(r.wet_RunID),str(r.dry_RunID),
                      sorted(stops[str(r.wet_RunID)]),events)
          for r in df.itertuples(index=False)]
    observed=np.asarray([v["all"] for v in vals],int)
    cached=df.strong_new_count.to_numpy()
    if not np.array_equal(observed,cached):
        bad=np.flatnonzero(observed!=cached)
        raise ValueError(f"original strong score recomputation differs at {len(bad)} pairs")
    df=df.copy()
    df["strong_new_no_named"]=np.asarray(
        [v["all_excluding_named_special_modes"] for v in vals],int)
    df["named_contribution"]=np.asarray(
        [v["burrowers_water_eggs"]+v["terrestrial_egg_direct_developer"] for v in vals],int)
    df["terrestrial_egg_contribution"]=np.asarray(
        [v["terrestrial_egg_direct_developer"] for v in vals],int)
    if not np.array_equal(df.strong_new_count,
        df.strong_new_no_named+df.named_contribution):
        raise RuntimeError("taxonomic strong-count decomposition failed")

    stable=df[df.stable_sites].copy()
    if len(stable)!=4045 or stable.route_cluster.nunique()!=563:
        raise ValueError("strict physical history cohort drift")
    a,cols=study.design(stable)
    outcomes=["strong_new_count","strong_new_no_named"]
    if int(a.named_contribution.sum())>0:
        outcomes.append("named_contribution")
    fitted=study.absorb_fit(a,outcomes,cols)
    common=fitted["strong_new_count"]["terms"]["layer_common"]["beta_per_0_01"]
    if abs(common-EXPECTED_REFERENCE_SOIL_COEFFICIENT_PER001)>2e-6:
        raise ValueError("original ERA5 route-fixed common soil slope did not reproduce")
    residual=fitted["strong_new_no_named"]["terms"]["layer_common"]
    original=fitted["strong_new_count"]["terms"]["layer_common"]
    medians={
        "known_burrowing_aquatic_count":int(sum(v["burrowers_water_eggs"] for v in vals)),
        "known_terrestrial_egg_count":int(sum(v["terrestrial_egg_direct_developer"] for v in vals)),
        "all_pair_strong_new_count":int(np.sum(observed)),
        "named_contribution_stable_pairs":int(stable.named_contribution.sum()),
        "all_strong_count_stable_pairs":int(stable.strong_new_count.sum()),
        "stable_pairs_with_named_contribution":int(np.sum(stable.named_contribution>0)),
        "stable_routes_with_named_contribution":int(stable.loc[
            stable.named_contribution>0,"route_cluster"].nunique())
    }
    result={
        "analysis":"naamp_fossorial_adult_surface_egg_vs_terrestrial_egg_leaveout_soil_v0_1",
        "status":"POST_HOC_NAMED_TAXA_EXCLUSION_NOT_A_CAUSAL_TRAIT_COMPARISON",
        "source_cache_expected_sha256":study.SOURCE_SHA,
        "matched_pair_total":len(df),"strict_site_pairs":len(stable),
        "strict_routes":int(stable.route_cluster.nunique()),
        "original_strong_endpoint_exactly_reproduced":True,
        "targeted_taxa":{
            "adult_burrow_aquatic_eggs":sorted(FOSSORIAL_AQUATIC),
            "terrestrial_eggs_direct_development":sorted(TERRESTRIAL_EGGS),
            "remaining_taxa_label":RESULT_NAME,
            "remaining_taxa_may_also_burrow":True},
        "counts":medians,
        "route_FE_CR1_original_common_soil_per001":original,
        "route_FE_CR1_after_removing_six_named_taxa_per001":residual,
        "same_sample_slope_change_per001":float(
            residual["beta_per_0_01"]-original["beta_per_0_01"]),
        "only_named_taxa_slope":(
            fitted["named_contribution"]["terms"]["layer_common"]
            if "named_contribution" in fitted else None),
        "no_egg_masses_tadpoles_or_juveniles_in_naamp":True,
        "not_direct_evidence_of_reproductive_success":True,
        "not_JAE_high_order_concentration":True,
        "soil_support_route_scale_ERA5_reanalysis_not_burrow":True,
        "no_independent_replication":True,"frozen_main_unchanged":True}
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment-cache",type=Path,required=True)
    p.add_argument("--output",type=Path,default=ROOT/
        "research/output/NAAMP_FOSSORIAL_LEAVEOUT_SOIL_V0_1.json")
    args=p.parse_args()
    run(args.environment_cache,args.output)
if __name__=="__main__":main()
