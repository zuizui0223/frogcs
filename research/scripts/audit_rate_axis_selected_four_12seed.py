"""Exact 4 old + 8 new independent RNG-seed audit for FOUR post-pilot rate axes.

No model simulation or ecological fitting. All four axes were selected after
inspection of the complete eight-axis 4seed screen. Numerical replication on
new seeds does NOT repair biological parameter-selection dependence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ALL_SEEDS=tuple(range(101,113))
BASES=(0,12)
FOCUS=("attack_scale","conversion","rho","f_adult_survival")
NEW_GROUPS=((105,106,107,108),(109,110,111,112))
CASES=("original","D_aquatic_long_only","S_growth_fast_only",
       "D_first_S_overtakes")
PLANTS=("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
MOBILITY=("off","both")
GUILDS=("F","S","D")
KEY=["base_rate_id","swapped_axis","structure_id","reverse_on","vertex",
     "seed","guild","movement"]
READOUTS=("final_occupied_patches","n_local_returns","n_local_extinctions",
          "n_3y_persistent_with_recruitment")


def verify_and_load(base12,original4,new8):
    source=pd.read_csv(base12/"all_four_rate_12seed_original_source_guilds.csv.gz")
    if (len(source)!=36864 or set(source.draw)!={0,4,8,12} or
        set(source.seed)!=set(ALL_SEEDS)):
        raise AssertionError("Original complete 12seed 4rate PR151 source missing")
    base=source[source.draw.isin(BASES)].copy()
    base["base_rate_id"]=base.draw.astype(int)
    base["swapped_axis"]="BASE_NO_RATE_CHANGE"
    if len(base)!=2*4*2*2*8*12*2*3:
        raise AssertionError("Original verified rate endpoints missing")

    first=pd.read_csv(original4/"all_true_source_fourseed_rate_axis_guilds.csv.gz")
    if len(first)!=55296 or set(first.seed)!={101,102,103,104}:
        raise AssertionError("Original 16-swap full 4seed source is missing or mutated")
    initial_baseline=first[first.swapped_axis.eq("BASE_NO_RATE_CHANGE")]
    comparison=base[base.seed.isin((101,102,103,104))]
    sortcols=["base_rate_id","structure_id","reverse_on","vertex",
              "seed","movement","guild"]
    a=initial_baseline.sort_values(sortcols).reset_index(drop=True)
    b=comparison.sort_values(sortcols).reset_index(drop=True)
    if (len(a)!=len(b) or
        not a[sortcols].equals(b[sortcols]) or
        not np.array_equal(a[list(READOUTS)].to_numpy(float),
                           b[list(READOUTS)].to_numpy(float))):
        raise AssertionError("Original four source seeds do not replay untouched source PR151")

    first=first[first.swapped_axis.isin(FOCUS)].copy()
    if len(first)!=8*4*2*2*8*4*2*3:
        raise AssertionError("Cannot reuse full original four seeds for all eight focus interventions")

    shards=sorted(d for d in new8.iterdir()
                  if d.is_dir() and d.name.startswith("frogcs-rate-axis-add8-"))
    if len(shards)!=16:
        raise AssertionError(f"Expected exactly 16 new true80y source shards, found {len(shards)}")
    seen=set();new=[]; events_count=0
    for d in shards:
        receipt=json.loads((d/"receipt.json").read_text(encoding="utf-8"))
        base_id=receipt.get("base_rate_id")
        axis=receipt.get("changed_original_LHS_axis")
        seeds=tuple(receipt.get("random_seed_labels",[]))
        label=(base_id,axis,seeds)
        if (base_id not in BASES or axis not in FOCUS or seeds not in NEW_GROUPS or
            label in seen):
            raise AssertionError("An unapproved, overlapping or missing new RNG source shard")
        seen.add(label)
        if (receipt.get("status")!="ORIGINAL_80Y_PROCESS_RATE_SINGLE_AXIS_SWAP_TRUE_SOURCE"
            or receipt.get("donor_rate_id")!=(12 if base_id==0 else 0)
            or receipt.get("years")!=80 or receipt.get("scale")!=3
            or receipt.get("movement_fraction")!=.15
            or receipt.get("no_external_immigration") is not True
            or receipt.get("source_hypotheses")!=128):
            raise AssertionError("New genuine biological source design changed")
        replay=receipt["exact_original_seasonal_kernel_replay"]
        for field,limit in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if replay[field]>limit:
                raise AssertionError("Original seasonal trophic source no longer matches")
        g=pd.read_csv(d/"axis_original_seed_guilds.csv.gz")
        e=pd.read_csv(d/"axis_true_return_events.csv.gz")
        if (len(g)!=128*4*2*3 or
            set(g.seed)!=set(seeds) or
            not g.draw.eq(base_id).all() or
            set(g.context)!=set(CASES) or
            set(g.plant_model)!=set(PLANTS) or
            set(g.movement)!=set(MOBILITY) or
            not g.immigration.eq(0).all() or
            len(e)!=int(g.n_local_returns.sum()) or
            int(g.n_recorded_migration_arrivals.sum())!=
            int(g.n_recorded_migration_departures.sum())):
            raise AssertionError("New genuine source/censor/migration ledger incomplete")
        if len(e) and e.cause_label.eq("unclassified").any():
            raise AssertionError("Unidentified source of real integer 0-to-positive return")
        g["base_rate_id"]=base_id
        g["swapped_axis"]=axis
        new.append(g)
        events_count+=len(e)
    if seen!={(base,axis,shard) for base in BASES for axis in FOCUS for shard in NEW_GROUPS}:
        raise AssertionError("Outcome-blind eight-seed source comparison not complete")
    joined=pd.concat([base,first,*new],ignore_index=True)
    if (len(joined)!=(2+8)*4*2*2*8*12*2*3 or
        joined.duplicated(KEY).any() or
        set(joined.seed)!=set(ALL_SEEDS) or
        set(joined.swapped_axis)!={"BASE_NO_RATE_CHANGE",*FOCUS}):
        raise AssertionError("Missing or duplicate original two rate backgrounds × focus8 ×12seeds")
    for _,g in joined.groupby(["base_rate_id","swapped_axis","seed","guild",
                               "context","plant_model"],sort=True):
        if (len(g)!=32 or set(g.reverse_on)!={0,1} or
            set(g.vertex)!=set(range(8)) or set(g.movement)!=set(MOBILITY)):
            raise AssertionError("Missing source native V×S×D or reversal cube in a 12seed test")
    return joined,events_count


def summarize(data,new_events,out):
    index=KEY[:-1]+["guild"] if False else KEY[:-1]  # overridden below
    source=["base_rate_id","swapped_axis","structure_id",
            "reverse_on","vertex","seed","guild"]
    a=data[data.movement.eq("off")].set_index(source).sort_index()
    b=data[data.movement.eq("both")].set_index(source).sort_index()
    if not a.index.equals(b.index):
        raise AssertionError("No same-source movement ON/OFF pairing")
    delta=(b[list(READOUTS)]-a[list(READOUTS)]).add_prefix("delta_").reset_index()
    delta["context"]=delta.structure_id.str.split("__").str[0]
    delta["plant_model"]=delta.structure_id.str.split("__").str[-1]
    p=(delta[delta.guild.eq("F")]
       .groupby(["base_rate_id","swapped_axis","context","plant_model","seed"],
                sort=True)
       .agg(delta_occupied=("delta_final_occupied_patches","mean"),
            delta_returns=("delta_n_local_returns","mean"))
       .reset_index())
    if (len(p)!=10*4*2*12 or
        p.duplicated(["base_rate_id","swapped_axis","context","plant_model","seed"]).any()):
        raise AssertionError("Source-conditioned 12seed per-plant F effects not complete")
    context=(p.groupby(["base_rate_id","swapped_axis","plant_model","context"],sort=True)
             .agg(mean_delta_occupied=("delta_occupied","mean"),
                  mean_delta_returns=("delta_returns","mean"))
             .reset_index())
    q=p.pivot(index=["base_rate_id","swapped_axis","plant_model","seed"],
              columns="context",values="delta_occupied")
    if (q.shape!=(10*2*12,4) or set(q.columns)!=set(CASES) or q.isna().any().any()):
        raise AssertionError("Original 2x2 growth×D aquatics within 12seed fixed treatment missing")
    q["growth_main"]=.5*(
        q["S_growth_fast_only"]+q["D_first_S_overtakes"]-
        q["original"]-q["D_aquatic_long_only"])
    q=q.reset_index()
    rng=np.random.default_rng(20261031)
    rows=[]
    for (base_id,axis,plant),g in q.groupby(
            ["base_rate_id","swapped_axis","plant_model"],sort=True):
        if sorted(g.seed)!=list(ALL_SEEDS):
            raise AssertionError("RNG label 101-112 incomplete in a fixed rate-axis contrast")
        g=g.sort_values("seed")
        arr=np.column_stack([g[c].to_numpy(float) for c in CASES])
        means=arr.mean(axis=0)
        mean_by_context=dict(zip(CASES,means))
        flags=(mean_by_context["original"]>0 and
               mean_by_context["D_aquatic_long_only"]>0 and
               mean_by_context["S_growth_fast_only"]<0 and
               mean_by_context["D_first_S_overtakes"]<0)
        growth=g["growth_main"].to_numpy(float)
        mc=growth[rng.integers(0,12,size=(9999,12))].mean(axis=1)
        same_seeds=(
            (arr[:,0]>0)&(arr[:,1]>0)&(arr[:,2]<0)&(arr[:,3]<0)
        )
        row=dict(base_rate_id=int(base_id),swapped_axis=axis,plant_model=plant,
            strict_growth_reversal_12seed_mean=bool(flags),
            n_independent_seed_labels=12,
            n_seed_blocks_strict_growth_reversal=int(same_seeds.sum()),
            growth_effect_mean=float(growth.mean()),
            growth_effect_12seed_MC_lower=float(np.quantile(mc,.025)),
            growth_effect_12seed_MC_upper=float(np.quantile(mc,.975)))
        row.update({f"mean_{context}":float(mean_by_context[context])
                   for context in CASES})
        rows.append(row)
    summary=pd.DataFrame(rows)
    if len(summary)!=20:raise AssertionError("20 rate-background/axis/plant combinations expected")
    grouped=(summary.groupby(["base_rate_id","swapped_axis"],sort=True)
             .agg(n_strict_reversal_plant_roles=("strict_growth_reversal_12seed_mean","sum"),
                  n_tested_roles=("plant_model","size"),
                  mean_growth_effect=("growth_effect_mean","mean"))
             .reset_index())
    if not grouped.n_tested_roles.eq(2).all():
        raise AssertionError("Cannot compare source plant mechanisms")
    out.mkdir(parents=True,exist_ok=True)
    for name,frame in (
        ("focal_old4_new8_original80_source.csv.gz",data),
        ("focal_12seed_source_movement_deltas.csv.gz",delta),
        ("focal_12seed_F_context_effects.csv",context),
        ("focal_12seed_growth_rate_axis_effects.csv",summary),
        ("focal_12seed_rate_axis_reversal_counts.csv",grouped),
        ("focal_12seed_perseed_plant_context.csv",p),
    ):
        frame.to_csv(out/name,index=False,
                     compression={"method":"gzip","mtime":0} if name.endswith(".gz") else None)
    doc=[
        "# Frogcs 12seed same-source old4 + 8 new confirmation after all8 rate-axis screening",
        "",
        "NOTE: attack_scale, conversion, rho and f_adult_survival were selected"
        " **after** the complete 16-arm 4seed screen, then tested on eight"
        " new RNG seed labels (105-112). The remaining four axes retain only"
        " the 4seed pilot. This confirmation does not establish a general"
        " ecological parameter-law or independent field evidence.",
        "",
        "## Both directions, including unsupportive outcomes",
        "",
        grouped.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Four S-growth × D-duration cells and 12seed MC intervals",
        "",
        summary.to_markdown(index=False,floatfmt=".3f"),
        "",
        "Twelve source seed-blocks are the numerical replication unit,"
        " and baseline ID0/ID12 sources are reused without rerun."
        " One-axis necessity/sufficiency is conditional on the *other seven*"
        " original LHS rates, original source fixed q3, no immigration,"
        " eight ring patches and a 15% annual dispersal fraction."
        " The finite-N model is an additional uncalibrated binomial/Poisson"
        " stochasticization, not literal tag-level reproduction or field"
        " frog calling observations.",
    ]
    (out/"AUDITED_12SEED_SELECTED_RATE_AXIS_RESULTS.md").write_text(
        "\n".join(doc)+"\n",encoding="utf-8")
    receipt=dict(status="EIGHT_FOCUS_AXES_12_INDEPENDENT_SEED_SOURCE_VERIFIED",
                 truly_new_seed_labels=list(range(105,113)),
                 original_seed_labels=list(range(101,105)),
                 rate_backgrounds=list(BASES),n_focus_rate_axes=len(FOCUS),
                 n_bidirectional_12seed_conditions=8,
                 n_original_plus_swapped_seed_guild_source_records=int(len(data)),
                 n_source_matched_movement_contrasts=int(len(delta)),
                 new_source_return_events=int(new_events),
                 selected_after_4seed_screen=True,
                 field_causal_inference=False)
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("FOCAL_RATE_AXIS_12SEED_AUDIT_SUCCESS",json.dumps(receipt),flush=True)
    print("FOCAL_RATE_AXIS_12SEED_REVERSES\n"+grouped.to_string(index=False),flush=True)
    print("FOCAL_RATE_AXIS_12SEED_CONTEXT\n"+summary.to_string(index=False),flush=True)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--pr151-original",type=Path,required=True)
    p.add_argument("--original4screen",type=Path,required=True)
    p.add_argument("--new8shards",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data,n=verify_and_load(a.pr151_original,a.original4screen,a.new8shards)
    summarize(data,n,a.out)
