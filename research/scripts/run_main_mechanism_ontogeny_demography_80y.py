"""Original-source 80y finite-N bridge: main #1479/#1455 x ontogeny x vegetation.

Uses unchanged PR155 120-day trophic, maturation, sampling and patch processes.
This is *model-native* feasibility, not fitted NAAMP predation or field forecasts.
The main-catalog fingerprints are enforced; main's 40/80-season scoring and
this finite-N 80-year endpoint are intentionally distinct estimands.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from spatial_cohort_80y_bridge import pilot_cube, replay_gate
from model_native_vegetation_abc import legal_plant_inventory
from finite_n_source_cohort_bridge import simulate_finite_group, summarize_finite_group
from run_D_E_common_engine_nuisance_80y import score_model_native_four_signs

PAPER_ROOT = Path(__file__).resolve().parents[2]
CATALOG = PAPER_ROOT / "research/results/final_mechanism_20261027/catalog.csv"
SOURCE_COMMIT = "19d45ffb833e2970aff8d88de101736aee289d26"
BASE_ROLE = "SF1_DF0_DS0_L1"
ROLES = (
    "SF1_DF0_DS0_L1",  # main #1479/#1455 vegetation features
    "SF1_DF0_DS0_L0",  # switch litter OFF
    "SF0_DF0_DS0_L1",  # switch frog shelter OFF
    "SF0_DF0_DS0_L0",  # no vegetation trophic function
    "SF0_DF0_DS1_L0",  # shelter S from D only
    "SF1_DF0_DS1_L0",  # both shelters, litter OFF
)
STAGES = ("original", "D_first_S_overtakes", "S_first_D_overtakes")
NETWORKS = {"main1479": {}, "main1455": {"edge_off": "SD"}}
MODES = ("off", "both")
QS = (3, 12)
SEED_STARTS = (101, 103)
DRAWS = (0, 4, 8, 12)
EXPECTED_FLAGS = {
    1479: (1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, "none", 1),
    1455: (1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, "none", 1),
}
FLAG_COLUMNS = (
    "cover_SF", "cover_DF", "cover_DS", "cover_SD", "survival", "timing",
    "support_DF", "support_DS", "edge_SD", "edge_DS", "reverse", "behavior", "litter",
)
SOURCE_RESPONSE = (
    "mean_cohort_B_last_window", "final_occupied_patches",
    "n_local_returns", "n_local_extinctions",
)


def verify_original_main_catalog():
    """Refuse to call a changed combination main #1479/#1455."""
    if not CATALOG.exists():
        raise AssertionError("The original main catalog is not present in the paper checkout")
    c = pd.read_csv(CATALOG).set_index("model_id")
    if len(c) != 3600:
        raise AssertionError("Original 3600-candidate catalog changed")
    for model, expected in EXPECTED_FLAGS.items():
        actual = tuple(c.loc[model, list(FLAG_COLUMNS)].tolist())
        if actual != expected:
            raise AssertionError(f"main model {model} flag fingerprint changed: {actual}")
    return hashlib.sha256(CATALOG.read_bytes()).hexdigest()


def source_cube():
    """Unselected four original LHS rate IDs and all three real stage contexts."""
    base = pilot_cube(4)
    base = base.loc[
        base.plant_model.eq(BASE_ROLE)
        & base.risk.eq(False)
        & base.reverse_on.eq(0)
    ].copy().reset_index(drop=True)
    if (len(base) != 3 * 4 * 8 or set(base.context) != set(STAGES)
            or set(base.draw) != set(DRAWS)
            or base.duplicated(["context", "draw", "vertex"]).any()):
        raise AssertionError("Unmodified 80y source cube is incomplete")
    plants = legal_plant_inventory().set_index("plant_model")
    if not set(ROLES).issubset(plants.index):
        raise AssertionError("Plant interventions not in main's legal model space")
    return base, plants


