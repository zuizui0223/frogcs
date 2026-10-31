"""Recolonization is not establishment: use complete real ABM census/UID artifacts.

Uses *only* prior SUCCESS source artifact #41186773263. No new random
numbers, simulated parameters or process-model modifications. Stage and
stochastic rates here are distinct from the genuine 80-year main ABC model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tracked_spatial_pedigree import ROOT, GUILDS, patch_occupancy_transitions

SOURCE=ROOT/"research/results/stochastic_pedigree_metapop_20261031"
OUTPUT=ROOT/"research/results/recolonization_establishment_20261031"
ARM=("mobility","reverse","seed")
CELL=(*ARM,"guild","patch")
KEY=(*CELL,"year")


def verify_sources(folder):
    files=dict(patches=folder/"patch_extirpation_recolonization.csv.gz",
               registry=folder/"registry_all_simulated_uids.csv.gz",
               annual=folder/"annual_stage_and_demographic_events.csv",
               lineage=folder/"lineage_generation_and_spatial_reach.csv",
               receipt=folder/"receipt.json")
    for name,path in files.items():
        if not path.is_file() or path.stat().st_size < 50:
            raise FileNotFoundError("Missing source-backed "+name+" "+str(path))
    receipt=json.loads(files["receipt"].read_text())
    if (receipt.get("n_trajectory_arms")!=16 or receipt.get("years")!=20 or
        receipt.get("spatial_patches")!=8 or
        receipt.get("not_same_kernel_as_original_80year_ABC") is not True or
        not receipt.get("original_seven_stage_kernel_sha256")):
        raise AssertionError("Unverifiable source ABM mechanism and data grain")
    patch=pd.read_csv(files["patches"])
    registry=pd.read_csv(files["registry"])
    annual=pd.read_csv(files["annual"])
    if len(patch)!=16*21*3*8 or len(annual)!=16*20:
        raise AssertionError("Incomplete source annual patch census")
    if len(registry)!=receipt["n_simulated_ever_lived_unique_ids"]:
        raise AssertionError("Incomplete living/dead parent ledger")
    if patch.duplicated(list(KEY)).any() or registry.duplicated(list(ARM)+["uid"]).any():
        raise AssertionError("Duplicate per-arm source UID or patch census")
    if annual.duplicated(list(ARM)+["year"]).any():
        raise AssertionError("Duplicate original census year")
    if len(patch[list(ARM)].drop_duplicates())!=16:
        raise AssertionError("Source mobility/reversal/seed arms changed")
    if not np.array_equal(np.sort(patch.year.unique()),np.arange(21)):
        raise AssertionError("Missing source annual census")
    if not np.array_equal(np.sort(annual.year.unique()),np.arange(1,21)):
        raise AssertionError("Source years missing")
    if (not patch.alive.ge(0).all() or not patch.n_newborn.ge(0).all()
        or not patch.known_surviving_immigrant_arrivals.ge(0).all()):
        raise AssertionError("Invalid source-stage abundance and births")
    hashes={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in files.items()}
    return patch,registry,annual,receipt,hashes


def natal_parent_births(registry):
    """Births in patch/year; records parent natal origin even after death."""
    rows=[]
    if registry.duplicated(list(ARM)+["uid"]).any():
        raise ValueError("Duplicate parent identity within experimental arm")
    for key,arm in registry.groupby(list(ARM),sort=True):
        parents=arm.set_index("uid")[["natal_patch","founder_patch","guild","generation"]]
        children=arm.loc[arm.parent_uid.ge(0)].copy()
        if children.empty:
            continue
        parent=parents.reindex(children.parent_uid.to_numpy(dtype=np.int64))
        if parent.isna().any().any():
            raise AssertionError("Descendant references unknown or removed parent UID")
        if not np.array_equal(children.guild.to_numpy(),parent.guild.to_numpy()):
            raise AssertionError("Parent not in child's own modeled trophic guild")
        if not np.array_equal(children.generation.to_numpy(dtype=int),
                              parent.generation.to_numpy(dtype=int)+1):
            raise AssertionError("Invalid original-ABM genealogical generation")
        birth_year=np.ceil(children.birth_time.to_numpy(float)-1e-9).astype(int)
        if (np.any(birth_year<1) or np.any(birth_year>20)
            or np.any(children.natal_patch.to_numpy(int)<0)
            or np.any(children.natal_patch.to_numpy(int)>7)):
            raise AssertionError("Misindexed original 20-year stage birth")
        children["year"]=birth_year
        children["from_outside_natal_parent"]=(
            children.natal_patch.to_numpy(int)!=parent.natal_patch.to_numpy(int)).astype(int)
        children["from_outside_founder"]=(
            children.natal_patch.to_numpy(int)!=children.founder_patch.to_numpy(int)).astype(int)
        q=(children.groupby(["guild","natal_patch","year"],sort=True)
            .agg(births_from_registry=("uid","size"),
                 births_with_exogenous_natal_parent=("from_outside_natal_parent","sum"),
                 births_with_exogenous_founder=("from_outside_founder","sum"))
            .reset_index().rename(columns={"natal_patch":"patch"}))
        for col,val in zip(ARM,key):q[col]=val
        rows.append(q)
    if not rows:
        return pd.DataFrame(columns=[*KEY,"births_from_registry",
            "births_with_exogenous_natal_parent","births_with_exogenous_founder"])
    return pd.concat(rows,ignore_index=True)


def attach_validated_births(patch,registry):
    q=natal_parent_births(registry)
    data=patch.merge(q,on=list(KEY),how="left",validate="one_to_one")
    for col in ("births_from_registry","births_with_exogenous_natal_parent",
                "births_with_exogenous_founder"):
        data[col]=data[col].fillna(0).astype(int)
    errors=data.n_newborn.to_numpy(int)-data.births_from_registry.to_numpy(int)
    if np.any(errors!=0):
        bad=data.loc[errors!=0,list(KEY)+["n_newborn","births_from_registry"]].head(5)
        raise AssertionError("Annual source birth counts do not reconcile with child UIDs\n"+
                             bad.to_string(index=False))
    return data


def event_table(annual_patch):
    """One row per annual-census empty→occupied transition, future censoring."""
    expected_cols=set(KEY)|{"alive","recolonized","locally_extinct","n_newborn",
                              "known_surviving_immigrant_arrivals",
                              "births_with_exogenous_natal_parent",
                              "births_with_exogenous_founder"}
    if not expected_cols.issubset(annual_patch):
        raise ValueError("Missing source census/immigration/birth fields")
    events=[]
    for keys,g in annual_patch.groupby(list(CELL),sort=True):
        x=g.sort_values("year").reset_index(drop=True)
        years=x.year.to_numpy(dtype=int)
        if not np.array_equal(years,np.arange(len(years))) or len(x)<2:
            raise AssertionError("Annual origin patch census changed")
        occupied=x.alive.to_numpy(float)>0
        loss=occupied[:-1]&(~occupied[1:])
        return_=(~occupied[:-1])&occupied[1:]
        if (not np.array_equal(x.locally_extinct.to_numpy(dtype=bool)[1:],loss)
            or not np.array_equal(x.recolonized.to_numpy(dtype=bool)[1:],return_)
            or bool(x.locally_extinct.iloc[0]) or bool(x.recolonized.iloc[0])):
            raise AssertionError("Recolonization/extirpation source definition changed")
        for t in np.flatnonzero(return_)+1:
            valid1=t+1<len(x)
            valid2=t+2<len(x)
            occupy1=bool(occupied[t+1]) if valid1 else None
            occupy2=bool(occupied[t+2]) if valid2 else None
            births1=int(x.n_newborn.iloc[t+1]) if valid1 else None
            outside1=int(x.births_with_exogenous_natal_parent.iloc[t+1]) if valid1 else None
            founder1=int(x.births_with_exogenous_founder.iloc[t+1]) if valid1 else None
            episode_len=0
            while t+episode_len<len(x) and occupied[t+episode_len]:
                episode_len+=1
            event=dict(zip(CELL,keys))
            event.update(dict(year_of_recolonization=int(t),
                observed_surviving_arrivals_in_return_year=int(
                    x.known_surviving_immigrant_arrivals.iloc[t]),
                births_during_return_year=int(x.n_newborn.iloc[t]),
                one_census_followup_observed=bool(valid1),
                retained_at_one_followup=occupy1,
                two_census_followups_observed=bool(valid2),
                retained_at_two_followups=(
                    bool(occupy1 and occupy2) if valid2 else None),
                locally_born_in_first_postreturn_year=births1,
                births_with_external_natal_parent_in_postreturn_year=outside1,
                births_with_external_founder_in_postreturn_year=founder1,
                two_census_persistence_and_postreturn_births=(
                    bool(occupy1 and occupy2 and births1>0) if valid2 else None),
                consecutive_observed_occupied_censuses=int(episode_len),
                occupied_spell_right_censored=bool(t+episode_len==len(x)),
                establishment_definition="annual_census_persistence_plus_local_births_not_offspring_survival"))
            events.append(event)
    if not events:
        return pd.DataFrame(columns=[*CELL,"year_of_recolonization",
                                     "retained_at_one_followup",
                                     "retained_at_two_followups"])
    return pd.DataFrame(events)


def source_annual_stage_audit(patch,annual):
    """Exact original F and D stage counts vs patch occupancy at every year."""
    p=patch[patch.year>0].groupby(list(ARM)+["year","guild"]).alive.sum()
    q=annual.set_index(list(ARM)+["year"])
    for guild,terms in (("F",["F_tadpole","F_adult"]),
                        ("D",["D_nymph","D_emerging","D_adult"])):
        x=p.xs(guild,level="guild").sort_index()
        y=q[terms].sum(axis=1).sort_index()
        if not x.index.equals(y.index) or not np.array_equal(x.to_numpy(dtype=int),
                                                              y.to_numpy(dtype=int)):
            raise AssertionError("Original F or D population census differs from patch/UID table")
    return True


def by_replicate(patch,events):
    allarms=patch[list(ARM)+["guild"]].drop_duplicates().sort_values(list(ARM)+["guild"])
    rows=[]
    for key,g in allarms.groupby(list(ARM)+["guild"],sort=True):
        names=(*ARM,"guild")
        filt=np.ones(len(events),bool)
        for col,val in zip(names,key):
            if col in events:
                filt &= events[col].to_numpy()==val
        obs=events.loc[filt]
        x=dict(zip(names,key))
        x.update(dict(n_recolonization_events=int(len(obs)),
                      n_recolonizations_with_survivor_movements=int(
                          (obs.observed_surviving_arrivals_in_return_year>0).sum()) if len(obs) else 0,
                      n_eligible_one_followup=int(obs.one_census_followup_observed.sum()) if len(obs) else 0,
                      n_retained_one_followup=int(
                          obs.retained_at_one_followup.fillna(False).astype(int).sum()) if len(obs) else 0,
                      n_eligible_two_followups=int(obs.two_census_followups_observed.sum()) if len(obs) else 0,
                      n_retained_two_followups=int(
                          obs.retained_at_two_followups.fillna(False).astype(int).sum()) if len(obs) else 0,
                      n_with_postreturn_local_births=int(
                          (obs.locally_born_in_first_postreturn_year.fillna(0)>0).sum()) if len(obs) else 0,
                      n_with_postreturn_external_natal_parent_births=int(
                          (obs.births_with_external_natal_parent_in_postreturn_year.fillna(0)>0).sum()) if len(obs) else 0,
                      n_two_census_persistent_plus_local_births=int(
                          obs.two_census_persistence_and_postreturn_births.fillna(False).astype(int).sum()) if len(obs) else 0,
                      n_recolonizations_censored_at_second_followup=int(
                          (~obs.two_census_followups_observed).sum()) if len(obs) else 0))
        rows.append(x)
    out=pd.DataFrame(rows)
    if out.shape[0]!=48 or out.n_eligible_two_followups.gt(out.n_recolonization_events).any():
        raise AssertionError("Missing source replicate or censored followup not handled")
    return out


def run(source=SOURCE,out=OUTPUT):
    source=Path(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    patches,registry,annual,receipt,hashes=verify_sources(source)
    source_annual_stage_audit(patches,annual)
    linked=attach_validated_births(patches,registry)
    events=event_table(linked)
    summary=by_replicate(linked,events)
    for fname,frame in [("recolonization_event_followup.csv",events),
                        ("recolonization_replicate_summary.csv",summary)]:
        frame.to_csv(out/fname,index=False)
    cohort=(summary.groupby(["mobility","reverse","guild"])
       .agg(n_seeds=("seed","nunique"),
            mean_recolonizations=("n_recolonization_events","mean"),
            mean_recolonizations_with_migrant=("n_recolonizations_with_survivor_movements","mean"),
            total_censored_second_followup=("n_recolonizations_censored_at_second_followup","sum"),
            total_observable_two_followup=("n_eligible_two_followups","sum"),
            total_retained_two_followup=("n_retained_two_followups","sum"),
            total_persistent_and_reproducing=("n_two_census_persistent_plus_local_births","sum"),
            total_with_postreturn_local_births=("n_with_postreturn_local_births","sum"),
            total_with_external_natal_parent_births=("n_with_postreturn_external_natal_parent_births","sum"))
       .reset_index())
    if not cohort.n_seeds.eq(4).all() or len(cohort)!=12:
        raise AssertionError("Incomplete four independent stochastic runs per condition")
    cohort.to_csv(out/"recolonization_cohort_conditions.csv",index=False)
    record=dict(status="SOURCE_BACKED_RECOLONIZATION_PERSISTENCE_AND_DURABLE_PARENT_IDENTITIES",
                source_run_id=41186773263,source_rng_kernel_unchanged=True,
                numerical_simulations_reused_not_new=True,
                n_source_event_rows=len(events),n_arms=len(summary)//3,
                n_ever_lived_individual_records=len(registry),
                annual_births_exactly_reconciled_to_all_children=True,
                stages_F_D_reconciled_with_original_annual_totals=True,
                two_year_followups_censored_not_labeled_failure=True,
                persistence_plus_birth_not_offspring_survival_or_true_establishment=True,
                natal_parent_source_is_not_two_parent_genetic_pedigree=True,
                original_naamp_spatial_recurrence_not_tested=True,
                original_genuine_80year_model_not_same_seven_stage_abm=True,
                source_sha256=hashes,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/"receipt.json").write_text(json.dumps(record,indent=2)+"\n")
    print("ANNUAL_RECOLONIZATION_FOLLOWUP_CONDITIONS\n"+cohort.to_string(index=False),flush=True)
    print("ANNUAL_RECOLONIZATION_ALL_EPISODES\n"+events.to_string(index=False),flush=True)
    return events,summary,cohort,record


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--source",type=Path,default=SOURCE)
    p.add_argument("--out",type=Path,default=OUTPUT)
    v=p.parse_args()
    if not v.run:p.error("Explicit --run required")
    run(v.source,v.out)
