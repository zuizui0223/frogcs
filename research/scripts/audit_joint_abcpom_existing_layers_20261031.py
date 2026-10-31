"""Fail-closed inventory of currently SEPARATE frogcs ABC–POM evidence layers.

Inputs are source-pinned actual GitHub CSVs:
  site_132_summary.csv, site_132_ranking.csv (PR146),
  native_abc.csv, plant_prior.csv (PR146), q_grids.csv (PR155).

This audit does NOT merge unmatched candidate identifiers/rate vectors,
does not fit a new model, does not compute a model/field posterior, and
does not treat q-scaled synthetic occupancy as observed frog calling.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


BACKGROUNDS=("uniform","target_group")
POPULATION_Q=(3,6,9,12)
NETWORKS=("all_active","SF_only","no_SF","no_direct_predation")
REQUIRED={
    "site_132_summary.csv":("background","n_candidates","n_distinct_groups",
        "best_case","best_distance","best_patterns_within_observed_95",
        "n_all_six_patterns_within_95","no_adequate_six_pattern_case"),
    "site_132_ranking.csv":("background","case","equivalence_group","distance_mahalanobis",
        "fitted_patterns_within_marginal_95","model_O_with_S_low","obs_O_with_S_low"),
    "native_abc.csv":("scale","structure_id","n_process_rate_draws",
        "n_actual_simulations","n_unique_accepted_rate_draws","n_accepted",
        "posterior_status"),
    "plant_prior.csv":("scale","structural_prior","leading_plant_model",
        "total_prior_classes"),
    "q_grids.csv":("scale","network_arm","n_plant_roles",
        "n_plant_roles_reversal","n_seed_block_strict_reversals")
}


def read_input(folder,name):
    file=folder/name
    if not file.is_file():raise AssertionError("Required original source unavailable: "+str(file))
    raw=file.read_bytes()
    with file.open(newline="",encoding="utf-8-sig") as h:
        reader=csv.DictReader(h)
        if not reader.fieldnames or not set(REQUIRED[name]).issubset(reader.fieldnames):
            raise AssertionError("Source schema changed: "+name)
        data=list(reader)
    if not data:raise AssertionError("Empty genuine source: "+name)
    return data,hashlib.sha256(raw).hexdigest()


def audit(folder):
    source={};digests={}
    for name in REQUIRED:
        source[name],digests[name]=read_input(folder,name)

    # 132 scenario source adequacy is a per-background descriptive result,
    # NOT 132 independent ecological posterior tests.
    summary=source["site_132_summary.csv"]
    ranking=source["site_132_ranking.csv"]
    if (len(summary)!=2 or
        {r["background"] for r in summary}!=set(BACKGROUNDS)):
        raise AssertionError("Real two-background 132-site study not balanced")
    if len(ranking)!=2*132:
        raise AssertionError("Only part of the original 132 model/2 SDM source is available")
    site=[]
    for bg in BACKGROUNDS:
        s=next(r for r in summary if r["background"]==bg)
        q=[r for r in ranking if r["background"]==bg]
        if (len(q)!=132 or len({r["case"] for r in q})!=132 or
            len({r["equivalence_group"] for r in q})!=104 or
            int(s["n_candidates"])!=132 or int(s["n_distinct_groups"])!=104 or
            int(s["n_all_six_patterns_within_95"])!=0 or
            s["no_adequate_six_pattern_case"].lower()!="true"):
            raise AssertionError("No longer original site-level six-pattern adequacy result")
        ranked=sorted(q,key=lambda r:float(r["distance_mahalanobis"]))
        best=ranked[0]
        if (best["case"]!=s["best_case"] or
            abs(float(best["distance_mahalanobis"])-float(s["best_distance"]))>1e-9 or
            int(best["fitted_patterns_within_marginal_95"])!=
            int(s["best_patterns_within_observed_95"])):
            raise AssertionError("Best source site case and summary do not reconcile")
        if max(int(x["fitted_patterns_within_marginal_95"]) for x in q)>=6:
            raise AssertionError("A full adequate original case existed but report states none")
        site.append(dict(
            evidence_layer="SITE_MAPPED_OBSERVATIONAL_POM",
            background=bg,original_source_candidates=132,
            distinct_source_surfaces=104,
            adequate_to_all_six_marginal_intervals=0,
            closest_case=best["case"],
            closest_mahalanobis_distance=round(float(s["best_distance"]),5),
            closest_marginal_patterns=int(s["best_patterns_within_observed_95"]),
            observed_low_S_global_rank_corr=round(float(best["obs_O_with_S_low"]),5),
            model_low_S_global_rank_corr=round(float(best["model_O_with_S_low"]),5),
            current_field_mechanism_inference="NO_ADEQUATE_FIXED_SOURCE_MODEL"
        ))

    # Purely internal balanced-supply source ABC (different model universe).
    native=source["native_abc.csv"]
    log=[r for r in native if r["scale"]=="log"]
    if (len(log)!=12 or len({r["structure_id"] for r in log})!=12 or
        any(int(r["n_process_rate_draws"])!=256 for r in log) or
        any(int(r["n_actual_simulations"])!=512 for r in log) or
        any("HYPOTHETICAL_PRIOR" not in r["posterior_status"] for r in log)):
        raise AssertionError("Old model-native source prior conditions changed")
    accepted=sum(int(r["n_accepted"]) for r in log)
    total=sum(int(r["n_actual_simulations"]) for r in log)
    native_selected=next((r for r in log if r["structure_id"]==
                           "original__baseline__risk0"),None)
    if (native_selected is None or
        int(native_selected["n_unique_accepted_rate_draws"])!=65 or
        int(native_selected["n_accepted"])!=130 or total!=6144):
        raise AssertionError("Predeclared source 256-rate prior result not reproduced")

    # Source structural-prior sensitivity, not a unique field posterior.
    plant=[r for r in source["plant_prior.csv"] if r["scale"]=="log"]
    priors={r["structural_prior"] for r in plant}
    if (len(plant)!=3 or len(priors)!=3 or
        any(int(r["total_prior_classes"])!=108 for r in plant)):
        raise AssertionError("Original 108 canonical classes and prior sensitivity incomplete")
    roles={r["leading_plant_model"] for r in plant}
    if len(roles)<2:
        raise AssertionError("Old source plant mechanism was unexpectedly prior-invariant")

    # Distinct synthetic finite-N demographic consequences (NOT a field fit).
    grid=source["q_grids.csv"]
    if (len(grid)!=4*4 or
        {(int(r["scale"]),r["network_arm"]) for r in grid}!=
        {(q,n) for q in POPULATION_Q for n in NETWORKS}):
        raise AssertionError("Real source 4 population q-grid network factorial incomplete")
    lookup={(int(r["scale"]),r["network_arm"]):r for r in grid}
    for q in POPULATION_Q:
        for network in NETWORKS:
            row=lookup[(q,network)]
            if int(row["n_plant_roles"])!=2:raise AssertionError("Missing nominal source vegetation roles")
            expected={3:2,6:1,9:0,12:0}[q] if network in ("all_active","SF_only") else 0
            if int(row["n_plant_roles_reversal"])!=expected:
                raise AssertionError("Source strict reversal has changed: "+
                                     str((q,network)))
            # Replication is exactly 12 distinct RNG labels for each plant.
            n=int(row["n_seed_block_strict_reversals"])
            if not 0<=n<=24:raise AssertionError("Invalid source 12-seed-based reversal count")

    # IMPORTANT: source universes/candidate identities are incompatible,
    # so 0 site adequacy in the 132 library DOES NOT imply 0 matches
    # in the DIFFERENT 12/108 hypothetical biological-rate libraries.
    report=dict(
        status="EXISTING_SOURCE_ABC_POM_LAYERS_AUDITED_NOT_JOINT_POSTERIOR",
        site_real_world=dict(
            4248 if False else "n_acoustic_sites":4248,
            n_backgrounds=2,n_fixed_source_models_per_background=132,
            n_distinct_models=104,n_site_models_adequate_to_all_six=0,
            background_rows=site,
            marginal_95_not_joint_inference=True),
        model_native_prior=dict(
            n_structures=12,n_hypothetical_rate_draws_per_structure=256,
            n_paired_reverse_states=2,n_genuine_80year_runs=total,
            n_four_sign_matches=accepted,
            original_baseline_risk0_accepted_rate_draws=65,
            n_canonical_structural_classes=108,
            n_declared_plant_prior_weightings=3,
            distinct_winning_plant_roles=len(roles),
            real_site_six_pattern_calibration=False),
        longrun_q=dict(
            q=list(POPULATION_Q),
            all_active_reversals=[int(lookup[(q,"all_active")]["n_plant_roles_reversal"]) for q in POPULATION_Q],
            SF_only_reversals=[int(lookup[(q,"SF_only")]["n_plant_roles_reversal"]) for q in POPULATION_Q],
            n_nominal_plant_input_settings=2,
            each_network_seed_count=12,
            original_populations_from_wild=False),
        allowed_joint_model_selection=False,
        allowed_field_conditioned_demographic_prediction=False,
        missing_link="NO_COMMON_AUDITED_MODEL_X_RATE_X_SITE_EMISSION_X_FINITE_N_SOURCE_LIBRARY",
        input_sha256=digests)
    return report


def save(result,out):
    out.mkdir(parents=True,exist_ok=True)
    (out/"unified_abcpom_evidence_gate.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    rows=[]
    for bg in result["site_real_world"]["background_rows"]:
        rows.append(dict(layer="observed_site_6_patterns",case=bg["background"],
            tested=132,compatible=0,meaning="no adequate source among 132",
            full_joint_field_posterior="NOT_ESTIMATED"))
    model=result["model_native_prior"]
    rows.append(dict(layer="model_native_4_signs",case="12_classes_256_rates",
         tested=model["n_genuine_80year_runs"],
         compatible=model["n_four_sign_matches"],
         meaning="hypothetical_prior_conditional_balanced_cube",
         full_joint_field_posterior="NOT_ESTIMATED"))
    for q,n in zip(result["longrun_q"]["q"],
                   result["longrun_q"]["SF_only_reversals"]):
        rows.append(dict(layer="demographic_q_model_only",case="q"+str(q),
             tested=2,compatible=n,
             meaning="strict_reversal_2_nominal_plants_synthetic",
             full_joint_field_posterior="NOT_ESTIMATED"))
    with (out/"unified_abcpom_funnel.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    site=result["site_real_world"]["background_rows"]
    lines=[
       "# Frogcs existing-evidence joint ABC–POM gate",
       "",
       "**Original source outputs checked, no new biological model fit.**",
       "This is an inventory of compatible and incompatible existing layers."
       " It cannot compute a field posterior or source-matched long-run prediction.",
       "",
       "## Real-site six-pattern POM — absolute adequacy",
       "",
       "| Observed SDM background | Frozen source cases | Adequate 6/6 | Best case | Distance | Model low-S O–F rank corr | Observed same-rank corr |",
       "|---|---:|---:|---|---:|---:|---:|",
    ]
    for s in site:
        lines.append("| "+s["background"]+" | 132 | 0 | "+s["closest_case"]+
            " | "+str(s["closest_mahalanobis_distance"])+" | "+
            str(s["model_low_S_global_rank_corr"])+" | "+
            str(s["observed_low_S_global_rank_corr"])+" |")
    lines+=["",
       "## Model-native biological-rate ABC is a DIFFERENT target",
       "",
       "- Original 12 structures × 256 process-rate vectors × paired reversal"
       " flags: "+str(model["n_genuine_80year_runs"])+" genuine 80y source runs;"
       " "+str(model["n_four_sign_matches"])+" match the four idealized"
       " model-native signs, including original-baseline/no-risk 65/256"
       " independent synthetic rate draws.",
       "- 108 canonical model classes with three different structural prior"
       " weights have "+str(model["distinct_winning_plant_roles"])+
       " different leading plant roles in the log scale.",
       "- These are neither a six-pattern real-site fit nor a calibrated"
       " wild-mechanism posterior.",
       "",
       "## Model-native year80 demographic consequence under arbitrary count q",
       "",
       "| Synthetic q | SF-only / 2 source plant settings producing strict growth-dependent movement reversal |",
       "|---:|---:|",
    ]
    for q,n in zip(result["longrun_q"]["q"],result["longrun_q"]["SF_only_reversals"]):
        lines.append("| "+str(q)+" | "+str(n)+" |")
    lines+=["",
       "**Joint status: NOT ESTIMATED.** The original site-mapped 132"
       " fixed-case model space, original 12/108-class biological-rate"
       " ABC model space and selected finite-N q source models do not"
       " currently share an audited structure×rate×observation mapping."
       " A proper sequential inference must fit real-site six patterns"
       " FIRST, then propagate only actual source-matched rate vectors"
       " to year80 occupancy (which has no measured NAAMP target).",
       "",
       "The six descriptive 95% marginal site-pattern intervals are NOT"
       " a single joint 95% acceptance test. q is an artificial count"
       " scale, and the source q6/q9 tests were exploratory post-q12.",
       "",
       "Source SHA-256 for all five exact original compact files recorded"
       " in unified_abcpom_evidence_gate.json.",
    ]
    (out/"UNIFIED_ABC_POM_EXISTING_EVIDENCE_AUDIT.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(a.input_dir)
    save(r,a.out)
    print("JOINT_ABC_POM_EVIDENCE_INVENTORY_SUCCESS "+json.dumps({
        "site_backgrounds":len(r["site_real_world"]["background_rows"]),
        "site_adequate_cases":r["site_real_world"]["n_site_models_adequate_to_all_six"],
        "native_four_sign_matches":r["model_native_prior"]["n_four_sign_matches"],
        "q_sf_only_compatible":r["longrun_q"]["SF_only_reversals"],
        "joint_field_model_posterior":r["allowed_joint_model_selection"],
    }),flush=True)