def controlled_plant(group, role, plants):
    """Keep the original source identity/seed key; intervene only on plant flags.

    Source RNG keys contain plant_model but not the plant flags; holding the
    original plant_model source key constant gives shared label-based RNG
    streams for ON/OFF comparisons. Changed populations still make downstream
    RNG draws diverge: NOT identical common-random-number trajectories.
    """
    g = group.copy()
    for name in ("cover_SF", "cover_DF", "cover_DS", "litter"):
        g[name] = int(plants.loc[role, name])
    if not g.plant_model.eq(BASE_ROLE).all():
        raise AssertionError("Anchor RNG source grouping changed")
    return g


def source_group_to_scores(g, *, stage, role, net, q, mode, seed, years):
    kwargs = NETWORKS[net]
    result = simulate_finite_group(
        g, scale=q, seed=seed, mode=mode, immigration=False,
        years=years, dt=.25, transfer=.15, **kwargs
    )
    summary, events = summarize_finite_group(
        g, result, scale=q, seed=seed, mode=mode,
        immigration=False, years=years
    )
    if (len(summary) != len(g) * 3 or len(events) !=
            int(summary.n_local_returns.sum()) or
            summary.n_external_immigrants.ne(0).any() or
            int(summary.n_recorded_migration_arrivals.sum()) !=
            int(summary.n_recorded_migration_departures.sum())):
        raise AssertionError("Real individual-count/return/mass ledger incorrect")
    summary = summary.copy()
    summary["network"] = net
    summary["main_id"] = 1479 if net == "main1479" else 1455
    summary["plant_role"] = role
    # Separate analytical IDs without changing the original biological source
    # IDs passed into simulate_finite_group.
    summary["structure_id"] = summary["structure_id"].astype(str) + "__" + role
    summary["plant_model"] = role
    frog = summary[summary.guild.eq("F")].copy()
    if (len(frog) != len(DRAWS) * 8 or
            frog.duplicated(["draw", "vertex"]).any() or
            not set(frog.vertex) == set(range(8))):
        raise AssertionError("Frog F/S/D × vegetation source cube incomplete")
    if years == 80:
        scores = score_model_native_four_signs(frog)
        scores["main_id"] = 1479 if net == "main1479" else 1455
        scores["plant_role"] = role
        extra = []
        for draw, part in frog.groupby("draw", sort=True):
            part = part.sort_values("vertex")
            # Original cube uses binary synthetic V vertex, although the
            # eight spatial patches use vegetation mosaics 0/.4 and .6/1.
            if len(part) != 8 or set(part.vertex) != set(range(8)):
                raise AssertionError("Cannot split original 8 vertices by V")
            extra.append(dict(
                structure_id=part.structure_id.iloc[0], draw=int(draw),
                f_v0_occupied=float(part[part.vertex < 4].final_occupied_patches.mean()),
                f_v1_occupied=float(part[part.vertex >= 4].final_occupied_patches.mean()),
                f_v0_returns=float(part[part.vertex < 4].n_local_returns.mean()),
                f_v1_returns=float(part[part.vertex >= 4].n_local_returns.mean()),
                f_year80_occ_mean=float(part.final_occupied_patches.mean()),
                f_reoccupation_mean=float(part.n_local_returns.mean()),
                f_extinction_mean=float(part.n_local_extinctions.mean()),
                f_source_vertices_zero=int((part.mean_cohort_B_last_window == 0).sum()),
            ))
        scores = scores.merge(pd.DataFrame(extra),
                              on=["structure_id", "draw"], validate="one_to_one")
        if len(scores) != len(DRAWS):
            raise AssertionError("Source summary missing one biological theta")
    else:
        scores = pd.DataFrame()
    return frog, scores, dict(
        stage=stage, role=role, main_id=int(summary.main_id.iloc[0]),
        q=q, mode=mode, seed=seed, original_biological_rate_ids=list(DRAWS),
        frog_source_vertices=len(frog), guild_source_vertices=len(summary),
        genuine_0_to_positive_frog_events=int(frog.n_local_returns.sum()),
        genuine_0_to_positive_all_guild_events=len(events),
        total_external_immigrants=int(summary.n_external_immigrants.sum()),
    )


