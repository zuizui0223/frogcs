#!/usr/bin/env python3
"""Exploratory site-by-taxon checkerboard C-score, preserving both incidence margins."""
from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

import run_naamp_local_chorus_memory_targeting as memory

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "exploratory" / "checkerboard_v1.json"
SEED = 20261020
B = 99
Q = 1.959963984540054


def cscore(rows):
    """Stone-Roberts C-score averaged over unordered pairs of active taxa."""
    n = len(rows)
    if n < 2:
        return float("nan")
    total = 0.0
    for i in range(n - 1):
        ai = rows[i]
        ki = len(ai)
        for j in range(i + 1, n):
            common = len(ai & rows[j])
            total += (ki - common) * (len(rows[j]) - common)
    return total / (n * (n - 1) / 2.0)


def trade(rows, rng):
    n = len(rows)
    i = rng.randrange(n)
    j = rng.randrange(n - 1)
    if j >= i:
        j += 1
    a, b = rows[i], rows[j]
    only_a = a - b
    only_b = b - a
    if not only_a or not only_b:
        return 0
    shared = a & b
    basket = sorted(only_a | only_b)
    rng.shuffle(basket)
    k = len(only_a)
    rows[i] = shared | set(basket[:k])
    rows[j] = shared | set(basket[k:])
    return 1


def fixed_margins_null(rows, rng):
    current = [set(s) for s in rows]
    m = len(current)
    observed = cscore(current)
    changed = 0
    for _ in range(max(80, 30*m)):
        changed += trade(current, rng)
    null = []
    for b in range(B):
        for _ in range(max(20, 8*m)):
            changed += trade(current, rng)
        null.append(cscore(current))
    a = np.asarray(null, dtype=float)
    expected = float(a.mean())
    sd = float(a.std(ddof=1))
    return {
        "n_species": m,
        "observed_cscore": float(observed),
        "null_cscore_mean": expected,
        "null_cscore_sd": sd,
        "delta_cscore": float(observed - expected),
        "ses_cscore": float((observed - expected)/sd) if sd > 1e-10 else None,
        "successful_curveball_trades": changed,
        "n_draws": B,
    }


def fit_mean_delta(df, ycol):
    if df.empty:
        return None
    fit = sm.OLS(
        df[ycol].astype(float).to_numpy(),
        np.ones((len(df),1)),
    ).fit(cov_type="cluster",cov_kwds={"groups":df.route_cluster.astype(str)})
    b = float(fit.params[0])
    se = float(fit.bse[0])
    return {
        "n": int(len(df)), "n_routes": int(df.route_cluster.nunique()),
        "mean": b, "route_cluster_se": se, "ci95": [b-Q*se,b+Q*se],
        "p_two_sided": float(fit.pvalues[0]),
    }


def paired_analysis(pairs, run_table, mode):
    key = "delta_cscore_" + mode
    ix = run_table.set_index("RunID")[key].to_dict()
    selected = pairs[
        pairs.wet_RunID.astype(str).isin(ix) &
        pairs.dry_RunID.astype(str).isin(ix)
    ].copy()
    if selected.empty:
        return {"n_pairs":0}
    selected["delta_wet"] = selected.wet_RunID.astype(str).map(ix)
    selected["delta_dry"] = selected.dry_RunID.astype(str).map(ix)
    selected["wet_minus_dry"] = selected.delta_wet - selected.delta_dry
    mean = fit_mean_delta(selected, "wet_minus_dry")
    if len(selected) < 100 or selected.route_cluster.nunique()<40:
        return {"n_pairs":len(selected),"paired_mean":mean,
                "rain_contrast_regression":None}
    formula = (
        "wet_minus_dry ~ rain_contrast + temp_difference + "
        "doy_difference + year_gap + C(State) + C(RunNumber)"
    )
    reg = smf.ols(formula, data=selected).fit(
        cov_type="cluster",cov_kwds={"groups":selected.route_cluster}
    )
    coef = float(reg.params["rain_contrast"])
    se = float(reg.bse["rain_contrast"])
    return {
        "paired_mean": mean,
        "n_pairs": int(len(selected)),
        "n_routes": int(selected.route_cluster.nunique()),
        "rain_contrast_regression": {
            "beta": coef,
            "se_cluster": se,
            "ci95": [coef-Q*se,coef+Q*se],
            "p_two_sided":float(reg.pvalues["rain_contrast"]),
            "formula":formula,
        }
    }


