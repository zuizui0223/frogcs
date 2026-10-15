#!/usr/bin/env python3
"""Frozen source-only coordinate eligibility sensitivity for original NAAMP C.

The biological outcome function, rainy/dry contrasts and covariate residualization
are IMPORTED unchanged from main's archived NAAMP JAE higher-order script.
The eligible geography/physical-SiteID list was independently fixed using
Runs.csv+Stops.csv+coordinates only on 2026-10-15 BEFORE this analysis.
Outputs: observational regression coefficients and route-cluster confidence
intervals. NO pseudo-independent source-replication, forest inference or
conditional null-residual equivalence to the JAE crossfit Monte Carlo.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import math

import numpy as np
import statsmodels.formula.api as smf

import naamp_focal_metadata_geometry_join_v0_1 as sourcejoin
import naamp_terrestrial_geometry_preflight_v1 as geo

ROOT=Path(__file__).resolve().parents[2]
ARCHIVED_MAIN=ROOT/"exploration"/"run_naamp_higher_order_final_rain_history_gate.py"
SOURCE_SUBSET_EXPECTED_PAIRS=2422
SOURCE_SUBSET_EXPECTED_ROUTES=358
REF_HOC_BETA=1.6503201354367818
REF_N_FULL=2916
REF_ROUTES_FULL=439
Q=1.959963984540054

def imported_archived_analysis():
    spec=importlib.util.spec_from_file_location("original_jae_higher_order",ARCHIVED_MAIN)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

def validate_keys(source,psub):
    geokeys={(str(p["wet_rid"]),str(p["dry_rid"]))
             for p in source["source_siteid_exact10_pairs"]}
    if len(geokeys)!=SOURCE_SUBSET_EXPECTED_PAIRS:
        raise ValueError("source-only exact-SiteID pair keys drift")
    rawkeys=[(str(x.wet_RunID),str(x.dry_RunID)) for x in psub.itertuples(index=False)]
    if len(rawkeys)!=len(set(rawkeys)):
        raise ValueError("original frozen analysis has duplicate wet/dry RunID keys")
    if not geokeys.issubset(set(rawkeys)):
        raise ValueError("precommitted source-only pair keys not a subset of JAE pairs")
    chosen=np.array([key in geokeys for key in rawkeys],bool)
    if int(chosen.sum())!=SOURCE_SUBSET_EXPECTED_PAIRS:
        raise ValueError("paper/source exact-site identity sample changed")
    if int(psub.loc[chosen,"route_cluster"].nunique())!=SOURCE_SUBSET_EXPECTED_ROUTES:
        raise ValueError("paper/source exact-site identity route count changed")
    return chosen

def observed_beta(part,rows,uniform):
    if len(part)!=len(rows):
        raise ValueError("pair and outcome arrays don't match")
    r,den=uniform.design_residual(part)
    return (r[:,None]*rows).sum(axis=0)/den

def regression(part,rows):
    df=part.copy().reset_index(drop=True)
    names=("route_new_species","extra_stop","higher_order","thirdplus")
    if rows.shape!=(len(df),len(names)):
        raise ValueError("matrix shape drift")
    estimates={}
    for j,name in enumerate(names):
        df["response"]=rows[:,j]
        formula="response ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
        model=smf.ols(formula,data=df).fit(
            cov_type="cluster",cov_kwds={"groups":df["route_cluster"]})
        b=float(model.params["rain_contrast"])
        se=float(model.bse["rain_contrast"])
        estimates[name]={"rain_contrast_beta":b,"route_cluster_se":se,
                          "ci95":[b-Q*se,b+Q*se],
                          "p_clustered":float(model.pvalues["rain_contrast"]),
                          "formula":formula}
    return estimates

def main():
    archived=imported_archived_analysis()
    raw,runs,psub,dsub,hsub,asub,pools,sampled,ss=archived.final.prepare_subset()
    if len(psub)!=REF_N_FULL or psub.route_cluster.nunique()!=REF_ROUTES_FULL:
        raise ValueError("original paper JAE sample SHA/metadata drift")
    original_coord=geo.download_pinned_coordinates()
    source=sourcejoin.produce(
        {"Runs.csv":raw["Runs.csv"],"Stops.csv":raw["Stops.csv"]},
        original_coord,enforce_pins=True)
    chosen=validate_keys(source,psub)
    rows=np.asarray([archived.metrics(d["wet"],d["dry"]) for d in dsub],float)
    full=observed_beta(psub,rows,archived.uniform)
    if abs(float(full[2])-REF_HOC_BETA)>1e-8:
        raise ValueError(f"failed independent original C beta reproduction: {full[2]}")
    out={"analysis":"naamp_original_higher_order_source_geometry_gate_sensitivity_v0_1",
         "status":"POST_HOC_DESCRIPTIVE_SELECTION_SENSITIVITY",
         "source_reference":"original pinned NAAMP Runs/Stops/Counts plus coordinates",
         "source_outcome_blind_gate_run":"https://github.com/zuizui0223/frogcs/actions/runs/38725438609",
         "fixed_beta_full_reference":REF_HOC_BETA,
         "source_only_gate_preceded_outcome_readback":True,
         "source_gate_checksum_pinned":True,
         "source_pair_siteid_exact10_required":True,
         "groups":{}}
    for name,mask in (("paper_frozen_history_all",np.ones(len(chosen),bool)),
                      ("exact10_original_siteid_geocoded",chosen),
                      ("not_exact10_original_siteid",~chosen)):
        part=psub.loc[mask].copy().reset_index(drop=True)
        obs=rows[mask]
        beta=observed_beta(part,obs,archived.uniform)
        est=regression(part,obs)
        if any(abs(float(beta[i])-est[key]["rain_contrast_beta"])>1e-8
               for i,key in enumerate(("route_new_species","extra_stop","higher_order","thirdplus"))):
            raise RuntimeError("frozen FWL and clustered OLS disagree")
        out["groups"][name]={
            "pairs":int(len(part)),"routes":int(part.route_cluster.nunique()),
            "states":int(part.State.nunique()),
            "observed_frozen_higher_order_statistic":float(beta[2]),
            "descriptive_route_cluster_models":est
        }
    out["interpretation_boundary"]={
        "not_an_independent_new_dataset":True,
        "not_a_new_landcover_or_forest_effect":True,
        "not_the_original_conditional_Monte_Carlo_residual":True,
        "not_a_causal_rainfall_estimate":True,
        "selection_based_on_source_quality_not_frog_responses":True,
        "excluded_group_state_weights_differ":True,
        "no_post_selection_buffer_radius_tuning":True,
        "no_change_to_main_JAE_submission_authorized":True}
    dest=ROOT/"research/output/NAAMP_ORIGINAL_HOC_SOURCE_GATE_SENSITIVITY_V0_1.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf8")
    compact={"analysis":out["analysis"],"groups":{
       name:{"pairs":v["pairs"],"routes":v["routes"],"states":v["states"],
             "higher_order_beta":v["observed_frozen_higher_order_statistic"],
             "cluster_CI95":v["descriptive_route_cluster_models"]["higher_order"]["ci95"]}
       for name,v in out["groups"].items()}}
    print(json.dumps(compact,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
