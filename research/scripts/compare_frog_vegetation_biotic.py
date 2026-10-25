#!/usr/bin/env python3
"""Prospective block-held-out site-level chorus prediction tiers.

Only marginal calling is predicted here. NOT frogcs joint concentration C,
abundance, breeding success or causal inference. Real E1–E4 predictions require
observed wetland hydrology, vegetation and predator census data.
--self-test uses synthetic cases ONLY, never ecological outcome data.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE = ["rain_contrast", "air_temp_c", "season_sin", "season_cos",
        "prior_site_strong_rate"]
HYDRO = ["water_level_cm", "hydroperiod_days", "inundated_fraction",
         "water_temp_c"]
PLANT = ["emergent_cover", "emergent_stem_density", "submerged_cover",
         "open_water_fraction", "canopy_cover"]
BIOTIC = ["fish_present", "odonate_larval_density", "salamander_larval_density",
          "prior_larval_prey_density"]
INT_BIOTIC = ["fish_x_emergent", "odonate_x_emergent",
              "odonate_x_submerged", "salamander_x_emergent"]
INT_STATE = ["rain_x_emergent", "waterlevel_x_emergent",
             "history_x_emergent"]
TIERS = {
    "E0_weather_history": BASE,
    "E1_plus_hydrology": BASE + HYDRO,
    "E2_plus_vegetation": BASE + HYDRO + PLANT,
    "E3_plus_stage_biotic": BASE + HYDRO + PLANT + BIOTIC + INT_BIOTIC,
    "E4_plus_local_state_filter": BASE + HYDRO + PLANT + BIOTIC
                                  + INT_BIOTIC + INT_STATE,
}
META = ["study_id", "route_id", "wetland_id", "site_id", "taxon_id",
        "event_time_utc", "last_prior_history_utc", "last_plant_measure_utc",
        "last_biotic_measure_utc", "strong_call_ci2plus"]
FRACTIONS = ["prior_site_strong_rate", "inundated_fraction", "emergent_cover",
             "submerged_cover", "open_water_fraction", "canopy_cover"]


def augment_and_check(frame):
    df = frame.copy()
    missing = [c for c in META + BASE + HYDRO + PLANT + BIOTIC
               if c not in df.columns]
    if missing:
        raise ValueError("Missing required measured fields: " + ", ".join(missing))
    if df.empty:
        raise ValueError("No site-event observations")
    for col in ["event_time_utc", "last_prior_history_utc",
                "last_plant_measure_utc", "last_biotic_measure_utc"]:
        df[col] = pd.to_datetime(df[col], utc=True, errors="raise")
        if df[col].isna().any():
            raise ValueError(f"Missing dated source: {col}")
    for prev in ["last_prior_history_utc", "last_plant_measure_utc",
                 "last_biotic_measure_utc"]:
        count = int((df[prev] >= df["event_time_utc"]).sum())
        if count:
            raise ValueError(f"Temporal leakage: {count} {prev} not prior to call")
    idcols = ["study_id", "route_id", "wetland_id", "site_id",
              "taxon_id", "event_time_utc"]
    if df[idcols].isna().any().any() or df.duplicated(idcols).any():
        raise ValueError("Missing IDs or duplicate site×taxon×event")
    y = df.strong_call_ci2plus
    if y.isna().any() or not set(y.unique()).issubset({0, 1}):
        raise ValueError("CI2plus must be observed binary 0/1")
    for col in dict.fromkeys(BASE + HYDRO + PLANT + BIOTIC):
        df[col] = pd.to_numeric(df[col], errors="raise")
        if not np.isfinite(df[col].to_numpy(dtype=float)).all():
            raise ValueError(f"Nonfinite measured covariate: {col}")
    for col in FRACTIONS:
        if ((df[col] < 0) | (df[col] > 1)).any():
            raise ValueError(f"Fraction outside [0,1]: {col}")
    if not set(df.fish_present.unique()).issubset({0, 1}):
        raise ValueError("fish_present must be observed 0/1")
    df["fish_x_emergent"] = df.fish_present * df.emergent_cover
    df["odonate_x_emergent"] = df.odonate_larval_density * df.emergent_cover
    df["odonate_x_submerged"] = df.odonate_larval_density * df.submerged_cover
    df["salamander_x_emergent"] = df.salamander_larval_density * df.emergent_cover
    df["rain_x_emergent"] = df.rain_contrast * df.emergent_cover
    df["waterlevel_x_emergent"] = df.water_level_cm * df.emergent_cover
    df["history_x_emergent"] = df.prior_site_strong_rate * df.emergent_cover
    return df


def crossvalidate(frame, n_splits=5):
    df = augment_and_check(frame)
    groups = df.study_id.astype(str) + ":" + df.route_id.astype(str)
    ng = int(groups.nunique())
    if ng < 3:
        raise ValueError("At least 3 independent study×route clusters required")
    splits = list(GroupKFold(n_splits=min(n_splits, ng)).split(df, groups=groups))
    records = []
    for tier, cols in TIERS.items():
        for fold, (i_train, i_valid) in enumerate(splits, 1):
            train, valid = df.iloc[i_train], df.iloc[i_valid]
            yt = train.strong_call_ci2plus.to_numpy(dtype=int)
            if len(np.unique(yt)) < 2:
                raise ValueError("A training fold has only one outcome class")
            transformer = ColumnTransformer([
                ("numeric", StandardScaler(), cols),
                ("taxon", OneHotEncoder(handle_unknown="ignore"), ["taxon_id"])
            ])
            model = Pipeline([
                ("features", transformer),
                ("logistic", LogisticRegression(max_iter=2000, C=1.0))
            ])
            features = cols + ["taxon_id"]
            model.fit(train[features], yt)
            probs = model.predict_proba(valid[features])[:, 1]
            y = valid.strong_call_ci2plus.to_numpy(dtype=int)
            records.append(dict(
                tier=tier, fold=fold, n_valid=len(y), n_training=len(yt),
                brier=float(brier_score_loss(y, probs)),
                logloss=float(log_loss(y, probs, labels=[0, 1]))))
    folds = pd.DataFrame(records)
    result = []
    for tier in TIERS:
        sub = folds.loc[folds.tier == tier]
        w = sub.n_valid.to_numpy()
        result.append(dict(
            tier=tier, n_valid=int(w.sum()), folds=len(sub),
            brier=float(np.average(sub.brier, weights=w)),
            logloss=float(np.average(sub.logloss, weights=w))))
    return folds, pd.DataFrame(result)


def fixture(n_routes=10, events_per_route=45, seed=120):
    rng = np.random.default_rng(seed)
    taxa = ["Pseudacris crucifer", "Lithobates clamitans", "Anaxyrus americanus"]
    rows = []
    for route in range(n_routes):
        baseline_veg = rng.uniform(.2, .9)
        fish = int(rng.random() < .55)
        for i in range(events_per_route):
            rain = rng.uniform(0, 3.5)
            veg = min(.98, max(.02, baseline_veg + rng.normal(0, .08)))
            odonate = rng.uniform(.1, 3.5)
            water = rng.normal(55, 20)
            prior = rng.uniform(.05, .65)
            eta = (-2 + .32 * rain + .008 * water + 1.2 * prior
                   - .75 * fish + .85 * fish * veg + .34 * odonate * veg)
            y = int(rng.random() < 1 / (1 + math.exp(-eta)))
            t = pd.Timestamp("2026-06-01T20:00:00Z") + pd.Timedelta(days=i)
            rows.append(dict(
                study_id="SYNTHETIC", route_id=str(route),
                wetland_id=f"wet-{route}", site_id=f"s-{route}",
                taxon_id=taxa[i % len(taxa)], event_time_utc=t.isoformat(),
                last_prior_history_utc=(t - pd.Timedelta(days=35)).isoformat(),
                last_plant_measure_utc=(t - pd.Timedelta(days=5)).isoformat(),
                last_biotic_measure_utc=(t - pd.Timedelta(hours=3)).isoformat(),
                strong_call_ci2plus=y, rain_contrast=rain,
                air_temp_c=rng.normal(22, 3),
                season_sin=math.sin(i / 45 * 2 * math.pi),
                season_cos=math.cos(i / 45 * 2 * math.pi),
                prior_site_strong_rate=prior, water_level_cm=water,
                hydroperiod_days=rng.uniform(25, 250),
                inundated_fraction=rng.uniform(.25, 1),
                water_temp_c=rng.normal(20, 2), emergent_cover=veg,
                emergent_stem_density=2 + veg * 30,
                submerged_cover=rng.uniform(0, 1),
                open_water_fraction=1 - veg,
                canopy_cover=rng.uniform(0, 1), fish_present=fish,
                odonate_larval_density=odonate,
                salamander_larval_density=rng.uniform(0, 4),
                prior_larval_prey_density=rng.uniform(0, 10)))
    return pd.DataFrame(rows)


def selftest():
    df = fixture()
    folds, summary = crossvalidate(df)
    assert len(summary) == 5 and folds.fold.nunique() == 5
    assert (summary.n_valid == len(df)).all()
    assert summary.brier.between(0, 1).all()
    broken = df.copy()
    broken.loc[0, "last_plant_measure_utc"] = broken.loc[0, "event_time_utc"]
    try:
        augment_and_check(broken)
    except ValueError as exc:
        assert "Temporal leakage" in str(exc)
    else:
        raise AssertionError("Temporal leakage guard did not fire")
    return {"status": "SELFTEST_PASS_SYNTHETIC_ONLY", "n": len(df),
            "tiers": list(summary.tier), "brier": summary.brier.round(4).tolist(),
            "leakage_guard": "pass"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input")
    parser.add_argument("--out", default="wetland_hierarchy_outputs")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(selftest(), indent=2))
        return
    if not args.input:
        parser.error("Provide --input independent field CSV or --self-test")
    frame = pd.read_csv(args.input)
    folds, summary = crossvalidate(frame)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    folds.to_csv(out / "blocked_cv_folds.csv", index=False)
    summary.to_csv(out / "blocked_cv_comparators.csv", index=False)
    (out / "interpretation.json").write_text(json.dumps({
        "data_rows": len(frame), "model_tiers": list(TIERS),
        "validation": "block held-out by entire study×route",
        "endpoint": "marginal CI2plus; NOT frogcs within-taxon multi-site C",
        "claim_boundary": "prediction only, no predation causal or history mechanism claim",
        "guard": "measured pre-event covariates, no silent imputation"
    }, indent=2) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