def make_rows(rid, sampled, ci, call_threshold):
    stops = sorted(sampled[rid], key=lambda s:int(s))
    idx = {s:i for i,s in enumerate(stops)}
    spp = defaultdict(set)
    for st in stops:
        for sp, value in ci.get((rid,st),{}).items():
            if value >= call_threshold:
                spp[sp].add(idx[st])
    return [spp[taxon] for taxon in sorted(spp)],len(spp)


def main():
    raw = memory.load_retry()
    runs, sets = memory.base.build_runs(raw)
    eligible = set(runs.RunID.astype(str))
    sampled, _ = memory.spatial.stop_matrix(raw, eligible)
    ci = memory.ci_map(raw, eligible, sampled)
    pairs = memory.base.pair_runs(runs, sets).copy().reset_index(drop=True)
    ridset = set(pairs.wet_RunID.astype(str)) | set(pairs.dry_RunID.astype(str))
    route = {str(x.RunID):str(x.route_cluster)
             for x in runs.itertuples(index=False)}

    rng = random.Random(SEED)
    records = []
    for rid in sorted(ridset):
        row = {"RunID":rid,"route_cluster":route[rid]}
        for mode, threshold in (("all",1),("strong",2)):
            cells, species = make_rows(rid,sampled,ci,threshold)
            if species < 3:
                continue
            z = fixed_margins_null(cells, rng)
            for name,value in z.items():
                row[name + "_" + mode] = value
        records.append(row)
    df = pd.DataFrame(records)
    out = {
        "analysis":"naamp_conditional_checkerboard_curveball_v1",
        "status":"posthoc_exploratory_user_authorized_not_rc6",
        "contract":"exploration/NAAMP_LOCAL_HISTORY_CHECKERBOARD_CONTRACT_2026_10_20.json",
        "parameters":{"seed":SEED,"draws_per_run":B,
                      "rows":"taxa", "columns":"ten fixed route stops",
                      "fixed_margins":["species detected-stop counts","stop species richness"]},
        "coverage":{
            "matched_pairs":int(len(pairs)),
            "unique_paired_runs":len(ridset),
        },
        "results":{},
        "interpretation_boundaries":{
            "competition_or_active_avoidance_established":False,
            "rainfall_causality_established":False,
            "independent_replication":False,
            "checkerboard_same_as_within_taxon_concentration":False,
        }
    }
    for mode in ("all","strong"):
        key="delta_cscore_"+mode
        if key not in df:
            out["results"][mode]={"eligible_runs":0}
            continue
        valid = df[df[key].notna()].copy()
        model = fit_mean_delta(valid,key)
        paired = paired_analysis(pairs,valid,mode)
        route_means=valid.groupby("route_cluster")[key].mean().to_numpy()
        out["results"][mode]={
            "eligible_runs":int(len(valid)),
            "eligible_routes":int(valid.route_cluster.nunique()),
            "unvaried_null_cscore_runs":int(
                (valid["null_cscore_sd_"+mode]<1e-10).sum()
            ),
            "mean_observed_cscore":float(valid["observed_cscore_"+mode].mean()),
            "mean_fixed_marginal_null_cscore":float(
                valid["null_cscore_mean_"+mode].mean()),
            "mean_residual_clustered":model,
            "equal_route_mean_residual":float(route_means.mean()),
            "paired_wet_minus_dry":paired,
            "classification":{
                "significant_excess_checkerboard":
                    bool(model["mean"]>0 and model["ci95"][0]>0),
                "wet_rain_enhanced_checkerboard":
                    bool(paired.get("paired_mean") and
                         paired["paired_mean"]["mean"]>0 and
                         paired["paired_mean"]["ci95"][0]>0),
            }
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("CHECKERBOARD_RESULT_BEGIN")
    print(json.dumps(out,sort_keys=True))
    print("CHECKERBOARD_RESULT_END")


if __name__=="__main__":
    main()
