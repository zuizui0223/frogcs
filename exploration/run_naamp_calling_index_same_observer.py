#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
EXP = ROOT / "exploration"
OUT = EXP / "NAAMP_CALLING_INDEX_SAME_OBSERVER_RECEIPT_V0_1.json"


def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


calling = loadmod("calling_base", EXP / "run_naamp_calling_index_decomposition.py")
sameobs = loadmod("same_observer_base", NAAMP / "run_naamp_same_observer_robustness.py")
base = calling.base
spatial = calling.spatial


def main():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    all_pairs, selected = sameobs.same_observer_pairs(raw, runs, route_sets)

    eligible = set(runs["RunID"].astype(str))
    sampled, _ = spatial.stop_matrix(raw, eligible)
    ci, ci_by_run_stop, duplicate_audit = calling.build_calling_index(raw, eligible, sampled)

    rows = []
    for pair in selected.itertuples(index=False):
        row = pair._asdict()
        row.update(calling.pair_components(pair, sampled, ci_by_run_stop))
        rows.append(row)
    df = pd.DataFrame(rows)

    endpoints = [
        "ci_total",
        "ci_activation",
        "ci_deactivation",
        "ci_shared_intensity",
        "binary_activation_net",
        "shared_intensification_net",
        "shared_intensity_mean_delta",
    ]
    models = {name: calling.fit(df, name) for name in endpoints}

    total_beta = models["ci_total"]["beta_rain_contrast"]
    component_betas = {
        k: models[k]["beta_rain_contrast"]
        for k in ("ci_activation", "ci_deactivation", "ci_shared_intensity")
    }
    shares = {
        k: float(v / total_beta) if abs(total_beta) > 1e-12 else None
        for k, v in component_betas.items()
    }

    threshold_dominant = bool(
        total_beta > 0
        and models["ci_activation"]["ci95"][0] > 0
        and shares["ci_activation"] is not None
        and shares["ci_activation"] > 0.5
        and component_betas["ci_activation"] > component_betas["ci_shared_intensity"]
    )

    output = {
        "analysis": "naamp_calling_index_same_observer_sensitivity_v0_1",
        "contract": "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#calling_index_same_observer_sensitivity",
        "coverage": {
            "all_pairs": int(len(all_pairs)),
            "same_observer_pairs": int(len(selected)),
            "same_observer_fraction": float(len(selected) / len(all_pairs)),
            "routes": int(selected["route_cluster"].nunique()),
            "observers": int(selected["_observer_token"].nunique()),
        },
        "duplicate_audit": duplicate_audit,
        "models": models,
        "component_beta_shares_of_total": shares,
        "classification": {
            "threshold_dominant_under_same_rule": threshold_dominant,
            "rule": (
                "total beta > 0; activation 95% CI > 0; activation contribution >50% "
                "of total beta; activation beta > shared-intensity beta"
            ),
        },
        "interpretation_boundary": {
            "observer_turnover_required_for_result": False if threshold_dominant else None,
            "all_observer_bias_eliminated": False,
            "CallingIndex": "ordinal acoustic intensity, not abundance or reproductive success",
            "causal_rainfall_claim": False,
            "submission_story_change_authorized": False,
        },
    }

    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
