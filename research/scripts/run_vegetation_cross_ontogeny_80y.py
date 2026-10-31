"""Cross three ontogenies × two handling types × 12 legal vegetation mechanisms.

Same original 120-day stage kernel + 80-y delayed recruitment dynamics.
This is *new real model execution* at 64 original 256-prior draw IDs, not
surface warping or artificial acoustic noise.  Original base replay is
a hard gate in every one of the six independent job shards.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from model_native_2x2x2_prior import (
    ROOT,DESIGN,SOURCES,YEARS,WINDOW,DT,model_names,cube_design,
    matching_prior_draws,annual_recurrence_batch,summarize_cube_output
)
from model_native_vegetation_abc import (
    annual_recurrence_plant,legal_plant_inventory,cross_plant_design
)
from run_macro_process_prior_predictive import anchor_values

OUT=ROOT/"research/results/macro_vegetation_cross_ontogeny_20261031"
N_DRAWS=64
CONTEXTS=("original","D_first_S_overtakes","S_first_D_overtakes")
FAMILIES=("baseline","shared_both")
BASE_ROLE="SF1_DF0_DS0_L1"
EPS_F=1e-8
EPS_STD=1e-7


def original_subsource(models,context,family):
    sub=models[(models.context==context)&(models.family==family)].copy()
    if len(sub)!=2 or sub.risk.nunique()!=2:
        raise AssertionError("Frozen ontogeny/handling/risk subcatalog incomplete")
    return sub


def matching_actual_parent_draws(n=N_DRAWS):
    """Subset original 256-draw Latin hypercube without outcome-based selection."""
    parent=matching_prior_draws(256)
    take=parent.iloc[::4].copy()
    if n!=64 or len(take)!=n or take.draw.nunique()!=n:
        raise AssertionError("Expected 64 of the actual 256 prior draw IDs")
    if not np.array_equal(take.draw.to_numpy(int),np.arange(0,256,4)):
        raise AssertionError("Original 256 LHS source draw order changed")
    return take


def replay_frozen_context(models,context,family,years=YEARS,window=WINDOW,dt=DT):
    """One physical plant-role baseline must be identical to independently saved F_B."""
    sub=original_subsource(models,context,family)
    prior=pd.DataFrame([anchor_values()])
    prior["reverse_on"]=0
    original=cube_design(sub,prior,anchor_both_edges=True)
    baseline=legal_plant_inventory()
    baseline=baseline[baseline.plant_model==BASE_ROLE]
    altered=cross_plant_design(original,baseline)
    clone=annual_recurrence_plant(altered,years=years,window=window,dt=dt)
    known=annual_recurrence_batch(original,years=years,window=window,dt=dt)
    idx=["original_case","vegetation","S_source","D_source"]
    a=clone.sort_values(idx).reset_index(drop=True)
    b=known.sort_values(idx).reset_index(drop=True)
    if len(a)!=32 or len(b)!=32 or not np.array_equal(a[idx],b[idx]):
        raise AssertionError("Independent original clone source vertex mismatch")
    diffs={}
    for field,lim in (("F_B",EPS_F),("F_fraction",EPS_F),("F_B_sd",EPS_STD)):
        v=float(abs(a[field]-b[field]).max())
        diffs["clone_"+field]=v
        if v>lim:raise AssertionError("Changed annual model in "+field)
    if (years,window,dt)==(YEARS,WINDOW,DT):
        frozen=pd.concat([pd.read_csv(p) for p in SOURCES],ignore_index=True)
        frozen=frozen[frozen.case.isin(a.original_case.unique()) &
                      frozen.S_source.isin((.25,2.)) &
                      frozen.D_source.isin((.25,2.))].copy()
        frozen=frozen.rename(columns={"case":"original_case"})
        z=frozen.sort_values(idx).reset_index(drop=True)
        if len(z)!=len(a) or not np.allclose(z[idx],a[idx],atol=1e-9,rtol=0):
            raise AssertionError("Archived original model experimental vertices mismatch")
        for field,lim in (("F_B",EPS_F),("F_fraction",EPS_F),("F_B_sd",EPS_STD)):
            v=float(abs(a[field]-z[field]).max())
            diffs["archive_"+field]=v
            if v>lim:raise AssertionError("Archived 80y control not replayed "+field)
    return diffs


def run(context,family):
    if context not in CONTEXTS or family not in FAMILIES:
        raise ValueError("One known original context and handling family needed")
    OUT.mkdir(parents=True,exist_ok=True)
    design=pd.read_csv(DESIGN)
    models=model_names(design)
    orig_check=replay_frozen_context(models,context,family)
    rates=matching_actual_parent_draws()
    base=original_subsource(models,context,family)
    cube=cube_design(base,rates)
    allplants=legal_plant_inventory()
    expanded=cross_plant_design(cube,allplants)
    if len(expanded)!=12*2*64*2*8:
        raise AssertionError("Stage×role×risk×prior×reversal factorial lost")
    result=annual_recurrence_plant(expanded)
    stats=summarize_cube_output(result)
    flags=result[["structure_id","plant_model","cover_SF",
                  "cover_DF","cover_DS","litter"]].drop_duplicates("structure_id")
    stats=stats.merge(flags,on="structure_id",validate="many_to_one")
    if len(stats)!=12*2*64*2 or stats.duplicated(["structure_id","draw","reverse_on"]).any():
        raise AssertionError("All actual annual role responses must be retained")
    for (_,risk),g in stats.groupby(["plant_model","risk"]):
        if len(g)!=64*2 or g.draw.nunique()!=64 or g.reverse_on.nunique()!=2:
            raise AssertionError("Improper paired rate/edge design")
    shard=f"{context}__{family}"
    stats.to_csv(OUT/(shard+"_actual_80year_model_signs.csv.gz"),
                 compression={"method":"gzip","mtime":0},index=False)
    rates.to_csv(OUT/(shard+"_matched_parent256_rate_draws.csv"),index=False)
    compact=(stats.groupby(["plant_model","risk"]).agg(
        log_accepts=("matches_log","sum"),
        raw_accepts=("matches_raw","sum"),
        n_original_simulations=("matches_log","size")).reset_index())
    compact["log_rate"]=compact.log_accepts/compact.n_original_simulations
    compact["raw_rate"]=compact.raw_accepts/compact.n_original_simulations
    compact.to_csv(OUT/(shard+"_role_sign_summary.csv"),index=False)
    receipt=dict(status="TRUE_80Y_CROSS_ONTOGENY_MAIN_LEGAL_PLANT_POM_PILOT",
                 context=context,family=family,
                 n_roles=12,n_risk_states=2,n_reversal_states=2,
                 n_original_demographic_prior_draws=64,
                 n_actual_80year_model_runs=len(stats),
                 n_8vertex_source_treatments=len(result),
                 parent_rate_draw_ids=rates.draw.to_list(),
                 no_rate_fitting_to_target_signs=True,
                 original_baseline_replay=orig_check,
                 original_population_kernel_unchanged=True,
                 main_3600_model_catalog_not_exhaustively_run=True,
                 source_sha256={str(path.relative_to(ROOT)):
                                hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in [DESIGN,*SOURCES,
                                    ROOT/"research/results/final_mechanism_20261027/catalog.csv"]},
                 source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/(shard+"_receipt.json")).write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("CROSSED_PLANT_BIOLOGICAL_RATE_SOURCE_COMPLETE",shard,
          "model_runs",len(stats),flush=True)
    print("CROSSED_PLANT_INTERACTIONS\n"+compact.to_string(index=False),flush=True)
    return stats,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--context",required=True,choices=CONTEXTS)
    p.add_argument("--family",required=True,choices=FAMILIES)
    v=p.parse_args()
    if not v.run:p.error("Explicit --run required")
    run(v.context,v.family)
