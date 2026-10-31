"""Exact-rejection ABC for CROSS stage timing, handling and vegetation roles.

144 structural×plant classes, 64 independent originally prior-sampled
demographic vectors, reversal ON/OFF paired, log(F_B) primary and raw
sensitivity.  Same prior IDs across all classes.  Not field causal posterior.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_native_2x2x2_prior import ROOT, TARGET, METRICS
from model_native_vegetation_abc import legal_plant_inventory
from run_vegetation_cross_ontogeny_80y import (
    OUT,N_DRAWS,CONTEXTS,FAMILIES,BASE_ROLE
)

BOOT=999
SEED=20261107
SCALES=("log","raw")
PLANT_FLAGS=("cover_SF","cover_DF","cover_DS","litter")
N_CLASSES=12*3*2*2
N_RAW_MODELS=N_CLASSES*N_DRAWS*2


def load_archived_cross_sources(folder=OUT):
    records=[];sha={};rate_ids=None;first_rate=None
    for context in CONTEXTS:
        for family in FAMILIES:
            stem=f"{context}__{family}"
            file=folder/(stem+"_actual_80year_model_signs.csv.gz")
            receipt=folder/(stem+"_receipt.json")
            rates=folder/(stem+"_matched_parent256_rate_draws.csv")
            for p in (file,receipt,rates):
                if not p.is_file() or p.stat().st_size<50:
                    raise FileNotFoundError("Missing actual 80-year model "+str(p))
                sha[str(p.name)]=hashlib.sha256(p.read_bytes()).hexdigest()
            rc=json.loads(receipt.read_text())
            if (rc["n_actual_80year_model_runs"]!=12*2*64*2
                or rc["n_original_demographic_prior_draws"]!=64 or
                rc["n_reversal_states"]!=2 or
                max(rc["original_baseline_replay"].values())>1e-7):
                raise AssertionError("Genuine frozen 80-year source not replayed")
            p=pd.read_csv(rates).sort_values("draw").reset_index(drop=True)
            key=("draw","attack_scale","rho","conversion","f_delay",
                 "f_juvenile_survival","f_adult_survival","s_growth_multiplier",
                 "d_growth_multiplier")
            if len(p)!=N_DRAWS or p.draw.nunique()!=N_DRAWS or not all(k in p for k in key):
                raise ValueError("Incomplete original shared demographic rate vectors")
            if rate_ids is None:
                rate_ids=p.draw.to_numpy(int)
                first_rate=p[list(key)].copy()
            else:
                pd.testing.assert_frame_equal(first_rate,p[list(key)],
                    check_exact=True)
            x=pd.read_csv(file)
            if len(x)!=12*2*64*2 or x.structure_id.nunique()!=24:
                raise AssertionError("Cross role shard incomplete")
            if x.duplicated(["structure_id","draw","reverse_on"]).any():
                raise AssertionError("Repeated cohort/role/rate draw")
            if x.groupby(["structure_id","draw"]).reverse_on.nunique().ne(2).any():
                raise AssertionError("Reversal nuisance imbalance")
            if set(x.context)!={context} or set(x.family)!={family}:
                raise AssertionError("Crossed stage source context mismatch")
            records.append(x)
    allruns=pd.concat(records,ignore_index=True)
    if len(allruns)!=N_RAW_MODELS or allruns.structure_id.nunique()!=N_CLASSES:
        raise AssertionError("Not 144 full structural plant classes")
    if not np.array_equal(rate_ids,np.arange(0,256,4)):
        raise AssertionError("Not a matched part of original 256 prior draw IDs")
    return allruns,first_rate,sha


def original_256_same_draw_gate(cross,prior_folder):
    """Baseline original timing/handling MUST reproduce completed 256 plant results."""
    if prior_folder is None:return {"status":"SKIPPED_NO_ORIGINAL_256_SOURCE"}
    counts=0;errors={}
    copy=cross[(cross.context=="original")&(cross.family=="baseline")]
    src=[]
    for sf in (0,1):
        for litter in (0,1):
            prefix=f"SF{sf}_L{litter}"
            f=Path(prior_folder)/(prefix+"_prior_vegetation_signs.csv.gz")
            if not f.is_file():
                raise FileNotFoundError("Cannot compare original 256 plant source "+str(f))
            x=pd.read_csv(f)
            x=x[x.draw.isin(copy.draw.unique())]
            src.append(x)
    old=pd.concat(src,ignore_index=True)
    keys=["plant_model","risk","draw","reverse_on"]
    # Exactly the same 24 role×risk classes x64 rate draws x2 reversal.
    old=old.sort_values(keys).reset_index(drop=True)
    new=copy.sort_values(keys).reset_index(drop=True)
    if len(old)!=24*64*2 or len(new)!=len(old):
        raise AssertionError("Mismatched same rate/edge original 256 plant source size")
    if not old[keys].equals(new[keys]):
        raise AssertionError("Same-rate source condition names do not align")
    for scale in SCALES:
        for metric in METRICS:
            key=f"beta_{scale}_{metric}"
            delta=float(np.abs(old[key]-new[key]).max())
            errors[key]=delta
            if delta>1e-8:
                raise AssertionError("Changed original 80y vegetation factorial baseline: "+key)
            skey=f"sign_{scale}_{metric}"
            if not (old[skey]==new[skey]).all():
                raise AssertionError("Changed source sign: "+skey)
        if not (old[f"matches_{scale}"]==new[f"matches_{scale}"]).all():
            raise AssertionError("Changed original 256 target decisions")
    counts=len(new)
    return dict(status="MATCHED_ORIGINAL_FULL256",n_paired_sources=counts,
                numerical_contrast_max_errors=errors)


def class_draw_matrix(rows,scale):
    if scale not in SCALES:raise ValueError("Unknown ecological response scale")
    x=rows.copy()
    x[f"matches_{scale}"]=x[f"matches_{scale}"].astype(int)
    g=(x.groupby(["draw","structure_id"],sort=True)
       .agg(accept=(f"matches_{scale}","mean"),
            n_reverse=("reverse_on","nunique"),
            n=("reverse_on","size")).reset_index())
    if len(g)!=N_CLASSES*N_DRAWS or g.n_reverse.ne(2).any() or g.n.ne(2).any():
        raise AssertionError("Not 144x64 paired biological-rate draw rows")
    mat=g.pivot(index="draw",columns="structure_id",values="accept")
    if len(mat)!=N_DRAWS or mat.shape[1]!=N_CLASSES or mat.isna().any().any():
        raise AssertionError("Missing model-native POM source")
    return mat


def marginalize_sources(rows,n_boot=BOOT):
    out=[];groups=[];comparison=[]
    rng=np.random.default_rng(SEED)
    indices=rng.integers(0,N_DRAWS,size=(n_boot,N_DRAWS))
    meta=rows.drop_duplicates("structure_id").set_index("structure_id")
    if len(meta)!=N_CLASSES or meta.index.duplicated().any():
        raise AssertionError("Mixed or repeated structural metadata")
    for scale in SCALES:
        matrix=class_draw_matrix(rows,scale)
        allclasses=matrix.columns.to_list()
        a=matrix.to_numpy(float)
        totals=a.sum(axis=0)
        denominator=totals.sum()
        if denominator<=0:
            raise ValueError("No source model produces four main signs")
        chosen=a[indices].sum(axis=1)
        if np.any(chosen.sum(axis=1)<=0):
            raise ValueError("No ABC matches in at least one paired draw bootstrap")
        rates=totals/N_DRAWS
        shares=totals/denominator
        bs_rate=chosen/N_DRAWS
        bs_share=chosen/chosen.sum(axis=1,keepdims=True)
        for i,structure in enumerate(allclasses):
            source=meta.loc[structure]
            out.append(dict(scale=scale,structure_id=structure,
                            context=source.context,family=source.family,
                            risk=bool(source.risk),plant_model=source.plant_model,
                            **{k:int(source[k]) for k in PLANT_FLAGS},
                            n_original_rate_vectors=N_DRAWS,
                            n_reversal_states_per_rate=2,
                            accepted_rate_weight=float(totals[i]),
                            acceptance_fraction=float(rates[i]),
                            acceptance_ci_low=float(np.quantile(bs_rate[:,i],.025)),
                            acceptance_ci_high=float(np.quantile(bs_rate[:,i],.975)),
                            conditional_model_share=float(shares[i]),
                            model_share_ci_low=float(np.quantile(bs_share[:,i],.025)),
                            model_share_ci_high=float(np.quantile(bs_share[:,i],.975)),
                            accepted_weight_adequate_for_rate_analysis=bool(totals[i]>=20)))
        for axis in ("context","family","risk","plant_model",*PLANT_FLAGS):
            arr=np.array([meta.loc[z,axis] for z in allclasses])
            for val in sorted(pd.unique(arr),key=str):
                ix=np.flatnonzero(arr==val)
                share=shares[ix].sum()
                interval=bs_share[:,ix].sum(axis=1)
                groups.append(dict(scale=scale,dimension=axis,label=str(val),
                                   n_class_hypotheses=len(ix),
                                   conditional_share=float(share),
                                   share_ci_low=float(np.quantile(interval,.025)),
                                   share_ci_high=float(np.quantile(interval,.975))))
        # Within each original context and feeding budget, plant role shares
        # integrate equally over refuge only within that particular stage class.
        for (context,family),group in meta.loc[allclasses].groupby(["context","family"]):
            mask=(meta.loc[allclasses].context.eq(context)&
                  meta.loc[allclasses].family.eq(family)).to_numpy()
            idx=np.flatnonzero(mask)
            subset=totals[idx]
            if subset.sum()==0:
                for name in sorted(meta.iloc[idx].plant_model.unique()):
                    comparison.append(dict(scale=scale,context=context,family=family,
                                           plant_model=name,n_original_rate_draws=N_DRAWS,
                                           matching_weight=0.,
                                           conditional_plant_share=np.nan,
                                           status="NO_FOUR_SIGN_MATCHES_IN_STAGE_CLASS"))
                continue
            norm=chosen[:,idx].sum(axis=1)
            for name in sorted(meta.iloc[idx].plant_model.unique()):
                jj=[j for j in idx if meta.loc[allclasses[j],"plant_model"]==name]
                part=float(totals[jj].sum()/subset.sum())
                bo=chosen[:,jj].sum(axis=1)
                good=norm>0
                q=bo[good]/norm[good]
                comparison.append(dict(scale=scale,context=context,family=family,
                                       plant_model=name,n_original_rate_draws=N_DRAWS,
                                       matching_weight=float(totals[jj].sum()),
                                       conditional_plant_share=part,
                                       share_ci_low=float(np.quantile(q,.025)) if len(q) else np.nan,
                                       share_ci_high=float(np.quantile(q,.975)) if len(q) else np.nan,
                                       n_valid_bootstraps=int(good.sum()),
                                       status="TRUE_GENUINE_STAGE_CONDITIONAL_ABC"))
    return (pd.DataFrame(out),pd.DataFrame(groups),
            pd.DataFrame(comparison))


def paired_vegetation_differences(rows,n_boot=BOOT):
    """Mechanism ON-OFF matched for same draw, stage, handling, risk and edge."""
    allrows=[];res=[]
    sampled=np.random.default_rng(SEED+1).integers(0,N_DRAWS,
                                                   size=(n_boot,N_DRAWS))
    for scale in SCALES:
        for role in PLANT_FLAGS:
            filters=np.ones(len(rows),dtype=bool)
            if role=="litter":filters &=rows.cover_DF.eq(0).to_numpy()
            if role=="cover_DF":filters &=rows.litter.eq(0).to_numpy()
            sub=rows.loc[filters].copy()
            outcome=f"matches_{scale}"
            sub[outcome]=sub[outcome].astype(int)
            other=[x for x in PLANT_FLAGS if x!=role]
            index=["context","family","risk","draw","reverse_on",*other]
            paired=sub.pivot(index=index,columns=role,
                             values=[outcome,*[f"beta_{scale}_{k}" for k in METRICS]])
            if paired.isna().any().any():
                raise AssertionError("Unpaired original main plant model ablation "+role)
            diff=paired.xs(1,axis=1,level=1)-paired.xs(0,axis=1,level=1)
            df=diff.reset_index()
            df["scale"]=scale;df["plant_axis"]=role
            df=df.rename(columns={outcome:"delta_acceptance",
                                  **{f"beta_{scale}_{z}":f"delta_{z}" for z in METRICS}})
            allrows.append(df)
            for (context,family),g in df.groupby(["context","family"]):
                draw_mean=g.groupby("draw").delta_acceptance.mean()
                if draw_mean.shape[0]!=N_DRAWS:
                    raise AssertionError("Mismatch in shared 64 prior vector effective unit")
                vals=draw_mean.sort_index().to_numpy(float)
                draws=vals[sampled].mean(axis=1)
                res.append(dict(scale=scale,context=context,family=family,
                                plant_axis=role,n_independent_draws=N_DRAWS,
                                n_same_rate_reverse_plant_pairs=len(g),
                                paired_mean_acceptance_gain=float(vals.mean()),
                                paired_gain_ci_low=float(np.quantile(draws,.025)),
                                paired_gain_ci_high=float(np.quantile(draws,.975)),
                                n_improve=int((g.delta_acceptance>0).sum()),
                                n_worsen=int((g.delta_acceptance<0).sum()),
                                n_tied=int((g.delta_acceptance==0).sum()),
                                **{f"mean_delta_{k}":float(g[f"delta_{k}"].mean())
                                   for k in METRICS}))
    return pd.concat(allrows,ignore_index=True),pd.DataFrame(res)


def run(directory=OUT,prior_256_folder=None,n_boot=BOOT):
    folder=Path(directory);folder.mkdir(parents=True,exist_ok=True)
    source,priors,hashes=load_archived_cross_sources(folder)
    previous=original_256_same_draw_gate(source,prior_256_folder)
    classes,marginals,context= marginalize_sources(source,n_boot=n_boot)
    paired,paired_summary=paired_vegetation_differences(source,n_boot=n_boot)
    tables=dict(cross_ontogeny_144class_abc=classes,
                cross_ontogeny_factor_marginals=marginals,
                cross_ontogeny_context_plant_shares=context,
                cross_ontogeny_vegetation_paired_effects=paired_summary,
                cross_ontogeny_full_paired_mechanism_changes=paired)
    for name,data in tables.items():
        data.to_csv(folder/(name+".csv.gz" if name.endswith("changes") else name+".csv"),
                    index=False,compression={"method":"gzip","mtime":0} if name.endswith("changes") else None)
    receipt=dict(status="ACTUAL_FULL_80Y_CROSS_ONTOGENY_PLANT_ABC_PILOT",
                 n_actual_80year_runs=len(source),n_plant_roles=12,
                 n_contexts=3,n_handling_modes=2,n_risk_states=2,n_reverse_states=2,
                 n_independent_biological_rate_draws=N_DRAWS,
                 n_bootstrap_matched_rate_draws=n_boot,
                 original_256_vegetation_replay=previous,
                 n_classes=N_CLASSES,
                 source_sha256=hashes,
                 no_field_calibrated_biological_rate_priors=True,
                 true_3600_main_ABC_not_completed=True,
                 note="Four pre-adjustment field directions compared only with model-native 2x2x2 log/raw aquatic F_B signs, not field likelihood",
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (folder/"cross_ontogeny_abc_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("CROSSED_VEGETATION_STAGE_MARGINALS\n"+marginals.to_string(index=False),flush=True)
    print("CROSSED_VEGETATION_PAIRED_MECHANISMS\n"+paired_summary.to_string(index=False),flush=True)
    print("CROSSED_VEGETATION_LEADERS\n"+
          classes.sort_values(["scale","conditional_model_share"],
                              ascending=[True,False]).groupby("scale").head(12).to_string(index=False),flush=True)
    print("CROSSED_VEGETATION_ORIGINAL_256_REPLAY\n"+json.dumps(previous),flush=True)
    return classes,marginals,context,paired_summary,receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--dir",type=Path,default=OUT)
    p.add_argument("--original-full256",type=Path,default=None)
    p.add_argument("--bootstrap",type=int,default=BOOT)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.dir,args.original_full256,args.bootstrap)
