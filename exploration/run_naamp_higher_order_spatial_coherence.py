#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
OUT = ROOT / "exploration" / "NAAMP_HIGHER_ORDER_SPATIAL_COHERENCE_RECEIPT_V0_1.json"

B = 1000
KAPPA = 2.0
ANCHOR = 0.75


def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


uniform = loadmod("uniform", NAAMP / "run_naamp_uniform_activation_null.py")
persistence = loadmod("persistence", NAAMP / "run_naamp_persistence_preserving_null.py")


def metrics(w, d):
    """Observed pair endpoints from wet/dry binary species x stop matrices."""
    d_route = d.any(axis=1)
    route_new = (~d_route) & w.any(axis=1)
    if not np.any(route_new):
        return np.asarray([0.0, 0.0, 0.0, 0.0])

    k = w[route_new].sum(axis=1).astype(float)
    extra = np.maximum(k - 1.0, 0.0)
    higher = extra * np.maximum(extra - 1.0, 0.0) / 2.0
    return np.asarray([
        float(len(k)),
        float(extra.sum()),
        float(higher.sum()),
        float(np.sum(k >= 3.0)),
    ])


def sim_metrics(w, d):
    """Endpoints for B simulated wet matrices; w shape B x species x stops."""
    d_route = d.any(axis=1)
    route_new = (~d_route[None, :]) & w.any(axis=2)
    k = w.sum(axis=2).astype(float)
    extra = np.maximum(k - 1.0, 0.0) * route_new
    higher = extra * np.maximum(extra - 1.0, 0.0) / 2.0
    n_new = route_new.sum(axis=1).astype(float)
    n_extra = extra.sum(axis=1).astype(float)
    n_higher = higher.sum(axis=1).astype(float)
    n_threeplus = ((k >= 3.0) & route_new).sum(axis=1).astype(float)
    return np.column_stack([n_new, n_extra, n_higher, n_threeplus])


def simulate(pair_data, probmaker, r, den, seed):
    rng = np.random.default_rng(seed)
    num = np.zeros((B, 4), dtype=float)
    for i, d in enumerate(pair_data):
        q = probmaker(d)
        w = rng.random((B,) + q.shape) < q[None, :, :]
        num += r[i] * sim_metrics(w, d["dry"])
    return num / den


def conditional(sim, obs):
    x1 = sim[:, 0]
    x2 = sim[:, 1]
    y = sim[:, 2]
    X = np.column_stack([np.ones(len(y)), x1, x2])
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    pred = X @ coef
    resid = y - pred

    obs_pred = float(coef[0] + coef[1] * obs[0] + coef[2] * obs[1])
    obs_resid = float(obs[2] - obs_pred)
    lo, hi = np.quantile(resid, [0.025, 0.975])
    p = float((1 + np.sum(resid >= obs_resid)) / (len(resid) + 1))

    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")

    uncond_p = float((1 + np.sum(y >= obs[2])) / (len(y) + 1))
    uncond_pct = float(np.mean(y <= obs[2]))

    return {
        "null_regression_intercept": float(coef[0]),
        "null_regression_new_species_slope": float(coef[1]),
        "null_regression_extra_stop_slope": float(coef[2]),
        "null_regression_r2": r2,
        "null_residual_ci95": [float(lo), float(hi)],
        "observed_new_species_beta": float(obs[0]),
        "observed_extra_stop_beta": float(obs[1]),
        "observed_higher_order_beta": float(obs[2]),
        "observed_threeplus_species_beta": float(obs[3]),
        "predicted_higher_order_beta_at_observed_first_order": obs_pred,
        "observed_conditional_residual": obs_resid,
        "conditional_upper_tail_p": p,
        "above_upper_95": bool(obs_resid > hi),
        "unconditioned_upper_tail_p": uncond_p,
        "unconditioned_percentile": uncond_pct,
    }


def main():
    pairs, pair_data, pools, dry_ids, sampled, ss, r, den, obs0, bm, rb, db, os = uniform.prepare()

    obs_rows = np.asarray([metrics(d["wet"], d["dry"]) for d in pair_data], dtype=float)
    obs = (r[:, None] * obs_rows).sum(axis=0) / den

    stops = {d["key"]: d["stops"] for d in pair_data}

    probs = uniform.baseline_probs(KAPPA, pools, dry_ids, stops, ss)

    def qu(d):
        return uniform.solve_shift(probs[d["key"]], d["wet_k"])

    hist = persistence.historical_cell_probs(pools, dry_ids, stops, ss)

    def qp(d):
        p = (1 - ANCHOR) * hist[d["key"]] + ANCHOR * d["dry"].astype(float)
        p = np.clip(p, 1e-8, 1 - 1e-8)
        return uniform.solve_shift(p, d["wet_k"])

    ub = simulate(pair_data, qu, r, den, uniform.SEED + 71000)
    pb = simulate(pair_data, qp, r, den, uniform.SEED + 72000)

    u = conditional(ub, obs)
    p = conditional(pb, obs)
    support = bool(u["above_upper_95"] and p["above_upper_95"])

    out = {
        "analysis": "naamp_higher_order_spatial_coherence_v0_1",
        "contract": "exploration/NAAMP_HIGHER_ORDER_SPATIAL_COHERENCE_CONTRACT_V0_1.json",
        "n_pairs": int(len(pairs)),
        "observed": {
            "route_new_species_gain_beta": float(obs[0]),
            "extra_stop_incidence_gain_beta": float(obs[1]),
            "higher_order_within_species_mass_beta": float(obs[2]),
            "threeplus_species_count_beta": float(obs[3]),
        },
        "uniform_kappa2": u,
        "persistence_anchor_0_75": p,
        "classification": {
            "higher_order_spatial_coherence_supported": support
        },
        "interpretation_boundary": {
            "literal_simultaneity_inferred": False,
            "individual_movement_inferred": False,
            "hydrological_connectivity_inferred": False,
            "causal_rainfall_claim": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
