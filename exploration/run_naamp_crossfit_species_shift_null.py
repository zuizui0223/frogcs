#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
OUT = ROOT / "exploration" / "NAAMP_CROSSFIT_SPECIES_SHIFT_NULL_RECEIPT_V0_1.json"
B = 1000
SEED = 2840223
KAPPA = 2.0
MIN_POSITIVE_CELLS = 20
MIN_POSITIVE_ROUTES = 5


def loadmod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base = loadmod("pulse_base", NAAMP / "run_naamp_ecological_pulse.py")
spatial = loadmod("spatial_base", NAAMP / "run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform = loadmod("uniform_base", NAAMP / "run_naamp_uniform_activation_null.py")


def fold_for_route(route_cluster: str) -> str:
    b = hashlib.sha256(str(route_cluster).encode("utf-8")).digest()[0]
    return "A" if b < 128 else "B"


def prepare_from_raw():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    eligible = set(runs["RunID"].astype(str))
    sampled, ss = spatial.stop_matrix(raw, eligible)
    pairs = base.pair_runs(runs, route_sets).copy().reset_index(drop=True)

    pair_keys = {
        (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        for p in pairs.itertuples(index=False)
    }
    strata_runs = defaultdict(list)
    for r in runs.itertuples(index=False):
        key = (str(r.State), str(r.RouteNumber), str(r.RunNumber))
        if key in pair_keys:
            strata_runs[key].append(str(r.RunID))

    pools = {}
    stops_by_key = {}
    for key, rids in strata_runs.items():
        pool = set()
        stops = None
        for rid in rids:
            rs = sorted(sampled[rid])
            if len(rs) != 10:
                continue
            if stops is None:
                stops = rs
            elif rs != stops:
                raise RuntimeError(f"stop drift within stratum {key}")
            for st in rs:
                pool.update(ss.get((rid, st), set()))
        if stops is None:
            raise RuntimeError(f"missing stops for {key}")
        pools[key] = sorted(pool)
        stops_by_key[key] = stops

    dry_ids = defaultdict(set)
    for p in pairs.itertuples(index=False):
        key = (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        dry_ids[key].add(str(p.dry_RunID))

    pair_data = []
    obs_components = np.zeros((len(pairs), 4), float)
    for i, p in enumerate(pairs.itertuples(index=False)):
        key = (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        species = pools[key]
        stops = stops_by_key[key]
        idx = {sp: j for j, sp in enumerate(species)}
        d = np.zeros((len(species), 10), bool)
        w = np.zeros((len(species), 10), bool)
        for t, st in enumerate(stops):
            for sp in ss.get((str(p.dry_RunID), st), set()):
                d[idx[sp], t] = True
            for sp in ss.get((str(p.wet_RunID), st), set()):
                w[idx[sp], t] = True
        obs_components[i] = uniform.component_counts(w, d)
        pair_data.append({
            "key": key,
            "species": species,
            "stops": stops,
            "dry": d,
            "wet": w,
            "wet_k": int(w.sum()),
            "route_cluster": str(p.route_cluster),
            "fold": fold_for_route(str(p.route_cluster)),
            "rain_contrast": float(p.rain_contrast),
        })

    r_all, den_all = uniform.design_residual(pairs)
    obs_betas = (r_all[:, None] * obs_components).sum(axis=0) / den_all

    refs = np.asarray([
        uniform.OBSERVED_REFERENCE["corner_expansion"],
        uniform.OBSERVED_REFERENCE["spatial_spread"],
        uniform.OBSERVED_REFERENCE["taxonomic_deepening"],
        uniform.OBSERVED_REFERENCE["within_core_rearrangement"],
    ])
    if not np.allclose(obs_betas, refs, atol=2e-10, rtol=0):
        raise RuntimeError(f"observed component reproduction failed: {obs_betas} vs {refs}")

    return raw, runs, pairs, pair_data, pools, dry_ids, stops_by_key, sampled, ss, r_all, den_all, obs_betas


def run_species_counts(runs, sampled, ss):
    counts = {}
    for r in runs.itertuples(index=False):
        rid = str(r.RunID)
        c = defaultdict(int)
        for st in sampled[rid]:
            for sp in ss.get((rid, st), set()):
                c[sp] += 1
        counts[rid] = dict(c)
    return counts


def fit_species_slopes(runs, sampled, ss, all_species, training_fold):
    x = runs.copy()
    x["route_fold"] = x["route_cluster"].astype(str).map(fold_for_route)
    x = x[x["route_fold"] == training_fold].copy().reset_index(drop=True)
    x["dry_x"] = np.log1p(x["DaysSinceRain"].astype(float))
    theta = 2.0 * np.pi * x["doy"].astype(float) / 365.25
    x["sin_doy"] = np.sin(theta)
    x["cos_doy"] = np.cos(theta)
    counts = run_species_counts(x, sampled, ss)

    slopes = {}
    audit = {}
    for sp in sorted(all_species):
        y = np.asarray([counts[str(rid)].get(sp, 0) for rid in x["RunID"].astype(str)], float)
        pos_cells = int(y.sum())
        pos_routes = int(
            x.loc[y > 0, "route_cluster"].astype(str).nunique()
        )
        info = {
            "positive_stop_cells": pos_cells,
            "positive_routes": pos_routes,
            "estimable": False,
            "method": "zero_differential_shift",
            "dryness_beta": 0.0,
            "wet_shift_gamma": 0.0,
        }
        if pos_cells < MIN_POSITIVE_CELLS or pos_routes < MIN_POSITIVE_ROUTES:
            slopes[sp] = 0.0
            audit[sp] = info
            continue

        d = x[["State", "RunNumber", "mean_temp_c", "dry_x", "sin_doy", "cos_doy"]].copy()
        d["prop"] = y / 10.0
        formula = (
            "prop ~ dry_x + mean_temp_c + sin_doy + cos_doy + "
            "C(State) + C(RunNumber)"
        )
        glm = smf.glm(
            formula,
            data=d,
            family=sm.families.Binomial(),
            freq_weights=np.repeat(10.0, len(d)),
        )
        method = "glm"
        try:
            fit = glm.fit(maxiter=200, disp=0)
            beta = float(fit.params["dry_x"])
            if not np.isfinite(beta) or abs(beta) > 20:
                raise RuntimeError("unstable slope")
        except Exception:
            method = "ridge_fallback"
            fit = glm.fit_regularized(alpha=0.01, L1_wt=0.0, maxiter=1000)
            beta = float(fit.params["dry_x"])
            if not np.isfinite(beta):
                beta = 0.0
                method = "zero_after_failed_regularization"

        gamma = float(-beta)
        slopes[sp] = gamma
        info.update({
            "estimable": bool(method != "zero_after_failed_regularization"),
            "method": method,
            "dryness_beta": beta,
            "wet_shift_gamma": gamma,
        })
        audit[sp] = info

    return slopes, audit, {
        "training_fold": training_fold,
        "n_runs": int(len(x)),
        "n_routes": int(x["route_cluster"].nunique()),
        "n_species_total": int(len(all_species)),
        "n_species_estimable": int(sum(v["estimable"] for v in audit.values())),
        "n_species_zero_shift": int(sum(not v["estimable"] for v in audit.values())),
    }


def simulate(pair_data, probs, slopes_by_train_fold, r_all, den_all, obs_betas):
    rng = np.random.default_rng(SEED)
    numer = np.zeros((B, 4), float)

    for i, dct in enumerate(pair_data):
        test_fold = dct["fold"]
        train_fold = "B" if test_fold == "A" else "A"
        slopes = slopes_by_train_fold[train_fold]
        p = probs[dct["key"]]
        gamma = np.asarray([slopes.get(sp, 0.0) for sp in dct["species"]], float)
        eta = uniform.logit(p) + gamma[:, None] * dct["rain_contrast"]
        pre = uniform.expit(eta)
        q = uniform.solve_shift(pre, dct["wet_k"])
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
    boundary = 1.0 - shares[:, 3]
    obs_boundary = float(1.0 - obs_shares[3])

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

    return {
        "replicates": B,
        "seed": SEED,
        "observed_component_betas": {names[j]: float(obs_betas[j]) for j in range(4)},
        "null_component_beta_mean": {names[j]: float(mean[j]) for j in range(4)},
        "primary_omnibus": {
            "observed_mahalanobis": dobs,
            "monte_carlo_p": p_omnibus,
            "reject_crossfit_species_shift_null": bool(p_omnibus < 0.05),
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
    ) = prepare_from_raw()

    all_species = sorted({sp for species in pools.values() for sp in species})
    slopes_A, audit_A, fold_A = fit_species_slopes(
        runs, sampled, ss, all_species, "A"
    )
    slopes_B, audit_B, fold_B = fit_species_slopes(
        runs, sampled, ss, all_species, "B"
    )
    slopes_by_train_fold = {"A": slopes_A, "B": slopes_B}

    probs = uniform.baseline_probs(KAPPA, pools, dry_ids, stops_by_key, ss)
    null = simulate(pair_data, probs, slopes_by_train_fold, r_all, den_all, obs_betas)

    common = sorted(
        sp for sp in all_species
        if audit_A[sp]["estimable"] and audit_B[sp]["estimable"]
    )
    if len(common) >= 3:
        a = np.asarray([slopes_A[sp] for sp in common], float)
        b = np.asarray([slopes_B[sp] for sp in common], float)
        corr = float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else None
    else:
        corr = None

    output = {
        "analysis": "naamp_crossfit_species_shift_null_v0_1",
        "contract": "exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#crossfit_species_shift_null",
        "n_pairs": int(len(pairs)),
        "n_routes": int(pairs["route_cluster"].nunique()),
        "route_fold_counts": {
            k: int(sum(d["fold"] == k for d in pair_data)) for k in ("A", "B")
        },
        "training_fold_A": fold_A,
        "training_fold_B": fold_B,
        "estimability_gate": {
            "minimum_positive_stop_cells": MIN_POSITIVE_CELLS,
            "minimum_positive_routes": MIN_POSITIVE_ROUTES,
        },
        "species_shift_crossfold": {
            "n_estimable_both_folds": int(len(common)),
            "pearson_gamma_correlation": corr,
            "fold_A_gamma": {
                sp: float(slopes_A[sp]) for sp in common
            },
            "fold_B_gamma": {
                sp: float(slopes_B[sp]) for sp in common
            },
        },
        "null_result": null,
        "decision": (
            "species_level_heterogeneity_insufficient"
            if null["primary_omnibus"]["reject_crossfit_species_shift_null"]
            else "species_level_heterogeneity_sufficient_under_tested_null"
        ),
        "interpretation_boundary": {
            "crossfit": "Species shifts are learned only on different routes from the held-out pair.",
            "site_specific_response_identified": False,
            "causal_rainfall_claim": False,
            "submission_story_change_authorized": False,
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
