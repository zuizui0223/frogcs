"""G1: spatially blocked, source-locked third-guild association versus shared environment.

This does not fit mechanism-model predator abundances or infer wild predation.
All source processing, five spatial folds, binomial acoustic link and ridge
come from immutable PR145 research/scripts/acoustic_mechanism_cv.py.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from acoustic_mechanism_cv import (
    prepare_sites, assign_spatial_folds, base_matrix, zrank,
    train_predict, log_score, ENV, BACKGROUNDS, RIDGE
)

MAIN_SHA="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
BRIDGE_SHA="a5ddc281ba17017a52b404a5725327f6e829824f"
SEED=20261102
N_BOOT=999
ARMS=("env_add","env_OS","env_plant2","env_all",
      "flex_add","flex_OS","flex_plant2","flex_all")
COMPARISONS=(("env_add","env_OS"),("env_add","env_all"),
             ("flex_add","flex_OS"),("flex_add","flex_all"),
             ("flex_plant2","flex_all"))
PREDICTIVE_REPLAY={
    "uniform":{"env_add":.670490,"env_all":.668009},
    "target_group":{"env_add":.672097,"env_all":.674809},
}


def design_matrices(d,background):
    """Original PR145 additive matrix, with outcome-blind extra columns."""
    base=base_matrix(d,background,interactions=False)
    o=zrank(d["mean_suitability_Odonata_"+background])
    s=zrank(d["mean_suitability_pond_breeding_Caudata_"+background])
    v=d.V.to_numpy(dtype=float)
    e=zrank(d[list(ENV)].to_numpy(dtype=float))
    # Exactly six environmental squares plus each unordered 2-way product.
    nonlinear=np.column_stack(
        [e[:,i]*e[:,i] for i in range(len(ENV))]+
        [e[:,i]*e[:,j] for i in range(len(ENV)) for j in range(i+1,len(ENV))]
    )
    if nonlinear.shape!=(len(d),21):
        raise AssertionError("Exactly 21 flexible environment terms expected")
    os=o*s;ov=o*v;sv=s*v;osv=o*s*v
    env_full=np.column_stack([base,os,ov,sv,osv])
    original_full=base_matrix(d,background,interactions=True)
    # PR145 used the same [O,S,V,OS,OV,SV,OSV] order before nuisance.
    # Predictions are invariant to column order with fixed common ridge.
    if not np.allclose(env_full[:,-4:],original_full[:,3:7]):
        raise AssertionError("The 4 original focal interactions have changed")
    designs={
       "env_add":base,
       "env_OS":np.column_stack((base,os)),
       "env_plant2":np.column_stack((base,ov,sv)),
       "env_all":env_full,
    }
    flexible=np.column_stack((base,nonlinear))
    designs.update({
       "flex_add":flexible,
       "flex_OS":np.column_stack((flexible,os)),
       "flex_plant2":np.column_stack((flexible,ov,sv)),
       "flex_all":np.column_stack((flexible,os,ov,sv,osv)),
    })
    if len(designs)!=len(ARMS) or set(designs)!=set(ARMS):
        raise AssertionError("Incomplete frozen common-environment experiment")
    for k,values in designs.items():
        if values.shape[0]!=len(d) or not np.isfinite(values).all():
            raise AssertionError("Nonfinite or source-incomplete design "+k)
    return designs


def heldout(d,folds,*,test_subset=None):
    """One completely held-out prediction per site, background and design."""
    if len(d)!=4248 or set(np.unique(folds))!=set(range(5)):
        raise AssertionError("Original source 5-fold split changed")
    k=d.k.to_numpy(dtype=int)
    n=d.n.to_numpy(dtype=int)
    groups=[]
    for bg in BACKGROUNDS:
        designs=design_matrices(d,bg)
        for fold in range(5):
            test=(folds==fold)
            train=~test
            if test_subset is not None:
                train=train & test_subset
            if train.sum()<1500 or test.sum()<100:
                raise AssertionError("Train/test source split inadequate")
            ix=np.where(test)[0]
            for arm,design in designs.items():
                p=train_predict(design[train],k[train],n[train],
                                design[test],ridge=RIDGE)
                grp=pd.DataFrame(dict(
                    site=d.site.iloc[ix].to_numpy(),
                    route=d.route.iloc[ix].to_numpy(),
                    spatial_block=d.spatial_block.iloc[ix].to_numpy(),
                    fold=fold,background=bg,candidate=arm,
                    k=k[ix],n=n[ix],V=d.V.iloc[ix].to_numpy(dtype=int),
                    predicted=p
                ))
                groups.append(grp)
    out=pd.concat(groups,ignore_index=True)
    if (len(out)!=4248*2*len(ARMS)
        or out.duplicated(["site","background","candidate"]).any()
        or out.groupby(["background","candidate"]).site.nunique().ne(4248).any()):
        raise AssertionError("Missing site-level out-of-block predictions")
    if (out.groupby(["site","background"]).spatial_block.nunique().max()!=1
        or out.groupby(["site","background"]).fold.nunique().max()!=1):
        raise AssertionError("Source spatial-block leakage")
    return out


def summarize(predictions,*,bootstrap=N_BOOT):
    d=predictions.copy()
    d["loss"]=log_score(d.k.to_numpy(),d.n.to_numpy(),d.predicted.to_numpy())
    d["brier"]=d.k*(1-d.predicted)**2+(d.n-d.k)*d.predicted**2
    agg=d.groupby(["background","candidate"],sort=True).agg(
        n_sites=("site","nunique"),
        n_surveys=("n","sum"),
        n_blocks=("spatial_block","nunique"),
        n_vegetation_positive=("V","sum"),
        nll=("loss","sum"),
        brier=("brier","sum")
    ).reset_index()
    agg["nll_per_survey"]=agg.nll/agg.n_surveys
    agg["brier_per_survey"]=agg.brier/agg.n_surveys
    if (len(agg)!=2*len(ARMS) or not agg.n_sites.eq(4248).all()
        or not agg.n_surveys.eq(63180).all() or not agg.n_blocks.eq(56).all()
        or not agg.n_vegetation_positive.eq(506).all()):
        raise AssertionError("Real-data denominators have changed")
    for bg in BACKGROUNDS:
        for arm,value in PREDICTIVE_REPLAY[bg].items():
            observed=agg[(agg.background==bg)&(agg.candidate==arm)].nll_per_survey.iloc[0]
            if abs(observed-value)>1e-5:
                raise AssertionError(f"Immutable PR145 held-out NLL replay mismatch {bg} {arm}: {observed}")
    comparisons=[]
    for bg in BACKGROUNDS:
        dt=d[d.background==bg]
        block=dt.groupby(["candidate","spatial_block"],sort=True).agg(
            total_loss=("loss","sum"),n_surveys=("n","sum")
        ).reset_index()
        blocks=sorted(block.spatial_block.unique())
        if len(blocks)!=56:
            raise AssertionError("Original 56 spatial blocks missing")
        for base,arm in COMPARISONS:
            b=block[block.candidate==base].set_index("spatial_block").loc[blocks]
            x=block[block.candidate==arm].set_index("spatial_block").loc[blocks]
            if not (b.n_surveys.to_numpy()==x.n_surveys.to_numpy()).all():
                raise AssertionError("Different spatial block denominators in paired CV")
            delta=b.total_loss.to_numpy()-x.total_loss.to_numpy()
            visits=b.n_surveys.to_numpy()
            point=delta.sum()/visits.sum()
            rng=np.random.default_rng(SEED)
            index=rng.integers(0,len(blocks),size=(bootstrap,len(blocks)))
            sample=delta[index].sum(axis=1)/visits[index].sum(axis=1)
            lo,hi=np.quantile(sample,[.025,.975])
            comparisons.append(dict(background=bg,baseline=base,augmented=arm,
                gain_nll_per_survey=float(point),bootstrap_95_low=float(lo),
                bootstrap_95_high=float(hi),n_spatial_blocks=56,
                n_completed_surveys=63180,n_sites=4248,n_bootstrap=bootstrap,
                interpretation="conditional block resampling of heldout predictions; not ecological causality"))
    contrasts=pd.DataFrame(comparisons)
    if len(contrasts)!=2*len(COMPARISONS) or contrasts.duplicated(["background","baseline","augmented"]).any():
        raise AssertionError("Complete nested comparison grid required")
    return agg,contrasts


def run(*,sites_path,visits_path,observed_contrasts_path,out):
    for input_path in (sites_path,visits_path,observed_contrasts_path):
        if not input_path.exists():
            raise FileNotFoundError("Original frozen source file absent: "+str(input_path))
    sites=pd.read_csv(sites_path)
    visits=pd.read_csv(visits_path)
    d=prepare_sites(sites,visits,expected_sites=4248)
    if (int(d.n.sum())!=63180 or d.site.duplicated().any()
        or d.route.nunique()!=432 or d.V.sum()!=506):
        raise AssertionError("Original 4248 NAAMP site/visit/route/vegetation ledger changed")
    folds=assign_spatial_folds(d)
    if (d.assign(fold=folds).groupby("route").fold.nunique().max()!=1
        or d.assign(fold=folds).groupby("spatial_block").fold.nunique().max()!=1):
        raise AssertionError("Source held-out route or spatial block contamination")
    obs=pd.read_csv(observed_contrasts_path)
    obs=obs[obs.group.eq("pond_breeding_Caudata")].copy()
    if len(obs)!=4 or obs.duplicated(["background","within_route"]).any():
        raise AssertionError("Missing original field-region and within-route contrasts")
    predictions=heldout(d,folds)
    agg, contrasts=summarize(predictions)
    out.mkdir(parents=True,exist_ok=True)
    predictions.to_csv(out/"heldout_site_predictions.csv.gz",index=False,
       compression={"method":"gzip","mtime":0})
    agg.to_csv(out/"nested_environment_models_heldout_scores.csv",index=False)
    contrasts.to_csv(out/"paired_56_block_gains.csv",index=False)
    obs.to_csv(out/"frozen_observed_high_low_correlations.csv",index=False)
    support=d.assign(fold=folds).groupby(["spatial_block","fold"]).agg(
        n_sites=("site","size"),n_surveys=("n","sum"),positive_vegetation=("V","sum")
    ).reset_index()
    support.to_csv(out/"frozen_56_block_support.csv",index=False)
    expected=contrasts[(contrasts.baseline=="flex_add")&
                       (contrasts.augmented=="flex_OS")]
    robust=bool(len(expected)==2 and (expected.bootstrap_95_low>0).all())
    receipt=dict(
        status="G1_FROGCS_FROZEN_SHARED_ENVIRONMENT_SPATIAL_BLOCK_COMPARISON_SUCCESS",
        source_main_sha=MAIN_SHA,source_bridge_sha=BRIDGE_SHA,
        source_files_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (sites_path,visits_path,observed_contrasts_path)},
        sites=4248,completed_surveys=63180,route_components=432,
        spatial_blocks=56,heldout_folds=5,positive_vegetation_sites=506,
        model_arms=list(ARMS),nuisance_env=list(ENV),
        nonlinear_environment_terms=21,ridge=RIDGE,
        Monte_Carlo_bootstrap=999,seed=SEED,
        source_fixed_prior_145_replay=True,
        incremental_OS_both_backgrounds_interval_positive=robust,
        field_predator_density_measured=False,
        no_new_field_observation=True,
        original_positive_regional_correlations_preserved=True,
        inference="within-cohort incremental predictive value, not observed predation or field trophic causality",
        runtime={"python":platform.python_version(),"numpy":np.__version__,"pandas":pd.__version__}
    )
    (out/"g1_source_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("FROGCS_G1_SHARED_ENVIRONMENT_SOURCE_VERIFIED",json.dumps(receipt),flush=True)
    print("G1_PAIRED_BLOCK_RESULTS\n"+contrasts.to_string(index=False),flush=True)
    return agg,contrasts


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sites",type=Path,required=True)
    p.add_argument("--visits",type=Path,required=True)
    p.add_argument("--observed-contrasts",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    run(sites_path=args.sites,visits_path=args.visits,
        observed_contrasts_path=args.observed_contrasts,out=args.output)
