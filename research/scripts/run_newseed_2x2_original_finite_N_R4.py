"""Same PR161 original 256 canonical 2x2 structures → genuine finite-N R4.

Uses UNMODIFIED PR160 integrated_finite_main3600.run_finite_batch from the
original main seasonal kernel. This stochastic model includes externally
supplied individuals; moving arrivals are not independently causal rescues.

Original source rate attack=.5, local rho=.75, stage/plant and all other
canonical features exactly reproduce the new-seed PR161 generator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confirmatory_2x2_vegetation_predator_switch import (
    N_BASE, SOURCE_MAIN_SHA, original_draws,
)
from integrated_finite_main3600 import (
    run_finite_batch, source_replay_gate, PATCHES, YEARS, WINDOW, DT,
    TRANSFER, QS, MOVE
)

N_SHARDS=16
SEEDS=(311,313)
EXPECTED_ARMS_PER_BASE=3*4*2*2*len(SEEDS)
SOURCE_ORIGINAL_RUN=41408471121
SOURCE_BRANCH_PR161="db70ffd8670e47cc8750a0b760144bc5fab36df0"


def require(value,reason):
    if not bool(value):
        raise AssertionError(reason)


def make_all_arms():
    models,prior,nuisance=original_draws()
    source=prior.drop(columns=["cover_SF","support_DF"]).join(
        models.set_index("model_id"),on="model_id",validate="many_to_one"
    )
    require(len(source)==N_BASE*12 and
            source.source_id.nunique()==N_BASE and
            not source.draw_id.duplicated().any(),
            "Original PR161 256-source 2x2 identity no longer matches")
    require(source.groupby(["source_id","context_id"]).arm.nunique().eq(4).all()
            and source.groupby(["source_id","context_id"]).model_id.nunique().eq(4).all(),
            "One of four original 3600 legal source plant interventions missing")
    require(np.array_equal(source.draw_id.to_numpy(),prior.draw_id.to_numpy()),
            "Source order changed relative to pre-fixed PR161 80year")
    require(source.groupby("source_id")[["attack","rho","conversion",
           "strength","refuge_order","gate_code"]].nunique().max().max()==1,
            "PR161 common biological theta was modified between treatments")
    require(np.allclose(source.attack.to_numpy(float),.5) and
            np.allclose(source.rho.to_numpy(float),.75),
            "Prior exploratory weak attack + high local rho regime drifted")
    rows=[]
    for q in QS:
        for move in MOVE:
            for seed in SEEDS:
                g=source.copy()
                g["q"]=int(q)
                g["move_on"]=int(move)
                g["seed"]=int(seed)
                g["edge_SF_on"]=1
                # Each source model draw already has its own immutable PR161
                # draw_id. The legacy PR160 finiteN RNG is keyed to draw_id
                # and stochastic condition: share M/theta, not exact RNG stream
                # between 00 and 11.
                g["sample_weight"]=1./N_BASE
                rows.append(g)
    arms=pd.concat(rows,ignore_index=True).sort_values(
        ["source_id","context_id","arm","q","move_on","seed"]
    ).reset_index(drop=True)
    require(len(arms)==N_BASE*EXPECTED_ARMS_PER_BASE and
            not arms.duplicated(["draw_id","q","move_on","seed"]).any() and
            arms.groupby("source_id").size().eq(EXPECTED_ARMS_PER_BASE).all(),
            "Incomplete PR161 original source × q × movement × seed matrix")
    require(arms.groupby(["source_id","context_id","arm"]).size().eq(8).all(),
            "One biological source variant lacks eight population arms")
    require(set(arms.seed)==set(SEEDS) and set(arms.q)=={3,12}
            and set(arms.move_on)=={0,1} and arms.edge_SF_on.eq(1).all(),
            "Novel unplanned population conditions present")
    return models,prior,arms


def run_shard(*,shard,output,years=80):
    require(shard in range(N_SHARDS),"Only original 16 source-ID shards allowed")
    require(years in (20,80),"Twenty-year method check or full80 only")
    models,prior,all_arms=make_all_arms()
    subset=all_arms[all_arms.source_id.mod(N_SHARDS)==shard].copy()
    require(len(subset)==16*EXPECTED_ARMS_PER_BASE and
            subset.source_id.nunique()==16,
            "Original source shard lacks exactly sixteen base backgrounds")
    # Validate all 4 mechanisms and three stages from the old source under
    # the unmodified main annual source model.
    source_probe=subset[(subset.edge_SF_on==1)&(subset.move_on==0)].iloc[[0]]
    error=source_replay_gate(source_probe)
    require(error<=1e-11,"Unmodified PR160 original main 4year replay failed")
    out=[]
    # A homogeneous original main behavior/litter/size-gate is required by
    # run_finite_batch. Bound batch size to control GitHub runner memory.
    for labels,group in subset.groupby(["behavior","litter","gate_code"],sort=True):
        sorted_rows=group.sort_values(
            ["source_id","context_id","arm","q","move_on","seed"]
        ).reset_index(drop=True)
        for offset in range(0,len(sorted_rows),64):
            batch=sorted_rows.iloc[offset:offset+64].copy()
            out.append(run_finite_batch(batch,years=years,dt=DT,transfer=TRANSFER))
    result=pd.concat(out,ignore_index=True).sort_values(
        ["draw_id","q","move_on","seed"]
    ).reset_index(drop=True)
    require(len(result)==len(subset) and
            not result.duplicated(["draw_id","q","move_on","seed"]).any(),
            "True R4 finiteN source arm lost in process")
    # Original PR160 run_finite_batch retains the original new-seed
    # proposal draw_id, not stage/plant fields. Exact one-to-one join.
    keys=["draw_id","q","move_on","seed"]
    annotations=subset[keys+["source_id","arm","attack","rho","conversion",
                    "strength","refuge_order","gate_code"]]
    result=result.merge(annotations,on=keys,validate="one_to_one")
    require(result.source_id.mod(N_SHARDS).eq(shard).all() and
            result.groupby(["source_id","context_id","arm"]).size().eq(8).all(),
            "Original PR161 source ID annotation diverged from model results")
    require(result.occupied_year80.between(0,8).all()
            and result.occupied_mean_year61_80.between(0,8).all(),
            "Original finite-N 80year occupancy outside artificial eight patches")
    for key in ("recolonization_events_80y","local_extinction_events_80y",
                "movement_assisted_returns_80y"):
        require((result[key]>=0).all() and
                np.allclose(result[key],np.rint(result[key]),rtol=0,atol=1e-12),
                "Impossible 80year count/event ledger: "+key)
    require(result[result.move_on==0].movement_assisted_returns_80y.eq(0).all(),
            "The original simulation logged a transport-assisted return without movement")
    require((result.movement_assisted_returns_80y<=
             result.recolonization_events_80y).all(),
            "Movement-flagged return exceeds model true 0 to positive returns")
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    name=f"newseed_finite_N_true80_shard_{shard:02d}.csv.gz"
    dest=output/name
    result.to_csv(dest,index=False,compression={"method":"gzip","mtime":0})
    receipt=dict(
        status="PR161_ORIGINAL_MODEL_FINITE_N_80Y_COMPLETE" if years==80 else
               "PR161_ORIGINAL_MODEL_20YEAR_METHOD_ONLY",
        source_PR161_true80_audit_run=SOURCE_ORIGINAL_RUN,
        source_PR161_branch_sha=SOURCE_BRANCH_PR161,
        source_main_biology_sha=SOURCE_MAIN_SHA,
        shard=shard,source_base_backgrounds=16,
        source_rows=len(result),source_arms_per_base=EXPECTED_ARMS_PER_BASE,
        original_PR161_256_base_seed=20261123,
        years=years,DT=DT,ring_patches=PATCHES,
        movement_fraction=TRANSFER,count_scales=list(QS),
        movement_levels=list(MOVE),process_seed_labels=list(SEEDS),
        predation_S_to_F_on=True,external_immigration_on=True,
        original_main_expected_value_replay_max_error=error,
        no_biological_source_changed=True,
        source_population_random_streams_shared_across_plant=False,
        model_patch_returns_not_exclusively_movement=False,
        field_calibration=False,
        file_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
    )
    (output/f"newseed_finite_N_shard_{shard:02d}_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("PR161_R4_GENUINE_FINITE_N_SOURCE_SHARD",
          json.dumps({k:v for k,v in receipt.items() if k!="file_sha256"}),flush=True)
    return result,receipt


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--shard",type=int,choices=tuple(range(N_SHARDS)),required=True)
    parser.add_argument("--years",type=int,choices=(20,80),default=80)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    run_shard(shard=a.shard,output=a.out,years=a.years)
