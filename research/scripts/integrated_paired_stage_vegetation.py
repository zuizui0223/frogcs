"""Paired plant pathway and stage interventions *on the same accepted 80y draws*.

The source draw's structure/rates stay fixed; intervention toggles one
coefficient at a time, and each source draw is tested at all three contexts.
This is a post-ABC mechanistic prediction, not reweighted ABC re-selection.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from abc_pom_main3600 import catalog, run_subset
from final_mechanism_common import FEATURES
from integrated_80y_prepare import HERE

INTERVENTIONS = ("cover_SF", "cover_DS")
MEASURES = ("log_OS", "log_OV", "log_SV", "log_OSV",
            "raw_OS", "raw_OV", "raw_SV", "raw_OSV",
            "mean_F_B", "mean_log_F_B")


def build_matched_variants(selected):
    models = catalog().set_index("model_id")
    proposals, variants, keys = [], [], []
    serial = 0
    for p in selected.sort_values("draw_id").itertuples(index=False):
        current = models.loc[int(p.model_id), list(FEATURES)].to_dict()
        for stage in range(3):
            for axis in INTERVENTIONS:
                for enabled in (0, 1):
                    vid = 1000000 + serial
                    feature = {**current, axis: enabled}
                    feature["model_id"] = vid
                    variants.append(feature)
                    proposals.append({
                        "draw_id": serial, "model_id": vid,
                        "context_id": stage,
                        "attack": float(p.attack), "rho": float(p.rho),
                        "conversion": float(p.conversion),
                        "strength": float(p.strength),
                        "refuge_order": str(p.refuge_order),
                        "gate_code": int(p.gate_code),
                    })
                    keys.append({
                        "draw_id": serial,
                        "source_draw_id": int(p.draw_id),
                        "original_context": int(p.context_id),
                        "original_model_id": int(p.model_id),
                        "axis": axis, "enabled": enabled,
                        "counterfactual_context": stage,
                        "source_sample_weight": float(p.sample_weight),
                        "was_source": int(enabled) == int(current[axis]) and stage == int(p.context_id),
                    })
                    serial += 1
    return pd.DataFrame(proposals), pd.DataFrame(variants), pd.DataFrame(keys)


def analyse_paired(selected: pd.DataFrame, out: Path, years=80, window=20, dt=.5):
    if not np.array_equal(np.sort(selected.draw_id.unique()), np.sort(selected.draw_id)):
        raise AssertionError("Selected draws must be unique")
    proposals, variants, keys = build_matched_variants(selected)
    ans = run_subset(proposals, variants, years=years, window=window, dt=dt, chunk=48)
    outputs = ans.merge(keys, on="draw_id", validate="one_to_one")
    # Replay selected ORIGINAL model/context without any altered biology.
    original = outputs[outputs.was_source].merge(
        selected, left_on="source_draw_id", right_on="draw_id",
        suffixes=("_replayed", "_selected"), validate="many_to_one"
    )
    if len(original) != 2 * len(selected):
        raise AssertionError("Expected exactly two original-source control replays")
    maximum = 0.
    for measure in ("log_OS", "log_OV", "log_SV", "log_OSV",
                    "raw_OS", "raw_OV", "raw_SV", "raw_OSV"):
        err = np.max(np.abs(
            original[measure + "_replayed"].to_numpy(float) -
            original[measure + "_selected"].to_numpy(float)
        ))
        maximum = max(maximum, float(err))
    if maximum > 1e-8:
        raise AssertionError(f"Main original 80y replay drift: {maximum}")
    pair_key = ["source_draw_id", "axis", "counterfactual_context"]
    if outputs.duplicated(pair_key + ["enabled"]).any():
        raise AssertionError("Duplicate interventions")
    on = outputs[outputs.enabled == 1].set_index(pair_key)
    off = outputs[outputs.enabled == 0].set_index(pair_key)
    if not on.index.equals(off.index):
        on, off = on.sort_index(), off.sort_index()
    if not on.index.equals(off.index):
        raise AssertionError("Unpaired post-ABC interventions")
    paired = on[["original_context", "original_model_id", "source_sample_weight"]].copy()
    paired["pass_on"] = on.accepted.astype(bool)
    paired["pass_off"] = off.accepted.astype(bool)
    paired["delta_pass"] = paired.pass_on.astype(int) - paired.pass_off.astype(int)
    for measure in MEASURES:
        paired["delta_" + measure] = on[measure] - off[measure]
    paired["on_mean_log_F_B"] = on.mean_log_F_B
    paired["off_mean_log_F_B"] = off.mean_log_F_B
    paired = paired.reset_index()
    out.mkdir(parents=True, exist_ok=True)
    paired.to_csv(out / "posterior_paired_plant_stage.csv", index=False)
    summary = paired.groupby(["axis", "counterfactual_context"]).agg(
        n=("source_draw_id", "size"),
        passage_gain=("delta_pass", lambda x: int((x == 1).sum())),
        passage_loss=("delta_pass", lambda x: int((x == -1).sum())),
        passage_unchanged=("delta_pass", lambda x: int((x == 0).sum())),
        mean_delta_pass=("delta_pass", "mean"),
        mean_delta_log_F_B=("delta_mean_log_F_B", "mean"),
        mean_delta_log_OSV=("delta_log_OSV", "mean"),
    ).reset_index()
    summary.to_csv(out / "posterior_plant_stage_summary.csv", index=False)
    # Within-draw signed context interaction (not cross-group association).
    rows = []
    for axis, group in paired.groupby("axis"):
        wide = group.pivot(index="source_draw_id", columns="counterfactual_context",
                           values="delta_mean_log_F_B")
        for a,b in [(0,1), (0,2), (1,2)]:
            x = wide[a].to_numpy()
            y = wide[b].to_numpy()
            mask = (np.abs(x) > 1e-9) & (np.abs(y) > 1e-9)
            rows.append({
                "axis": axis, "context_a": a, "context_b": b,
                "n_same_draw": len(x),
                "n_both_nonzero": int(mask.sum()),
                "n_sign_reverse": int((np.sign(x[mask]) != np.sign(y[mask])).sum()),
                "mean_delta_effect_b_minus_a": float((y-x).mean()),
            })
    pd.DataFrame(rows).to_csv(out / "same_draw_stage_effect_reversals.csv", index=False)
    report = {
        "source_draws": len(selected),
        "original_source_replays": len(original),
        "maximum_exact_replay_error": maximum,
        "paired_intervention_rows": len(paired),
        "all_three_contexts_per_source": True,
        "statistic": "within-draw pathway ON-OFF change in mean log F_B and four-sign gate",
        "caution": "Post-selection counterfactual; not field causal effect or source-independent calibration.",
    }
    (out / "stage_intervention_audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print("INTEGRATED_PAIRED_PLANT " + json.dumps(report), flush=True)
    print("INTEGRATED_STAGE_INTERVENTIONS\n" + summary.to_string(index=False), flush=True)
    return paired


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("--source", type=Path, default=HERE/"selected_draws.csv")
    arg.add_argument("--out", type=Path, default=HERE)
    arg.add_argument("--years", type=int, default=80)
    arg.add_argument("--window", type=int, default=20)
    arg.add_argument("--dt", type=float, default=.5)
    args = arg.parse_args()
    analyse_paired(pd.read_csv(args.source), args.out,
                   years=args.years, window=args.window, dt=args.dt)
