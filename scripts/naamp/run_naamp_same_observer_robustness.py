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
ANCHORS = (0.50, 0.75, 0.90)
PRIMARY_KAPPA = 2.0
PRIMARY_ANCHOR = 0.75
MIN_PAIRS = 750
MIN_ROUTES = 200


def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base = loadmod("pulse_base", ROOT / "run_naamp_ecological_pulse.py")
spatial = loadmod("spatial_base", ROOT / "run_naamp_spatial_taxonomic_activation_decomposition.py")
uniform = loadmod("uniform_base", ROOT / "run_naamp_uniform_activation_null.py")
persistence = loadmod("persistence_base", ROOT / "run_naamp_persistence_preserving_null.py")


def observer_map(raw):
    out = {}
    for r in raw["Runs.csv"]:
        rid = str(r.get("RunID") or "").strip()
        obs = str(r.get("ObserverTrackingID") or "").strip()
        if rid:
            out[rid] = obs
    return out


def same_observer_pairs(raw, runs, route_sets):
    pairs = base.pair_runs(runs, route_sets).copy().reset_index(drop=True)
    obs = observer_map(raw)
    wet = pairs["wet_RunID"].astype(str).map(obs).fillna("")
    dry = pairs["dry_RunID"].astype(str).map(obs).fillna("")
    keep = (wet != "") & (dry != "") & (wet == dry)
    selected = pairs.loc[keep].copy().reset_index(drop=True)
    selected["_observer_token"] = wet.loc[keep].to_numpy()
    return pairs, selected


def headline_package(selected, sampled, stop_species, route_sets):
    rows = []
    for p in selected.itertuples(index=False):
        metrics = spatial.pair_metrics(p, sampled, stop_species, route_sets)
        row = p._asdict()
        row.update(metrics)
        rows.append(row)
    df = pd.DataFrame(rows)
    endpoints = [
        "delta_active_stops",
        "delta_mean_species_per_active_stop",
        "richness_gain",
    ]
    models = {e: spatial.fit_ols(df, e) for e in endpoints}
    return df, models


