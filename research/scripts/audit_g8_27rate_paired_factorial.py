"""Independent completeness and paired source-resampling audit of G8 27-rate model results.

Runs ONLY when all 64 genuine 80-year shards exist. Not a field-model fit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confirmatory_2x2_vegetation_predator_switch import original_draws
from run_g8_27rate_paired_factorial import (
    RATE_GRID, NSHARDS, SOURCES_PER_SHARD, N_BASE, EXPECTED_ROWS,
)

B = 10000
SEED = 20261107
ARMS = ("00", "10", "01", "11")
METRICS = ("compatibility", "factorial_compatibility", "viable_compatibility",
           "frog_log_cohort", "arm11_compatibility", "arm00_compatibility")


def require(x, msg):
    if not bool(x):
        raise AssertionError(msg)


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def response_contrasts(effects):
    """One paired row per original background × rate × original context."""
    keys = ["source_id", "rate_id", "context_id"]
    needed = ["accepted", "accepted_and_floor", "mean_log_F_B"]
    require(len(effects) == EXPECTED_ROWS, "Missing original 80-year G8 scenarios")
    require(set(effects.arm) == set(ARMS) and
            set(effects.rate_id) == set(range(27)) and
            set(effects.context_id) == {0, 1, 2} and
            set(effects.source_id) == set(range(256)),
            "Incomplete source × rate × stage × vegetation support")
    require(not effects.duplicated(keys + ["arm"]).any() and
            effects.groupby(keys, sort=False).arm.nunique().eq(4).all(),
            "Pairing is missing or duplicated")
    for rate_id, (attack, rho, conv) in enumerate(RATE_GRID):
        x = effects.loc[effects.rate_id == rate_id, ["attack", "rho", "conversion"]].to_numpy(float)
        require(len(x) == 256*3*4 and
                np.allclose(x, np.array([attack, rho, conv]), rtol=0, atol=0),
                "Rate-cell parameter drift")
    require(not effects[needed].isna().any().any() and
            np.isfinite(effects["mean_log_F_B"].to_numpy(float)).all(),
            "Nonfinite model outcomes")
    wide = effects.pivot(index=keys, columns="arm", values=needed)
    wide = wide.sort_index()
    require(len(wide) == 256*27*3, "Missing paired source/context")
    a = {name: np.column_stack([wide[(name, arm)].to_numpy(float) for arm in ARMS])
         for name in needed}
    df = wide.index.to_frame(index=False).reset_index(drop=True)
    # Fixed coding from original source:
    # 00 neither function; 10 frog refuge only; 01 odonate feeding support only; 11 both.
    df["compatibility"] = a["accepted"][:, 3] - a["accepted"][:, 0]
    df["factorial_compatibility"] = (
        a["accepted"][:, 3] - a["accepted"][:, 1] -
        a["accepted"][:, 2] + a["accepted"][:, 0]
    )
    df["viable_compatibility"] = (
        a["accepted_and_floor"][:, 3] - a["accepted_and_floor"][:, 0]
    )
    df["frog_log_cohort"] = a["mean_log_F_B"][:, 3] - a["mean_log_F_B"][:, 0]
    df["arm11_compatibility"] = a["accepted"][:, 3]
    df["arm00_compatibility"] = a["accepted"][:, 0]
    require(df[["compatibility", "viable_compatibility",
                "arm11_compatibility", "arm00_compatibility"]]
            .isin((-1., 0., 1.)).all().all(), "Invalid binary contrast")
    return df


def summarize(df, boot=B, seed=SEED):
    """Bootstrap *backgrounds*, not sites, across all matched rate/corner conditions."""
    require(not df.duplicated(["source_id", "rate_id", "context_id"]).any(),
            "Duplicated source-rate-context")
    require(df.source_id.nunique() > 1 and boot > 0,
            "Paired source resamples require multiple backgrounds")
    ids = sorted(df.source_id.unique())
    n = len(ids)
    if n != 256:
        raise AssertionError(f"Full G8 requires all 256 source backgrounds (got {n})")
    rng = np.random.default_rng(seed)
    resample = rng.integers(0, n, size=(boot, n))
    rows = []
    # Report all rate/corner combinations, plus equal-weight pooling across contexts
    # and across all 27 grid cells, without data-dependent trimming.
    plans = []
    for rid in range(27):
        for ctx in (0, 1, 2):
            plans.append((str(rid), str(ctx),
                          df[(df.rate_id == rid) & (df.context_id == ctx)]))
        plans.append((str(rid), "pooled_3",
                      df[df.rate_id == rid].groupby("source_id")[list(METRICS)]
                      .mean().reset_index()))
    plans.append(("pooled_27", "pooled_3",
                  df.groupby("source_id")[list(METRICS)].mean().reset_index()))
    for rate_id, context, g in plans:
        require(g.source_id.nunique() == 256, "Unpaired source subset in summary")
        g = g.groupby("source_id")[list(METRICS)].mean().reindex(ids)
        require(not g.isna().any().any(), "Missing source in aggregation")
        for metric in METRICS:
            values = g[metric].to_numpy(float)
            draws = values[resample].mean(axis=1)
            lo, hi = np.quantile(draws, (0.025, 0.975))
            rows.append(dict(rate_id=rate_id, context=context, metric=metric,
                             n_backgrounds=n, n_bootstrap=boot,
                             mean=float(values.mean()),
                             pointwise_mc95_low=float(lo), pointwise_mc95_high=float(hi),
                             positive_sources=int((values > 0).sum()),
                             negative_sources=int((values < 0).sum()),
                             zero_sources=int((values == 0).sum())))
    return pd.DataFrame(rows)


def check_old_same_rate(effects, original_file):
    """G8 original-rate cells reproduce PR161 true80, source-by-source, no retuning."""
    original = pd.read_csv(original_file, dtype={"arm": str}, keep_default_na=False)
    matched = effects.loc[
        effects.attack.eq(0.5) & effects.rho.eq(0.75) &
        effects.conversion.eq(effects.original_conversion)
    ].copy()
    require(len(matched) == 256*3*4 and len(original) == 256*3*4,
            "Exactly 3072 same-rate PR161 source rows required")
    cols = ["source_id", "context_id", "arm"]
    old = original.set_index(cols).sort_index()
    new = matched.set_index(cols).sort_index()
    require(old.index.is_unique and new.index.is_unique and old.index.equals(new.index),
            "Original matched source IDs differ")
    maxerr = 0.
    for key in ("model_id", "strength", "refuge_order", "gate_code", "conversion"):
        require(np.array_equal(old[key].to_numpy(), new[key].to_numpy()),
                "Original model/rate/nuisance pairing changed: " + key)
    for metric in ("mean_F_B", "mean_log_F_B", "log_OS", "log_OV", "log_SV", "log_OSV",
                   "min_F", "min_S"):
        err = float(np.max(np.abs(old[metric].to_numpy(float) -
                                  new[metric].to_numpy(float))))
        maxerr = max(maxerr, err)
    require(maxerr < 1e-10, f"PR161 80-year original outcome replay mismatch: {maxerr}")
    for key in ("accepted", "floor_ok", "accepted_and_floor"):
        require(np.array_equal(old[key].astype(str).to_numpy(),
                               new[key].astype(str).to_numpy()),
                "Original accepted/floor flags differ: " + key)
    return maxerr


def run(*, shards, old, out):
    shards, old, out = Path(shards), Path(old), Path(out)
    paths = sorted(shards.rglob("g8_true80_*_receipt.json"))
    require(len(paths) == NSHARDS, f"Need all {NSHARDS} successful 80-year receipts; got {len(paths)}")
    data = []
    all_hashes = {}
    for shard in range(NSHARDS):
        matches = [p for p in paths if p.name == f"g8_true80_{shard:02d}_receipt.json"]
        require(len(matches) == 1, "Missing/duplicated shard " + str(shard))
        receipt = json.loads(matches[0].read_text())
        require(receipt["status"] == "G8_TRUE80_SOURCE_SHARD" and
                receipt["shard"] == shard and receipt["n_shards"] == NSHARDS and
                receipt["sources"] == list(range(shard*SOURCES_PER_SHARD,
                                                   (shard+1)*SOURCES_PER_SHARD)) and
                receipt["rate_ids"] == list(range(27)) and
                receipt["contexts"] == [0, 1, 2] and
                receipt["years"] == 80 and receipt["window"] == 20 and
                receipt["negative_control_max_abs"] < 1e-10 and
                receipt["n_scenarios"] == SOURCES_PER_SHARD * 27 * 3 * 4 and
                receipt["n_vertices"] == SOURCES_PER_SHARD * 27 * 3 * 4 * 8,
                "Shard full-design integrity failure: " + str(shard))
        for filename, expected in receipt["files_sha256"].items():
            f = matches[0].with_name(filename)
            require(f.is_file() and file_sha(f) == expected,
                    "Input scientific blob SHA mismatch " + filename)
            all_hashes[filename] = expected
        ep = matches[0].with_name(f"g8_true80_{shard:02d}_effects.csv.gz")
        e = pd.read_csv(ep, dtype={"arm": str}, keep_default_na=False)
        require(e.source_id.nunique() == SOURCES_PER_SHARD and
                len(e) == SOURCES_PER_SHARD * 27 * 3 * 4 and
                not e.draw_id.duplicated().any(), "Corrupt effect rows in shard " + str(shard))
        data.append(e)
    effects = pd.concat(data, ignore_index=True)
    require(len(effects) == EXPECTED_ROWS and effects.draw_id.is_unique,
            "Incomplete original source experiment")
    # Independent original design re-creation, from 3,600-model source seed,
    # and original PR161 80-year outcome replay.
    _, design, _ = original_draws()
    original_map = design.set_index(["source_id", "context_id", "arm"]).sort_index()
    fixed = effects.set_index(["source_id", "context_id", "arm"]).sort_index()
    for key in ("model_id", "strength", "refuge_order", "gate_code"):
        expected = original_map[key].reindex(fixed.index)
        require(np.array_equal(expected.to_numpy(), fixed[key].to_numpy()),
                "Source identity corrupted: " + key)
    replay_maxerr = check_old_same_rate(effects, old)
    contrasts = response_contrasts(effects)
    summary = summarize(contrasts)
    out.mkdir(parents=True, exist_ok=True)
    contrasts.to_csv(out / "g8_all_source_rate_context_paired.csv.gz",
                     index=False, compression={"method": "gzip", "mtime": 0})
    summary.to_csv(out / "g8_full_27rate_compatibility_abundance_summary.csv", index=False)
    # Count four directions and frog abundance signs WITHOUT replacing continuous estimates.
    rate_compare = (contrasts.groupby("rate_id")
                    .agg(
                        n_source_context=("source_id", "size"),
                        compatible_increment_mean=("compatibility", "mean"),
                        compatible_11_mean=("arm11_compatibility", "mean"),
                        compatible_00_mean=("arm00_compatibility", "mean"),
                        viable_increment_mean=("viable_compatibility", "mean"),
                        log_frog_cohort_increment_mean=("frog_log_cohort", "mean"),
                        count_compatibility_positive=("compatibility", lambda x: int((x>0).sum())),
                        count_compatibility_negative=("compatibility", lambda x: int((x<0).sum())),
                        count_frog_benefit_positive=("frog_log_cohort", lambda x: int((x>0).sum())),
                        count_frog_benefit_negative=("frog_log_cohort", lambda x: int((x<0).sum()))
                    ).reset_index())
    rate_compare["attack"] = rate_compare.rate_id.map(lambda i: RATE_GRID[int(i)][0])
    rate_compare["rho"] = rate_compare.rate_id.map(lambda i: RATE_GRID[int(i)][1])
    rate_compare["conversion"] = rate_compare.rate_id.map(lambda i: RATE_GRID[int(i)][2])
    rate_compare.to_csv(out / "g8_27rate_descriptive_counts.csv", index=False)
    files = sorted(p for p in out.iterdir() if p.is_file())
    receipt = dict(
        status="G8_27RATE_TRUE80_ALL_256_SOURCE_SUCCESS",
        source_shards=NSHARDS, n_sources=256, n_rates=27, n_contexts=3,
        n_plant_arms=4, n_original_true80_scenarios=EXPECTED_ROWS,
        n_source_vertices=EXPECTED_ROWS*8,
        original_model_pr161_rate_cell_replay_max_abs=replay_maxerr,
        no_missing_source_or_success_filter=True, fixed_rate_grid=True,
        prior_negative_G5_G7_not_overturned=True,
        bootstrap_draws=B, bootstrap_seed=SEED,
        inference="Model-conditional source-background sensitivity, no wild field likelihood",
        all_shard_sha256=all_hashes,
        output_sha256={p.name:file_sha(p) for p in files})
    (out / "g8_completion_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("G8_COMPLETE_27RATE_AUDIT " + json.dumps({
        k: receipt[k] for k in ("status", "n_sources", "n_rates",
                "n_original_true80_scenarios", "original_model_pr161_rate_cell_replay_max_abs")}),
          flush=True)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--shards", required=True, type=Path)
    parser.add_argument("--old", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    run(shards=args.shards, old=args.old, out=args.out)
