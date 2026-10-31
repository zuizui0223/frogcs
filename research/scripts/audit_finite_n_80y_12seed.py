"""Combine completed original four seed and NEW eight 80y source runs.

Never rerun or re-fit the biology. RNG seed 101–112 are independent
replications; all 64 same source cube treatment cells are fixed design.
The resulting 12-seed CI is synthetic Monte Carlo only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

FULL_SEEDS=tuple(range(101,113))
NEW_BLOCKS=((105,106,107,108),(109,110,111,112))
MODES=("off","both")
GUILDS=("F","S","D")
METRICS=("final_occupied_patches","n_local_returns","n_local_extinctions",
         "n_3y_persistent_with_recruitment")


def load(original,extra):
    f0=original/"source_80year_finite_seed_scenarios.csv.gz"
    if not f0.exists():
        raise AssertionError("Original completed 4-seed source artifact missing")
    old=pd.read_csv(f0)
    if (set(old.seed)!={101,102,103,104} or len(old)!=12288
        or set(old.movement)!={"off","recruits","carryover","both"}):
        raise AssertionError("Original genuine 80y source invalid or incomplete")
    old=old[old.movement.isin(MODES)].copy()
    dirs=sorted(p for p in extra.iterdir() if p.is_dir() and p.name.startswith(
        "frogcs-finite-n-extra8-source-"
    ))
    if len(dirs)!=8:
        raise AssertionError(f"All eight independent 80y rate shards required, got {len(dirs)}")
    keys=set()
    frames=[old]
    for folder in dirs:
        receipt=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        scale=receipt["finite_individual_count_scales"]
        im=receipt["immigration_states"]
        seeds=tuple(receipt["seeds"])
        if (len(scale)!=1 or len(im)!=1 or seeds not in NEW_BLOCKS
            or receipt["source_years"]!=80 or receipt["cohort_source_cases"]!=64
            or receipt["movement_modes"]!=list(MODES)
            or receipt["patches"]!=8
            or any(v>1e-8 for v in receipt["source_replay_differences"].values())):
            raise AssertionError("New 80-year seed source protocol/replay invalid")
        cond=(int(scale[0]),bool(im[0]),seeds)
        if cond in keys:
            raise AssertionError("Repeated new seed/count/immigration condition")
        keys.add(cond)
        f=pd.read_csv(folder/"finite_seed_scenario_guild_summary.csv.gz")
        if (len(f)!=64*len(seeds)*len(MODES)*len(GUILDS)
             or set(f.seed)!=set(seeds)
             or set(f.scale)!={int(scale[0])}
             or set(f.immigration)!={int(im[0])}
             or set(f.movement)!=set(MODES)):
            raise AssertionError("Incomplete true new 80y biological source data")
        events=pd.read_csv(folder/"finite_recolonization_followups.csv.gz")
        if len(events)!=int(f.n_local_returns.sum()):
            raise AssertionError("New reoccupation events not source verified")
        if int(f.n_recorded_migration_arrivals.sum())!=int(
               f.n_recorded_migration_departures.sum()):
            raise AssertionError("Source land exchange conservation failed")
        frames.append(f)
    expected={(sc,im,seed) for sc in (3,12)
              for im in (False,True) for seed in NEW_BLOCKS}
    if keys!=expected:
        raise AssertionError("Missing fixed new replicate treatment")
    both=pd.concat(frames,ignore_index=True)
    unique=["structure_id","draw","reverse_on","vertex","scale",
            "immigration","seed","movement","guild"]
    if (len(both)!=64*12*2*2*2*3 or
        both.duplicated(unique).any() or
        set(both.seed)!=set(FULL_SEEDS)):
        raise AssertionError("Full twelve true-seed source census is incomplete")
    return both


def summarize(source,out):
    x=source
    index=["structure_id","draw","reverse_on","vertex",
           "scale","immigration","seed","guild"]
    old=x[x.movement.eq("off")].set_index(index).sort_index()
    new=x[x.movement.eq("both")].set_index(index).sort_index()
    if not old.index.equals(new.index):
        raise AssertionError("Cannot pair original 2x2x2 model and 12 distinct seed labels")
    d=(new[list(METRICS)]-old[list(METRICS)]).reset_index()
    vals=(d.groupby(["scale","immigration","guild","seed"],sort=True)[list(METRICS)]
          .mean().reset_index())
    rng=np.random.default_rng(20261031)
    results=[]
    for key,g in vals.groupby(["scale","immigration","guild"],sort=True):
        if sorted(g.seed.tolist())!=list(FULL_SEEDS):
            raise AssertionError("Require independent 101...112 labels exactly once")
        r=dict(zip(["scale","immigration","guild"],key),
               n_independent_seed_blocks=12,
               n_fixed_model_conditions_per_seed=64)
        g=g.sort_values("seed")
        for metric in METRICS:
            a=g[metric].to_numpy(float)
            draws=rng.integers(0,12,size=(9999,12))
            boot=a[draws].mean(axis=1)
            r["delta_"+metric+"_mean"]=float(a.mean())
            r["delta_"+metric+"_orig4"]=float(a[:4].mean())
            r["delta_"+metric+"_new8"]=float(a[4:].mean())
            r["delta_"+metric+"_95mc_lower"]=float(np.quantile(boot,.025))
            r["delta_"+metric+"_95mc_upper"]=float(np.quantile(boot,.975))
            r["delta_"+metric+"_positive_seed_blocks"]=int((a>0).sum())
            r["delta_"+metric+"_negative_seed_blocks"]=int((a<0).sum())
            r["delta_"+metric+"_zero_seed_blocks"]=int((a==0).sum())
        results.append(r)
    combined=pd.DataFrame(results)
    # Do not hide the very stage×plant context that motivates this bridge.
    # Source model names are original context__handling__risk__plant labels.
    d["context"]=d.structure_id.astype(str).str.split("__").str[0]
    d["plant_model"]=d.structure_id.astype(str).str.split("__").str[-1]
    if (set(d.context)!={"original","D_first_S_overtakes"} or
        set(d.plant_model)!={"SF1_DF0_DS0_L1","SF0_DF0_DS1_L0"}):
        raise AssertionError("Original source ontogeny/plant-role labels changed")
    disagg_by_seed=(d.groupby(["scale","immigration","context","plant_model",
                               "guild","seed"],sort=True)[list(METRICS)]
                     .mean().reset_index())
    disagg=(disagg_by_seed.groupby(["scale","immigration","context","plant_model",
                                    "guild"],sort=True)
            .agg(n_independent_seeds=("seed","size"),
                 mean_delta_occupancy=("final_occupied_patches","mean"),
                 mean_delta_returns=("n_local_returns","mean"),
                 mean_delta_extinctions=("n_local_extinctions","mean"))
            .reset_index())
    if not disagg.n_independent_seeds.eq(12).all():
        raise AssertionError("Missing source 12seed by stage × plant context")
    means=(x.groupby(["scale","immigration","movement","guild"],sort=True)
           .agg(n_seed_scenarios=("seed","size"),
                mean_final_occupied=("final_occupied_patches","mean"),
                mean_returns=("n_local_returns","mean"),
                mean_extirpations=("n_local_extinctions","mean"),
                n_3y_followable=("n_3y_observable_returns","sum"),
                n_3y_persist_recruits=("n_3y_persistent_with_recruitment","sum"))
           .reset_index())
    out.mkdir(parents=True,exist_ok=True)
    x.to_csv(out/"all_12seed_source_guild_conditions.csv.gz",index=False,
             compression={"method":"gzip","mtime":0})
    vals.to_csv(out/"paired_seed_block_deltas_12.csv",index=False)
    combined.to_csv(out/"comparison_12seed_block_intervals.csv",index=False)
    means.to_csv(out/"12seed_source_condition_means.csv",index=False)
    disagg_by_seed.to_csv(out/"12seed_stage_plant_seed_deltas.csv",index=False)
    disagg.to_csv(out/"12seed_stage_plant_interactions.csv",index=False)
    slim=combined[["scale","immigration","guild",
                   "delta_final_occupied_patches_orig4",
                   "delta_final_occupied_patches_new8",
                   "delta_final_occupied_patches_mean",
                   "delta_final_occupied_patches_95mc_lower",
                   "delta_final_occupied_patches_95mc_upper",
                   "delta_final_occupied_patches_positive_seed_blocks",
                   "delta_final_occupied_patches_negative_seed_blocks"]]
    lines=[
        "# Finite-N frogcs genuine 80y: independent 12-seed source replication",
        "",
        "**12 independently simulated RNG seed labels; original first 4 reused"
        " byte-for-byte, 8 genuinely new biological trajectories per fixed"
        " stage×plant×rate treatment.** All source replay, event/immigration,"
        " right censor and closed landscape mass checks passed. This is"
        " synthetic population dynamics, not field demographic inference.",
        "",
        "## Both annual movement streams ON − movement OFF: year80 occupied patches",
        "",
        slim.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Twelve-seed source means for all guilds",
        "",
        means.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Stage order × plant mechanism: own-immigration-OFF context differences",
        "",
        disagg[(disagg.immigration==0)&
               (disagg.guild.isin(("F","D")))].to_markdown(index=False,floatfmt=".3f"),
        "",
        "Only 12 seed labels are independent replicate units; 64 fixed model"
        " source treatment corners, patches and event rows are not additional"
        " random replication. Bootstrap 9999 resamples 12 seed-block means"
        " and reflects only this chosen source parameter/design space."
        " Different movement treatments use distinct RNG streams even with"
        " equal seed labels: the comparison is not individual pathwise.",
        "Any source-native F_B four signs are not field-acoustic validation;"
        " no 12-seed claim warrants unique causal model selection.",
    ]
    (out/"AUDITED_12SEED_80Y_FINITE_N_RESULT.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    receipt=dict(status="FULL_12_INDEPENDENT_SEED_80Y_SOURCE_REPLICATION_SUCCESS",
                 original_seed_count=4,new_seed_count=8,
                 n_source_guild_conditions=int(len(x)),
                 n_paired_source_treatments=int(len(d)),
                 n_actual_seed_blocks=12,
                 causal_field_inference=False)
    (out/"AUDITED_12SEED_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt),flush=True)
    print("TWELVE_SEED_OCCUPANCY_CONTRASTS\n"+slim.to_string(index=False),flush=True)
    print("TWELVE_SEED_SOURCE_MEANS\n"+means.to_string(index=False),flush=True)
    print("TWELVE_SEED_STAGE_PLANT_CONTEXT\n"+disagg.to_string(index=False),flush=True)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--extra-shards",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    summarize(load(a.original,a.extra_shards),a.out)
