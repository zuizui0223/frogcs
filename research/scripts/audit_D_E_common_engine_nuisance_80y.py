"""Independent exact-source audit: D and E outputs from SAME finite-N 80year runs.

This NEVER fits the actual 4248-site six-pattern observed data, does not
estimate a field posterior, and does not re-run the biology. Each source
vertex has 4 original hypothetical LHS rate IDs, 4 original RNG labels,
2 population-count scales and 4 actual annual movement modes. q and
movement are balanced nuisance alternatives; report sensitivity under
each, not only average model-native sign acceptance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_D_E_common_engine_nuisance_80y import (
    biological_cube,score_model_native_four_signs,
    NETWORKS,RATE_IDS,CONTEXTS,PLANTS,MODES,QS,MOVE_FRAC
)

SEEDS=(101,102,103,104)
SEED_SHARDS=((101,102),(103,104))
UNIT=["structure_id","draw","vertex","reverse_on","scale",
      "seed","movement","guild","network"]
SCORE_KEY=["network","scale","movement","seed","structure_id","draw"]
F_FIELDS=["network","scale","movement","seed","structure_id","draw",
          "context","plant_model"]


def source_gated_load(artifact_dir):
    dirs=sorted(x for x in artifact_dir.iterdir() if x.is_dir() and
                x.name.startswith("frogcs-DE-80y-q"))
    if len(dirs)!=2*4*2:
        raise AssertionError(f"Expected exactly 16 independently executed 80y source artifacts, got {len(dirs)}")
    expected={(q,mode,seeds) for q in QS for mode in MODES
              for seeds in SEED_SHARDS}
    seen=set();data=[];source_scores=[];counts=[]
    for folder in dirs:
        receipt=json.loads((folder/"receipt.json").read_text())
        q=receipt.get("scale");mode=receipt.get("movement_mode")
        labels=tuple(receipt.get("independent_rng_seed_labels",[]))
        key=(q,mode,labels)
        if key not in expected or key in seen:
            raise AssertionError("Unapproved, duplicate or selected source q/mobility/seed shard")
        seen.add(key)
        if (receipt.get("status")!="D_E_ORIGINAL_TRUE80Y_COHORT_SIGN_AND_DEMOGRAPHY_SHARD_SUCCESS"
            or receipt.get("original_source_immutable_commit")!="19d45ffb833e2970aff8d88de101736aee289d26"
            or receipt.get("years")!=80
            or receipt.get("synthetic_annual_transfer_fraction")!=MOVE_FRAC
            or receipt.get("n_source_factorial_vertices")!=128
            or receipt.get("n_biological_networks")!=len(NETWORKS)
            or receipt.get("external_immigration") is not False
            or receipt.get("site_4248_field_pattern_abc_estimated") is not False
            or receipt.get("original_biological_lhs_rate_ids")!=list(RATE_IDS)):
            raise AssertionError("Original biological 80y source design no longer fixed")
        for measure,limit in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if receipt["source_deterministic_replay_fouryear_errors"][measure]>limit:
                raise AssertionError("Original 120day+annual source method replay failed")
        frame=pd.read_csv(folder/"original_80y_guild_scenario_summary.csv.gz")
        signs=pd.read_csv(folder/"same_run_native_four_signs_and_demography.csv")
        e=pd.read_csv(folder/"original_80y_zero_to_positive_events.csv.gz")
        group_receipt=pd.read_csv(folder/"actual_return_event_group_counts.csv")
        if (len(frame)!=128*len(labels)*len(NETWORKS)*3 or
            len(signs)!=2*2*4*len(NETWORKS)*len(labels) or
            set(frame.draw)!=set(RATE_IDS) or
            set(frame.context)!=set(CONTEXTS) or
            set(frame.plant_model)!=set(PLANTS) or
            set(frame.network)!=set(NETWORKS) or
            set(frame.guild)!={"F","S","D"} or
            not frame.scale.eq(q).all() or
            set(frame.movement)!={mode} or
            set(frame.seed)!=set(labels) or
            frame.duplicated(UNIT).any() or
            int(frame.n_local_returns.sum())!=len(e) or
            len(e)!=int(group_receipt.n_return_events.sum()) or
            group_receipt.n_return_events.ne(group_receipt.n_reported_returns).any()):
            raise AssertionError("Original finite-N source/output q/mode/guild/return missing")
        if (int(frame.n_recorded_migration_arrivals.sum())!=
            int(frame.n_recorded_migration_departures.sum()) or
            frame.n_external_immigrants.ne(0).any() or
            (len(e) and e.cause_label.eq("unclassified").any())):
            raise AssertionError("Original ring transport/returns must balance")
        if len(e):
            for field,event in (
                ("n_3y_observable_returns","followup_3y_observable"),
                ("n_3y_persistent_returns","occupied_three_followups"),
                ("n_3y_persistent_with_recruitment","operational_3y_recruitment")):
                if int(frame[field].sum())!=int(e[event].sum()):
                    raise AssertionError("Genuine 3y return right-censor denominator not restored")
        if (not signs[SCORE_KEY].equals(signs[SCORE_KEY]) or
            signs.duplicated(SCORE_KEY).any() or
            set(signs.network)!=set(NETWORKS)):
            raise AssertionError("Incomplete true old-model biological 2×2×2 scores")
        recalculated=score_model_native_four_signs(frame[frame.guild.eq("F")])
        a=signs.sort_values(SCORE_KEY).reset_index(drop=True)
        b=recalculated.sort_values(SCORE_KEY).reset_index(drop=True)
        if len(a)!=len(b) or not a[SCORE_KEY].equals(b[SCORE_KEY]):
            raise AssertionError("Cannot independently reconstruct true 80y same-source 2x2x2 group")
        metrics=[c for c in b if c.startswith("beta_") or c.startswith("matches_")
                 or c.startswith("sign_") or c.startswith("f_year")
                 or c.startswith("n_local_returns_mean") or
                 c.startswith("n_local_extinctions_mean") or
                 c.startswith("n_f_vertices_zero")]
        for metric in metrics:
            if (pd.api.types.is_numeric_dtype(a[metric]) and
                not np.allclose(a[metric],b[metric],rtol=0,atol=1e-10)):
                raise AssertionError("Saved four-sign/80y outcome differs from true source "+metric)
        data.append(frame)
        source_scores.append(recalculated)
        counts.append(dict(scale=q,mode=mode,seeds=",".join(map(str,labels)),
             n_source_guild_results=int(len(frame)),
             n_true_reoccupation_events=int(len(e)),
             n_true_F_2x2x2_source_summaries=int(len(recalculated))))
    if seen!=expected:
        raise AssertionError("All fixed model nuisance/seed sources were not evaluated")
    frame=pd.concat(data,ignore_index=True)
    signs=pd.concat(source_scores,ignore_index=True)
    if (len(frame)!=2*4*4*128*len(NETWORKS)*3 or
        len(signs)!=2*4*4*2*2*4*len(NETWORKS) or
        frame.duplicated(UNIT).any() or
        signs.duplicated(SCORE_KEY).any()):
        raise AssertionError("Balanced original source q×mobility×seed network model lost")
    return frame,signs,pd.DataFrame(counts)


def summarize_all(frame,scores,shard_counts,out):
    src=biological_cube()
    if set(src.draw)!=set(RATE_IDS) or len(src)!=128:
        raise AssertionError("Original parent biological prior vectors drifted")
    # Each group has 4 hypothetical rate draws × 4 independent stochastic
    # seeds × 2 q × 4 mobility modes = 128 source-native replicate slots.
    strata=["context","plant_model","network"]
    pooled=(scores.groupby(strata,sort=True)
       .agg(n_source_models=("draw","size"),
            four_sign_rate_raw=("matches_raw","mean"),
            four_sign_rate_log1p=("matches_log1p","mean"),
            mean_year80_occupied=("f_year80_occupied_mean","mean"),
            mean_local_return_events=("n_local_returns_mean","mean"))
       .reset_index())
    if len(pooled)!=2*2*len(NETWORKS) or not pooled.n_source_models.eq(128).all():
        raise AssertionError("Cannot marginalize balanced q/mode/source rate and seed without bias")
    sensitivity=(scores.groupby(strata+["scale","movement"],sort=True)
        .agg(n_scored_source_cases=("draw","size"),
             matches_log1p=("matches_log1p","sum"),
             proportion_log1p=("matches_log1p","mean"),
             matches_raw=("matches_raw","sum"),
             proportion_raw=("matches_raw","mean"),
             mean_year80_occupied=("f_year80_occupied_mean","mean"))
        .reset_index())
    if len(sensitivity)!=len(pooled)*2*4 or not sensitivity.n_scored_source_cases.eq(16).all():
        raise AssertionError("Scale/mobility subgroups missing before assertion of robustness")
    prior=(scores.groupby(strata+["draw"],sort=True)
        .agg(n_source_models=("seed","size"),
             matched_log1p=("matches_log1p","sum"),
             proportion_log1p=("matches_log1p","mean"))
        .reset_index())
    if not prior.n_source_models.eq(2*4*4).all():
        raise AssertionError("All four rate IDs must be present under every q/mobility/seed")
    # Long-run paired movement comparisons on SAME θ, stage, vegetation,
    # predator network, count scale and RNG seed label. Random STREAM is
    # not held pathwise identical across modes by original finite-N engine.
    keys=["context","plant_model","network","draw","seed","scale","structure_id"]
    off=scores[scores.movement.eq("off")].set_index(keys).sort_index()
    moves=[]
    for mode in MODES[1:]:
        on=scores[scores.movement.eq(mode)].set_index(keys).sort_index()
        if not off.index.equals(on.index):
            raise AssertionError("Cannot match original biological θ and RNG seed")
        diff=(on[["f_year80_occupied_mean","n_local_returns_mean",
                   "n_local_extinctions_mean"]]-
              off[["f_year80_occupied_mean","n_local_returns_mean",
                   "n_local_extinctions_mean"]]).add_prefix("movement_delta_").reset_index()
        diff["movement"]=mode
        moves.append(diff)
    paired=pd.concat(moves,ignore_index=True)
    if len(paired)!=2*2*len(NETWORKS)*4*4*2*3:
        raise AssertionError("Original 80y same-θ nuisance-conditioned movement contrasts missing")
    move_summary=(paired.groupby(["context","plant_model","network","scale","movement"],sort=True)
        .agg(n_biological_rate_seed_pairs=("draw","size"),
             mean_occupancy_effect=("movement_delta_f_year80_occupied_mean","mean"),
             mean_reoccupation_effect=("movement_delta_n_local_returns_mean","mean"),
             mean_extinction_effect=("movement_delta_n_local_extinctions_mean","mean"))
        .reset_index())
    if not move_summary.n_biological_rate_seed_pairs.eq(16).all():
        raise AssertionError("Improperly matched model-native q×movement source pairs")
    # Descriptive gain/loss by q and mode, no independent field posterior.
    join_cols=["context","plant_model","network","draw","seed","structure_id","scale"]
    raw=(scores[[*join_cols,"movement","matches_log1p"]]
         .pivot(index=join_cols,columns="movement",values="matches_log1p"))
    if raw.isna().any().any():
        raise AssertionError("No complete 4-mode within-θ model-native sign comparison")
    changed=(raw[["recruits","carryover","both"]].ne(raw["off"],axis=0)).any(axis=1)
    instability=dict(n_same_source_model_theta_seed_q_groups=int(len(raw)),
                     n_groups_any_sign_match_changed_by_mobility=int(changed.sum()),
                     fraction_groups_any_sign_match_changed=float(changed.mean()))

    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    for filename,table in (
        ("source_genuine_80year_all_guild_scenarios.csv.gz",frame),
        ("same_run_model_native_F_signs_and_demography.csv",scores),
        ("balanced_q_mobility_nuisance_marginalized_mechanisms.csv",pooled),
        ("conditional_q_mobility_ABC_feasibility.csv",sensitivity),
        ("conditional_original_biological_rate_ABC_feasibility.csv",prior),
        ("same_theta_80year_movement_effects.csv",paired),
        ("same_theta_year80_movement_effects_summary.csv",move_summary),
        ("all_source_shard_return_event_audit.csv",shard_counts)):
        table.to_csv(out/filename,index=False,compression=(
            {"method":"gzip","mtime":0} if filename.endswith(".gz") else None))
    receipt=dict(status="D_E_SAME_ORIGINAL_TRUE80Y_NUISANCE_SIGN_AND_OUTCOME_AUDIT_SUCCESS",
      original_scientific_source_sha="19d45ffb833e2970aff8d88de101736aee289d26",
      n_genuine_80year_source_shards=16,
      n_original_biological_rate_draws=4,
      n_independent_rng_seed_labels=4,
      n_synthetic_population_scales=2,
      n_original_annual_movement_modes=4,
      n_paired_trophic_networks=len(NETWORKS),
      n_original_stage_contexts=len(CONTEXTS),
      n_main_legal_nominal_plant_inputs=len(PLANTS),
      n_genuine_source_scenario_guild_results=len(frame),
      n_same_run_model_native_sign_and_demography_scores=len(scores),
      n_true_zero_to_positive_returns=int(shard_counts.n_true_reoccupation_events.sum()),
      n_true_movement_vs_off_paired_source_contrasts=len(paired),
      all_model_nuisance_outcomes_preserved=True,
      original_reverse_predation_flag_on_tested=False,
      original_F_to_D_reverse_stage_null_in_two_contexts=True,
      original_256_source_prior_exhaustively_sampled=False,
      nuisance_robust_independent_of_prior_not_proven=True,
      site_mapped_six_pattern_POM_fitted=False,
      field_mechanism_posterior=False,
      matched_field_conditioned_demographic_prediction=False,
      movement_acceptance_change=instability)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    report=[
       "# Frogcs D+E SAME original 80-year biological engine — quantitative nuisance audit",
       "",
       "**These are original-source stochastic MODEL-NATIVE comparisons, not"
       " six-statistic actual NAAMP site fits or a field-conditioned posterior.**",
       "Every network was run with the same original 4 hypothetical biological"
       " rate vectors and 4 RNG labels across q3/q12 and all 4 actual annual"
       " mobility modes. The same 80-year cohort simulations emit both four"
       " source factorial interaction signs and final occupied patches,"
       " reoccupation and extinction.",
       "",
       "## Descriptive source sign feasibility integrated over nuisance alternatives",
       "",
       pooled.to_markdown(index=False,floatfmt=".3f"),
       "",
       "## Conditional q and annual movement response — all cells, including failures",
       "",
       sensitivity.to_markdown(index=False,floatfmt=".3f"),
       "",
       "## Mobility-induced changes in model-native four-sign acceptance",
       "",
       json.dumps(instability,indent=2),
       "",
       "## Same-source year80 occupancy and local reoccupation effects",
       "",
       move_summary.to_markdown(index=False,floatfmt=".3f"),
       "",
       "## Inference ceiling",
       "",
       "All comparisons use illustrative original LHS IDs 0/4/8/12, two"
       " non-orthogonal S growth×D duration source contexts and two plant"
       " settings, with frog-completed→emerging-D flag OFF in a timing-null"
       " subset. q is a hypothetical count scale, annual mobility .15 is not"
       " observed, and the first q/mobility integration is a BALANCED"
       " descriptive nuisance mixture, NOT evidence of parameter-invariant"
       " field causality. Source O/D/S supply vertices are NOT actual SDM"
       " suitabilities, and source F last20-year aquatic cohort is NOT adult"
       " NAAMP CallingIndex. The observed 4248-site six-effect quantitative"
       " POM is still a DISTINCT not-adequately-fitted layer. Do not claim"
       " an empirical posterior or wild trophic-cause identification.",
    ]
    (out/"AUDITED_SAME_ENGINE_D_E_NUISANCE_RESULTS.md").write_text(
        "\n".join(report)+"\n")
    print("D_E_SAME_ENGINE_80Y_AUDIT_SUCCESS",
          json.dumps(receipt),flush=True)
    print("D_E_NUISANCE_MARGINALIZED_SOURCE_SIGN_FEASIBILITY\n"+
          pooled.to_string(index=False),flush=True)
    print("D_E_SIGN_ACCEPTANCE_MOBILITY_CHANGE\n"+
          json.dumps(instability),flush=True)
    print("D_E_NUISANCE_CONDITIONAL_SOURCE_SIGN_FEASIBILITY\n"+
          sensitivity.to_string(index=False),flush=True)
    print("D_E_YEAR80_OCCUPANCY_MOVEMENT_EFFECTS\n"+
          move_summary.to_string(index=False),flush=True)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    frame,scores,counts=source_gated_load(a.input)
    summarize_all(frame,scores,counts,a.output)
