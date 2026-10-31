"""Factorial isolate S growth vs D aquatic duration in the frogcs 80-year finite-N bridge.

CRITICAL CORRECTION: original and D_first_S_overtakes BOTH have
S arrival day20 and D arrival day0. Their prior contrast jointly changes
S aquatic growth (.014 -> .03) and D aquatic duration (40 -> 60 days).
This source-locked 2x2 ablation computes ONLY the two previously absent
mixed settings; original and both-changed source are reused from true
independent 12-seed PR149 results, never simulated again for inference.

Not a species arrival-order experiment, not field-calibrated demography.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from finite_n_source_cohort_bridge import (
    ROOT, PATCHES, simulate_finite_group, summarize_finite_group,
    source_cube, GUILDS
)
from spatial_cohort_80y_bridge import replay_gate

OUT=ROOT/"research/results/growth_duration_isolation_20261031"
NEW_CONTEXTS=("S_growth_fast_only","D_aquatic_long_only")
OLD_CONTEXTS=("original","D_first_S_overtakes")
PLANT_ROLES=("SF1_DF0_DS0_L1","SF0_DF0_DS1_L0")
SEED_LABELS=tuple(range(101,113))
DEFAULT_YEARS=80
DEFAULT_SCALE=3
DEFAULT_MOVE=.15
REPLAY_GATES=dict(F_B=1e-8,F_fraction=1e-8,F_B_sd=1e-7)


def _ordered(source):
    keys=["plant_model","reverse_on","vertex","draw"]
    if source.duplicated(keys).any():
        raise AssertionError("Conflicting factorial source IDs")
    return source.sort_values(keys).reset_index(drop=True)


def source_factorial(input_source_cube=None):
    """Verify original source for ONE fixed rate draw, then build missing factor cells."""
    all_orig=(source_cube(1) if input_source_cube is None
              else input_source_cube.copy())
    original=_ordered(all_orig[all_orig.context.eq("original")])
    dfirst=_ordered(all_orig[all_orig.context.eq("D_first_S_overtakes")])
    if len(original)!=32 or len(dfirst)!=32:
        raise AssertionError("Expected exact two-plant × reversal × eight-corner reference")
    keys=["plant_model","reverse_on","vertex","draw"]
    if not original[keys].equals(dfirst[keys]):
        raise AssertionError("Cannot align source factor arms by plant/reversal/corner")
    # Compare every other attribute: this is not an isolated arrival effect.
    allowed_different={"context","structure_id","original_case","sg","dduration"}
    for col in original.columns:
        if col in allowed_different:
            continue
        a,b=original[col],dfirst[col]
        if pd.api.types.is_numeric_dtype(a):
            if not np.allclose(a.to_numpy(float),b.to_numpy(float),rtol=1e-13,atol=1e-13):
                raise AssertionError(f"Unexpected additional source difference: {col}")
        elif not a.equals(b):
            raise AssertionError(f"Unexpected nonnumeric source difference: {col}")
    for src in (original,dfirst):
        if (not np.allclose(src.sa,20) or not np.allclose(src.da,0) or
            not np.allclose(src.dg,dfirst.dg)):
            raise AssertionError("Source arrival or D growth changed unexpectedly")
    if (not np.allclose(original.dduration,40) or
        not np.allclose(dfirst.dduration,60) or
        not np.allclose(dfirst.sg/original.sg, 0.030/0.014,rtol=1e-11,atol=1e-11)):
        raise AssertionError("Fixed stage-size and D persistence contrast changed")

    hybrids=[]
    for context in NEW_CONTEXTS:
        g=original.copy()
        if context=="S_growth_fast_only":
            g["sg"]=dfirst.sg.to_numpy(float)
        elif context=="D_aquatic_long_only":
            g["dduration"]=dfirst.dduration.to_numpy(float)
        g["context"]=context
        g["structure_id"]=g["structure_id"].str.replace(
            r"^original__",context+"__",regex=True
        )
        g["original_case"]=-1  # New combos are not part of main's frozen 132 cases
        if g.structure_id.str.startswith("original__").any():
            raise AssertionError("Hybrid source IDs were not relabeled")
        hybrids.append(g)
    cross=pd.concat(hybrids,ignore_index=True)
    if (len(cross)!=64 or cross.duplicated(
        ["structure_id","draw","reverse_on","vertex"]).any()):
        raise AssertionError("Incomplete 2×2 source-factorial missing-cell comparisons")
    # Source kernels must be biologically equal on the joint-change corner.
    reconstructed=original.copy()
    reconstructed["sg"]=dfirst.sg.to_numpy(float)
    reconstructed["dduration"]=dfirst.dduration.to_numpy(float)
    for col in ("sa","da","sg","dg","dduration","hs","hd",
                "attack_scale","rho","conversion","f_delay",
                "f_adult_survival","f_juvenile_survival"):
        if not np.allclose(reconstructed[col],dfirst[col],rtol=0,atol=1e-14):
            raise AssertionError("The old D_first contrast changed another biological input")
    return cross,original,dfirst


def run(*,seed_start=101,seeds=4,years=DEFAULT_YEARS,scale=DEFAULT_SCALE,
        transfer=DEFAULT_MOVE,source_validation=True):
    if (seed_start not in SEED_LABELS or seeds<1 or
        seed_start+seeds-1>SEED_LABELS[-1] or
        years<4 or not isinstance(scale,int) or scale<1 or
        not np.isfinite(transfer) or not 0<=transfer<=1):
        raise ValueError("Predeclared source seed, duration or finite population scale invalid")
    cross,orig,dfirst=source_factorial()
    if source_validation:
        replay=replay_gate(cross,years=years,window=min(20,years),dt=.25)
        for k,lim in REPLAY_GATES.items():
            if replay[k]>lim:
                raise AssertionError("New hybrid source replay failed "+k)
    else:
        replay=None
    records,returns=[],[]
    for seed in range(seed_start,seed_start+seeds):
        for movement in ("off","both"):
            # Match previous PR149's per-(risk,litter) grouping and seed rule,
            # not pseudo-independent RNG per cube vertex or patch.
            for (_risk,litter),g in cross.groupby(["risk","litter"],sort=True):
                g=g.reset_index(drop=True)
                o=simulate_finite_group(
                    g,scale=scale,seed=seed,mode=movement,
                    immigration=False,years=years,dt=.25,transfer=transfer
                )
                a,b=summarize_finite_group(
                    g,o,scale=scale,seed=seed,mode=movement,
                    immigration=False,years=years
                )
                records.append(a)
                if len(b):returns.append(b)
        print("TRUE_80Y_HYBRID_SOURCE_SEED_COMPLETED",seed,flush=True)
    result=pd.concat(records,ignore_index=True)
    events=(pd.concat(returns,ignore_index=True) if returns else
            pd.DataFrame(columns=["structure_id","seed","guild"]))
    keys=["structure_id","draw","reverse_on","vertex","scale",
          "seed","movement","immigration","guild"]
    expected=len(cross)*seeds*2*len(GUILDS)
    if (len(result)!=expected or
        result.duplicated(keys).any() or
        len(events)!=int(result.n_local_returns.sum())):
        raise AssertionError("Source seeds/conditions and all return events incomplete")
    if (set(result.context)!=set(NEW_CONTEXTS) or
        set(result.plant_model)!=set(PLANT_ROLES) or
        set(result.movement)!={"off","both"} or
        not result.immigration.eq(0).all() or
        not result.scale.eq(scale).all()):
        raise AssertionError("Hybrid source biological treatment was not held fixed")
    if (result.n_external_immigrants.to_numpy(int)!=0).any():
        raise AssertionError("External arrival occurred in a closed source model")
    if int(result.n_recorded_migration_arrivals.sum())!=int(
        result.n_recorded_migration_departures.sum()):
        raise AssertionError("Spatial mass conservation failed")

    OUT.mkdir(parents=True,exist_ok=True)
    result.to_csv(OUT/"hybrid_seed_scenario_guild_summary.csv.gz",
                  index=False,compression={"method":"gzip","mtime":0})
    events.to_csv(OUT/"hybrid_reoccupation_followup_events.csv.gz",
                  index=False,compression={"method":"gzip","mtime":0})
    paired=pair_difference(result)
    paired.to_csv(OUT/"hybrid_same_source_seed_movement_effects.csv",index=False)
    receipt={
        "status":"TRUE_SOURCE_80Y_STAGE_GROWTH_VS_D_DURATION_FACTORIAL_HYBRIDS",
        "biological_source_changed":False,
        "source_arrival_days":{"D":0,"S":20},
        "original_D_aquatic_days":40,
        "old_joint_D_aquatic_days":60,
        "S_growth_rate_change_base_to_fast": [0.014,0.030],
        "new_missing_cells":list(NEW_CONTEXTS),
        "replay":replay,
        "source_n_factorial_model_corners":int(len(cross)),
        "total_seed_scenario_guild_results":int(len(result)),
        "events":int(len(events)),
        "seed_labels":list(range(seed_start,seed_start+seeds)),
        "scale":scale,"movement_fraction":transfer,
        "external_immigration":False,"years":years,
        "only_off_and_both_movement":True,
        "baseline_and_joint_original_sources_reused_separately":True,
        "model_not_empirical_site_calibrated":True,
        "code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (OUT/"receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",
        encoding="utf-8"
    )
    print("FACTORIAL_SOURCE_RECEIPT "+json.dumps(receipt),flush=True)
    print("HYBRID_MOVEMENT_EFFECT_F\n"+paired[paired.guild.eq("F")]
          .groupby(["context","plant_model"])[
              ["delta_final_occupied_patches","delta_n_local_returns"]
          ].mean().to_string(),flush=True)
    return result,events,paired,receipt


def pair_difference(result):
    """Same seed/source cube identifiers; seed label does not imply pathwise RNG pairing."""
    keys=["structure_id","draw","reverse_on","vertex",
          "scale","seed","immigration","guild"]
    old=result[result.movement.eq("off")].set_index(keys).sort_index()
    moved=result[result.movement.eq("both")].set_index(keys).sort_index()
    if not old.index.equals(moved.index):
        raise AssertionError("Missing OFF vs both source cube pairs")
    fields=["final_occupied_patches","n_local_returns",
            "n_local_extinctions","n_3y_persistent_with_recruitment"]
    a=(moved[fields]-old[fields]).add_prefix("delta_").reset_index()
    a["context"]=a.structure_id.str.split("__").str[0]
    a["plant_model"]=a.structure_id.str.split("__").str[-1]
    return a


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--seed-start",type=int,default=101)
    p.add_argument("--seeds",type=int,default=4)
    p.add_argument("--years",type=int,default=DEFAULT_YEARS)
    p.add_argument("--scale",type=int,default=DEFAULT_SCALE)
    p.add_argument("--transfer",type=float,default=DEFAULT_MOVE)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(seed_start=args.seed_start,seeds=args.seeds,years=args.years,
        scale=args.scale,transfer=args.transfer)
