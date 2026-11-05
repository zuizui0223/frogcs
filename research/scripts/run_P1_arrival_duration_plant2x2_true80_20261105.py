"""True 80-year source factorial: salamander arrival × aquatic duration, pure effects.

Reuses exact PR161 256 canonical model backgrounds and all 4 legal
vegetation-function switches. The original PR161 stage1 and stage2 MUST be
reproduced independently as late-short and early-long, respectively.
Environmental field breeding onset is NOT measured by this simulation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from abc_pom_main3600 import CORNERS, corner_contrasts, accepted_signs
from confirmatory_2x2_vegetation_predator_switch import (
    original_draws, N_BASE, ARMS, SOURCE_MAIN_SHA, VERTEX_DATA
)
from final_mechanism_common import catalog, evaluate, FEATURES

N_SHARDS=8
TIMING=(
    ("LS",40,40,1),  # original PR161 context 1
    ("LL",40,60,-1), # new
    ("ES",0,40,-1),  # new
    ("EL",0,60,2),  # original PR161 context 2
)
BOUNDS=("LS","LL","ES","EL")
N_PER_SHARD=N_BASE//N_SHARDS
SOURCE_MODEL_SEED=20261123
N_SCENARIOS=N_BASE*len(TIMING)*len(ARMS)
N_VERTICES=N_SCENARIOS*len(CORNERS)
YEARS=80
WINDOW=20
DT=.5
CHUNK=24
SAVE_VERTICES=("F_B","S_B","D_B","F_fraction","audit_H_SF",
               "audit_H_DF","audit_H_DS","audit_H_SD",
               "minimum_F_survival","minimum_S_survival")
OUTCOME_COLS=("log_OS","log_OV","log_SV","log_OSV",
              "mean_F_B","mean_log_F_B","min_F","min_S",
              "H_SF_V1_S2_D2","H_DF_V1_S2_D2",
              "D_F_hazard_share_V1_S2_D2")


def require(ok,message):
    if not bool(ok):
        raise AssertionError(message)


def create_factorial():
    models,prior,nuisance=original_draws()
    require(len(models)==3600 and len(prior)==3072 and len(nuisance)==N_BASE,
            "Original fixed 3600 catalog / 256 PR161 backgrounds changed")
    base=prior[prior.context_id.eq(1)].sort_values(["source_id","arm"])
    require(len(base)==1024 and base.source_id.nunique()==N_BASE
            and base.groupby("source_id").arm.nunique().eq(4).all(),
            "Original legal stage1 256×4 plant source missing")
    stage_rows=[]
    for sid in range(N_BASE):
        q=base[base.source_id==sid]
        require(len(q)==4,"Missing source background")
        q=q.set_index("arm")
        for ti,(label,sarrival,sduration,original_cid) in enumerate(TIMING):
            for arm_index,(arm,cover,support) in enumerate(ARMS):
                src=q.loc[arm]
                require(int(src.cover_SF)==cover and int(src.support_DF)==support,
                        "Original canonical treatment flags drifted")
                original_id=(sid*12+original_cid*4+arm_index
                             if original_cid>=0 else -1)
                stage_rows.append(dict(
                    draw_id=sid*16+ti*4+arm_index,
                    original_draw_id=original_id,
                    source_id=sid,
                    timing_context_id=ti,
                    stage_design=label,
                    original_context_id=original_cid,
                    source_main_model_id=int(src.model_id),
                    model_id=int(src.model_id),
                    arm=arm,
                    attack=float(src.attack),
                    rho=float(src.rho),
                    conversion=float(src.conversion),
                    strength=float(src.strength),
                    refuge_order=str(src.refuge_order),
                    gate_code=int(src.gate_code),
                    cover_SF=int(src.cover_SF),
                    support_DF=int(src.support_DF),
                    f_arrival=20,s_arrival=sarrival,d_arrival=20,
                    F_duration=45,S_duration=sduration,D_duration=60
                ))
    x=pd.DataFrame(stage_rows).sort_values("draw_id").reset_index(drop=True)
    require(len(x)==N_SCENARIOS and x.draw_id.eq(np.arange(N_SCENARIOS)).all(),
            "Independent two-factor stage and four-plant complete source missing")
    require(x.groupby(["source_id","stage_design"]).arm.nunique().eq(4).all() and
            x.groupby(["source_id","arm"]).stage_design.nunique().eq(4).all(),
            "Original canonical 2x2×2x2 pairing missing")
    require(x.groupby("source_id")[["attack","rho","conversion","strength",
            "refuge_order","gate_code"]].nunique().max().max()==1,
            "Original PR161 nuisance theta differs across arrival and duration")
    require(x.groupby("source_id").model_id.nunique().eq(4).all(),
            "Only vegetation model ID should vary within each source")
    for group in ("LS","EL"):
        id1=1 if group=="LS" else 2
        q=x[x.stage_design.eq(group)]
        require(q.original_context_id.eq(id1).all() and
                np.array_equal(q.original_draw_id.to_numpy(),
                               q.source_id.to_numpy()*12+id1*4+
                               q.arm.map({a:i for i,(a,_,_) in enumerate(ARMS)}).to_numpy()),
                "Original PR161 context identity not reproducible")
    return models,x


def seasonal_original(proposals,models,*,years=YEARS,window=WINDOW,dt=DT):
    require(years in (4,YEARS) and 1<=window<=years,
            "New stage factorial true80 and source four-year test only")
    # All plant interventions exist as legal members of the original catalog,
    # not synthetic invalid feature combinations.
    features=models.set_index("model_id")
    joined=proposals.drop(columns=["cover_SF","support_DF"]).join(
        features,on="model_id",validate="many_to_one")
    require(not joined.isna().any().any() and
            joined.groupby("source_id").model_id.nunique().eq(4).all(),
            "Original source catalog assignment or theta invalid")
    results=[]
    vertices=[]
    corners=np.asarray(CORNERS)
    for (beh,litter,gate),group in joined.groupby(
        ["behavior","litter","gate_code"],sort=True):
        for a in range(0,len(group),CHUNK):
            b=group.iloc[a:a+CHUNK].copy().reset_index(drop=True)
            batch=b.loc[b.index.repeat(len(corners))].reset_index(drop=True).copy()
            v=np.tile(corners,(len(b),1))
            batch["vegetation"],batch["S_source"],batch["D_source"]=v.T
            batch["block_id"]=batch.timing_context_id
            rates={k:batch[k].to_numpy() for k in
                   ("attack","rho","conversion","strength","refuge_order")}
            states=evaluate(batch,years=years,window=window,dt=dt,
                            size_gate=None if int(gate)==0 else .5,**rates)
            frog=states.F_B.to_numpy(dtype=float).reshape(-1,2,2,2)
            require(np.isfinite(frog).all() and (frog>0).all(),
                    "Original cohort has undefined source F_B")
            log_sign=corner_contrasts(np.log(frog))
            raw_sign=corner_contrasts(frog)
            keep=b[["draw_id","original_draw_id","source_id","model_id",
                    "timing_context_id","stage_design","original_context_id","arm",
                    "attack","rho","conversion","strength","refuge_order",
                    "gate_code","s_arrival","S_duration"]].copy()
            for i,name in enumerate(("OS","OV","SV","OSV")):
                keep["log_"+name]=log_sign[:,i]
                keep["raw_"+name]=raw_sign[:,i]
            keep["accepted"]=accepted_signs(log_sign,1e-6)
            keep["mean_F_B"]=frog.mean(axis=(1,2,3))
            keep["mean_log_F_B"]=np.log(frog).mean(axis=(1,2,3))
            keep["min_F"]=states.minimum_F_survival.to_numpy(float).reshape(-1,8).min(axis=1)
            keep["min_S"]=states.minimum_S_survival.to_numpy(float).reshape(-1,8).min(axis=1)
            keep["floor_ok"]=(keep.min_F>=.05)&(keep.min_S>=.05)
            keep["accepted_and_floor"]=(keep.accepted & keep.floor_ok)
            hs=states.audit_H_SF.to_numpy(dtype=float).reshape(-1,2,2,2)
            hd=states.audit_H_DF.to_numpy(dtype=float).reshape(-1,2,2,2)
            keep["H_SF_V1_S2_D2"]=hs[:,1,1,1]
            keep["H_DF_V1_S2_D2"]=hd[:,1,1,1]
            total=hs[:,1,1,1]+hd[:,1,1,1]
            keep["D_F_hazard_share_V1_S2_D2"]=np.divide(
                hd[:,1,1,1],total,out=np.full(len(b),np.nan),
                where=total>1e-12)
            results.append(keep)
            from_states=states[["F_B","S_B","D_B","F_fraction","audit_H_SF",
                                "audit_H_DF","audit_H_DS","audit_H_SD",
                                "minimum_F_survival","minimum_S_survival"]].copy()
            from_states["draw_id"]=np.repeat(b.draw_id.to_numpy(),8)
            from_states["source_id"]=np.repeat(b.source_id.to_numpy(),8)
            from_states["stage_design"]=np.repeat(b.stage_design.to_numpy(),8)
            from_states["arm"]=np.repeat(b.arm.to_numpy(),8)
            from_states["original_draw_id"]=np.repeat(b.original_draw_id.to_numpy(),8)
            from_states["vertex"]=np.tile(np.arange(8),len(b))
            from_states["vegetation"]=batch.vegetation.to_numpy()
            from_states["S_source"]=batch.S_source.to_numpy()
            from_states["D_source"]=batch.D_source.to_numpy()
            vertices.append(from_states)
    a=pd.concat(results,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    v=pd.concat(vertices,ignore_index=True).sort_values(
        ["draw_id","vertex"]).reset_index(drop=True)
    require(len(a)==len(proposals) and len(v)==len(a)*8
            and not a.draw_id.duplicated().any()
            and not v.duplicated(["draw_id","vertex"]).any(),
            "Four-context source 80-year biological rows lost")
    return a,v


def run(*,shard,out,years=YEARS):
    require(shard in range(N_SHARDS),"Unknown original source ID shard")
    models,prior=create_factorial()
    group=prior[prior.source_id.mod(N_SHARDS)==shard].copy()
    require(len(group)==N_PER_SHARD*16 and
            group.source_id.nunique()==N_PER_SHARD,
            "Original 32 backgrounds per source shard changed")
    effects,verts=seasonal_original(group,models,
                         years=years,window=20 if years==80 else 2)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    stem=f"factorial_original80_shard_{shard:02d}"
    ep=out/(stem+"_effects.csv.gz")
    vp=out/(stem+"_vertices.csv.gz")
    effects.to_csv(ep,index=False,compression={"method":"gzip","mtime":0})
    verts.to_csv(vp,index=False,compression={"method":"gzip","mtime":0})
    record=dict(
        status="P1_TRUE80_CONTEXTS_ISOLATED" if years==80 else "P1_FOURYEAR_METHOD_SMOKE_ONLY",
        original_main_sha=SOURCE_MAIN_SHA,
        original_PR161_source_seed=SOURCE_MODEL_SEED,
        shard=shard,
        original_backgrounds=N_PER_SHARD,
        source_rows=len(effects),source_vertices=len(verts),
        n_timing_conditions=4,n_plant_roles=4,
        contexts=[dict(label=x,arrival=y,duration=z,legacy_context=c) for x,y,z,c in TIMING],
        source_f_arrival=20,source_F_duration=45,
        source_d_arrival=20,source_D_duration=60,
        years=years,window=20 if years==80 else 2,dt=DT,
        positive_field_breeding_priority_measured=False,
        ecological_breeding_onset_field_test_run=False,
        file_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ep,vp)},
    )
    (out/(stem+"_receipt.json")).write_text(json.dumps(
        record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("P1_ORIGINAL_TIMING_DURATION_SOURCE_SHARD",json.dumps({
        k:v for k,v in record.items() if k!="file_sha256"}),flush=True)


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--shard",type=int,choices=tuple(range(N_SHARDS)),required=True)
    cli.add_argument("--years",type=int,choices=(4,80),default=80)
    cli.add_argument("--out",type=Path,required=True)
    args=cli.parse_args()
    run(shard=args.shard,out=args.out,years=args.years)
