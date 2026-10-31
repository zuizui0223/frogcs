"""Audit original PR150 draw0 and three NEW fixed synthetic biological rate draws.

All 80y finite-N source trajectories must exist (old12 for ID0, new 9
4seed shards for IDs 4/8/12). No source biology is rerun. Original
stage arrival days are IDENTICAL across contexts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import matching_prior_draws

RATE_IDS=(0,4,8,12)
ALL_SEEDS=tuple(range(101,113))
SEED_SHARDS=((101,102,103,104),(105,106,107,108),(109,110,111,112))
STAGES=("original","S_growth_fast_only","D_aquatic_long_only",
        "D_first_S_overtakes")
PLANTS=("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
GUILDS=("F","S","D")
MOVES=("off","both")
METRICS=("final_occupied_patches","n_local_returns","n_local_extinctions")
K=["draw","context","plant_model","reverse_on","vertex","seed","guild"]


def verify_load(original_dir,extra_root):
    source=original_dir/"source_new_and_old_12seed_conditions.csv.gz"
    if not source.exists():
        raise AssertionError("Missing complete original ID0 growth×duration source")
    o=pd.read_csv(source)
    if (len(o)!=9216 or set(o.draw)!={0} or set(o.seed)!=set(ALL_SEEDS)
        or set(o.context)!=set(STAGES)):
        raise AssertionError("Original rateID0 source from PR150 incomplete")
    folders=sorted(f for f in extra_root.iterdir() if f.is_dir() and
                   f.name.startswith("frogcs-growth-duration-rateprior-"))
    if len(folders)!=9:
        raise AssertionError("Nine genuinely executed 80y process-rate sources required")
    found=set()
    frames=[o]
    n_events=0
    for p in folders:
        r=json.loads((p/"receipt.json").read_text(encoding="utf-8"))
        did=r.get("fixed_256_LHS_rate_draw_id")
        seeds=tuple(r.get("independent_rng_seed_labels",[]))
        if (did not in RATE_IDS[1:] or seeds not in SEED_SHARDS or
            (did,seeds) in found):
            raise AssertionError("Unapproved or duplicated frozen rate/source seeds")
        found.add((did,seeds))
        if (r.get("status")!="TRUE_80Y_GROWTH_DURATION_FACTORIAL_BIOLOGICAL_PRIOR_STRESS"
            or r.get("model_horizon_years")!=80
            or r.get("n_source_eightcorner_model_units")!=128
            or r.get("population_scale")!=3
            or r.get("external_immigration") is not False
            or r.get("movement_fraction")!=.15
            or r.get("original_stage_arrival_days")!={"S":20,"D":0}):
            raise AssertionError("Rate source protocol changed")
        for k,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if r["original_rate_replay_errors"][k]>tol:
                raise AssertionError("Original 80year source not replayed")
        d=pd.read_csv(p/"rate_seed_scenario_guild_summary.csv.gz")
        e=pd.read_csv(p/"rate_true_reoccupation_events.csv.gz")
        if (len(d)!=128*4*2*3 or set(d.seed)!=set(seeds) or
            set(d.draw)!={did} or set(d.context)!=set(STAGES) or
            set(d.plant_model)!=set(PLANTS) or set(d.movement)!=set(MOVES) or
            d.duplicated(K+["movement"]).any() or
            not d.immigration.eq(0).all()):
            raise AssertionError("Rate stress biological source cases missing")
        if len(e)!=int(d.n_local_returns.sum()):
            raise AssertionError("Annual zero-to-positive return events and seed record mismatch")
        if e.cause_label.eq("unclassified").any():
            raise AssertionError("Unclassified movement/immigration/recruitment return")
        if int(d.n_recorded_migration_arrivals.sum())!=int(
            d.n_recorded_migration_departures.sum()):
            raise AssertionError("Closed synthetic landscape mass violated")
        n_events+=len(e)
        frames.append(d)
    if found!={(id,seed) for id in RATE_IDS[1:] for seed in SEED_SHARDS}:
        raise AssertionError("Incomplete rate-draw×12seed source matrix")
    full=pd.concat(frames,ignore_index=True)
    expected=4*4*2*2*8*12*2*3
    if (len(full)!=expected or full.duplicated(K+["movement"]).any()
        or set(full.draw)!=set(RATE_IDS) or set(full.seed)!=set(ALL_SEEDS)):
        raise AssertionError("Missing original+new complete 80y four-rate source factorial")
    return full,n_events


def analyze(full,new_events,out):
    off=full[full.movement.eq("off")].set_index(K).sort_index()
    both=full[full.movement.eq("both")].set_index(K).sort_index()
    if not off.index.equals(both.index):
        raise AssertionError("Fixed rate/source/seed movement ON/OFF mismatch")
    differences=(both[list(METRICS)]-off[list(METRICS)]).add_prefix("delta_").reset_index()
    seed_avg=(differences.groupby(["draw","context","plant_model","guild","seed"],sort=True)
              [[f"delta_{name}" for name in METRICS]].mean().reset_index())
    if len(seed_avg)!=4*4*2*3*12:
        raise AssertionError("Rate-source per-seed blocks missing")
    panel=seed_avg.pivot(index=["draw","plant_model","guild","seed"],
                         columns="context",values="delta_final_occupied_patches")
    if len(panel)!=4*2*3*12 or set(panel.columns)!=set(STAGES) or panel.isna().any().any():
        raise AssertionError("Missing rate-specific 2×2 source factorial corner")
    A=panel["original"]
    B=panel["S_growth_fast_only"]
    C=panel["D_aquatic_long_only"]
    D=panel["D_first_S_overtakes"]
    effects=pd.DataFrame(index=panel.index)
    effects["growth_at_Dshort"]=B-A
    effects["growth_at_Dlong"]=D-C
    effects["D_period_at_Sslow"]=C-A
    effects["D_period_at_Sfast"]=D-B
    effects["growth_main"]=.5*(B-A+D-C)
    effects["D_period_main"]=.5*(C-A+D-B)
    effects["factor_interaction"]=D-B-C+A
    effects["combined_minus_base"]=D-A
    effects=effects.reset_index()
    rng=np.random.default_rng(20261031)
    rows=[]
    for (draw,plant,guild),g in effects.groupby(["draw","plant_model","guild"],sort=True):
        if sorted(g.seed.tolist())!=list(ALL_SEEDS):
            raise AssertionError("Genuine 12seed rate source not complete")
        t=dict(draw=int(draw),plant_model=plant,guild=guild,independent_rng_seeds=12)
        for key in ("growth_main","D_period_main","factor_interaction",
                    "combined_minus_base"):
            a=g.sort_values("seed")[key].to_numpy(float)
            bs=a[rng.integers(0,12,size=(9999,12))].mean(axis=1)
            t[key+"_mean"]=float(a.mean())
            t[key+"_MC_lower"]=float(np.quantile(bs,.025))
            t[key+"_MC_upper"]=float(np.quantile(bs,.975))
            t[key+"_positive_seeds"]=int((a>0).sum())
            t[key+"_negative_seeds"]=int((a<0).sum())
        rows.append(t)
    summary=pd.DataFrame(rows)
    if len(summary)!=4*2*3:
        raise AssertionError("Missing frozen rate-draw conditional effects")

    means=(seed_avg.groupby(["draw","context","plant_model","guild"],sort=True)
           .agg(mean_movement_occupied=("delta_final_occupied_patches","mean"),
                mean_delta_returns=("delta_n_local_returns","mean"),
                mean_delta_extinctions=("delta_n_local_extinctions","mean"))
           .reset_index())
    f_means=means[means.guild.eq("F")].pivot(
        index=["draw","plant_model"],columns="context",values="mean_movement_occupied"
    ).reset_index()
    # A rate×plant 'reversal' is valid only if movement benefit is positive
    # in BOTH low-S-growth cells and negative in BOTH high-S-growth cells.
    f_means["growth_sign_reversal"]=(
        (f_means["original"]>0)&(f_means["D_aquatic_long_only"]>0)&
        (f_means["S_growth_fast_only"]<0)&(f_means["D_first_S_overtakes"]<0)
    )
    f_effect=summary[summary.guild.eq("F")].copy()
    counts=(f_means.groupby("draw").growth_sign_reversal
            .agg(["sum","count"]).reset_index())
    counts=counts.rename(columns={"sum":"plant_roles_with_growth_sign_reversal",
                                  "count":"tested_plant_roles"})
    if len(f_means)!=8 or len(f_effect)!=8:
        raise AssertionError("Rate×plant F stress incomplete")

    out.mkdir(parents=True,exist_ok=True)
    for name,df in (
        ("all_four_rate_12seed_original_source_guilds.csv.gz",full),
        ("matched_four_rate_80y_movement_effects.csv.gz",differences),
        ("four_rate_12seed_block_means.csv",seed_avg),
        ("four_rate_12seed_factor_contrasts.csv",effects),
        ("four_rate_12seed_factor_mc_intervals.csv",summary),
        ("four_rate_cell_movement_means.csv",means),
        ("four_rate_frog_growth_sign_reversal.csv",f_means),
        ("four_rate_reversal_count_by_draw.csv",counts),
    ):
        df.to_csv(out/name,index=False,
                  compression={"method":"gzip","mtime":0} if name.endswith(".gz") else None)
    prior=matching_prior_draws(256)
    prior=prior[prior.draw.isin(RATE_IDS)].sort_values("draw").reset_index(drop=True)
    if list(prior.draw)!=list(RATE_IDS) or len(prior)!=4:
        raise AssertionError("Frozen original source LHS rate vector identities changed")
    prior.to_csv(out/"exact_original_four_LHS_prior_rate_vectors.csv",index=False)
    main=f_effect[["draw","plant_model","growth_main_mean",
                   "growth_main_MC_lower","growth_main_MC_upper",
                   "D_period_main_mean","D_period_main_MC_lower",
                   "D_period_main_MC_upper","factor_interaction_mean"]]
    doc=[
        "# frogcs: 80-year growth × D aquatic duration across four hypothetical biological rate draws",
        "",
        "All true 80year source runs for previously fixed original ID0 and 3"
        " additional original-LHS rate draw IDs4,8,12 verified. Each rate"
        " has 12 independent seed labels but **four selected rate vectors"
        " are NOT a probability sample of field ecological rates**.",
        "",
        "## Exact growth sign inversion under fixed rate × plant source conditions",
        "",
        f_means.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Counts across 2 vegetation roles for each rate draw",
        "",
        counts.to_markdown(index=False),
        "",
        "## Main rate × plant conditional 2×2 effects (frog F, year80 occupancy)",
        "",
        main.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Original frozen hypothetical rate vectors used (NOT field estimates)",
        "",
        prior.to_markdown(index=False,floatfmt=".4f"),
        "",
        "Every contrast is movement ON−OFF, averaged over 2 predation reversal"
        " states and 8 fixed source factorial vertices. Bootstrap MC intervals"
        " resample only the 12 seed-block means per biological rate draw.",
        "S and D arrive at day 20 and day 0 in every factorial treatment."
        " Altered S growth and D aquatic duration are independent synthetic"
        " interventions on the original trophic source kernel.",
        "The model is still q=3, immigration OFF, 8 synthetic ring patches,"
        " annual movement fraction .15. No posterior over true field"
        " mechanisms, source density, climate or NAAMP calling is inferred.",
    ]
    (out/"AUDITED_FOUR_RATE_GROWTH_DURATION_FINDINGS.md").write_text(
        "\n".join(doc)+"\n",encoding="utf-8"
    )
    receipt=dict(status="FOUR_SOURCE_RATE_DRAWS_FULL_12SEED_GROWTH_DURATION_AUDITED",
        biological_rate_ids=list(RATE_IDS),
        independent_seed_labels_per_rate=12,
        n_verified_guild_scenario_results=len(full),
        n_movement_paired_results=len(differences),
        n_additional_true_return_events=new_events,
        n_rate_plant_conditions=int(len(f_means)),
        field_causal_inference=False)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("RATE_STRESS_SOURCE_AUDIT_SUCCESS",json.dumps(receipt),flush=True)
    print("FROG_RATE_CELL_MEANS\n"+f_means.to_string(index=False),flush=True)
    print("FROG_RATE_MAIN_EFFECTS\n"+main.to_string(index=False),flush=True)
    print("FROG_GROWTH_SIGN_REVERSAL_COUNT\n"+counts.to_string(index=False),flush=True)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--new9",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x,n=verify_load(a.original,a.new9)
    analyze(x,n,a.output)
