#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
NAAMP = ROOT / "scripts" / "naamp"
OUT = ROOT / "exploration" / "NAAMP_CALLING_INDEX_PHYSICAL_STOP_SENSITIVITY_RECEIPT_V0_1.json"
Q = 1.959963984540054


def loadmod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


base = loadmod("pulse_base", NAAMP / "run_naamp_ecological_pulse.py")
spatial = loadmod("spatial_base", NAAMP / "run_naamp_spatial_taxonomic_activation_decomposition.py")


def physical_site_map(raw, eligible_run_ids):
    vals = defaultdict(set)
    for s in raw["Stops.csv"]:
        rid = (s.get("RunID") or "").strip()
        st = (s.get("StopNumber") or "").strip()
        sid = (s.get("SiteID") or "").strip()
        if rid not in eligible_run_ids or (s.get("SkippedStop") or "").strip() != "0" or not st:
            continue
        if sid:
            vals[(rid, st)].add(sid)
    conflict = {k: v for k, v in vals.items() if len(v) > 1}
    if conflict:
        raise RuntimeError(f"multiple SiteID values per run-stop: {list(conflict)[:10]}")
    return {k: next(iter(v)) for k, v in vals.items() if v}


def physically_stable_pair(pair, sampled, site):
    wet = str(pair.wet_RunID)
    dry = str(pair.dry_RunID)
    wst = set(sampled[wet]); dst = set(sampled[dry])
    if len(wst) != 10 or wst != dst:
        return False
    for st in sorted(wst):
        ws = site.get((wet, st)); ds = site.get((dry, st))
        if ws is None or ds is None or ws != ds:
            return False
    return True


def build_calling_index(raw, eligible_run_ids, sampled):
    values = defaultdict(list)
    for row in raw["Counts.csv"]:
        rid = (row.get("RunID") or "").strip()
        st = (row.get("StopNumber") or "").strip()
        sp = (row.get("Species") or "").strip()
        if rid not in eligible_run_ids or st not in sampled.get(rid, set()) or not sp:
            continue
        try:
            ci = int(float((row.get("CallingIndex") or "").strip()))
        except Exception:
            continue
        if ci not in (1, 2, 3):
            continue
        values[(rid, st, sp)].append(ci)

    out = {}
    by_run_stop = defaultdict(dict)
    duplicate_cells = 0
    conflicting_duplicate_cells = 0
    duplicate_rows_excess = 0
    for key, vals in values.items():
        if len(vals) > 1:
            duplicate_cells += 1
            duplicate_rows_excess += len(vals) - 1
            if len(set(vals)) > 1:
                conflicting_duplicate_cells += 1
        value = max(vals)
        out[key] = value
        rid, st, sp = key
        by_run_stop[(rid, st)][sp] = value

    return out, by_run_stop, {
        "positive_cells": int(len(out)),
        "duplicate_cells": int(duplicate_cells),
        "conflicting_duplicate_cells": int(conflicting_duplicate_cells),
        "duplicate_rows_excess": int(duplicate_rows_excess),
        "duplicate_resolution": "maximum CallingIndex within RunID x StopNumber x Species",
    }


def pair_components(pair, sampled, ci_by_run_stop):
    wet = str(pair.wet_RunID)
    dry = str(pair.dry_RunID)
    wet_stops = set(sampled[wet])
    dry_stops = set(sampled[dry])
    if wet_stops != dry_stops or len(wet_stops) != 10:
        raise RuntimeError(f"unaligned stops: wet={wet} dry={dry}")
    stops = sorted(wet_stops)

    activation = 0.0
    deactivation = 0.0
    shared_intensity = 0.0
    total = 0.0
    n_activation = 0
    n_deactivation = 0
    n_shared = 0
    n_shared_up = 0
    n_shared_down = 0

    for st in stops:
        wet_map = ci_by_run_stop.get((wet, st), {})
        dry_map = ci_by_run_stop.get((dry, st), {})
        species = set(wet_map) | set(dry_map)
        for sp in species:
            w = int(wet_map.get(sp, 0))
            d = int(dry_map.get(sp, 0))
            diff = w - d
            total += diff
            if d == 0 and w > 0:
                activation += w
                n_activation += 1
            elif d > 0 and w == 0:
                deactivation -= d
                n_deactivation += 1
            elif d > 0 and w > 0:
                shared_intensity += diff
                n_shared += 1
                n_shared_up += int(diff > 0)
                n_shared_down += int(diff < 0)

    if abs(total - (activation + deactivation + shared_intensity)) > 1e-12:
        raise RuntimeError("CallingIndex decomposition identity failed")

    return {
        "ci_activation": activation,
        "ci_deactivation": deactivation,
        "ci_shared_intensity": shared_intensity,
        "ci_total": total,
        "binary_activation_net": float(n_activation - n_deactivation),
        "n_activation_cells": int(n_activation),
        "n_deactivation_cells": int(n_deactivation),
        "n_shared_positive_cells": int(n_shared),
        "shared_intensification_net": float(n_shared_up - n_shared_down),
        "shared_intensity_mean_delta": (
            float(shared_intensity / n_shared) if n_shared > 0 else np.nan
        ),
    }


