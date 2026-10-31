"""Run TRUE 80-year finite-N frogs/salamanders/dragonflies with ONE directed
predator edge ablated under paired original-LHS recruitment regimes.

The four simulated active directed edges are SF, DF, DS and SD.
The fifth F->emerging D edge FE is STRUCTURALLY INACTIVE in the frozen
source (frog completion day65 >= D emergence-end day45 or65). It is
source-tested and intentionally NOT pseudo-treated as a biological factor.

All results are MODEL-INTERNAL to the original unmodified seasonal hazard
kernel and the explicit finite-N binomial/Poisson annual recruitment model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from rate_axis_synthetic_growth_rescue_80y import (
    original_rate_factorial,swap_fixed_rate_axis
)
from finite_n_source_cohort_bridge import (
    ROOT,simulate_finite_group,summarize_finite_group,GUILDS
)
from spatial_cohort_80y_bridge import replay_gate

OUT=ROOT/"research/results/predator_edge_recruitment_80y_20261031"
REGIMES=("rate12_base","rate12_rho0")
ACTIVE_EDGES=("SF","DF","DS","SD")
SOURCE_SEED_SHARDS=(101,105,109)
SOURCE_SEEDS=tuple(range(101,113))
YEARS=80
SCALE=3
TRANSFER=.15


def source_by_recruitment_regime(regime):
    if regime=="rate12_base":
        source=original_rate_factorial(12)
    elif regime=="rate12_rho0":
        source=swap_fixed_rate_axis(12,"rho")
    else:
        raise ValueError("Unapproved or outcome-selected local recruitment regime")
    if (len(source)!=128 or not source.draw.eq(12).all()
        or not source.risk.eq(False).all()
        or set(source.context)!={"original","S_growth_fast_only",
                                  "D_aquatic_long_only","D_first_S_overtakes"}
        or set(source.plant_model)!={"SF0_DF0_DS1_L0","SF1_DF0_DS0_L1"}
        or source.duplicated(["structure_id","draw","reverse_on","vertex"]).any()):
        raise AssertionError("Unbalanced original trophic biological source")
    return source


def assert_recruitment_axis_only_changed():
    base=source_by_recruitment_regime("rate12_base")
    on=source_by_recruitment_regime("rate12_rho0")
    cols=[c for c in base.columns if c!="rho"]
    if not base[cols].equals(on[cols]):
        # Numeric roundtrip compared separately if original/source values
        # differ due to benign dtype but all design columns should match.
        for c in cols:
            if pd.api.types.is_numeric_dtype(base[c]):
                if not np.allclose(base[c],on[c],rtol=0,atol=1e-12):
                    raise AssertionError("Non-rho biological rate changed: "+c)
            elif not base[c].equals(on[c]):
                raise AssertionError("Non-rho source label or plant context changed: "+c)
    if np.allclose(base.rho,on.rho,atol=1e-12,rtol=0):
        raise AssertionError("Recruitment factor control did not actually change rho")
    return True


def run(*,regime,edge_off,seed_start,years=YEARS,
        scale=SCALE,transfer=TRANSFER):
    if (regime not in REGIMES or edge_off not in ACTIVE_EDGES or
        seed_start not in SOURCE_SEED_SHARDS or years!=YEARS or
        scale!=SCALE or not np.isclose(transfer,TRANSFER)):
        raise ValueError("Only the frozen 80y source edge×recruitment design allowed")
    assert_recruitment_axis_only_changed()
    source=source_by_recruitment_regime(regime)
    errors=replay_gate(source,years=YEARS,window=20,dt=.25)
    for name,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
        if errors[name]>tol:
            raise AssertionError("Original trophic+80y deterministic source identity failed: "+name)
    rows=[]
    returns=[]
    for seed in range(seed_start,seed_start+4):
        for mode in ("off","both"):
            for (_,litter),g in source.groupby(["risk","litter"],sort=True):
                g=g.reset_index(drop=True)
                output=simulate_finite_group(
                    g,scale=scale,seed=seed,mode=mode,immigration=False,
                    years=years,dt=.25,transfer=transfer,edge_off=edge_off
                )
                f,e=summarize_finite_group(
                    g,output,scale=scale,seed=seed,mode=mode,
                    immigration=False,years=years
                )
                f["edge_off"]=edge_off
                f["recruitment_regime"]=regime
                rows.append(f)
                if len(e):
                    e["edge_off"]=edge_off
                    e["recruitment_regime"]=regime
                    returns.append(e)
        print("EDGE_HAZARD_TRUE_SOURCE_80Y_COMPLETED",regime,edge_off,seed,flush=True)
    df=pd.concat(rows,ignore_index=True)
    events=(pd.concat(returns,ignore_index=True) if returns else
            pd.DataFrame(columns=["structure_id","draw","seed","guild"]))
    keys=["edge_off","recruitment_regime","structure_id","draw","reverse_on",
          "vertex","seed","movement","guild"]
    if (len(df)!=128*4*2*len(GUILDS) or
        df.duplicated(keys).any() or set(df.context)!={
            "original","S_growth_fast_only","D_aquatic_long_only",
            "D_first_S_overtakes"} or
        set(df.seed)!=set(range(seed_start,seed_start+4)) or
        not df.immigration.eq(0).all() or
        not df.scale.eq(scale).all() or
        set(df.movement)!={"off","both"} or
        int(df.n_local_returns.sum())!=len(events)):
        raise AssertionError("Original source/return/movement 80year data incomplete")
    if int(df.n_recorded_migration_arrivals.sum())!=int(
        df.n_recorded_migration_departures.sum()):
        raise AssertionError("Integer-conservative migration mass ledger mismatch")
    if len(events) and events.cause_label.eq("unclassified").any():
        raise AssertionError("At least one reoccupation source is not classified")

    OUT.mkdir(parents=True,exist_ok=True)
    df.to_csv(OUT/"edge_original_seed_scenario_guilds.csv.gz",index=False,
              compression={"method":"gzip","mtime":0})
    events.to_csv(OUT/"edge_true_0_to_positive_events.csv.gz",index=False,
                  compression={"method":"gzip","mtime":0})
    local=(df[df.guild.eq("F")].groupby(["context","plant_model","movement"],
                                      sort=True)
           .agg(mean_final_occupied=("final_occupied_patches","mean"),
                mean_local_returns=("n_local_returns","mean"))
           .reset_index())
    local.to_csv(OUT/"source_F_80year_means.csv",index=False)
    receipt=dict(
        status="TRUE_80YEAR_SINGLE_TROPHIC_EDGE_REMOVAL_FINITE_N",
        recruitment_regime=regime,base_256_LHS_rate_draw_id=12,
        rho_changed_from_original_12_only=(regime=="rate12_rho0"),
        source_replay_differences=errors,
        single_ablation_removed_directed_edge=edge_off,
        source_original_stage_arrival_days={"F":20,"S":20,"D":0},
        F_completion_day=65,D_emergence_end_days=[45,65],
        edge_FE_structurally_inactive_under_original_source=True,
        source_stage_plant_reverse_factors=128,
        n_true_80year_seed_guild_scenarios=int(len(df)),
        n_true_0_to_positive_events=int(len(events)),
        independent_seed_labels=list(range(seed_start,seed_start+4)),
        n_synthetic_patches=8,years=YEARS,cohort_scale=SCALE,
        movement_modes=["off","both"],annual_movement_fraction=transfer,
        external_immigration=False,
        original_120day_biology_kernel_reused=True,
        no_wild_prey_predator_mechanism_inference=True,
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (OUT/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("TRUE_SOURCE_PREDATOR_EDGE_REMOVAL_RECEIPT",json.dumps(receipt),flush=True)
    print("TRUE_SOURCE_F_80Y\n"+local.to_string(index=False),flush=True)
    return df,events,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--regime",choices=REGIMES,required=True)
    p.add_argument("--edge-off",choices=ACTIVE_EDGES,required=True)
    p.add_argument("--seed-start",type=int,choices=SOURCE_SEED_SHARDS,required=True)
    a=p.parse_args()
    if not a.run:
        p.error("Explicit --run required")
    run(regime=a.regime,edge_off=a.edge_off,seed_start=a.seed_start)
