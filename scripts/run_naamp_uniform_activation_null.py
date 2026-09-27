#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
B = 1000
SEED = 2840223
KAPPAS = (1.0, 2.0, 5.0)

OBSERVED_REFERENCE = {
    "corner_expansion": 0.5039964764047035,
    "spatial_spread": 0.2080305999098008,
    "taxonomic_deepening": 0.5443545384491266,
    "within_core_rearrangement": 0.10902229863833068,
    "sorensen": -0.0004916260102541838,
}

def loadmod(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

base = loadmod("pulse", ROOT / "run_naamp_ecological_pulse.py")
spatial = loadmod("spatial", ROOT / "run_naamp_spatial_taxonomic_activation_decomposition.py")

def expit(x):
    x = np.asarray(x, float)
    out = np.empty_like(x)
    pos = x >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-x[pos]))
    e = np.exp(x[~pos])
    out[~pos] = e / (1.0 + e)
    return out

def logit(p):
    p = np.clip(np.asarray(p, float), 1e-12, 1 - 1e-12)
    return np.log(p) - np.log1p(-p)

def design_residual(df):
    x = df["rain_contrast"].to_numpy(float)
    pieces = [
        np.ones((len(df), 1), float),
        df[["temp_difference", "doy_difference", "year_gap"]].to_numpy(float),
        pd.get_dummies(df["State"].astype(str), drop_first=True, dtype=float).to_numpy(),
        pd.get_dummies(df["RunNumber"].astype(str), drop_first=True, dtype=float).to_numpy(),
    ]
    z = np.column_stack(pieces)
    coef = np.linalg.lstsq(z, x, rcond=None)[0]
    r = x - z @ coef
    denom = float(r @ r)
    if not np.isfinite(denom) or denom <= 0:
        raise RuntimeError("invalid residualized rain denominator")
    return r, denom

def sorensen(mat):
    # mat: species x stop boolean
    richness = mat.sum(axis=0)
    active = np.flatnonzero(richness > 0)
    if len(active) < 2:
        return np.nan
    vals = []
    for ii in range(len(active)):
        i = int(active[ii])
        for jj in range(ii + 1, len(active)):
            j = int(active[jj])
            a = int(np.logical_and(mat[:, i], mat[:, j]).sum())
            den = int(richness[i] + richness[j])
            vals.append((den - 2 * a) / den if den else 0.0)
    return float(np.mean(vals))

def component_counts(w, d):
    # w,d: species x stop boolean
    d_route = d.any(axis=1)
    w_route = w.any(axis=1)
    d_stop = d.any(axis=0)
    w_stop = w.any(axis=0)
    g = w & ~d
    l = d & ~w

    gain_corner = np.sum(g & ~d_route[:, None] & ~d_stop[None, :])
    gain_spatial = np.sum(g & d_route[:, None] & ~d_stop[None, :])
    gain_tax = np.sum(g & ~d_route[:, None] & d_stop[None, :])
    gain_core = np.sum(g & d_route[:, None] & d_stop[None, :])

    loss_corner = np.sum(l & ~w_route[:, None] & ~w_stop[None, :])
    loss_spatial = np.sum(l & w_route[:, None] & ~w_stop[None, :])
    loss_tax = np.sum(l & ~w_route[:, None] & w_stop[None, :])
    loss_core = np.sum(l & w_route[:, None] & w_stop[None, :])

    return np.asarray([
        gain_corner - loss_corner,
        gain_spatial - loss_spatial,
        gain_tax - loss_tax,
        gain_core - loss_core,
    ], float)

def simulated_components(w, d):
    # w: B x species x stop; d: species x stop
    d_route = d.any(axis=1)
    d_stop = d.any(axis=0)
    w_route = w.any(axis=2)
    w_stop = w.any(axis=1)
    g = w & ~d[None, :, :]
    l = d[None, :, :] & ~w

    gain_corner = np.sum(g & ~d_route[None, :, None] & ~d_stop[None, None, :], axis=(1,2))
    gain_spatial = np.sum(g & d_route[None, :, None] & ~d_stop[None, None, :], axis=(1,2))
    gain_tax = np.sum(g & ~d_route[None, :, None] & d_stop[None, None, :], axis=(1,2))
    gain_core = np.sum(g & d_route[None, :, None] & d_stop[None, None, :], axis=(1,2))

    loss_corner = np.sum(l & ~w_route[:, :, None] & ~w_stop[:, None, :], axis=(1,2))
    loss_spatial = np.sum(l & w_route[:, :, None] & ~w_stop[:, None, :], axis=(1,2))
    loss_tax = np.sum(l & ~w_route[:, :, None] & w_stop[:, None, :], axis=(1,2))
    loss_core = np.sum(l & w_route[:, :, None] & w_stop[:, None, :], axis=(1,2))

    return np.column_stack([
        gain_corner - loss_corner,
        gain_spatial - loss_spatial,
        gain_tax - loss_tax,
        gain_core - loss_core,
    ]).astype(float)

