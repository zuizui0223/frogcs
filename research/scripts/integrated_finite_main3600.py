"""80-year finite-N posterior predictions using the *unmodified main* seasonal kernel.

ABCPOM selection is NEVER based on stochastic signs. The exact original main
stage_vegetation_network.simulate + final_network_summary annual expectation
are reused. Finite cohort conversion, annual integer noise and 8-ring
movement are clearly declared new counterfactual assumptions.

Eight patches are the 2×2×2 V/S/D vertices in lexical order, not observed sites.
This differs from the PR149 finite-N extension's **different** seasonal
stage_network_extension_20261029 kernel; do not concatenate its results.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from abc_pom_main3600 import CORNERS, catalog
from final_mechanism_common import CONTEXTS, evaluate
from final_network_summary import summarize_years
from integrated_80y_prepare import HERE
from multiyear_stage_network import DEMOGRAPHY
from stage_vegetation_network import DEFAULT, simulate

PATCHES = 8
YEARS = 80
WINDOW = 20
DT = .5
TRANSFER = .15
QS = (3, 12)
EDGE_SF = (0, 1)
MOVE = (0, 1)
SEEDS = (101, 102)  # Independent synthetic process replicates; expand after smoke.
ARMS = list(product(QS, EDGE_SF, MOVE, SEEDS))


def sample_ring_transfer(x: np.ndarray, frac: float, rng):
    """Integer-conserving annual left-right dispersal over eight patch vertices."""
    if x.ndim != 3 or x.shape[1:] != (PATCHES, 3) or (x < 0).any():
        raise ValueError("Require nonnegative arm-by-eight-by-three integer cohorts")
    if not np.issubdtype(x.dtype, np.integer) or not 0 <= frac <= 1:
        raise ValueError("Invalid integer cohorts or transport probability")
    left = rng.binomial(x, frac / 2)
    right = rng.binomial(x-left, frac / (2-frac))
    incoming = np.roll(left, -1, axis=1) + np.roll(right, 1, axis=1)
    outgoing = left + right
    result = x - outgoing + incoming
    if not np.array_equal(result.sum(axis=1), x.sum(axis=1)):
        raise AssertionError("Nonconservative integer dispersal")
    return result, incoming, outgoing


def arms_for_selected(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    models = catalog().set_index("model_id")
    for item in selected.sort_values("draw_id").itertuples(index=False):
        feature = models.loc[int(item.model_id)].to_dict()
        for q, edge, move, seed in ARMS:
            rows.append({
                **feature, "draw_id": int(item.draw_id),
                "model_id": int(item.model_id),
                "context_id": int(item.context_id),
                "attack": float(item.attack),
                "rho": float(item.rho),
                "conversion": float(item.conversion),
                "strength": float(item.strength),
                "refuge_order": str(item.refuge_order),
                "gate_code": int(item.gate_code),
                "q": int(q), "edge_SF_on": int(edge),
                "move_on": int(move), "seed": int(seed),
                "sample_weight": float(item.sample_weight),
            })
    return pd.DataFrame(rows)


def make_main_design(arms: pd.DataFrame):
    """Exact input construction used by main final_mechanism_common.evaluate()."""
    if arms.empty:
        raise ValueError("No population arms")
    arms = arms.reset_index(drop=True)
    des = arms.loc[arms.index.repeat(PATCHES)].reset_index(drop=True).copy()
    vertices = np.tile(np.asarray(CORNERS, dtype=float), (len(arms), 1))
    des["vegetation"], des["S_source"], des["D_source"] = vertices.T
    for key in CONTEXTS[0]:
        des[key] = np.repeat([CONTEXTS[i][key] for i in arms.context_id], PATCHES)
    des["attack_scale"] = des.attack.to_numpy(float)
    des["roles"] = 15
    des["cue"] = np.where(des.behavior == "cue_SF", 3., 0.)
    des["community"] = "FSD"
    options = dict(
        stage_durations=des[["F_duration", "S_duration", "D_duration"]].to_numpy(float),
        emergence_delay=(5 * des.vegetation * des.timing).to_numpy(float),
        size_gate=None if arms.gate_code.iloc[0] == 0 else 0.5,
        functional_response="litter" if arms.litter.iloc[0] else None,
        behavioral_refuge=arms.behavior.iloc[0] == "risk_refuge",
    )
    controls = {key: (des[key] * des.strength).to_numpy(float)
                for key in ["cover_SF", "cover_DF", "cover_DS", "cover_SD",
                            "support_DF", "support_DS"]}
    controls.update(
        edge_SD=des.edge_SD.to_numpy(float),
        edge_DS=des.edge_DS.to_numpy(float),
        edge_SF=des.edge_SF_on.to_numpy(float),
        cue_SD=0.,
        emerge_survival=(des.survival * des.strength).to_numpy(float),
        emerge_exposure=0.,
    )
    options["pathway_controls"] = controls
    kernel = des[[k for k in DEFAULT if k in des]].to_dict("records")
    source = np.column_stack((
        np.ones(len(des)), des.S_source.to_numpy(float),
        des.D_source.to_numpy(float),
    )).reshape(len(arms), PATCHES, 3)
    rho = des.rho.to_numpy(float).reshape(len(arms), PATCHES, 1)
    conversion = np.repeat(des.conversion.to_numpy(float)[:, None], 3, axis=1)
    return kernel, options, source, rho, conversion, des


def source_replay_gate(arm: pd.DataFrame) -> float:
    """Compare our handoff against main.evaluate on true zero-movement means."""
    if len(arm) != 1 or arm.edge_SF_on.iloc[0] != 1:
        raise ValueError("Replay one main-standard predation-enabled arm")
    ker, options, source, rho, conversion, des = make_main_design(arm)
    s = summarize_years(
        [{**k, "rho": float(r)} for k, r in zip(ker, rho[:,0,0].repeat(PATCHES))],
        years=4, window=2, dt=1., source_cohorts=source.reshape(-1,3),
        seasonal_options=options, conversion=conversion
    )
    orig = evaluate(
        des, years=4, window=2, dt=1.,
        attack=des.attack.to_numpy(float),
        strength=des.strength.to_numpy(float),
        rho=des.rho.to_numpy(float),
        conversion=des.conversion.to_numpy(float),
        refuge_order=des.refuge_order.to_numpy(),
        size_gate=options["size_gate"],
    )
    err = max(np.max(np.abs(s[col].to_numpy() - orig[col].to_numpy()))
              for col in ("F_B", "F_fraction", "S_B", "D_B"))
    if err > 1e-11:
        raise AssertionError(f"Main seasonal/annual expected-value source drift: {err}")
    return float(err)


def run_finite_batch(arms: pd.DataFrame, *, years=YEARS, dt=DT,
                     transfer=TRANSFER):
    """Vectorize q/edge/migration/seed arms under one main model family.

    Each source draw has 16 crossed arms. Ring mixing is symmetric and mass
    conserving; no site-geometry inference is claimed.
    """
    if (arms.behavior.nunique(), arms.litter.nunique(),
        arms.gate_code.nunique()) != (1, 1, 1):
        raise ValueError("Group homogeneous behavioural/litter/gate mode first")
    if len(arms) == 0 or years < WINDOW or dt <= 0:
        raise ValueError("Invalid finite-N batch configuration")
    kernel, options, source, rho, conv, _ = make_main_design(arms)
    n = len(arms)
    scale = arms.q.to_numpy(dtype=int).reshape(n,1,1)
    movement = arms.move_on.to_numpy(dtype=bool).reshape(n,1,1)
    if not np.isin(scale, QS).all():
        raise ValueError("Undeclared scale")
    survival = np.asarray(DEMOGRAPHY["survival"], float)
    juvenile = np.asarray(DEMOGRAPHY["juvenile"], float)
    delay = np.asarray(DEMOGRAPHY["delays"], int)
    K = float(DEMOGRAPHY["capacity"])
    # Original main initial densities equal one per present guild.
    N = np.broadcast_to(scale, (n,PATCHES,3)).copy()
    prev_complete = np.zeros_like(N)
    total_recolonizations = np.zeros(n, dtype=int)
    total_local_extinctions = np.zeros(n, dtype=int)
    movement_assisted_returns = np.zeros(n, dtype=int)
    mean_occupied_20 = np.zeros(n)
    mean_F_total_20 = np.zeros(n)
    a_key = (f"INTEGRATED_MAIN3600_{int(arms.gate_code.iloc[0])}_"
             f"{arms.behavior.iloc[0]}_{int(arms.litter.iloc[0])}")
    rng_seed = int.from_bytes(hashlib.blake2b(a_key.encode(),digest_size=8).digest(),"big")
    rng = np.random.default_rng(rng_seed)
    for yr in range(years):
        result = simulate(
            kernel, dt=dt,
            initial_cohorts=(N / scale).reshape(n*PATCHES,3),
            **options
        )
        finished = result[["F_completed", "S_completed", "D_completed"]].to_numpy(float)
        finished = finished.reshape(n,PATCHES,3)
        current_density = N / scale
        if ((finished < -1e-9).any() or
            (finished > current_density + 1e-9).any() or
            not np.isfinite(finished).all()):
            raise AssertionError("Seasonal cohort closure broken")
        completion_p = np.divide(
            finished, current_density,
            out=np.zeros_like(finished), where=(N > 0)
        )
        completed = rng.binomial(N, np.clip(completion_p,0,1))
        due = np.empty_like(N)
        # Original main delay 2,2,1: current S/D completion, and F/S from
        # prior year for the two guilds with delay two.
        due[:,:,0] = prev_complete[:,:,0]
        due[:,:,1] = prev_complete[:,:,1]
        due[:,:,2] = completed[:,:,2]
        carry = rng.binomial(N, survival)
        local_density = (
            rho * conv.reshape(n,PATCHES,3) *
            juvenile**(delay-1) * (due / scale) /
            (1 + (due / scale) / K)
        )
        ext_density = (1-rho)*(1-survival)*source
        recruits = rng.poisson(scale*local_density)
        external = rng.poisson(scale*ext_density)
        moved_carry, incoming_c, _ = sample_ring_transfer(carry, transfer, rng)
        moved_recruits, incoming_r, _ = sample_ring_transfer(recruits, transfer, rng)
        N_next = (
            np.where(movement, moved_carry, carry) +
            np.where(movement, moved_recruits, recruits) + external
        )
        if not np.array_equal(N_next.sum(axis=1),
                              (carry+recruits+external).sum(axis=1)):
            raise AssertionError("Movement cannot create/destroy individuals")
        was = N[:,:,0] > 0
        now = N_next[:,:,0] > 0
        total_recolonizations += ((~was) & now).sum(axis=1)
        total_local_extinctions += (was & (~now)).sum(axis=1)
        incoming_f = (incoming_c + incoming_r)[:,:,0]
        movement_assisted_returns += (
            ((~was) & now & (incoming_f>0) & movement[:,:,0])
        ).sum(axis=1)
        if yr >= years-WINDOW:
            mean_occupied_20 += now.sum(axis=1) / WINDOW
            mean_F_total_20 += N_next[:,:,0].sum(axis=1) / WINDOW
        N = N_next
        prev_complete = completed
    out = arms[["draw_id", "model_id", "context_id", "q", "edge_SF_on",
                "move_on", "seed", "sample_weight", "cover_SF",
                "cover_DS", "edge_SD", "edge_DS", "support_DF",
                "litter", "behavior"]].copy()
    out["occupied_year80"] = (N[:,:,0] > 0).sum(axis=1)
    out["occupied_mean_year61_80"] = mean_occupied_20
    out["mean_F_count_year61_80"] = mean_F_total_20
    out["recolonization_events_80y"] = total_recolonizations
    out["local_extinction_events_80y"] = total_local_extinctions
    out["movement_assisted_returns_80y"] = movement_assisted_returns
    out["all8_occupied_year80"] = (out.occupied_year80 == PATCHES)
    out["zero8_occupied_year80"] = (out.occupied_year80 == 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=HERE/"selected_draws.csv")
    ap.add_argument("--out", type=Path, default=HERE)
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--years", type=int, default=YEARS)
    ap.add_argument("--dt", type=float, default=DT)
    args = ap.parse_args()
    if args.shards < 1 or not 0 <= args.shard < args.shards:
        ap.error("Invalid shard")
    selected = pd.read_csv(args.source)
    selected = selected[selected.draw_id.astype(int) % args.shards == args.shard]
    if selected.empty:
        raise AssertionError("Empty posterior shard")
    arms = arms_for_selected(selected)
    outputs = []
    for (_, _, _), g in arms.groupby(["behavior", "litter", "gate_code"],sort=True):
        # Critical same-kernel source replay for one unablated / undeviated arm.
        baseline = g[(g.edge_SF_on == 1) & (g.move_on == 0)].iloc[:1]
        source_replay_gate(baseline)
        outputs.append(run_finite_batch(g, years=args.years,dt=args.dt))
    result = pd.concat(outputs,ignore_index=True).sort_values(
        ["draw_id","q","edge_SF_on","move_on","seed"]
    )
    expected = len(selected) * len(ARMS)
    if len(result) != expected or result.duplicated(
        ["draw_id","q","edge_SF_on","move_on","seed"]
    ).any():
        raise AssertionError("Not all prospective 80y prediction arms ran")
    args.out.mkdir(parents=True,exist_ok=True)
    path = args.out / f"finite_predictions_shard_{args.shard:02d}.csv.gz"
    result.to_csv(path,index=False,compression="gzip")
    print("INTEGRATED_FINITE_MAIN3600 " + json.dumps({
        "shard":args.shard, "source_draws":len(selected),
        "arms":expected, "mean_occupancy":float(result.occupied_year80.mean()),
        "zero_events":int(result.recolonization_events_80y.sum()),
        "movement_assisted_events":int(result.movement_assisted_returns_80y.sum()),
    }),flush=True)


if __name__ == "__main__":
    main()
