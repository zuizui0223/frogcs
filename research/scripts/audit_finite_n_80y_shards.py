"""Auditable scientific summary of four genuine 80y finite-N source shards.

No biological process is rerun or fitted. Checks original seasonal source replay,
integer return/establishment denominators, per-arm factorial completeness, and
matched synthetic movement effects. Models have only 4 independent seed labels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import four_contrasts, categorized_sign, TARGET

GUILDS=("F","S","D")
MODES=("off","recruits","carryover","both")
SOURCE_CASES=64
SEEDS=(101,102,103,104)
RATE_ID=0
COLUMNS=(
    "final_occupied_patches","n_local_extinctions","n_local_returns",
    "n_2y_observable_returns","n_2y_persistent_returns",
    "n_3y_observable_returns","n_3y_persistent_returns",
    "n_3y_persistent_with_recruitment",
    "mean_cohort_B_last_window","final_individual_count",
)

def load_source(root):
    shards=sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith(
        "frogcs-finite-n-80y-source-"
    ))
    if len(shards)!=4:
        raise AssertionError(f"Exactly four completed source shards required, got {len(shards)}")
    seen=set()
    frames=[]
    eventframes=[]
    receipts=[]
    for folder in shards:
        receipt=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
        count=tuple(receipt["finite_individual_count_scales"])
        im=tuple(receipt["immigration_states"])
        if len(count)!=1 or len(im)!=1:
            raise AssertionError("Each successful shard must be unique scale × immigration")
        label=(int(count[0]),bool(im[0]))
        if label in seen:
            raise AssertionError("Repeated shard condition")
        seen.add(label)
        if (receipt["source_years"]!=80 or receipt["cohort_source_cases"]!=SOURCE_CASES
            or receipt["seeds"]!=list(SEEDS) or
            receipt["movement_modes"]!=list(MODES) or receipt["patches"]!=8):
            raise AssertionError("Finite 80y fixed prior design changed")
        if (receipt["source_replay_differences"]["F_B"]>1e-8 or
            receipt["source_replay_differences"]["F_fraction"]>1e-8 or
            receipt["source_replay_differences"]["F_B_sd"]>1e-7):
            raise AssertionError("Original PR146 model replay failed")
        f=pd.read_csv(folder/"finite_seed_scenario_guild_summary.csv.gz")
        e=pd.read_csv(folder/"finite_recolonization_followups.csv.gz")
        n=SOURCE_CASES*len(SEEDS)*len(MODES)*len(GUILDS)
        if len(f)!=n or f.duplicated([
            "structure_id","draw","reverse_on","vertex","seed","guild","movement"
        ]).any():
            raise AssertionError("Missing or duplicated model×seed×guild outputs")
        if not f.immigration.eq(int(im[0])).all() or not f.scale.eq(int(count[0])).all():
            raise AssertionError("Shard treatment mismatch")
        if int(f.n_local_returns.sum())!=len(e):
            raise AssertionError("Recolonization event source ledger mismatch")
        for a,b in [("n_2y_observable_returns","followup_2y_observable"),
                    ("n_2y_persistent_returns","occupied_both_followups"),
                    ("n_3y_observable_returns","followup_3y_observable"),
                    ("n_3y_persistent_returns","occupied_three_followups"),
                    ("n_3y_persistent_with_recruitment","operational_3y_recruitment")]:
            if int(f[a].sum())!=int(e[b].sum()):
                raise AssertionError("Post-return censor/persistence denominator mismatch: "+a)
        if bool(im[0]) is False and int(f.n_external_immigrants.sum())!=0:
            raise AssertionError("Immigration OFF produced arrivals from outside")
        if not f[f.movement.eq("off")].n_recorded_migration_arrivals.eq(0).all():
            raise AssertionError("Mobility OFF cannot generate spatial migrants")
        if int(f.n_recorded_migration_arrivals.sum())!=int(f.n_recorded_migration_departures.sum()):
            raise AssertionError("Spatial movement failed global mass conservation")
        if e.cause_label.eq("unclassified").any():
            raise AssertionError("An unexplained 0→positive event exists")
        if not f.n_3y_persistent_with_recruitment.le(f.n_3y_persistent_returns).all():
            raise AssertionError("Impossible persistence + recruitment event subset")
        frames.append(f)
        eventframes.append(e)
        receipts.append(receipt)
    if seen!={(3,False),(3,True),(12,False),(12,True)}:
        raise AssertionError("Fixed finite-N × external source factorial incomplete")
    whole=pd.concat(frames,ignore_index=True)
    events=pd.concat(eventframes,ignore_index=True)
    unique=["structure_id","draw","reverse_on","vertex","scale","seed",
            "movement","immigration","guild"]
    if whole.duplicated(unique).any() or set(whole.guild)!=set(GUILDS):
        raise AssertionError("Combined sample identities duplicated")
    return whole,events,receipts


def native_four_signs(summary):
    """No pseudocount: undefined log if any of 8 source F_B cells is 0."""
    f=summary[summary.guild.eq("F")].copy()
    cols=["structure_id","draw","reverse_on","scale","seed","movement","immigration"]
    rows=[]
    for key,g in f.groupby(cols,sort=True):
        if len(g)!=8 or set(g.vertex)!=set(range(8)):
            raise AssertionError("Missing true 2x2x2 model source corners")
        cube=g.sort_values("vertex").mean_cohort_B_last_window.to_numpy(float).reshape(2,2,2)
        if not np.isfinite(cube).all() or (cube<0).any():
            raise AssertionError("Invalid finite source F_B window")
        raw=four_contrasts(cube)
        rs=categorized_sign(raw)
        rec=dict(zip(cols,key))
        rec.update(raw_four_sign_match=int(np.array_equal(rs,np.asarray(TARGET))),
                   raw_sign_pattern=",".join(map(str,rs)),
                   positive_all_8_vertices=int(np.all(cube>0)),
                   min_F_B=float(cube.min()),
                   max_F_B=float(cube.max()))
        if (cube>0).all():
            signs=categorized_sign(four_contrasts(np.log(cube)))
            rec["log_four_sign_match"]=int(np.array_equal(signs,np.asarray(TARGET)))
            rec["log_sign_pattern"]=",".join(map(str,signs))
        else:
            rec["log_four_sign_match"]=np.nan
            rec["log_sign_pattern"]="undefined_zero_cohort_no_pseudocount"
        rows.append(rec)
    out=pd.DataFrame(rows)
    expected=SOURCE_CASES*len(SEEDS)*2*2*len(MODES)//8
    if len(out)!=expected:
        raise AssertionError(f"Lost true four-sign source cubes: {len(out)} != {expected}")
    return out


def paired_summary(summary):
    index=["structure_id","draw","reverse_on","vertex","scale","seed",
           "immigration","guild"]
    off=summary[summary.movement.eq("off")].set_index(index).sort_index()
    result=[]
    for move in MODES[1:]:
        on=summary[summary.movement.eq(move)].set_index(index).sort_index()
        if not off.index.equals(on.index):
            raise AssertionError("Same-source movement and OFF identity mismatch")
        p=(on[list(COLUMNS)]-off[list(COLUMNS)]).add_prefix("delta_").reset_index()
        p["movement"]=move
        result.append(p)
    return pd.concat(result,ignore_index=True)


def analyze(root,out):
    whole,events,receipts=load_source(root)
    signs=native_four_signs(whole)
    pairs=paired_summary(whole)
    agg=(whole.groupby(["scale","immigration","movement","context","plant_model","guild"],
                       sort=True)
         .agg(n_seed_cases=("seed","size"),
              mean_final_patches=("final_occupied_patches","mean"),
              mean_local_extinctions=("n_local_extinctions","mean"),
              mean_local_returns=("n_local_returns","mean"),
              mean_recruits=("n_local_recruits","mean"),
              total_returns_2y_followable=("n_2y_observable_returns","sum"),
              total_2y_occupancy=("n_2y_persistent_returns","sum"),
              total_returns_3y_followable=("n_3y_observable_returns","sum"),
              total_3y_occupancy=("n_3y_persistent_returns","sum"),
              total_3y_occupancy_plus_recruits=("n_3y_persistent_with_recruitment","sum"))
         .reset_index())
    pooled=(agg.groupby(["scale","immigration","movement","guild"],sort=True)
            .agg(n_source_units=("n_seed_cases","sum"),
                 mean_final_occupied=("mean_final_patches","mean"),
                 mean_local_returns=("mean_local_returns","mean"),
                 mean_local_extinctions=("mean_local_extinctions","mean"),
                 total_returns_3y_followable=("total_returns_3y_followable","sum"),
                 total_3y_occupied=("total_3y_occupancy","sum"),
                 total_3y_plus_recruits=("total_3y_occupancy_plus_recruits","sum"))
            .reset_index())
    contrasts=(pairs.groupby(["scale","immigration","movement","guild"],sort=True)
               .agg(n_source_paired_scenarios=("seed","size"),
                    mean_delta_occupancy=("delta_final_occupied_patches","mean"),
                    mean_delta_returns=("delta_n_local_returns","mean"),
                    mean_delta_extinctions=("delta_n_local_extinctions","mean"),
                    mean_delta_3y_persistent_recruitment=(
                        "delta_n_3y_persistent_with_recruitment","mean"))
               .reset_index())
    pats=(signs.groupby(["scale","immigration","movement"],sort=True)
          .agg(n_model_native_cubes=("raw_four_sign_match","size"),
               n_with_all_8_positive=("positive_all_8_vertices","sum"),
               raw_matches=("raw_four_sign_match","sum"),
               log_matches=("log_four_sign_match","sum"))
          .reset_index())
    classes=(events.groupby(["scale","immigration","movement","guild","cause_label"],sort=True)
             .agg(n_returns=("census_year","size"),
                  n_3y_observable=("followup_3y_observable","sum"),
                  n_3y_occupied=("occupied_three_followups","sum"),
                  n_3y_occupied_plus_recruits=("operational_3y_recruitment","sum"))
             .reset_index())
    out.mkdir(parents=True,exist_ok=True)
    for name,frame in [
        ("source_80year_finite_seed_scenarios.csv.gz",whole),
        ("source_80year_return_events.csv.gz",events),
        ("finite_80year_group_means.csv",agg),
        ("finite_80year_guild_comparison.csv",pooled),
        ("finite_80year_movement_vs_off.csv",contrasts),
        ("finite_80year_native_four_signs.csv",signs),
        ("finite_80year_four_sign_summary.csv",pats),
        ("finite_80year_return_sources.csv",classes),
    ]:
        compression=({"method":"gzip","mtime":0} if name.endswith(".gz") else None)
        frame.to_csv(out/name,index=False,compression=compression)
    report=[
        "# Frogcs 80-year integer cohort and real-zero patch POM (synthetic)",
        "",
        "**Four separate true source shards have been checked: original PR146 seasonal"
        " trophic source unchanged; integer movement closed landscape mass"
        " conservative; all events and denominators complete.**",
        "",
        f"- Source conditions: {SOURCE_CASES} original cube corners, 4 seeds,"
        " two arbitrary count scales, 2 external immigration states,"
        " 4 annual movement modes, 80 years and 8 synthetic ring patches.",
        f"- Total annual model×guild summaries: {len(whole):,};"
        f" true integer 0→positive patch reoccupancy events: {len(events):,}.",
        f"- Source deterministic replay max absolute F_B error:"
        f" {max(x['source_replay_differences']['F_B'] for x in receipts):.4g}.",
        "- All effects below are finite synthetic experiment comparisons, not"
        " field movement, acoustic activity, literal parentage, or empirical"
        " Bayesian probabilities.",
        "",
        "## Local patch occupancy, return and persistence (mean across source scenarios and seeds)",
        "",
        pooled.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Paired movement−off differences (same treatment definition, seed labels; not individual pathwise)",
        "",
        contrasts.to_markdown(index=False,floatfmt=".3f"),
        "",
        "## Cause of model-native zero→positive events, after right censor accounting",
        "",
        classes.to_markdown(index=False),
        "",
        "## Model-native 2×2×2 F_B four-sign patterns",
        "",
        pats.to_markdown(index=False),
        "",
        "**Log F_B is undefined if any of 8 source cube corners is exactly zero.**"
        " No pseudocount or artificial imputation. Do not interpret count-scale"
        " movement as field mechanism calibration.",
        "",
        "## Maturation and independence boundaries",
        "",
        "Two-year post-return local recruitment is not the same as newborns in"
        " PR147. For original F delay=2 or3 years, recruitment can lag local"
        " reappearance: 3-year followup is an additional descriptive diagnostic,"
        " not proof that the sampled recruits descended from the colonist."
        " The source comparison models many same-seed parameter/patch cells;"
        " the number of independent RNG replicates is only **4** per treatment."
        " No inference about global biological posterior or unique mechanism.",
    ]
    report_text="\n".join(report)+"\n"
    (out/"AUDITED_FINITE_N_80YEAR_FINDINGS.md").write_text(report_text,encoding="utf-8")
    receipt=dict(status="SOURCE_80Y_FINITE_N_STOCHASTIC_AUDIT_SUCCESS",
                 n_source_shards=4,
                 total_source_summaries=int(len(whole)),
                 total_actual_return_events=int(len(events)),
                 n_model_native_four_sign_cases=int(len(signs)),
                 n_paired_movement_source_cases=int(len(pairs)),
                 possible_field_inference=False)
    (out/"AUDITED_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt),flush=True)
    print("FINITE_80Y_GUILD_COMPARISON\n"+pooled.to_string(index=False),flush=True)
    print("FINITE_80Y_MOVEMENT_VS_OFF\n"+contrasts.to_string(index=False),flush=True)
    print("FINITE_80Y_FOUR_SIGNS\n"+pats.to_string(index=False),flush=True)
    print("FINITE_80Y_RECOLONIZATION_SOURCES\n"+classes.to_string(index=False),flush=True)
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    analyze(a.shards_root,a.out)
