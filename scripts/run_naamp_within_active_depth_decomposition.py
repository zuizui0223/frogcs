#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base = load_module("pulse_base", ROOT / "run_naamp_ecological_pulse.py")
spatial = load_module(
    "spatial_decomp",
    ROOT / "run_naamp_spatial_taxonomic_activation_decomposition.py",
)

Q = 1.959963984540054

def run_depth_metrics(raw, runs, route_sets):
    eligible = set(runs["RunID"].astype(str))
    sampled, stop_species = spatial.stop_matrix(raw, eligible)
    pairs = base.pair_runs(runs, route_sets).copy()
    rows = []

    for p in pairs.itertuples(index=False):
        w = str(p.wet_RunID)
        d = str(p.dry_RunID)
        w_stops = set(sampled[w])
        d_stops = set(sampled[d])
        if len(w_stops) != 10 or w_stops != d_stops:
            raise RuntimeError(f"stop alignment failed wet={w} dry={d}")
        stops = sorted(w_stops)

        kw = {st: len(stop_species.get((w, st), set())) for st in stops}
        kd = {st: len(stop_species.get((d, st), set())) for st in stops}

        aw = [st for st in stops if kw[st] >= 1]
        ad = [st for st in stops if kd[st] >= 1]
        if not aw or not ad:
            mean_w = mean_d = frac2_w = frac2_d = excess2_w = excess2_d = np.nan
            frac3_w = frac3_d = excess3_w = excess3_d = np.nan
        else:
            mean_w = sum(kw[st] for st in aw) / len(aw)
            mean_d = sum(kd[st] for st in ad) / len(ad)
            frac2_w = sum(kw[st] >= 2 for st in aw) / len(aw)
            frac2_d = sum(kd[st] >= 2 for st in ad) / len(ad)
            excess2_w = sum(max(kw[st] - 2, 0) for st in aw) / len(aw)
            excess2_d = sum(max(kd[st] - 2, 0) for st in ad) / len(ad)
            frac3_w = sum(kw[st] >= 3 for st in aw) / len(aw)
            frac3_d = sum(kd[st] >= 3 for st in ad) / len(ad)
            excess3_w = sum(max(kw[st] - 3, 0) for st in aw) / len(aw)
            excess3_d = sum(max(kd[st] - 3, 0) for st in ad) / len(ad)

        shared_active = [st for st in stops if kw[st] >= 1 and kd[st] >= 1]
        shared_delta = (
            float(np.mean([kw[st] - kd[st] for st in shared_active]))
            if shared_active else np.nan
        )

        newly_active = [st for st in stops if kd[st] == 0 and kw[st] >= 1]
        lost_active = [st for st in stops if kw[st] == 0 and kd[st] >= 1]
        new_mean = (
            float(np.mean([kw[st] for st in newly_active]))
            if newly_active else np.nan
        )
        lost_mean = (
            float(np.mean([kd[st] for st in lost_active]))
            if lost_active else np.nan
        )

        trans = {
            "shared_1_to_1": 0,
            "shared_1_to_2": 0,
            "shared_1_to_3plus": 0,
            "shared_2_to_1": 0,
            "shared_2_to_2": 0,
            "shared_2_to_3plus": 0,
            "shared_3plus_to_lower": 0,
            "shared_3plus_to_same_or_higher": 0,
        }
        for st in shared_active:
            a, b = kd[st], kw[st]
            if a == 1 and b == 1:
                trans["shared_1_to_1"] += 1
            elif a == 1 and b == 2:
                trans["shared_1_to_2"] += 1
            elif a == 1 and b >= 3:
                trans["shared_1_to_3plus"] += 1
            elif a == 2 and b == 1:
                trans["shared_2_to_1"] += 1
            elif a == 2 and b == 2:
                trans["shared_2_to_2"] += 1
            elif a == 2 and b >= 3:
                trans["shared_2_to_3plus"] += 1
            elif a >= 3 and b < a:
                trans["shared_3plus_to_lower"] += 1
            elif a >= 3 and b >= a:
                trans["shared_3plus_to_same_or_higher"] += 1
            else:
                raise RuntimeError(f"unclassified shared transition dry={a}, wet={b}")

        row = p._asdict()
        row.update({
            "delta_mean_species_per_active_stop": mean_w - mean_d
                if np.isfinite(mean_w) and np.isfinite(mean_d) else np.nan,
            "delta_fraction_2plus_active": frac2_w - frac2_d
                if np.isfinite(frac2_w) and np.isfinite(frac2_d) else np.nan,
            "delta_excess_beyond_two_active": excess2_w - excess2_d
                if np.isfinite(excess2_w) and np.isfinite(excess2_d) else np.nan,
            "delta_fraction_3plus_active": frac3_w - frac3_d
                if np.isfinite(frac3_w) and np.isfinite(frac3_d) else np.nan,
            "delta_excess_beyond_three_active": excess3_w - excess3_d
                if np.isfinite(excess3_w) and np.isfinite(excess3_d) else np.nan,
            "shared_active_stop_delta_species_mean": shared_delta,
            "n_shared_active_stops": int(len(shared_active)),
            "n_newly_active_stops": int(len(newly_active)),
            "n_lost_active_stops": int(len(lost_active)),
            "newly_active_stop_mean_species": new_mean,
            "lost_active_stop_mean_species": lost_mean,
            **trans,
        })

        if np.isfinite(row["delta_mean_species_per_active_stop"]):
            err = (
                row["delta_mean_species_per_active_stop"]
                - row["delta_fraction_2plus_active"]
                - row["delta_excess_beyond_two_active"]
            )
            if abs(err) > 1e-12:
                raise RuntimeError(f"2plus identity failed: {err}")
            err2 = (
                row["delta_excess_beyond_two_active"]
                - row["delta_fraction_3plus_active"]
                - row["delta_excess_beyond_three_active"]
            )
            if abs(err2) > 1e-12:
                raise RuntimeError(f"3plus identity failed: {err2}")

        rows.append(row)
    return pd.DataFrame(rows)

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
        "delta_mean_species_per_active_stop",
        "delta_fraction_2plus_active",
        "delta_excess_beyond_two_active",
        "shared_active_stop_delta_species_mean",
        "delta_fraction_3plus_active",
        "delta_excess_beyond_three_active",
    ]
    return {e: fit_ols(df, e) for e in endpoints}

