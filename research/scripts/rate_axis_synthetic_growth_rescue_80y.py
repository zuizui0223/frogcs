"""Source-locked *one-axis-at-a-time* biological-rate swaps (ID0 <-> ID12).

Why: original frogcs four-rate stress found a S-growth-dependent reversal
of 80-year F occupancy response to annual dispersal under illustrative
process-rate ID0 but NOT ID12. Which of the eight original LHS dimensions
can change this outcome when exchanged one at a time, in each direction?

All stage/plant/seasonal trophic source equations unchanged. This tests
conditional single-axis sufficiency/necessity ONLY, not interaction
identification, a field posterior, or a proof of causal biological mechanism.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from spatial_cohort_80y_bridge import ROOT, pilot_cube, replay_gate
from isolate_S_growth_D_duration_finite80y import source_factorial
from finite_n_source_cohort_bridge import (
    simulate_finite_group, summarize_finite_group, GUILDS
)

OUT = ROOT / "research/results/growth_rescue_rate_axis_swaps_20261031"
AXES = (
    "attack_scale",
    "s_growth_multiplier",
    "d_growth_multiplier",
    "rho",
    "conversion",
    "f_juvenile_survival",
    "f_adult_survival",
    "f_delay",
)
DIMENSIONS = {
    "attack_scale":"attack_scale",
    "s_growth_multiplier":"sg",
    "d_growth_multiplier":"dg",
    "rho":"rho",
    "conversion":"conversion",
    "f_juvenile_survival":"f_juvenile_survival",
    "f_adult_survival":"f_adult_survival",
    "f_delay":"f_delay",
}
PHYSICS = ("sa", "da", "sg", "dg", "dduration", "hs", "hd",
           "attack_scale", "rho", "conversion", "f_delay",
           "f_adult_survival", "f_juvenile_survival")
CONTEXTS = ("original","S_growth_fast_only",
            "D_aquatic_long_only","D_first_S_overtakes")
PLANTS = ("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
BASES = (0,12)
SEEDS = (101,102,103,104)
YEARS = 80
TRANSFER = .15
SCALE = 3


def original_rate_factorial(rate_id):
    """All 4 biological factor cells use the original, frozen parent256 rate vector."""
    if rate_id not in BASES:
        raise ValueError("Only fixed source endpoints ID0 and ID12 allowed")
    all_cube = pilot_cube(4)
    subset = all_cube[
        all_cube.draw.eq(rate_id) &
        all_cube.context.isin(("original","D_first_S_overtakes")) &
        all_cube.plant_model.isin(PLANTS) &
        all_cube.risk.eq(False)
    ].copy()
    if len(subset) != 64:
        raise AssertionError("Original full 2x2x2 endpoint source missing")
    hybrids,original,joint = source_factorial(subset)
    out = pd.concat([original,hybrids,joint],ignore_index=True)
    out = out.sort_values(
        ["context","plant_model","reverse_on","vertex"]
    ).reset_index(drop=True)
    if (len(out)!=128 or
        out.duplicated(["structure_id","draw","reverse_on","vertex"]).any() or
        set(out.context)!=set(CONTEXTS) or
        not out.draw.eq(rate_id).all()):
        raise AssertionError("Original fixed source endpoint factorial corrupted")
    return out


def paired_rate_endpoints():
    low=original_rate_factorial(0)
    high=original_rate_factorial(12)
    keys=["context","plant_model","reverse_on","vertex"]
    if not low[keys].equals(high[keys]):
        raise AssertionError("Rate endpoints do not share identical biological treatments")
    if not np.array_equal(low.f_delay.to_numpy(int),low.f_delay.to_numpy(int)):
        raise AssertionError("Ill-defined maturation lag")
    # The frozen source context variables and plant role choices cannot
    # differ between the endpoint base and donor.
    nuisance=["vegetation","S_source","D_source","sa","da","dduration",
              "hs","hd","cover_SF","cover_DF","cover_DS","litter"]
    for name in nuisance:
        if not np.allclose(low[name],high[name],rtol=0,atol=1e-12):
            raise AssertionError("Rate source does not match on fixed non-rate axis: "+name)
    return low,high


def swap_fixed_rate_axis(base_id,axis):
    if base_id not in BASES or axis not in AXES:
        raise ValueError("Only predeclared rate endpoint and one original LHS axis allowed")
    low,high = paired_rate_endpoints()
    base,donor = (low,high) if base_id==0 else (high,low)
    out=base.copy()
    col=DIMENSIONS[axis]
    out[col]=donor[col].to_numpy(copy=True)
    # All original rate-vector dimensions except the swapped one must
    # remain precisely equal to the base; the selected one equals donor.
    for name in PHYSICS:
        reference=(donor if name==col else base)
        if not np.allclose(out[name].to_numpy(float),
                           reference[name].to_numpy(float),
                           rtol=0,atol=1e-12):
            raise AssertionError("Original biological rate swap changed another axis "+name)
    unchanged_cols=["community","plant_model","vertex","vegetation",
                    "S_source","D_source","reverse_on","risk","litter",
                    "cover_SF","cover_DF","cover_DS","family","context",
                    "structure_id"]
    for name in unchanged_cols:
        if name in out and not out[name].equals(base[name]):
            raise AssertionError("Rate manipulation changed source treatment "+name)
    if out.draw.nunique()!=1 or int(out.draw.iloc[0])!=base_id:
        raise AssertionError("One-axis rate source was mislabeled")
    return out


def verify_complete_swap_positive_control():
    """Replacing ALL eight columns would exactly reproduce the other source."""
    low, high=paired_rate_endpoints()
    for base,donor in ((low,high),(high,low)):
        g=base.copy()
        for name in AXES:
            col=DIMENSIONS[name]
            g[col]=donor[col].to_numpy(copy=True)
        for name in PHYSICS:
            if not np.allclose(g[name].to_numpy(float),
                               donor[name].to_numpy(float),rtol=0,atol=1e-12):
                raise AssertionError("Original donor mechanism mismatch after all-rate swap")
    return True


def simulate_axis(base_id,axis,*,years=YEARS,seeds=SEEDS,transfer=TRANSFER):
    if (years!=YEARS or tuple(seeds)!=SEEDS or
        not np.isclose(transfer,TRANSFER)):
        raise ValueError("Use only the prespecified 80year 4seed first-pass source design")
    source=swap_fixed_rate_axis(base_id,axis)
    if not verify_complete_swap_positive_control():
        raise AssertionError("Donor endpoint reconstruction failed")
    replay=replay_gate(source,years=YEARS,window=20,dt=.25)
    if (replay["F_B"]>1e-8 or replay["F_fraction"]>1e-8 or
        replay["F_B_sd"]>1e-7):
        raise AssertionError("Actual 80year 120-day source kernel replay not exact")

    raw=[]; event_frames=[]
    for seed in seeds:
        for mode in ("off","both"):
            for (_risk,litter),group in source.groupby(["risk","litter"],sort=True):
                group=group.reset_index(drop=True)
                run=simulate_finite_group(
                    group,scale=SCALE,seed=int(seed),mode=mode,
                    immigration=False,years=YEARS,dt=.25,
                    transfer=transfer
                )
                summary,events=summarize_finite_group(
                    group,run,scale=SCALE,seed=int(seed),
                    mode=mode,immigration=False,years=YEARS
                )
                raw.append(summary)
                if len(events):event_frames.append(events)
        print("RATE_AXIS_TRUE_80Y_SEED_COMPLETED",base_id,axis,seed,flush=True)

    frame=pd.concat(raw,ignore_index=True)
    events=(pd.concat(event_frames,ignore_index=True) if event_frames else
            pd.DataFrame(columns=["seed","guild","structure_id"]))
    key=["structure_id","draw","reverse_on","vertex","seed","movement","guild"]
    if (len(frame)!=128*len(seeds)*2*len(GUILDS) or
        frame.duplicated(key).any() or
        len(events)!=int(frame.n_local_returns.sum()) or
        set(frame.context)!=set(CONTEXTS) or
        set(frame.movement)!={"off","both"} or
        set(frame.plant_model)!=set(PLANTS) or
        set(frame.seed)!=set(seeds) or
        not frame.draw.eq(base_id).all() or
        not frame.immigration.eq(0).all() or
        not frame.scale.eq(SCALE).all()):
        raise AssertionError("Real finite source/seed/return identity failed")
    if int(frame.n_recorded_migration_arrivals.sum())!=int(
        frame.n_recorded_migration_departures.sum()):
        raise AssertionError("True stochastic ring movement lost cohort mass")
    off=frame[frame.movement.eq("off")].set_index(
        ["structure_id","reverse_on","vertex","seed","guild"]
    ).sort_index()
    both=frame[frame.movement.eq("both")].set_index(
        ["structure_id","reverse_on","vertex","seed","guild"]
    ).sort_index()
    if not off.index.equals(both.index):
        raise AssertionError("Unpaired fixed-source movement control")
    fields=["final_occupied_patches","n_local_returns","n_local_extinctions"]
    delta=(both[fields]-off[fields]).add_prefix("delta_").reset_index()
    delta["context"]=delta.structure_id.str.split("__").str[0]
    delta["plant_model"]=delta.structure_id.str.split("__").str[-1]
    delta["base_rate_id"]=base_id
    delta["swapped_from_rate_id"]=12 if base_id==0 else 0
    delta["swapped_axis"]=axis
    if len(delta)!=128*4*3:
        raise AssertionError("Missing source native 2x2x2 vertex comparisons")

    OUT.mkdir(parents=True,exist_ok=True)
    frame.to_csv(OUT/"axis_original_seed_guilds.csv.gz",index=False,
       compression={"method":"gzip","mtime":0})
    events.to_csv(OUT/"axis_true_return_events.csv.gz",index=False,
       compression={"method":"gzip","mtime":0})
    delta.to_csv(OUT/"axis_movement_off_paired_deltas.csv",index=False)
    summary=(delta[delta.guild.eq("F")]
             .groupby(["base_rate_id","swapped_axis","plant_model","context"],sort=True)
             .agg(n_fixed_vertex_seed_cases=("seed","size"),
                  delta_occupied_mean=("delta_final_occupied_patches","mean"),
                  delta_returns_mean=("delta_n_local_returns","mean"))
             .reset_index())
    summary.to_csv(OUT/"axis_F_context_mean.csv",index=False)
    receipt=dict(status="ORIGINAL_80Y_PROCESS_RATE_SINGLE_AXIS_SWAP_TRUE_SOURCE",
        base_rate_id=base_id,donor_rate_id=(12 if base_id==0 else 0),
        changed_original_LHS_axis=axis,original_true_fouryear_source=False,
        exact_original_seasonal_kernel_replay=replay,years=YEARS,
        random_seed_labels=list(seeds),biological_rate_fixed_components=7,
        one_exchanged_original_rate_component=1,
        source_hypotheses=128,matched_source_scenario_guild_rows=int(len(delta)),
        true_N0_to_Npositive_events=int(len(events)),
        no_external_immigration=True,scale=SCALE,movement_fraction=transfer,
        no_plant_role_ontogeny_or_predator_edge_change=True,
        absolute_field_rates_calibrated=False,
        exact_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("RATE_AXIS_SHARD_SUCCESS",json.dumps(receipt),flush=True)
    print("RATE_AXIS_F_CONTEXT\n"+summary.to_string(index=False),flush=True)
    return delta,summary,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--base-rate-id",type=int,choices=BASES,required=True)
    p.add_argument("--axis",choices=AXES,required=True)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    simulate_axis(args.base_rate_id,args.axis)
