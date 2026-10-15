#!/usr/bin/env python3
"""Post hoc SAME-frozen-null concentration residual on source-quality eligible routes.

Source-only exact-ten SiteID gate was frozen and successfully audited before
this outcome analysis. Original cross-fitted species rain slopes are fitted on
the same original training-route folds, never optimized on 2422 geography.
Original KAPPA/ANCHOR/B=1000/random seed, prior SiteID history, wet-k shift
and regression conditioning are imported from main's frozen archived scripts.

A geographically restricted reused NAAMP subset is NOT independent replication.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

import numpy as np

import naamp_focal_metadata_geometry_join_v0_1 as sourcejoin
import naamp_terrestrial_geometry_preflight_v1 as geo
from naamp_hoc_exact_siteid_geography_sensitivity_v0_1 import (
    imported_archived_analysis,validate_keys,REF_HOC_BETA)

ROOT=Path(__file__).resolve().parents[2]
ARCH_CROSSFIT=ROOT/"exploration"/"run_naamp_higher_order_crossfit_species_history.py"
ARCH_CROSSFIT_RECEIPT=ROOT/"exploration"/"NAAMP_HIGHER_ORDER_CROSSFIT_SPECIES_HISTORY_RECEIPT_V0_1.json"
OUT=ROOT/"research/output/NAAMP_EXACT_SITEID_HOC_CROSSFIT_NULL_V0_1.json"
SOURCE_PAIRS=2422
SOURCE_ROUTES=358
B=1000
SEED=2840223+102000

def load_code():
    spec=importlib.util.spec_from_file_location("frozen_j_a_e_crossfit",ARCH_CROSSFIT)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

def main():
    archived=imported_archived_analysis()
    cross=load_code()
    if cross.B!=B or cross.ANCHOR!=0.75 or cross.KAPPA!=2.0:
        raise ValueError("old frozen null hyperparameters changed; STOP")
    original=json.loads(ARCH_CROSSFIT_RECEIPT.read_text(encoding="utf8"))
    frozen=original["prior_history_subset"]
    if frozen["n_pairs"]!=2916 or frozen["n_routes"]!=439 or \
       abs(frozen["observed"]["higher_order_beta"]-REF_HOC_BETA)>1e-8:
        raise ValueError("frozen main output reference drift")
    raw,runs,psub,dsub,hsub,asub,pools,sampled,ss=archived.final.prepare_subset()
    source=sourcejoin.produce({"Runs.csv":raw["Runs.csv"],
                              "Stops.csv":raw["Stops.csv"]},
                              geo.download_pinned_coordinates(),enforce_pins=True)
    mask=validate_keys(source,psub)
    sub=psub.loc[mask].copy().reset_index(drop=True)
    dd=[v for v,k in zip(dsub,mask) if k]
    hh=[v for v,k in zip(hsub,mask) if k]
    if len(sub)!=SOURCE_PAIRS or int(sub.route_cluster.nunique())!=SOURCE_ROUTES:
        raise ValueError("frozen source-complete exact ten siteID sample drift")

    original_rows=np.asarray([archived.metrics(d["wet"],d["dry"]) for d in dsub],float)
    rfull,denfull=archived.uniform.design_residual(psub)
    original_b=(rfull[:,None]*original_rows).sum(axis=0)/denfull
    if abs(original_b[2]-REF_HOC_BETA)>1e-8:
        raise ValueError("original 2916 higher-order beta did not reproduce")
    obsrows=original_rows[mask]
    rr,den=archived.uniform.design_residual(sub)
    obs=(rr[:,None]*obsrows).sum(axis=0)/den
    if not np.isfinite(obs).all():
        raise ValueError("source-complete observed model has nonfinite beta")
    all_species=sorted({sp for spp in pools.values() for sp in spp})
    slopes_A,auditA,foldA=cross.joint.fit_species_slopes(
        runs,sampled,ss,all_species,"A")
    slopes_B,auditB,foldB=cross.joint.fit_species_slopes(
        runs,sampled,ss,all_species,"B")
    training={"A":slopes_A,"B":slopes_B}
    sim=cross.simulate_joint(sub,dd,hh,training,rr,den,SEED)
    result=cross.conditional(sim,obs)
    out={
      "analysis":"naamp_source_complete_siteid_frozen_crossfit_null_v0_1",
      "scope":"post_hoc_source_quality_selection_sensitivity_not_independent_confirmation",
      "source_eligibility_preceded_outcome_read":True,
      "source_gate":"2012_2026_full_ten_siteids_original_route_geometry",
      "coverage":{"full_pairs":int(len(psub)),"full_routes":int(psub.route_cluster.nunique()),
                  "source_complete_pairs":int(len(sub)),
                  "source_complete_routes":int(sub.route_cluster.nunique()),
                  "states":int(sub.State.nunique())},
      "observed":{
        "full_higher_order_beta":float(original_b[2]),
        "source_complete_route_new_species_beta":float(obs[0]),
        "source_complete_extra_stop_beta":float(obs[1]),
        "source_complete_higher_order_beta":float(obs[2]),
        "source_complete_threeplus_species_beta":float(obs[3])
      },
      "original_full_reference":{
        "predicted_higher_order_beta":float(
            frozen["joint_crossfit_species_prior_history_persistence_null"]["predicted_higher_order_beta"]),
        "conditional_residual":float(
            frozen["joint_crossfit_species_prior_history_persistence_null"]["observed_conditional_residual"]),
        "p_value":float(
            frozen["joint_crossfit_species_prior_history_persistence_null"]["conditional_upper_tail_p"])
      },
      "null_training":{
        "uses_identical_original_route_crossfit_rule":True,
        "species_shift_training_includes_original_routes_no_focal_retuning":True,
        "species_training_route_folds":{"A":foldA,"B":foldB},
        "frozen_prior_history_kappa":cross.KAPPA,
        "frozen_dry_persistence_anchor":cross.ANCHOR,
        "B":B,"rng_seed":SEED
      },
      "frozen_crossfit_species_local_history_persistence_null":result,
      "classification":{
        "observed_conditional_excess_above_null_95":
             bool(result["above_upper_95"]),
        "do_not_change_JAE_main_manuscript":True},
      "interpretation_boundary":{
        "not_an_original_C1V2_landcover_result":True,
        "no_forest_connectivity_exposure":True,
        "not_an_external_independent_dataset":True,
        "not_physical_frog_movement_evidence":True,
        "not_caused_by_rainfall":True,
        "spatial_geography_gate_cannot_prove_300m_coordinate_accuracy":True,
        "selection_is_geographically_unbalanced":True
      }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({
      "analysis":out["analysis"],
      "coverage":out["coverage"],
      "observed":out["observed"],
      "original_full_reference":out["original_full_reference"],
      "source_complete_null":result,
      "interpretation_boundary":out["interpretation_boundary"]
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