def prepare_matrix(selected, runs, sampled, ss):
    pair_keys = {
        (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        for p in selected.itertuples(index=False)
    }

    strata_runs = defaultdict(list)
    for r in runs.itertuples(index=False):
        key = (str(r.State), str(r.RouteNumber), str(r.RunNumber))
        if key in pair_keys:
            strata_runs[key].append(str(r.RunID))

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
        if stops is None:
            raise RuntimeError(f"missing aligned stops {key}")
        pools[key] = sorted(pool)
        stops_by_stratum[key] = stops

    dry_ids = defaultdict(set)
    for p in selected.itertuples(index=False):
        key = (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        dry_ids[key].add(str(p.dry_RunID))

    pair_data = []
    obs_components = np.zeros((len(selected), 4), float)
    for i, p in enumerate(selected.itertuples(index=False)):
        key = (str(p.State), str(p.RouteNumber), str(p.RunNumber))
        species = pools[key]
        stops = stops_by_stratum[key]
        index = {sp: j for j, sp in enumerate(species)}
        d = np.zeros((len(species), 10), bool)
        w = np.zeros((len(species), 10), bool)
        for t, st in enumerate(stops):
            for sp in ss.get((str(p.dry_RunID), st), set()):
                d[index[sp], t] = True
            for sp in ss.get((str(p.wet_RunID), st), set()):
                w[index[sp], t] = True
        obs_components[i] = uniform.component_counts(w, d)
        pair_data.append({
            "key": key,
            "species": species,
            "stops": stops,
            "dry": d,
            "wet": w,
            "wet_k": int(w.sum()),
            "dry_sorensen": uniform.sorensen(d),
        })

    r_all, den_all = uniform.design_residual(selected)
    obs_betas = (r_all[:, None] * obs_components).sum(axis=0) / den_all
    return pair_data, pools, dry_ids, r_all, den_all, obs_betas


def run_nulls(selected, pair_data, pools, dry_ids, ss, r_all, den_all, obs_betas):
    dummy_mask = np.zeros(len(selected), dtype=bool)
    dummy_r = np.asarray([], float)

    uniform_results = {}
    for kappa in KAPPAS:
        uniform_results[f"{kappa:.1f}"] = uniform.null_for_kappa(
            kappa,
            selected,
            pair_data,
            pools,
            dry_ids,
            ss,
            r_all,
            den_all,
            obs_betas,
            dummy_mask,
            dummy_r,
            1.0,
            np.nan,
            simulate_sorensen=False,
        )

    stops_by_key = {d["key"]: d["stops"] for d in pair_data}
    hist = persistence.historical_cell_probs(pools, dry_ids, stops_by_key, ss)
    persistence_results = {
        f"{anchor:.2f}": persistence.null_for_anchor(
            anchor, pair_data, hist, r_all, den_all, obs_betas
        )
        for anchor in ANCHORS
    }
    return uniform_results, persistence_results


def classify(models, uniform_results, persistence_results):
    headline_positive_ci = all(v["ci95"][0] > 0 for v in models.values())
    headline_positive = all(v["beta_rain_contrast"] > 0 for v in models.values())

    u = uniform_results[f"{PRIMARY_KAPPA:.1f}"]
    p = persistence_results[f"{PRIMARY_ANCHOR:.2f}"]
    u_reject = u["primary_omnibus"]["monte_carlo_p"] < 0.05
    p_reject = p["primary_omnibus"]["monte_carlo_p"] < 0.05

    u_b = u["boundary_crossing_share"]
    p_b = p["boundary_crossing_share"]
    u_above_ci = u_b["observed"] > u_b["null_ci95"][1]
    p_above_ci = p_b["observed"] > p_b["null_ci95"][1]
    u_above_mean = u_b["observed"] > u_b["null_mean"]
    p_above_mean = p_b["observed"] > p_b["null_mean"]

    if headline_positive_ci and u_reject and p_reject and u_above_ci and p_above_ci:
        label = "observer_robust"
    elif headline_positive and u_above_mean and p_above_mean:
        label = "directionally_consistent_qualified"
    else:
        label = "mixed"

    return {
        "classification": label,
        "headline_all_positive": bool(headline_positive),
        "headline_all_positive_ci95": bool(headline_positive_ci),
        "primary_uniform_reject": bool(u_reject),
        "primary_persistence_reject": bool(p_reject),
        "observed_boundary_above_uniform_mean": bool(u_above_mean),
        "observed_boundary_above_persistence_mean": bool(p_above_mean),
        "observed_boundary_above_uniform_ci95": bool(u_above_ci),
        "observed_boundary_above_persistence_ci95": bool(p_above_ci),
    }


def main():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    all_pairs, selected = same_observer_pairs(raw, runs, route_sets)

    eligible = set(runs["RunID"].astype(str))
    sampled, ss = spatial.stop_matrix(raw, eligible)

    n_routes = int(selected["route_cluster"].nunique()) if len(selected) else 0
    n_observers = int(selected["_observer_token"].nunique()) if len(selected) else 0
    gate = bool(len(selected) >= MIN_PAIRS and n_routes >= MIN_ROUTES)

    output = {
        "analysis": "naamp_same_observer_robustness_v0_1",
        "contract": "provenance/contracts/NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json",
        "coverage": {
            "all_matched_pairs": int(len(all_pairs)),
            "same_observer_pairs": int(len(selected)),
            "same_observer_fraction": float(len(selected) / len(all_pairs)) if len(all_pairs) else None,
            "same_observer_routes": n_routes,
            "same_observer_unique_observers": n_observers,
            "minimum_gate_pairs": MIN_PAIRS,
            "minimum_gate_routes": MIN_ROUTES,
            "gate_pass": gate,
        },
        "headline_models": None,
        "uniform_results_by_kappa": None,
        "persistence_results_by_anchor": None,
        "decision": {
            "classification": "underpowered" if not gate else None
        },
        "interpretation_boundary": {
            "causal_rainfall_claim_authorized": False,
            "observer_equivalence_proven": False,
            "unique_mechanism_identified": False,
            "post_readback_retuning_authorized": False,
        },
    }

    if gate:
        headline_df, models = headline_package(selected, sampled, ss, route_sets)
        pair_data, pools, dry_ids, r_all, den_all, obs_betas = prepare_matrix(
            selected, runs, sampled, ss
        )
        uniform_results, persistence_results = run_nulls(
            selected, pair_data, pools, dry_ids, ss, r_all, den_all, obs_betas
        )
        output["headline_models"] = models
        output["uniform_results_by_kappa"] = uniform_results
        output["persistence_results_by_anchor"] = persistence_results
        output["decision"] = classify(models, uniform_results, persistence_results)

    Path("NAAMP_SAME_OBSERVER_ROBUSTNESS_RECEIPT_V0_1.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
