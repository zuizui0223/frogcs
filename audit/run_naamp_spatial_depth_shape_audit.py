#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
OUT = ROOT / "audit" / "NAAMP_SPATIAL_DEPTH_SHAPE_AUDIT_RECEIPT_V0_1.json"

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


def choose2(x):
    x = np.asarray(x)
    return x * (x - 1) / 2.0


def observed_metrics(w, d):
    dryroute = d.any(axis=1)
    route_new = (~dryroute) & w.any(axis=1)
    k = w.sum(axis=1).astype(int)

    marginal = np.asarray([np.sum(route_new & (k >= j)) for j in range(1, 11)], float)
    exact = np.asarray([np.sum(route_new & (k == j)) for j in range(1, 11)], float)

    kr = k[route_new].astype(float)
    total_sites = float(kr.sum())
    extra = float(np.maximum(kr - 1, 0).sum())
    third_plus = float(np.maximum(kr - 2, 0).sum())
    H = float(choose2(np.maximum(kr - 1, 0)).sum())
    P = float(choose2(kr).sum())

    if abs(extra - marginal[1:].sum()) > 1e-9:
        raise RuntimeError("extra-stop identity failed")
    if abs(third_plus - marginal[2:].sum()) > 1e-9:
        raise RuntimeError("third-plus identity failed")
    if abs(P - H - extra) > 1e-9:
        raise RuntimeError("pair-count identity failed")

    return np.concatenate([marginal, exact, [total_sites, extra, third_plus, H, P]])


def simulated_metrics(w, d):
    # w: B x species x stop; d: species x stop
    dryroute = d.any(axis=1)
    route_new = (~dryroute[None, :]) & w.any(axis=2)
    k = w.sum(axis=2).astype(int)

    marginal = np.column_stack([
        np.sum(route_new & (k >= j), axis=1) for j in range(1, 11)
    ]).astype(float)
    exact = np.column_stack([
        np.sum(route_new & (k == j), axis=1) for j in range(1, 11)
    ]).astype(float)

    kr = k.astype(float) * route_new
    total_sites = kr.sum(axis=1)
    extra = (np.maximum(k - 1, 0) * route_new).sum(axis=1).astype(float)
    third_plus = (np.maximum(k - 2, 0) * route_new).sum(axis=1).astype(float)
    H = (choose2(np.maximum(k - 1, 0)) * route_new).sum(axis=1).astype(float)
    P = (choose2(k) * route_new).sum(axis=1).astype(float)

    if not np.allclose(extra, marginal[:, 1:].sum(axis=1)):
        raise RuntimeError("sim extra-stop identity failed")
    if not np.allclose(third_plus, marginal[:, 2:].sum(axis=1)):
        raise RuntimeError("sim third-plus identity failed")
    if not np.allclose(P, H + extra):
        raise RuntimeError("sim pair-count identity failed")

    return np.column_stack([marginal, exact, total_sites, extra, third_plus, H, P])


def stat(v, obs):
    lo, hi = np.quantile(v, [0.025, 0.975])
    return {
        "null_mean": float(np.mean(v)),
        "null_ci95": [float(lo), float(hi)],
        "observed": float(obs),
        "upper_tail_p": float((1 + np.sum(v >= obs)) / (len(v) + 1)),
        "above_upper_95": bool(obs > hi),
    }


def main():
    pairs, pair_data, pools, dry_ids, sampled, ss, r, den, *_ = uniform.prepare()
    observed_rows = np.asarray([observed_metrics(x["wet"], x["dry"]) for x in pair_data])
    observed_beta = (r[:, None] * observed_rows).sum(axis=0) / den

    names = (
        [f"marginal_site_{j}_beta" for j in range(1, 11)]
        + [f"exact_k_{j}_taxa_beta" for j in range(1, 11)]
        + ["total_route_new_sites_beta", "extra_stop_beta", "third_plus_beta",
           "concentration_H_beta", "standard_pair_count_P_beta"]
    )
    if len(names) != len(observed_beta):
        raise RuntimeError("metric-name mismatch")

    stops = {x["key"]: x["stops"] for x in pair_data}
    uniform_probs = uniform.baseline_probs(KAPPA, pools, dry_ids, stops, ss)
    history_probs = persistence.historical_cell_probs(pools, dry_ids, stops, ss)

    def simulate(kind, seed):
        rng = np.random.default_rng(seed)
        numer = np.zeros((B, len(names)), float)
        for i, x in enumerate(pair_data):
            if kind == "uniform":
                p = uniform_probs[x["key"]]
            else:
                p = (1 - ANCHOR) * history_probs[x["key"]] + ANCHOR * x["dry"].astype(float)
                p = np.clip(p, 1e-8, 1 - 1e-8)
            q = uniform.solve_shift(p, x["wet_k"])
            wsim = rng.random((B,) + q.shape) < q[None, :, :]
            numer += r[i] * simulated_metrics(wsim, x["dry"])
        return numer / den

    ub = simulate("uniform", uniform.SEED + 91000)
    pb = simulate("persistence", uniform.SEED + 92000)

    observed = {names[i]: float(observed_beta[i]) for i in range(len(names))}
    uniform_report = {names[i]: stat(ub[:, i], observed_beta[i]) for i in range(len(names))}
    persistence_report = {names[i]: stat(pb[:, i], observed_beta[i]) for i in range(len(names))}

    marginal = observed_beta[:10]
    exact = observed_beta[10:20]
    total_sites, extra, third_plus, H, P = observed_beta[20:]

    # Algebraic coefficient identities must also hold because all endpoints use the same linear rain contrast.
    identity = {
        "extra_minus_sum_marginal_2_to_10": float(extra - marginal[1:].sum()),
        "third_plus_minus_sum_marginal_3_to_10": float(third_plus - marginal[2:].sum()),
        "P_minus_H_minus_extra": float(P - H - extra),
        "third_marginal_from_thirdplus_minus_fourthplus": float(marginal[2]),
    }

    # Descriptive shape classification only.
    above_u = [j for j in range(1, 11) if uniform_report[f"marginal_site_{j}_beta"]["above_upper_95"]]
    above_p = [j for j in range(1, 11) if persistence_report[f"marginal_site_{j}_beta"]["above_upper_95"]]
    above_both = sorted(set(above_u).intersection(above_p))

    out = {
        "analysis": "naamp_spatial_depth_shape_audit_v0_1",
        "contract": "audit/NAAMP_SPATIAL_DEPTH_SHAPE_AUDIT_CONTRACT_V0_1.json",
        "n_pairs": int(len(pairs)),
        "observed_betas": observed,
        "algebraic_identities": identity,
        "uniform_kappa2": uniform_report,
        "persistence_anchor_0_75": persistence_report,
        "marginal_sites_above_upper_95_both_nulls": above_both,
        "shape_interpretation": {
            "third_site_is_predeclared_biological_threshold": False,
            "exponential_shape_tested": False,
            "exponential_shape_authorized": False,
            "metric_H_is_quadratic_triangular_not_exponential": True,
            "H_equivalent_to_standard_pair_count_after_conditioning_on_extra_stop": True,
            "note": (
                "Interpret exact/marginal depth coefficients descriptively. The frozen third-plus result "
                "localizes excess into the cumulative tail beyond the second occupied site; it does not "
                "by itself establish a discontinuity at exactly k=3."
            ),
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
