"""Re-score the *saved* main 194,400 deterministic cells without any simulation.

Independent from the legacy 18-cell ranked/conditional score. Reports exactly
which definition of the balanced factorial four-direction pattern is used.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from abc_pom_main3600 import DEST, corner_contrasts, accepted_signs
from final_mechanism_common import OUT, catalog, CONTEXTS

REGEX = re.compile(r"^(none|cue_SF|risk_refuge)_[01]_\d{4}_cells\.csv\.gz$")


def main():
    src_files = sorted(p for p in OUT.glob("*_cells.csv.gz") if REGEX.fullmatch(p.name))
    if not src_files:
        raise FileNotFoundError("Missing archived full-screen *_NNNN_cells.csv.gz files")
    cols = ["model_id", "block_id", "vegetation", "S_source", "D_source", "F_B"]
    chunks = [pd.read_csv(p, usecols=cols) for p in src_files]
    full = pd.concat(chunks, ignore_index=True)
    if len(full) != 194400:
        raise AssertionError("Frozen 194,400 source cells are missing: " + str(len(full)))
    counts = full.groupby(["model_id", "block_id"], sort=True).size()
    if len(counts) != 10800 or not (counts == 18).all():
        raise AssertionError("Expected 10,800 model-context groups of 18 cells")
    if full.duplicated(["model_id", "block_id", "vegetation", "S_source", "D_source"]).any():
        raise AssertionError("Duplicate factorial cell in preserved output")
    if not np.isfinite(full.F_B).all() or (full.F_B <= 0).any():
        raise AssertionError("Non-positive or non-finite F_B")
    full = full.loc[
        full.S_source.isin([0.25, 2.0]) & full.D_source.isin([0.25, 2.0])
    ].sort_values(["model_id", "block_id", "vegetation", "S_source", "D_source"])
    if len(full) != 10800 * 8:
        raise AssertionError("Expected 8 corners per model/context")
    if not (full.groupby(["model_id", "block_id"]).size() == 8).all():
        raise AssertionError("Missing one or more corners")
    logz = np.log(full.F_B.to_numpy()).reshape(-1, 2, 2, 2)
    rawz = full.F_B.to_numpy().reshape(-1, 2, 2, 2)
    cs = corner_contrasts(logz)
    rawcs = corner_contrasts(rawz)
    groups = full.iloc[::8][["model_id", "block_id"]].reset_index(drop=True)
    for i, key in enumerate(["OS", "OV", "SV", "OSV"]):
        groups["log_" + key] = cs[:, i]
        groups["raw_" + key] = rawcs[:, i]
    groups["accepted"] = accepted_signs(cs)
    groups["raw_accepted"] = accepted_signs(rawcs)
    groups["three_signs"] = (cs[:, 0] < -1e-6) & (cs[:, 1] < -1e-6) & (cs[:, 2] > 1e-6)
    model_data = catalog()
    if model_data.model_id.nunique() != 3600:
        raise AssertionError("Catalog changed")
    groups = groups.merge(model_data, on="model_id", validate="many_to_one")
    DEST.mkdir(parents=True, exist_ok=True)
    groups.to_csv(DEST / "fixed_screen_directional_scores.csv.gz", index=False, compression="gzip")
    by_stage = groups.groupby("block_id").agg(
        groups=("model_id", "size"),
        accepted=("accepted", "sum"),
        accepted3=("three_signs", "sum"),
    )
    by_stage["accept_rate"] = by_stage.accepted / by_stage.groups
    by_stage.to_csv(DEST / "fixed_screen_stage_rates.csv")
    axes = [
        "edge_SD", "edge_DS", "cover_SF", "cover_DF", "cover_DS",
        "cover_SD", "support_DF", "support_DS", "survival", "timing",
        "reverse", "behavior", "litter",
    ]
    rows = []
    for axis in axes:
        for val, g in groups.groupby(axis):
            rows.append(dict(
                axis=axis, value=str(val), n=len(g),
                accepted=int(g.accepted.sum()), accept_rate=float(g.accepted.mean()),
                three_sign_accepted=int(g.three_signs.sum())
            ))
    pd.DataFrame(rows).to_csv(DEST / "fixed_screen_axes.csv", index=False)
    total = int(groups.accepted.sum())
    summary = {
        "source": "original main frozen 18-cell screen only; not resimulated",
        "files": len(src_files),
        "scenario_cells": 194400,
        "model_contexts": len(groups),
        "main_models": 3600,
        "accepted_log_four_sign": total,
        "accepted_log_three_sign": int(groups.three_signs.sum()),
        "accepted_raw_four_sign": int(groups.raw_accepted.sum()),
        "prior_reported_158_matches": total == 158,
        "stage_frequencies": [
            dict(block_id=int(idx), n=int(row.groups),
                 accepted=int(row.accepted), accept_rate=float(row.accept_rate),
                 context=CONTEXTS[int(idx)])
            for idx, row in by_stage.iterrows()
        ],
        "criterion": "balanced third-axis marginal OS, OV, SV and differential OSV; eps 1e-6",
        "not_abc": "This is a frozen-rate factorial structure screen, not independent structure-and-rate draws.",
    }
    (DEST / "fixed_screen_audit.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("FROZEN_MAIN_DIRECTION_AUDIT " + json.dumps({
        "source_files": len(src_files), "scenarios": 194400,
        "model_contexts": len(groups), "four_sign": total,
        "three_sign": summary["accepted_log_three_sign"],
        "claimed_158_matches": summary["prior_reported_158_matches"],
        "stage_accepted": [int(x) for x in by_stage.accepted]
    }), flush=True)
    if total != 158:
        print("CRITICAL_COMPARISON: 158 differs under explicitly stated balanced contrasts; "
              "do not claim validation of 158 without identifying the alternative formula.",
              flush=True)


if __name__ == "__main__":
    main()
