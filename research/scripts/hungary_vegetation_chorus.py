#!/usr/bin/env python3
"""Independent empirical screening: 2024 Hungary wetland plant cover and frog calls.

Reads the original, CC-BY-4.0 Zenodo 15044115 files pinned in research/external/.
Models whether *any anuran* is detected per acoustic visit, comparing incremental
out-of-wetland value of water depth, emergent and submerged vegetation.
Visual surveys are a METHOD SENSITIVITY (not truth about abundance).
No matched wet/dry runs, historical between-year chorus, calling intensity,
actual predation, demographic occupancy or vegetation changes are available.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SOURCE = "Mizsei & Wenner (2025), Zenodo 10.5281/zenodo.15044115, CC BY 4.0"
MD5 = {
    "wetland_amp_site_data.csv": "795da443249760fbc0bf30249910a4ef",
    "wetland_amp_surv_data.csv": "edcd6f12518192c01e3dbae8521c16c9",
}
FROGS = ["Pelobates fuscus", "Rana dalmatina", "Bombina bombina",
         "Hyla arborea", "Pelophylax ridibundus", "Bufotes viridis", "Bufo bufo"]
NEWTS = ["Lissotriton vulgaris", "Triturus dobrogicus"]
BASE = ["doy", "doy_sq", "temp", "humid", "prec"]
TIERS = {
    "W0_weather_phenology": (BASE, []),
    "W1_plus_depth_context": (BASE + ["depth"], ["ci"]),
    "W2_plus_emergent": (BASE + ["depth", "cover_emerged"], ["ci"]),
    "W2alt_plus_submerged": (BASE + ["depth", "cover_submers"], ["ci"]),
    "W3_both_plants_diversity": (
        BASE + ["depth", "cover_emerged", "cover_submers", "plant_sp"], ["ci"]),
}
SEED = 20261025


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def require(condition, msg):
    if not condition:
        raise ValueError(msg)


def load_data(folder, enforce_md5=True):
    folder = Path(folder)
    for fn, expected in MD5.items():
        p = folder / fn
        require(p.is_file(), f"Missing raw Zenodo input: {p}")
        digest = md5(p)
        if enforce_md5:
            require(digest == expected,
                    f"Source checksum mismatch for {fn}: {digest} != {expected}")
    sites = pd.read_csv(folder / "wetland_amp_site_data.csv")
    visits = pd.read_csv(folder / "wetland_amp_surv_data.csv")
    require(len(sites) == 29, f"Unexpected site row count {len(sites)}")
    require(len(visits) == 381, f"Unexpected survey row count {len(visits)}")
    require(not sites["site"].duplicated().any(), "Site IDs not unique")
    require(visits["site"].isin(sites["site"]).all(),
            "Survey site without matching habitat row")
    require(all(x in visits.columns for x in FROGS + NEWTS),
            "Missing named amphibian columns")
    require(set(visits["method"]) == {"acoustic", "visual", "dipnet", "bottletrap"},
            "Method codes changed")
    numeric = ["depth", "cover_emerged", "cover_submers", "plant_sp", "fish"]
    for col in numeric:
        require(sites[col].notna().all(), f"Missing measured {col}")
    require(sites["fish"].isin([0, 1]).all(), "Fish variable not binary")
    for col in ["cover_emerged", "cover_submers"]:
        require(sites[col].between(0, 100).all(), f"Invalid % cover {col}")
    for col in FROGS + NEWTS:
        require((pd.to_numeric(visits[col], errors="coerce") >= 0).all(),
                f"Missing/negative species observations: {col}")
    require(visits["doy"].notna().all() and visits["date"].notna().all(),
            "Survey phenology missing")
    visits = visits.copy()
    sites = sites.copy()
    visits["frog_species_detected"] = (visits[FROGS] > 0).sum(axis=1)
    visits["newt_species_detected"] = (visits[NEWTS] > 0).sum(axis=1)
    visits["frog_any"] = (visits["frog_species_detected"] > 0).astype(int)
    visits["any_amphibian"] = ((visits[FROGS + NEWTS] > 0).any(axis=1)).astype(int)
    visits["doy_sq"] = ((visits["doy"] - 133.0) / 40.0) ** 2
    require(set(visits["method"]) == {"acoustic", "visual", "dipnet", "bottletrap"},
            "Unknown methods")
    df = visits.merge(sites, on="site", validate="many_to_one")
    for col in BASE + ["depth", "cover_emerged", "cover_submers", "plant_sp"]:
        require(np.isfinite(pd.to_numeric(df[col], errors="coerce")).all(),
                f"Not enough valid observed numeric entries: {col}")
    return sites, visits, df


def fit_predict_blocked(frame, n_splits=5):
    require(frame["site"].nunique() >= n_splits, "Not enough independent sites")
    groups = frame["site"].to_numpy()
    yy = frame["frog_any"].astype(int).to_numpy()
    splits = list(GroupKFold(n_splits=n_splits).split(frame, yy, groups=groups))
    out = {}
    for tier, (numcols, cats) in TIERS.items():
        xcols = numcols + cats
        pred = np.full(len(frame), np.nan)
        for itrain, ival in splits:
            Xtrain, ytrain = frame.iloc[itrain][xcols], yy[itrain]
            require(len(np.unique(ytrain)) == 2,
                    f"Training data contain only one label in {tier}")
            tfs = [("num", StandardScaler(), numcols)]
            if cats:
                tfs.append(("cat", OneHotEncoder(handle_unknown="ignore"), cats))
            pipeline = Pipeline([
                ("prep", ColumnTransformer(tfs)),
                ("model", LogisticRegression(C=1.0, max_iter=3000)),
            ])
            pipeline.fit(Xtrain, ytrain)
            pred[ival] = pipeline.predict_proba(frame.iloc[ival][xcols])[:, 1]
        require(np.isfinite(pred).all(), "A held-out prediction missing")
        out[tier] = pred
    return yy, out


def outcome_cv(frame, bootstrap=1000):
    yy, preds = fit_predict_blocked(frame)
    require(np.isfinite(yy).all(), "Outcome missing")
    sites = frame["site"].to_numpy()
    keys = sorted(set(sites))
    per_site = {}
    for tier, v in preds.items():
        p = np.clip(v, 1e-9, 1 - 1e-9)
        brier = (yy - p) ** 2
        loss = -(yy * np.log(p) + (1 - yy) * np.log(1 - p))
        per_site[tier] = np.array([
            np.mean(brier[sites == s]) for s in keys
        ])
        per_site[(tier, "logloss")] = np.array([
            np.mean(loss[sites == s]) for s in keys
        ])
    scores = {}
    for tier, p in preds.items():
        pp = np.clip(p, 1e-9, 1 - 1e-9)
        scores[tier] = {
            "site_balanced_brier": float(per_site[tier].mean()),
            "visit_weighted_brier": float(np.mean((yy - p) ** 2)),
            "site_balanced_logloss": float(per_site[(tier, "logloss")].mean()),
            "visit_weighted_logloss": float(np.mean(
                -(yy * np.log(pp) + (1 - yy) * np.log(1 - pp)))),
        }
    baseline_pairs = [
        ("W1_plus_depth_context", "W0_weather_phenology"),
        ("W2_plus_emergent", "W1_plus_depth_context"),
        ("W2alt_plus_submerged", "W1_plus_depth_context"),
        ("W3_both_plants_diversity", "W1_plus_depth_context"),
        ("W3_both_plants_diversity", "W2_plus_emergent"),
    ]
    rng = np.random.default_rng(SEED + len(frame))
    sampled = rng.integers(0, len(keys), size=(bootstrap, len(keys)))
    comparison = {}
    for full, ref in baseline_pairs:
        diff = per_site[ref] - per_site[full]  # Positive means improvement
        boot = diff[sampled].mean(axis=1)
        comparison[f"{full}_versus_{ref}"] = {
            "site_balanced_brier_improvement": float(diff.mean()),
            "cluster_bootstrap_95ci": [float(np.quantile(boot, p))
                                       for p in [.025, .975]],
            "bootstrap_fraction_positive": float(np.mean(boot > 0)),
            "interpretation": "exploratory CV prediction difference, "
                              "not a causal estimate or fixed significance test",
        }
    return {
        "visits": len(frame),
        "sites": int(frame.site.nunique()),
        "frog_positive_visits": int(yy.sum()),
        "positive_visit_rate": float(np.mean(yy)),
        "models": scores,
        "incremental": comparison,
    }


def within_season_history(acoustic):
    # History only among same-year earlier monitoring visits: NOT years of site fidelity.
    a = acoustic.sort_values(["site", "date", "doy"]).copy()
    out = []
    for site, d in a.groupby("site", sort=False):
        if len(d) < 2:
            continue
        first = int(d["frog_any"].iloc[0])
        for val in d["frog_any"].iloc[1:].astype(int):
            out.append({"site": site, "initial_detected": first,
                        "later_detected": int(val)})
    h = pd.DataFrame(out)
    return {
        "sites_with_repeat": int(h.site.nunique()),
        "later_visits": int(len(h)),
        "first_visit_positive_sites": int(
            h.groupby("site")["initial_detected"].first().sum()),
        "later_rate_if_first_positive":
            float(h.loc[h.initial_detected == 1, "later_detected"].mean())
            if (h.initial_detected == 1).any() else None,
        "later_rate_if_first_negative":
            float(h.loc[h.initial_detected == 0, "later_detected"].mean())
            if (h.initial_detected == 0).any() else None,
        "boundary": "same-spring repeated detection; no independent year "
                    "and no physical individual identity",
    }


def analyze(folder, bootstrap=1000):
    sites, visits, df = load_data(folder)
    methods = {}
    for meth in ["acoustic", "visual", "dipnet", "bottletrap"]:
        d = df.loc[df.method == meth]
        methods[meth] = {
            "visits": int(len(d)), "sites": int(d.site.nunique()),
            "anuran_positive_visits": int(d.frog_any.sum()),
            "anuran_positive_fraction": float(d.frog_any.mean()),
            "newt_positive_visits": int((d.newt_species_detected > 0).sum()),
        }
    results = {}
    for meth in ["acoustic", "visual"]:
        group = df.loc[df.method == meth].reset_index(drop=True)
        results[meth] = outcome_cv(group, bootstrap)
    auc = df.loc[df.method == "acoustic"]
    history = within_season_history(auc)
    summary = {
        "study": SOURCE,
        "study_design": "29 wetland sites, 2024 spring, cross-sectional "
                        "site covariates, repeated non-standardizable methods",
        "data_sha256": {
            str(p.name): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(folder).glob("wetland_amp_*.csv")
        },
        "n_site_rows": int(len(sites)),
        "n_survey_rows": int(len(visits)),
        "distinct_doy": int(visits.doy.nunique()),
        "fish_positive_sites": int(sites.fish.sum()),
        "site_context_counts": {
            str(k): int(v) for k, v in sites.ci.value_counts().items()
        },
        "emergent_cover_min_max": [
            float(sites.cover_emerged.min()),
            float(sites.cover_emerged.max()),
        ],
        "methods": methods,
        "prediction_cv": results,
        "within_spring_acoustic_history": history,
        "boundaries": [
            "No historic multi-year strong-chorus re-use: single 2024 season.",
            "No ordinal CallingIndex, eggs, tadpole survival or predation.",
            "Fish × emergent cover is NONESTIMABLE: only two fish sites.",
            "Within-site static plants cannot identify plant-change causal effect.",
            "Models predict acoustic detection, not true adult abundance/occupancy.",
            "GroupKFold leaves out whole sites; no independent study/year holdout.",
            "Bootstraps condition on fixed held-out predictions: exploratory.",
            "Multiple tier comparisons are exploratory and not pre-registered.",
        ],
    }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="research/external/zenodo_15044115")
    parser.add_argument("--output", default="research/results/hungary_2024_screen")
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()
    x = analyze(args.source, args.bootstrap)
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    (target / "observed_results.json").write_text(
        json.dumps(x, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("BEGIN_HUNGARY_ACTUAL_RESULTS")
    print(json.dumps(x, indent=2, ensure_ascii=False))
    print("END_HUNGARY_ACTUAL_RESULTS")


if __name__ == "__main__":
    main()
