"""Audit true 80year F/S/D single directed predator-edge removals.

All 24 new source shards must succeed under original seasonal trophic
kernel. Baseline source for all five active edges is not rerun: it comes
from immutable PR151 original rateID12 and PR152 rho-to-ID0 12seed
source artifacts. FE is a proven source timing null, not an experiment.
No pseudo-replication: 12 independent RNG seed blocks per condition.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REGIMES=("rate12_base","rate12_rho0")
EDGES=("all_active","no_SF","no_DF","no_DS","no_SD")
ACTIVE_CODES=("SF","DF","DS","SD")
CONTEXTS=("original","S_growth_fast_only","D_aquatic_long_only",
          "D_first_S_overtakes")
PLANTS=("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
GUILDS=("F","S","D")
SEED_SHARDS=((101,102,103,104),(105,106,107,108),(109,110,111,112))
ALL_SEEDS=tuple(range(101,113))
N_EXPERIMENT_SOURCE_CELLS=128
METRICS=("final_occupied_patches","n_local_returns","n_local_extinctions",
         "n_3y_persistent_with_recruitment")
PAIR_KEYS=("recruitment_regime","edge_status","structure_id","draw",
           "reverse_on","vertex","seed","guild")

def original_baseline(rate12_source,rate12_rho_source):
    p0=rate12_source/"all_four_rate_12seed_original_source_guilds.csv.gz"
    p1=rate12_rho_source/"focal_old4_new8_original80_source.csv.gz"
    if not p0.exists() or not p1.exists():
        raise AssertionError("Missing genuine original 12seed/PR152 rate source")
    a=pd.read_csv(p0)
    b=pd.read_csv(p1)
    if (len(a)!=36864 or set(a.draw)!={0,4,8,12} or
        set(a.seed)!=set(ALL_SEEDS) or
        len(b)!=92160 or set(b.base_rate_id)!={0,12}):
        raise AssertionError("Original old biological 12seed source not complete")
    a=a[(a.draw==12)&(a.immigration==0)&a.scale.eq(3)&
        a.movement.isin(("off","both"))].copy()
    b=b[(b.base_rate_id==12)&b.swapped_axis.eq("rho")&
        b.immigration.eq(0)&b.scale.eq(3)&
        b.movement.isin(("off","both"))].copy()
    if len(a)!=N_EXPERIMENT_SOURCE_CELLS*12*2*3 or len(b)!=len(a):
        raise AssertionError("Baseline 80-year source exact two treatment counts missing")
    a["recruitment_regime"]="rate12_base"
    b["recruitment_regime"]="rate12_rho0"
    a["edge_status"]="all_active"
    b["edge_status"]="all_active"
    for t in (a,b):
        if (set(t.context)!=set(CONTEXTS) or
            set(t.plant_model)!=set(PLANTS) or
            set(t.seed)!=set(ALL_SEEDS) or
            set(t.reverse_on)!={0,1} or
            set(t.vertex)!=set(range(8))):
            raise AssertionError("Baseline plant×S growth×D period model incomplete")
    return pd.concat([a,b],ignore_index=True)


def load_all(pr151_dir,pr152_dir,shard_dir):
    baseline=original_baseline(pr151_dir,pr152_dir)
    dirs=sorted(x for x in shard_dir.iterdir() if x.is_dir() and
                x.name.startswith("frogcs-predator-edge-80y-"))
    if len(dirs)!=24:
        raise AssertionError(f"Need all 24 real 80y source shards, got {len(dirs)}")
    expected={(r,e,shard) for r in REGIMES for e in ACTIVE_CODES
              for shard in SEED_SHARDS}
    seen=set()
    added=[]
    events_by_case=[]
    for folder in dirs:
        receipt=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        regime=receipt.get("recruitment_regime")
        edge=receipt.get("single_ablation_removed_directed_edge")
        seeds=tuple(receipt.get("independent_seed_labels",[]))
        name=(regime,edge,seeds)
        if name not in expected or name in seen:
            raise AssertionError("Predeclared directed edge source case missing or duplicated")
        seen.add(name)
        if (receipt.get("status")!="TRUE_80YEAR_SINGLE_TROPHIC_EDGE_REMOVAL_FINITE_N"
            or receipt.get("base_256_LHS_rate_draw_id")!=12
            or receipt.get("F_completion_day")!=65
            or receipt.get("D_emergence_end_days")!=[45,65]
            or receipt.get("source_stage_plant_reverse_factors")!=128
            or receipt.get("years")!=80 or receipt.get("cohort_scale")!=3
            or receipt.get("annual_movement_fraction")!=.15
            or receipt.get("external_immigration") is not False
            or receipt.get("original_120day_biology_kernel_reused") is not True):
            raise AssertionError("Source control status or biology changed")
        for k,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if receipt["source_replay_differences"][k]>tol:
                raise AssertionError("Source unchanged seasonal+annual kernel replay failed")
        d=pd.read_csv(folder/"edge_original_seed_scenario_guilds.csv.gz")
        events=pd.read_csv(folder/"edge_true_0_to_positive_events.csv.gz")
        if (len(d)!=N_EXPERIMENT_SOURCE_CELLS*4*2*3 or
            not d.draw.eq(12).all() or not d.scale.eq(3).all() or
            not d.immigration.eq(0).all() or
            set(d.seed)!=set(seeds) or set(d.movement)!={"off","both"} or
            not d.recruitment_regime.eq(regime).all() or
            not d.edge_off.eq(edge).all() or
            set(d.context)!=set(CONTEXTS) or set(d.plant_model)!=set(PLANTS) or
            d.duplicated(["edge_off","structure_id","reverse_on","vertex",
                          "seed","movement","guild"]).any() or
            len(events)!=int(d.n_local_returns.sum())):
            raise AssertionError("True source model/seed/censoring/event data incomplete: "+str(name))
        if len(events) and events.cause_label.eq("unclassified").any():
            raise AssertionError("An event lacks a biological source category: "+str(name))
        if (int(d.n_recorded_migration_arrivals.sum())!=
            int(d.n_recorded_migration_departures.sum())):
            raise AssertionError("Stochastic dispersal did not conserve ring source mass")
        for f,z in (("n_3y_observable_returns","followup_3y_observable"),
                    ("n_3y_persistent_returns","occupied_three_followups"),
                    ("n_3y_persistent_with_recruitment","operational_3y_recruitment")):
            if int(d[f].sum())!=int(events[z].sum()):
                raise AssertionError("True three-year return / right censor denominator mismatch")
        d["edge_status"]="no_"+edge
        added.append(d)
        events_by_case.append(dict(recruitment_regime=regime,
                  edge_status="no_"+edge,
                  independent_seed_shard=",".join(map(str,seeds)),
                  n_events=len(events),
                  n_3y_followable=int(events.followup_3y_observable.sum()),
                  n_3y_persistent=int(events.occupied_three_followups.sum()),
                  n_3y_with_local_recruitment=int(events.operational_3y_recruitment.sum())))
    if seen!=expected:
        raise AssertionError("Not all four directed edges and both recruitment settings present")
    all_cases=pd.concat([baseline,*added],ignore_index=True)
    if (len(all_cases)!=2*5*128*12*2*3 or
        all_cases.duplicated(list(PAIR_KEYS)+["movement"]).any()):
        raise AssertionError("Combined original source + 24 80y ablations incomplete")
    # Source plant, stage and original biological prior draw matched across arms.
    for key,g in all_cases.groupby(
        ["recruitment_regime","edge_status","context","plant_model","guild","seed"],
        sort=True):
        if (len(g)!=2*2*8 or set(g.reverse_on)!={0,1} or
            set(g.vertex)!=set(range(8)) or
            set(g.movement)!={"off","both"}):
            raise AssertionError("Source eight-corner × F→D reverse flag unbalanced: "+str(key))
    return all_cases,pd.DataFrame(events_by_case)


def compute(all_cases,event_counts,out):
    source=list(PAIR_KEYS)
    a=all_cases[all_cases.movement.eq("off")].set_index(source).sort_index()
    b=all_cases[all_cases.movement.eq("both")].set_index(source).sort_index()
    if not a.index.equals(b.index):
        raise AssertionError("Movement source covariates not identical within ablation")
    deltas=(b[list(METRICS)]-a[list(METRICS)]).add_prefix("delta_").reset_index()
    deltas["context"]=deltas.structure_id.str.split("__").str[0]
    deltas["plant_model"]=deltas.structure_id.str.split("__").str[-1]
    blocks=(deltas[deltas.guild.eq("F")].groupby(
        ["recruitment_regime","edge_status","plant_model","context","seed"],sort=True)
        [[f"delta_{x}" for x in METRICS]].mean().reset_index())
    if len(blocks)!=2*5*2*4*12 or blocks.duplicated(
        ["recruitment_regime","edge_status","plant_model","context","seed"]).any():
        raise AssertionError("Source population edge model not complete for 12 independent seeds")
    pv=blocks.pivot(index=["recruitment_regime","edge_status","plant_model","seed"],
          columns="context",values="delta_final_occupied_patches")
    if (pv.shape!=(2*5*2*12,4) or
        set(pv.columns)!=set(CONTEXTS) or pv.isna().any().any()):
        raise AssertionError("Four source growth/period contexts not complete")
    pv["growth_main"]=.5*(pv["S_growth_fast_only"]+pv["D_first_S_overtakes"]-
                            pv["original"]-pv["D_aquatic_long_only"])
    pv["strict_reversal_for_seed"]=(
        pv["original"].gt(0)&pv["D_aquatic_long_only"].gt(0)&
        pv["S_growth_fast_only"].lt(0)&pv["D_first_S_overtakes"].lt(0))
    pv=pv.reset_index()
    rng=np.random.default_rng(20261031)
    results=[]
    for (regime,edge,plant),g in pv.groupby(
        ["recruitment_regime","edge_status","plant_model"],sort=True):
        g=g.sort_values("seed")
        if g.seed.tolist()!=list(ALL_SEEDS):
            raise AssertionError("Not 12 true seed labels in source edge×recruitment comparison")
        c=g[list(CONTEXTS)].to_numpy(float).mean(axis=0)
        m=dict(zip(CONTEXTS,c))
        strict=(m["original"]>0 and m["D_aquatic_long_only"]>0 and
                m["S_growth_fast_only"]<0 and m["D_first_S_overtakes"]<0)
        x=g.growth_main.to_numpy(float)
        boot=x[rng.integers(0,12,size=(9999,12))].mean(axis=1)
        row=dict(recruitment_regime=regime,edge_status=edge,plant_model=plant,
           n_genuine_rng_seed_blocks=12,
           strict_growth_sign_reversal_mean=bool(strict),
           n_seed_blocks_strict_reversal=int(g.strict_reversal_for_seed.sum()),
           growth_main_movement_effect=float(x.mean()),
           growth_main_95mc_lower=float(np.quantile(boot,.025)),
           growth_main_95mc_upper=float(np.quantile(boot,.975)))
        row.update({f"movement_delta_{k}":float(m[k]) for k in CONTEXTS})
        results.append(row)
    summary=pd.DataFrame(results)
    if len(summary)!=2*5*2:
        raise AssertionError("Missing source pathway×plant×recruitment condition")
    effects=(summary.groupby(["recruitment_regime","edge_status"],sort=True)
             .agg(n_strict_reversal_plant_roles=("strict_growth_sign_reversal_mean","sum"),
                  n_plant_roles=("plant_model","size"),
                  n_individual_seed_reversals=("n_seed_blocks_strict_reversal","sum"),
                  mean_growth_main=("growth_main_movement_effect","mean"))
             .reset_index())
    if not effects.n_plant_roles.eq(2).all():
        raise AssertionError("Plant factorial incomplete")
    # Compare each ablation with the true all-edge source on the same seed labels.
    idx=["recruitment_regime","plant_model","seed"]
    base=pv[pv.edge_status.eq("all_active")].set_index(idx).sort_index()
    compare=[]
    for edge in EDGES[1:]:
        candidate=pv[pv.edge_status.eq(edge)].set_index(idx).sort_index()
        if not candidate.index.equals(base.index):
            raise AssertionError("Original same biological source/seed ablation mismatch")
        d=(candidate[["growth_main"]]-base[["growth_main"]]).reset_index()
        d["ablated_edge"]=edge
        compare.append(d.rename(columns={"growth_main":"delta_growth_main_ablation_minus_all"}))
    contrasts=pd.concat(compare,ignore_index=True)
    if len(contrasts)!=2*2*12*4:
        raise AssertionError("Pathway vs intact source contrasts missing")

    out.mkdir(parents=True,exist_ok=True)
    for name,frame in (
        ("original_80year_source_edge_12seed_guilds.csv.gz",all_cases),
        ("movement_effect_edge12seed_frog_source.csv.gz",deltas),
        ("focal_12seed_growth_2x2_plant_contexts.csv",blocks),
        ("focal_12seed_2x2_reversal_per_seed.csv",pv),
        ("focal_12seed_2x2_reversal_mc_intervals.csv",summary),
        ("focal_12seed_predator_edge_status.csv",effects),
        ("focal_12seed_ablation_vs_intact_pairing.csv",contrasts),
        ("actual_reoccupation_source_shard_audit.csv",event_counts),
    ):
        frame.to_csv(out/name,index=False,compression=(
            {"method":"gzip","mtime":0} if name.endswith(".gz") else None))
    receipt=dict(
        status="TRUE_24_ORIGINAL_80Y_EDGE_ABLATIONS_AND_BOTH_RECRUITMENT_CONTEXTS_AUDIT_SUCCESS",
        active_directed_edges=list(ACTIVE_CODES),
        biologically_structurally_inactive_FE_edge=True,
        population_years=80,
        synthetic_scale=3,external_immigration=False,
        n_independent_seed_labels=12,
        n_actual_source_guild_records=int(len(all_cases)),
        n_paired_movement_source_cases=int(len(deltas)),
        n_original_truly_new_single_edge_shards=24,
        n_true_new_0_to_positive_returns=int(event_counts.n_events.sum()),
        fitted_wild_predation_rates=False,
        seed_multiregion_replication=False,
    )
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    report=[
        "# frogcs: 80-year 4 active trophic edges ×2 local recruitments, true 12seed audit",
        "",
        "**Original PR146 seasonal hazard and PR149–152 demographic model unchanged**."
        " Four source-directed edges individually disabled in the original"
        " model; no field trophic rates inferred. 24 TRUE new original80y"
        " source runs passed source replay, migration conservation and the"
        " original integer 0→positive event right-censor denominators.",
        "",
        "The F-completed→D-emerging reverse predation FE is an exact structural"
        " timing-null in this source because F finishes at day65 while D"
        " emergence ends on day45 or65. It CANNOT explain source stage"
        " or dispersal conclusions; PR147's separate ABM reverse predation"
        " must not be interchanged with this source.",
        "",
        "## All four active predation removals, two recruitment backgrounds",
        "",
        effects.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Twelve-seed per-plant F stage-growth rescue patterns",
        "",
        summary.to_markdown(index=False,floatfmt=".3f"),
        "",
        "An edge removal changing the sign of the dispersal effect is a"
        " model-native intervention that also changes future predator"
        " densities and competition. It does NOT identify an additive"
        " independent causal contribution or a field effect.",
        "",
        "## Inference ceilings",
        "",
        "F growth/timing, source biology and rho×conversion recruitment product"
        " are predeclared. This is only one q=3 synthetic population scale,"
        " two arbitrarily selected rate backgrounds, synthetic annual"
        " mobility .15, closed 8 patch ring, two legal plant roles,"
        " and 12 Monte Carlo seed labels. No independent wild pond evidence.",
    ]
    (out/"AUDITED_TROPHIC_EDGES_RECRUITMENT_12SEED_RESULTS.md").write_text(
       "\n".join(report)+"\n",encoding="utf-8")
    print("PREDATOR_EDGE_SOURCE_AUDIT_RECEIPT",json.dumps(receipt),flush=True)
    print("PREDATOR_EDGE_STRICT_REVERSAL_COUNTS\n"+effects.to_string(index=False),flush=True)
    print("PREDATOR_EDGE_PLANT_STAGE_CONTEXT\n"+summary.to_string(index=False),flush=True)
    return effects,summary,receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--pr151",type=Path,required=True)
    p.add_argument("--pr152",type=Path,required=True)
    p.add_argument("--new-shards",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    df,events=load_all(a.pr151,a.pr152,a.new_shards)
    compute(df,events,a.out)