def fit(df, response):
    x = df[np.isfinite(pd.to_numeric(df[response], errors="coerce"))].copy()
    formula = (
        f"{response} ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber)"
    )
    model = smf.ols(formula, data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["route_cluster"]}
    )
    b = float(model.params["rain_contrast"])
    se = float(model.bse["rain_contrast"])
    return {
        "response": response,
        "n_pairs": int(len(x)),
        "n_routes": int(x["route_cluster"].nunique()),
        "beta_rain_contrast": b,
        "se_cluster": se,
        "ci95": [b - Q * se, b + Q * se],
        "p_value": float(model.pvalues["rain_contrast"]),
    }


def main():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    eligible = set(runs["RunID"].astype(str))
    sampled, _ = spatial.stop_matrix(raw, eligible)
    pairs_all = base.pair_runs(runs, route_sets).copy().reset_index(drop=True)
    site = physical_site_map(raw, eligible)
    stable_mask = np.asarray([
        physically_stable_pair(p, sampled, site)
        for p in pairs_all.itertuples(index=False)
    ], dtype=bool)
    pairs = pairs_all.loc[stable_mask].copy().reset_index(drop=True)
    if len(pairs) != 4172:
        raise RuntimeError(f"physical-stable pair count drift: {len(pairs)} != 4172")

    ci, ci_by_run_stop, duplicate_audit = build_calling_index(raw, eligible, sampled)

    rows = []
    for pair in pairs.itertuples(index=False):
        row = pair._asdict()
        row.update(pair_components(pair, sampled, ci_by_run_stop))
        rows.append(row)
    df = pd.DataFrame(rows)

    residual = (
        df["ci_total"]
        - df["ci_activation"]
        - df["ci_deactivation"]
        - df["ci_shared_intensity"]
    )
    max_identity_error = float(np.max(np.abs(residual.to_numpy(float))))
    if max_identity_error > 1e-12:
        raise RuntimeError(f"identity drift: {max_identity_error}")

    endpoints = [
        "ci_total",
        "ci_activation",
        "ci_deactivation",
        "ci_shared_intensity",
        "binary_activation_net",
        "shared_intensification_net",
        "shared_intensity_mean_delta",
    ]
    models = {name: fit(df, name) for name in endpoints}

    total_beta = models["ci_total"]["beta_rain_contrast"]
    component_betas = {
        k: models[k]["beta_rain_contrast"]
        for k in ("ci_activation", "ci_deactivation", "ci_shared_intensity")
    }
    beta_identity_error = float(
        total_beta
        - component_betas["ci_activation"]
        - component_betas["ci_deactivation"]
        - component_betas["ci_shared_intensity"]
    )
    shares = {
        k: float(v / total_beta) if abs(total_beta) > 1e-12 else None
        for k, v in component_betas.items()
    }

    activation_ci = models["ci_activation"]["ci95"]
    threshold_dominant = bool(
        total_beta > 0
        and activation_ci[0] > 0
        and shares["ci_activation"] is not None
        and shares["ci_activation"] > 0.5
        and component_betas["ci_activation"] > component_betas["ci_shared_intensity"]
    )

    exact = df[df["year_gap"] == 1].copy()
    exact_models = {name: fit(exact, name) for name in endpoints}

    output = {
        "analysis": "naamp_calling_index_physical_stop_sensitivity_v0_1",
        "contract": "exploration/NAAMP_CALLING_INDEX_PHYSICAL_STOP_SENSITIVITY_CONTRACT_V0_1.json",
        "parent_pairs": int(len(pairs_all)),
        "physically_stable_fraction": float(len(pairs) / len(pairs_all)),
        "n_pairs": int(len(df)),
        "n_routes": int(df["route_cluster"].nunique()),
        "duplicate_audit": duplicate_audit,
        "identity_checks": {
            "max_pair_identity_error": max_identity_error,
            "rain_beta_identity_error": beta_identity_error,
        },
        "primary_models": models,
        "component_beta_shares_of_total": shares,
        "classification": {
            "threshold_dominant_under_prefixed_rule": threshold_dominant,
            "rule": (
                "total beta > 0; activation 95% CI > 0; activation contribution >50% "
                "of total beta; activation beta > shared-intensity beta"
            ),
        },
        "exact_consecutive_year": {
            "n_pairs": int(len(exact)),
            "models": exact_models,
        },
        "descriptive": {
            "activation_cells_total": int(df["n_activation_cells"].sum()),
            "deactivation_cells_total": int(df["n_deactivation_cells"].sum()),
            "shared_positive_cells_total": int(df["n_shared_positive_cells"].sum()),
            "mean_pair_shared_intensity_delta": float(df["shared_intensity_mean_delta"].mean()),
        },
        "interpretation_boundary": {
            "CallingIndex": "ordinal acoustic intensity, not abundance or reproductive success",
            "causal_rainfall_claim": False,
            "physical_stop_identity": "All ten StopNumbers have identical nonmissing SiteID in wet and dry runs.",
            "submission_story_change_authorized": False,
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
