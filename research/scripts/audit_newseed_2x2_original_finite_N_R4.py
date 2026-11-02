"""Independent original-source inventory and matched R4 population consequences.

All full 24576 genuinely simulated population arms, 16 untouched shard SHA
receipts, original PR161 3072 deterministic source labels and fixed newseed
rates are checked before interpretation. Cluster Monte Carlo unit is 256
original canonical model backgrounds, NOT 3 stages, 2 seeds or 8 patch cells.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confirmatory_2x2_vegetation_predator_switch import original_draws
from run_newseed_2x2_original_finite_N_R4 import (
    N_SHARDS, SEEDS, EXPECTED_ARMS_PER_BASE, SOURCE_MAIN_SHA,
    SOURCE_ORIGINAL_RUN, SOURCE_BRANCH_PR161, make_all_arms,
)

N_BASE=256
N_EXPECTED=24576
BOOT=10000
BOOT_SEED=20261125
STAGES=(0,1,2)
ARMS=("00","10","01","11")
Q=(3,12)
MOVE=(0,1)
METRICS=(
   "occupied_year80","occupied_mean_year61_80",
   "mean_F_count_year61_80","recolonization_events_80y",
   "local_extinction_events_80y","movement_assisted_returns_80y",
   "all8_occupied_year80","zero8_occupied_year80",
)
CONTRASTS={
    "both_vs_neither":("11","00"),
    "shelter_only_vs_neither":("10","00"),
    "D_support_only_vs_neither":("01","00"),
    "both_vs_shelter_only":("11","10"),
    "both_vs_support_only":("11","01"),
}
SOURCE_CHECK_FIELDS=(
    "draw_id","model_id","source_id","context_id","arm",
    "attack","rho","conversion","strength","refuge_order","gate_code"
)


def require(value,message):
    if not bool(value):
        raise AssertionError(message)


def load_sources(root):
    root=Path(root)
    sources=[]
    recs=[]
    for shard in range(N_SHARDS):
        paths=list(root.rglob(f"newseed_finite_N_shard_{shard:02d}_receipt.json"))
        require(len(paths)==1,f"Missing original finiteN biological source receipt for shard {shard}")
        r=json.loads(paths[0].read_text())
        fn=paths[0].parent/f"newseed_finite_N_true80_shard_{shard:02d}.csv.gz"
        require(r["status"]=="PR161_ORIGINAL_MODEL_FINITE_N_80Y_COMPLETE" and
                r["source_main_biology_sha"]==SOURCE_MAIN_SHA and
                r["source_PR161_true80_audit_run"]==SOURCE_ORIGINAL_RUN and
                r["source_PR161_branch_sha"]==SOURCE_BRANCH_PR161 and
                r["source_base_backgrounds"]==16 and
                r["source_rows"]==1536 and
                r["source_arms_per_base"]==EXPECTED_ARMS_PER_BASE and
                r["shard"]==shard and r["years"]==80 and
                r["movement_fraction"]==.15 and
                r["external_immigration_on"] is True and
                r["predation_S_to_F_on"] is True and
                r["count_scales"]==[3,12] and
                r["movement_levels"]==[0,1] and
                r["process_seed_labels"]==list(SEEDS) and
                r["original_main_expected_value_replay_max_error"]<=1e-11,
                "Original finiteN source model and biological input receipt mismatched")
        require(fn.is_file() and
                hashlib.sha256(fn.read_bytes()).hexdigest()==r["file_sha256"],
                "Original 80-year source model file or SHA changed")
        x=pd.read_csv(fn,dtype={"arm":str})
        require(len(x)==1536 and x.source_id.mod(N_SHARDS).eq(shard).all()
                and not x.duplicated(["draw_id","q","move_on","seed"]).any(),
                "Source split incomplete or duplicate stochastic result")
        sources.append(x)
        recs.append(r)
    data=pd.concat(sources,ignore_index=True).sort_values(
        ["draw_id","q","move_on","seed"]).reset_index(drop=True)
    require(len(data)==N_EXPECTED and data.source_id.nunique()==N_BASE and
            data.draw_id.nunique()==N_BASE*12 and
            not data.duplicated(["draw_id","q","move_on","seed"]).any(),
            "Original newseed 24,576 arms not complete")
    require(data.groupby(["source_id","context_id","arm"]).size().eq(8).all()
            and data.groupby(["source_id","context_id","q","move_on","seed"]).arm.nunique().eq(4).all(),
            "One matched plant 2x2 cohort intervention arm is missing")
    require(set(data.context_id)==set(STAGES) and set(data.arm)==set(ARMS)
            and set(data.q)==set(Q) and set(data.move_on)==set(MOVE)
            and set(data.seed)==set(SEEDS) and data.edge_SF_on.eq(1).all(),
            "Unplanned arm, stage or original predation edge in finiteN source")
    final=data.occupied_year80.to_numpy(dtype=float)
    mean=data.occupied_mean_year61_80.to_numpy(dtype=float)
    require(np.isfinite(final).all() and np.isfinite(mean).all() and
            (final>=0).all() and (final<=8).all() and
            np.array_equal(final,np.rint(final)),
            "Year80 final source occupied patches must be exact integers within 0–8")
    require((mean>=-1e-10).all() and (mean<=8+1e-10).all(),
            "Original 20-year mean patch occupancy exceeds 0–8 after float tolerance")
    for metric in ("recolonization_events_80y","local_extinction_events_80y",
                   "movement_assisted_returns_80y"):
        require(data[metric].ge(0).all() and
                np.allclose(data[metric],np.rint(data[metric]),rtol=0,atol=1e-12),
                "Original individual model source movement/return ledger invalid")
    require(data.loc[data.move_on.eq(0),"movement_assisted_returns_80y"].eq(0).all(),
            "Nonmoving original arm logged movement assisted local return")
    require(data.movement_assisted_returns_80y.le(data.recolonization_events_80y).all(),
            "Movement assisted returns cannot exceed true patch returns")
    return data,recs


def verify_link(data, original_PR161_source):
    m,p,nuisance=original_draws()
    old=pd.read_csv(original_PR161_source,dtype={"arm":str}).sort_values("draw_id")
    require(len(old)==3072 and old.draw_id.eq(np.arange(3072)).all()
            and old.source_id.nunique()==N_BASE and
            set(old.arm)==set(ARMS) and
            old.groupby(["source_id","context_id"]).arm.nunique().eq(4).all(),
            "Archived PR161 independent 3072 prior source missing")
    require(old.model_id.eq(p.model_id).all(),"Archived main 3600 canonical identity changed")
    key=list(SOURCE_CHECK_FIELDS)
    for f in key:
        require(f in old.columns and f in p.columns and
                np.array_equal(old[f].to_numpy(),p[f].to_numpy()),
                "Original PR161 frozen biological source not identical: "+f)
    baseline=data.groupby("draw_id",sort=True).first().reset_index()
    require(len(baseline)==3072,
            "Original PR161 source label missing from new finiteN results")
    for f in key:
        require(np.array_equal(baseline[f].to_numpy(),
                               old[f].to_numpy()),
                "New 80year original finiteN did not use same source feature/rate tuple: "+f)
    require(data.groupby("source_id")["model_id"].nunique().eq(4).all(),
            "New same-source canonical vegetation 2x2 structure changed")
    require(data.groupby("source_id")[["attack","rho","conversion","strength",
                    "refuge_order","gate_code"]].nunique().max().max()==1,
            "Same source rate tuple was not held paired")
    return hashlib.sha256(Path(original_PR161_source).read_bytes()).hexdigest()


def resample_source(x, metric, contrast, kind, q, move, context, draw):
    """Compute paired interventions first, then cluster bootstrap 256 sources."""
    if context=="pooled":
        selection=x[x.q.eq(q) & x.move_on.eq(move)]
    else:
        selection=x[x.q.eq(q) & x.move_on.eq(move) & x.context_id.eq(int(context))]
    # Average process seeds within each canonical source×context×arm.
    grouped=(selection.groupby(["source_id","context_id","arm"],sort=True)
                    [metric].mean().reset_index())
    wide=grouped.pivot(index=["source_id","context_id"],columns="arm",values=metric)
    require(set(wide.columns)==set(ARMS),"One plant factorial arm absent from source")
    wide=wide.reindex(columns=list(ARMS)).sort_index()
    if kind=="arm":
        values=wide[contrast]
    elif kind=="pair":
        upper,lower=CONTRASTS[contrast]
        values=wide[upper]-wide[lower]
    elif kind=="synergy":
        values=wide["11"]-wide["10"]-wide["01"]+wide["00"]
    else:
        raise ValueError(kind)
    per=values.unstack("context_id").reindex(range(N_BASE))
    require(per.shape==(N_BASE,3) and np.isfinite(per.to_numpy()).all(),
            "A source stage/plant/repetition result missing")
    v=per.mean(axis=1).to_numpy(float) if context=="pooled" else per[int(context)].to_numpy(float)
    estimate=float(v.mean())
    interval=np.quantile(v[draw].mean(axis=1),[.025,.975])
    return dict(q=int(q),move_on=int(move),stage=str(context),metric=metric,
                kind=kind,contrast=contrast,mean=estimate,
                mc95_low=float(interval[0]),mc95_high=float(interval[1]),
                n_base_source_clusters=N_BASE,n_process_seed_labels=len(SEEDS))


def summarize(data):
    rng=np.random.default_rng(BOOT_SEED)
    draw=rng.integers(0,N_BASE,size=(BOOT,N_BASE))
    rows=[]
    for metric in METRICS:
        for q in Q:
            for move in MOVE:
                for ctx in ("0","1","2","pooled"):
                    for arm in ARMS:
                        rows.append(resample_source(data,metric,arm,"arm",q,move,ctx,draw))
                    for label in CONTRASTS:
                        rows.append(resample_source(data,metric,label,"pair",q,move,ctx,draw))
                    rows.append(resample_source(data,metric,"2x2_factorial","synergy",
                                                q,move,ctx,draw))
    d=pd.DataFrame(rows)
    require(len(d)==len(METRICS)*len(Q)*len(MOVE)*4*(4+len(CONTRASTS)+1),
            "Incomplete source original q×movement×stage×plant 2x2 estimands")
    require(not d.duplicated(["q","move_on","stage","metric","kind","contrast"]).any(),
            "Duplicated source-based R4 population estimator")
    # Movement effect source pairs, including that the movement condition is
    # treated as a same-source difference; original RNG draws differ by
    # move_on in the unmodified source.
    movement=[]
    for metric in METRICS:
        for q in Q:
            for ctx in ("0","1","2","pooled"):
                sel=data[data.q.eq(q)]
                g=(sel.groupby(["source_id","context_id","arm","move_on"],sort=True)
                         [metric].mean().reset_index())
                pivot=g.pivot(index=["source_id","context_id","arm"],columns="move_on",values=metric)
                require(set(pivot.columns)==set(MOVE),"One movement arm missing")
                effect=(pivot[1]-pivot[0]).unstack("arm").reindex(columns=list(ARMS))
                require(not effect.isna().any().any(),"Missing original source movement effect")
                candidates={
                    "movement_effect_00":effect["00"],
                    "movement_effect_11":effect["11"],
                    "both_vs_neither_movement_interaction":effect["11"]-effect["00"],
                    "factorial_movement_interaction":
                         effect["11"]-effect["10"]-effect["01"]+effect["00"],
                }
                for label,s in candidates.items():
                    w=s.unstack("context_id").reindex(range(N_BASE))
                    require(w.shape==(N_BASE,3) and np.isfinite(w.to_numpy()).all(),
                            "Selected source movement contrast lacks context")
                    z=w.mean(axis=1).to_numpy(float) if ctx=="pooled" else w[int(ctx)].to_numpy(float)
                    mc=np.quantile(z[draw].mean(axis=1),[.025,.975])
                    movement.append(dict(q=int(q),stage=str(ctx),metric=metric,
                           contrast=label,mean=float(z.mean()),
                           mc95_low=float(mc[0]),mc95_high=float(mc[1]),
                           n_base_source_clusters=N_BASE))
    m=pd.DataFrame(movement)
    require(len(m)==len(METRICS)*2*4*4,
            "Original finiteN 2x2 movement influence summary incomplete")
    return d,m


def audit(root,PR161_source,out):
    a,recs=load_sources(root)
    prior_sha=verify_link(a,PR161_source)
    table,movement=summarize(a)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"R4_full_256_model_2x2_occupancy_and_events.csv",index=False)
    movement.to_csv(out/"R4_paired_256_model_plant_and_movement_contrasts.csv",index=False)
    a.to_csv(out/"R4_genuine_all_24576_model_80y_arms.csv.gz",
             index=False,compression={"method":"gzip","mtime":0})
    detail=table[(table.metric.isin(["occupied_year80","recolonization_events_80y",
                                    "mean_F_count_year61_80"])) &
                 (table.kind.isin(["pair","synergy"])) &
                 (table.contrast.isin(["both_vs_neither","2x2_factorial"]))].copy()
    detail.to_csv(out/"R4_plant_two_function_main_contrasts.csv",index=False)
    result=dict(
        status="PR161_SAME256_R4_GENUINE80_FINITE_N_INDEPENDENT_SOURCE_AUDIT_SUCCESS",
        source_PR161_run=SOURCE_ORIGINAL_RUN,
        original_PR161_archived_sha256=prior_sha,
        original_main_sha=SOURCE_MAIN_SHA,
        original_256_source_seed=20261123,
        original_process_seed_labels=list(SEEDS),
        genuine_stochastic_80year_arms=len(a),
        source_distinct_PR161_draws=a.draw_id.nunique(),
        original_canonical_structures=N_BASE,
        repeated_developmental_contexts=len(STAGES),
        original_plant_interventions=list(ARMS),
        original_8patch_model_only=True,
        original_count_scales=list(Q),
        original_movement_conditions=list(MOVE),
        survival_and_population_model_original_PR160_unchanged=True,
        external_immigration_in_original_finiteN_source=True,
        source_rng_key_includes_plant_draw_id=True,
        distinct_matched_biological_rates_not_common_random_streams=True,
        source_cluster_bootstrap_repetitions=BOOT,
        source_cluster_seed=BOOT_SEED,
        n_main_effect_rows=len(table),
        n_movement_effect_rows=len(movement),
        original_shard_receipts=recs,
        factual_NAAMP_predation_estimated=False,
        population_forecast_for_actual_wetlands=False,
        inference="model-native conditional finiteN R4 with artificial 8-patch ring only",
    )
    (out/"R4_256_source_audit_receipt.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("PR161_SAME256_R4_FINITE_N_AUDIT_SUCCESS",
          json.dumps({k:v for k,v in result.items() if k!="original_shard_receipts"}),flush=True)
    print("SOURCE_R4_MAIN_EFFECTS\n"+table.loc[
        table.metric.eq("occupied_year80") & table.stage.eq("pooled") &
        table.contrast.isin(["both_vs_neither","2x2_factorial"]),
        ["q","move_on","metric","kind","contrast","mean","mc95_low","mc95_high"]
        ].to_string(index=False),flush=True)
    print("SOURCE_R4_MOVEMENT_EFFECTS\n"+movement.loc[
        movement.metric.eq("occupied_year80") & movement.stage.eq("pooled"),
        ["q","contrast","mean","mc95_low","mc95_high"]].to_string(index=False),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--original-PR161-source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    x=p.parse_args()
    audit(x.input,x.original_PR161_source,x.output)
