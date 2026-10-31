"""Conservative annual spatial extension of the *existing* 120-day + 80-y frogcs model.

Reuses stage_network_extension_20261029.simulate, the exact PR146 seasonal
hazard kernel and demographic rates. Only moves annual carryover and/or
matured local recruitment between synthetic ring patches. This is NOT the
PR147 seven-stage individual ABM, its rates, or its extinction estimand.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from stage_network_extension_20261029 import simulate as seasonal_kernel
from multiyear_stage_network import DEMOGRAPHY
from model_native_2x2x2_prior import (
    DESIGN, ROOT, TARGET, YEARS, WINDOW, DT, cube_design, model_names,
    matching_prior_draws, summarize_cube_output,
)
from model_native_vegetation_abc import (
    annual_recurrence_plant, cross_plant_design, legal_plant_inventory,
)

OUT = ROOT / "research/results/common_kernel_spatial_cohort_20261031"
MODES = ("off", "recruits", "carryover", "both")
PILOT_ROLES = ("SF1_DF0_DS0_L1", "SF0_DF0_DS1_L0", "SF1_DF0_DS1_L0")
PATCHES = 8
SOURCE_DRAW_IDS = (0, 4, 8, 12)
REPLAY_TOLERANCES = {"F_B": 1e-8, "F_fraction": 1e-8, "F_B_sd": 1e-7}


def ring_mix(cohorts, transfer):
    """Annual conservative symmetric nearest-neighbour transfer, [scenario,patch,guild].

    transfer is a per-annual-transition *fraction*, NOT a diffusion
    coefficient comparable to the PR147 model-year individual jump rate.
    """
    x = np.asarray(cohorts, dtype=float)
    mu = np.asarray(transfer, dtype=float)
    if x.ndim != 3 or x.shape[1] < 2 or x.shape[2] != 3:
        raise ValueError("Expected [scenario, >=2 patches, F/S/D] cohorts")
    if mu.shape != (3,) or not np.isfinite(mu).all() or (mu < 0).any() or (mu > 1).any():
        raise ValueError("Three finite guild-specific annual fractions in [0,1] required")
    if not np.isfinite(x).all() or (x < 0).any():
        raise ValueError("Nonnegative finite cohort densities required")
    mixed = (1 - mu) * x + .5 * mu * (np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1))
    if (mixed < -1e-12).any() or not np.allclose(
        mixed.sum(axis=1), x.sum(axis=1), rtol=1e-12, atol=1e-11
    ):
        raise AssertionError("Annual movement changed global cohort mass")
    return mixed


def synthetic_vegetation(vertices, patch_ids, landscape):
    """Homogeneous V=0/1 exactly reproduces PR146; mosaic 0/.4 or .6/1."""
    base = np.asarray(vertices, dtype=float)
    patch = np.asarray(patch_ids, dtype=int)
    if base.shape != patch.shape or not np.isin(base, [0, 1]).all():
        raise ValueError("Original binary plant vertices and matching patch IDs required")
    if landscape == "homogeneous":
        return base.copy()
    if landscape != "mosaic":
        raise ValueError("Unknown synthetic landscape")
    vals = .2 + .6 * base + np.where(patch % 2 == 0, -.2, .2)
    if ((vals < -1e-12) | (vals > 1+1e-12)).any():
        raise AssertionError("Unbounded synthetic vegetation")
    return np.clip(vals, 0, 1)


def spatial_annual_recurrence(cube, *, mode="off", transfer=.15,
                              landscape="mosaic", patches=PATCHES,
                              years=YEARS, window=WINDOW, dt=DT):
    """Exactly source-derived season and maturation; novel annual movement only.

    'recruits' moves the due-based post-maturation local contribution, while
    'carryover' moves survival * B. Neither label is a measured larval or
    adult migrant; PR147 stage-specific dispersal must remain a separate test.
    Annual nonzero background immigration in the SOURCE equations is retained.
    Accordingly zero-based extinction/recolonization cannot be inferred here.
    """
    if mode not in MODES or patches < 2 or not 1 <= window <= years:
        raise ValueError("Invalid annual movement design")
    if not np.isfinite(transfer) or not 0 <= transfer <= 1:
        raise ValueError("Invalid annual transfer fraction")
    if cube.empty or cube.duplicated(["structure_id", "draw", "reverse_on", "vertex"]).any():
        raise ValueError("Nonempty unique PR146 source cube required")
    outputs = []
    for (risk, litter), g in cube.groupby(["risk", "litter"], sort=True):
        g = g.reset_index(drop=True)
        n = len(g)
        # Entire original 2x2x2 model is replicated at each patch; only
        # vegetation and annual cohort transport are spatially extended.
        q = g.loc[g.index.repeat(patches)].reset_index(drop=True)
        patch_ids = np.tile(np.arange(patches), n)
        veg = synthetic_vegetation(q.vegetation.to_numpy(float), patch_ids, landscape)
        N = len(q)
        params = [
            dict(community="FSD", roles=15, refuge_order="D",
                 vegetation=float(veg[i]), f_arrival=20.,
                 s_arrival=float(r.sa), d_arrival=float(r.da),
                 attack_scale=float(r.attack_scale), cue=0.,
                 reverse=bool(r.reverse_on))
            for i, r in enumerate(q.itertuples(index=False))
        ]
        opts = dict(
            stage_durations=np.column_stack([
                np.full(N, 45.), np.full(N, 80.), q.dduration.to_numpy(float)
            ]),
            functional_response="litter" if bool(litter) else None,
            behavioral_refuge=bool(risk),
            handling_s=q.hs.to_numpy(float), handling_d=q.hd.to_numpy(float),
            s_growth=q.sg.to_numpy(float), d_growth=q.dg.to_numpy(float),
            sd_size_mode="dynamic",
            pathway_controls=dict(
                cover_SF=q.cover_SF.to_numpy(float),
                cover_DF=q.cover_DF.to_numpy(float),
                cover_DS=q.cover_DS.to_numpy(float), cover_SD=np.zeros(N),
                support_DF=np.zeros(N), support_DS=np.zeros(N),
                emerge_survival=np.zeros(N), emerge_exposure=np.zeros(N),
                cue_SD=np.zeros(N), edge_SD=np.ones(N), edge_DS=np.ones(N),
            )
        )
        source = np.column_stack([
            np.ones(N), q.S_source.to_numpy(float), q.D_source.to_numpy(float)
        ])
        rho = q.rho.to_numpy(float)[:, None]
        survival = np.column_stack([
            q.f_adult_survival.to_numpy(float), np.full(N, .5), np.zeros(N)
        ])
        conversion = np.broadcast_to(q.conversion.to_numpy(float)[:, None], (N, 3)).copy()
        juvenile = np.column_stack([
            q.f_juvenile_survival.to_numpy(float), np.full(N, .8), np.full(N, .8)
        ])
        delays = np.column_stack([
            q.f_delay.to_numpy(int), np.full(N, 2, int), np.ones(N, int)
        ])
        if not np.isin(delays[:, 0], [2, 3]).all():
            raise AssertionError("Source model F maturation-delay range changed")
        K = float(DEMOGRAPHY["capacity"])
        immigrant = (1 - rho) * (1 - survival) * source
        B = np.ones_like(source) * float(DEMOGRAPHY["initial_scale"])
        upper = np.maximum(B, (rho * conversion * K + immigrant) / (1 - survival))
        previous1, previous2 = np.zeros_like(B), np.zeros_like(B)
        F_patch_sum = np.zeros((n, patches))
        F_mean_sum = np.zeros(n)
        F_mean_sq_sum = np.zeros(n)
        fraction_sum = np.zeros(n)

        for year in range(years):
            season = seasonal_kernel(params, dt=dt, initial_cohorts=B, **opts)
            C = season[["F_completed", "S_completed", "D_completed"]].to_numpy(float)
            if not np.isfinite(C).all() or (C < 0).any():
                raise AssertionError("Seasonal completion invalid")
            due = np.empty_like(C)
            due[:, 0] = np.where(delays[:, 0] == 2, previous1[:, 0], previous2[:, 0])
            due[:, 1] = previous1[:, 1]
            due[:, 2] = C[:, 2]
            local = rho * conversion * juvenile ** (delays - 1) * due / (1 + due / K)
            carry = survival * B
            mu = np.full(3, float(transfer))
            if mode in ("recruits", "both"):
                local = ring_mix(local.reshape(n, patches, 3), mu).reshape(N, 3)
            if mode in ("carryover", "both"):
                carry = ring_mix(carry.reshape(n, patches, 3), mu).reshape(N, 3)
            next_B = carry + local + immigrant
            if (not np.isfinite(next_B).all() or (next_B < 0).any()
                    or (next_B > upper + 1e-9).any()):
                raise AssertionError("Annual mass/nonnegativity/source upper bound violated")
            if year >= years - window:
                f = B[:, 0].reshape(n, patches)
                avg = f.mean(axis=1)
                F_patch_sum += f
                F_mean_sum += avg
                F_mean_sq_sum += avg ** 2
                frac = np.divide(
                    C[:, 0], B[:, 0],
                    out=np.ones(N, dtype=float), where=B[:, 0] > 0
                ).reshape(n, patches)
                fraction_sum += frac.mean(axis=1)
            previous2, previous1 = previous1, C
            B = next_B

        per_patch = F_patch_sum / window
        F_B = F_mean_sum / window
        eff = np.divide(
            per_patch.sum(axis=1) ** 2, np.square(per_patch).sum(axis=1),
            out=np.zeros(n), where=np.square(per_patch).sum(axis=1) > 0
        )
        if np.any(eff > patches + 1e-8) or np.any(eff < 1 - 1e-8):
            raise AssertionError("Invalid spatial effective-patch index")
        result = g[[
            "structure_id", "context", "family", "risk", "original_case",
            "reverse_on", "draw", "vertex", "vegetation", "S_source", "D_source"
        ]].copy()
        result["F_B"] = F_B
        result["F_fraction"] = fraction_sum / window
        result["F_B_sd"] = np.sqrt(np.maximum(0, F_mean_sq_sum / window - F_B ** 2))
        result["effective_patches_F"] = eff
        result["F_patch_cv"] = (
            per_patch.std(axis=1) /
            np.maximum(per_patch.mean(axis=1), 1e-12)
        )
        result["min_patch_F_B"] = per_patch.min(axis=1)
        result["max_patch_F_B"] = per_patch.max(axis=1)
        if not np.isfinite(result.select_dtypes(include=[np.number])).all().all():
            raise AssertionError("Nonfinite spatial model output")
        outputs.append(result)
    result = pd.concat(outputs, ignore_index=True)
    if len(result) != len(cube):
        raise AssertionError("Source model factorial vertices lost")
    return result


def pilot_cube(draws=1):
    """Predefined first parent rate IDs; no outcome-dependent hypothesis filtering."""
    if not 1 <= draws <= len(SOURCE_DRAW_IDS):
        raise ValueError("Pilot uses 1..4 prespecified parent256 draw IDs")
    design = model_names(pd.read_csv(DESIGN))
    selected = design[
        design.context.isin((
            "original", "D_first_S_overtakes", "S_first_D_overtakes"
        )) & design.family.eq("baseline") & design.risk.eq(False)
    ].copy()
    if len(selected) != 3:
        raise AssertionError("Expected 3 source ontogenies with baseline handling, risk OFF")
    parent = matching_prior_draws(256)
    rates = parent[parent.draw.isin(SOURCE_DRAW_IDS[:draws])].copy()
    if list(rates.draw) != list(SOURCE_DRAW_IDS[:draws]):
        raise AssertionError("Fixed original prior ID subset lost")
    base = cube_design(selected, rates)
    plants = legal_plant_inventory()
    plants = plants[plants.plant_model.isin(PILOT_ROLES)].copy()
    cube = cross_plant_design(base, plants)
    if len(cube) != 3 * draws * 2 * 8 * len(PILOT_ROLES):
        raise AssertionError("Incomplete 3 ontogenies × plant × rates × edge × 8 vertices")
    return cube


def replay_gate(cube, *, years=YEARS, window=WINDOW, dt=DT, patches=PATCHES):
    """Hard gate: no annual movement on homogeneous patches exactly replays PR146."""
    baseline = annual_recurrence_plant(cube, years=years, window=window, dt=dt)
    spatial = spatial_annual_recurrence(
        cube, mode="off", landscape="homogeneous", patches=patches,
        years=years, window=window, dt=dt
    )
    keys = ["structure_id", "draw", "reverse_on", "vertex"]
    a = baseline.sort_values(keys).reset_index(drop=True)
    b = spatial.sort_values(keys).reset_index(drop=True)
    if len(a) != len(b) or not a[keys].equals(b[keys]):
        raise AssertionError("Source replay design IDs differ")
    differences = {}
    for name, tol in REPLAY_TOLERANCES.items():
        err = float(np.max(np.abs(a[name].to_numpy(float) - b[name].to_numpy(float))))
        differences[name] = err
        if err > tol:
            raise AssertionError("PR146 source-model replay failed " + name + ": " + str(err))
    if not np.allclose(b.effective_patches_F, patches, atol=1e-8, rtol=0):
        raise AssertionError("Homogeneous source is not spatially homogeneous")
    return differences


def run(*, draws=1, years=YEARS, window=WINDOW, transfer=.15, dt=DT):
    cube = pilot_cube(draws)
    original_replay = replay_gate(cube, years=years, window=window, dt=dt)
    records, signs = [], []
    for mode in MODES:
        current = spatial_annual_recurrence(
            cube, mode=mode, transfer=transfer, landscape="mosaic",
            years=years, window=window, dt=dt
        )
        current["movement"] = mode
        records.append(current)
        score = summarize_cube_output(current)
        score["movement"] = mode
        signs.append(score)
    outcomes = pd.concat(records, ignore_index=True)
    scores = pd.concat(signs, ignore_index=True)
    keys = ["structure_id", "draw", "reverse_on", "vertex"]
    baseline = outcomes[outcomes.movement.eq("off")].set_index(keys)
    paired = []
    for mode in MODES[1:]:
        cur = outcomes[outcomes.movement.eq(mode)].set_index(keys)
        if not cur.index.is_unique or not cur.index.equals(baseline.index):
            raise AssertionError("Movement/source scenario ID pairing invalid")
        d = (cur[["F_B", "effective_patches_F", "F_patch_cv"]] -
             baseline[["F_B", "effective_patches_F", "F_patch_cv"]])
        d = d.add_prefix("delta_").reset_index()
        d["movement"] = mode
        paired.append(d)
    comparison = pd.concat(paired, ignore_index=True)
    summary = (scores.groupby(["movement", "context"])
               .agg(n_source_cases=("matches_log", "size"),
                    four_sign_matches=("matches_log", "sum"),
                    four_sign_matches_raw=("matches_raw", "sum"))
               .reset_index())
    summary["match_fraction"] = summary.four_sign_matches / summary.n_source_cases
    OUT.mkdir(parents=True, exist_ok=True)
    outcomes.to_csv(OUT / "model_native_spatial_vertices.csv.gz", index=False,
                    compression={"method": "gzip", "mtime": 0})
    scores.to_csv(OUT / "model_native_four_sign_patterns.csv", index=False)
    comparison.to_csv(OUT / "paired_annual_movement_effects.csv", index=False)
    summary.to_csv(OUT / "summary_by_ontogeny_and_movement.csv", index=False)
    receipt = dict(
        status="SYNTHETIC_SPATIAL_ANNUAL_COHORT_PILOT_NOT_FIELD_ESTIMATE",
        original_pr146_homogeneous_off_replay=original_replay,
        years=years, window=window, draws=draws, draw_ids=list(SOURCE_DRAW_IDS[:draws]),
        patches=PATCHES, vegetation_mosaic="V0:[0,0.4];V1:[0.6,1]",
        annual_transfer_fraction=transfer, movement_modes=MODES,
        n_80_year_pr146_cube_cases=int(len(cube)),
        n_spatial_source_vertices=int(len(outcomes)),
        n_2x2x2_sign_evaluations=int(len(scores)),
        n_movement_paired_vertex_differences=int(len(comparison)),
        annual_immigration_from_source_retained=True,
        actual_local_extinction_and_recolonization_estimable=False,
        seven_stage_pr147_abm_rate_calibration=False,
        stochastic_individual_demography=False,
        field_mechanism_posterior=False,
        source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (OUT / "receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2), flush=True)
    print(summary.to_string(index=False), flush=True)
    return outcomes, scores, comparison, receipt


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    p.add_argument("--draws", type=int, default=1)
    p.add_argument("--years", type=int, default=YEARS)
    p.add_argument("--window", type=int, default=WINDOW)
    p.add_argument("--transfer", type=float, default=.15)
    p.add_argument("--dt", type=float, default=DT)
    a = p.parse_args()
    if not a.run:
        p.error("Explicit --run required")
    run(draws=a.draws, years=a.years, window=a.window,
        transfer=a.transfer, dt=a.dt)
