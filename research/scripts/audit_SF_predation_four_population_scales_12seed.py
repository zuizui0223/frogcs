"""Fail-closed source audit: original q3/q12 and NEW real q6/q9 80y trajectories.

No biological model is rerun. Original source is immutable successful
PR154 artifact, new q6/9 requires all 24 true 80-year sources and exact
return-event/censoring ledger. Each treatment has exactly 12 independent
RNG seed labels; original V×S×D source factorial vertices are NOT samples.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

SCALES=(3,6,9,12)
NEW_SCALES=(6,9)
NETS=("all_active","SF_only","no_SF","no_direct_predation")
SEED_SHARDS=((101,102,103,104),(105,106,107,108),(109,110,111,112))
SEEDS=tuple(range(101,113))
PLANTS=("SF0_DF0_DS1_L0","SF1_DF0_DS0_L1")
CONTEXTS=("original","S_growth_fast_only","D_aquatic_long_only",
          "D_first_S_overtakes")
READOUTS=("final_occupied_patches","n_local_returns","n_local_extinctions",
          "n_3y_persistent_with_recruitment")
KEY=["scale","recruitment_regime","network_arm","structure_id",
     "reverse_on","vertex","seed","guild","movement"]

def load_verified(original_dir,new_dir):
    path=original_dir/"original_q3_genuine_q12_source_scenarios.csv.gz"
    if not path.exists():
        raise AssertionError("Missing genuine q3/q12 original 80-year 12seed source data")
    old=pd.read_csv(path)
    if (len(old)!=147456 or set(old.scale)!={3,12} or
        set(old.recruitment_regime)!={"rate12_base","rate12_rho0"} or
        set(old.network_arm)!=set(NETS) or
        set(old.seed)!=set(SEEDS)):
        raise AssertionError("Earlier q3/q12 audited source controls changed")
    old=old[old.recruitment_regime.eq("rate12_rho0")].copy()
    if len(old)!=2*4*128*12*2*3:
        raise AssertionError("Old q3+q12 high-recruitment original source not complete")

    dirs=sorted(d for d in new_dir.iterdir() if d.is_dir() and
                d.name.startswith("frogcs-q69-source-"))
    if len(dirs)!=24:
        raise AssertionError(f"All 24 genuine q6/q9 source runs required; got {len(dirs)}")
    seen=set()
    frames=[old]
    events=[]
    for folder in dirs:
        r=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        q=r.get("q_synthetic_population_count_per_density_unit")
        net=r.get("network_arm")
        seeds=tuple(r.get("independent_seed_labels",[]))
        key=(q,net,seeds)
        if (q not in NEW_SCALES or net not in NETS or
            seeds not in SEED_SHARDS or key in seen):
            raise AssertionError("Incomplete/duplicate q6/q9 source arm: "+str(key))
        seen.add(key)
        edges={
            "all_active":["SF","DF","DS","SD"],
            "SF_only":["SF"],
            "no_SF":["DF","DS","SD"],
            "no_direct_predation":[],
        }
        if (r.get("status")!="ORIGINAL_120DAY_TROPHIC_80YEAR_FINITE_N_INTERMEDIATE_Q_SOURCE_SUCCESS"
            or r.get("recruitment_regime")!="rate12_rho0"
            or r.get("active_directed_trophic_edges")!=edges[net]
            or r.get("n_original_source_factorial_cases")!=128
            or r.get("original_years")!=80
            or r.get("annual_movement_fraction")!=.15
            or r.get("external_immigration") is not False
            or r.get("same_biological_rates_and_original_kernel") is not True):
            raise AssertionError("Precommitted biology or q changed in source calculation")
        for f,tol in (("F_B",1e-8),("F_fraction",1e-8),("F_B_sd",1e-7)):
            if r["source_replay_errors"][f]>tol:
                raise AssertionError("Original deterministic 80y trophic source replay failed: "+f)
        f=pd.read_csv(folder/"q6_q9_real_80y_seed_scenario_guild.csv.gz")
        e=pd.read_csv(folder/"q6_q9_real_zero_to_positive_events.csv.gz")
        if (len(f)!=128*4*2*3 or set(f.seed)!=set(seeds) or
            set(f.movement)!={"off","both"} or
            set(f.context)!=set(CONTEXTS) or
            set(f.plant_model)!=set(PLANTS) or
            not f.network_arm.eq(net).all() or
            not f.recruitment_regime.eq("rate12_rho0").all() or
            not f.scale.eq(q).all() or
            not f.immigration.eq(0).all() or
            f.duplicated(KEY).any() or
            len(e)!=int(f.n_local_returns.sum())):
            raise AssertionError("True original new synthetic source/q/seed/event incomplete")
        if int(f.n_recorded_migration_arrivals.sum())!=int(
                f.n_recorded_migration_departures.sum()):
            raise AssertionError("Original spatial F/S/D migration mass not conserved")
        if len(e) and e.cause_label.eq("unclassified").any():
            raise AssertionError("New source 0→positive return did not classify")
        for key1,key2 in (
            ("n_3y_observable_returns","followup_3y_observable"),
            ("n_3y_persistent_returns","occupied_three_followups"),
            ("n_3y_persistent_with_recruitment","operational_3y_recruitment"),
        ):
            if int(f[key1].sum())!=int(e[key2].sum()):
                raise AssertionError("New q source returns not matching 3y follow-up/censor")
        frames.append(f)
        events.append(dict(scale=int(q),network_arm=net,seeds="_".join(map(str,seeds)),
                  n_true_N0_to_positive_returns=int(len(e)),
                  n_3y_followable=int(e.followup_3y_observable.sum()),
                  n_3y_persistent=int(e.occupied_three_followups.sum()),
                  n_3y_with_local_recruits=int(e.operational_3y_recruitment.sum())))
    if seen!={(q,n,seeds) for q in NEW_SCALES for n in NETS for seeds in SEED_SHARDS}:
        raise AssertionError("Original preregistered 24 source treatments incomplete")
    full=pd.concat(frames,ignore_index=True)
    if (len(full)!=4*4*128*12*2*3 or
        set(full.scale)!=set(SCALES) or full.duplicated(KEY).any() or
        set(full.recruitment_regime)!={"rate12_rho0"}):
        raise AssertionError("Original q3,6,9,12 source factorial does not balance")
    for (q,n,seed,guild),g in full.groupby(
        ["scale","network_arm","seed","guild"],sort=True):
        if (len(g)!=128*2 or set(g.movement)!={"off","both"} or
            set(g.context)!=set(CONTEXTS) or
            set(g.plant_model)!=set(PLANTS)):
            raise AssertionError("Source 2×2 growth/D aquatic/plant/seasonal motor conditions lost")
    return full,pd.DataFrame(events)


def audit(full,event_counts,out):
    index=[c for c in KEY if c!="movement"]
    a=full[full.movement.eq("off")].set_index(index).sort_index()
    b=full[full.movement.eq("both")].set_index(index).sort_index()
    if not a.index.equals(b.index):
        raise AssertionError("No original q-matched same-source movement ON/OFF pairs")
    delta=(b[list(READOUTS)]-a[list(READOUTS)]).add_prefix("delta_").reset_index()
    delta["context"]=delta.structure_id.str.split("__").str[0]
    delta["plant_model"]=delta.structure_id.str.split("__").str[-1]
    blocks=(delta[delta.guild.eq("F")].groupby(
        ["scale","network_arm","plant_model","context","seed"],sort=True)
        [[f"delta_{metric}" for metric in READOUTS]]
        .mean().reset_index())
    if len(blocks)!=4*4*2*4*12:
        raise AssertionError("Original q×network×plant 12seed data lost")
    pv=blocks.pivot(index=["scale","network_arm","plant_model","seed"],
       columns="context",values="delta_final_occupied_patches")
    if (len(pv)!=4*4*2*12 or set(pv.columns)!=set(CONTEXTS) or
        pv.isna().any().any()):
        raise AssertionError("Source exact 2×2 S growth and D aquatic contexts not balanced")
    pv["S_growth_effect"]=.5*(pv["S_growth_fast_only"]+pv["D_first_S_overtakes"]-
                               pv["original"]-pv["D_aquatic_long_only"])
    pv["strict_reversal_per_seed"]=(
        pv["original"].gt(0)&pv["D_aquatic_long_only"].gt(0)&
        pv["S_growth_fast_only"].lt(0)&pv["D_first_S_overtakes"].lt(0))
    pv=pv.reset_index()
    rng=np.random.default_rng(20261031)
    rows=[]
    for (q,net,plant),g in pv.groupby(
        ["scale","network_arm","plant_model"],sort=True):
        g=g.sort_values("seed")
        if g.seed.tolist()!=list(SEEDS):
            raise AssertionError("No twelve independent Monte Carlo seed blocks")
        m=g[list(CONTEXTS)].mean()
        strict=bool(m.original>0 and m.D_aquatic_long_only>0 and
                    m.S_growth_fast_only<0 and m.D_first_S_overtakes<0)
        v=g.S_growth_effect.to_numpy(float)
        boot=v[rng.integers(0,12,size=(9999,12))].mean(axis=1)
        rec=dict(scale=int(q),network_arm=net,plant_model=plant,
            n_independent_seed_labels=12,
            strict_reversal_across_4_source_cells=strict,
            n_seed_blocks_with_all_4_signs=int(g.strict_reversal_per_seed.sum()),
            S_growth_modifier_mean=float(v.mean()),
            S_growth_modifier_MC_lower=float(np.quantile(boot,.025)),
            S_growth_modifier_MC_upper=float(np.quantile(boot,.975)))
        rec.update({"movement_delta_"+name:float(m[name]) for name in CONTEXTS})
        rows.append(rec)
    perplant=pd.DataFrame(rows)
    if len(perplant)!=4*4*2:
        raise AssertionError("Missing 4 scales×4 network arms×2 legal vegetation models")
    grouped=(perplant.groupby(["scale","network_arm"],sort=True)
             .agg(n_plant_roles_reversal=("strict_reversal_across_4_source_cells","sum"),
                  n_plant_roles=("plant_model","size"),
                  n_seed_block_strict_reversals=("n_seed_blocks_with_all_4_signs","sum"),
                  mean_S_growth_modifier=("S_growth_modifier_mean","mean"))
             .reset_index())
    if not grouped.n_plant_roles.eq(2).all():
        raise AssertionError("Not both original plant role source manipulations")

    occupancy=(full[full.guild.eq("F")].groupby(
        ["scale","network_arm","plant_model","context","movement"],sort=True)
        .agg(mean_occupied=("final_occupied_patches","mean"),
             percentage_zero=("final_occupied_patches",lambda x: 100*np.mean(np.asarray(x)==0)),
             percentage_eight=("final_occupied_patches",lambda x: 100*np.mean(np.asarray(x)==8)),
             mean_local_returns=("n_local_returns","mean"),
             mean_local_extinctions=("n_local_extinctions","mean"),
             n_source_scenarios=("seed","size"))
        .reset_index())

    out.mkdir(parents=True,exist_ok=True)
    for filename,d in (
        ("genuine_80year_q3_q6_q9_q12_all_finite_guild_source.csv.gz",full),
        ("matched_four_population_scales_source_movement_deltas.csv.gz",delta),
        ("four_q_frog_seed_block_effects.csv",blocks),
        ("four_q_2x2_growth_effects_per_seed.csv",pv),
        ("four_q_12seed_plant_MC_intervals.csv",perplant),
        ("four_q_strict_reversal_counts.csv",grouped),
        ("four_q_frog_year80_occupancy_floor_ceiling.csv",occupancy),
        ("genuine_new_q6_q9_reoccupation_event_counts.csv",event_counts),
    ):
        d.to_csv(out/filename,index=False,compression=(
            {"method":"gzip","mtime":0} if filename.endswith(".gz") else None))
    receipt=dict(
        status="FOUR_POPULATION_SCALES_GENUINE_SOURCE_80YEAR_12SEED_AUDIT_SUCCESS",
        old_source_q3_q12_reused_unchanged=True,
        n_new_q6_q9_80year_source_shards=24,
        n_synthetic_count_scales=4,
        n_original_source_seed_guild_rows=int(len(full)),
        n_same_source_movement_contrasts=int(len(delta)),
        n_new_genuine_q6_q9_integer_reoccupation_events=int(event_counts.n_true_N0_to_positive_returns.sum()),
        independent_rng_seed_labels=list(SEEDS),
        artificial_population_scale_not_wild_count=True,
        causal_field_mechanism_inference=False
    )
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    lines=[
        "# frogcs: 80year source-verified finite-N population scale grid q3/q6/q9/q12",
        "",
        "**This is exploratory q6/9 mapping added AFTER observing the q12"
        " loss of strict S-growth-dependent dispersal sign reversal.**"
        " Old q3 and q12 are identical reused verified source outputs."
        " Each new q6/9 80-year model passed the original seasonal and"
        " delayed-cohort biology, integer 0→positive reoccupation and all"
        " right-censoring and closed spatial ring mass checks.",
        "",
        "## Strict reversed dispersal-effect pattern, all source networks",
        "",
        grouped.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Plant-specific movement effects by growth and aquatic duration",
        "",
        perplant.to_markdown(index=False,floatfmt=".4f"),
        "",
        "## Local population occupancy floor/ceiling across q values",
        "",
        occupancy.to_markdown(index=False,floatfmt=".4f"),
        "",
        "None of the four q values is an actual population size in real ponds."
        " The finite synthetic q grid can show a numerical bracket over"
        " tested q values, NOT a field biological critical population size"
        " or mathematically sharp transition. Only the 12 original RNG"
        " labels, not repeated fixed factor vertices or patches or 80year"
        " local return events, are independent Monte Carlo replicates."
        " The conditional biological rateID12+rho(ID0), migration fraction"
        " .15 and no external immigration remain hypothetical.",
    ]
    (out/"AUDITED_INTERMEDIATE_Q3_Q6_Q9_Q12_12SEED_RESULTS.md").write_text(
       "\n".join(lines)+"\n",encoding="utf-8")
    print("INTERMEDIATE_Q_SOURCE_AUDIT_RECEIPT",json.dumps(receipt),flush=True)
    print("INTERMEDIATE_Q_STRICT_REVERSALS\n"+grouped.to_string(index=False),flush=True)
    print("INTERMEDIATE_Q_PLANT_CONTEXTS\n"+perplant.to_string(index=False),flush=True)
    print("INTERMEDIATE_Q_FLOOR_CEILING\n"+occupancy.to_string(index=False),flush=True)
    return receipt,perplant,grouped

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--existing-q3-q12",type=Path,required=True)
    p.add_argument("--new-q6-q9",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args()
    full,e=load_verified(x.existing_q3_q12,x.new_q6_q9)
    audit(full,e,x.out)
