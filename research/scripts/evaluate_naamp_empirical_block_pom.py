"""Observed residual-ICC-conditioned acoustic POM for archived mechanism sources.

Reuses exactly the same full-rank rank R², same 4,248 NAAMP sites, same
direction/low-S ternary pattern definitions and the identical genuinely rerun
80-year source artifacts from PR #146. Only the Gaussian 2-degree block
component is changed from an *invented .25 amplitude* to an empirical
NAAMP pooled-regression-residual method-of-moments amplitude.

This is NOT independent acoustic-detection-noise calibration: geographic
ecological variation is included in those residual moments. No biological
scenario posterior is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from select_macro_trophic_scenarios import ROOT,SITE,VISITS,SEED,load_cohort
from pattern_oriented_abc_pilot import BACKGROUNDS
from r2_calibrated_directional_pom import (
    MODES,FAMILIES,N_CAL,N_EVAL,rankrows,site_rank_r2,
    signal_at_sites,calibrate_r2,five_pattern_matrix,categories,
    category_agreement,observed_context,source_families
)
from estimate_naamp_residual_spatial_icc import empirical_block_noise

SOURCE=ROOT/"research/results/macro_observed_residual_icc_20261031/observed_residual_spatial_icc.csv"
OUT=ROOT/"research/results/macro_empirical_block_pom_20261031"
MATCH=("MATCHED_R2","MATCHED_WITHOUT_NOISE")
N_EVAL_COMPARE=128


def read_icc(path=SOURCE):
    if not Path(path).is_file():
        raise FileNotFoundError("Real NAAMP ICC audit required: "+str(path))
    s=pd.read_csv(path)
    if len(s)!=2 or set(s.background)!=set(BACKGROUNDS):
        raise ValueError("Incomplete actual NAAMP residual spatial structure")
    if s.sites.ne(4248).any() or s.completed_surveys.ne(63180).any() or s.n_spatial_blocks.ne(56).any():
        raise AssertionError("Residual spatial grouping not comparable to 4248-site cohort")
    for row in s.itertuples(index=False):
        if not np.isclose(row.alpha_block_to_site**2,
                          row.icc/(1-row.icc),rtol=0,atol=1e-12):
            raise AssertionError("Residual ICC does not match Gaussian amplitude")
        if not 0<=row.icc<1:
            raise ValueError("Invalid empirical-block correlation")
        if not 0<=row.spatial_icc_ci_low<=row.spatial_icc_ci_high<1:
            raise ValueError("Invalid empirical block interval")
    return s.set_index("background")


def evaluate(family,cal=16,n_eval=N_EVAL_COMPARE,out=OUT,icc_path=SOURCE):
    if family not in FAMILIES:raise ValueError("Wrong source family")
    if cal<4 or n_eval<8:raise ValueError("Too few fixed Gaussian replicates")
    out.mkdir(parents=True,exist_ok=True)
    site=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if int(site.n.sum())!=63180 or int(site.V.sum())!=506:
        raise AssertionError("NAAMP original observation ledger changed")
    icc=read_icc(icc_path)
    grids,labels,alias,groups,provenance=source_families(family)
    rows=[];summary=[];observations=[]
    for bg in BACKGROUNDS:
        context=observed_context(site,bg)
        ref=icc.loc[bg]
        target=float(context["target_r2"])
        if not np.isclose(target,float(ref.observed_8term_rank_r2),atol=1e-9,rtol=0):
            raise AssertionError("Measured residual ICC and POM R² have different original estimands")
        correlation=float(ref.icc)
        amplitude=float(ref.alpha_block_to_site)
        offset=(0 if bg=="uniform" else 10000)
        # Reuse the original experiment's seeds and unit Gaussian convention;
        # only the block component alpha is changed from .25 to empirical.
        calibration=empirical_block_noise(site,cal,SEED+711+40000+offset,correlation)
        evaluation=empirical_block_noise(site,n_eval,SEED+2711+40000+offset,correlation)
        obs_state=context["observed_boot5"]
        for i,name in enumerate(("OS","OV","delta_S_high_minus_low",
                                 "delta_V_positive_minus_zero","O_with_S_low")):
            observations.append(dict(family=family,background=bg,pattern=name,
                                     target_rank_r2=target,measured_residual_icc=correlation,
                                     measured_gaussian_block_alpha=amplitude,
                                     observed_estimate=float(context["point"][i]),
                                     selected=bool(i in context["selected"]),
                                     observed_lowS_zero_band=float(context["delta"])
                                     if i==4 else np.nan))
        for mode in MODES:
            for idx,(grp,members) in enumerate(sorted(groups.items())):
                signal=signal_at_sites(site,bg,grids[members[0]],mode)
                calibrated=calibrate_r2(signal,target,calibration,context["q"])
                perturbed=rankrows(signal[None,:]+
                                   calibrated["sigma"]*evaluation)
                actual_r2=site_rank_r2(perturbed,context["q"])
                stats=five_pattern_matrix(perturbed,context["design"],context["pinv"])
                category=categories(stats,context["delta"])
                soft,exact=category_agreement(obs_state,category,context["selected"])
                modal=context["modal"][list(context["selected"])]
                matches=np.all(category[:,list(context["selected"])]==modal[None,:],axis=1)
                q=(category[:,4]==0).mean()
                row=dict(
                    family=family,noise_type="naamp_residual_icc_2degree",
                    background=bg,mode=mode,source_group=grp,
                    n_exact_aliases=len(members),
                    r2_target=target,icc_residual=correlation,alpha_block=amplitude,
                    icc_ci_low=float(ref.spatial_icc_ci_low),
                    icc_ci_high=float(ref.spatial_icc_ci_high),
                    r2_evaluation_mean=float(actual_r2.mean()),
                    r2_evaluation_sd=float(actual_r2.std(ddof=1)),
                    **calibrated,
                    soft_joint_agreement=float(soft),
                    exact_observed_bootstrap_joint_agreement=float(exact),
                    modal_complete_frequency=float(matches.mean()),
                    modal_complete_count=int(matches.sum()),
                    eval_reps=n_eval,
                    q_lowS_near_zero=float(q),
                    q_negative_OS=float(np.mean(category[:,0]<0)),
                    q_negative_OV=float(np.mean(category[:,1]<0)),
                    q_negative_delta_S=float(np.mean(category[:,2]<0)),
                    q_negative_delta_V=float(np.mean(category[:,3]<0)),
                    n_selected=len(context["selected"]),
                    selected_patterns=";".join(
                        ["OS","OV","delta_S_high_minus_low",
                         "delta_V_positive_minus_zero","O_with_S_low"][j]
                        for j in context["selected"]))
                rows.append(row)
                if idx%40==0:
                    print("EMPIRICAL_ICC_POM",family,bg,mode,idx+1,"of",len(groups),
                          "icc",round(correlation,6),
                          "target_r2",round(target,6),
                          "status",calibrated["calibration_status"],flush=True)
            matching=[r for r in rows
                      if r["background"]==bg and r["mode"]==mode and
                         r["calibration_status"] in MATCH]
            if len(matching):
                best=sorted(matching,key=lambda r:(-r["soft_joint_agreement"],
                                                   r["source_group"]))[0]
                n_complete=sum(r["modal_complete_count"]>0 for r in matching)
                n10=sum(r["modal_complete_frequency"]>=.1 for r in matching)
                n_bad=len(groups)-len(matching)
                summary.append(dict(family=family,background=bg,mode=mode,
                                    n_source_groups=len(groups),
                                    n_r2_matched=len(matching),
                                    n_r2_not_matched=n_bad,
                                    n_group_with_any_full_sign_match=n_complete,
                                    n_group_with_ge_10pct_full_sign_match=n10,
                                    best_source_group=best["source_group"],
                                    best_joint_score=best["soft_joint_agreement"],
                                    best_full_sign_frequency=best["modal_complete_frequency"],
                                    best_lowS_zero_frequency=best["q_lowS_near_zero"],
                                    empirical_icc=correlation,empirical_alpha=amplitude,
                                    status="CONDITIONAL_OBSERVED_RESIDUAL_ICC_NOT_CAUSAL"))
            else:
                summary.append(dict(family=family,background=bg,mode=mode,
                                    n_source_groups=len(groups),n_r2_matched=0,
                                    n_r2_not_matched=len(groups),
                                    status="ALL_NOISE_R2_UNREACHABLE"))
    score=pd.DataFrame(rows);summ=pd.DataFrame(summary);ob=pd.DataFrame(observations)
    if len(score)!=len(groups)*len(BACKGROUNDS)*len(MODES) or len(summ)!=4 or len(ob)!=10:
        raise AssertionError("Incomplete empirical ICC source/background/mode matrix")
    # Exact-source groups must be identified even when scenario labels repeat.
    for name,df in [("source_group_scores",score),("family_summary",summ),
                    ("observed_icc_and_patterns",ob)]:
        df.to_csv(out/(family+"_"+name+".csv"),index=False)
    allmatched=score[score.calibration_status.isin(MATCH)]
    intersection=[]
    for mode in MODES:
        q=allmatched[(allmatched['mode']==mode)&(allmatched.modal_complete_count>0)]
        x=q.groupby("source_group").background.nunique()
        both=sorted(x[x==2].index)
        intersection.append(dict(family=family,mode=mode,
                                 n_groups_with_matching_simulation_both_backgrounds=len(both),
                                 groups=";".join(both)))
    both=pd.DataFrame(intersection)
    both.to_csv(out/(family+"_cross_background_groups.csv"),index=False)
    record=dict(status="POM_CONDITIONAL_ON_NAAMP_RESIDUAL_SPATIAL_ICC_NOT_DETECTION_CALIBRATION",
                family=family,sites=len(site),visits=int(site.n.sum()),n_groups=len(groups),
                original_case_labels=len(grids),noise_calibration_fields=cal,
                independent_eval_fields=n_eval,spatial_block_definition="route centroid 2 degree",
                near_zero_labeling="observed 999-block bootstrap low-S ternary",
                r2_noise_calibrated_per_source_group=True,
                spatial_icc_not_independent="Observed residual after same eight-column rank OLS includes unmeasured ecology and spatial sampling",
                no_external_acoustic_stage_bridge=True,
                icc_input_sha256=hashlib.sha256(Path(icc_path).read_bytes()).hexdigest(),
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [SITE,VISITS,*provenance]},
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(family+"_receipt.json")).write_text(json.dumps(record,indent=2)+"\n")
    print("EMPIRICAL_ICC_FAMILY_SUMMARY\n"+summ.to_string(index=False),flush=True)
    print("EMPIRICAL_ICC_BOTH_SDM_BACKGROUND\n"+both.to_string(index=False),flush=True)
    return dict(scores=score,summary=summ,observed=ob,both=both)


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--family",required=True,choices=FAMILIES)
    a.add_argument("--icc-source",type=Path,default=SOURCE)
    a.add_argument("--cal-reps",type=int,default=16)
    a.add_argument("--eval-reps",type=int,default=N_EVAL_COMPARE)
    v=a.parse_args()
    if not v.run:a.error("Explicit --run required")
    evaluate(v.family,v.cal_reps,v.eval_reps,icc_path=v.icc_source)


if __name__=="__main__":
    main()
