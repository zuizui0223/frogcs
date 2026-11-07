"""G11 independent disjoint-background model holdout across all frozen G8 rate cells.

Original biological model, 4 legal vegetation variants, original 80-year kernel.
The G11 protocol is fixed before any new heldout 80-year outcome is inspected.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confirmatory_2x2_vegetation_predator_switch import (
    ARMS, SOURCE_MAIN_SHA, original_draws,
    simulate_original_80y, check_source_replay,
)
from final_mechanism_common import FEATURES
from run_g8_27rate_paired_factorial import RATE_GRID, v0_negative_control

N_BASE = 256
SOURCE_SEED = 20261107
N_SHARDS = 64
SOURCES_PER_SHARD = N_BASE // N_SHARDS
YEARS, WINDOW, DT = 80, 20, .5
N_SCENARIOS = N_BASE * len(RATE_GRID) * 3 * len(ARMS)
N_VERTICES = N_SCENARIOS * 8


def require(ok, message):
    if not bool(ok):
        raise AssertionError(message)


def frozen_selection():
    """Return 256 genuinely novel baseline structural IDs and new nuisance draws."""
    models, _, old_nuisance = original_draws()
    require(len(models) == 3600 and len(old_nuisance) == 256, "Frozen catalog/sample drift")
    legal = models.loc[
        models.cover_SF.eq(0) & models.support_DF.eq(0) &
        (~models.behavior.eq("risk_refuge"))
    ].sort_values("model_id")
    require(len(legal) == 720, "Expected complete 720 original-catalog legal baseline structures")
    keyset = set(tuple(getattr(row, k) for k in FEATURES)
                 for row in models.itertuples(index=False))
    for base in legal.itertuples(index=False):
        feat = {k: getattr(base, k) for k in FEATURES}
        for _,cover,support in ARMS:
            test = dict(feat, cover_SF=cover, support_DF=support)
            require(tuple(test[k] for k in FEATURES) in keyset,
                    "Illegal counterfactual quartet for original catalog ID")
    old_ids = set(old_nuisance.original_base_model_id.astype(int))
    require(len(old_ids) == 256 and old_ids.issubset(set(legal.model_id)),
            "Original G8 structural source identity changed")
    unused = np.array(sorted(set(legal.model_id) - old_ids), dtype=int)
    require(len(unused) == 464, "Structural holdout candidate pool must contain 464 IDs")
    rng = np.random.default_rng(SOURCE_SEED)
    chosen = rng.choice(unused, N_BASE, replace=False)
    require(len(set(chosen)) == N_BASE and not (set(chosen) & old_ids),
            "G11 disjoint structural selection failed")
    nuisance = pd.DataFrame({
        "source_id": np.arange(N_BASE, dtype=int),
        "baseline_model_id": chosen,
        "original_conversion": rng.choice([2.,4.,8.], size=N_BASE),
        "strength": rng.choice([.5,1.], size=N_BASE),
        "refuge_order": rng.choice(["S","equal","D"], size=N_BASE),
        "gate_code": rng.integers(0,2, size=N_BASE),
    })
    require(nuisance.source_id.is_unique, "New nuisance source IDs not unique")
    identity = {
        "protocol": "G11_DISJOINT_STRUCTURE_HOLDOUT_PROTOCOL_2026-11-07.md",
        "original_main_commit": SOURCE_MAIN_SHA,
        "selection_seed": SOURCE_SEED,
        "eligible_legal_base_structures": len(legal),
        "original_g8_base_structures": len(old_ids),
        "remaining_preselection_structures": len(unused),
        "selected_g11_new_structures": len(chosen),
        "remaining_unselected": len(unused) - len(chosen),
        "old_base_ids_sorted": sorted(int(x) for x in old_ids),
        "new_base_ids_by_source": [int(x) for x in chosen],
        "new_nuisance_by_source": nuisance.to_dict("records"),
    }
    selection_sha = hashlib.sha256(
        json.dumps(identity, sort_keys=True, ensure_ascii=False,
                   separators=(",",":")).encode("utf8")).hexdigest()
    return models, nuisance, identity, selection_sha


def make_grid(source_ids, rate_ids=None, contexts=(0,1,2)):
    models, nuisance, identity, selection_sha = frozen_selection()
    source_ids = tuple(source_ids)
    rate_ids = tuple(range(len(RATE_GRID))) if rate_ids is None else tuple(rate_ids)
    contexts = tuple(contexts)
    require(len(source_ids)>0 and len(set(source_ids)) == len(source_ids) and
            all(0<=sid<N_BASE for sid in source_ids), "Bad disjoint source IDs")
    require(len(rate_ids)>0 and len(set(rate_ids)) == len(rate_ids) and
            all(0<=rid<len(RATE_GRID) for rid in rate_ids), "Bad rate IDs")
    require(len(contexts)>0 and len(set(contexts)) == len(contexts) and
            all(c in (0,1,2) for c in contexts), "Bad original context IDs")
    keymap = {
        tuple(getattr(row,k) for k in FEATURES): int(row.model_id)
        for row in models.itertuples(index=False)
    }
    require(len(keymap)==3600, "Canonical feature lookup not unique")
    base_models = models.set_index("model_id")
    raw=[]
    for source_id in source_ids:
        f=nuisance.iloc[source_id]
        base=base_models.loc[int(f.baseline_model_id)]
        feat={k:base[k] for k in FEATURES}
        require(feat["cover_SF"]==0 and feat["support_DF"]==0 and
                feat["behavior"]!="risk_refuge", "Non-legal heldout baseline")
        for context in contexts:
            for arm_idx,(arm,cover,support) in enumerate(ARMS):
                variant={**feat, "cover_SF":cover, "support_DF":support}
                key=tuple(variant[k] for k in FEATURES)
                require(key in keymap, "New quartet not in original 3600 catalog")
                before=source_id*12+context*4+arm_idx
                for rid in rate_ids:
                    attack,rho,conversion=RATE_GRID[rid]
                    raw.append({
                        "draw_id":before*27+rid,
                        "source_id":source_id,
                        "original_draw_id":before,
                        "rate_id":rid,
                        "context_id":context,
                        "arm":arm,
                        "model_id":keymap[key],
                        "baseline_model_id":int(f.baseline_model_id),
                        "attack":attack,
                        "rho":rho,
                        "conversion":conversion,
                        "original_conversion":float(f.original_conversion),
                        "strength":float(f.strength),
                        "refuge_order":str(f.refuge_order),
                        "gate_code":int(f.gate_code),
                        "cover_SF":cover,
                        "support_DF":support,
                    })
    design=pd.DataFrame(raw).sort_values("draw_id").reset_index(drop=True)
    require(len(design)==len(source_ids)*len(rate_ids)*len(contexts)*4 and
            design.draw_id.is_unique and
            design.groupby(["source_id","rate_id","context_id"]).arm.nunique().eq(4).all(),
            "Incomplete heldout crossed source design")
    require(design.groupby("source_id")[["strength","refuge_order","gate_code"]]
            .nunique().max().max()==1,"Changed nuisance across rate/context")
    require(design.groupby(["source_id","rate_id","context_id"])
            .model_id.nunique().eq(4).all(), "Missing original canonical plant variants")
    for rid,(attack,rho,conversion) in enumerate(RATE_GRID):
        r=design[design.rate_id==rid]
        if not r.empty:
            require(np.array_equal(r[["attack","rho","conversion"]].to_numpy(),
                                   np.broadcast_to([attack,rho,conversion],(len(r),3))),
                    "G11 rate grid changed")
    return models,design,identity,selection_sha


def run(shard, out, smoke=False):
    require(0 <= shard < N_SHARDS, "Unknown holdout shard")
    original_ids=tuple(range(shard*SOURCES_PER_SHARD,(shard+1)*SOURCES_PER_SHARD))
    ids=original_ids[:1] if smoke else original_ids
    rate_ids=(0,13) if smoke else tuple(range(27))
    contexts=(0,1) if smoke else (0,1,2)
    years=4 if smoke else YEARS
    models,design,identity,identity_sha=make_grid(ids,rate_ids,contexts)
    # Leave the original unchanged 80-year model function as the sole generator.
    outcomes,vertices=simulate_original_80y(design,models,
                                  years=years,window=2 if smoke else WINDOW,
                                  dt=DT,chunk=24)
    metadata=design[["draw_id","original_draw_id","original_conversion",
                     "rate_id","baseline_model_id"]]
    outcomes=outcomes.merge(metadata,how="left",on="draw_id",validate="one_to_one")
    vertices=vertices.merge(metadata,how="left",on="draw_id",validate="many_to_one")
    require(len(outcomes)==len(design) and len(vertices)==len(design)*8,
            "Source biological rows or V/S/D vertices missing")
    null_err=v0_negative_control(vertices)
    if smoke:
        check_source_replay(models,design,outcomes,years=4)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    label=f"g11_{'smoke' if smoke else 'true80'}_{shard:02d}"
    ef=out/(label+"_effects.csv.gz")
    vf=out/(label+"_vertices.csv.gz")
    gz={"method":"gzip","mtime":0}
    outcomes.sort_values("draw_id").to_csv(ef,index=False,compression=gz)
    vertices.sort_values(["draw_id","vertex"]).to_csv(vf,index=False,compression=gz)
    receipt=dict(
        status="G11_FOUR_YEAR_METHOD_ONLY" if smoke else "G11_TRUE80_DISJOINT_SHARD",
        shard=shard,n_shards=N_SHARDS,source_ids=list(ids),
        source_baseline_model_ids=[identity["new_base_ids_by_source"][i] for i in ids],
        old_G8_structure_count=256,old_new_structural_overlap=0,
        eligible_legal_baselines=720,remaining_preselection=464,
        selection_sha256=identity_sha,selection_seed=SOURCE_SEED,
        source_main_sha=SOURCE_MAIN_SHA,years=years,dt=DT,
        window=2 if smoke else WINDOW,contexts=list(contexts),
        rates=list(rate_ids),plant_arms=["00","10","01","11"],
        n_original_scenarios=len(outcomes),n_original_vertices=len(vertices),
        max_abs_V0_plant_null=null_err,
        file_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (ef,vf)},
        used_all_outcomes_including_failures=True,
        field_model_likelihood=False,
    )
    (out/(label+"_receipt.json")).write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("G11_HELDOUT_SOURCE_SHARD "+json.dumps({
        "status":receipt["status"],"shard":shard,
        "scenarios":len(outcomes),"vertices":len(vertices),
        "selection_sha256":identity_sha,"V0_null":null_err}),flush=True)
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--shard",required=True,type=int)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--smoke",action="store_true")
    a=ap.parse_args()
    run(a.shard,a.out,a.smoke)
