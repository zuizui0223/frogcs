#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
B = 1000
SEED = 2840223
ANCHORS = (0.50, 0.75, 0.90)
PRIMARY_ANCHOR = 0.75


def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


uniform = loadmod("uniform_base", ROOT / "run_naamp_uniform_activation_null.py")


def historical_cell_probs(pools, dry_ids, stops_by_key, ss):
    """Cell-only Jeffreys-smoothed dry-history probabilities; no species-level shrinkage."""
    out = {}
    for key, species in pools.items():
        runs = sorted(dry_ids[key])
        n = len(runs)
        if n < 1:
            raise RuntimeError(f"no dry history {key}")
        stops = stops_by_key[key]
        if len(species) == 0:
            out[key] = np.zeros((0, 10), float)
            continue
        idx = {sp: i for i, sp in enumerate(species)}
        y = np.zeros((len(species), 10), float)
        for rid in runs:
            for t, st in enumerate(stops):
                for sp in ss.get((rid, st), set()):
                    y[idx[sp], t] += 1.0
        p = (y + 0.5) / (n + 1.0)
        out[key] = np.clip(p, 1e-8, 1 - 1e-8)
    return out


def null_for_anchor(anchor, pair_data, hist_probs, r_all, den_all, obs_betas):
    rng = np.random.default_rng(SEED + int(round(anchor * 10000)))
    numer = np.zeros((B, 4), float)

    for i, dct in enumerate(pair_data):
        p_hist = hist_probs[dct["key"]]
        d = dct["dry"].astype(float)
        p_anchor = (1.0 - anchor) * p_hist + anchor * d
        p_anchor = np.clip(p_anchor, 1e-8, 1 - 1e-8)
        q = uniform.solve_shift(p_anchor, dct["wet_k"])
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
    obs_total = float(obs_betas.sum())
    obs_shares = obs_betas / obs_total

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

    share_report = {
        names[j]: stat(shares[:, j], obs_shares[j])
        for j in range(4)
    }
    boundary = 1.0 - shares[:, 3]
    obs_boundary = float(1.0 - obs_shares[3])

    return {
        "anchor_weight": float(anchor),
        "replicates": B,
        "observed_component_betas": {
            names[j]: float(obs_betas[j]) for j in range(4)
        },
        "null_component_beta_mean": {
            names[j]: float(mean[j]) for j in range(4)
        },
        "primary_omnibus": {
            "observed_mahalanobis": dobs,
            "monte_carlo_p": p_omnibus,
            "reject_persistence_preserving_uniform_activation": bool(p_omnibus < 0.05),
        },
        "component_shares": share_report,
        "boundary_crossing_share": stat(boundary, obs_boundary),
        "valid_share_replicates": int(valid.sum()),
    }


def main():
    (
        pairs,
        pair_data,
        pools,
        dry_ids,
        sampled,
        ss,
        r_all,
        den_all,
        obs_betas,
        beta_mask,
        r_beta,
        den_beta,
        obs_sor_beta,
    ) = uniform.prepare()

    stops_by_key = {}
    for dct in pair_data:
        stops_by_key[dct["key"]] = dct["stops"]

    hist_probs = historical_cell_probs(
        pools, dry_ids, stops_by_key, ss
    )

    results = {
        f"{a:.2f}": null_for_anchor(
            a, pair_data, hist_probs, r_all, den_all, obs_betas
        )
        for a in ANCHORS
    }

    primary = results[f"{PRIMARY_ANCHOR:.2f}"]
    strong = all(
        results[f"{a:.2f}"]["primary_omnibus"]["monte_carlo_p"] < 0.05
        for a in ANCHORS
    )
    primary_reject = (
        primary["primary_omnibus"]["monte_carlo_p"] < 0.05
    )
    obs_boundary = primary["boundary_crossing_share"]["observed"]
    primary_upper = primary["boundary_crossing_share"]["null_ci95"][1]
    boundary_above = bool(obs_boundary > primary_upper)

    if strong:
        decision = "strong_rejection_under_persistence_anchoring"
    elif primary_reject:
        decision = "primary_rejection_with_anchor_sensitivity"
    else:
        decision = "consistent_with_persistence_preserving_uniform_activation"

    title_authorized = bool(strong and boundary_above)

    output = {
        "analysis": "naamp_persistence_preserving_uniform_activation_null_v0_1",
        "contract": "provenance/contracts/NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json",
        "scope": "provenance/submission/RC10_SCOPE_UNFREEZE_V0_1.json",
        "decision_tree": "provenance/submission/RC10_STORY_DECISION_TREE_V0_1.json",
        "n_pairs": int(len(pairs)),
        "simulation_replicates": B,
        "seed": SEED,
        "primary_anchor_weight": PRIMARY_ANCHOR,
        "results_by_anchor": results,
        "decision": decision,
        "title_support": {
            "strong_rejection_all_anchor_weights": bool(strong),
            "observed_boundary_above_primary_95pct": boundary_above,
            "boundary_biased_title_authorized": title_authorized,
            "candidate_title": (
                "Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"
                if title_authorized else None
            ),
        },
        "comparison_to_existing_primary_null": {
            "existing_kappa2_boundary_null_mean": 0.808672,
            "existing_kappa2_within_core_null_mean": 0.191328,
            "purpose": "Assess whether strong pair-specific dry-state persistence materially changes the allocation benchmark.",
        },
        "interpretation_boundary": {
            "causal_claim_authorized": False,
            "unique_mechanism_identified": False,
            "temporary_wet_site_hypothesis_is_discussion_only": True,
            "post_readback_retuning_authorized": False,
        },
    }

    Path("NAAMP_PERSISTENCE_PRESERVING_NULL_RECEIPT_V0_1.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