def simulated_sorensen(w):
    # w: B x species x stop; all rows required to have >=2 active stops
    rich = w.sum(axis=1)
    active = rich > 0
    total = np.zeros(w.shape[0], float)
    count = np.zeros(w.shape[0], int)
    for i in range(w.shape[2]):
        for j in range(i + 1, w.shape[2]):
            valid = active[:, i] & active[:, j]
            if not np.any(valid):
                continue
            a = np.logical_and(w[:, :, i], w[:, :, j]).sum(axis=1)
            den = rich[:, i] + rich[:, j]
            s = np.zeros(w.shape[0], float)
            s[valid] = (den[valid] - 2.0 * a[valid]) / den[valid]
            total += s
            count += valid.astype(int)
    if np.any(count == 0):
        raise RuntimeError("Sørensen simulation retained a row with <2 active stops")
    return total / count

def solve_shift(p, target):
    n = p.size
    if target <= 0:
        return np.zeros_like(p)
    if target >= n:
        return np.ones_like(p)
    eta = logit(p)
    lo, hi = -40.0, 40.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        val = float(expit(eta + mid).sum())
        if val < target:
            lo = mid
        else:
            hi = mid
    return expit(eta + (lo + hi) / 2.0)

def prepare():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    eligible = set(runs["RunID"].astype(str))
    sampled, ss = spatial.stop_matrix(raw, eligible)
    pairs = base.pair_runs(runs, route_sets).copy().reset_index(drop=True)

    run_rows = {}
    strata_runs = defaultdict(list)
    for r in runs.itertuples(index=False):
        rid = str(r.RunID)
        key = (str(r.State), str(r.RouteNumber), str(r.RunNumber))
        run_rows[rid] = key
        strata_runs[key].append(rid)

    pools = {}
    stops_by_stratum = {}
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
                raise RuntimeError(f"stop labels drift within stratum {key}")
            for st in rs:
                pool.update(ss.get((rid, st), set()))
        if not pool or stops is None:
            raise RuntimeError(f"empty candidate pool {key}")
        pools[key] = sorted(pool)
        stops_by_stratum[key] = stops

    dry_ids = defaultdict(set)
    for p in pairs.itertuples(index=False):
        key = (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        dry_ids[key].add(str(p.dry_RunID))

    pair_data = []
    obs_components = np.zeros((len(pairs), 4), float)
    obs_dsor = np.full(len(pairs), np.nan)
    for i, p in enumerate(pairs.itertuples(index=False)):
        key = (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        species = pools[key]
        stops = stops_by_stratum[key]
        index = {sp:j for j,sp in enumerate(species)}
        d = np.zeros((len(species), 10), bool)
        w = np.zeros((len(species), 10), bool)
        for t, st in enumerate(stops):
            for sp in ss.get((str(p.dry_RunID), st), set()):
                d[index[sp], t] = True
            for sp in ss.get((str(p.wet_RunID), st), set()):
                w[index[sp], t] = True
        obs_components[i] = component_counts(w, d)
        sd, sw = sorensen(d), sorensen(w)
        if np.isfinite(sd) and np.isfinite(sw):
            obs_dsor[i] = sw - sd
        pair_data.append({
            "key": key, "species": species, "stops": stops,
            "dry": d, "wet": w, "wet_k": int(w.sum()),
            "dry_sorensen": sd,
        })

    r_all, den_all = design_residual(pairs)
    obs_betas = (r_all[:, None] * obs_components).sum(axis=0) / den_all

    refs = np.asarray([
        OBSERVED_REFERENCE["corner_expansion"],
        OBSERVED_REFERENCE["spatial_spread"],
        OBSERVED_REFERENCE["taxonomic_deepening"],
        OBSERVED_REFERENCE["within_core_rearrangement"],
    ])
    if not np.allclose(obs_betas, refs, atol=2e-10, rtol=0):
        raise RuntimeError(f"observed quadrant beta reproduction failed: {obs_betas} vs {refs}")

    beta_mask = np.isfinite(obs_dsor)
    beta_df = pairs.loc[beta_mask].reset_index(drop=True)
    r_beta, den_beta = design_residual(beta_df)
    obs_sor_beta = float((r_beta * obs_dsor[beta_mask]).sum() / den_beta)
    if abs(obs_sor_beta - OBSERVED_REFERENCE["sorensen"]) > 2e-10:
        raise RuntimeError(f"observed Sørensen beta reproduction failed: {obs_sor_beta}")

    return pairs, pair_data, pools, dry_ids, sampled, ss, r_all, den_all, obs_betas, beta_mask, r_beta, den_beta, obs_sor_beta

def baseline_probs(kappa, pools, dry_ids, stops_by_key, ss):
    out = {}
    for key, species in pools.items():
        runs = sorted(dry_ids[key])
        n = len(runs)
        if n < 1:
            raise RuntimeError(f"no dry history {key}")
        stops = stops_by_key[key]
        idx = {sp:i for i,sp in enumerate(species)}
        y = np.zeros((len(species), 10), float)
        for rid in runs:
            for t, st in enumerate(stops):
                for sp in ss.get((rid, st), set()):
                    y[idx[sp], t] += 1.0
        total_slots = n * 10 * len(species)
        mu0 = (float(y.sum()) + 0.5) / (total_slots + 1.0)
        ys = y.sum(axis=1)
        mus = (ys + kappa * mu0) / (n * 10.0 + kappa)
        p = (y + kappa * mus[:, None]) / (n + kappa)
        out[key] = np.clip(p, 1e-8, 1 - 1e-8)
    return out

def null_for_kappa(kappa, pairs, pair_data, pools, dry_ids, ss, r_all, den_all, obs_betas, beta_mask, r_beta, den_beta, obs_sor_beta):
    stops_by_key = {d["key"]: d["stops"] for d in pair_data}
    probs = baseline_probs(kappa, pools, dry_ids, stops_by_key, ss)
    rng = np.random.default_rng(SEED + int(kappa * 1000))

    numer = np.zeros((B, 4), float)
    sor_num = np.zeros(B, float)
    beta_position = {int(orig):j for j,orig in enumerate(np.flatnonzero(beta_mask))}

    for i, dct in enumerate(pair_data):
        p = probs[dct["key"]]
        q = solve_shift(p, dct["wet_k"])
        wsim = rng.random((B,) + q.shape) < q[None, :, :]
        comps = simulated_components(wsim, dct["dry"])
        numer += r_all[i] * comps

        if i in beta_position:
            # Keep the beta-diversity estimand on the same fixed eligible pair set.
            active_n = wsim.any(axis=1).sum(axis=1)
            bad = active_n < 2
            rounds = 0
            while np.any(bad):
                rounds += 1
                if rounds > 200:
                    raise RuntimeError(f"unable to obtain beta-eligible wet draws for pair {i}")
                replacement = rng.random((int(bad.sum()),) + q.shape) < q[None, :, :]
                wsim[bad] = replacement
                active_n[bad] = replacement.any(axis=1).sum(axis=1)
                bad = active_n < 2
            sw = simulated_sorensen(wsim)
            ds = dct["dry_sorensen"]
            j = beta_position[i]
            sor_num += r_beta[j] * (sw - ds)

    betas = numer / den_all
    sor_betas = sor_num / den_beta

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
    boundary = 1.0 - shares[:, 3]
    obs_boundary = float(1.0 - obs_shares[3])

    def stat(v, obs):
        qlo, qhi = np.quantile(v, [0.025, 0.975])
        return {
            "null_mean": float(np.mean(v)),
            "null_ci95": [float(qlo), float(qhi)],
            "observed": float(obs),
            "observed_percentile": float((1 + np.sum(v <= obs)) / (len(v) + 1)),
        }

    names = ["corner_expansion", "spatial_spread", "taxonomic_deepening", "within_core_rearrangement"]
    share_report = {names[j]: stat(shares[:,j], obs_shares[j]) for j in range(4)}

    return {
        "kappa": float(kappa),
        "replicates": B,
        "observed_component_betas": {names[j]: float(obs_betas[j]) for j in range(4)},
        "null_component_beta_mean": {names[j]: float(mean[j]) for j in range(4)},
        "primary_omnibus": {
            "observed_mahalanobis": dobs,
            "monte_carlo_p": p_omnibus,
            "reject_uniform_activation": bool(p_omnibus < 0.05),
        },
        "component_shares": share_report,
        "boundary_crossing_share": stat(boundary, obs_boundary),
        "sorensen_beta_secondary": stat(sor_betas, obs_sor_beta),
        "valid_share_replicates": int(valid.sum()),
    }

def main():
    pairs, pair_data, pools, dry_ids, sampled, ss, r_all, den_all, obs_betas, beta_mask, r_beta, den_beta, obs_sor_beta = prepare()

    results = {}
    for kappa in KAPPAS:
        results[str(int(kappa))] = null_for_kappa(
            kappa, pairs, pair_data, pools, dry_ids, ss,
            r_all, den_all, obs_betas, beta_mask, r_beta, den_beta, obs_sor_beta
        )

    p2 = results["2"]["primary_omnibus"]["monte_carlo_p"]
    reject_all = all(results[str(int(k))]["primary_omnibus"]["monte_carlo_p"] < 0.05 for k in KAPPAS)
    if p2 >= 0.05:
        decision = "consistent_with_uniform_activation"
    elif reject_all:
        decision = "strong_rejection_of_uniform_activation"
    else:
        decision = "inconclusive_smoothing_sensitivity"

    output = {
        "analysis": "naamp_uniform_activation_null_v0_1",
        "contract": "NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json",
        "repair": "NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json",
        "n_pairs": int(len(pairs)),
        "n_beta_pairs": int(beta_mask.sum()),
        "simulation_replicates": B,
        "seed": SEED,
        "primary_kappa": 2.0,
        "results_by_kappa": results,
        "decision": decision,
        "interpretation_boundary": {
            "causal_claim_authorized": False,
            "uniform_null_is_acoustic_not_demographic": True,
            "failure_to_reject_means_structural_allocation_must_not_be_sold_as_beyond_uniform_activation": True,
            "rejection_does_not_identify_unique_mechanism": True,
            "retuning_after_readback_authorized": False,
        },
    }
    Path("NAAMP_UNIFORM_ACTIVATION_NULL_RECEIPT_V0_1.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
