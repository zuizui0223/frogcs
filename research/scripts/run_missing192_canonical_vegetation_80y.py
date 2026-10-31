"""Actually run ONLY the remaining 192 original rate draws for canonical plant cases.

The model is the *unchanged* frogcs season-within-year trophic network and
annual 80-year maturation/recruitment recurrence, under all 18 canonical
plant × risk classes per stage context/handling. No repeated 64 previously
simulated parent draw IDs, no duplicated SF0 behavioral refuge classes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import (
    ROOT,DESIGN,SOURCES,model_names,cube_design,matching_prior_draws,
    summarize_cube_output
)
from model_native_vegetation_abc import (
    legal_plant_inventory,cross_plant_design,annual_recurrence_plant
)
from run_vegetation_cross_ontogeny_80y import (
    CONTEXTS,FAMILIES,replay_frozen_context,original_subsource
)

OUT=ROOT/"research/results/macro_vegetation_full256_canonical_20261031"
N_PARENT=256
N_TO_RUN=192
N_CANONICAL_CLASSES_PER_SHARD=18
N_BIOLOGICAL_RUNS_PER_SHARD=N_CANONICAL_CLASSES_PER_SHARD*N_TO_RUN*2


def new_draws_only():
    parent=matching_prior_draws(256)
    subset=parent.loc[parent.draw.mod(4).ne(0)].copy()
    if len(parent)!=256 or len(subset)!=192 or subset.draw.nunique()!=192:
        raise AssertionError("Wrong count of source-original 256 LHS prior draws")
    if not np.array_equal(subset.draw.to_numpy(dtype=int),
                          np.arange(256)[np.arange(256)%4!=0]):
        raise AssertionError("Rate IDs not the prespecified 192 missing ones")
    return subset


def canonical_cube(original,plant_roles):
    allmodels=cross_plant_design(original,plant_roles)
    # main's catalog() canonicalizes behavior=risk_refuge to behavior=none
    # if cover_SF is switched OFF. We do not run these exact clones.
    models=allmodels[~(allmodels.cover_SF.eq(0)&allmodels.risk.eq(True))].copy()
    if models.structure_id.nunique()!=18:
        raise AssertionError("Canonical vegetation classes must be exactly 18")
    if models.groupby(["structure_id","draw","reverse_on"]).vertex.nunique().ne(8).any():
        raise AssertionError("Lost exact 2×2×2 treatment within canonical plant role")
    if models.duplicated(["structure_id","draw","reverse_on","vertex"]).any():
        raise AssertionError("Overlapping rate draws or source vertices")
    return models


def run(context,family):
    if context not in CONTEXTS or family not in FAMILIES or (context=="original" and family=="baseline"):
        raise ValueError("Reuse archived genuine full256 original/baseline; run only 5 other structural shards")
    OUT.mkdir(parents=True,exist_ok=True)
    models=model_names(pd.read_csv(DESIGN))
    fixed_check=replay_frozen_context(models,context,family)
    prior=new_draws_only()
    original=cube_design(original_subsource(models,context,family),prior)
    cube=canonical_cube(original,legal_plant_inventory())
    if len(cube)!=N_BIOLOGICAL_RUNS_PER_SHARD*8:
        raise AssertionError("Missing a true 80-year process/plant/edge treatment")
    genuine=annual_recurrence_plant(cube)
    summarized=summarize_cube_output(genuine)
    flags=genuine[["structure_id","plant_model","cover_SF","cover_DF",
                   "cover_DS","litter"]].drop_duplicates("structure_id")
    values=summarized.merge(flags,on="structure_id",validate="many_to_one")
    if (len(values)!=N_BIOLOGICAL_RUNS_PER_SHARD or
        values.structure_id.nunique()!=18 or
        values.draw.nunique()!=192 or
        values.groupby(["structure_id","draw"]).reverse_on.nunique().ne(2).any()):
        raise AssertionError("Incomplete actual new biological source run coverage")
    stem=f"{context}__{family}"
    values.to_csv(OUT/(stem+"_missing192_actual_80year_signs.csv.gz"),
                  compression={"method":"gzip","mtime":0},index=False)
    prior.to_csv(OUT/(stem+"_missing192_original_rate_draws.csv"),index=False)
    concise=(values.groupby(["plant_model","risk"]).agg(
        n_original_80year_runs=("matches_log","size"),
        accepted_log=("matches_log","sum"),
        accepted_raw=("matches_raw","sum")).reset_index())
    concise["conditional_accept_log"]=concise.accepted_log/concise.n_original_80year_runs
    concise["conditional_accept_raw"]=concise.accepted_raw/concise.n_original_80year_runs
    concise.to_csv(OUT/(stem+"_missing192_model_sign_summary.csv"),index=False)
    receipt=dict(status="ACTUAL_80Y_192_MISSING_DRAWS_ONLY_FOR_MAIN_108_CANONICAL_PLANT_MODELS",
                 context=context,family=family,
                 n_independent_missing_rate_draws=192,
                 reused_previous64_not_recomputed=True,
                 previously_completed_original_baseline_full256_not_recomputed=True,
                 n_original_80year_runs=len(values),
                 n_8vertex_source_treatments=len(genuine),
                 n_canonical_distinct_classes=18,
                 original_archive_and_old_annual_replay=fixed_check,
                 source_original_rate_IDs=sorted(int(x) for x in prior.draw),
                 biological_parameter_priors_hypothetical=True,
                 independent_field_causal_evidence=False,
                 source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [DESIGN,*SOURCES]},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/(stem+"_receipt.json")).write_text(
        json.dumps(receipt,indent=2)+"\n")
    print("COMPLETE_TRUE_NEW_80Y_SOURCE",stem,len(values),"rate ids",
          prior.draw.min(),prior.draw.max(),flush=True)
    print(concise.to_string(index=False),flush=True)
    return values,concise


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--context",required=True,choices=CONTEXTS)
    p.add_argument("--family",required=True,choices=FAMILIES)
    a=p.parse_args()
    if not a.run:p.error("Explicit --run required")
    run(a.context,a.family)
