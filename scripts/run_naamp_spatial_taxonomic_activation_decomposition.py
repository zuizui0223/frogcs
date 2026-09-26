#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent
BASE_SCRIPT = ROOT / "run_naamp_ecological_pulse.py"
spec = importlib.util.spec_from_file_location("pulse_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)

Q = 1.959963984540054


def stop_matrix(raw, eligible_run_ids):
    sampled = defaultdict(set)
    for s in raw["Stops.csv"]:
        rid = (s.get("RunID") or "").strip()
        if rid not in eligible_run_ids or (s.get("SkippedStop") or "").strip() != "0":
            continue
        st = (s.get("StopNumber") or "").strip()
        if st:
            sampled[rid].add(st)

    stop_species = defaultdict(set)
    for c in raw["Counts.csv"]:
        rid = (c.get("RunID") or "").strip()
        st = (c.get("StopNumber") or "").strip()
        if rid not in eligible_run_ids or st not in sampled.get(rid, set()):
            continue
        if (c.get("CallingIndex") or "").strip() not in base.POS:
            continue
        sp = (c.get("Species") or "").strip()
        if sp:
            stop_species[(rid, st)].add(sp)

    bad = {rid: len(sts) for rid, sts in sampled.items() if len(sts) != 10}
    if bad:
        raise RuntimeError(f"eligible complete runs lost 10-stop identity: {list(bad.items())[:10]}")
    return sampled, stop_species


def route_set(run_id, stops, stop_species):
    out = set()
    for st in stops:
        out.update(stop_species.get((run_id, st), set()))
    return out


def pair_metrics(pair, sampled, stop_species, route_sets):
    w = str(pair.wet_RunID)
    d = str(pair.dry_RunID)
    w_stops = set(sampled[w])
    d_stops = set(sampled[d])
    if len(w_stops) != 10 or len(d_stops) != 10 or w_stops != d_stops:
        raise RuntimeError(
            f"stop alignment failed for pair wet={w} dry={d}: "
            f"wet={sorted(w_stops)} dry={sorted(d_stops)}"
        )
    stops = sorted(w_stops)

    W_by = {st: set(stop_species.get((w, st), set())) for st in stops}
    D_by = {st: set(stop_species.get((d, st), set())) for st in stops}
    W = route_set(w, stops, stop_species)
    D = route_set(d, stops, stop_species)
    if W != set(route_sets[w]) or D != set(route_sets[d]):
        raise RuntimeError(f"route species-set mismatch wet={w} dry={d}")

    active_w = {st: len(W_by[st]) > 0 for st in stops}
    active_d = {st: len(D_by[st]) > 0 for st in stops}
    n_active_w = sum(active_w.values())
    n_active_d = sum(active_d.values())

    inc_w = sum(len(W_by[st]) for st in stops)
    inc_d = sum(len(D_by[st]) for st in stops)

    alpha_active_w = inc_w / n_active_w if n_active_w > 0 else np.nan
    alpha_active_d = inc_d / n_active_d if n_active_d > 0 else np.nan
    redundancy_w = inc_w / len(W) if len(W) > 0 else np.nan
    redundancy_d = inc_d / len(D) if len(D) > 0 else np.nan

    shared = W & D
    if shared:
        shared_delta = np.mean([
            sum(sp in W_by[st] for st in stops) - sum(sp in D_by[st] for st in stops)
            for sp in shared
        ])
    else:
        shared_delta = np.nan

    wet_only = W - D
    dry_only = D - W

    def footprint_dependent(sp, source_by, other_active):
        locs = [st for st in stops if sp in source_by[st]]
        if not locs:
            raise RuntimeError("species missing from source route")
        return all(not other_active[st] for st in locs)

    wet_dep = sum(footprint_dependent(sp, W_by, active_d) for sp in wet_only)
    dry_dep = sum(footprint_dependent(sp, D_by, active_w) for sp in dry_only)
    wet_within = len(wet_only) - wet_dep
    dry_within = len(dry_only) - dry_dep

    footprint_net = int(wet_dep - dry_dep)
    within_net = int(wet_within - dry_within)
    richness_gain = int(len(W) - len(D))
    if footprint_net + within_net != richness_gain:
        raise RuntimeError("richness decomposition identity failed")

    gain_2x2 = {
        "route_new__dry_inactive_stop": 0,
        "route_existing__dry_inactive_stop": 0,
        "route_new__dry_active_stop": 0,
        "route_existing__dry_active_stop": 0,
    }
    for st in stops:
        for sp in W_by[st] - D_by[st]:
            route_new = sp not in D
            dry_inactive = not active_d[st]
            if route_new and dry_inactive:
                key = "route_new__dry_inactive_stop"
            elif (not route_new) and dry_inactive:
                key = "route_existing__dry_inactive_stop"
            elif route_new and (not dry_inactive):
                key = "route_new__dry_active_stop"
            else:
                key = "route_existing__dry_active_stop"
            gain_2x2[key] += 1

    return {
        "delta_active_stops": float(n_active_w - n_active_d),
        "wet_active_stops": int(n_active_w),
        "dry_active_stops": int(n_active_d),
        "delta_species_stop_incidences": float(inc_w - inc_d),
        "wet_species_stop_incidences": int(inc_w),
        "dry_species_stop_incidences": int(inc_d),
        "delta_mean_species_per_active_stop": float(alpha_active_w - alpha_active_d)
            if np.isfinite(alpha_active_w) and np.isfinite(alpha_active_d) else np.nan,
        "delta_mean_stops_per_route_species": float(redundancy_w - redundancy_d)
            if np.isfinite(redundancy_w) and np.isfinite(redundancy_d) else np.nan,
        "shared_species_delta_stops_mean": float(shared_delta) if np.isfinite(shared_delta) else np.nan,
        "n_shared_species": int(len(shared)),
        "wet_only_species": int(len(wet_only)),
        "dry_only_species": int(len(dry_only)),
        "wet_footprint_dependent_species": int(wet_dep),
        "dry_footprint_dependent_species": int(dry_dep),
        "wet_within_footprint_species": int(wet_within),
        "dry_within_footprint_species": int(dry_within),
        "footprint_dependent_net_species": float(footprint_net),
        "within_footprint_net_species": float(within_net),
        "richness_gain_identity": float(richness_gain),
        **{f"gain2x2_{k}": int(v) for k, v in gain_2x2.items()},
    }


def build_pairs():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    eligible = set(runs["RunID"].astype(str))
    sampled, stop_species = stop_matrix(raw, eligible)
    pairs = base.pair_runs(runs, route_sets).copy()

    rows = []
    for p in pairs.itertuples(index=False):
        m = pair_metrics(p, sampled, stop_species, route_sets)
        row = p._asdict()
        row.update(m)
        rows.append(row)
    out = pd.DataFrame(rows)

    if not np.allclose(
        out["richness_gain"].astype(float),
        out["footprint_dependent_net_species"] + out["within_footprint_net_species"],
        equal_nan=False,
    ):
        raise RuntimeError("dataframe richness identity failed")
    return out


def fit_ols(df, response):
    x = df[np.isfinite(pd.to_numeric(df[response], errors="coerce"))].copy()
    formula = (
        f"{response} ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber)"
    )
    fit = smf.ols(formula, data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["route_cluster"]}
    )
    b = float(fit.params["rain_contrast"])
    se = float(fit.bse["rain_contrast"])
    return {
        "response": response,
        "formula": formula,
        "n_pairs": int(len(x)),
        "n_routes": int(x["route_cluster"].nunique()),
        "beta_rain_contrast": b,
        "se_cluster": se,
        "ci95": [b - Q * se, b + Q * se],
        "p_value": float(fit.pvalues["rain_contrast"]),
    }


