"""Audit a completed full 80-year spatial-source artifact; no new model fitting."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from spatial_cohort_80y_bridge import MODES, PILOT_ROLES, REPLAY_TOLERANCES

KEYS = ["structure_id", "draw", "reverse_on", "vertex"]
SCORE_KEYS = KEYS[:3]
FIELDS = ["F_B", "effective_patches_F", "F_patch_cv"]
REQUIRED = {
    "model_native_spatial_vertices.csv.gz",
    "model_native_four_sign_patterns.csv",
    "paired_annual_movement_effects.csv",
    "summary_by_ontogeny_and_movement.csv",
    "receipt.json",
}


def review(root: Path):
    missing = REQUIRED - {p.name for p in root.iterdir()}
    if missing:
        raise ValueError("Missing genuine source artifact members: " + repr(sorted(missing)))
    receipt = json.loads((root / "receipt.json").read_text())
    if receipt.get("years") != 80 or receipt.get("window") != 20:
        raise AssertionError("Only full 80-year source can support scientific pilot summary")
    if receipt.get("draw_ids") != [0, 4, 8, 12] or receipt.get("draws") != 4:
        raise AssertionError("Four originally fixed rate IDs required")
    if receipt.get("patches") != 8 or receipt.get("annual_immigration_from_source_retained") is not True:
        raise AssertionError("Unapproved spatial or demographic design")
    if receipt.get("actual_local_extinction_and_recolonization_estimable") is not False:
        raise AssertionError("Cannot pretend the deterministic model measured recolonization")
    for field, tol in REPLAY_TOLERANCES.items():
        err = receipt["original_pr146_homogeneous_off_replay"][field]
        if not np.isfinite(err) or err > tol:
            raise AssertionError("PR146 annual source replay failed: " + field)

    vertices = pd.read_csv(root / "model_native_spatial_vertices.csv.gz")
    scores = pd.read_csv(root / "model_native_four_sign_patterns.csv")
    paired = pd.read_csv(root / "paired_annual_movement_effects.csv")
    expected_vertex = 3 * len(PILOT_ROLES) * 4 * 2 * 8 * len(MODES)
    expected_sign = expected_vertex // 8
    if len(vertices) != expected_vertex or len(scores) != expected_sign:
        raise AssertionError("Lost full 80y source vertices or sign patterns")
    if vertices.duplicated(KEYS + ["movement"]).any():
        raise AssertionError("Duplicated source scenario/patch vertex")
    if scores.duplicated(SCORE_KEYS + ["movement"]).any():
        raise AssertionError("Duplicated sign summaries")
    if set(vertices.movement) != set(MODES) or set(scores.movement) != set(MODES):
        raise AssertionError("Missing movement control")
    if not vertices.F_B.gt(0).all() or not vertices.effective_patches_F.between(1, 8+1e-8).all():
        raise AssertionError("Invalid native population spatial output")
    if len(paired) != (len(MODES)-1) * expected_vertex // len(MODES):
        raise AssertionError("Movement paired differences missing")

    scores["plant"] = scores.structure_id.astype(str).str.split("__").str[-1]
    vertices["plant"] = vertices.structure_id.astype(str).str.split("__").str[-1]
    if set(scores.plant) != set(PILOT_ROLES):
        raise AssertionError("Unplanned plant submodel in pilot")
    means = (vertices.groupby(["movement", "context", "plant"], sort=True)
             .agg(n_vertices=("F_B", "size"),
                  mean_F_B=("F_B", "mean"),
                  mean_effective_patches=("effective_patches_F", "mean"),
                  mean_F_patch_cv=("F_patch_cv", "mean"))
             .reset_index())

    match = (scores.groupby(["movement", "context", "plant"], sort=True)
             .agg(n_cases=("matches_log", "size"),
                  accepted_log=("matches_log", "sum"),
                  accepted_raw=("matches_raw", "sum"))
             .reset_index())
    control = scores[scores.movement.eq("off")].set_index(SCORE_KEYS).sort_index()
    paired_signs = []
    for mode in MODES[1:]:
        other = scores[scores.movement.eq(mode)].set_index(SCORE_KEYS).sort_index()
        if not other.index.equals(control.index):
            raise AssertionError("Paired model-native sign IDs missing")
        c_accept = control.matches_log.astype(bool)
        x_accept = other.matches_log.astype(bool)
        if (scores["plant"].isna()).any():
            raise AssertionError("Unrecognized plant model")
        change_any = np.zeros(len(other), dtype=bool)
        for field in ("OS", "OV", "SV", "OSV"):
            col = "sign_log_" + field
            change_any |= (other[col].to_numpy(int) != control[col].to_numpy(int))
        rows = other.reset_index()[SCORE_KEYS + ["context", "plant"]].copy()
        rows["movement"] = mode
        rows["gained_four_sign"] = (~c_accept.to_numpy()) & x_accept.to_numpy()
        rows["lost_four_sign"] = c_accept.to_numpy() & (~x_accept.to_numpy())
        rows["changed_at_least_one_sign"] = change_any
        paired_signs.append(rows)
    transitions = pd.concat(paired_signs, ignore_index=True)
    changes = (transitions.groupby(["movement", "context"], sort=True)
               .agg(n_cases=("changed_at_least_one_sign", "size"),
                    gained=("gained_four_sign", "sum"),
                    lost=("lost_four_sign", "sum"),
                    any_sign_flip=("changed_at_least_one_sign", "sum"))
               .reset_index())

    means.to_csv(root / "AUDITED_SPATIAL_RESPONSE_MEANS.csv", index=False)
    match.to_csv(root / "AUDITED_FOUR_SIGN_MATCHES.csv", index=False)
    changes.to_csv(root / "AUDITED_PAIRED_FOUR_SIGN_TRANSITIONS.csv", index=False)

    source = receipt["original_pr146_homogeneous_off_replay"]
    lines = [
        "# PR #146 source-derived 80y spatial-transport pilot (synthetic)",
        "",
        "**Status: true source run complete and post-source ID, conservation, and"
        " replay gates passed. Not field-mechanism identification.**",
        "",
        f"- Source replay abs differences: F_B={source['F_B']},"
        f" F_fraction={source['F_fraction']}, F_B_sd={source['F_B_sd']}.",
        f"- {len(vertices)} source cube vertices after patch means,"
        f" {len(scores)} factorial 4-sign evaluations (4 parameter draw IDs),"
        f" {len(paired)} matched movement-vs-off vertex effects.",
        "- **No PR #147 local recolonization estimate**: 80y source is continuous density"
        " with retained annual external immigration.",
        "",
        "## Movement-associated changes in the model-native four signs",
        "",
        changes.to_markdown(index=False),
        "",
        "## Movement × ontogeny × plant-role summaries",
        "",
        match.to_markdown(index=False),
        "",
        "## Mean F_B and spatial concentration (do NOT call patch occupancy)",
        "",
        means.to_markdown(index=False, floatfmt=".5f"),
        "",
        "The source code and four matched rate draws are predeclared."
        " Differences are properties of a finite synthetic parameter"
        " experiment, not empirical effects or robust mechanism probabilities.",
        "",
        "Next valid bridge: finite-N stage-demographic transitions on the"
        " original seasonal hazard and annual delay equations, with external"
        " immigration explicitly varied; do not add arbitrary density thresholds"
        " to manufacture local extinction.",
    ]
    (root / "AUDITED_80Y_PILOT_RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("\n".join(lines), flush=True)
    return means, match, changes


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", type=Path, required=True)
    args = p.parse_args()
    review(args.source_dir)
