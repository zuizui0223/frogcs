"""Independent P1 source audit and 256-source cluster contrasts.

Crucial gate: true80 LS and EL contexts exactly replay the prior successful
PR161 original source at individual M×theta×plant and V/S/D corner level.
Compares non-causal source model timing and aquatic duration separately.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from abc_pom_main3600 import corner_contrasts,accepted_signs
from run_P1_arrival_duration_plant2x2_true80_20261105 import (
    N_SHARDS,N_BASE,N_SCENARIOS,N_VERTICES,TIMING,BOUNDS,
    ARMS,OUTCOME_COLS,YEARS,WINDOW,SOURCE_MODEL_SEED,
    SOURCE_MAIN_SHA,create_factorial
)

BOOT=10000
SEED=20261126
METRICS=("accepted","accepted_and_floor","floor_ok",
         "mean_F_B","mean_log_F_B","H_SF_V1_S2_D2","H_DF_V1_S2_D2",
         "D_F_hazard_share_V1_S2_D2",
         "log_OS","log_OV","log_SV","log_OSV")
V_COLUMNS=("F_B","S_B","D_B","F_fraction","audit_H_SF","audit_H_DF",
           "audit_H_DS","audit_H_SD","minimum_F_survival","minimum_S_survival")
SOURCE_ORIGINAL_PR161=41408471121


def require(ok,msg):
    if not bool(ok):
        raise AssertionError(msg)


def original_shards(root):
    frames=[];verts=[];recs=[]
    root=Path(root)
    for shard in range(N_SHARDS):
        matches=list(root.rglob(f"factorial_original80_shard_{shard:02d}_receipt.json"))
        require(len(matches)==1,"Missing source shard receipt "+str(shard))
        path=matches[0]
        rec=json.loads(path.read_text())
        base=f"factorial_original80_shard_{shard:02d}"
        e=path.parent/(base+"_effects.csv.gz")
        v=path.parent/(base+"_vertices.csv.gz")
        require(rec["status"]=="P1_TRUE80_CONTEXTS_ISOLATED" and
                rec["original_main_sha"]==SOURCE_MAIN_SHA and
                rec["original_PR161_source_seed"]==SOURCE_MODEL_SEED and
                rec["shard"]==shard and rec["source_rows"]==512 and
                rec["source_vertices"]==4096 and
                rec["years"]==80 and rec["window"]==20 and rec["dt"]==.5,
                "Invalid unchanged source biology timing/duration receipt")
        require(e.is_file() and v.is_file() and
                hashlib.sha256(e.read_bytes()).hexdigest()==rec["file_sha256"][e.name] and
                hashlib.sha256(v.read_bytes()).hexdigest()==rec["file_sha256"][v.name],
                "Original P1 SHA256 source file mismatch")
        group=pd.read_csv(e,dtype={"arm":str,"stage_design":str})
        vv=pd.read_csv(v,dtype={"arm":str,"stage_design":str})
        require(len(group)==512 and len(vv)==4096 and
                group.source_id.mod(N_SHARDS).eq(shard).all() and
                vv.source_id.mod(N_SHARDS).eq(shard).all(),
                "Unmatched original model background shard or missing vertices")
        frames.append(group);verts.append(vv);recs.append(rec)
    a=pd.concat(frames,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    v=pd.concat(verts,ignore_index=True).sort_values(
        ["draw_id","vertex"]).reset_index(drop=True)
    require(len(a)==N_SCENARIOS and len(v)==N_VERTICES
            and a.draw_id.eq(np.arange(N_SCENARIOS)).all()
            and np.array_equal(v.draw_id.to_numpy(dtype=int),
                               np.repeat(a.draw_id.to_numpy(dtype=int),8))
            and not v.duplicated(["draw_id","vertex"]).any(),
            "Not the complete original 4096×8 80-year study")
    require(a.source_id.nunique()==N_BASE and set(a.stage_design)==set(BOUNDS)
            and a.groupby(["source_id","stage_design"]).arm.nunique().eq(4).all(),
            "Original 256 background/4 timing/4 plant source incomplete")
    return a,v,recs


def independently_replay_original_source(a,v,old_effect_path,old_vertex_path):
    models,prior=create_factorial()
    indexed=a.set_index("draw_id").loc[prior.draw_id].reset_index()
    for col in ("source_id","model_id","original_draw_id","stage_design",
                "timing_context_id","s_arrival","S_duration","gate_code",
                "attack","rho","conversion","strength","refuge_order","arm"):
        if col not in indexed.columns:
            # Context-specific values exist in the proposal manifest,
            # source output includes only the columns necessary to match.
            if col in ("s_arrival","S_duration"):
                continue
            raise AssertionError("Source context/model input field missing "+col)
        require(np.array_equal(indexed[col].to_numpy(),prior[col].to_numpy()),
                "Original 256 source independent identity changed: "+col)
    original=pd.read_csv(old_effect_path,dtype={"arm":str})
    original_vertices=pd.read_csv(old_vertex_path,dtype={"arm":str})
    require(len(original)==3072 and original.draw_id.nunique()==3072
            and len(original_vertices)==24576,
            "True original PR161 model source is not the archived 3072/24576 result")
    sub=a[a.stage_design.isin(["LS","EL"])].sort_values("original_draw_id")
    orig=original[original.context_id.isin([1,2])].sort_values("draw_id")
    require(len(sub)==2048 and len(orig)==2048 and
            np.array_equal(sub.original_draw_id.to_numpy(),orig.draw_id.to_numpy()),
            "P1 original LS+EL contexts do not map to PR161 1/2 source IDs")
    for field in ("source_id","model_id","arm","attack","rho","conversion",
                  "strength","refuge_order","gate_code"):
        require(np.array_equal(sub[field].to_numpy(),orig[field].to_numpy()),
                "Original PR161 model parameter changed: "+field)
    differences={}
    for col in OUTCOME_COLS:
        q=sub[col].to_numpy(dtype=float)
        o=orig[col].to_numpy(dtype=float)
        tol=float(np.nanmax(np.abs(q-o))) if np.isfinite(q-o).any() else 0.
        require(np.allclose(q,o,rtol=0,atol=1e-9,equal_nan=True),
                f"Original PR161 true80 source replay mismatch {col}: {tol}")
        differences[col]=tol
    require(np.array_equal(sub.accepted.to_numpy(bool),orig.accepted.to_numpy(bool))
            and np.array_equal(sub.floor_ok.to_numpy(bool),orig.floor_ok.to_numpy(bool)),
            "Original PR161 acceptance/survival did not replay")
    legacy_v=v[v.original_draw_id.ge(0)].sort_values(["original_draw_id","vertex"])
    oldv=original_vertices[original_vertices.context_id.isin([1,2])].sort_values(
        ["draw_id","vertex"])
    require(len(legacy_v)==16384 and len(oldv)==16384 and
            np.array_equal(legacy_v.original_draw_id.to_numpy(),oldv.draw_id.to_numpy())
            and np.array_equal(legacy_v.vertex.to_numpy(),oldv.vertex.to_numpy()),
            "Original 8-cell PR161 source stage identity not replayed")
    for col in V_COLUMNS:
        require(np.allclose(legacy_v[col],oldv[col],rtol=0,atol=1e-9,equal_nan=True),
                "Original PR161 eight source corner biology changed: "+col)
    # All 4 original legal plant variant source paths must coincide at V=0.
    neg=v[v.vegetation.eq(0)].copy()
    for col in V_COLUMNS:
        w=neg.groupby(["source_id","stage_design","vertex"])[col].agg(["min","max"])
        gap=float((w["max"]-w["min"]).abs().max())
        require(gap<=1e-9,"V0 source model unexpectedly changes with plants: "+
                col+" gap "+str(gap))
    p_f=v.F_B.to_numpy(float).reshape(-1,2,2,2)
    require(np.isfinite(p_f).all() and (p_f>0).all(),
            "One original aquatic source F response missing")
    computed=corner_contrasts(np.log(p_f))
    for i,term in enumerate(("OS","OV","SV","OSV")):
        require(np.allclose(computed[:,i],a["log_"+term],
                            atol=1e-9,rtol=0),
                "Four original model signs do not reproduce source response: "+term)
    require(np.array_equal(accepted_signs(computed,1e-6),a.accepted.to_numpy(bool)),
            "Original four-sign epsilon differed after isolated stage design")
    return dict(legacy_original_2048_true80_source_rows_replayed=True,
                legacy_original_16384_original_vertices_replayed=True,
                original_max_absolute_error=differences,
                original_vegetation_zero_negative_control_passed=True)


def summarize(a):
    require(len(a)==N_SCENARIOS and set(a.stage_design)==set(BOUNDS),
            "No independent four-timing source results")
    rng=np.random.default_rng(SEED)
    idx=rng.integers(0,N_BASE,size=(BOOT,N_BASE))
    summaries=[];mechanisms=[];moderators=[]
    for metric in METRICS:
        w=a.pivot(index="source_id",columns=["stage_design","arm"],values=metric).astype(float)
        require(w.shape==(N_BASE,16) and
                set(w.columns)=={(t,x[0]) for t in BOUNDS for x in ARMS},
                "An original M×theta model lacks a timing/plant intervention")
        for timing in BOUNDS:
            for arm,_,_ in ARMS:
                v=w[(timing,arm)].to_numpy(float)
                valid=np.isfinite(v)
                n=int(valid.sum())
                mean=float(v[valid].mean()) if n else np.nan
                if n:
                    boot=v[valid][rng.integers(0,n,size=(BOOT,n))].mean(axis=1)
                    lo,hi=np.quantile(boot,[.025,.975])
                else:lo,hi=np.nan,np.nan
                summaries.append(dict(metric=metric,timing=timing,arm=arm,
                    n_original_source_backgrounds=n,
                    mean=mean,mc95_low=float(lo),mc95_high=float(hi)))
            # The same legal background is used in all four plant states.
            terms={
              "both_minus_neither":w[(timing,"11")]-w[(timing,"00")],
              "refuge_only_minus_neither":w[(timing,"10")]-w[(timing,"00")],
              "feeding_support_only_minus_neither":w[(timing,"01")]-w[(timing,"00")],
              "plant_factorial":w[(timing,"11")]-w[(timing,"10")]-w[(timing,"01")]+w[(timing,"00")]
            }
            for title,values in terms.items():
                v=values.to_numpy(float)
                valid=np.isfinite(v)
                n=int(valid.sum())
                if n:
                    z=v[valid]
                    boot=z[rng.integers(0,n,size=(BOOT,n))].mean(axis=1)
                    lo,hi=np.quantile(boot,[.025,.975])
                    mean=float(z.mean())
                else:lo,hi,mean=np.nan,np.nan,np.nan
                mechanisms.append(dict(metric=metric,timing=timing,
                    contrast=title,n_original_source_backgrounds=n,
                    mean=mean,mc95_low=float(lo),mc95_high=float(hi)))
        plant={t:(w[(t,"11")]-w[(t,"00")]).to_numpy(float) for t in BOUNDS}
        vals={
          "pure_arrival_moderation_of_plant_effect":
              (plant["ES"]-plant["LS"]+plant["EL"]-plant["LL"])/2,
          "pure_duration_moderation_of_plant_effect":
              (plant["LL"]-plant["LS"]+plant["EL"]-plant["ES"])/2,
          "arrival_x_duration_moderation_of_plant_effect":
              plant["EL"]-plant["ES"]-plant["LL"]+plant["LS"]
        }
        for name,v in vals.items():
            valid=np.isfinite(v)
            n=int(valid.sum())
            if n:
                z=v[valid]
                boot=z[rng.integers(0,n,size=(BOOT,n))].mean(axis=1)
                lo,hi=np.quantile(boot,[.025,.975])
                mean=float(z.mean())
            else:lo,hi,mean=np.nan,np.nan,np.nan
            moderators.append(dict(metric=metric,contrast=name,
                n_original_source_backgrounds=n,
                mean=mean,mc95_low=float(lo),mc95_high=float(hi),
                confidence_interval_excludes_zero=bool(lo>0 or hi<0) if n else False))
    summaries=pd.DataFrame(summaries)
    mechanisms=pd.DataFrame(mechanisms)
    moderators=pd.DataFrame(moderators)
    require(len(summaries)==len(METRICS)*16 and
            len(mechanisms)==len(METRICS)*16 and
            len(moderators)==len(METRICS)*3,
            "Original complete paired developmental timing and duration estimands missing")
    return summaries,mechanisms,moderators


def run(shards,old_effects,old_vertices,out):
    a,v,recs=original_shards(shards)
    replay=independently_replay_original_source(a,v,old_effects,old_vertices)
    rate,plant,moderators=summarize(a)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    a.to_csv(out/"P1_original4096_isolated_timing_duration_80year.csv.gz",
             index=False,compression={"method":"gzip","mtime":0})
    v.to_csv(out/"P1_original32768_vegetation_predator_corners.csv.gz",
             index=False,compression={"method":"gzip","mtime":0})
    rate.to_csv(out/"P1_4timing_x_4vegetation_source_rates.csv",index=False)
    plant.to_csv(out/"P1_within_timing_paired_vegetation_effects.csv",index=False)
    moderators.to_csv(out/"P1_pure_arrival_duration_and_interaction.csv",index=False)
    receipt=dict(
      status="P1_PURE_SALAMANDER_ARRIVAL_VS_DURATION_ORIGINAL80_SOURCE_AUDIT_SUCCESS",
      original_main_sha=SOURCE_MAIN_SHA,
      source_original_PR161_run=SOURCE_ORIGINAL_PR161,
      original_PR161_256_source_seed=SOURCE_MODEL_SEED,
      source_256_backgrounds=N_BASE,source_80year_scenarios=len(a),
      source_8corner_80year_outputs=len(v),shards=N_SHARDS,
      source_original_stage1_2_replay=replay,
      source_model_cluster_bootstrap=BOOT,
      bootstrap_seed=SEED,
      estimated_breeding_priority_wild=False,
      original_G3_GBIF_egg_stage_G0_qualified=False,
      field_vegetation_x_breeding_lead_model_run=False,
      source_biological_theta_unchanged=True,
      source_shard_receipts=recs,
    )
    (out/"P1_isolated_stage_source_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("P1_PURE_ARRIVAL_DURATION_TRUE80_SOURCE_INDEPENDENT_AUDIT_SUCCESS",
        json.dumps({k:v for k,v in receipt.items() if k!="source_shard_receipts"}),flush=True)
    print("P1_PURE_STAGE_MODERATORS\n"+moderators.to_string(index=False),flush=True)
    print("P1_FROG_ABUNDANCE_PLANT\n"+
          plant[(plant.metric=="mean_log_F_B")].to_string(index=False),flush=True)
    print("P1_FOUR_SIGN_PLANT\n"+
          plant[(plant.metric=="accepted")].to_string(index=False),flush=True)
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards",type=Path,required=True)
    p.add_argument("--original-PR161-scores",type=Path,required=True)
    p.add_argument("--original-PR161-vertices",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    run(args.shards,args.original_PR161_scores,args.original_PR161_vertices,args.output)