def model_package(df):
    endpoints = [
        "delta_active_stops",
        "shared_species_delta_stops_mean",
        "footprint_dependent_net_species",
        "within_footprint_net_species",
        "richness_gain",
        "delta_species_stop_incidences",
        "delta_mean_species_per_active_stop",
        "delta_mean_stops_per_route_species",
    ]
    return {x: fit_ols(df, x) for x in endpoints}


def descriptive(df):
    gain_cols = [c for c in df.columns if c.startswith("gain2x2_")]
    gain_totals = {c.replace("gain2x2_", ""): int(df[c].sum()) for c in gain_cols}
    route_new_total = (
        gain_totals["route_new__dry_inactive_stop"]
        + gain_totals["route_new__dry_active_stop"]
    )
    inactive_total = (
        gain_totals["route_new__dry_inactive_stop"]
        + gain_totals["route_existing__dry_inactive_stop"]
    )
    return {
        "n_pairs": int(len(df)),
        "n_routes": int(df["route_cluster"].nunique()),
        "mean_wet_active_stops": float(df["wet_active_stops"].mean()),
        "mean_dry_active_stops": float(df["dry_active_stops"].mean()),
        "mean_delta_active_stops": float(df["delta_active_stops"].mean()),
        "mean_delta_shared_species_stops": float(df["shared_species_delta_stops_mean"].mean()),
        "mean_footprint_dependent_net_species": float(df["footprint_dependent_net_species"].mean()),
        "mean_within_footprint_net_species": float(df["within_footprint_net_species"].mean()),
        "wet_only_species_total": int(df["wet_only_species"].sum()),
        "dry_only_species_total": int(df["dry_only_species"].sum()),
        "wet_footprint_dependent_species_total": int(df["wet_footprint_dependent_species"].sum()),
        "dry_footprint_dependent_species_total": int(df["dry_footprint_dependent_species"].sum()),
        "wet_footprint_dependent_fraction_of_wet_only": float(
            df["wet_footprint_dependent_species"].sum() / df["wet_only_species"].sum()
        ) if df["wet_only_species"].sum() else None,
        "dry_footprint_dependent_fraction_of_dry_only": float(
            df["dry_footprint_dependent_species"].sum() / df["dry_only_species"].sum()
        ) if df["dry_only_species"].sum() else None,
        "wet_incidence_gain_2x2": gain_totals,
        "fraction_wet_incidence_gains_route_new": float(route_new_total / sum(gain_totals.values()))
            if sum(gain_totals.values()) else None,
        "fraction_wet_incidence_gains_at_dry_inactive_stops": float(inactive_total / sum(gain_totals.values()))
            if sum(gain_totals.values()) else None,
    }