def run_shard(*, stage, q, seed_start, out, years=80):
    if (stage not in STAGES or q not in QS or seed_start not in SEED_STARTS
            or years not in (4, 80)):
        raise ValueError("Only the frozen biological design is permitted")
    fingerprint = verify_original_main_catalog()
    base, plants = source_cube()
    original = base[base.context.eq(stage)].copy().reset_index(drop=True)
    if len(original) != len(DRAWS) * 8:
        raise AssertionError("Stage subset is not original 4draw × 8vertex")
    # Exact unchanged deterministic seasonal + 4y maturation comparison.
    replay = replay_gate(original, years=4, window=2, dt=.25)
    if max(replay.values()) > 1e-7:
        raise AssertionError("Original source seasonal/annual replay failed")
    frog_parts, scores_parts, receipts = [], [], []
    for seed in range(seed_start, seed_start+2):
        for role in ROLES:
            g = controlled_plant(original, role, plants)
            for net in NETWORKS:
                for mode in MODES:
                    f, sc, receipt = source_group_to_scores(
                        g, stage=stage, role=role, net=net, q=q,
                        mode=mode, seed=seed, years=years
                    )
                    frog_parts.append(f)
                    if len(sc):
                        scores_parts.append(sc)
                    receipts.append(receipt)
        print("MAIN_ANCHOR_TRUE_SOURCE_STAGE_SEED_DONE", stage, q, seed, years, flush=True)
    frogs = pd.concat(frog_parts, ignore_index=True)
    scores = (pd.concat(scores_parts, ignore_index=True)
              if scores_parts else pd.DataFrame())
    key = ["context", "plant_role", "network", "draw", "vertex",
           "scale", "seed", "movement"]
    expected_sims = 2 * len(ROLES) * len(NETWORKS) * len(MODES) * len(DRAWS) * 8
    if len(frogs) != expected_sims or frogs.duplicated(key).any():
        raise AssertionError("A source 2×2×2 original stage×role×edge cell is missing")
    if years == 80:
        skey = key[:4] + key[5:]
        if len(scores) != expected_sims // 8 or scores.duplicated(skey).any():
            raise AssertionError("Full genuine 80y four-sign/occupancy summaries missing")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    comp = {"method": "gzip", "mtime": 0}
    frogs.to_csv(out / "original_80y_frog_vertex_demography.csv.gz",
                 index=False, compression=comp)
    if years == 80:
        scores.to_csv(out / "same_model_four_sign_and_occupancy.csv", index=False)
    pd.DataFrame(receipts).to_csv(out / "source_group_accounting.csv", index=False)
    receipt = dict(
        status=("GENUINE_80YEAR_MODEL_NATIVE" if years == 80
                else "FOURYEAR_METHOD_SMOKE_ONLY"),
        original_main_catalog_sha256=fingerprint,
        biological_source_commit=SOURCE_COMMIT,
        stage=stage, q=q, seed_labels=[seed_start, seed_start+1],
        years=years, source_rate_draw_ids=list(DRAWS),
        model_catalog_ids=[1479,1455], plant_role_ids=list(ROLES),
        movement_modes=list(MODES), n_frog_vertex_rows=int(len(frogs)),
        n_four_sign_and_occupancy=int(len(scores)),
        n_0_to_positive_frog_patch_events=int(frogs.n_local_returns.sum()),
        original_4y_same_kernel_replay_errors=replay,
        synthetic_vegetation_patch_design="V0:0/.4,V1:.6/1",
        synthetic_annual_movement_fraction=.15, external_immigration=False,
        independent_rate_draws=4, independent_stochastic_seeds=2,
        posterior_over_field_trophic_process=False,
        observational_calling_bridge_calibrated=False,
        source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (out / "receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8"
    )
    print("MAIN_ONTOGENY_DEMOGRAPHY_SOURCE_RECEIPT", json.dumps(receipt), flush=True)
    return frogs, scores, receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    p.add_argument("--stage", choices=STAGES, required=True)
    p.add_argument("--q", type=int, choices=QS, required=True)
    p.add_argument("--seed-start", type=int, choices=SEED_STARTS, required=True)
    p.add_argument("--years", type=int, choices=(4,80), default=80)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if not a.run:
        p.error("Explicit --run required")
    run_shard(stage=a.stage, q=a.q, seed_start=a.seed_start,
              years=a.years, out=a.out)
