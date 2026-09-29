#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
OUT = ROOT / "exploration" / "NAAMP_SPECIES_VS_SITE_AXIS_CONTRAST_RECEIPT_V0_1.json"
B = 1000
KAPPA = 2.0
ANCHOR = 0.75


def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


uniform = loadmod("uniform_base", NAAMP / "run_naamp_uniform_activation_null.py")
persistence = loadmod("persistence_base", NAAMP / "run_naamp_persistence_preserving_null.py")


def summarize(v, observed):
    lo, hi = np.quantile(v, [0.025, 0.975])
    return {
        "null_mean": float(np.mean(v)),
        "null_ci95": [float(lo), float(hi)],
        "observed": float(observed),
        "upper_tail_monte_carlo_p": float((1 + np.sum(v >= observed)) / (len(v) + 1)),
        "observed_percentile": float((1 + np.sum(v <= observed)) / (len(v) + 1)),
    }


def simulate_uniform(pair_data, probs, r_all, den_all):
    rng = np.random.default_rng(uniform.SEED + int(KAPPA * 1000))
    numer = np.zeros((B, 4), float)
    for i, dct in enumerate(pair_data):
        p = probs[dct["key"]]
        q = uniform.solve_shift(p, dct["wet_k"])
        wsim = rng.random((B,) + q.shape) < q[None, :, :]
        comps = uniform.simulated_components(wsim, dct["dry"])
        numer += r_all[i] * comps
    return numer / den_all


def simulate_persistence(pair_data, hist_probs, r_all, den_all):
    rng = np.random.default_rng(uniform.SEED + int(round(ANCHOR * 10000)))
    numer = np.zeros((B, 4), float)
    for i, dct in enumerate(pair_data):
        p_hist = hist_probs[dct["key"]]
        d = dct["dry"].astype(float)
        p_anchor = (1.0 - ANCHOR) * p_hist + ANCHOR * d
        p_anchor = np.clip(p_anchor, 1e-8, 1 - 1e-8)
        q = uniform.solve_shift(p_anchor, dct["wet_k"])
        wsim = rng.random((B,) + q.shape) < q[None, :, :]
        comps = uniform.simulated_components(wsim, dct["dry"])
        numer += r_all[i] * comps
    return numer / den_all


def contrast_from_betas(betas):
    total = betas.sum(axis=1)
    valid = np.isfinite(total) & (np.abs(total) > 1e-12)
    shares = betas[valid] / total[valid, None]
    # route-new share - new-stop share = (corner+tax) - (corner+spatial) = tax-spatial
    return shares[:, 2] - shares[:, 1]


def main():
    (
        pairs, pair_data, pools, dry_ids, sampled, ss, r_all, den_all,
        obs_betas, beta_mask, r_beta, den_beta, obs_sor_beta
    ) = uniform.prepare()

    obs_shares = obs_betas / float(obs_betas.sum())
    observed = float(obs_shares[2] - obs_shares[1])
    observed_route_new = float(obs_shares[0] + obs_shares[2])
    observed_new_stop = float(obs_shares[0] + obs_shares[1])

    stops_by_key = {d["key"]: d["stops"] for d in pair_data}
    probs = uniform.baseline_probs(KAPPA, pools, dry_ids, stops_by_key, ss)
    ub = simulate_uniform(pair_data, probs, r_all, den_all)
    uc = contrast_from_betas(ub)

    hist = persistence.historical_cell_probs(pools, dry_ids, stops_by_key, ss)
    pb = simulate_persistence(pair_data, hist, r_all, den_all)
    pc = contrast_from_betas(pb)

    u = summarize(uc, observed)
    p = summarize(pc, observed)
    support = bool(
        observed > u["null_ci95"][1]
        and observed > p["null_ci95"][1]
    )

    output = {
        "analysis": "naamp_species_vs_site_axis_contrast_v0_1",
        "contract": "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#species_vs_site_axis_contrast",
        "n_pairs": int(len(pairs)),
        "observed_component_shares": {
            "corner_expansion": float(obs_shares[0]),
            "spatial_spread": float(obs_shares[1]),
            "taxonomic_deepening": float(obs_shares[2]),
            "within_core_rearrangement": float(obs_shares[3]),
        },
        "observed_route_new_share": observed_route_new,
        "observed_new_stop_share": observed_new_stop,
        "observed_taxonomic_minus_spatial": observed,
        "uniform_kappa2": u,
        "persistence_anchor_0_75": p,
        "classification": {
            "taxonomic_axis_excess_supported_under_both_nulls": support
        },
        "interpretation_boundary": {
            "meaning": (
                "Positive excess means rainfall-associated allocation is disproportionately "
                "taxonomic (route-new species) relative to spatial (newly active stops), beyond "
                "the same contrast expected under the tested null family."
            ),
            "physiological_mechanism_identified": False,
            "causal_rainfall_claim": False,
            "submission_story_change_authorized": False,
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
