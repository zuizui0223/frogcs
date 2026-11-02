"""Independent fail-closed source audit and 256-background paired 2x2 inference.

Bio season / annual source is not re-estimated or calibrated against field
acoustic calls. All paired comparisons use identical source ID and nuisance.
The two vegetation functions may alter model per-larva predator hazards, not
the actual number of wild tadpoles eaten by either predator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from abc_pom_main3600 import accepted_signs, corner_contrasts
from confirmatory_2x2_vegetation_predator_switch import (
    ARMS, ESSENTIAL, N_BASE, N_SHARDS, RANDOM_SEED, SOURCE_MAIN_SHA,
    original_draws, require
)

BOOT_SEED=20261124
N_BOOT=10000
N_STAGES=3
ARM_LABELS=("00","10","01","11")
VERTEX_FIELDS=("F_B","S_B","D_B","F_fraction","audit_H_SF",
               "audit_H_DF","audit_H_DS","audit_H_SD",
               "minimum_F_survival","minimum_S_survival")
MEASURES=(
    "accepted", "accepted_and_floor", "floor_ok",
    "mean_log_F_B", "mean_F_B",
    "H_SF_V1_S2_D2", "H_DF_V1_S2_D2", "D_F_hazard_share_V1_S2_D2",
    "log_OS","log_OV","log_SV","log_OSV"
)
PAIRS=(("both_minus_neither","11","00"),
       ("refuge_only_minus_neither","10","00"),
       ("odonate_support_only_minus_neither","01","00"),
       ("both_minus_refuge_only","11","10"),
       ("both_minus_support_only","11","01"))
SHARE="D_F_hazard_share_V1_S2_D2"


def load_shards(root):
    root=Path(root)
    results=[]
    sources=[]
    receipts=[]
    for i in range(N_SHARDS):
        files=list(root.rglob(f"receipt_shard_{i:02d}.json"))
        require(len(files)==1,"Missing/duplicate original source shard receipt "+str(i))
        loc=files[0].parent
        rec=json.loads(files[0].read_text())
        require(rec["status"]=="GENUINE_80Y_CANONICAL_2x2" and
                rec["source_main_sha"]==SOURCE_MAIN_SHA and
                rec["seed"]==RANDOM_SEED and
                rec["source_id_shard"]==i and
                rec["source_backgrounds_in_shard"]==32 and
                rec["candidate_proposals"]==384 and
                rec["eight_corners"]==3072 and rec["years"]==80,
                "One biological shard was not original true80 source")
        effect_path=loc/f"source_results_shard_{i:02d}.csv.gz"
        vertex_path=loc/f"source_vertices_shard_{i:02d}.csv.gz"
        for p in (effect_path,vertex_path):
            require(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==
                    rec["output_source_sha256"][p.name],
                    "Source 80year biology file missing or SHA changed")
        effect=pd.read_csv(effect_path,dtype={"arm":str})
        corner=pd.read_csv(vertex_path,dtype={"arm":str})
        require(len(effect)==384 and len(corner)==3072 and
                not effect.draw_id.duplicated().any() and
                not corner.duplicated(["draw_id","vertex"]).any(),
                "A source shard has missing/duplicate factorial cells")
        require(effect.source_id.mod(N_SHARDS).eq(i).all()
                and corner.source_id.mod(N_SHARDS).eq(i).all(),
                "Source model mismatched its frozen shard")
        results.append(effect)
        sources.append(corner)
        receipts.append(rec)
    a=pd.concat(results,ignore_index=True).sort_values("draw_id").reset_index(drop=True)
    v=pd.concat(sources,ignore_index=True).sort_values(["draw_id","vertex"]).reset_index(drop=True)
    require(len(a)==3072 and len(v)==24576 and a.draw_id.eq(np.arange(3072)).all(),
            "New-independent-source complete 3072 proposal / 24576 biological vertex ledger failed")
    require(a.groupby(["source_id","context_id"]).arm.nunique().eq(4).all()
            and a.source_id.nunique()==256 and a.context_id.nunique()==3,
            "Missing plant quartet or original source developmental context")
    require(set(a.arm)==set(ARM_LABELS) and v.groupby("draw_id").vertex.nunique().eq(8).all(),
            "Original 2x2x2 biological eight-corner model order missing")
    require(set(v.source_main_model_sha)=={SOURCE_MAIN_SHA},
            "Original source identity changed")
    require(np.array_equal(v.draw_id.to_numpy(),np.repeat(a.draw_id,8)),
            "Original draw/source-row ordering changed")
    return a,v,receipts


def validate_canonical_and_recompute(a,v):
    models,p,nuisance=original_draws()
    require(a.draw_id.equals(p.draw_id),"Independent new-seed source draw IDs altered")
    for field in ESSENTIAL:
        v_expected=p[field].to_numpy()
        v_observed=a[field].to_numpy()
        require(np.array_equal(v_expected,v_observed),
                "Frozen original canonical catalog/seed/biological rate drift: "+field)
    require(a.source_id.nunique()==N_BASE and
            a.groupby("source_id")["model_id"].nunique().eq(4).all(),
            "Original model 2x2 quartet identity broken")
    # Grouped tests enforce same nuisance and other 11 original structure
    # flags. The only different canonical features allowed are
    # cover_SF and support_DF.
    features=[x for x in models if x not in ("assumptions","extrapolation_flags")]
    other=[x for x in features if x not in ("cover_SF","support_DF","model_id")]
    x=a[["draw_id","source_id","context_id","arm","model_id"]].merge(
        models[["model_id"]+other+["cover_SF","support_DF"]],
        on="model_id",validate="many_to_one")
    for col in other:
        require(x.groupby("source_id")[col].nunique().max()==1,
                "One background's structure feature changed outside plant 2x2: "+col)
    cover={"00":0,"10":1,"01":0,"11":1}
    support={"00":0,"10":0,"01":1,"11":1}
    require(np.array_equal(x.cover_SF.to_numpy(),
                           x.arm.map(cover).to_numpy()) and
            np.array_equal(x.support_DF.to_numpy(),
                           x.arm.map(support).to_numpy()),
            "Canonical IDs did not encode original plant feature switches")
    # The untouched old source has perfectly inactive vegetation path at V=0.
    none=v[v.vegetation.eq(0)]
    for col in VERTEX_FIELDS:
        g=none.groupby(["source_id","context_id","vertex"])[col].agg(["min","max"])
        gap=float((g["max"]-g["min"]).abs().max())
        require(gap<=1e-9,"Non-vegetated source has arm-dependent biology: "+col+" "+str(gap))
    # Recompute every coefficient and acceptance from original saved
    # aquatic-cohort vertices, not from the stored derived sign table.
    value=v.F_B.to_numpy(dtype=float).reshape(-1,2,2,2)
    require(np.isfinite(value).all() and (value>0).all(),"Invalid F original source")
    logb=corner_contrasts(np.log(value))
    raw=corner_contrasts(value)
    for j,name in enumerate(("OS","OV","SV","OSV")):
        require(np.allclose(logb[:,j],a["log_"+name],atol=1e-9,rtol=0) and
                np.allclose(raw[:,j],a["raw_"+name],atol=1e-9,rtol=0),
                "Saved original main 80y four-sign contrasts fail independent replay: "+name)
    require(np.array_equal(accepted_signs(logb,1e-6),a.accepted.to_numpy(bool)),
            "Original epsilon 1e-6 four-sign rule changed in new source")
    require(np.allclose(value.mean(axis=(1,2,3)),a.mean_F_B,atol=1e-9,rtol=0),
            "Original model F mean differs from source readback")
    require(np.allclose(np.log(value).mean(axis=(1,2,3)),a.mean_log_F_B,
                        atol=1e-9,rtol=0),"Original source log F mean changed")
    for col,cell in (("H_SF_V1_S2_D2","audit_H_SF"),
                     ("H_DF_V1_S2_D2","audit_H_DF")):
        val=v[cell].to_numpy(dtype=float).reshape(-1,2,2,2)[:,1,1,1]
        require(np.allclose(val,a[col],atol=1e-9,rtol=0),
                "Original integrated predator hazard source does not reproduce "+col)
    values=v[list(("audit_H_SF","audit_H_DF"))].to_numpy(dtype=float)
    require(np.isfinite(values).all() and (values>=-1e-9).all(),
            "Original within-season predator hazards invalid")
    # This is an integrated per-F-larva *hazard* partition. Because
    # encounter intensities change during the season, it is not
    # realized number of deaths attributable to either predator.
    h=a.H_SF_V1_S2_D2+a.H_DF_V1_S2_D2
    frac=np.divide(a.H_DF_V1_S2_D2,h,out=np.full(len(a),np.nan),where=h>1e-12)
    require(np.allclose(a.D_F_hazard_share_V1_S2_D2,frac,
                        rtol=0,atol=1e-9,equal_nan=True),
            "Original predator hazard share does not reproduce")
    require(np.array_equal(a.accepted_and_floor.to_numpy(bool),
                            a.accepted.to_numpy(bool)&a.floor_ok.to_numpy(bool)),
            "Original survival floor gate not paired with sign acceptance")
    return {"null_V0_max_absolute_drift":0.0,
            "source_frozen_main_sha":SOURCE_MAIN_SHA,
            "n_original_256_base_models":int(nuisance.source_id.nunique()),
            "all_24576_original_model_corners_recomputed":True}


def frame(a):
    k=["source_id","context_id"]
    out=a.copy()
    metrics=list(MEASURES)
    cols={}
    for metric in metrics:
        w=out.pivot(index=k,columns="arm",values=metric).sort_index()
        require(list(w.columns)==list(ARM_LABELS),
                "Source quartet member missing in "+metric)
        cols[metric]=w.astype(float)
    rows=[]
    for metric,w in cols.items():
        for name,above,below in PAIRS:
            dif=w[above]-w[below]
            rows.append(dif.rename((metric,name)))
        synergy=w["11"]-w["10"]-w["01"]+w["00"]
        rows.append(synergy.rename((metric,"factorial_synergy")))
        for arm in ARM_LABELS:
            rows.append(w[arm].rename((metric,"arm_rate_"+arm)))
    data=pd.concat(rows,axis=1)
    data.columns=pd.MultiIndex.from_tuples(data.columns,names=["metric","contrast"])
    return data


def infer(data,bootstrap=N_BOOT):
    source=np.arange(N_BASE)
    rng=np.random.default_rng(BOOT_SEED)
    draw=rng.integers(0,N_BASE,size=(bootstrap,N_BASE))
    rows=[]
    # For each background, average the three source stages so stage contexts
    # cannot inflate independently simulated biological source sample sizes.
    for (metric,contrast) in data.columns:
        if metric==SHARE:
            # A hazard share is UNDEFINED if both predator hazard paths are
            # zero, not a missing observation that should be replaced by 0.
            for context in (0,1,2,"pooled"):
                if context=="pooled":
                    a=data[(metric,contrast)].unstack("context_id").to_numpy(float)
                    keep=np.isfinite(a).all(axis=1)
                    vals=a[keep].mean(axis=1)
                else:
                    a=data[(metric,contrast)].unstack("context_id")
                    vals=a[context].to_numpy(float)
                    keep=np.isfinite(vals)
                    vals=vals[keep]
                n=len(vals)
                if n<20:
                    rows.append(dict(metric=metric,contrast=contrast,context=str(context),
                                     mean=np.nan,ci95_low=np.nan,ci95_high=np.nan,
                                     n_source_backgrounds=n,
                                     statistic_status="UNIDENTIFIED_NO_PREDATOR_HAZARD"))
                    continue
                # The complete-case share estimand uses a fresh seed and only
                # source backgrounds with positive modelled predator hazard.
                rr=np.random.default_rng(BOOT_SEED).integers(0,n,size=(bootstrap,n))
                boot=vals[rr].mean(axis=1)
                lo,hi=np.quantile(boot,[.025,.975])
                rows.append(dict(metric=metric,contrast=contrast,context=str(context),
                                 mean=float(vals.mean()),ci95_low=float(lo),ci95_high=float(hi),
                                 n_source_backgrounds=n,statistic_status="MODEL_SOURCE_HAZARD_SHARE"))
            continue
        wide=data[(metric,contrast)].unstack("context_id").reindex(source)
        require(wide.shape==(N_BASE,3) and np.isfinite(wide.to_numpy()).all(),
                "Missing original background unit/context for "+metric+" "+contrast)
        arr=wide.to_numpy(dtype=float)
        for context,v in [(str(c),arr[:,c]) for c in range(3)]+[("pooled",arr.mean(axis=1))]:
            est=float(v.mean())
            draws=v[draw].mean(axis=1)
            lo,hi=np.quantile(draws,[.025,.975])
            rows.append(dict(metric=metric,contrast=contrast,context=context,
                    mean=est,ci95_low=float(lo),ci95_high=float(hi),
                    n_source_backgrounds=N_BASE,
                    n_pos=int((v>1e-10).sum()),n_neg=int((v<-1e-10).sum()),
                    n_zero=int((np.abs(v)<=1e-10).sum()),
                    statistic_status="MODEL_NATIVE_SOURCE_BOOTSTRAP"))
    table=pd.DataFrame(rows)
    require(len(table)==len(MEASURES)*(len(PAIRS)+1+4)*4,
            "Original complete stage × source paired estimand inventory incorrect")
    return table


def aggregate(input_path,out):
    a,v,receipts=load_shards(input_path)
    audit=validate_canonical_and_recompute(a,v)
    terms=infer(frame(a))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    a.to_csv(out/"true80_canonical_paired_2x2_proposals.csv.gz",
             index=False,compression={"method":"gzip","mtime":0})
    v.to_csv(out/"true80_all_24576_original_model_vertices.csv.gz",
             index=False,compression={"method":"gzip","mtime":0})
    terms.to_csv(out/"paired_2x2_source_background_95MC.csv",index=False)
    arm=terms[terms.contrast.str.startswith("arm_rate_") &
              terms.metric.isin(["accepted","accepted_and_floor","floor_ok","mean_log_F_B"])].copy()
    arm.to_csv(out/"four_arm_true80_success_and_survival.csv",index=False)
    gate=terms[(terms.metric=="accepted")&
               (terms.contrast.isin(("both_minus_neither","factorial_synergy")))]
    decision={}
    for label,g in gate.groupby("contrast"):
        q=g[g.context=="pooled"].iloc[0]
        decision[label]=dict(estimated_mean=q["mean"],bootstrap_95=[q.ci95_low,q.ci95_high],
                              positive_supported=bool(q.ci95_low>0))
    mechanism={}
    for metric,pair in [
      ("H_SF_V1_S2_D2","refuge_only_minus_neither"),
      ("H_DF_V1_S2_D2","odonate_support_only_minus_neither"),
      (SHARE,"both_minus_neither"),
    ]:
        q=terms[(terms.metric==metric)&(terms.contrast==pair)&
                (terms.context=="pooled")]
        require(len(q)==1,"Paired original source H_SF/H_DF hazard endpoint missing")
        row=q.iloc[0]
        mechanism[metric]=dict(contrast=pair,mean=row["mean"],
                bootstrap_95=[row.ci95_low,row.ci95_high],
                n_defined=int(row.n_source_backgrounds))
    receipt=dict(
        status="CONFIRMATORY_NEW_SEED_PAIRED_2x2_ORIGINAL_80Y_SOURCE_AUDIT_SUCCESS",
        historical_discovery_source_run=41262102436,
        original_main_sha=SOURCE_MAIN_SHA,
        new_independent_seed=RANDOM_SEED,
        base_canonical_structures=N_BASE,
        context_levels=N_STAGES,
        vegetation_switch_arms=list(ARM_LABELS),
        new_80year_model_proposals=len(a),original_80year_vertices=len(v),
        original_80year_job_shards=N_SHARDS,
        source_background_bootstrap_draws=N_BOOT,
        source_background_bootstrap_seed=BOOT_SEED,
        preregistered_acceptance_decisions=decision,
        mechanistic_source_per_frog_hazard_gate=mechanism,
        original_background_V0_pathway_null_verified=True,
        original_main_canonical_legality_verified=True,
        original_four_sign_eps=1e-6,
        model_hazard_not_wild_mortality=True,
        confirms_field_predator_replacement=False,
        inferential_status="new-seed fixed-regime synthetic model intervention; independent model reapplication not field posterior",
        original_shard_source_receipts=receipts,
    )
    (out/"true80_independent_audit_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CONFIRMATORY_2x2_SOURCE_INDEPENDENT_AUDIT_PASS",
          json.dumps({k:v for k,v in receipt.items() if k!="original_shard_source_receipts"}),flush=True)
    print("PREDATOR_SWITCH_ACCEPTANCE_AND_HAZARD\n"+
          terms.loc[(terms.context=="pooled")&
            (terms.metric.isin(["accepted","accepted_and_floor","mean_log_F_B",
                                "H_SF_V1_S2_D2","H_DF_V1_S2_D2",SHARE])) &
            (terms.contrast.isin(["both_minus_neither","refuge_only_minus_neither",
                                "odonate_support_only_minus_neither","factorial_synergy",
                                "arm_rate_00","arm_rate_10","arm_rate_01","arm_rate_11"])),
            ["metric","contrast","mean","ci95_low","ci95_high","n_source_backgrounds"]].to_string(index=False),flush=True)
    return receipt,terms


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    x=p.parse_args()
    aggregate(x.input,x.output)
