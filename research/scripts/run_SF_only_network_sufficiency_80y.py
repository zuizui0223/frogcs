"""Test whether S-larva -> F-larva direct predation by itself is sufficient
for recruitment-dependent dispersal-effect reversal in the *source-locked*
80y frogcs finite-N model. A no-active-direct-predator control is included.

Original 120-day seasonal trophic hazard, 80y recruitment/lag, rates,
plant roles, stochastic finite count and landscape all unchanged.
Extra 12 NEW genuine 80y jobs only for SF_only and no_predators,
two original local-recruitment contexts, 12 seed labels. Original intact
and sole-SF-removed baselines reused from PR153, not fitted/recomputed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_predator_edge_recruitment_80y import (
    ROOT,REGIMES,source_by_recruitment_regime,
    assert_recruitment_axis_only_changed
)
from finite_n_source_cohort_bridge import (
    simulate_finite_group,summarize_finite_group,GUILDS
)
from spatial_cohort_80y_bridge import replay_gate

OUT=ROOT/"research/results/SF_only_sufficiency_80y_20261031"
ARMS=("SF_only","no_direct_predation")
SEED_SHARDS=(101,105,109)


def run(*,regime,arm,seed_start,years=80):
    if (regime not in REGIMES or arm not in ARMS or
        seed_start not in SEED_SHARDS or years!=80):
        raise ValueError("Only predeclared 80y source model recruitment×sufficiency arms")
    assert_recruitment_axis_only_changed()
    src=source_by_recruitment_regime(regime)
    replay=replay_gate(src,years=years,window=20,dt=.25)
    for key,limit in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        if replay[key]>limit:
            raise AssertionError("Original source trophic/demographic replay failed")
    active=("SF",) if arm=="SF_only" else ()
    dataset=[];eventdata=[]
    for seed in range(seed_start,seed_start+4):
        for move in ("off","both"):
            for (_,litter),group in src.groupby(["risk","litter"],sort=True):
                group=group.reset_index(drop=True)
                output=simulate_finite_group(
                    group,scale=3,seed=seed,mode=move,
                    immigration=False,years=years,dt=.25,
                    transfer=.15,active_edges=active
                )
                a,b=summarize_finite_group(
                    group,output,scale=3,seed=seed,
                    mode=move,immigration=False,years=years
                )
                a["network_arm"]=arm
                a["recruitment_regime"]=regime
                dataset.append(a)
                if len(b):
                    b["network_arm"]=arm
                    b["recruitment_regime"]=regime
                    eventdata.append(b)
        print("SF_ONLY_80YEAR_SOURCE_SEED_COMPLETED",regime,arm,seed,flush=True)
    df=pd.concat(dataset,ignore_index=True)
    events=(pd.concat(eventdata,ignore_index=True) if eventdata else
            pd.DataFrame(columns=["structure_id","draw","seed","guild"]))
    keys=["recruitment_regime","network_arm","structure_id","reverse_on",
          "vertex","seed","movement","guild"]
    if (len(df)!=128*4*2*3 or df.duplicated(keys).any() or
        set(df.seed)!=set(range(seed_start,seed_start+4)) or
        set(df.movement)!={"off","both"} or
        not df.immigration.eq(0).all() or not df.scale.eq(3).all() or
        set(df.context)!={"original","S_growth_fast_only",
                          "D_aquatic_long_only","D_first_S_overtakes"} or
        int(df.n_local_returns.sum())!=len(events)):
        raise AssertionError("Actual 80y finite population source factorial incomplete")
    if (int(df.n_recorded_migration_arrivals.sum())!=
        int(df.n_recorded_migration_departures.sum())):
        raise AssertionError("Source count migration did not conserve mass")
    if len(events) and events.cause_label.eq("unclassified").any():
        raise AssertionError("Unexplained true return event")
    OUT.mkdir(parents=True,exist_ok=True)
    df.to_csv(OUT/"sufficiency_original_seed_scenario_guilds.csv.gz",
              index=False,compression={"method":"gzip","mtime":0})
    events.to_csv(OUT/"sufficiency_true_0_to_positive_events.csv.gz",
              index=False,compression={"method":"gzip","mtime":0})
    result=dict(
        status="TRUE_80YEAR_SF_ONLY_VS_ALL_DIRECT_PREDATORS_OFF_SOURCE",
        source_replay=replay,recruitment_regime=regime,network_arm=arm,
        active_directed_predation_edges=list(active),
        FE_zero_by_original_F65_D45_65_timing=True,
        n_synthetic_model_corners=128,
        n_seed_guild_records=int(len(df)),
        n_true_integer_zero_to_positive_returns=int(len(events)),
        independent_seed_labels=list(range(seed_start,seed_start+4)),
        original_biological_prior_draw=12,rho_alone_changed=(regime=="rate12_rho0"),
        year_horizon=80,source_ring_patches=8,synthetic_N_scale=3,
        external_immigration=False,
        both_recruits_and_survivors_annual_movement_fraction=.15,
        source_finite_N_sampling_model_unchanged=True,
        no_field_mechanism_inference=True,
        source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (OUT/"receipt.json").write_text(json.dumps(result,indent=2)+"\n")
    print("SF_ONLY_GENUINE_SOURCE_RECEIPT",json.dumps(result),flush=True)
    print("SF_ONLY_F_YEAR80_MEANS\n"+df[df.guild.eq("F")].groupby(
        ["context","plant_model","movement"]
    )["final_occupied_patches"].mean().to_string(),flush=True)
    return df,events,result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--regime",choices=REGIMES,required=True)
    p.add_argument("--arm",choices=ARMS,required=True)
    p.add_argument("--seed-start",type=int,choices=SEED_SHARDS,required=True)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run(regime=a.regime,arm=a.arm,seed_start=a.seed_start)
