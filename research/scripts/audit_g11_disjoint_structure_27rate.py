"""G11 complete 64-shard independently disjoint 256-structure holdout audit.

No results are accepted until every original 80-year scenario, source corner,
source seed and independently recomputed sign indicator are reconciled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_g11_disjoint_structure_27rate import (
    frozen_selection, RATE_GRID, N_BASE, N_SHARDS,
    SOURCES_PER_SHARD, N_SCENARIOS, N_VERTICES,
)
from audit_g8_27rate_paired_factorial import response_contrasts, summarize

B = 10000
SEED = 20261107
METRICS = ("compatibility","frog_log_cohort","viable_compatibility",
           "factorial_compatibility")


def require(ok,msg):
    if not bool(ok):
        raise AssertionError(msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_shard(archive, shard, source_identity_sha, base_ids):
    label=f"g11_true80_{shard:02d}"
    receipt_path=archive/(label+"_receipt.json")
    require(receipt_path.is_file(), "Missing 80-year receipt "+label)
    receipt=json.loads(receipt_path.read_text())
    ids=list(range(shard*SOURCES_PER_SHARD,(shard+1)*SOURCES_PER_SHARD))
    expected_bases=[int(base_ids[i]) for i in ids]
    require(receipt["status"]=="G11_TRUE80_DISJOINT_SHARD"
        and receipt["selection_sha256"]==source_identity_sha
        and receipt["source_ids"]==ids
        and receipt["source_baseline_model_ids"]==expected_bases
        and receipt["old_new_structural_overlap"]==0
        and receipt["eligible_legal_baselines"]==720
        and receipt["source_main_sha"]=="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
        and receipt["years"]==80 and receipt["window"]==20 and receipt["dt"]==.5
        and receipt["rates"]==list(range(27))
        and receipt["contexts"]==[0,1,2]
        and receipt["plant_arms"]==["00","10","01","11"]
        and receipt["n_original_scenarios"]==SOURCES_PER_SHARD*27*3*4
        and receipt["n_original_vertices"]==SOURCES_PER_SHARD*27*3*4*8
        and receipt["max_abs_V0_plant_null"]<1e-10,
        "G11 original-shard biological/methodological receipt failure: "+label)
    for name,orig_sha in receipt["file_sha256"].items():
        require(sha(archive/name)==orig_sha,"G11 shard biological artifact SHA drift: "+name)
    e=pd.read_csv(archive/(label+"_effects.csv.gz"),dtype={"arm":str},keep_default_na=False)
    v=pd.read_csv(archive/(label+"_vertices.csv.gz"),dtype={"arm":str},keep_default_na=False)
    require(len(e)==SOURCES_PER_SHARD*27*3*4
            and len(v)==len(e)*8
            and e.draw_id.is_unique and
            not v.duplicated(["draw_id","vertex"]).any(), "Scenario/vertex identity drift: "+label)
    require(set(e.source_id)==set(ids)
            and e.rate_id.nunique()==27
            and e.context_id.nunique()==3
            and set(e.arm)=={"00","10","01","11"}
            and e.groupby(["source_id","rate_id","context_id"]).arm.nunique().eq(4).all(),
            "Original quartet incomplete: "+label)
    require(e.groupby("source_id").baseline_model_id.nunique().eq(1).all(),
            "New canonical base differed within source "+label)
    for sid,g in e.groupby("source_id"):
        require(int(g.baseline_model_id.iloc[0])==base_ids[int(sid)],
                "Structure selection differs from frozen source "+str(sid))
    for rid,(attack,rho,conversion) in enumerate(RATE_GRID):
        q=e[e.rate_id==rid]
        require(len(q)==SOURCES_PER_SHARD*3*4 and
                np.allclose(q[["attack","rho","conversion"]],
                            np.array([attack,rho,conversion]),atol=0,rtol=0),
                "Rate tuning within original shard "+label)
    # Independent sign reconstruction from eight *original per-corner* frog states,
    # not merely recalculating a stored acceptance rate.
    v=v.sort_values(["draw_id","vertex"])
    require(np.array_equal(v.vertex.to_numpy(),np.tile(np.arange(8),len(e))),
            "Source corner 0..7 ordering drift")
    order=e.sort_values("draw_id")
    require(np.array_equal(v.draw_id.to_numpy().reshape(-1,8)[:,0],
                           order.draw_id.to_numpy()), "Source-corner joins changed")
    fb=v.F_B.to_numpy(float).reshape(-1,2,2,2)
    require(np.isfinite(fb).all() and (fb>0).all(), "Undefined source frog state")
    z=np.log(fb)
    sd=z[:,:,1,1]-z[:,:,1,0]-z[:,:,0,1]+z[:,:,0,0]
    os=sd.mean(axis=1)
    ov=(z[:,1,:,1]-z[:,1,:,0]-z[:,0,:,1]+z[:,0,:,0]).mean(axis=1)
    sv=(z[:,1,1,:]-z[:,1,0,:]-z[:,0,1,:]+z[:,0,0,:]).mean(axis=1)
    osv=sd[:,1]-sd[:,0]
    recalculated=np.column_stack([os,ov,sv,osv])
    old=order[["log_OS","log_OV","log_SV","log_OSV"]].to_numpy(float)
    err=float(np.max(np.abs(recalculated-old)))
    require(err<1e-11, "Independent source contrast calculations differ: "+label)
    calc=((os< -1e-6)&(ov< -1e-6)&(sv>1e-6)&(osv>1e-6))
    require(np.array_equal(calc,order.accepted.to_numpy(bool)),
            "Original four-sign accept flags disagree: "+label)
    require(np.max(np.abs(z.mean(axis=(1,2,3))-
                         order.mean_log_F_B.to_numpy(float)))<1e-11,
            "Independent mean log frog model outcome differs: "+label)
    # Recheck vegetation=0 invariance on all state and predator-hazard fields.
    v0=v.loc[v.vegetation==0]
    cols=["F_B","S_B","D_B","F_fraction","audit_H_SF","audit_H_DF",
          "audit_H_DS","audit_H_SD","minimum_F_survival","minimum_S_survival"]
    gr=v0.groupby(["source_id","rate_id","context_id","vertex"],sort=True)
    require(gr.size().eq(4).all(), "Unpaired V0 model cases: "+label)
    spread=(gr[cols].max()-gr[cols].min()).to_numpy(float)
    require(np.isfinite(spread).all() and float(np.max(np.abs(spread)))<1e-10,
            "Independent V0 plant-function negative control failed: "+label)
    return e, {"shard":shard,"n_original_scenarios":len(e),
               "n_original_vertices":len(v),
               "independent_four_sign_max_abs":err,
               "selection_sha256":source_identity_sha}


def run(shards, old_summary, out):
    shards,old_summary,out=map(Path,(shards,old_summary,out))
    _,new_ids,selection,selection_sha=frozen_selection()
    base_ids=selection["new_base_ids_by_source"]
    require(len(base_ids)==256 and len(set(base_ids))==256
            and not (set(base_ids)&set(selection["old_base_ids_sorted"])),
            "G11 disjointness failed")
    files=sorted(shards.glob("g11_true80_*_receipt.json"))
    require(len(files)==N_SHARDS,"G11 requires all 64/64 80-year result shards")
    frames=[];audit=[]
    for shard in range(N_SHARDS):
        frame,check=verify_shard(shards,shard,selection_sha,base_ids)
        frames.append(frame);audit.append(check)
    effects=pd.concat(frames,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    require(len(effects)==N_SCENARIOS and effects.draw_id.is_unique,
            "G11 full original 82,944 scenarios missing")
    require(effects.source_id.nunique()==256
            and not effects.duplicated(["source_id","rate_id","context_id","arm"]).any(),
            "G11 full source/arm pairing missing")
    compare=response_contrasts(effects)
    summary=summarize(compare,boot=B,seed=SEED)
    require(len(compare)==256*27*3 and len(summary)==654, "G11 aggregate accounting drift")
    primary={}
    for metric in METRICS:
        r=summary[(summary.rate_id=="pooled_27")&
                  (summary.context=="pooled_3")&
                  (summary.metric==metric)]
        require(len(r)==1,"Missing G11 full-grid paired metric "+metric)
        primary[metric]={k:float(r.iloc[0][k]) for k in
                         ["mean","pointwise_mc95_low","pointwise_mc95_high"]}
    old=pd.read_csv(old_summary,dtype={"rate_id":str,"context":str})
    require(len(old)==654,"Original G8 source result table incomplete")
    old_baseline={}
    for metric in METRICS:
        p=old[(old.rate_id=="pooled_27")&
              (old.context=="pooled_3")&(old.metric==metric)]
        require(len(p)==1,"Original G8 pooled metric lost")
        old_baseline[metric]=float(p.iloc[0]["mean"])
    require(abs(old_baseline["compatibility"]-.027054398148148147)<1e-12
            and abs(old_baseline["frog_log_cohort"]+.04029997695177505)<1e-12,
            "Original G8 published result modified")
    # Holdout acceptance checks are fixed BEFORE looking at G11 outcomes.
    replication={
        "higher_compatibility_in_unseen_structures":
        primary["compatibility"]["pointwise_mc95_low"]>0,
        "lower_mean_frog_cohort_in_unseen_structures":
        primary["frog_log_cohort"]["pointwise_mc95_high"]<0,
    }
    replication["joint_compatibility_population_mismatch"]=all(replication.values())
    context={}
    for ci in range(3):
        p=summary[(summary.rate_id=="pooled_27")&
                  (summary.context==str(ci))&
                  (summary.metric=="frog_log_cohort")]
        require(len(p)==1,"Missing heldout developmental context "+str(ci))
        context[str(ci)]={k:float(p.iloc[0][k]) for k in
                          ("mean","pointwise_mc95_low","pointwise_mc95_high")}
    new=(compare.compatibility==1)
    loss=(compare.frog_log_cohort<0)
    nnew=int(new.sum());nloss=int((new&loss).sum());ngain=int((new&~loss).sum())
    source_count=compare.assign(new=new,loss=(new&loss)).groupby("source_id").agg(
        new=("new","sum"),loss=("loss","sum")).reindex(range(256)).fillna(0)
    rng=np.random.default_rng(SEED)
    idx=rng.integers(0,256,size=(B,256))
    n=source_count["new"].to_numpy(dtype=float)[idx].sum(axis=1)
    k=source_count["loss"].to_numpy(dtype=float)[idx].sum(axis=1)
    valid=n>0
    require(valid.sum()>0,"No new-sign holdout bootstrap support")
    ratio=k[valid]/n[valid]
    ci=np.quantile(ratio,[.025,.975])
    out.mkdir(parents=True,exist_ok=True)
    ef=out/"g11_disjoint_full_82944_source_scenarios.csv.gz"
    cf=out/"g11_disjoint_20736_matched_source_rate_context.csv.gz"
    sm=out/"g11_all_27_rate_source_bootstrap_estimates.csv"
    selection_path=out/"g11_frozen_structure_selection.json"
    effects.to_csv(ef,index=False,compression={"method":"gzip","mtime":0})
    compare.to_csv(cf,index=False,compression={"method":"gzip","mtime":0})
    summary.to_csv(sm,index=False)
    selection_path.write_text(
        json.dumps({"selection":selection,"sha256":selection_sha},
                   indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    table=[]
    for rid,(a,r,c) in enumerate(RATE_GRID):
        entry=dict(rate_id=rid,attack=a,rho=r,conversion=c,
                   n_original_matched_source_context=256*3)
        for metric in METRICS:
            q=summary[(summary.rate_id==str(rid))&
                      (summary.context=="pooled_3")&
                      (summary.metric==metric)]
            require(len(q)==1,"Missing 27-cell outcome")
            entry[metric]=float(q.iloc[0]["mean"])
            entry[metric+"_ci95_low"]=float(q.iloc[0]["pointwise_mc95_low"])
            entry[metric+"_ci95_high"]=float(q.iloc[0]["pointwise_mc95_high"])
        table.append(entry)
    tb=out/"g11_all_27_rate_paired_effects.csv"
    pd.DataFrame(table).to_csv(tb,index=False)
    receipt=dict(
       status="G11_DISJOINT_256_STRUCTURE_27_RATE_TRUE80_AUDIT_SUCCESS",
       original_main_sha="5e2f0a87c639df373fa2700b29403d2ab417a1cc",
       source_selection_seed=20261107,
       selection_sha256=selection_sha,eligible_legal_base_structures=720,
       original_G8_base_structures=256,previously_unused_baselines=464,
       disjoint_G11_source_structures=256,old_new_model_structure_overlap=0,
       full_shards=64,source_scenarios=len(effects),
       source_vertices=N_VERTICES,matched_source_rate_context=len(compare),
       context_counts=3,rate_cells=27,plant_arms=4,
       old_G8_pooled_means=old_baseline,holdout_pooled_effects=primary,
       fixed_replication_gates=replication,
       holdout_context_log_frog_effects=context,
       G11_new_sign_generation_cases=nnew,
       G11_new_sign_cases_frog_loss=nloss,
       G11_new_sign_cases_frog_nonloss=ngain,
       G11_new_sign_case_loss_fraction=nloss/nnew if nnew else None,
       G11_new_sign_case_loss_bootstrap95=list(map(float,ci)),
       G11_new_sign_bootstrap_valid=int(valid.sum()),
       bootstrap_source_units=256,bootstrap_draws=B,bootstrap_seed=SEED,
       all_64_independent_source_sign_gates_passed=True,
       original_structure_and_rates_unchanged=True,
       no_field_model_identification=True,
       archived_files_sha256={p.name:sha(p) for p in (ef,cf,sm,selection_path,tb)},
       shard_independent_receipts=audit,
    )
    (out/"g11_final_independent_validation_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("G11_FULL_256_HELDOUT_TRUE80 ",json.dumps({
        "status":receipt["status"],"scenario_count":len(effects),
        "replication":replication,"primary_effects":primary,
        "new_sign_total":nnew,"new_sign_loss":nloss,
    }),flush=True)
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--shards",required=True,type=Path)
    ap.add_argument("--g8-summary",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    run(args.shards,args.g8_summary,args.out)
