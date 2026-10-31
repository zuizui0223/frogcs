"""Intermediate-scale q6/q9 boundary check following q3/q12 fixed-source comparison.

Use actual original 120-day hazard +80year maturation source unchanged.
q6/q9 are arbitrary synthetic count-per-density sensitivities (vs source
verified q3 from PR153), not an estimate of field individual abundance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from run_predator_edge_recruitment_80y import (
    ROOT, REGIMES, source_by_recruitment_regime,
    assert_recruitment_axis_only_changed
)
from finite_n_source_cohort_bridge import (
    simulate_finite_group, summarize_finite_group, GUILDS
)
from spatial_cohort_80y_bridge import replay_gate

OUT = ROOT/"research/results/SF_predation_intermediate_q6_q9_20261031"
NETWORKS=("all_active","SF_only","no_SF","no_direct_predation")
NETWORK_ACTIVE={
    "all_active":None,
    "SF_only":("SF",),
    "no_SF":("DF","DS","SD"),
    "no_direct_predation":(),
}
SEED_STARTS=(101,105,109)
YEARS=80
SCALES=(6,9)
MOVE=.15


def run(*, regime, network, seed_start, years=YEARS, scale=6):
    if (regime!="rate12_rho0" or network not in NETWORKS or
        seed_start not in SEED_STARTS or years!=YEARS or scale not in SCALES):
        raise ValueError("Only frozen q6/q9 high-recruitment 80y source factorial accepted")
    assert_recruitment_axis_only_changed()
    cube=source_by_recruitment_regime(regime)
    if len(cube)!=128 or cube.duplicated(["structure_id","draw","reverse_on","vertex"]).any():
        raise AssertionError("Original source full 2x2x2 cube missing")
    errors=replay_gate(cube, years=years, window=20, dt=.25)
    for field,limit in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        if errors[field]>limit:
            raise AssertionError("Source PR146 reproduction failed: "+field)
    samples=[]
    events=[]
    for seed in range(seed_start,seed_start+4):
        for mobility in ("off","both"):
            for (_,litter),g in cube.groupby(["risk","litter"],sort=True):
                g=g.reset_index(drop=True)
                x=simulate_finite_group(
                    g,scale=scale,seed=seed,mode=mobility,
                    immigration=False,years=years,dt=.25,transfer=MOVE,
                    active_edges=NETWORK_ACTIVE[network]
                )
                s,e=summarize_finite_group(
                    g,x,scale=scale,seed=seed,mode=mobility,
                    immigration=False,years=years
                )
                s["network_arm"]=network
                s["recruitment_regime"]=regime
                samples.append(s)
                if len(e):
                    e["network_arm"]=network
                    e["recruitment_regime"]=regime
                    events.append(e)
        print("INTERMEDIATE_Q_80Y_SOURCE_SEED_COMPLETED",regime,network,seed,flush=True)
    data=pd.concat(samples,ignore_index=True)
    event=(pd.concat(events,ignore_index=True) if events else
           pd.DataFrame(columns=["structure_id","draw","seed","guild"]))
    keys=["network_arm","recruitment_regime","structure_id","draw",
          "reverse_on","vertex","seed","movement","guild"]
    if (len(data)!=128*4*2*len(GUILDS) or data.duplicated(keys).any() or
        set(data.seed)!=set(range(seed_start,seed_start+4)) or
        set(data.movement)!={"off","both"} or
        not data.immigration.eq(0).all() or
        not data.scale.eq(scale).all() or
        set(data.context)!={"original","S_growth_fast_only",
                           "D_aquatic_long_only","D_first_S_overtakes"} or
        set(data.plant_model)!={"SF0_DF0_DS1_L0","SF1_DF0_DS0_L1"} or
        len(event)!=int(data.n_local_returns.sum())):
        raise AssertionError("Original 80y finite source factor/event/seed totals incomplete")
    if int(data.n_recorded_migration_arrivals.sum()) != int(
         data.n_recorded_migration_departures.sum()):
        raise AssertionError("Original spatial population transfer conservation failed")
    if len(event) and event.cause_label.eq("unclassified").any():
        raise AssertionError("Unexplained integer N=0→N>0 reoccupation")
    for a,b in (("n_3y_observable_returns","followup_3y_observable"),
                ("n_3y_persistent_returns","occupied_three_followups"),
                ("n_3y_persistent_with_recruitment","operational_3y_recruitment")):
        if len(event) and int(data[a].sum())!=int(event[b].sum()):
            raise AssertionError("Three-year censor / source return denominator mismatched: "+a)
    OUT.mkdir(parents=True,exist_ok=True)
    data.to_csv(OUT/"q6_q9_real_80y_seed_scenario_guild.csv.gz",
                compression={"method":"gzip","mtime":0},index=False)
    event.to_csv(OUT/"q6_q9_real_zero_to_positive_events.csv.gz",
                 compression={"method":"gzip","mtime":0},index=False)
    receipt=dict(
        status="ORIGINAL_120DAY_TROPHIC_80YEAR_FINITE_N_INTERMEDIATE_Q_SOURCE_SUCCESS",
        q_synthetic_population_count_per_density_unit=scale,
        source_replay_errors=errors,original_rate_id=12,
        recruitment_regime=regime,network_arm=network,
        active_directed_trophic_edges=(
            ["SF","DF","DS","SD"] if NETWORK_ACTIVE[network] is None
            else list(NETWORK_ACTIVE[network])
        ),
        F_completed_D_emergence_timing_null_in_subset=True,
        n_original_source_factorial_cases=128,
        n_source_seed_guild_records=int(len(data)),
        n_true_integer_zero_to_positive_events=int(len(event)),
        independent_seed_labels=list(range(seed_start,seed_start+4)),
        original_years=years,annual_movement_fraction=MOVE,
        external_immigration=False,same_biological_rates_and_original_kernel=True,
        tested_N0_to_positive_event_and_right_censor=True,
        not_observed_field_demography=True,
        source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    )
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("INTERMEDIATE_Q_FINITE_SOURCE_RECEIPT",json.dumps(receipt),flush=True)
    print("INTERMEDIATE_Q_F_MEANS\n"+data[data.guild.eq("F")].groupby(
        ["context","plant_model","movement"]
    )["final_occupied_patches"].mean().to_string(),flush=True)
    return data,event,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--regime",choices=("rate12_rho0",),required=True)
    p.add_argument("--network",choices=NETWORKS,required=True)
    p.add_argument("--seed-start",type=int,choices=SEED_STARTS,required=True)
    p.add_argument("--scale",type=int,choices=SCALES,required=True)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run(regime=a.regime,network=a.network,seed_start=a.seed_start,scale=a.scale)
