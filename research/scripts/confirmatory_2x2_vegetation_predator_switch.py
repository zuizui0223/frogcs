"""Frozen new-seed 2x2 canonical-vegetation source experiment at 80 years.

Every original M/background, rate vector and stage is paired across:
    00 baseline, 10 frog shelter, 01 odonate feeding support, 11 both.
Only the two exact original canonical catalog flags differ. Original seasonal
and annual biological kernels, four-sign rule and 120-day audit hazards are
unchanged; do not treat the output as measured wetland trophic dynamics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from abc_pom_main3600 import CORNERS, accepted_signs, corner_contrasts, run_subset
from final_mechanism_common import CONTEXTS, FEATURES, catalog, evaluate

RANDOM_SEED=20261123
N_BASE=256
N_SHARDS=8
RATE_ATTACK=.5
RATE_RHO=.75
ARMS=(("00",0,0),("10",1,0),("01",0,1),("11",1,1))
CHUNK=24
SOURCE_MAIN_SHA="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
ESSENTIAL=("source_id","context_id","arm","model_id","attack","rho",
           "conversion","strength","refuge_order","gate_code")
VERTEX_DATA=("F_B","S_B","D_B","F_fraction","audit_H_SF","audit_H_DF",
             "audit_H_DS","audit_H_SD","minimum_F_survival",
             "minimum_S_survival")


def require(condition,message):
    if not bool(condition):
        raise AssertionError(message)


def original_draws():
    models=catalog()
    require(len(models)==3600 and
            np.array_equal(models.model_id.to_numpy(),np.arange(3600)),
            "Frozen original 3600 canonical models changed")
    background=models[(models.cover_SF.eq(0))&
                      (models.support_DF.eq(0))&
                      (~models.behavior.eq("risk_refuge"))]
    require(len(background)>=N_BASE,
            "Too few original canonical source backgrounds for pre-fixed sample")
    # Sampling a base with each of the other model features held fixed means
    # all four counterfactuals can be mapped to a genuine main model_id.
    rng=np.random.default_rng(RANDOM_SEED)
    chosen=rng.choice(background.model_id.to_numpy(dtype=int),size=N_BASE,replace=False)
    chosen_info=models.set_index("model_id").loc[chosen].reset_index()
    nuisance=pd.DataFrame({
        "source_id":np.arange(N_BASE,dtype=int),
        "original_base_model_id":chosen,
        "attack":RATE_ATTACK,
        "rho":RATE_RHO,
        "conversion":rng.choice([2.0,4.0,8.0],size=N_BASE),
        "strength":rng.choice([.5,1.0],size=N_BASE),
        "refuge_order":rng.choice(["S","equal","D"],size=N_BASE),
        "gate_code":rng.integers(0,2,size=N_BASE),
    })
    lookup={tuple(getattr(row,k) for k in FEATURES):int(row.model_id)
            for row in models.itertuples(index=False)}
    require(len(lookup)==3600,"Canonical feature tuple lookup non-unique")
    proposals=[]
    for sid,base in enumerate(chosen_info.itertuples(index=False)):
        original={k:getattr(base,k) for k in FEATURES}
        require(original["cover_SF"]==0 and original["support_DF"]==0 and
                original["behavior"]!="risk_refuge","Illegal initial plant background")
        rates=nuisance.iloc[sid][["attack","rho","conversion","strength","refuge_order","gate_code"]].to_dict()
        for context in range(3):
            for pos,(arm,cover,support) in enumerate(ARMS):
                feat={**original,"cover_SF":cover,"support_DF":support}
                key=tuple(feat[k] for k in FEATURES)
                require(key in lookup,"Counterfactual not legal in original 3600 catalog")
                pid=sid*12+context*4+pos
                proposals.append(dict(
                    draw_id=pid,source_id=sid,
                    context_id=context,arm=arm,
                    model_id=lookup[key],
                    **rates,
                    cover_SF=cover,support_DF=support,
                ))
    p=pd.DataFrame(proposals).sort_values("draw_id").reset_index(drop=True)
    require(len(p)==3072 and p.draw_id.eq(np.arange(3072)).all(),
            "Full original-source × three-stage × canonical plant quartet incomplete")
    require(p.groupby(["source_id","context_id"]).arm.nunique().eq(4).all(),
            "At least one 2x2 original plant intervention missing")
    require(p.groupby("source_id").model_id.nunique().eq(4).all(),
            "Four intervention arms not mapped to four original canonical source models")
    require(p.groupby("source_id")[["attack","rho","conversion","strength",
            "refuge_order","gate_code"]].nunique().max().max()==1,
            "Biological theta modified between same-source plant intervention arms")
    return models,p,nuisance


def simulate_original_80y(proposals,models,*,years=80,window=20,dt=.5,chunk=CHUNK):
    require(1<=window<=years and years in (4,80),"Only specified source years admitted")
    joined=proposals.join(models.set_index("model_id"),
                          on="model_id",validate="many_to_one",
                          rsuffix="_source")
    require(not joined.isna().any().any(),"Noncanonical main catalog source join")
    rows=[]
    verts=[]
    corners=np.asarray(CORNERS)
    for (behavior,litter,gate_code),group in joined.groupby(
        ["behavior","litter","gate_code"],sort=True):
        for start in range(0,len(group),chunk):
            b=group.iloc[start:start+chunk].reset_index(drop=True).copy()
            des=b.loc[b.index.repeat(8)].reset_index(drop=True).copy()
            c=np.tile(corners,(len(b),1))
            des["vegetation"],des["S_source"],des["D_source"]=c.T
            for k in CONTEXTS[0]:
                des[k]=np.repeat([CONTEXTS[i][k] for i in b.context_id],8)
            des["block_id"]=des.context_id
            rates={k:des[k].to_numpy() for k in
                    ("attack","rho","conversion","strength","refuge_order")}
            result=evaluate(des,years=years,window=window,dt=dt,
                            size_gate=None if int(gate_code)==0 else .5,
                            **rates)
            f=result.F_B.to_numpy(dtype=float).reshape(-1,2,2,2)
            require(np.isfinite(f).all() and (f>0).all(),
                    "Original aquatic source is nonfinite/zero")
            lg=corner_contrasts(np.log(f))
            raw=corner_contrasts(f)
            compatible=accepted_signs(lg,1e-6)
            R=b[list(ESSENTIAL)].copy()
            for i,name in enumerate(("OS","OV","SV","OSV")):
                R["log_"+name]=lg[:,i]
                R["raw_"+name]=raw[:,i]
            R["accepted"]=compatible
            R["mean_F_B"]=f.mean(axis=(1,2,3))
            R["mean_log_F_B"]=np.log(f).mean(axis=(1,2,3))
            R["min_F"]=result.minimum_F_survival.to_numpy(float).reshape(-1,8).min(axis=1)
            R["min_S"]=result.minimum_S_survival.to_numpy(float).reshape(-1,8).min(axis=1)
            R["floor_ok"]=(R.min_F>=.05)&(R.min_S>=.05)
            R["accepted_and_floor"]=(R.accepted & R.floor_ok)
            hsf=result.audit_H_SF.to_numpy(dtype=float).reshape(-1,2,2,2)
            hdf=result.audit_H_DF.to_numpy(dtype=float).reshape(-1,2,2,2)
            R["H_SF_V1_S2_D2"]=hsf[:,1,1,1]
            R["H_DF_V1_S2_D2"]=hdf[:,1,1,1]
            total=hsf[:,1,1,1]+hdf[:,1,1,1]
            R["D_F_hazard_share_V1_S2_D2"]=np.divide(
                hdf[:,1,1,1],total,out=np.full(len(b),np.nan),where=total>1e-12)
            R["F_B_V1_S2_D2"]=f[:,1,1,1]
            require(np.all(np.isfinite(hsf)) and np.all(np.isfinite(hdf)) and
                    (hsf>=-1e-12).all() and (hdf>=-1e-12).all(),
                    "Original integrated source predator hazards invalid")
            rows.append(R)
            V=result[list(ESSENTIAL)+["vegetation","S_source","D_source"]+
                     list(VERTEX_DATA)].copy()
            V["vertex"]=np.tile(np.arange(8),len(b))
            V["source_main_model_sha"]=SOURCE_MAIN_SHA
            verts.append(V)
    effects=pd.concat(rows,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    vertices=pd.concat(verts,ignore_index=True)
    require(len(effects)==len(proposals) and
            len(vertices)==len(effects)*8 and
            not effects.draw_id.duplicated().any() and
            not vertices.duplicated(["draw_id","vertex"]).any(),
            "Original 80y seed→vertex and four-sign completeness failed")
    return effects,vertices


def check_source_replay(models,proposals,effects,years=4):
    # Independent source implementation replay uses unchanged PR160 helper.
    chk=proposals.sort_values("draw_id").head(8).copy()
    original=run_subset(chk,models,years=years,window=min(2,years),dt=.5)
    matching=effects.set_index("draw_id").loc[chk.draw_id].reset_index(drop=True)
    for col in ("log_OS","log_OV","log_SV","log_OSV",
                "mean_F_B","mean_log_F_B","min_F","min_S"):
        if not np.allclose(matching[col],original[col],atol=1e-9,rtol=0):
            raise AssertionError("Original unchanged model source replay failed: "+col)
    if not np.array_equal(matching.accepted,original.accepted):
        raise AssertionError("Main source 4-sign classification differs")
    return True


def run(shard,out,*,years=80):
    require(0<=shard<N_SHARDS,"Unknown source shard")
    models,p,nuisance=original_draws()
    sl=p[p.source_id.mod(N_SHARDS)==shard].copy()
    require(len(sl)==384 and sl.source_id.nunique()==32 and
            sl.groupby(["source_id","context_id"]).arm.nunique().eq(4).all(),
            "Original 32 independently sampled 2x2 source backgrounds/shard incomplete")
    effects,vertices=simulate_original_80y(sl,models,years=years,
                                            window=20 if years==80 else 2)
    if years==4:
        check_source_replay(models,sl,effects,years=4)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    effects.to_csv(out/f"source_results_shard_{shard:02d}.csv.gz",
                   index=False,compression={"method":"gzip","mtime":0})
    vertices.to_csv(out/f"source_vertices_shard_{shard:02d}.csv.gz",
                    index=False,compression={"method":"gzip","mtime":0})
    receipt=dict(status="GENUINE_80Y_CANONICAL_2x2" if years==80 else "SMOKE_4Y_METHODS_ONLY",
        source_main_sha=SOURCE_MAIN_SHA,seed=RANDOM_SEED,source_id_shard=shard,
        source_base_models=N_BASE,source_backgrounds_in_shard=32,
        candidate_proposals=len(sl),eight_corners=len(vertices),
        exact_canonical_catalog_models=3600,
        stages=3,plant_roles=["00","10","01","11"],
        frozen_attack=RATE_ATTACK,frozen_rho=RATE_RHO,
        years=years,source_replay_checked=(years==4),
        output_source_sha256={
            name:hashlib.sha256((out/name).read_bytes()).hexdigest()
            for name in [f"source_results_shard_{shard:02d}.csv.gz",
                         f"source_vertices_shard_{shard:02d}.csv.gz"]
        },
        wild_vegetation_refuge_measured=False,
        field_mechanism_posterior=False)
    (out/f"receipt_shard_{shard:02d}.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("CONFIRMATORY_2x2_SOURCE_RECEIPT",json.dumps(receipt),flush=True)
    return effects,vertices


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--shard",type=int,required=True,choices=tuple(range(N_SHARDS)))
    cli.add_argument("--out",type=Path,required=True)
    cli.add_argument("--years",type=int,choices=(4,80),default=80)
    a=cli.parse_args()
    run(a.shard,a.out,years=a.years)
