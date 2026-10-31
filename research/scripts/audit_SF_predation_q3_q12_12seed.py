"""Fail-closed 12seed source audit of q3 (immutable PR153) vs genuine q12.

No biological process is rerun in the auditor. All 24 real q12 shards
are required, with the same original habitat, stage, plant, maturation
and trophic source as the verified q3 PR153 experiment. Count q12 is
a synthetic finite-population scale, not a field estimate.

Do not treat 8 patches × source vertices × many years as independent
replication. Exactly 12 RNG seed labels per fixed factor are sampled.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REGIMES=("rate12_base","rate12_rho0")
NETWORKS=("all_active","SF_only","no_SF","no_direct_predation")
SEED_SHARDS=((101,102,103,104),(105,106,107,108),(109,110,111,112))
ALL_SEEDS=tuple(range(101,113))
PLANTS=("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
CONTEXTS=("original","S_growth_fast_only","D_aquatic_long_only",
          "D_first_S_overtakes")
GUILDS=("F","S","D")
FIELDS=("final_occupied_patches","n_local_returns","n_local_extinctions",
        "n_3y_persistent_with_recruitment")
ID=["scale","recruitment_regime","network_arm","structure_id",
    "draw","reverse_on","vertex","seed","guild","movement"]


def load_sources(old_dir,new_root):
    src=old_dir/"original_12seed_all_networks_guilds.csv.gz"
    if not src.exists():
        raise AssertionError("Missing actual prior q3 12seed independent source artifact")
    original=pd.read_csv(src)
    if (len(original)!=129024 or set(original.network_arm)!={
        "all_active","no_SF","no_DF","no_DS","no_SD",
        "SF_only","no_direct_predation"} or
        set(original.seed)!=set(ALL_SEEDS)):
        raise AssertionError("Prior original q3 source is incomplete or altered")
    original=original[original.network_arm.isin(NETWORKS)].copy()
    if (len(original)!=2*4*128*12*2*3 or
        not original.scale.eq(3).all() or
        set(original.recruitment_regime)!=set(REGIMES)):
        raise AssertionError("Old q3 original control does not meet fixed test design")

    shards=sorted(x for x in new_root.iterdir() if x.is_dir() and
                  x.name.startswith("frogcs-q12-SF-source-"))
    if len(shards)!=24:
        raise AssertionError(f"Require exactly 24 genuine new q12 biological sources; got {len(shards)}")
    expected={(r,n,s) for r in REGIMES for n in NETWORKS for s in SEED_SHARDS}
    seen=set()
    frames=[original]
    event_records=[]
    for folder in shards:
        receipt=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        regime=receipt.get("recruitment_regime")
        network=receipt.get("network_arm")
        seedtuple=tuple(receipt.get("independent_seed_labels",[]))
        label=(regime,network,seedtuple)
        if label not in expected or label in seen:
            raise AssertionError("Duplicated or unapproved q12 source treatment "+str(label))
        seen.add(label)
        controls={
            "all_active":["SF","DF","DS","SD"],"SF_only":["SF"],
            "no_SF":["DF","DS","SD"],"no_direct_predation":[]
        }
        if (receipt.get("status")!="ORIGINAL_120DAY_TROPHIC_80YEAR_FINITE_N_Q12_SOURCE_SUCCESS"
            or receipt.get("q12_synthetic_population_count_per_density_unit")!=12
            or receipt.get("n_original_source_factorial_cases")!=128
            or receipt.get("original_years")!=80
            or receipt.get("annual_movement_fraction")!=.15
            or receipt.get("external_immigration") is not False
            or receipt.get("active_directed_trophic_edges")!=controls[network]
            or receipt.get("same_biological_rates_and_original_kernel") is not True):
            raise AssertionError("The original biological source or synthetic q12 design changed")
        for field,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if receipt["source_replay_errors"][field]>tol:
                raise AssertionError("Original deterministic 80y source not reproduced "+field)
        s=pd.read_csv(folder/"q12_real_80y_seed_scenario_guild.csv.gz")
        e=pd.read_csv(folder/"q12_real_zero_to_positive_events.csv.gz")
        if (len(s)!=128*4*2*3 or
            set(s.seed)!=set(seedtuple) or set(s.context)!=set(CONTEXTS) or
            set(s.plant_model)!=set(PLANTS) or
            set(s.movement)!={"off","both"} or
            not s.scale.eq(12).all() or not s.immigration.eq(0).all() or
            not s.network_arm.eq(network).all() or
            not s.recruitment_regime.eq(regime).all() or
            s.duplicated(ID).any() or
            len(e)!=int(s.n_local_returns.sum())):
            raise AssertionError("Source q12 2x2 stage×habitat integer ledger incomplete")
        if (int(s.n_recorded_migration_arrivals.sum())!=
            int(s.n_recorded_migration_departures.sum())):
            raise AssertionError("Original source closed 8-patch transport mass did not balance")
        if len(e) and e.cause_label.eq("unclassified").any():
            raise AssertionError("Model return classification lost")
        for a,b in (("n_3y_observable_returns","followup_3y_observable"),
                    ("n_3y_persistent_returns","occupied_three_followups"),
                    ("n_3y_persistent_with_recruitment","operational_3y_recruitment")):
            if int(s[a].sum())!=int(e[b].sum()):
                raise AssertionError("Actual 3-year recruitment return censor/count mismatch")
        frames.append(s)
        event_records.append(dict(recruitment_regime=regime,
            network_arm=network,seed_group="_".join(map(str,seedtuple)),
            n_integer_zero_to_positive_events=len(e),
            n_3y_observable=int(e.followup_3y_observable.sum()),
            n_3y_persistent=int(e.occupied_three_followups.sum()),
            n_3y_persistent_with_recruitment=int(e.operational_3y_recruitment.sum())))
    if seen!=expected:
        raise AssertionError("Missing originally prespecified source, predator and seed strata")
    all_data=pd.concat(frames,ignore_index=True)
    if (len(all_data)!=2*2*4*128*12*2*3 or
        all_data.duplicated(ID).any() or
        set(all_data.scale)!={3,12}):
        raise AssertionError("Original q3 plus genuine q12 source factorial cannot be merged")
    return all_data,pd.DataFrame(event_records)


def audit(data,event_counts,out):
    key=[x for x in ID if x!="movement"]
    a=data[data.movement.eq("off")].set_index(key).sort_index()
    b=data[data.movement.eq("both")].set_index(key).sort_index()
    if not a.index.equals(b.index):
        raise AssertionError("Matched q3/q12 original source stage-plant seeds missing")
    dif=(b[list(FIELDS)]-a[list(FIELDS)]).add_prefix("delta_").reset_index()
    dif["context"]=dif.structure_id.str.split("__").str[0]
    dif["plant_model"]=dif.structure_id.str.split("__").str[-1]
    if len(dif)!=2*2*4*128*12*3:
        raise AssertionError("Original finite source movement ON/OFF matched comparisons lost")
    f=dif[dif.guild.eq("F")]
    blocks=(f.groupby(["scale","recruitment_regime","network_arm",
                       "plant_model","context","seed"],sort=True)
            [[f"delta_{name}" for name in FIELDS]]
            .mean().reset_index())
    if len(blocks)!=2*2*4*2*4*12:
        raise AssertionError("Twelve RNG seed source blocks per 2×4×2×4 cells incomplete")
    pv=blocks.pivot(index=["scale","recruitment_regime","network_arm","plant_model","seed"],
                    columns="context",values="delta_final_occupied_patches")
    if (len(pv)!=2*2*4*2*12 or
        set(pv.columns)!=set(CONTEXTS) or pv.isna().any().any()):
        raise AssertionError("Four source S growth × D aquatic cells lost")
    pv["growth_main"]=.5*(pv["S_growth_fast_only"]+pv["D_first_S_overtakes"]-
                          pv["original"]-pv["D_aquatic_long_only"])
    pv["strict_reversal_for_seed"]=(
        (pv["original"]>0)&(pv["D_aquatic_long_only"]>0)&
        (pv["S_growth_fast_only"]<0)&(pv["D_first_S_overtakes"]<0))
    pv=pv.reset_index()
    rng=np.random.default_rng(20261031)
    results=[]
    for (q,r,n,plant),g in pv.groupby(
        ["scale","recruitment_regime","network_arm","plant_model"],sort=True):
        g=g.sort_values("seed")
        if g.seed.tolist()!=list(ALL_SEEDS):
            raise AssertionError("Twelve independent simulated seed labels missing")
        vals=g[list(CONTEXTS)].mean()
        strict=bool(vals.original>0 and vals.D_aquatic_long_only>0 and
                    vals.S_growth_fast_only<0 and vals.D_first_S_overtakes<0)
        v=g.growth_main.to_numpy(float)
        bootstrap=v[rng.integers(0,12,size=(9999,12))].mean(axis=1)
        row=dict(scale=int(q),recruitment_regime=r,network_arm=n,plant_model=plant,
            n_independent_RNG_seed_labels=12,
            strict_sign_reversal_from_mean=bool(strict),
            n_seeds_strict_sign_reversal=int(g.strict_reversal_for_seed.sum()),
            growth_main_mean=float(v.mean()),
            growth_main_MC_lower=float(np.quantile(bootstrap,.025)),
            growth_main_MC_upper=float(np.quantile(bootstrap,.975)))
        row.update({"movement_delta_"+name:float(vals[name]) for name in CONTEXTS})
        results.append(row)
    results=pd.DataFrame(results)
    if len(results)!=2*2*4*2:
        raise AssertionError("Original q3 and q12 population stress condition output incomplete")
    summary=(results.groupby(["scale","recruitment_regime","network_arm"],sort=True)
             .agg(n_plant_roles_with_strict_reversal=("strict_sign_reversal_from_mean","sum"),
                  n_plant_roles=("plant_model","size"),
                  n_seed_strict_reversal_total=("n_seeds_strict_sign_reversal","sum"),
                  mean_growth_main=("growth_main_mean","mean"))
             .reset_index())
    if not summary.n_plant_roles.eq(2).all():
        raise AssertionError("Missing original two legal plant choices")
    levels=(data[data.guild.eq("F")].groupby(
        ["scale","recruitment_regime","network_arm","context","plant_model","movement"],
        sort=True)
        .agg(mean_final_occupied=("final_occupied_patches","mean"),
             pct_source_scenarios_zero=("final_occupied_patches",lambda x: 100*np.mean(np.asarray(x)==0)),
             pct_source_scenarios_full8=("final_occupied_patches",lambda x: 100*np.mean(np.asarray(x)==8)),
             mean_local_returns=("n_local_returns","mean"),
             mean_local_extinctions=("n_local_extinctions","mean"),
             n_source_scenarios=("seed","size"))
        .reset_index())
    scales=levels[levels.recruitment_regime.eq("rate12_rho0")].copy()
    out.mkdir(parents=True,exist_ok=True)
    for name,frame in (
        ("original_q3_genuine_q12_source_scenarios.csv.gz",data),
        ("population_q3_q12_same_source_movement_deltas.csv.gz",dif),
        ("population_q3_q12_seed_blocks.csv",blocks),
        ("population_q3_q12_2x2_growth_cells_per_seed.csv",pv),
        ("population_q3_q12_2x2_MC_intervals.csv",results),
        ("population_q3_q12_strict_reversal_counts.csv",summary),
        ("population_q3_q12_occupancy_and_saturation.csv",levels),
        ("q12_true_reoccupation_event_shard_counts.csv",event_counts),
    ):
        frame.to_csv(out/name,index=False,compression=(
            {"method":"gzip","mtime":0} if name.endswith(".gz") else None))
    receipt=dict(
        status="TRUE_80YEAR_Q3_VS_Q12_12SEED_SOURCE_VERIFIED_POPULATION_SCALE_AUDIT_SUCCESS",
        original_q3_source_reused_without_rerun=True,
        n_genuine_q12_source_shards=24,
        n_true_new_q12_integer_zero_to_positive_returns=int(event_counts.n_integer_zero_to_positive_events.sum()),
        n_original_and_new_source_guild_scenarios=int(len(data)),
        n_paired_movement_source_guild_contrasts=int(len(dif)),
        n_independent_rng_seed_labels_per_fixed_treatment=12,
        original_biological_seasonal_and_annual_kernels_unchanged=True,
        fitted_observed_field_population_size=False,
        wild_trophic_causal_inference=False,
    )
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    report=[
      "# frogcs original q3 → q12 finite-N sensitivity: conditional S→F predator necessity and sufficiency",
      "",
      "The original PR153 q3 source is immutable; all 24 additional q12 genuine"
      " original80-year source runs and all independent censor/mass tests must"
      " pass. q is a count scale, NOT a measured pond population size.",
      "",
      "## Q3 and Q12: strict 2×2 growth-dependent dispersal sign reversal",
      "",
      summary.to_markdown(index=False,floatfmt=".4f"),
      "",
      "## Two plant settings: stage-growth main effect and each source cell",
      "",
      results.to_markdown(index=False,floatfmt=".4f"),
      "",
      "## Actual F year80 occupancy and zero/eight patch floor-ceiling",
      "",
      scales.to_markdown(index=False,floatfmt=".4f"),
      "",
      "## Interpretation and uncertainty",
      "",
      "Each original q is an illustrative density-to-integer count mapping,"
      " altering stochastic demographic drift. This comparison has two"
      " highly selected original hypothetical biological rate backgrounds"
      " and fixed one movement rate .15, immigration OFF, 8 ring patches."
      " The four original S growth/D period contexts are NOT four independent"
      " seed replicates. Only 12 RNG seed labels per treatment. All"
      " Monte Carlo confidence bands are synthetic seed-resampling ranges,"
      " never field ecological causal effects or true biological parameter"
      " posteriors. A failure of strict sign reversal at q12 may result"
      " from population saturation/floor, and cannot prove disappearance"
      " of predation or dispersal in actual wetlands.",
    ]
    (out/"AUDITED_Q3_Q12_12SEED_FINDINGS.md").write_text(
       "\n".join(report)+"\n",encoding="utf-8")
    print("Q12_POPULATION_SCALE_AUDIT_RECEIPT",json.dumps(receipt),flush=True)
    print("Q12_STRICT_REVERSE_COUNTS\n"+summary.to_string(index=False),flush=True)
    print("Q12_PER_PLANT_STAGE_EFFECTS\n"+results.to_string(index=False),flush=True)
    print("Q12_F_LEVELS\n"+scales.to_string(index=False),flush=True)
    return summary,results,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--q3-source",type=Path,required=True)
    p.add_argument("--q12-shards",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    df,events=load_sources(args.q3_source,args.q12_shards)
    audit(df,events,args.out)
