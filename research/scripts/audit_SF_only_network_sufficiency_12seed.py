"""Full original biology 80y 12seed necessity+single-path sufficiency check.

Reuses immutable PR153 all-active, each-one-removed sources. Adds only
the genuinely new 12seed SF-only and no-direct-predation source outputs.
The FE edge is source-proven null for these two D0,F20 contexts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

REGIMES=("rate12_base","rate12_rho0")
NEW_ARMS=("SF_only","no_direct_predation")
ALL_ARMS=("all_active","no_SF","no_DF","no_DS","no_SD",
          "SF_only","no_direct_predation")
SEED_SHARDS=((101,102,103,104),(105,106,107,108),(109,110,111,112))
SEEDS=tuple(range(101,113))
PLANTS=("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
STAGES=("original","S_growth_fast_only","D_aquatic_long_only",
        "D_first_S_overtakes")
FIELDS=("final_occupied_patches","n_local_returns",
        "n_local_extinctions","n_3y_persistent_with_recruitment")
MODEL_KEYS=["recruitment_regime","network_arm","structure_id","reverse_on",
            "vertex","seed","guild","movement"]


def load_source(necessity_dir,new_dir):
    oldpath=necessity_dir/"original_80year_source_edge_12seed_guilds.csv.gz"
    if not oldpath.exists():
        raise AssertionError("Original independently audited 12seed necessity source not found")
    old=pd.read_csv(oldpath)
    if (len(old)!=2*5*128*12*2*3 or set(old.edge_status)!=set(ALL_ARMS[:5])
        or set(old.recruitment_regime)!=set(REGIMES) or
        set(old.seed)!=set(SEEDS)):
        raise AssertionError("Existing 12seed source changed")
    old["network_arm"]=old.edge_status
    shards=sorted(p for p in new_dir.iterdir() if p.is_dir() and
                  p.name.startswith("frogcs-SF-suff-80y-"))
    if len(shards)!=12:
        raise AssertionError("Required 12 new genuine 80y sufficiency source shards")
    expected={(r,a,part) for r in REGIMES for a in NEW_ARMS
              for part in SEED_SHARDS}
    seen=set()
    frames=[old];source_events=0
    for folder in shards:
        rec=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        regime=rec.get("recruitment_regime"); arm=rec.get("network_arm")
        seeds=tuple(rec.get("independent_seed_labels",[]))
        if (regime,arm,seeds) not in expected or (regime,arm,seeds) in seen:
            raise AssertionError("Unapproved or repeated post-hoc sufficiency seed shard")
        seen.add((regime,arm,seeds))
        if (rec.get("status")!="TRUE_80YEAR_SF_ONLY_VS_ALL_DIRECT_PREDATORS_OFF_SOURCE"
            or rec.get("original_biological_prior_draw")!=12
            or rec.get("year_horizon")!=80 or
            rec.get("synthetic_N_scale")!=3 or
            rec.get("source_ring_patches")!=8 or
            rec.get("external_immigration") is not False or
            rec.get("both_recruits_and_survivors_annual_movement_fraction")!=.15 or
            rec.get("n_synthetic_model_corners")!=128 or
            rec.get("active_directed_predation_edges")!=(
                ["SF"] if arm=="SF_only" else [])):
            raise AssertionError("Original recruitment/source design changed in sufficiency run")
        for metric,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if rec["source_replay"][metric]>tol:
                raise AssertionError("Original biological source did not replay")
        frame=pd.read_csv(folder/"sufficiency_original_seed_scenario_guilds.csv.gz")
        events=pd.read_csv(folder/"sufficiency_true_0_to_positive_events.csv.gz")
        if (len(frame)!=128*4*2*3 or
            set(frame.seed)!=set(seeds) or
            set(frame.movement)!={"off","both"} or
            set(frame.context)!=set(STAGES) or
            set(frame.plant_model)!=set(PLANTS) or
            not frame.recruitment_regime.eq(regime).all() or
            not frame.network_arm.eq(arm).all() or
            not frame.immigration.eq(0).all() or
            len(events)!=int(frame.n_local_returns.sum())):
            raise AssertionError("True 80y SF-only finite-N source/returns missing")
        if (int(frame.n_recorded_migration_arrivals.sum())!=
            int(frame.n_recorded_migration_departures.sum())):
            raise AssertionError("Closed spatial ring not population conservative")
        if len(events) and events.cause_label.eq("unclassified").any():
            raise AssertionError("Unknown source of integer local reoccupation")
        for f,e in (("n_3y_observable_returns","followup_3y_observable"),
                    ("n_3y_persistent_with_recruitment","operational_3y_recruitment")):
            if int(frame[f].sum())!=int(events[e].sum()):
                raise AssertionError("Right-censoring/interval denominator mismatch")
        source_events+=len(events)
        frames.append(frame)
    if seen!=expected:
        raise AssertionError("Incomplete genuine independent source RNG conditions")
    data=pd.concat(frames,ignore_index=True)
    if (len(data)!=2*7*128*12*2*3 or
        data.duplicated(MODEL_KEYS).any() or
        set(data.network_arm)!=set(ALL_ARMS)):
        raise AssertionError("Missing or repeated necessity/sufficiency biological scenario")
    return data,source_events


def analyze(data,new_events,out):
    keys=["recruitment_regime","network_arm","structure_id","reverse_on",
          "vertex","seed","guild"]
    off=data[data.movement.eq("off")].set_index(keys).sort_index()
    on=data[data.movement.eq("both")].set_index(keys).sort_index()
    if not off.index.equals(on.index):
        raise AssertionError("No original matched treatment-specific dispersal source")
    d=(on[list(FIELDS)]-off[list(FIELDS)]).add_prefix("delta_").reset_index()
    d["context"]=d.structure_id.str.split("__").str[0]
    d["plant_model"]=d.structure_id.str.split("__").str[-1]
    block=(d[d.guild.eq("F")].groupby(
        ["recruitment_regime","network_arm","plant_model","context","seed"],sort=True)
        [[f"delta_{name}" for name in FIELDS]].mean().reset_index())
    if len(block)!=2*7*2*4*12:
        raise AssertionError("Missing original 12seed source 2×2 stage factorial")
    p=block.pivot(
       index=["recruitment_regime","network_arm","plant_model","seed"],
       columns="context",values="delta_final_occupied_patches")
    if len(p)!=2*7*2*12 or set(p.columns)!=set(STAGES) or p.isna().any().any():
        raise AssertionError("Incomplete fixed source network×plant stage conditions")
    p["growth_main"]=.5*(
        p["S_growth_fast_only"]+p["D_first_S_overtakes"]-
        p["original"]-p["D_aquatic_long_only"])
    p["strict_for_seed"]=(
        (p["original"]>0)&(p["D_aquatic_long_only"]>0)&
        (p["S_growth_fast_only"]<0)&(p["D_first_S_overtakes"]<0))
    p=p.reset_index()
    rng=np.random.default_rng(20261031)
    rows=[]
    for (r,arm,plant),g in p.groupby(
        ["recruitment_regime","network_arm","plant_model"],sort=True):
        g=g.sort_values("seed")
        if g.seed.tolist()!=list(SEEDS):
            raise AssertionError("Missing independent twelve source Monte Carlo seeds")
        m=g[list(STAGES)].mean()
        strict=(m.original>0 and m.D_aquatic_long_only>0 and
                m.S_growth_fast_only<0 and m.D_first_S_overtakes<0)
        a=g.growth_main.to_numpy(float)
        b=a[rng.integers(0,12,size=(9999,12))].mean(axis=1)
        row=dict(recruitment_regime=r,network_arm=arm,plant_model=plant,
            n_independent_rng_seeds=12,
            strict_reversal_mean=bool(strict),
            n_seed_blocks_strict=int(g.strict_for_seed.sum()),
            growth_main=float(a.mean()),
            growth_main_MC_lower=float(np.quantile(b,.025)),
            growth_main_MC_upper=float(np.quantile(b,.975)))
        row.update({"movement_delta_"+col:float(m[col]) for col in STAGES})
        rows.append(row)
    s=pd.DataFrame(rows)
    if len(s)!=2*7*2:
        raise AssertionError("Incomplete source direct-predator network conditions")
    cnt=(s.groupby(["recruitment_regime","network_arm"],sort=True)
         .agg(n_plant_roles_with_reversal=("strict_reversal_mean","sum"),
              n_plant_roles=("plant_model","size"),
              n_rng_seed_blocks_with_reversal=("n_seed_blocks_strict","sum"),
              mean_S_growth_modifier=("growth_main","mean"))
         .reset_index())
    if not cnt.n_plant_roles.eq(2).all():
        raise AssertionError("Missing original plant functions")

    out.mkdir(parents=True,exist_ok=True)
    for name,t in (
        ("original_12seed_all_networks_guilds.csv.gz",data),
        ("original_12seed_all_networks_movement_deltas.csv.gz",d),
        ("original_12seed_all_networks_frog_seed_blocks.csv",block),
        ("original_12seed_all_networks_frog_2x2_contexts.csv",p),
        ("original_12seed_all_networks_frog_context_mc_intervals.csv",s),
        ("original_12seed_all_networks_strict_reversal_counts.csv",cnt),
    ):
        t.to_csv(out/name,index=False,compression=(
            {"method":"gzip","mtime":0} if name.endswith(".gz") else None))
    report=[
        "# Frogcs true80y: is S→F predation alone sufficient for stage-growth-dependent dispersal reversal?",
        "",
        "This secondary test was specified AFTER the four separate"
        " edge-deletion necessity screen. It pairs all old 12seed untouched"
        " model output with 12 new true80y source SF-only and direct-predation"
        " OFF arms across two recruitment contexts. The source original"
        " F→emerging D edge remains temporally zero in this subset.",
        "",
        "## All network outcomes — strict four-cell source stage criterion",
        "",
        cnt.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Plant-specific source effects and 12 independent RNG blocks",
        "",
        s.to_markdown(index=False,floatfmt=".4f"),
        "",
        "Under both recruitment backgrounds, edge removal affects subsequent"
        " predator abundances. SF-only is a *within-model* sufficiency"
        " intervention in the presence of all original recruitment and"
        " finite-cohort stochastic assumptions, not empirical causal proof.",
        "No-predation controls may have tiny nonzero estimated differences"
        " from RNG fluctuations across biological context labels, even"
        " though with all directed trophic hazards OFF frog completion does"
        " not biologically depend on S growth. Interpret zero-near"
        " numerical sign patterns using 12seed MC intervals, not just"
        " strict sign logic.",
    ]
    (out/"AUDITED_12SEED_SF_ONLY_SUFFICIENCY_RESULT.md").write_text(
        "\n".join(report)+"\n",encoding="utf-8")
    receipt=dict(status="TRUE_80Y_12SEED_SF_ONLY_SUFFICIENCY_AND_NO_PREDATION_AUDIT_SUCCESS",
        independent_seed_labels=12,
        n_genuine_new_80year_source_shards=12,
        n_original_source_guild_rows=int(len(data)),
        n_same_source_movement_contrasts=int(len(d)),
        new_true_integer_return_events=int(new_events),
        old_five_network_cases_reused=True,
        sole_SF_vs_no_direct_predation_biological_source_true=True,
        field_causality_or_universal_sufficiency=False)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("SF_SUFFICIENCY_SOURCE_AUDIT_RECEIPT",json.dumps(receipt),flush=True)
    print("SF_SUFFICIENCY_SOURCE_REVERSAL_COUNTS\n"+cnt.to_string(index=False),flush=True)
    print("SF_SUFFICIENCY_SOURCE_PLANT_CONDITIONS\n"+s.to_string(index=False),flush=True)
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--necessity-source",type=Path,required=True)
    p.add_argument("--sufficiency-shards",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data,new_events=load_source(args.necessity_source,args.sufficiency_shards)
    analyze(data,new_events,args.out)
