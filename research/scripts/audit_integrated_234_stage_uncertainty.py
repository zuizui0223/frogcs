"""Independent matched-source uncertainty audit for PR160 stage refuges.

Input: original successful GitHub Action #41262102436 artifact
  integrated-234-paired-stage-vegetation/posterior_paired_plant_stage.csv

This does NOT run biology, refit a model, infer a field posterior or treat the
three replays of the same source ID as independent data. The 96 source draw IDs
are the resampling units, selected as 32 per ORIGINAL stage stratum. Resampling
is stratified within those 3 original source strata. Within-source effects
across the three counterfactual stages are kept paired.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_STAGE_ACCEPTS=(317,265,212)
N_SELECTED_PER_STRATUM=32
N_SOURCES=96
AXES=("cover_SF","cover_DS")
METRICS=("delta_mean_log_F_B","delta_pass")
BOOTSTRAP_SEED=20261101
N_BOOTSTRAP=20000
ZERO_TOL=1e-10


def validate_source(frame):
    key=["source_draw_id","axis","counterfactual_context"]
    if (len(frame)!=N_SOURCES*len(AXES)*3 or
        frame.duplicated(key).any() or
        set(frame.axis)!=set(AXES) or
        set(frame.counterfactual_context)!={0,1,2}):
        raise AssertionError("Source matched 96*2*3 counterfactuals incomplete")
    src=frame[["source_draw_id","original_context","source_sample_weight"]].drop_duplicates()
    if len(src)!=N_SOURCES or src.source_draw_id.nunique()!=N_SOURCES:
        raise AssertionError("Original 96 source IDs not unique")
    if (set(src.original_context)!={0,1,2} or
        not src.groupby("original_context").size().eq(N_SELECTED_PER_STRATUM).all()):
        raise AssertionError("One or more original selection strata missing")
    for original_context,g in src.groupby("original_context"):
        expected=SOURCE_STAGE_ACCEPTS[int(original_context)]/sum(SOURCE_STAGE_ACCEPTS)/N_SELECTED_PER_STRATUM
        if not np.allclose(g.source_sample_weight,expected,rtol=0,atol=1e-12):
            raise AssertionError("Original accepted-source mass not preserved")
    if not np.isclose(src.source_sample_weight.sum(),1.,atol=1e-12):
        raise AssertionError("All source weights must sum to 1")
    if not frame.groupby(["source_draw_id","axis"]).counterfactual_context.nunique().eq(3).all():
        raise AssertionError("Source counterfactual stage matching incomplete")
    if not frame.groupby(["source_draw_id","counterfactual_context"])["axis"].nunique().eq(2).all():
        raise AssertionError("Source plant-contrast matching incomplete")
    for m in METRICS:
        if m not in frame or not np.isfinite(frame[m]).all():
            raise AssertionError("Missing/invalid source statistic "+m)
    if not set(frame.delta_pass.unique()).issubset({-1,0,1}):
        raise AssertionError("Four-sign classification may only change -1/0/1")
    return src.sort_values("source_draw_id").reset_index(drop=True)


def stratified_source_indices(src,seed=BOOTSTRAP_SEED,n=N_BOOTSTRAP):
    original=src.original_context.to_numpy(int)
    rng=np.random.default_rng(seed)
    draws=np.zeros((n,len(src)),dtype=np.int32)
    for context in range(3):
        pos=np.flatnonzero(original==context)
        if len(pos)!=N_SELECTED_PER_STRATUM:
            raise AssertionError("Original draw sample must be 32 per stratum")
        draws[:,pos]=pos[rng.integers(0,len(pos),size=(n,len(pos)))]
    return draws


def analyse(frame, n_bootstrap=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    src=validate_source(frame)
    ids=src.source_draw_id.to_numpy()
    weights=src.source_sample_weight.to_numpy(float)
    sampled=stratified_source_indices(src,seed=seed,n=n_bootstrap)
    sampled_weight=weights[sampled]
    sampled_weight/=sampled_weight.sum(axis=1,keepdims=True)
    rows=[]
    for axis in AXES:
        selected=frame[frame.axis.eq(axis)]
        for metric in METRICS:
            wide=selected.pivot(index="source_draw_id",columns="counterfactual_context",
                                values=metric).loc[ids]
            if wide.shape!=(N_SOURCES,3) or not np.isfinite(wide.to_numpy()).all():
                raise AssertionError("Source/context response matrix incomplete")
            mat=wide.to_numpy(float)
            # Source labels remain shared across all three counterfactual contexts.
            for label,values in [
                *((str(c),mat[:,c]) for c in (0,1,2)),
                ("1-0",mat[:,1]-mat[:,0]),
                ("2-0",mat[:,2]-mat[:,0]),
                ("2-1",mat[:,2]-mat[:,1]),
            ]:
                bs=(values[sampled]*sampled_weight).sum(axis=1)
                lo,hi=np.quantile(bs,[.025,.975])
                rows.append(dict(
                    axis=axis,stage_contrast=label,metric=metric,
                    weighted_mean=float(np.dot(values,weights)),
                    source_bootstrap_95_low=float(lo),
                    source_bootstrap_95_high=float(hi),
                    n_source_ids=N_SOURCES,
                    n_positive=int(np.sum(values>ZERO_TOL)),
                    n_negative=int(np.sum(values < -ZERO_TOL)),
                    n_zero=int(np.sum(np.abs(values)<=ZERO_TOL)),
                    bootstrap_replicates=n_bootstrap,
                    bootstrap_unit="original accepted source M,T,theta draw_id",
                    uncertainty_type="conditional synthetic prior/sample Monte Carlo only",
                ))
    result=pd.DataFrame(rows)
    if len(result)!=len(AXES)*len(METRICS)*6:
        raise AssertionError("Incomplete matched source effect/cross-stage rows")
    return result


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--paired",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    cli.add_argument("--bootstrap",type=int,default=N_BOOTSTRAP)
    a=cli.parse_args()
    if a.bootstrap < 500:
        raise ValueError("Stratified Monte Carlo resampling requires >=500 repeats")
    frame=pd.read_csv(a.paired)
    result=analyse(frame,n_bootstrap=a.bootstrap)
    a.output.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.output/"source_weighted_stage_interventions_bootstrap.csv",index=False)
    receipt={
        "status":"PR160_MATCHED_SOURCE_WEIGHTED_STAGE_MC_AUDITED",
        "source_workflow_run_id":41262102436,
        "source_artifact":"integrated-234-paired-stage-vegetation",
        "n_source_draws":N_SOURCES,
        "original_accepted_context_counts":list(SOURCE_STAGE_ACCEPTS),
        "original_sample_strata_size":N_SELECTED_PER_STRATUM,
        "paired_intervention_rows":len(frame),
        "bootstrap_seed":BOOTSTRAP_SEED,
        "bootstrap_repetitions":a.bootstrap,
        "source_identity_cross_stage_preserved":True,
        "field_posterior":False,
        "actual_wetland_longrun_forecast":False,
        "note":"Sample/bootstrap uncertainty is not uncertainty about real trophic causation.",
    }
    (a.output/"audit_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PR160_SOURCE_WEIGHTED_STAGE_AUDIT_SUCCESS",json.dumps(receipt),flush=True)
    print(result[["axis","stage_contrast","metric","weighted_mean",
                  "source_bootstrap_95_low","source_bootstrap_95_high"]].to_string(index=False),flush=True)
    return result


if __name__=="__main__":
    main()
