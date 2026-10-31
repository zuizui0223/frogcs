"""Stage-conditional dispersal ablation using the source seven-stage stochastic ABM.

No new ABM hazards, maturation, birth equations or randomness. The only
intervention is which source-stage diffusion entries are set to zero. All
new 20-y model outputs are retained by adult/aquatic/S-only mobility mode.
Original off/all mobility source was independently run earlier and is reused
by later aggregation, not counted as new simulations.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from multigeneration_reversal import (
    STAGES,FT,FA,SL,SA,DN,DE,DA,Rates,initial_grid,simulate_pde
)
from tracked_spatial_pedigree import simulate_traced_abm,SEEDS,YEARS,DT,ROOT,GUILDS
from assess_recolonization_establishment import (
    attach_validated_births,event_table,source_annual_stage_audit
)

OUT=ROOT/"research/results/stage_specific_dispersal_pom_20261031"
MODES=("off","original","adult_only","aquatic_only","S_only")
NEW_MODES=("adult_only","aquatic_only","S_only")
MOBILITY_STAGES={
    "off":(),
    "original":tuple(range(len(STAGES))),
    "adult_only":(FA,SA,DA),
    "aquatic_only":(FT,SL,DN),
    "S_only":(SL,SA)
}


def stage_mobility_rates(name,base=Rates()):
    if name not in MODES:raise ValueError("Unknown source life-stage movement regime")
    allowed=MOBILITY_STAGES[name]
    diffusion=tuple(float(v) if i in allowed else 0.
                    for i,v in enumerate(base.diffusion))
    result=replace(base,diffusion=diffusion)
    if name=="original" and result.diffusion!=base.diffusion:
        raise AssertionError("Original mobility intervention must be exactly identity")
    if name=="off" and any(diffusion):
        raise AssertionError("No-dispersal control not zero")
    return result


def actual_mode_summary(patch,events,year=YEARS):
    rows=[]
    group=["mobility","reverse","seed","guild"]
    for key,g in patch.groupby(group,sort=True):
        annual=g.groupby("year").agg(n_occupied=("occupied","sum"),
                                     extinctions=("locally_extinct","sum"),
                                     returns=("recolonized","sum"),
                                     moves=("known_surviving_immigrant_arrivals","sum"))
        if not np.array_equal(annual.index.to_numpy(int),np.arange(year+1)):
            raise AssertionError("Missing census in source-ABM postprocessing")
        meta=dict(zip(group,key))
        f=np.ones(len(events),bool)
        for k,val in meta.items():
            if k in events:
                f &= events[k].to_numpy()==val
        e=events.loc[f]
        meta.update(dict(year_end=year,n_occupied_year_end=int(annual.loc[year,"n_occupied"]),
                         n_local_extinction_events=int(annual.extinctions.sum()),
                         n_recolonizations=int(annual.returns.sum()),
                         n_seen_survivor_movements=int(annual.moves.sum()),
                         n_return_events_recovered=len(e),
                         n_recolonizations_witnessed_by_survivor_move=int(
                            (e.observed_surviving_arrivals_in_return_year>0).sum()) if len(e) else 0,
                         n_one_year_followup_eligible=int(
                             e.one_census_followup_observed.sum()) if len(e) else 0,
                         n_one_year_retained=int(
                             e.retained_at_one_followup.fillna(False).astype(int).sum()) if len(e) else 0,
                         n_two_year_followup_eligible=int(
                             e.two_census_followups_observed.sum()) if len(e) else 0,
                         n_two_year_retained=int(
                             e.retained_at_two_followups.fillna(False).astype(int).sum()) if len(e) else 0,
                         n_two_census_persistence_plus_local_births=int(
                             e.two_census_persistence_and_postreturn_births.fillna(False).astype(int).sum()) if len(e) else 0,
                         n_return_events_right_censored_at_2years=int(
                             (~e.two_census_followups_observed).sum()) if len(e) else 0,
                         n_with_external_natal_parent_births=int(
                             (e.births_with_external_natal_parent_in_postreturn_year.fillna(0)>0).sum()) if len(e) else 0))
        if meta["n_recolonizations"]!=len(e):
            raise AssertionError("Lost one annual reoccupation event")
        rows.append(meta)
    out=pd.DataFrame(rows)
    if len(out)!=2*len(SEEDS)*3:
        raise AssertionError("Incomplete original per-guild stochastic arms")
    return out


def run(mode,years=YEARS,dt=DT,seeds=SEEDS,out=OUT):
    if mode not in NEW_MODES:
        raise ValueError("New experiment must not rerun preexisting original/off modes")
    if len(seeds)!=4 or tuple(seeds)!=SEEDS or years!=YEARS or dt!=DT:
        raise ValueError("Prespecified identical 20-y, four-seed, dt=.05 setting required")
    out.mkdir(parents=True,exist_ok=True)
    init,vegetation=initial_grid(8)
    original=Rates()
    rates=stage_mobility_rates(mode,original)
    annual=[];patch=[];registry=[];movement=[];lineage=[];episodes=[];pde=[]
    for reverse in (False,True):
        density,_=simulate_pde(init,vegetation,rates,years=years,
                                dt=dt,reverse=reverse)
        density["mobility"]=mode
        pde.append(density)
        for seed in seeds:
            source=simulate_traced_abm(init,vegetation,rates,years=years,
                                       dt=dt,reverse=reverse,seed=seed)
            outputs={}
            for key in ("annual","patch","registry","movements","lineages"):
                x=source[key].copy()
                for k,v in (("mobility",mode),("reverse",reverse),("seed",seed)):
                    x[k]=v
                outputs[key]=x
            linked=attach_validated_births(outputs["patch"],outputs["registry"])
            e=event_table(linked)
            source_annual_stage_audit(linked,outputs["annual"])
            if len(e):episodes.append(e)
            annual.append(outputs["annual"])
            patch.append(linked)
            registry.append(outputs["registry"])
            if len(outputs["movements"]):
                movement.append(outputs["movements"])
            lineage.append(outputs["lineages"])
            permitted={STAGES[i] for i in MOBILITY_STAGES[mode]}
            if len(outputs["movements"]) and not set(outputs["movements"].stage).issubset(permitted):
                raise AssertionError("Stage moved despite diffusion zero under predeclared ablation")
            print("STAGE_SPECIFIC_ABM_COMPLETE",mode,reverse,seed,
                  "S patches at year20",int(linked[
                      (linked.year==years)&(linked.guild=="S")].occupied.sum()),
                  "recolonizations",len(e),flush=True)
    annual=pd.concat(annual,ignore_index=True)
    patch=pd.concat(patch,ignore_index=True)
    registry=pd.concat(registry,ignore_index=True)
    lineage=pd.concat(lineage,ignore_index=True)
    movements=pd.concat(movement,ignore_index=True) if movement else pd.DataFrame()
    events=pd.concat(episodes,ignore_index=True) if episodes else pd.DataFrame()
    summary=actual_mode_summary(patch,events,years)
    if len(annual)!=years*2*len(seeds) or len(patch)!=(years+1)*8*3*2*len(seeds):
        raise AssertionError("Loss of one of the full actual stochastic source trajectories")
    paths=dict(
        summary=out/(mode+"_stage_mobility_seed_summary.csv"),
        episodes=out/(mode+"_recolonization_event_followup.csv"),
        lineage=out/(mode+"_living_lineage_ancestry.csv"),
        registry=out/(mode+"_all_ever_lived_uid_parents.csv.gz"),
        annual=out/(mode+"_annual_population_events.csv"),
        patch=out/(mode+"_patch_occupancy_and_births.csv.gz"),
        movements=out/(mode+"_observed_survivor_movements.csv.gz"),
        pde=out/(mode+"_pde_companion.csv"))
    for key,x in (("summary",summary),("episodes",events),
                  ("lineage",lineage),("registry",registry),
                  ("annual",annual),("patch",patch),
                  ("movements",movements),("pde",pd.concat(pde,ignore_index=True))):
        gz=str(paths[key]).endswith(".gz")
        x.to_csv(paths[key],index=False,
                 compression={"method":"gzip","mtime":0} if gz else None)
    receipt=dict(status="SYNTHETIC_STAGE_SPECIFIC_DISPERSAL_EFFECT_ON_LINEAGE_AND_PATCH_RECOLONIZATION",
                 original_stochastic_kernel_unchanged=True,
                 original_seven_stage_kernel_sha256=hashlib.sha256(
                     Path(__file__).with_name("multigeneration_reversal.py").read_bytes()).hexdigest(),
                 source_pedigree_trace_sha256=hashlib.sha256(
                     Path(__file__).with_name("tracked_spatial_pedigree.py").read_bytes()).hexdigest(),
                 mode=mode,original_rates=original.diffusion,
                 intervention_diffusion_rates=rates.diffusion,
                 enabled_stages=[STAGES[i] for i in MOBILITY_STAGES[mode]],
                 n_new_true_20y_stochastic_arms=2*len(seeds),
                 seed_list=list(seeds),years=years,dt=dt,n_patches=8,
                 total_historical_individual_uids=len(registry),
                 all_birth_uid_and_patch_counts_reconciled=True,
                 n_patch_recolonization_episodes=len(events),
                 original_80year_deterministic_ABC_is_different_kernel=True,
                 no_empirical_pond_connectivity_or_dispersal_fit=True,
                 actual_aquatic_interpond_move_is_not_assumed_biologically_possible=True,
                 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(mode+"_receipt.json")).write_text(
        json.dumps(receipt,indent=2)+"\n")
    print("STAGE_SPECIFIC_DISPERSAL_RESCUE_SUMMARY\n"+summary.to_string(index=False),flush=True)
    return summary,receipt


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--mode",choices=NEW_MODES,required=True)
    v=a.parse_args()
    if not v.run:a.error("Explicit --run required")
    run(v.mode)