def main():
    pairs = build_pairs()
    primary = model_package(pairs)
    exact = pairs[pairs["year_gap"] == 1].copy()
    sensitivity = model_package(exact)

    b_rich = primary["richness_gain"]["beta_rain_contrast"]
    b_parts = (
        primary["footprint_dependent_net_species"]["beta_rain_contrast"]
        + primary["within_footprint_net_species"]["beta_rain_contrast"]
    )

    result = {
        "analysis": "naamp_spatial_taxonomic_activation_decomposition_v0_1",
        "contract": "NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_CONTRACT_V0_1.json",
        "status": "post-opening mechanistic decomposition frozen before endpoint readback",
        "descriptive": descriptive(pairs),
        "primary_models": primary,
        "exact_consecutive_year": {
            "descriptive": descriptive(exact),
            "models": sensitivity,
        },
        "identity_checks": {
            "pairwise_richness_identity_all_pass": True,
            "primary_richness_beta": b_rich,
            "primary_sum_component_betas": b_parts,
            "primary_beta_identity_error": float(b_rich - b_parts),
        },
        "interpretation_boundary": {
            "active": "Calling detection, not occupancy, abundance, or reproductive success.",
            "footprint_dependent": (
                "Observed structural dependence: the species is detected only at stops that were "
                "inactive in the comparison run. This is not a causal mediation estimate."
            ),
            "causal_rainfall_claim_authorized": False,
            "endpoint_retuning_after_readback_authorized": False,
        },
    }

    Path("NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_RECEIPT_V0_1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
