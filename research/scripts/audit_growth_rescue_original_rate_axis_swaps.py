"""Fail-closed audit for all 16 single-original-LHS-axis swaps (4-seed pilot).

Reuses verified PR151 draw ID0 and ID12 source controls, with no rerun or
counterfactual fitting. Every new 80y arm must be genuine, run successfully
under exactly the original trophic kernel and finite-N conditional-demographic
equations; source of the large repeated event counts remains explicit.

DO NOT treat the four-seed pilot as definitive parameter-region inference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from rate_axis_synthetic_growth_rescue_80y import AXES, BASES, CONTEXTS, PLANTS
from model_native_2x2x2_prior import matching_prior_draws

SEEDS=(101,102,103,104)
KEYS=("base_rate_id","swapped_axis","context","plant_model",
      "reverse_on","vertex","seed","guild")
MOVEMENT_KEY=list(KEYS)
REQUIRED_METRICS=("final_occupied_patches","n_local_returns","n_local_extinctions")
EXPECTED_NAMES={(base,ax) for base in BASES for ax in AXES}


def validate_source(src_dir,new_dir):
    oldfile=src_dir/"all_four_rate_12seed_original_source_guilds.csv.gz"
    if not oldfile.exists():
        raise AssertionError("Missing immutable original four-rate genuine source")
    old=pd.read_csv(oldfile)
    if (len(old)!=36864 or set(old.draw)!={0,4,8,12} or
        set(old.seed)!=set(range(101,113))):
        raise AssertionError("Original biological rate source not the verified PR151 data")
    old=old[old.draw.isin(BASES)&old.seed.isin(SEEDS)&
            old.movement.isin(("off","both"))].copy()
    old["base_rate_id"]=old.draw
    old["swapped_axis"]="BASE_NO_RATE_CHANGE"
    if len(old)!=2*4*2*2*8*4*2*3:
        raise AssertionError("Baseline original 80y source factorial missing")
    dirs=sorted(d for d in new_dir.iterdir() if d.is_dir() and
                d.name.startswith("frogcs-rate-axis-80y-"))
    if len(dirs)!=16:
        raise AssertionError(f"16 source-fixed controlled swap shards required, got {len(dirs)}")
    found=set()
    records=[old]
    true_events=0
    for p in dirs:
        rc=json.loads((p/"receipt.json").read_text(encoding="utf-8"))
        case=(rc["base_rate_id"],rc["changed_original_LHS_axis"])
        if case not in EXPECTED_NAMES or case in found:
            raise AssertionError("Source rate-axis intervention missing, repeated or selected")
        found.add(case)
        if (rc["status"]!="ORIGINAL_80Y_PROCESS_RATE_SINGLE_AXIS_SWAP_TRUE_SOURCE"
            or rc["donor_rate_id"] != (12 if case[0]==0 else 0)
            or rc["years"]!=80 or rc["scale"]!=3
            or rc["movement_fraction"]!=.15
            or rc["random_seed_labels"]!=list(SEEDS)
            or rc["no_external_immigration"] is not True
            or rc["source_hypotheses"]!=128):
            raise AssertionError("Biological source rate swap design drift")
        replay=rc["exact_original_seasonal_kernel_replay"]
        for v,lim in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if replay[v]>lim:
                raise AssertionError("Source 80y model replay failed "+str(case))
        f=pd.read_csv(p/"axis_original_seed_guilds.csv.gz")
        events=pd.read_csv(p/"axis_true_return_events.csv.gz")
        if (len(f)!=128*4*2*3 or set(f.context)!=set(CONTEXTS) or
            set(f.plant_model)!=set(PLANTS) or
            set(f.seed)!=set(SEEDS) or set(f.movement)!={"off","both"} or
            not f.draw.eq(case[0]).all() or
            not f.immigration.eq(0).all() or
            f.duplicated(["structure_id","reverse_on","vertex",
                          "seed","guild","movement"]).any() or
            len(events)!=int(f.n_local_returns.sum())):
            raise AssertionError("A source-verified output shard is incomplete "+str(case))
        if (int(f.n_recorded_migration_arrivals.sum())!=
            int(f.n_recorded_migration_departures.sum())):
            raise AssertionError("Source movement ledger does not conserve guild cohorts")
        if len(events) and events.cause_label.eq("unclassified").any():
            raise AssertionError("Return source cannot be reconstructed")
        f["base_rate_id"]=case[0]
        f["swapped_axis"]=case[1]
        records.append(f)
        true_events+=len(events)
    if found!=EXPECTED_NAMES:
        raise AssertionError("Some originally prescribed biological rate axes missing")
    result=pd.concat(records,ignore_index=True)
    if (len(result)!=18*4*2*2*8*4*2*3 or
        result.duplicated(list(KEYS)+["movement"]).any()):
        raise AssertionError("Missing source×axis×plant×stage×seed×guild identities")
    for _,g in result.groupby(["base_rate_id","swapped_axis","context",
                              "plant_model","seed","guild"]):
        if (len(g)!=32 or set(g.reverse_on)!={0,1} or
            set(g.vertex)!=set(range(8)) or
            set(g.movement)!={"off","both"}):
            raise AssertionError("Unbalanced source 2×2×2 on/off cell")
    return result,true_events


def main_analysis(df,true_events,out):
    off=df[df.movement.eq("off")].set_index(MOVEMENT_KEY).sort_index()
    on=df[df.movement.eq("both")].set_index(MOVEMENT_KEY).sort_index()
    if not off.index.equals(on.index):
        raise AssertionError("No matched source/corner/seed effects")
    effect=(on[list(REQUIRED_METRICS)]-off[list(REQUIRED_METRICS)])
    effect=effect.add_prefix("delta_").reset_index()
    f=effect[effect.guild.eq("F")].copy()
    per_seed=(f.groupby(["base_rate_id","swapped_axis","plant_model",
                         "context","seed"],sort=True)
              [[f"delta_{x}" for x in REQUIRED_METRICS]]
              .mean().reset_index())
    counts=per_seed.groupby(["base_rate_id","swapped_axis","plant_model","context"]
                             ).seed.nunique()
    if not counts.eq(4).all():
        raise AssertionError("No independent four-seed model diagnostic")
    agg=(per_seed.groupby(["base_rate_id","swapped_axis",
                           "plant_model","context"],sort=True)
          .agg(mean_movement_occupied=("delta_final_occupied_patches","mean"),
               seed_min=("delta_final_occupied_patches","min"),
               seed_max=("delta_final_occupied_patches","max"),
               mean_reoccupation_delta=("delta_n_local_returns","mean"),
               mean_extirpation_delta=("delta_n_local_extinctions","mean"))
          .reset_index())
    grid=agg.pivot(index=["base_rate_id","swapped_axis","plant_model"],
                   columns="context",values="mean_movement_occupied").reset_index()
    if (len(grid)!=18*2 or
        set(grid.columns)-{"base_rate_id","swapped_axis","plant_model"}!=set(CONTEXTS)):
        raise AssertionError("Missing source-stage 2x2 factorial for inferred biological rate effect")
    grid["strict_growth_sign_reversal"]=(
        (grid["original"]>0)&(grid["D_aquatic_long_only"]>0)&
        (grid["S_growth_fast_only"]<0)&(grid["D_first_S_overtakes"]<0)
    )
    grid["growth_main_effect"]=.5*(
        grid["S_growth_fast_only"]+grid["D_first_S_overtakes"]-
        grid["original"]-grid["D_aquatic_long_only"]
    )
    grid["period_main_effect"]=.5*(
        grid["D_aquatic_long_only"]+grid["D_first_S_overtakes"]-
        grid["original"]-grid["S_growth_fast_only"]
    )
    grid["interaction"]=(
        grid["D_first_S_overtakes"]-grid["S_growth_fast_only"]-
        grid["D_aquatic_long_only"]+grid["original"]
    )
    signs=(grid.groupby(["base_rate_id","swapped_axis"],sort=True)
           .agg(reversal_plant_roles=("strict_growth_sign_reversal","sum"),
                n_plant_roles=("plant_model","size"),
                mean_growth_effect=("growth_main_effect","mean"))
           .reset_index())
    if not signs.n_plant_roles.eq(2).all():
        raise AssertionError("Only selected plant roles in rate swap endpoint")

    prior=matching_prior_draws(256)
    prior=prior[prior.draw.isin(BASES)].sort_values("draw")
    if list(prior.draw)!=list(BASES):
        raise AssertionError("Original rate source/ID mapping changed")
    out.mkdir(parents=True,exist_ok=True)
    for name,frame in (
        ("all_true_source_fourseed_rate_axis_guilds.csv.gz",df),
        ("matched_movement_source_fourseed.csv.gz",effect),
        ("fourseed_native_growth_duration_context_effects.csv",agg),
        ("fourseed_rate_axis_2x2_sign_reversal.csv",grid),
        ("fourseed_rate_axis_reversal_counts.csv",signs),
        ("exact_original_LHS_rate0_12_vectors.csv",prior),
    ):
        frame.to_csv(out/name,index=False,
                     compression={"method":"gzip","mtime":0} if name.endswith(".gz") else None)
    receipt=dict(status="ALL_16_TRUE_80YEAR_SINGLE_RATE_AXES_AUDITED_WITH_ORIGINAL_ENDPOINTS",
                 biologically_independent_rate_draw_endpoints=2,
                 true_experimental_single_axis_swaps=16,
                 original_controls_reused=True,
                 n_guild_scenario_source_records=int(len(df)),
                 n_matched_source_guild_contrasts=int(len(effect)),
                 n_new_true_zero_to_positive_events=int(true_events),
                 n_independent_seed_labels_per_rate_axis=4,
                 field_parameter_rate_inference=False)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    lines=[
        "# Frogcs: original LHS ID0↔ID12 one-axis source swap (4seed diagnostic)",
        "",
        "Actual source tests and 80-year runs for all 16 predeclared interventions"
        " passed; original ID0 and12 verified source reused, no retuning or"
        " additional selection. This is a **4-seed conditional diagnostic**,"
        " not evidence that any original LHS rate is sufficient or necessary"
        " across field systems, alternative rate backgrounds, or stochastic laws.",
        "",
        "## All rate axes and both counterfactual directions (do not select only successes)",
        "",
        signs.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Fixed plant context and source factor cells",
        "",
        grid.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Actual fixed rate vectors",
        "",
        prior.to_markdown(index=False,floatfmt=".4f"),
        "",
        "One-axis swap into ID0 tests loss of the ID0 sign pattern conditional"
        " on the other seven ID0 rate components. The converse into ID12"
        " tests gain conditional on the other seven ID12 components."
        " Nonzero interactions between rate axes are not eliminated."
        " Complete swap of all eight rate axes exactly reconstructs the donor"
        " source vector, a source/input positive control. No wild predation"
        " rates, true wetland movement, density, or adult calling data fitted.",
    ]
    (out/"AUDITED_FOURSEED_RATE_AXIS_SOURCE_FINDINGS.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    print("RATE_AXIS_AUDIT_SUCCESS",json.dumps(receipt),flush=True)
    print("RATE_AXIS_REVERSAL_COUNTS\n"+signs.to_string(index=False),flush=True)
    print("RATE_AXIS_GROWTH_EFFECTS\n"+grid.to_string(index=False),flush=True)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--swap-shards",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    df,n=validate_source(args.original,args.swap_shards)
    main_analysis(df,n,args.out)
