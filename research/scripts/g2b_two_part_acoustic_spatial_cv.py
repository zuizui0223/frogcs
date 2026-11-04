"""Source-locked G2B two-part acoustic observation test, not larval calibration.

Out-of-geographic-block original PR145 training, original G1 env matrices,
fixed source 4248 sites/63180 NAAMP survey visits. Distinguish:
 any/n, strong/any, direct strong/n, factored P(any)*P(strong|any).
No test-outcome information enters predictor training or factored predictions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from acoustic_mechanism_cv import (
    prepare_sites, assign_spatial_folds, train_predict,
    log_score, BACKGROUNDS, RIDGE
)
from g1_shared_environment_spatial_block import design_matrices
from g2_acoustic_outcome_definition_audit import rebuild

SOURCE_MAIN_SHA="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
PR145_SHA="a5ddc281ba17017a52b404a5725327f6e829824f"
SOURCE_SITES=4248
SOURCE_VISITS=63180
SOURCE_ANY=47912
SOURCE_STRONG=36554
SOURCE_NO_ANY_SITES=66
N_BLOCKS=56
N_ROUTES=432
N_FOLDS=5
ARMS=("env_add","env_OS","flex_add","flex_OS")
STAGES=("any_all","strong_given_any","strong_all_direct","strong_all_factored")
PAIRS=(("env_add","env_OS"),("flex_add","flex_OS"))
BOOT_SEED=20261105
BOOT=999
REPLAY={
    "uniform":{"env_add":.670490,"env_OS":.668798},
    "target_group":{"env_add":.672097,"env_OS":.673882}
}


def require(ok,msg):
    if not bool(ok):
        raise AssertionError(msg)


def verified_data(site_file,visit_file):
    raw_sites=pd.read_csv(site_file)
    visits=pd.read_csv(visit_file)
    d=prepare_sites(raw_sites,visits,expected_sites=SOURCE_SITES)
    obs=rebuild(raw_sites,visits)
    require(set(d.site)==set(obs.site) and d.site.is_unique,
            "Site identities changed between original G1 and G2")
    obs=obs.set_index("site").loc[d.site].reset_index()
    any_count=obs.any_events.to_numpy(dtype=int)
    strong_count=obs.strong_events.to_numpy(dtype=int)
    n=d.n.to_numpy(dtype=int)
    require(np.array_equal(strong_count,d.k.to_numpy(dtype=int)),
            "Original PR145 strong event count not repeated by source G2")
    require(int(n.sum())==SOURCE_VISITS and
            int(any_count.sum())==SOURCE_ANY and
            int(strong_count.sum())==SOURCE_STRONG and
            int(np.count_nonzero(any_count==0))==SOURCE_NO_ANY_SITES,
            "Original acoustic visit response source totals drifted")
    require((n>=1).all() and
            (strong_count<=any_count).all() and (any_count<=n).all() and
            (strong_count>=0).all(),
            "Unphysical or incomplete acoustic visit state")
    require(d.route.nunique()==N_ROUTES and d.spatial_block.nunique()==N_BLOCKS,
            "Source geographic block and route support differs")
    folds=assign_spatial_folds(d)
    require(set(folds)==set(range(N_FOLDS)) and
            d.assign(fold=folds).groupby("route").fold.nunique().max()==1 and
            d.assign(fold=folds).groupby("spatial_block").fold.nunique().max()==1,
            "Original holdout source block leakage")
    return d,folds,any_count,strong_count,n


def model_predictions(d,folds,k_any,k_strong,n):
    records=[]
    for background in BACKGROUNDS:
        design=design_matrices(d,background)
        for fold in range(N_FOLDS):
            test=folds==fold
            train=~test
            conditional_train=train & (k_any>0)
            test_ix=np.flatnonzero(test)
            require(train.sum()>2000 and conditional_train.sum()>1800 and test.sum()>100,
                    "Original source fold has insufficient train/test sites")
            for arm in ARMS:
                m=design[arm]
                pa=train_predict(m[train],k_any[train],n[train],m[test],ridge=RIDGE)
                pc=train_predict(m[conditional_train],k_strong[conditional_train],
                                 k_any[conditional_train],m[test],ridge=RIDGE)
                pdirect=train_predict(m[train],k_strong[train],n[train],m[test],ridge=RIDGE)
                p_factored=pa*pc
                require(np.isfinite([*pa,*pc,*pdirect,*p_factored]).all() and
                        (pa>=0).all() and (pa<=1).all() and
                        (pc>=0).all() and (pc<=1).all() and
                        (pdirect>=0).all() and (pdirect<=1).all() and
                        (p_factored>=0).all() and (p_factored<=pa+1e-12).all(),
                        "Invalid biological observation-proxy state probabilities")
                records.append(pd.DataFrame(dict(
                    site=d.site.iloc[test_ix].to_numpy(),
                    route=d.route.iloc[test_ix].to_numpy(),
                    spatial_block=d.spatial_block.iloc[test_ix].to_numpy(),
                    fold=fold,background=background,candidate=arm,
                    n_completed=n[test_ix],n_any=k_any[test_ix],n_strong=k_strong[test_ix],
                    pred_any=pa,pred_given_any=pc,
                    pred_strong_direct=pdirect,pred_strong_factored=p_factored,
                )))
    x=pd.concat(records,ignore_index=True)
    require(len(x)==SOURCE_SITES*len(BACKGROUNDS)*len(ARMS) and
            not x.duplicated(["site","background","candidate"]).any() and
            x.groupby(["background","candidate"]).site.nunique().eq(SOURCE_SITES).all(),
            "Missing original single heldout prediction per physical site")
    require(x.groupby(["site","background"]).fold.nunique().eq(1).all() and
            x.groupby(["site","background"]).spatial_block.nunique().eq(1).all(),
            "Source heldout block or site split across candidate models")
    return x


def scored(pred):
    cols={
      "any_all":("n_any","n_completed","pred_any"),
      "strong_given_any":("n_strong","n_any","pred_given_any"),
      "strong_all_direct":("n_strong","n_completed","pred_strong_direct"),
      "strong_all_factored":("n_strong","n_completed","pred_strong_factored"),
    }
    frames=[]
    for stage,(numerator,denominator,p_col) in cols.items():
        part=pred.copy()
        if stage=="strong_given_any":
            part=part[part.n_any>0].copy()
        part["observation_stage"]=stage
        part["trials"]=part[denominator].astype(int)
        part["successes"]=part[numerator].astype(int)
        part["loss"]=log_score(part.successes,part.trials,part[p_col])
        part["brier"]=(part.successes*(1-part[p_col])**2+
                       (part.trials-part.successes)*part[p_col]**2)
        require((part.trials>0).all() and part.loss.ge(0).all(),
                "Nonpositive source trials/invalid observed acoustic loss")
        frames.append(part[[
          "site","route","spatial_block","fold","background","candidate",
          "observation_stage","trials","successes","loss","brier"
        ]])
    long=pd.concat(frames,ignore_index=True)
    group=["background","candidate","observation_stage"]
    agg=long.groupby(group,sort=True).agg(
        sites=("site","nunique"),blocks=("spatial_block","nunique"),
        trials=("trials","sum"),events=("successes","sum"),
        nll_sum=("loss","sum"),brier_sum=("brier","sum")
    ).reset_index()
    agg["nll_per_trial"]=agg.nll_sum/agg.trials
    agg["brier_per_trial"]=agg.brier_sum/agg.trials
    require(len(agg)==len(BACKGROUNDS)*len(ARMS)*len(STAGES),
            "Incomplete two-part acoustic outcome model score grid")
    for stage in STAGES:
        g=agg[agg.observation_stage==stage]
        expected_trials=SOURCE_ANY if stage=="strong_given_any" else SOURCE_VISITS
        expected_sites=SOURCE_SITES-SOURCE_NO_ANY_SITES if stage=="strong_given_any" else SOURCE_SITES
        expected_events=SOURCE_ANY if stage=="any_all" else SOURCE_STRONG
        require(g.trials.eq(expected_trials).all() and
                g.sites.eq(expected_sites).all() and
                g.blocks.eq(N_BLOCKS).all() and
                g.events.eq(expected_events).all(),
                "Observed any/strong source denominator changed under a model")
    for bg in BACKGROUNDS:
        for arm,reference in REPLAY[bg].items():
            result=agg[(agg.background==bg)&(agg.candidate==arm)&
                       (agg.observation_stage=="strong_all_direct")].nll_per_trial
            require(len(result)==1 and abs(float(result.iloc[0])-reference)<3e-5,
                    "Source original G1 adult strong-call held-out score mismatch")
    return long,agg


def paired_intervals(long,n_bootstrap=BOOT):
    results=[]
    for bg in BACKGROUNDS:
        sub=long[long.background==bg]
        for stage in STAGES:
            data=sub[sub.observation_stage==stage]
            blocks=(data.groupby(["candidate","spatial_block"],sort=True)
                         .agg(loss=("loss","sum"),trials=("trials","sum"))
                         .reset_index())
            def interval(baseline,augmented,label):
                b=blocks[blocks.candidate==baseline].set_index("spatial_block").sort_index()
                a=blocks[blocks.candidate==augmented].set_index("spatial_block").sort_index()
                require(len(b)==N_BLOCKS and b.index.equals(a.index) and
                        np.array_equal(b.trials,a.trials),
                        "Source geographic blocks not paired in observation stage "+stage)
                d=(b.loss-a.loss).to_numpy(float)
                n=b.trials.to_numpy(dtype=float)
                require((n>=0).all() and n.sum()>0,"Invalid binomial denominators")
                rng=np.random.default_rng(BOOT_SEED)
                draws=rng.integers(0,N_BLOCKS,size=(n_bootstrap,N_BLOCKS))
                bs=d[draws].sum(axis=1)/n[draws].sum(axis=1)
                lo,hi=np.quantile(bs,[.025,.975])
                return dict(background=bg,stage=stage,baseline=baseline,
                            augmented=augmented,comparison=label,
                            gain_nll_per_trial=float(d.sum()/n.sum()),
                            conditional_95_low=float(lo),conditional_95_high=float(hi),
                            original_source_blocks=N_BLOCKS,
                            n_observation_trials=int(n.sum()),
                            bootstrap=n_bootstrap,
                            independent_wild_sites_not_obtained=True)
            for base,addition in PAIRS:
                results.append(interval(base,addition,"incremental_OS"))
        # The factored and direct strong-call links differ in source model
        # architecture, not in denominators or field response definitions.
        # Combine their heldout losses from the exact same sites/blocks.
        for arm in ARMS:
            b=(sub[(sub.observation_stage=="strong_all_direct")&(sub.candidate==arm)]
                 .groupby("spatial_block").agg(loss=("loss","sum"),trials=("trials","sum"))
                 .sort_index())
            a=(sub[(sub.observation_stage=="strong_all_factored")&(sub.candidate==arm)]
                 .groupby("spatial_block").agg(loss=("loss","sum"),trials=("trials","sum"))
                 .sort_index())
            require(len(b)==N_BLOCKS and b.index.equals(a.index) and
                    np.array_equal(b.trials,a.trials),
                    "Direct strong and two-part strong are not the same observed trial population")
            d=b.loss.to_numpy(float)-a.loss.to_numpy(float)
            n=b.trials.to_numpy(float)
            rng=np.random.default_rng(BOOT_SEED)
            ix=rng.integers(0,N_BLOCKS,size=(n_bootstrap,N_BLOCKS))
            bs=d[ix].sum(axis=1)/n[ix].sum(axis=1)
            lo,hi=np.quantile(bs,[.025,.975])
            results.append(dict(background=bg,stage="strong_all_factored",
               baseline=arm,augmented=arm,comparison="factored_vs_direct_strong",
               gain_nll_per_trial=float(d.sum()/n.sum()),
               conditional_95_low=float(lo),conditional_95_high=float(hi),
               original_source_blocks=N_BLOCKS,n_observation_trials=int(n.sum()),
               bootstrap=n_bootstrap,independent_wild_sites_not_obtained=True))
    out=pd.DataFrame(results)
    require(len(out)==len(BACKGROUNDS)*(len(STAGES)*len(PAIRS)+len(ARMS)) and
            not out.duplicated(["background","stage","baseline","augmented","comparison"]).any(),
            "Precommitted G2B 24 paired block comparisons incomplete")
    return out


def graphic(comp,out):
    c=comp[(comp.comparison=="incremental_OS") &
           (comp.baseline=="flex_add")].copy()
    fig,ax=plt.subplots(figsize=(11,5.6))
    stages=("any_all","strong_given_any","strong_all_direct","strong_all_factored")
    label=("Any calling / completed visit","Strong | any calling visit",
           "Strong direct / completed visit","Strong factored / completed visit")
    for i,stage in enumerate(stages):
        for bg,off,marker in (("uniform",-.11,"o"),("target_group",.11,"s")):
            x=c[(c.stage==stage)&(c.background==bg)]
            require(len(x)==1,"Heldout two-part source G2B figure missing row")
            z=x.iloc[0]
            ax.errorbar(float(z.gain_nll_per_trial),3-i+off,
                        xerr=[[float(z.gain_nll_per_trial-z.conditional_95_low)],
                              [float(z.conditional_95_high-z.gain_nll_per_trial)]],
                        marker=marker,linestyle="none",capsize=4,
                        color="C0" if bg=="uniform" else "C1")
    ax.set_yticks(range(4),list(reversed(label)))
    ax.axvline(0,color="grey",linewidth=1)
    ax.set_xlabel("Held-out NLL reduction after O×S addition (positive = improvement)")
    ax.set_title("G2B · Does third-guild information survive a two-part acoustic observation model?")
    ax.grid(axis="x",alpha=.2)
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0],[0],color="C0",marker="o",linestyle="none",label="Uniform SDM"),
        Line2D([0],[0],color="C1",marker="s",linestyle="none",label="Target-group SDM"),
    ],loc="upper center",bbox_to_anchor=(.5,1.09),ncol=2,frameon=False)
    fig.text(.015,.01,"Source 56-block bootstrap intervals, 999 draws. Conditional stage scores per recorded any-call; others per completed visit. Adult calls ≠ aquatic predator ecology.",fontsize=8)
    fig.tight_layout(rect=(0,.06,1,.85))
    fig.savefig(out/"G2B_spatial_holdout_two_part_acoustic_incremental_OS.png",dpi=180)
    plt.close(fig)


def run(site,visits,out):
    d,folds,k_any,k_strong,n=verified_data(site,visits)
    heldout=model_predictions(d,folds,k_any,k_strong,n)
    long,agg=scored(heldout)
    contrasts=paired_intervals(long)
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    heldout.to_csv(out/"source_4248_site_two_part_heldout_predictions.csv.gz",
                   index=False,compression={"method":"gzip","mtime":0})
    agg.to_csv(out/"G2B_stage_model_scores.csv",index=False)
    contrasts.to_csv(out/"G2B_56block_paired_increments.csv",index=False)
    block_counts=d.assign(fold=folds).groupby(["spatial_block","fold"]).agg(
        n_sites=("site","size"),n_completed=("n","sum")).reset_index()
    block_counts.to_csv(out/"G2B_original_spatial_block_support.csv",index=False)
    graphic(contrasts,out)
    primary=contrasts[(contrasts.comparison=="incremental_OS")&
              (contrasts.stage=="strong_given_any")&
              (contrasts.baseline=="flex_add")]
    robust=bool(len(primary)==2 and primary.conditional_95_low.gt(0).all())
    receipt=dict(
      status="G2B_ORIGINAL_4248_SITE_TWO_PART_ACOUSTIC_SPATIAL_HELDOUT_SOURCE_AUDITED",
      original_main_sha=SOURCE_MAIN_SHA,statistical_bridge_sha=PR145_SHA,
      n_original_sites=SOURCE_SITES,n_original_completed_visits=SOURCE_VISITS,
      original_any_positive_visits=SOURCE_ANY,
      original_strong_positive_visits=SOURCE_STRONG,
      original_any_zero_sites=SOURCE_NO_ANY_SITES,
      n_original_routes=N_ROUTES,n_geographic_blocks=N_BLOCKS,n_folds=N_FOLDS,
      original_ridge=RIDGE,n_designs_per_background=len(ARMS),
      n_outcome_definition_scores=len(agg),n_paired_block_comparisons=len(contrasts),
      n_original_site_prediction_rows=len(heldout),
      conditional_strong_trials=SOURCE_ANY,
      original_G1_direct_strong_source_replay=True,
      conditional_strong_OS_gain_positive_both_backgrounds=robust,
      bootstrap_seed=BOOT_SEED,bootstrap_draws=BOOT,
      source_files_sha256={Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest()
                           for p in (site,visits)},
      larval_to_calling_biological_observation_link_calibrated=False,
      observed_detection_probability_estimated=False,
      source_cohort_independent_field_validation=False,
      did_not_refit_biological_80year_model=True,
      interpretation="two-part adult acoustic statistical response sensitivity, not measured predation",
    )
    (out/"G2B_source_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("G2B_ORIGINAL_TWO_PART_SOURCE_AUDIT_SUCCESS",
          json.dumps({k:v for k,v in receipt.items() if k!="source_files_sha256"}),flush=True)
    print("G2B_PAIR_SOURCE_GAINS\n"+contrasts.to_string(index=False),flush=True)
    print("G2B_SOURCE_MODELS\n"+agg.to_string(index=False),flush=True)
    return agg,contrasts


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--sites",type=Path,required=True)
    p.add_argument("--visits",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.sites,a.visits,a.output)
