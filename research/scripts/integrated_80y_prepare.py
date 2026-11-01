"""One 80-year ABC sample shared by selection, stage interventions and finite-N prediction.

No re-selection is permitted after inspecting the finite-N counterfactuals.
The original 20k proposal IDs/rates are recreated and checked before analysis.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from abc_pom_main3600 import (
    SEED, SOURCE_SHA, accepted_signs, catalog, draw_prior, summarize,
)

HERE = Path(__file__).resolve().parents[1] / "results/abc_pom_integrated_20261101"
SOURCE = Path(__file__).resolve().parents[1] / "results/abc_pom_main3600_80y_20261101"
SELECT_SEED = 20261102
SELECT_N = 96
CONTEXTS = (0, 1, 2)
CORE = ["model_id", "context_id", "attack", "rho", "conversion", "strength",
        "refuge_order", "gate_code"]


def load_verified_shards(path: Path, *, n: int = 20000, shards: int = 8):
    files = sorted(path.glob("shard_*.csv.gz"))
    if len(files) != shards:
        raise AssertionError(f"Missing shards: {len(files)} != {shards}")
    all_rows = pd.concat((pd.read_csv(x) for x in files), ignore_index=True)
    if len(all_rows) != n or all_rows.draw_id.nunique() != n:
        raise AssertionError("Incomplete or duplicated source proposals")
    all_rows = all_rows.sort_values("draw_id").reset_index(drop=True)
    if not np.array_equal(all_rows.draw_id.to_numpy(), np.arange(n)):
        raise AssertionError("Draw IDs must cover exactly 0..n-1")
    if not np.array_equal(
        all_rows.accepted.to_numpy(bool),
        accepted_signs(all_rows[["log_OS", "log_OV", "log_SV", "log_OSV"]].to_numpy()),
    ):
        raise AssertionError("Archived 80y accepted flags disagree with frozen rule")
    # Defensive check: output rows are still the originally seeded full-catalog prior.
    frozen = draw_prior(n, seed=SEED, models=catalog())
    for col in CORE:
        if not np.array_equal(all_rows[col].to_numpy(), frozen[col].to_numpy()):
            raise AssertionError("Nuisance or structural prior drift: " + col)
    return all_rows


def prepare(frame: pd.DataFrame, out: Path, select_n=SELECT_N) -> dict:
    """Posterior-stratified sample with explicit weights for three timing groups."""
    if select_n % len(CONTEXTS) != 0:
        raise ValueError("Selected count must be divisible by 3")
    if frame.empty or not frame.draw_id.is_unique:
        raise AssertionError("Invalid source proposal ledger")
    n = len(frame)
    summarize(frame, n=n, out=out)
    accepted = frame.loc[frame.accepted].copy()
    if len(accepted) < select_n:
        raise AssertionError("Too few prior accepted draws to select prospective cases")
    rng = np.random.default_rng(SELECT_SEED)
    per = select_n // 3
    selected = []
    counts = accepted.context_id.value_counts().to_dict()
    for context_id in CONTEXTS:
        pool = accepted[accepted.context_id == context_id]
        if len(pool) < per:
            raise AssertionError(f"Underpowered context {context_id}: {len(pool)}")
        idx = np.sort(rng.choice(pool.index.to_numpy(), size=per, replace=False))
        group = pool.loc[idx].copy()
        # Horvitz-Thompson equivalent weights, normalized to sum 1.
        group["sample_weight"] = (len(pool) / len(accepted)) / per
        group["selection_seed"] = SELECT_SEED
        selected.append(group)
    selection = pd.concat(selected, ignore_index=True).sort_values("draw_id")
    if not np.isclose(selection.sample_weight.sum(), 1., atol=1e-12):
        raise AssertionError("Selected posterior mass does not sum to one")
    out.mkdir(parents=True, exist_ok=True)
    selection.to_csv(out / "selected_draws.csv", index=False)
    # Structural × context comparisons are conditional raw-rate observations,
    # not paired causal toggles. The stage-matched toggle analysis is separate.
    axes = ["cover_SF", "cover_DS", "support_DF", "litter",
            "edge_SD", "edge_DS", "cover_DF", "behavior"]
    group_rows = []
    for axis in axes:
        for (ctx, value), g in frame.groupby(["context_id", axis], observed=True):
            count = int(g.accepted.sum())
            group_rows.append({
                "axis": axis, "context_id": int(ctx), "level": str(value),
                "n_prior": len(g), "n_accepted": count,
                "conditional_acceptance": count / len(g),
                "within_accepted_mass": count / max(1, counts[int(ctx)]),
                "not_paired": True,
            })
    pd.DataFrame(group_rows).to_csv(out / "context_structural_conditional.csv", index=False)
    terms = ["context_id", "edge_SD", "edge_DS", "cover_SF", "cover_DS"]
    combinations = frame.groupby(terms, observed=True).agg(
        n_prior=("draw_id", "size"),
        n_accepted=("accepted", "sum"),
    ).reset_index()
    combinations["accept_rate"] = combinations.n_accepted / combinations.n_prior
    combinations["accepted_mass"] = combinations.n_accepted / len(accepted)
    combinations.to_csv(out / "mechanism_stage_combinations.csv", index=False)
    summary = {
        "source_main_sha": SOURCE_SHA, "selection_period_years": 80,
        "source_proposals": n, "accepted_80year": len(accepted),
        "selected_draws": len(selection), "context_draw_counts": counts,
        "selection_seed": SELECT_SEED,
        "selection": "Equal 32 per context, randomized within 80-year accepted set",
        "weighting": "Inverse-stratum sample weights reproduce each context's accepted posterior mass",
        "decisive_prohibition": "Finite-N dynamics and site observations do NOT enter ABC acceptance.",
        "next_contract": "Use identical draw_id, structure and nuisance tuple for every intervention and prediction.",
        "limitations": "Hypothetical rate prior and model-native sign target, no field posterior.",
    }
    (out / "integrated_design.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("INTEGRATED_SELECTION " + json.dumps(summary), flush=True)
    return summary


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("--input", type=Path, default=SOURCE)
    arg.add_argument("--out", type=Path, default=HERE)
    arg.add_argument("--draws", type=int, default=20000)
    arg.add_argument("--shards", type=int, default=8)
    arg.add_argument("--selected", type=int, default=SELECT_N)
    a = arg.parse_args()
    prepare(load_verified_shards(a.input, n=a.draws, shards=a.shards), a.out, a.selected)
