"""Test previously unobserved 3 synthetic biological process-rate draws for the
verified S-growth×D-aquatic-duration dispersal interaction.

Uses 3 prespecified IDs from the 256-draw LHS source inventory: 4,8,12,
with a complete controlled 2×2 factorial (4 contexts) and independent
per-draw 12 RNG seed labels. PR150 source draw0 is NOT rerun.

Original 120-day stage-specific seasonal hazard kernel unchanged;
finite-N recruitment is still a NEW uncalibrated stochastic assumption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from spatial_cohort_80y_bridge import pilot_cube, replay_gate, ROOT
from isolate_S_growth_D_duration_finite80y import (
    source_factorial, NEW_CONTEXTS
)
from finite_n_source_cohort_bridge import (
    simulate_finite_group,summarize_finite_group,GUILDS
)

OUT=ROOT/"research/results/growth_duration_rate_stress_20261031"
PRIOR_IDS=(4,8,12)
CONTEXTS=("original","S_growth_fast_only","D_aquatic_long_only",
          "D_first_S_overtakes")
SEED_RANGE=tuple(range(101,113))
SCALE=3
MOVE_FRACTION=.15


def biological_factorial(rate_id):
    if rate_id not in PRIOR_IDS:
        raise ValueError("Rate stress restricted to previously frozen process draw IDs 4/8/12")
    c=pilot_cube(4)
    c=c[c.draw.eq(rate_id)&
        c.context.isin(("original","D_first_S_overtakes"))&
        c.plant_model.isin(("SF1_DF0_DS0_L1","SF0_DF0_DS1_L0"))&
        c.risk.eq(False)].copy()
    if len(c)!=64:
        raise AssertionError("Incomplete original fixed rate draw×plant 2×2×2 source")
    missing,original,both=source_factorial(c)
    full=pd.concat([original,missing,both],ignore_index=True)
    full=full.sort_values(["context","plant_model","reverse_on","vertex"]).reset_index(drop=True)
    if (len(full)!=128 or
        full.duplicated(["structure_id","draw","reverse_on","vertex"]).any() or
        set(full.context)!=set(CONTEXTS) or
        not full.draw.eq(rate_id).all()):
        raise AssertionError("Missing source contrast or biological rate draw changed")
    return full


def execute(rate_id,seed_start,seeds=4,years=80):
    if (rate_id not in PRIOR_IDS or seed_start not in (101,105,109) or
        seeds!=4 or years!=80):
        raise ValueError("Only fully prespecified 12seed × 80year source shards are allowed")
    all_source=biological_factorial(rate_id)
    replay=replay_gate(all_source,years=80,window=20,dt=.25)
    for value,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        if replay[value]>tol:
            raise AssertionError("PR146 original demographic seasonal replay failed: "+value)

    datasets=[]
    eventsets=[]
    for seed in range(seed_start,seed_start+4):
        for mode in ("off","both"):
            for (_risk,litter),g in all_source.groupby(["risk","litter"],sort=True):
                g=g.reset_index(drop=True)
                x=simulate_finite_group(
                    g,scale=SCALE,seed=int(seed),mode=mode,
                    immigration=False,years=years,dt=.25,
                    transfer=MOVE_FRACTION
                )
                a,e=summarize_finite_group(
                    g,x,scale=SCALE,seed=int(seed),mode=mode,
                    immigration=False,years=years
                )
                datasets.append(a)
                if len(e):eventsets.append(e)
        print("ACTUAL_HYPOTHETICAL_PROCESS_DRAW",rate_id,
              "80YEAR_SEED_COMPLETED",seed,flush=True)
    s=pd.concat(datasets,ignore_index=True)
    events=(pd.concat(eventsets,ignore_index=True) if eventsets else
            pd.DataFrame(columns=["structure_id","draw","seed","guild"]))
    unique=["structure_id","draw","reverse_on","vertex",
            "scale","seed","movement","immigration","guild"]
    if (len(s)!=128*4*2*len(GUILDS) or
        s.duplicated(unique).any() or
        int(s.n_local_returns.sum())!=len(events) or
        set(s.context)!=set(CONTEXTS) or
        set(s.movement)!={"off","both"} or
        set(s.seed)!=set(range(seed_start,seed_start+4)) or
        not s.draw.eq(rate_id).all() or
        not s.immigration.eq(0).all()):
        raise AssertionError("True source rate stress outputs incomplete")
    if int(s.n_recorded_migration_arrivals.sum())!=int(
        s.n_recorded_migration_departures.sum()):
        raise AssertionError("Closed movement conservation violated")

    OUT.mkdir(parents=True,exist_ok=True)
    s.to_csv(OUT/"rate_seed_scenario_guild_summary.csv.gz",index=False,
             compression={"method":"gzip","mtime":0})
    events.to_csv(OUT/"rate_true_reoccupation_events.csv.gz",index=False,
                  compression={"method":"gzip","mtime":0})
    result=dict(
        status="TRUE_80Y_GROWTH_DURATION_FACTORIAL_BIOLOGICAL_PRIOR_STRESS",
        fixed_256_LHS_rate_draw_id=rate_id,
        n_source_eightcorner_model_units=128,
        n_seed_guild_records=len(s),
        n_true_zero_to_positive_events=len(events),
        independent_rng_seed_labels=list(range(seed_start,seed_start+4)),
        original_stage_arrival_days={"S":20,"D":0},
        original_rate_replay_errors=replay,
        population_scale=SCALE,external_immigration=False,
        movement_fraction=MOVE_FRACTION,model_horizon_years=years,
        no_source_biology_kernel_changes=True,
        uncalibrated_hypothetical_rate_prior=True,
        not_field_causal_inference=True,
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (OUT/"receipt.json").write_text(json.dumps(result,indent=2)+"\n")
    print("GROWTH_DURATION_RATE_SHARD_RECEIPT",json.dumps(result),flush=True)
    return s,events,result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--rate-draw",type=int,required=True,choices=PRIOR_IDS)
    p.add_argument("--seed-start",type=int,required=True,choices=(101,105,109))
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    execute(a.rate_draw,a.seed_start)
