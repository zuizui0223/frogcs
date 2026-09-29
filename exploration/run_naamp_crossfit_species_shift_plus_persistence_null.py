#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
EXP = ROOT / "exploration"
OUT = EXP / "NAAMP_CROSSFIT_SPECIES_SHIFT_PLUS_PERSISTENCE_RECEIPT_V0_1.json"

B = 1000
SEED = 2840223
ANCHOR = 0.75


def loadmod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


crossfit = loadmod("crossfit_base", EXP / "run_naamp_crossfit_species_shift_null.py")
uniform = crossfit.uniform
persistence = loadmod(
    "persistence_base", NAAMP / "run_naamp_persistence_preserving_null.py"
)


def simulate_combined(pair_data, hist_probs, slopes_by_train_fold, r_all, den_all, obs_betas):
    rng = np.random.default_rng(SEED)
    numer = np.zeros((B, 4), float)

    for i, dct in enumerate(pair_data):
        test_fold = dct["fold"]
        train_fold = "B" if test_fold == "A" else "A"
        slopes = slopes_by_train_fold[train_fold]

        p_hist = hist_probs[dct["key"]]
        d = dct["dry"].astype(float)
        p_anchor = (1.0 - ANCHOR) * p_hist + ANCHOR * d
        p_anchor = np.clip(p_anchor, 1e-8, 1 - 1e-8)

        gamma = np.asarray([slopes.get(sp, 0.0) for sp in dct["species"]], float)
        eta = uniform.logit(p_anchor) + gamma[:, None] * dct["rain_contrast"]
        p_species = uniform.expit(eta)

        # Preserve the observed pair-level magnitude while allowing the
        # prefixed cross-route species-specific differential response.
        q = uniform.solve_shift(p_species, dct["wet_k"])
        wsim = rng.random((B,) + q.shape) < q[None, :, :]
        comps = uniform.simulated_components(wsim, dct["dry"])
        numer += r_all[i] * comps

    betas = numer / den_all
    mean = betas.mean(axis=0)
    cov = np.cov(betas, rowvar=False, ddof=1)
    inv = np.linalg.pinv(cov)

    centered = betas - mean[None, :]
    dnull = np.einsum("bi,ij,bj->b", centered, inv, centered)
    dobs_vec = obs_betas - mean
    dobs = float(dobs_vec @ inv @ dobs_vec)
    p_omnibus = float((1 + np.sum(dnull >= dobs)) / (B + 1))

    total = betas.sum(axis=1)
    valid = np.isfinite(total) & (np.abs(total) > 1e-12)
    shares = betas[valid] / total[valid, None]
    obs_shares = obs_betas / float(obs_betas.sum())

    names = [
        "corner_expansion",
        "spatial_spread",
        "taxonomic_deepening",
        "within_core_rearrangement",
    ]

    def stat(v, obs):
        lo, hi = np.quantile(v, [0.025, 0.975])
        return {
            "null_mean": float(np.mean(v)),
            "null_ci95": [float(lo), float(hi)],
            "observed": float(obs),
            "observed_percentile": float((1 + np.sum(v <= obs)) / (len(v) + 1)),
        }

    boundary = 1.0 - shares[:, 3]
    obs_boundary = float(1.0 - obs_shares[3])

    return {
        "replicates": B,
        "seed": SEED,
        "anchor_weight": ANCHOR,
        "observed_component_betas": {
            names[j]: float(obs_betas[j]) for j in range(4)
        },
        "null_component_beta_mean": {
            names[j]: float(mean[j]) for j in range(4)
        },
        "primary_omnibus": {
            "observed_mahalanobis": dobs,
            "monte_carlo_p": p_omnibus,
            "reject_crossfit_species_shift_plus_persistence_null": bool(p_omnibus < 0.05),
        },
        "component_shares": {
            names[j]: stat(shares[:, j], obs_shares[j]) for j in range(4)
        },
        "boundary_crossing_share": stat(boundary, obs_boundary),
        "valid_share_replicates": int(valid.sum()),
    }


def main():
    (
        raw, runs, pairs, pair_data, pools, dry_ids, stops_by_key,
        sampled, ss, r_all, den_all, obs_betas
    ) = crossfit.prepare_from_raw()

    all_species = sorted({sp for species in pools.values() for sp in species})
    slopes_A, audit_A, fold_A = crossfit.fit_species_slopes(
        runs, sampled, ss, all_species, "A"
    )
    slopes_B, audit_B, fold_B = crossfit.fit_species_slopes(
        runs, sampled, ss, all_species, "B"
    )
    slopes_by_train_fold = {"A": slopes_A, "B": slopes_B}

    hist_probs = persistence.historical_cell_probs(
        pools, dry_ids, stops_by_key, ss
    )
    null = simulate_combined(
        pair_data, hist_probs, slopes_by_train_fold,
        r_all, den_all, obs_betas
    )

    common = sorted(
        sp for sp in all_species
        if audit_A[sp]["estimable"] and audit_B[sp]["estimable"]
    )

    output = {
        "analysis": "naamp_crossfit_species_shift_plus_persistence_null_v0_1",
        "contract": (
            "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json"
            "#crossfit_species_shift_plus_persistence_null"
        ),
        "n_pairs": int(len(pairs)),
        "n_routes": int(pairs["route_cluster"].nunique()),
        "route_fold_counts": {
            k: int(sum(d["fold"] == k for d in pair_data)) for k in ("A", "B")
        },
        "training_fold_A": fold_A,
        "training_fold_B": fold_B,
        "species_shift_estimability": {
            "minimum_positive_stop_cells": crossfit.MIN_POSITIVE_CELLS,
            "minimum_positive_routes": crossfit.MIN_POSITIVE_ROUTES,
            "n_estimable_both_folds": int(len(common)),
        },
        "null_result": null,
        "decision": (
            "species_plus_persistence_insufficient"
            if null["primary_omnibus"]["reject_crossfit_species_shift_plus_persistence_null"]
            else "species_plus_persistence_sufficient_under_tested_additive_null"
        ),
        "interpretation_boundary": {
            "species_shift_crossfit": True,
            "dry_state_persistence_anchor": ANCHOR,
            "species_by_site_interaction_directly_estimated": False,
            "if_rejected": (
                "Transferable species-specific rainfall response plus strong pair-specific "
                "dry-state persistence remains insufficient; additional contextual or "
                "non-additive species x site structure is required by the observed allocation."
            ),
            "causal_rainfall_claim": False,
            "submission_story_change_authorized": False,
        },
    }

    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
