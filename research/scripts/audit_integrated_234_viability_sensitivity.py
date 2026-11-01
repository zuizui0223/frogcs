"""Source-frozen PR160 sensitivity: stage-refuge effects after original survival floor.

This is a conditional, exploratory source-resampling sensitivity. It neither
repeats nor replaces the 96-draw primary analysis. The viability flag is
defined at each original selected M,T,theta context; it DOES NOT assert
that all three counterfactual stages pass the original survival floor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

RUN_ID = 41262102436
PAIRED_SHA256 = "878bdcbb909598bc02459c1be178a9e91eddd7700e7dcc4a8c15325ba547f905"
SELECTED_SHA256 = "739ac81c0e781451537d5485a362bb1be27d9807fda03842c82ca2a0f0e82934"
COUNTS = (317, 265, 212)
SEED = 20261101
REPEATS = 20000
METRICS = (
    "delta_mean_log_F_B", "delta_pass", "delta_log_OS", "delta_log_OV",
    "delta_log_SV", "delta_log_OSV"
)
AXES = ("cover_SF", "cover_DS")
TOL = 1e-10


def source_identity_checks(paired, selected):
    if len(paired) != 576 or len(selected) != 96:
        raise AssertionError("Only the 96-source original PR160 pair table is authorized")
    if selected.draw_id.duplicated().any() or set(selected.context_id) != {0, 1, 2}:
        raise AssertionError("Wrong source draw identities or developmental strata")
    if not selected.groupby("context_id").size().eq(32).all():
        raise AssertionError("Expected 32 accepted source draws from each original context")
    key = ["source_draw_id", "axis", "counterfactual_context"]
    if paired.duplicated(key).any() or set(paired["axis"]) != set(AXES):
        raise AssertionError("Duplicate/missing source intervention identities")
    if not paired.groupby(["source_draw_id", "axis"]).counterfactual_context.nunique().eq(3).all():
        raise AssertionError("All 3 within-source counterfactual contexts required")
    if not paired.groupby("source_draw_id").size().eq(6).all():
        raise AssertionError("A 96-source draw lacks one of its six plant/stage responses")
    if set(paired.source_draw_id) != set(selected.draw_id):
        raise AssertionError("Source M,T,theta IDs differ between artifacts")
    if selected.floor_ok.isna().any() or not set(selected.edge_DS.unique()).issubset({0,1}):
        raise AssertionError("Missing original-survival-floor or directed predator edge")
    if not selected.accepted.all():
        raise AssertionError("Original selected 96 M,T,theta models must be 80y four-sign accepted")
    expected = selected.context_id.map(
        {c: COUNTS[c]/sum(COUNTS)/32.0 for c in range(3)}
    )
    if not np.allclose(selected.sample_weight, expected, rtol=0, atol=1e-12):
        raise AssertionError("Original accepted-context source weights were changed")
    j = paired.merge(
        selected[["draw_id", "context_id", "sample_weight", "floor_ok", "edge_DS"]],
        left_on="source_draw_id", right_on="draw_id", validate="many_to_one"
    )
    if (len(j) != len(paired) or
        (j.original_context != j.context_id).any() or
        not np.allclose(j.source_sample_weight, j.sample_weight, rtol=0, atol=1e-12)):
        raise AssertionError("Source identity and weight do not survive the join")
    for metric in METRICS:
        if metric not in j or not np.isfinite(j[metric]).all():
            raise AssertionError("Missing/invalid original biological response: " + metric)
    if not set(j.delta_pass.unique()).issubset({-1,0,1}):
        raise AssertionError("Invalid model-native four-sign ON/OFF changes")
    # A refuge for S against D has no biological meaning when D->S
    # predation is removed. Verify this is an exact structural null.
    inactive = j[(j["axis"] == "cover_DS") & (j.edge_DS == 0)]
    if (len(inactive) != 19*3 or
        np.max(np.abs(inactive[list(METRICS)].to_numpy(dtype=float))) > 1e-12):
        raise AssertionError("Inactive D->S network unexpectedly reacts to S refuge")
    return j


def resampled_conditional_effects(joined, condition, mask, draws=REPEATS):
    choices = joined[mask][["source_draw_id", "original_context", "source_sample_weight"]].drop_duplicates()
    choices = choices.sort_values("source_draw_id").reset_index(drop=True)
    if len(choices) < 10 or choices.source_draw_id.duplicated().any():
        raise AssertionError("Invalid subset of original independent source draws")
    orig = choices.original_context.to_numpy(dtype=int)
    expected_counts = choices.groupby("original_context").size().to_dict()
    if set(expected_counts) != {0,1,2} or min(expected_counts.values()) < 3:
        raise AssertionError("All 3 original source strata must be represented")
    base_weight = choices.source_sample_weight.to_numpy(dtype=float)
    base_weight = base_weight / base_weight.sum()
    rng = np.random.default_rng(SEED)
    idx = np.empty((draws,len(choices)), dtype=np.int32)
    for c in (0,1,2):
        local = np.flatnonzero(orig == c)
        idx[:,local] = rng.choice(local, size=(draws,len(local)), replace=True)
    wb = base_weight[idx]
    wb /= wb.sum(axis=1,keepdims=True)
    ids = choices.source_draw_id.to_numpy()
    rows = []
    for axis in AXES:
        part = joined[joined["axis"] == axis]
        for metric in METRICS:
            wide = part.pivot(index="source_draw_id",
                              columns="counterfactual_context", values=metric).loc[ids]
            a = wide.to_numpy(dtype=float)
            if a.shape != (len(choices),3) or not np.isfinite(a).all():
                raise AssertionError("Incomplete source-paired three-stage matrix")
            for c in range(3):
                v = a[:,c]
                bs = np.sum(v[idx]*wb, axis=1)
                lo,hi = np.quantile(bs,[.025,.975])
                rows.append(dict(
                    subset=condition,
                    axis=axis, counterfactual_context=c, metric=metric,
                    weighted_effect=float(np.dot(base_weight,v)),
                    bootstrap_95_low=float(lo), bootstrap_95_high=float(hi),
                    n_source_draws=len(choices),
                    n_positive=int((v > TOL).sum()),
                    n_negative=int((v < -TOL).sum()),
                    n_zero=int((np.abs(v) <= TOL).sum()),
                    source_original_context0=expected_counts[0],
                    source_original_context1=expected_counts[1],
                    source_original_context2=expected_counts[2],
                    n_bootstraps=draws,
                    uncertainty="synthetic selected-source conditional Monte Carlo, NOT field CI",
                ))
    return pd.DataFrame(rows)


def analyse(paired, selected, draws=REPEATS):
    joined = source_identity_checks(paired, selected)
    conditions = {
        "original_survival_floor_50": joined.floor_ok,
        "D_to_S_edge_active_77": joined.edge_DS == 1,
        "both_survival_floor_and_edge_37": joined.floor_ok & (joined.edge_DS == 1),
    }
    outcome = pd.concat(
        [resampled_conditional_effects(joined, name, cond, draws=draws)
         for name,cond in conditions.items()], ignore_index=True
    )
    if (len(outcome) != 3*len(AXES)*3*len(METRICS) or
        outcome.duplicated(["subset","axis","counterfactual_context","metric"]).any()):
        raise AssertionError("Original-source sensitivity table is incomplete")
    return outcome


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--paired",type=Path,required=True)
    cli.add_argument("--selected",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    cli.add_argument("--bootstrap",type=int,default=REPEATS)
    args = cli.parse_args()
    if args.bootstrap < 500:
        raise ValueError("Use at least 500 bootstrap draws")
    for file,expected in [(args.paired, PAIRED_SHA256), (args.selected,SELECTED_SHA256)]:
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        if digest != expected:
            raise AssertionError(f"Original successful GitHub source bytes changed: {file.name} {digest}")
    paired = pd.read_csv(args.paired)
    selected = pd.read_csv(args.selected)
    output = analyse(paired,selected,draws=args.bootstrap)
    args.output.mkdir(parents=True,exist_ok=True)
    output.to_csv(args.output/"original_survival_floor_stage_refuge_sensitivity.csv",index=False)
    counts=selected.groupby(["context_id","floor_ok"]).size()
    receipt=dict(
        status="FROGCS_PR160_ORIGINAL_SOURCE_FLOOR_SENSITIVITY_AUDIT_SUCCESS",
        source_github_run=RUN_ID,
        original_paired_sha256=PAIRED_SHA256,
        original_selected_sha256=SELECTED_SHA256,
        independent_original_model_draws=96,
        original_source_survival_floor_pass=int(selected.floor_ok.sum()),
        original_context_floor_pass=[int(counts.get((c,True),0)) for c in (0,1,2)],
        D_to_S_edge_active=int(selected.edge_DS.sum()),
        source_eligible_both=int((selected.floor_ok & (selected.edge_DS==1)).sum()),
        sample_size_is_not_field_replication=True,
        floor_eligibility_applies_only_to_original_selected_context=True,
        n_rows=len(output),n_bootstraps=args.bootstrap,seed=SEED,
        no_biological_rerun=True,actual_field_predation_inferred=False,
    )
    (args.output/"audit_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FROGCS_ORIGINAL_SOURCE_FLOOR_SENSITIVITY_AUDIT_SUCCESS",json.dumps(receipt))
    print(output.loc[(output.metric.isin(("delta_mean_log_F_B","delta_pass")))
                     & (output.subset=="original_survival_floor_50"),
                     ["axis","counterfactual_context","metric","weighted_effect",
                      "bootstrap_95_low","bootstrap_95_high"]].to_string(index=False))
    return output


if __name__ == "__main__":
    main()
