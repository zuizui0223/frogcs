"""Audit the original/combined stage model with two NEW single-factor source runs.

This is an actual 2x2 controlled intervention on S growth and D aquatic
duration. The original and joint-changed arms use the SAME verified old12
PR149 source file, not new runs. The single-factor cells come from THREE
independent successful 4seed 80year Actions shards, with no missing sources.
Only 12 RNG seed labels are independent Monte Carlo replicates.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

CONTEXTS=("original","S_growth_fast_only",
          "D_aquatic_long_only","D_first_S_overtakes")
PLANT_ROLES=("SF1_DF0_DS0_L1","SF0_DF0_DS1_L0")
SEEDS=tuple(range(101,113))
GUILDS=("F","S","D")
METRICS=("final_occupied_patches","n_local_returns",
         "n_local_extinctions","n_3y_persistent_with_recruitment")
REPLAY_TOLERANCES={"F_B":1e-8,"F_fraction":1e-8,"F_B_sd":1e-7}
INDEX=["context","plant_model","reverse_on","vertex","seed","guild"]
K=["context","plant_model","reverse_on","vertex","seed","guild","movement"]

def combine(old_dir,new_root):
    # Existing genuine 12seed source, not a synthetic summary recreated from a headline.
    p=old_dir/"all_12seed_source_guild_conditions.csv.gz"
    if not p.exists():
        raise AssertionError("Missing source-verified original and joint-growth/duration arms")
    old=pd.read_csv(p)
    if len(old)!=18432 or set(old.seed)!=set(SEEDS):
        raise AssertionError("Old 12seed source changed")
    old=old[(old.scale==3)&(old.immigration==0)&
            old.context.isin(("original","D_first_S_overtakes"))&
            old.movement.isin(("off","both"))].copy()
    if len(old)!=4608:
        raise AssertionError("Frozen old 2 timing arms are not complete")

    folders=sorted(x for x in new_root.iterdir() if x.is_dir() and
                   x.name.startswith("frogcs-growth-duration-80y-seeds"))
    if len(folders)!=3:
        raise AssertionError("Three successful outcome-blind new-source seed shards required")
    expected={(101,102,103,104),(105,106,107,108),(109,110,111,112)}
    got=set()
    new=[]
    for folder in folders:
        r=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        seeds=tuple(r.get("seed_labels",[]))
        if seeds not in expected or seeds in got:
            raise AssertionError("New source seed labels missing or duplicated")
        got.add(seeds)
        if (r.get("status")!="TRUE_SOURCE_80Y_STAGE_GROWTH_VS_D_DURATION_FACTORIAL_HYBRIDS"
            or r.get("years")!=80 or r.get("scale")!=3 or
            r.get("external_immigration") is not False or
            r.get("movement_fraction")!=.15 or
            r.get("source_arrival_days")!={"D":0,"S":20} or
            r.get("source_n_factorial_model_corners")!=64):
            raise AssertionError("New factorial source/arrival model changed")
        for label,tol in REPLAY_TOLERANCES.items():
            if r["replay"][label]>tol:
                raise AssertionError("New isolated source replay failed: "+label)
        a=pd.read_csv(folder/"hybrid_seed_scenario_guild_summary.csv.gz")
        e=pd.read_csv(folder/"hybrid_reoccupation_followup_events.csv.gz")
        if (len(a)!=64*len(seeds)*2*3 or
            a.duplicated(K).any() or
            set(a.context)!={"S_growth_fast_only","D_aquatic_long_only"} or
            set(a.seed)!=set(seeds) or
            set(a.plant_model)!=set(PLANT_ROLES) or
            not a.draw.eq(0).all() or
            not a.immigration.eq(0).all() or
            not a.scale.eq(3).all()):
            raise AssertionError("New one-factor source returns wrong set")
        if int(a.n_local_returns.sum())!=len(e) or e.cause_label.eq("unclassified").any():
            raise AssertionError("New 0→positive event ledger incomplete")
        new.append(a)
    if got!=expected:
        raise AssertionError("Exactly 12 new-seed source replicates required")
    full=pd.concat([old,*new],ignore_index=True)
    if (len(full)!=4*2*2*8*12*2*3 or
        full.duplicated(K).any() or
        set(full.context)!=set(CONTEXTS) or
        not full.draw.eq(0).all()):
        raise AssertionError("Missing model × factorial growth/period × 12 seeds")
    for (context,role,reversal,seed,guild),g in full.groupby(
            ["context","plant_model","reverse_on","seed","guild"]):
        if len(g)!=16 or set(g.vertex)!={0,1,2,3,4,5,6,7} or set(g.movement)!={"off","both"}:
            raise AssertionError("Source F/S/D×8 factorial treatment missing at "+context)
    return full

def analyze(full,out):
    a=full[full.movement.eq("off")].set_index(INDEX).sort_index()
    b=full[full.movement.eq("both")].set_index(INDEX).sort_index()
    if not a.index.equals(b.index):
        raise AssertionError("Original source/cell/seed comparison cannot be paired")
    deltas=(b[list(METRICS)]-a[list(METRICS)]).add_prefix("delta_").reset_index()
    # Biological 2x2 model cells remain fixed within each seed; 16
    # reverse×site factorial choices are NOT 16 independent RNG draws.
    blocks=(deltas.groupby(["context","plant_model","guild","seed"],sort=True)
            [[f"delta_{v}" for v in METRICS]].mean().reset_index())
    if len(blocks)!=4*2*3*12:
        raise AssertionError("Missing independent-seed conditional 2×2 blocks")
    # By explicit matrix contrast: changing S growth or D hydroperiod
    # while holding all other source processes fixed.
    pivots={}
    for metric in METRICS:
        z=blocks.pivot(index=["plant_model","guild","seed"],
                       columns="context",values="delta_"+metric)
        if list(sorted(z.columns))!=list(sorted(CONTEXTS)) or len(z)!=2*3*12:
            raise AssertionError("Mismatched fixed-factor stages")
        pivots[metric]=z
    x=pivots["final_occupied_patches"]
    base=x["original"]
    growth=x["S_growth_fast_only"]
    duration=x["D_aquatic_long_only"]
    combined=x["D_first_S_overtakes"]
    contrasts=pd.DataFrame(index=x.index)
    contrasts["growth_at_shortD"]=growth-base
    contrasts["growth_at_longD"]=combined-duration
    contrasts["duration_at_slowS"]=duration-base
    contrasts["duration_at_fastS"]=combined-growth
    contrasts["growth_main_mean"]=.5*(contrasts.growth_at_shortD+contrasts.growth_at_longD)
    contrasts["duration_main_mean"]=.5*(contrasts.duration_at_slowS+contrasts.duration_at_fastS)
    contrasts["interaction"]=combined-growth-duration+base
    contrasts["joint_minus_base"]=combined-base
    contrasts=contrasts.reset_index()
    rng=np.random.default_rng(20261031)
    lines=[]
    for (plant,guild),q in contrasts.groupby(["plant_model","guild"],sort=True):
        if sorted(q.seed.tolist())!=list(SEEDS):
            raise AssertionError("No 12 independent-seed stage-factor pairing")
        r=dict(plant_model=plant,guild=guild,independent_rng_seeds=12)
        q=q.sort_values("seed")
        for val in ("growth_at_shortD","growth_at_longD","duration_at_slowS",
                    "duration_at_fastS","growth_main_mean","duration_main_mean",
                    "interaction","joint_minus_base"):
            v=q[val].to_numpy(float)
            boots=v[rng.integers(0,12,size=(9999,12))].mean(axis=1)
            r[val+"_mean"]=float(v.mean())
            r[val+"_95mc_lower"]=float(np.quantile(boots,.025))
            r[val+"_95mc_upper"]=float(np.quantile(boots,.975))
            r[val+"_n_seed_positive"]=int((v>0).sum())
            r[val+"_n_seed_negative"]=int((v<0).sum())
            r[val+"_n_seed_zero"]=int((v==0).sum())
        lines.append(r)
    factors=pd.DataFrame(lines)
    if len(factors)!=2*3:raise AssertionError("Incomplete 2x2 mechanism contrasts")

    rng2=np.random.default_rng(20261031)
    level=[]
    for (context,plant,guild),q in blocks.groupby(
            ["context","plant_model","guild"],sort=True):
        if len(q)!=12: raise AssertionError("Missing 12seed context level")
        vals=q.sort_values("seed")["delta_final_occupied_patches"].to_numpy(float)
        boots=vals[rng2.integers(0,12,size=(9999,12))].mean(axis=1)
        level.append(dict(context=context,plant_model=plant,guild=guild,
            n_independent_seeds=12,
            movement_effect_mean=float(vals.mean()),
            movement_effect_MC_lower=float(np.quantile(boots,.025)),
            movement_effect_MC_upper=float(np.quantile(boots,.975)),
            n_seed_positive=int((vals>0).sum()),
            n_seed_negative=int((vals<0).sum()),
            n_seed_zero=int((vals==0).sum())))
    levels=pd.DataFrame(level)
    if len(levels)!=4*2*3:raise AssertionError("Lost treatment effects")

    out.mkdir(parents=True,exist_ok=True)
    for name,frame in (
        ("source_new_and_old_12seed_conditions.csv.gz",full),
        ("matched_movement_source_effects.csv.gz",deltas),
        ("seed_block_2x2_context_effects.csv",blocks),
        ("seed_block_2x2_mechanism_contrasts.csv",contrasts),
        ("12seed_2x2_mechanism_mc_intervals.csv",factors),
        ("12seed_2x2_cell_mc_intervals.csv",levels),
    ):
        compression={"method":"gzip","mtime":0} if name.endswith(".gz") else None
        frame.to_csv(out/name,index=False,compression=compression)
    table=levels[levels.guild.eq("F")][[
        "plant_model","context","movement_effect_mean",
        "movement_effect_MC_lower","movement_effect_MC_upper",
        "n_seed_positive","n_seed_negative","n_seed_zero"]]
    factor_f=factors[factors.guild.eq("F")][[
        "plant_model","growth_main_mean_mean","growth_main_mean_95mc_lower",
        "growth_main_mean_95mc_upper","duration_main_mean_mean",
        "duration_main_mean_95mc_lower","duration_main_mean_95mc_upper",
        "interaction_mean","interaction_95mc_lower","interaction_95mc_upper"]]
    report=[
        "# frogcs: S growth × D aquatic exposure duration 2×2 causal-model ablation",
        "",
        "**Both original/source alternatives have D arrival day 0 and S arrival"
        " day 20. Therefore the prior contrast does NOT isolate arrival order.**",
        "",
        "Two newly simulated single-change arms have been combined with the"
        " original 12-seed PR149 biological source (no original runs repeated)."
        " Original 120-day trophic kernel and delayed 80-year recruitment source"
        " replay passed; q3, no external immigration, year80, transport fraction .15.",
        "",
        "## Frog end-of-year80 occupancy movement effect: both movement vs none",
        "",
        table.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Within-model main effects and two-factor interaction",
        "",
        "Positive stage-factor coefficient changes the **movement-associated**"
        " year80 occupied-patch response. It is not a direct growth effect on"
        " population size nor a field-colonization effect.",
        "",
        factor_f.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Interpretation boundaries",
        "",
        "The individual growth×duration cells are interventions on the numerical"
        " source model, not observed stage ratios. Main-factor averages are"
        " across two fixed growth/period levels; the interaction explicitly"
        " measures their nonadditivity. Source rate draw ID0, two plant roles,"
        " eight synthetic ring patches, 12 independent RNG seed labels and"
        " uncalibrated biological transfer rate 0.15 limit generalization.",
        "All Monte Carlo 95% intervals resample the **12 seed block means**, not"
        " the 16 source factorial cells, 8 patches or repeated return events.",
        "No NAAMP acoustic observation or field predator density bridge is fitted.",
    ]
    (out/"AUDITED_12SEED_GROWTH_DURATION_RESULT.md").write_text(
        "\n".join(report)+"\n",encoding="utf-8")
    receipt=dict(status="FULL_2x2_GROWTH_DURATION_SOURCE_LOCKED_12SEED_AUDIT_SUCCESS",
                 original_source_conditions=2,new_single_factor_conditions=2,
                 n_total_seeds=12,n_source_condition_guild_rows=int(len(full)),
                 n_movement_paired_rows=int(len(deltas)),
                 original_stage_arrival_days={"D":0,"S":20},
                 no_field_causal_inference=True)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("GROWTH_DURATION_AUDIT_RECEIPT",json.dumps(receipt),flush=True)
    print("FOCAL_F_CELLS\n"+table.to_string(index=False),flush=True)
    print("FOCAL_F_MAIN_AND_INTERACTION\n"+factor_f.to_string(index=False),flush=True)
    return levels,factors,receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--old12",type=Path,required=True)
    p.add_argument("--new3",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    analyze(combine(args.old12,args.new3),args.output)
