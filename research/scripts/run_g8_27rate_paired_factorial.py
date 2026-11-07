"""G8 all-rate genuinely paired vegetation experiment, using the frozen original 80-year kernel.

Prospective G8 design: research/G8_27RATE_PAIRED_FACTORIAL_PROTOCOL_2026-11-07.md
No wild field likelihood, no selected-only source structures. Source code is unmodified.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confirmatory_2x2_vegetation_predator_switch import (
    ARMS, N_BASE, SOURCE_MAIN_SHA, VERTEX_DATA,
    original_draws, simulate_original_80y, check_source_replay,
)

ATTACK = (0.5, 1.5, 3.0)
RHO = (0.25, 0.5, 0.75)
CONVERSION = (2.0, 4.0, 8.0)
RATE_GRID = tuple(itertools.product(ATTACK, RHO, CONVERSION))
NSHARDS = 64
SOURCES_PER_SHARD = N_BASE // NSHARDS
EXPECTED_ROWS = N_BASE * len(RATE_GRID) * 3 * len(ARMS)
YEARS = 80
WINDOW = 20
DT = 0.5


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def make_grid(*, source_ids=None, rate_ids=None, contexts=None):
    """Retain all original backgrounds and all legal 2x2 arms; change rates only."""
    models, original, nuisance = original_draws()
    require(len(models) == 3600 and len(original) == N_BASE * 3 * 4,
            "Frozen PR161 source structural experiment missing")
    if source_ids is None:
        source_ids = tuple(range(N_BASE))
    if rate_ids is None:
        rate_ids = tuple(range(len(RATE_GRID)))
    if contexts is None:
        contexts = (0, 1, 2)
    source_ids, rate_ids, contexts = map(tuple, (source_ids, rate_ids, contexts))
    require(len(source_ids) == len(set(source_ids)) and all(0 <= s < N_BASE for s in source_ids),
            "Selected source IDs invalid/duplicated")
    require(len(rate_ids) == len(set(rate_ids)) and
            all(0 <= r < len(RATE_GRID) for r in rate_ids), "Rate IDs invalid/duplicated")
    require(len(contexts) == len(set(contexts)) and all(c in (0, 1, 2) for c in contexts),
            "Original context IDs invalid/duplicated")
    original = original[original.source_id.isin(source_ids) & original.context_id.isin(contexts)]
    require(len(original) == len(source_ids) * len(contexts) * len(ARMS),
            "Source / developmental context / legal arm lost")
    groups = []
    for rate_id in rate_ids:
        attack, rho, conversion = RATE_GRID[rate_id]
        q = original.copy()
        q["original_draw_id"] = q["draw_id"].astype(int)
        q["original_conversion"] = q["conversion"].astype(float)
        q["rate_id"] = int(rate_id)
        q["draw_id"] = q["original_draw_id"].astype(int) * len(RATE_GRID) + rate_id
        q["attack"] = float(attack)
        q["rho"] = float(rho)
        q["conversion"] = float(conversion)
        groups.append(q)
    p = pd.concat(groups, ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    require(p.draw_id.is_unique and len(p) ==
            len(source_ids) * len(contexts) * len(ARMS) * len(rate_ids),
            "Incomplete matched 27-rate design")
    for cols in (["source_id", "rate_id", "context_id"],
                 ["source_id", "rate_id", "arm"]):
        expected = len(ARMS) if cols[-1] == "context_id" else len(contexts)
        require(p.groupby(cols).size().eq(expected).all(), "Incomplete pairing by " + str(cols))
    require(p.groupby(["source_id", "rate_id", "context_id"]).arm.nunique().eq(4).all(),
            "Four plant counterfactuals not matched")
    require(p.groupby("source_id")[["strength", "refuge_order", "gate_code"]]
            .nunique().max().max() == 1, "Original nuisance changed across rate cells")
    require(p.groupby(["source_id", "rate_id"])[["attack", "rho", "conversion"]]
            .nunique().max().max() == 1, "Rate parameters differ within source cell")
    require(p.groupby(["source_id", "rate_id", "context_id"]).model_id.nunique().eq(4).all(),
            "Four legal original canonical model IDs not mapped")
    return models, p, nuisance


def v0_negative_control(vertices):
    """All states and hazards at V=0 must be arm-invariant under the original kernel."""
    cols = ["F_B", "S_B", "D_B", "F_fraction", "audit_H_SF",
            "audit_H_DF", "audit_H_DS", "audit_H_SD",
            "minimum_F_survival", "minimum_S_survival"]
    v0 = vertices.loc[vertices.vegetation.eq(0)].copy()
    require(len(v0) * 2 == len(vertices),
            "Expected equal V=0 and V=1 vertices")
    groups = v0.groupby(["source_id", "rate_id", "context_id", "vertex"], sort=False)
    require(groups.size().eq(4).all(), "Every V=0 corner must have all four arms")
    spread = groups[cols].max() - groups[cols].min()
    require(np.isfinite(spread.to_numpy(float)).all(), "Non-finite V=0 source corner")
    err = float(np.max(np.abs(spread.to_numpy(float))))
    require(err < 1e-10, f"V=0 plant arm changed original biological source: {err}")
    return err


def run(*, shard: int, out: Path, smoke: bool = False):
    require(0 <= shard < NSHARDS, "Unknown fixed shard ID")
    source_ids = tuple(range(shard * SOURCES_PER_SHARD, (shard + 1) * SOURCES_PER_SHARD))
    if smoke:
        source_ids, rate_ids, contexts = source_ids[:1], (0, 13), (0, 1)
        years, window = 4, 2
    else:
        rate_ids, contexts = tuple(range(27)), (0, 1, 2)
        years, window = YEARS, WINDOW
    models, design, _ = make_grid(source_ids=source_ids, rate_ids=rate_ids,
                                   contexts=contexts)
    effects, vertices = simulate_original_80y(design, models, years=years,
                                               window=window, dt=DT, chunk=24)
    m = design[["draw_id", "original_draw_id", "original_conversion", "rate_id"]]
    effects = effects.merge(m, on="draw_id", how="left", validate="one_to_one")
    vertices = vertices.merge(m, on="draw_id", how="left", validate="many_to_one")
    require(len(effects) == len(design) and len(vertices) == len(design) * 8,
            "Scenario/vertex accounting drift")
    require(effects.rate_id.notna().all() and
            vertices.rate_id.notna().all(), "Grid metadata lost")
    err = v0_negative_control(vertices)
    if smoke:
        check_source_replay(models, design, effects, years=4)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    marker = f"g8_{'smoke' if smoke else 'true80'}_{shard:02d}"
    ep = out / (marker + "_effects.csv.gz")
    vp = out / (marker + "_vertices.csv.gz")
    # Exact gzip bytes made stable across reruns.
    options = dict(index=False, compression={"method": "gzip", "mtime": 0})
    effects.sort_values("draw_id").to_csv(ep, **options)
    vertices.sort_values(["draw_id", "vertex"]).to_csv(vp, **options)
    receipt = dict(
        status="G8_FOUR_YEAR_METHOD_ONLY" if smoke else "G8_TRUE80_SOURCE_SHARD",
        source_main_sha=SOURCE_MAIN_SHA,
        source_background_seed=20261123,
        shard=shard, n_shards=NSHARDS, sources=list(source_ids),
        rate_ids=list(rate_ids), contexts=list(contexts),
        source_count=len(source_ids),
        n_rate_cells=len(rate_ids),
        canonical_catalog_models=3600,
        n_scenarios=len(effects), n_vertices=len(vertices),
        expected_full_scenarios=EXPECTED_ROWS,
        expected_full_vertices=EXPECTED_ROWS*8,
        years=years, window=window, dt=DT,
        negative_control_max_abs=err, replay_4y=smoke,
        files_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (ep, vp)},
        no_biological_rate_reselection=True,
        all_compatibility_outcomes_preserved=True,
        observed_predator_rates_or_larval_abundance=False,
    )
    (out / (marker + "_receipt.json")).write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("G8_SHARD_RECEIPT " + json.dumps(receipt), flush=True)
    return receipt


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--shard", type=int, required=True)
    cli.add_argument("--out", type=Path, required=True)
    cli.add_argument("--smoke", action="store_true")
    a = cli.parse_args()
    run(shard=a.shard, out=a.out, smoke=a.smoke)
