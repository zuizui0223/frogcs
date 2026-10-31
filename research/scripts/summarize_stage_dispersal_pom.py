"""Five mobility-regime model-native POM using true stochastic ABM seed outputs.

Reuse original/off 16 path-verified 20-year simulations and new adult-only,
aquatic-only, S-only 24 simulations. Keep 4 actual random seed labels as
uncertainty units, not repeated years, patches or descendants.
No acoustic observational model, no field posterior and no change to
the original seven-stage stochastic cohort/predation kernel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tracked_spatial_pedigree import ROOT, SEEDS, GUILDS
from run_stage_specific_dispersal_ablation import OUT as NEW,MODES,NEW_MODES
from assess_recolonization_establishment import (
    SOURCE as ORIGINAL,OUTPUT as SOURCE_PERSISTENCE
)

OUT=ROOT/"research/results/stage_dispersal_persistence_pom_20261031"
SOURCE_ORIGINAL_SUMMARY=ORIGINAL/"metapopulation_seed_level_summary.csv"
ARM=("mobility","reverse","seed","guild")
HORIZON=20


def load_prior_modes(original=SOURCE_ORIGINAL_SUMMARY,
                     followup=SOURCE_PERSISTENCE/"recolonization_replicate_summary.csv"):
    prior=pd.read_csv(original)
    rescue=pd.read_csv(followup)
    if (len(prior)!=48 or len(rescue)!=48
        or prior.duplicated(list(ARM)).any()
        or rescue.duplicated(list(ARM)).any()):
        raise AssertionError("Original 16 ABM arms and 3 guilds source mismatched")
    if set(prior.mobility)!={"off","original"}:
        raise AssertionError("No all-vs-none original mobility control")
    if not set(prior.guild)==set(GUILDS):
        raise AssertionError("Missing original F/S/D spatial records")
    d=prior.merge(rescue,on=list(ARM),how="inner",validate="one_to_one",
                  suffixes=("_source","_uid"))
    if len(d)!=48:raise AssertionError("Missing original source ancestry rescue episodes")
    checks=[
        ("n_recolonization_events_source","n_recolonization_events_uid"),
        ("n_recolonizations_with_surviving_immigrant",
         "n_recolonizations_with_survivor_movements"),
    ]
    for a,b in checks:
        if not (d[a].to_numpy(int)==d[b].to_numpy(int)).all():
            raise AssertionError("Original move/recolonization receipts disagree")
    rename=dict(n_occupied_end="occupied_year20",
                n_local_extinction_events="n_extinctions",
                n_recolonization_events_source="n_recolonizations",
                n_survivor_movements="n_observed_survivor_movements",
                n_living_elsewhere_than_ancestor_patch="n_living_elsewhere_than_founder_patch",
                n_multisite_founder_lineages="n_multisite_founder_lineages",
                n_living_grandchild_or_later="n_living_grandchild_or_later",
                n_eligible_two_followups="n_two_followups_eligible",
                n_retained_two_followups="n_two_followups_retained",
                n_two_census_persistent_plus_local_births="n_two_followups_and_local_birth",
                n_recolonizations_censored_at_second_followup="n_two_followups_censored",
                n_with_postreturn_external_natal_parent_births="n_postreturn_outside_parent_birth_events")
    cols=list(ARM)+list(rename)
    return d[cols].rename(columns=rename).copy()


def load_stage_specific(folder=NEW):
    result=[];receipts={}
    for mode in NEW_MODES:
        paths=[folder/(mode+"_stage_mobility_seed_summary.csv"),
               folder/(mode+"_living_lineage_ancestry.csv"),
               folder/(mode+"_receipt.json")]
        for f in paths:
            if not f.is_file() or f.stat().st_size<50:
                raise FileNotFoundError("Missing genuine new 20-y stage migration source "+str(f))
        s=pd.read_csv(paths[0])
        lineage=pd.read_csv(paths[1])
        rc=json.loads(paths[2].read_text())
        if (len(s)!=24 or len(lineage)!=24 or
            rc.get("n_new_true_20y_stochastic_arms")!=8 or
            rc.get("original_stochastic_kernel_unchanged") is not True or
            rc.get("mode")!=mode):
            raise AssertionError("Incomplete stage mobility source and original kernel anchor")
        if lineage.duplicated(list(ARM)).any() or s.duplicated(list(ARM)).any():
            raise AssertionError("Duplicate stage source/lineage population")
        matched=s.merge(lineage[list(ARM)+[
            "n_living_elsewhere_than_founder_patch",
            "n_living_grandchild_or_later",
            "n_lineages_with_living_descendants_in_multiple_patches"]],
            on=list(ARM),validate="one_to_one")
        if len(matched)!=24:raise AssertionError("Incomplete original source lineage join")
        matched=matched.rename(columns=dict(
            n_occupied_year_end="occupied_year20",
            n_local_extinction_events="n_extinctions",
            n_seen_survivor_movements="n_observed_survivor_movements",
            n_two_year_followup_eligible="n_two_followups_eligible",
            n_two_year_retained="n_two_followups_retained",
            n_two_census_persistence_plus_local_births="n_two_followups_and_local_birth",
            n_return_events_right_censored_at_2years="n_two_followups_censored",
            n_with_external_natal_parent_births="n_postreturn_outside_parent_birth_events",
            n_lineages_with_living_descendants_in_multiple_patches="n_multisite_founder_lineages"))
        cols=list(ARM)+[
            "occupied_year20","n_extinctions","n_recolonizations",
            "n_observed_survivor_movements",
            "n_living_elsewhere_than_founder_patch",
            "n_living_grandchild_or_later","n_multisite_founder_lineages",
            "n_two_followups_eligible","n_two_followups_retained",
            "n_two_followups_and_local_birth",
            "n_two_followups_censored","n_postreturn_outside_parent_birth_events"]
        result.append(matched[cols].copy())
        receipts[mode]={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in paths}
    return pd.concat(result,ignore_index=True),receipts


def complete_source_table(prior,new):
    allrows=pd.concat([prior,new],ignore_index=True)
    if len(allrows)!=len(MODES)*len(SEEDS)*2*len(GUILDS):
        raise AssertionError("Five mobility regimes × four seeds × two edge arms incomplete")
    if (allrows.duplicated(list(ARM)).any()
        or set(allrows.mobility)!=set(MODES)
        or set(allrows.guild)!=set(GUILDS)
        or set(allrows.seed)!=set(SEEDS)
        or set(allrows.reverse)!={False,True}):
        raise AssertionError("Source scenario/seed/guild unpaired")
    for col in ("occupied_year20","n_extinctions","n_recolonizations",
                "n_observed_survivor_movements",
                "n_living_elsewhere_than_founder_patch","n_multisite_founder_lineages",
                "n_two_followups_eligible","n_two_followups_retained",
                "n_two_followups_and_local_birth","n_two_followups_censored"):
        if (not np.isfinite(allrows[col].to_numpy(float)).all()
            or allrows[col].lt(0).any()):
            raise ValueError("Invalid source ecology endpoint "+col)
    if (allrows.occupied_year20.gt(8).any()
        or (allrows.n_recolonizations!=
            allrows.n_two_followups_eligible+allrows.n_two_followups_censored).any()
        or (allrows.n_two_followups_retained>allrows.n_two_followups_eligible).any()
        or (allrows.n_two_followups_and_local_birth>allrows.n_two_followups_retained).any()
        or allrows[allrows.mobility=="off"].n_observed_survivor_movements.ne(0).any()
        or allrows[allrows.mobility=="off"].n_recolonizations.ne(0).any()):
        raise AssertionError("Patch census/conditional offspring invalid or false rescue")
    return allrows.sort_values(list(ARM)).reset_index(drop=True)


def paired_dispersal_effects(allrows):
    reference=allrows[allrows.mobility=="off"].set_index(["reverse","seed","guild"])
    full=allrows[allrows.mobility=="original"].set_index(["reverse","seed","guild"])
    endpoint=["occupied_year20","n_extinctions","n_recolonizations",
              "n_observed_survivor_movements",
              "n_multisite_founder_lineages","n_two_followups_and_local_birth",
              "n_living_elsewhere_than_founder_patch"]
    rows=[]
    for mode in MODES:
        if mode=="off":continue
        d=allrows[allrows.mobility==mode].set_index(["reverse","seed","guild"])
        for anchor_name,anchor in (("no_dispersal",reference),("original_all_stages",full)):
            if (mode=="original" and anchor_name=="original_all_stages"):
                continue
            if not d.index.equals(anchor.index):
                raise AssertionError("Comparative diffusion mode uses different seed/taxon labels")
            for idx,(rev,seed,guild) in enumerate(d.index):
                row=dict(mobility=mode,baseline=anchor_name,reverse=bool(rev),
                         seed=int(seed),guild=guild)
                for k in endpoint:
                    row["delta_"+k]=float(d.iloc[idx][k]-anchor.iloc[idx][k])
                rows.append(row)
    return pd.DataFrame(rows)


def model_native_motifs(allrows,paired):
    rows=[]
    for (mode,reverse,guild),g in allrows.groupby(["mobility","reverse","guild"]):
        if len(g)!=4:raise AssertionError("Not four independent stochastic source paths")
        q=paired[(paired.mobility==mode)&
                 (paired.baseline=="no_dispersal")&
                 (paired.reverse==reverse)&
                 (paired.guild==guild)]
        if mode=="off":
            greater=0
        else:
            if len(q)!=4:raise AssertionError("Missing paired no-mobility source baseline")
            greater=int((q["delta_occupied_year20"]>0).sum())
        rows.append(dict(mobility=mode,reverse=bool(reverse),guild=guild,
            n_stochastic_seeds=4,
            mean_occupied_year20=float(g.occupied_year20.mean()),
            mean_local_extinction_events=float(g.n_extinctions.mean()),
            mean_recolonization_events=float(g.n_recolonizations.mean()),
            mean_persistent_return_with_local_births=float(g.n_two_followups_and_local_birth.mean()),
            mean_n_survivor_movements=float(g.n_observed_survivor_movements.mean()),
            mean_multisite_founder_lineages=float(g.n_multisite_founder_lineages.mean()),
            mean_founder_exogenous_alive=float(g.n_living_elsewhere_than_founder_patch.mean()),
            n_seed_replicates_with_recolonization=int((g.n_recolonizations>0).sum()),
            n_seed_replicates_with_birth_plus_2year_persistence=int(
                (g.n_two_followups_and_local_birth>0).sum()),
            n_seed_replicates_with_multisite_genealogy=int(
                (g.n_multisite_founder_lineages>0).sum()),
            n_seed_replicates_exceeding_same_seed_no_mobility_occupancy=greater,
            n_valid_two_year_followup_events=int(g.n_two_followups_eligible.sum()),
            n_two_year_retained_events=int(g.n_two_followups_retained.sum()),
            n_two_year_persistent_birth_events=int(g.n_two_followups_and_local_birth.sum()),
            n_right_censored_recolonization_episodes=int(g.n_two_followups_censored.sum()),
            outcome_scope="MODEL_NATIVE_UNCALIBRATED_SPATIAL_POM_NOT_FIELD_ABC"))
    out=pd.DataFrame(rows)
    if len(out)!=len(MODES)*2*3:
        raise AssertionError("Missing source mobility/trophic guild and predator contrast")
    return out


def run(old_source=SOURCE_ORIGINAL_SUMMARY,
        old_persistence=SOURCE_PERSISTENCE/"recolonization_replicate_summary.csv",
        new_source=NEW,out=OUT):
    out.mkdir(parents=True,exist_ok=True)
    prior=load_prior_modes(Path(old_source),Path(old_persistence))
    modern,receipts=load_stage_specific(Path(new_source))
    allrows=complete_source_table(prior,modern)
    paired=paired_dispersal_effects(allrows)
    motifs=model_native_motifs(allrows,paired)
    table=dict(stage_dispersal_all_five_modes_seed_guild=allrows,
               stage_dispersal_matched_seed_contrasts=paired,
               stage_dispersal_model_native_pom_motifs=motifs)
    for name,frame in table.items():
        frame.to_csv(out/(name+".csv"),index=False)
    record=dict(status="TRUE_SEVEN_STAGE_ABM_STAGE_MOBILITY_POM_CONDITIONAL_ON_SYNTHETIC_RATES",
                original_20year_arms_reused=16,new_20year_arms_run=24,
                seed_replicates_per_treatment=4,
                spatial_patches=8,years=20,stage_mobility_modes=list(MODES),
                original_seven_stage_kernel_unmodified=True,
                unmatched_original_deterministic_80year_ABC_not_used_as_evidence=True,
                source_sha256={Path(old_source).name:hashlib.sha256(Path(old_source).read_bytes()).hexdigest(),
                               Path(old_persistence).name:hashlib.sha256(Path(old_persistence).read_bytes()).hexdigest()},
                new_source_sha256=receipts,
                right_censored_reoccupations_not_failed=True,
                n_actual_model_source_seed_guild_records=len(allrows),
                model_native_not_field_pom=True,
                source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"receipt.json").write_text(json.dumps(record,indent=2)+"\n")
    print("FIVE_STAGE_DISPERSAL_RESCUE_POM\n"+motifs.to_string(index=False),flush=True)
    print("STAGE_DISPERSAL_MATCHED_REPLICATE_COUNTS\n"+paired.to_string(index=False),flush=True)
    return table,record


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--old-persistence",type=Path,default=SOURCE_PERSISTENCE/"recolonization_replicate_summary.csv")
    a.add_argument("--new-source",type=Path,default=NEW)
    a.add_argument("--output",type=Path,default=OUT)
    v=a.parse_args()
    if not v.run:a.error("Explicit --run required")
    run(old_persistence=v.old_persistence,new_source=v.new_source,out=v.output)
