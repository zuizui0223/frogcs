"""Same-rate S larval vs adult dispersal without modifying frogcs ABM/PDE.

Stage×coefficient = {S_larva, S_adult} × {.05,.22} per model-year
diffusion; all other guilds/stages immobile. Not equating actual migration
flux or claiming aquatic between-pond migration occurs in nature.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from multigeneration_reversal import Rates,STAGES,SL,SA,initial_grid,simulate_pde
from tracked_spatial_pedigree import simulate_traced_abm,SEEDS,YEARS,DT,ROOT
from assess_recolonization_establishment import (
    attach_validated_births,event_table,source_annual_stage_audit
)
from run_stage_specific_dispersal_ablation import actual_mode_summary

OUT=ROOT/"research/results/equal_rate_S_stage_dispersal_20261031"
STAGES_TO_COMPARE={"S_larva":SL,"S_adult":SA}
DIFFUSION_VALUES={"005":.05,"022":.22}
NEW_MODES=tuple(f"{stage}_{rate}" for stage in STAGES_TO_COMPARE
                for rate in DIFFUSION_VALUES)


def equal_rate_modes(name,base=Rates()):
    if name not in NEW_MODES:raise ValueError("Unknown fixed S stage × diffusion rate")
    stage_name,code=name.rsplit("_",1)
    value=DIFFUSION_VALUES[code]
    index=STAGES_TO_COMPARE[stage_name]
    entries=[0.]*len(STAGES);entries[index]=value
    result=replace(base,diffusion=tuple(entries))
    if np.count_nonzero(result.diffusion)!=1 or result.diffusion[index]!=value:
        raise AssertionError("Source S larval/adult single-stage dispersal altered")
    return result


def run(mode,years=YEARS,dt=DT,seeds=SEEDS,out=OUT):
    if mode not in NEW_MODES or tuple(seeds)!=SEEDS or years!=YEARS or dt!=DT:
        raise ValueError("Predeclared identical 20-y, four-seed two-stage-per-capita comparison required")
    out.mkdir(parents=True,exist_ok=True)
    x,v=initial_grid(8)
    p=equal_rate_modes(mode)
    stages=set([STAGES[np.flatnonzero(np.asarray(p.diffusion)>0)[0]]])
    annual=[];patch=[];registry=[];movement=[];lineage=[];events=[];pde=[]
    for reverse in (False,True):
        densities,_=simulate_pde(x,v,p,years=years,dt=dt,reverse=reverse)
        densities["mode"]=mode
        pde.append(densities)
        for seed in seeds:
            one=simulate_traced_abm(x,v,p,years=years,dt=dt,
                                    reverse=reverse,seed=seed)
            data={}
            for key in ("annual","patch","registry","movements","lineages"):
                q=one[key].copy()
                for k,val in (("mobility",mode),("reverse",reverse),("seed",seed)):
                    q[k]=val
                data[key]=q
            linked=attach_validated_births(data["patch"],data["registry"])
            source_annual_stage_audit(linked,data["annual"])
            e=event_table(linked)
            if len(e):events.append(e)
            annual.append(data["annual"])
            patch.append(linked)
            registry.append(data["registry"])
            if len(data["movements"]):
                if not set(data["movements"].stage).issubset(stages):
                    raise AssertionError("Stage other than named S-stage dispersed")
                movement.append(data["movements"])
            lineage.append(data["lineages"])
            print("EQUAL_S_RATE_ABM_COMPLETE",mode,"reverse",reverse,
                  "seed",seed,"S-year20",int(linked[
                      (linked.year==years)&(linked.guild=="S")].occupied.sum()),
                  "recolonizations",len(e),flush=True)
    frames=dict(annual=pd.concat(annual,ignore_index=True),
                patch=pd.concat(patch,ignore_index=True),
                registry=pd.concat(registry,ignore_index=True),
                movement=pd.concat(movement,ignore_index=True) if movement else pd.DataFrame(),
                lineage=pd.concat(lineage,ignore_index=True),
                events=pd.concat(events,ignore_index=True) if events else pd.DataFrame(),
                pde=pd.concat(pde,ignore_index=True))
    summary=actual_mode_summary(frames["patch"],frames["events"],years)
    if (len(summary)!=24 or len(frames["annual"])!=160
        or len(frames["patch"])!=8*21*8*3):
        raise AssertionError("Original four-seed/guild/stage data grain incomplete")
    for name,frame in [("seed_summary",summary),("reoccupation_followup",frames["events"]),
                       ("lineage",frames["lineage"]),("annual",frames["annual"]),
                       ("patch",frames["patch"]),("registry",frames["registry"]),
                       ("observed_movements",frames["movement"]),
                       ("pde",frames["pde"])]:
        gz=name in ("patch","registry","observed_movements")
        frame.to_csv(out/(mode+"_"+name+".csv"+(".gz" if gz else "")),
                     index=False,compression={"method":"gzip","mtime":0} if gz else None)
    receipt=dict(status="UNMODIFIED_SEVEN_STAGE_ABM_EQUAL_PER_CAPITA_S_STAGE_MIGRATION",
        mode=mode,enabled_stage=next(iter(stages)),
        chosen_diffusion=float(max(p.diffusion)),
        original_source_diffusion_rates=list(Rates().diffusion),
        modified_source_diffusion_rates=list(p.diffusion),
        years=years,dt=dt,seed_list=list(seeds),
        n_new_actual_stochastic_runs=8,
        n_original_pde_density_runs=2,
        n_simulated_individuals_ever_alive=len(frames["registry"]),
        n_annual_census_reoccupations=len(frames["events"]),
        stage_rates_equal_but_realized_migrant_flux_can_differ=True,
        original_ABM_kernel_unchanged=True,
        source_ABM_SHA256=hashlib.sha256(
            Path(__file__).with_name("multigeneration_reversal.py").read_bytes()).hexdigest(),
        source_tracing_SHA256=hashlib.sha256(
            Path(__file__).with_name("tracked_spatial_pedigree.py").read_bytes()).hexdigest(),
        no_field_dispersal_rates_or_genetic_parentage=True,
        distinct_from_genuine_80y_main_ABC=True,
        script_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(mode+"_receipt.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    print("S_SAME_RATE_STAGE_ABLATION_SEED_RESULTS\n"+summary.to_string(index=False),flush=True)
    return summary,receipt


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--mode",choices=NEW_MODES,required=True)
    args=a.parse_args()
    if not args.run:a.error("Explicit --run required")
    run(args.mode)