def descriptives(df):
    trans_cols = [c for c in df.columns if c.startswith("shared_")]
    transitions = {
        c: int(df[c].sum())
        for c in trans_cols
        if c not in {"shared_active_stop_delta_species_mean"}
    }
    return {
        "n_pairs": int(len(df)),
        "n_routes": int(df["route_cluster"].nunique()),
        "mean_delta_species_per_active_stop": float(
            df["delta_mean_species_per_active_stop"].mean()
        ),
        "mean_delta_fraction_2plus_active": float(
            df["delta_fraction_2plus_active"].mean()
        ),
        "mean_delta_excess_beyond_two_active": float(
            df["delta_excess_beyond_two_active"].mean()
        ),
        "mean_shared_active_stop_delta_species": float(
            df["shared_active_stop_delta_species_mean"].mean()
        ),
        "total_shared_active_stops": int(df["n_shared_active_stops"].sum()),
        "total_newly_active_stops": int(df["n_newly_active_stops"].sum()),
        "total_lost_active_stops": int(df["n_lost_active_stops"].sum()),
        "mean_species_newly_active_stops": float(
            np.average(
                df.loc[df["n_newly_active_stops"] > 0, "newly_active_stop_mean_species"],
                weights=df.loc[df["n_newly_active_stops"] > 0, "n_newly_active_stops"],
            )
        ) if (df["n_newly_active_stops"] > 0).any() else None,
        "mean_species_lost_active_stops": float(
            np.average(
                df.loc[df["n_lost_active_stops"] > 0, "lost_active_stop_mean_species"],
                weights=df.loc[df["n_lost_active_stops"] > 0, "n_lost_active_stops"],
            )
        ) if (df["n_lost_active_stops"] > 0).any() else None,
        "shared_active_transition_counts": transitions,
    }

def identity_report(models):
    b_mean = models["delta_mean_species_per_active_stop"]["beta_rain_contrast"]
    b2 = models["delta_fraction_2plus_active"]["beta_rain_contrast"]
    bx2 = models["delta_excess_beyond_two_active"]["beta_rain_contrast"]
    b3 = models["delta_fraction_3plus_active"]["beta_rain_contrast"]
    bx3 = models["delta_excess_beyond_three_active"]["beta_rain_contrast"]
    return {
        "mean_beta": b_mean,
        "two_component_sum_beta": b2 + bx2,
        "two_component_error": b_mean - (b2 + bx2),
        "deep_beta": bx2,
        "deep_three_component_sum_beta": b3 + bx3,
        "deep_component_error": bx2 - (b3 + bx3),
    }

def main():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    pairs = run_depth_metrics(raw, runs, route_sets)

    primary = model_package(pairs)
    exact = pairs[pairs["year_gap"] == 1].copy()
    exact_models = model_package(exact)

    result = {
        "analysis": "naamp_within_active_depth_decomposition_v0_1",
        "contract": "NAAMP_WITHIN_ACTIVE_DEPTH_CONTRACT_V0_1.json",
        "status": "post-opening depth decomposition frozen before endpoint readback",
        "descriptive": descriptives(pairs),
        "primary_models": primary,
        "identity_checks": identity_report(primary),
        "exact_consecutive_year": {
            "descriptive": descriptives(exact),
            "models": exact_models,
            "identity_checks": identity_report(exact_models),
        },
        "interpretation_boundary": {
            "active_stop": "Acoustic detection, not occupancy or abundance.",
            "shared_active_stop": "Same numbered route stop active in both surveys; not proof of local population change.",
            "causal_rainfall_claim_authorized": False,
            "endpoint_retuning_after_readback_authorized": False,
        },
    }
    Path("NAAMP_WITHIN_ACTIVE_DEPTH_RECEIPT_V0_1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
