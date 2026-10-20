#!/usr/bin/env python3
"""Exploratory within-species/pair historical SiteID targeting with local observed covariates."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

import run_naamp_local_chorus_memory_targeting as memory

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "exploratory" / "history_context_v1.json"
Q = 1.959963984540054


def air_temperature_map(raw, runs):
    scale = {str(r.RunID): str(r.TempScale) for r in runs.itertuples(index=False)}
    out = {}
    for s in raw["Stops.csv"]:
        rid = (s.get("RunID") or "").strip()
        st = (s.get("StopNumber") or "").strip()
        if rid not in scale or not st or (s.get("SkippedStop") or "").strip() != "0":
            continue
        try:
            v = float((s.get("AirTemp") or "").strip())
        except (TypeError, ValueError):
            continue
        if not math.isfinite(v):
            continue
        if scale[rid] == "F":
            v = (v - 32.0) * 5.0 / 9.0
        elif scale[rid] != "C":
            continue
        if -30.0 <= v <= 55.0:
            out[(rid, st)] = v
    return out


def fit_group_fixed_effects(data, adjusted):
    response = "wet_strong"
    cols = ["prior_site_strong"]
    if adjusted:
        cols += [
            "temperature_c", "other_taxa_ci2", "prior_other_strong",
            "stop_position", "stop_position_sq",
        ]
    work = data.copy()
    means = work.groupby("pair_species", sort=False)
    y = work[response] - means[response].transform("mean")
    X = pd.DataFrame(index=work.index)
    for col in cols:
        demeaned = work[col] - means[col].transform("mean")
        if col != "prior_site_strong":
            sd = float(work[col].std(ddof=0))
            if sd > 1e-10:
                demeaned = demeaned / sd
        X[col] = demeaned
    fit = sm.OLS(y.astype(float), X.astype(float)).fit(
        cov_type="cluster", cov_kwds={"groups": work["route_cluster"].astype(str)}
    )
    b = float(fit.params["prior_site_strong"])
    se = float(fit.bse["prior_site_strong"])
    return {
        "n_stop_rows": int(len(work)),
        "n_species_pair_groups": int(work.pair_species.nunique()),
        "n_routes": int(work.route_cluster.nunique()),
        "n_species": int(work.species.nunique()),
        "beta_history": b,
        "route_cluster_se": se,
        "ci95": [b-Q*se,b+Q*se],
        "p_two_sided": float(fit.pvalues["prior_site_strong"]),
        "adjusted": adjusted,
        "predictor_rank": int(np.linalg.matrix_rank(X.to_numpy())),
        "predictor_count": len(cols),
        "additional_covariates": cols[1:],
    }


def main():
    raw = memory.load_retry()
    runs, sets = memory.base.build_runs(raw)
    eligible = set(runs.RunID.astype(str))
    sampled, _ = memory.spatial.stop_matrix(raw, eligible)
    sites = memory.site_map(raw, eligible)
    ci = memory.ci_map(raw, eligible, sampled)
    meta, by_stratum = memory.build_history(runs, sampled, sites, ci)
    temps = air_temperature_map(raw, runs)

    all_pairs = memory.base.pair_runs(runs, sets).copy().reset_index(drop=True)
    stable = all_pairs.loc[
        np.asarray([memory.stable_pair(p, sampled, sites)
                    for p in all_pairs.itertuples(index=False)], bool)
    ].copy().reset_index(drop=True)

    rows = []
    unmatched = 0
    for pid, p in enumerate(stable.itertuples(index=False)):
        part = memory.pair_rows(
            pid, p, sampled, sites, ci, meta, by_stratum, False
        )
        if not part:
            continue
        w = str(p.wet_RunID)
        inv = defaultdict(list)
        for st in sampled[w]:
            inv[sites[(w, st)]].append(st)
        cutoff = int(p.year_earlier)
        key = meta[w]["key"]
        previous = [rid for rid in by_stratum[key]
                    if meta[rid]["year"] < cutoff]

        prior_at_site = defaultdict(set)
        for rid in previous:
            for st in sampled.get(rid, set()):
                sid = sites.get((rid, st))
                if sid is None:
                    continue
                for species, value in ci.get((rid, st), {}).items():
                    if value >= 2:
                        prior_at_site[sid].add(species)
        for x in part:
            found = inv.get(x["SiteID"], [])
            if len(found) != 1:
                unmatched += 1
                continue
            st = found[0]
            sp = x["species"]
            other = sum(
                int(value >= 2)
                for taxon, value in ci.get((w, st), {}).items()
                if taxon != sp
            )
            pos = (float(st) - 5.5) / 4.5
            rows.append({
                **x,
                "temperature_c": temps.get((w, st), np.nan),
                "other_taxa_ci2": float(other),
                "prior_other_strong": float(
                    len(prior_at_site.get(x["SiteID"], set()) - {sp})
                ),
                "stop_position": pos,
                "stop_position_sq": pos**2,
            })

    d = pd.DataFrame(rows)
    if d.empty:
        raise RuntimeError("No prior-history focal cells")
    candidate_groups = int(d.pair_species.nunique())
    total_rows = len(d)
    complete = d.dropna(
        subset=["temperature_c", "prior_site_strong", "wet_strong",
                "other_taxa_ci2", "prior_other_strong", "stop_position"]
    ).copy()
    informative = complete.groupby("pair_species")["prior_site_strong"].nunique()
    groups = set(informative[informative >= 2].index)
    complete = complete[complete.pair_species.isin(groups)].copy()

    if complete.empty:
        raise RuntimeError("No informative complete-case groups")
    baseline = fit_group_fixed_effects(complete, adjusted=False)
    adjusted = fit_group_fixed_effects(complete, adjusted=True)
    support = bool(
        adjusted["n_species_pair_groups"] >= 350 and
        adjusted["n_routes"] >= 200 and
        adjusted["ci95"][0] > 0 and adjusted["beta_history"] > 0
    )
    result = {
        "analysis": "naamp_historical_site_vs_local_context_v1",
        "status": "posthoc_exploratory_user_authorized_not_rc6",
        "contract": "exploration/NAAMP_LOCAL_HISTORY_CHECKERBOARD_CONTRACT_2026_10_20.json",
        "coverage": {
            "matched_pairs": len(all_pairs), "stable_site_pairs": len(stable),
            "candidate_stop_rows": total_rows,
            "candidate_pair_species_groups": candidate_groups,
            "unmatched_or_duplicate_siteids": unmatched,
            "stop_temperature_complete_case_fraction": float(
                d.temperature_c.notna().mean()
            ),
        },
        "baseline_same_sample": baseline,
        "adjusted_same_sample": adjusted,
        "history_coefficient_attenuation_fraction": (
            1.0 - adjusted["beta_history"] / baseline["beta_history"]
            if abs(baseline["beta_history"]) > 1e-10 else None
        ),
        "classification": {
            "historical_site_predicts_after_measured_local_context": support,
            "measured_stop_conditions_are_all_environmental_drivers": False,
            "direct_hydrology_measured": False,
            "site_quality_vs_biological_memory_discriminated": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("HISTORY_CONTEXT_RESULT_BEGIN")
    print(json.dumps(result, sort_keys=True))
    print("HISTORY_CONTEXT_RESULT_END")


if __name__ == "__main__":
    main()
