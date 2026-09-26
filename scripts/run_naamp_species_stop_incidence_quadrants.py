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

def build_quadrants():
    raw = base.load()
    runs, route_sets = base.build_runs(raw)
    eligible = set(runs["RunID"].astype(str))
    sampled, stop_species = spatial.stop_matrix(raw, eligible)
    pairs = base.pair_runs(runs, route_sets).copy()

    rows = []
    for p in pairs.itertuples(index=False):
        w, d = str(p.wet_RunID), str(p.dry_RunID)
        w_stops, d_stops = set(sampled[w]), set(sampled[d])
        if len(w_stops) != 10 or w_stops != d_stops:
            raise RuntimeError(f"stop alignment failed wet={w} dry={d}")
        stops = sorted(w_stops)
        W_by = {st: set(stop_species.get((w, st), set())) for st in stops}
        D_by = {st: set(stop_species.get((d, st), set())) for st in stops}
        W = set().union(*(W_by[st] for st in stops))
        D = set().union(*(D_by[st] for st in stops))

        gain = {
            "corner_expansion": 0,
            "spatial_spread": 0,
            "taxonomic_deepening": 0,
            "within_core_rearrangement": 0,
        }
        loss = {k: 0 for k in gain}

        for st in stops:
            dry_active = len(D_by[st]) > 0
            wet_active = len(W_by[st]) > 0

            for sp in W_by[st] - D_by[st]:
                route_new = sp not in D
                if route_new and not dry_active:
                    gain["corner_expansion"] += 1
                elif (not route_new) and not dry_active:
                    gain["spatial_spread"] += 1
                elif route_new and dry_active:
                    gain["taxonomic_deepening"] += 1
                else:
                    gain["within_core_rearrangement"] += 1

            for sp in D_by[st] - W_by[st]:
                route_lost = sp not in W
                if route_lost and not wet_active:
                    loss["corner_expansion"] += 1
                elif (not route_lost) and not wet_active:
                    loss["spatial_spread"] += 1
                elif route_lost and wet_active:
                    loss["taxonomic_deepening"] += 1
                else:
                    loss["within_core_rearrangement"] += 1

        net = {k: gain[k] - loss[k] for k in gain}
        inc_w = sum(len(W_by[st]) for st in stops)
        inc_d = sum(len(D_by[st]) for st in stops)
        delta = inc_w - inc_d
        if sum(net.values()) != delta:
            raise RuntimeError(
                f"incidence identity failed wet={w} dry={d}: "
                f"{sum(net.values())} != {delta}"
            )

        row = p._asdict()
        row.update({
            "delta_species_stop_incidences": float(delta),
            **{k: float(v) for k, v in net.items()},
            **{f"gain_{k}": int(v) for k, v in gain.items()},
            **{f"loss_{k}": int(v) for k, v in loss.items()},
            "spatial_axis_net": float(net["corner_expansion"] + net["spatial_spread"]),
            "taxonomic_axis_net": float(net["corner_expansion"] + net["taxonomic_deepening"]),
        })
        rows.append(row)

    return pd.DataFrame(rows)

def fit(df, response):
    x = df[np.isfinite(pd.to_numeric(df[response], errors="coerce"))].copy()
    formula = (
        f"{response} ~ rain_contrast + temp_difference + doy_difference + "
        "year_gap + C(State) + C(RunNumber)"
    )
    m = smf.ols(formula, data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["route_cluster"]}
    )
    b = float(m.params["rain_contrast"])
    se = float(m.bse["rain_contrast"])
    return {
        "response": response,
        "n_pairs": int(len(x)),
        "n_routes": int(x["route_cluster"].nunique()),
        "formula": formula,
        "beta_rain_contrast": b,
        "se_cluster": se,
        "ci95": [b - Q * se, b + Q * se],
        "p_value": float(m.pvalues["rain_contrast"]),
    }

def models(df):
    names = [
        "delta_species_stop_incidences",
        "corner_expansion",
        "spatial_spread",
        "taxonomic_deepening",
        "within_core_rearrangement",
        "spatial_axis_net",
        "taxonomic_axis_net",
    ]
    return {n: fit(df, n) for n in names}

def summarize_counts(df):
    qs = ["corner_expansion", "spatial_spread", "taxonomic_deepening", "within_core_rearrangement"]
    return {
        "n_pairs": int(len(df)),
        "n_routes": int(df["route_cluster"].nunique()),
        "total_wet_incidence_gains": {q: int(df[f"gain_{q}"].sum()) for q in qs},
        "total_dry_incidence_losses": {q: int(df[f"loss_{q}"].sum()) for q in qs},
        "mean_net_components": {q: float(df[q].mean()) for q in qs},
        "mean_total_delta_incidence": float(df["delta_species_stop_incidences"].mean()),
    }

def identity(m):
    total = m["delta_species_stop_incidences"]["beta_rain_contrast"]
    comps = {
        q: m[q]["beta_rain_contrast"]
        for q in ["corner_expansion", "spatial_spread", "taxonomic_deepening", "within_core_rearrangement"]
    }
    s = sum(comps.values())
    shares = {q: (v / total if total != 0 else None) for q, v in comps.items()}
    return {
        "total_beta": total,
        "component_betas": comps,
        "sum_component_betas": s,
        "identity_error": total - s,
        "component_fraction_of_total_beta": shares,
    }

def main():
    df = build_quadrants()
    primary = models(df)
    exact = df[df["year_gap"] == 1].copy()
    exact_models = models(exact)

    result = {
        "analysis": "naamp_species_stop_incidence_quadrants_v0_1",
        "contract": "NAAMP_SPECIES_STOP_QUADRANTS_CONTRACT_V0_1.json",
        "status": "post-opening matrix decomposition frozen before endpoint readback",
        "descriptive": summarize_counts(df),
        "primary_models": primary,
        "identity": identity(primary),
        "exact_consecutive_year": {
            "descriptive": summarize_counts(exact),
            "models": exact_models,
            "identity": identity(exact_models),
        },
        "interpretation_boundary": {
            "incidence": "Binary acoustic species detection at a stop, not abundance.",
            "new_existing": "Relative to the paired run, not colonization or extinction.",
            "active_inactive": "Relative to the paired run, not habitat creation.",
            "causal_rainfall_claim_authorized": False,
            "endpoint_retuning_after_readback_authorized": False,
        },
    }
    Path("NAAMP_SPECIES_STOP_QUADRANTS_RECEIPT_V0_1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
