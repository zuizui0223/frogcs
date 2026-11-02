"""Joint structure × nuisance rejection ABC-POM for the original 3,600 models.

The target is a *model-native* four-sign pattern, not observed-site likelihood.
One proposal selects an actual main-catalog mechanism, a stage context and
independent nuisance parameters BEFORE running the original deterministic kernel.
No resimulation of accepted draws is used for acceptance statistics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from final_mechanism_common import CONTEXTS, OUT as MAIN_OUT, catalog, evaluate

DEST = Path(__file__).resolve().parents[1] / "results/abc_pom_main3600_20261101"
SEED = 20261101
SOURCE_SHA = "5e2f0a87c639df373fa2700b29403d2ab417a1cc"
CORNERS = [(v, s, d) for v in (0.0, 1.0) for s in (0.25, 2.0) for d in (0.25, 2.0)]
AXES = [
    "edge_SD", "edge_DS", "cover_SF", "cover_DF", "cover_DS",
    "cover_SD", "support_DF", "support_DS", "survival", "timing",
    "reverse", "behavior", "litter", "context_id", "gate_code",
    "attack", "rho", "conversion", "strength", "refuge_order",
]


def draw_prior(n: int, seed: int = SEED, models: pd.DataFrame | None = None) -> pd.DataFrame:
    """Finite, explicitly artificial and independent priors. Whole draw is shard-invariant."""
    if n < 1:
        raise ValueError("n must be positive")
    if models is None:
        models = catalog()
    if len(models) != 3600 or not np.array_equal(models.model_id.to_numpy(), np.arange(3600)):
        raise ValueError("Model catalog mismatch: frozen 3,600 canonical IDs required")
    rng = np.random.default_rng(seed)
    draws = pd.DataFrame({
        "draw_id": np.arange(n, dtype=int),
        "model_id": rng.integers(0, len(models), size=n),
        "context_id": rng.integers(0, len(CONTEXTS), size=n),
        "attack": rng.choice([0.5, 1.5, 3.0], size=n),
        "rho": rng.choice([0.25, 0.5, 0.75], size=n),
        "conversion": rng.choice([2.0, 4.0, 8.0], size=n),
        "strength": rng.choice([0.5, 1.0], size=n),
        "refuge_order": rng.choice(["S", "equal", "D"], size=n),
        "gate_code": rng.integers(0, 2, size=n),
    })
    return draws


def corner_contrasts(z: np.ndarray) -> np.ndarray:
    """Balanced 2×2×2 factorial contrasts (V,S,D), with ±1 signs.

    OS (S×D), OV (V×D), SV (V×S) average across the third axis;
    OSV is the S×D difference-in-differences at V=1 minus V=0.
    No division by source-value difference: positive scaling cannot change signs.
    """
    if z.ndim != 4 or z.shape[1:] != (2, 2, 2):
        raise ValueError("Require array shaped (proposal, vegetation, S, D), binary ordered")
    sd_by_v = z[:, :, 1, 1] - z[:, :, 1, 0] - z[:, :, 0, 1] + z[:, :, 0, 0]
    os = sd_by_v.mean(axis=1)
    ov = (z[:, 1, :, 1] - z[:, 1, :, 0] -
          z[:, 0, :, 1] + z[:, 0, :, 0]).mean(axis=1)
    sv = (z[:, 1, 1, :] - z[:, 1, 0, :] -
          z[:, 0, 1, :] + z[:, 0, 0, :]).mean(axis=1)
    osv = sd_by_v[:, 1] - sd_by_v[:, 0]
    return np.column_stack((os, ov, sv, osv))


def accepted_signs(contrasts: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    if eps < 0:
        raise ValueError("eps must not be negative")
    return ((contrasts[:, 0] < -eps) &
            (contrasts[:, 1] < -eps) &
            (contrasts[:, 2] > eps) &
            (contrasts[:, 3] > eps))


def run_subset(
    proposals: pd.DataFrame, models: pd.DataFrame,
    *, years: int = 40, window: int = 10, dt: float = 0.5,
    chunk: int = 64, eps: float = 1e-6,
) -> pd.DataFrame:
    if chunk < 1:
        raise ValueError("chunk must be positive")
    if proposals.empty:
        raise ValueError("No proposals in shard")
    m = models.set_index("model_id")
    all_results = []
    p = proposals.join(m, on="model_id", validate="many_to_one")
    if p.isna().any().any():
        raise AssertionError("Catalog joins contained missing values")
    # evaluate() supports mixed per-scenario rates but a *single* behavioral
    # response, litter mode and size_gate per batched call.
    for (behavior, litter, gate_code), g in p.groupby(
        ["behavior", "litter", "gate_code"], sort=True
    ):
        for offset in range(0, len(g), chunk):
            b = g.iloc[offset:offset + chunk].reset_index(drop=True)
            des = b.loc[b.index.repeat(8)].reset_index(drop=True).copy()
            c = np.tile(np.asarray(CORNERS), (len(b), 1))
            des["vegetation"], des["S_source"], des["D_source"] = c.T
            for key in CONTEXTS[0]:
                des[key] = np.repeat([CONTEXTS[i][key] for i in b.context_id], 8)
            des["block_id"] = np.repeat(b.context_id.to_numpy(), 8)
            kw = {k: des[k].to_numpy() for k in
                  ("attack", "rho", "conversion", "strength", "refuge_order")}
            simulated = evaluate(
                des, years=years, window=window, dt=dt,
                size_gate=None if gate_code == 0 else 0.5, **kw
            )
            fb = simulated.F_B.to_numpy(dtype=float).reshape(-1, 2, 2, 2)
            if not np.isfinite(fb).all() or (fb <= 0).any():
                raise AssertionError("F_B must be positive and finite before log")
            logc = corner_contrasts(np.log(fb))
            rawc = corner_contrasts(fb)
            record = b[["draw_id", "model_id", "context_id", "attack", "rho",
                        "conversion", "strength", "refuge_order", "gate_code",
                        "behavior", "litter", "edge_SD", "edge_DS", "cover_SF",
                        "cover_DF", "cover_DS", "cover_SD", "support_DF",
                        "support_DS", "survival", "timing", "reverse"]].copy()
            for i, name in enumerate(("OS", "OV", "SV", "OSV")):
                record["log_" + name] = logc[:, i]
                record["raw_" + name] = rawc[:, i]
            record["mean_F_B"] = fb.mean(axis=(1, 2, 3))
            record["mean_log_F_B"] = np.log(fb).mean(axis=(1, 2, 3))
            record["accepted"] = accepted_signs(logc, eps)
            record["raw_accepted"] = accepted_signs(rawc, eps)
            record["min_F"] = simulated.minimum_F_survival.to_numpy().reshape(-1, 8).min(axis=1)
            record["min_S"] = simulated.minimum_S_survival.to_numpy().reshape(-1, 8).min(axis=1)
            record["floor_ok"] = (record.min_F >= 0.05) & (record.min_S >= 0.05)
            all_results.append(record)
    combined = pd.concat(all_results, ignore_index=True).sort_values("draw_id")
    if not combined.draw_id.is_unique or len(combined) != len(proposals):
        raise AssertionError("Lost or duplicated proposals")
    return combined.reset_index(drop=True)


def wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / denom
    rad = z / denom * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (float(max(0, mid - rad)), float(min(1, mid + rad)))


def summarize(frame: pd.DataFrame, *, n: int, out: Path) -> dict:
    if len(frame) != n or set(frame.draw_id.astype(int)) != set(range(n)):
        raise AssertionError("Expected all exact draw IDs; missing/duplicate shard?")
    accepted = frame.accepted.astype(bool)
    k = int(accepted.sum())
    rows = []
    for axis in AXES:
        for level, g in frame.groupby(axis, dropna=False):
            successes = int(g.accepted.sum())
            count = len(g)
            lo, hi = wilson(successes, count)
            prior_share = count / n
            posterior_share = successes / k if k else float("nan")
            rows.append(dict(
                axis=axis, level=str(level), n=count, accepted=successes,
                prior_share=prior_share, accept_rate=successes/count,
                rate_ci_low=lo, rate_ci_high=hi,
                accepted_share=posterior_share,
                enrichment=posterior_share / prior_share if k else float("nan"),
            ))
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "axis_acceptance.csv", index=False)
    tm = frame.groupby("model_id").agg(
        proposed=("draw_id", "size"), accepted=("accepted", "sum")
    ).sort_values(["accepted", "proposed"], ascending=False)
    tm.to_csv(out / "model_acceptance.csv")
    sampled_ci = wilson(k, n)
    summary = {
        "status": "model_native_abc_pom_not_empirical_posterior",
        "base_main_sha": SOURCE_SHA,
        "model_space": 3600,
        "contexts": len(CONTEXTS),
        "n_proposed": n,
        "n_accepted_log": k,
        "acceptance_rate_log": k / n,
        "acceptance_rate_wilson95": list(sampled_ci),
        "n_accepted_raw": int(frame.raw_accepted.sum()),
        "n_accepted_log_and_floor5pct": int((accepted & frame.floor_ok).sum()),
        "distinct_models_proposed": int(frame.model_id.nunique()),
        "distinct_models_accepted": int(frame.loc[accepted, "model_id"].nunique()),
        "n_models_zero": int((tm.accepted == 0).sum()),
        "positive_summary": "Four signs are a synthetic *conditional compatibility criterion*; no field posterior or identified cause.",
        "priors": {
            "catalog": "uniform over the exact main 3,600 model IDs",
            "context": "uniform over the three frozen main stage-duration designs",
            "attack": [0.5, 1.5, 3.0],
            "rho": [0.25, 0.5, 0.75],
            "conversion": [2.0, 4.0, 8.0],
            "strength": [0.5, 1.0],
            "refuge_order": ["S", "equal", "D"],
            "size_gate": [None, 0.5],
        },
        "target": "log(F_B) factorial OS<0, OV<0, SV>0, OSV>0",
        "seed": SEED,
        "caveats": [
            "All draws are deterministic and conditional on uncalibrated priors.",
            "2x2x2 contrasts are balanced over the third axis, unlike the original 18-cell rank slope criterion.",
            "The 3,600 models are unequally representative of ecological functions.",
            "No observed NAAMP site counts or acoustic-to-larval mapping is fitted.",
            "Wilson intervals cover simulation draw variability, not uncertainty in empirical ecological processes.",
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    frame.loc[accepted].to_csv(out / "accepted_draws.csv.gz", index=False, compression="gzip")
    print("ABC_POM_FINAL_SUMMARY " + json.dumps({
        k: summary[k] for k in (
            "n_proposed", "n_accepted_log", "acceptance_rate_log",
            "n_accepted_raw", "n_accepted_log_and_floor5pct",
            "distinct_models_proposed", "distinct_models_accepted",
        )
    }), flush=True)
    print("ABC_POM_STAGE\n" + pd.DataFrame(rows).query("axis=='context_id'").to_string(index=False), flush=True)
    print("ABC_POM_TROPHIC_EDGE\n" + pd.DataFrame(rows).query("axis in ['edge_SD','edge_DS']").to_string(index=False), flush=True)
    return summary


def cli():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--draws", type=int, default=20000)
    arg.add_argument("--seed", type=int, default=SEED)
    arg.add_argument("--shards", type=int, default=1)
    arg.add_argument("--shard", type=int, default=0)
    arg.add_argument("--chunk", type=int, default=64)
    arg.add_argument("--years", type=int, default=40)
    arg.add_argument("--window", type=int, default=10)
    arg.add_argument("--dt", type=float, default=0.5)
    arg.add_argument("--epsilon", type=float, default=1e-6)
    arg.add_argument("--out", type=Path, default=DEST)
    arg.add_argument("--summarize-only", action="store_true")
    a = arg.parse_args()
    if a.shards < 1 or not 0 <= a.shard < a.shards:
        arg.error("Invalid shard index")
    a.out.mkdir(parents=True, exist_ok=True)
    if a.summarize_only:
        paths = sorted(a.out.glob("shard_*.csv.gz"))
        if len(paths) != a.shards:
            raise AssertionError("Expected " + str(a.shards) + " shard files, got " + str(len(paths)))
        frame = pd.concat((pd.read_csv(p) for p in paths), ignore_index=True)
        summarize(frame, n=a.draws, out=a.out)
    else:
        models = catalog()
        p = draw_prior(a.draws, a.seed, models)
        p = p[p.draw_id % a.shards == a.shard].copy()
        result = run_subset(
            p, models, years=a.years, window=a.window,
            dt=a.dt, chunk=a.chunk, eps=a.epsilon,
        )
        file = a.out / ("shard_%02d.csv.gz" % a.shard)
        result.to_csv(file, index=False, compression="gzip")
        print("ABC_POM_SHARD " + json.dumps({
            "shard": a.shard, "shards": a.shards,
            "n": len(result), "accepted": int(result.accepted.sum()),
            "raw_accepted": int(result.raw_accepted.sum()), "path": str(file)
        }), flush=True)
        if a.shards == 1:
            summarize(result, n=a.draws, out=a.out)


if __name__ == "__main__":
    cli()
