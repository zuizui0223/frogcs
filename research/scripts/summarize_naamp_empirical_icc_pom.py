"""Final three-noise-structure ecological POM audit with paired S→D risk effects.

Compares existing successful iid and artificial .25 block Gaussian models to a
new NAAMP rank-OLS residual ICC-matched Gaussian model, all source groups.

All 12 conditions (3 noise structures x 2 SDM backgrounds x 2 rank/log
signals) are *sensitivity assumptions* on the same NAAMP outcomes, NOT 12
independent replications. No posterior mechanism probabilities.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from r2_calibrated_directional_pom import FAMILIES,MODES,BACKGROUNDS

ROOT=Path("research/results/macro_empirical_block_pom_20261031")
OLD=Path("research/results/macro_r2_matched_directional_20261031")
CALIBRATION=("MATCHED_R2","MATCHED_WITHOUT_NOISE")
NEW_NOISE="naamp_residual_icc_2degree"
OLD_NOISE=("iid","spatial_block_025")
CONTEXTS=3*len(MODES)*len(BACKGROUNDS)


def combine(new,old):
    prev=pd.read_csv(old/"all_source_group_scores.csv")
    if set(prev.noise_type)!=set(OLD_NOISE):
        raise ValueError("Prior noise structure is missing")
    data=[prev]
    labels=[]
    summary=[]
    for family in FAMILIES:
        p=new/(family+"_source_group_scores.csv")
        lp=new/(family+"_candidate_scores.csv")
        sp=new/(family+"_family_summary.csv")
        if any(not z.is_file() for z in (p,lp,sp)):
            raise FileNotFoundError("Missing true ICC output for "+family)
        d=pd.read_csv(p)
        lab=pd.read_csv(lp)
        sm=pd.read_csv(sp)
        if not d.noise_type.eq(NEW_NOISE).all() or d.family.nunique()!=1:
            raise AssertionError("Not measured-ICC source family")
        n={"frozen132":104,"realrate192":128,"facilitation72":48}[family]
        x={"frozen132":132,"realrate192":192,"facilitation72":72}[family]
        if len(d)!=4*n or len(lab)!=4*x or len(sm)!=4:
            raise AssertionError("Source grouping or same-site observable missing")
        data.append(d);labels.append(lab);summary.append(sm)
    combined=pd.concat(data,ignore_index=True)
    for family,n in [("frozen132",104),("realrate192",128),("facilitation72",48)]:
        q=combined[combined.family==family]
        if len(q)!=CONTEXTS*n:
            raise AssertionError("Missing noise-context comparison source cases")
        if q.duplicated(["noise_type","background","mode","source_group"]).any():
            raise AssertionError("Duplicated source under a noise context")
        if q.groupby("source_group").size().ne(CONTEXTS).any():
            raise AssertionError("Missing matched noise response for a source group")
    return combined,pd.concat(labels,ignore_index=True),pd.concat(summary,ignore_index=True)


def robust_three_noise(combined):
    rows=[];coverage=[]
    for (family,source),q in combined.groupby(["family","source_group"]):
        if len(q)!=CONTEXTS:raise ValueError("Incomplete 12-context scenario")
        matched=q.calibration_status.isin(CALIBRATION)
        frac=q.modal_complete_frequency.to_numpy(float)
        row=dict(family=family,source_group=source,n_conditions=CONTEXTS,
                 n_r2_calibrated=int(matched.sum()),
                 n_contexts_with_any_exact=int((frac>0).sum()),
                 n_contexts_at_least_10pct=int((frac>=.1).sum()),
                 min_exact_match_frequency=float(frac.min()),
                 mean_exact_match_frequency=float(frac.mean()),
                 min_joint_soft_score=float(q.soft_joint_agreement.min()),
                 mean_joint_soft_score=float(q.soft_joint_agreement.mean()),
                 all_12_any_exact=bool(np.all(frac>0)&matched.all()),
                 all_12_ge_10pct=bool(np.all(frac>=.1)&matched.all()))
        rows.append(row)
    stable=pd.DataFrame(rows)
    for family,g in stable.groupby("family"):
        best=g.sort_values(["min_joint_soft_score","source_group"],
                           ascending=[False,True]).iloc[0]
        coverage.append(dict(family=family,n_source_groups=len(g),
                             n_all_12_any_exact=int(g.all_12_any_exact.sum()),
                             n_all_12_ge_10pct=int(g.all_12_ge_10pct.sum()),
                             max_number_of_conditions_any_exact=int(g.n_contexts_with_any_exact.max()),
                             best_maximin_source_group=best.source_group,
                             best_min_joint_soft_score=float(best.min_joint_soft_score),
                             best_min_complete_frequency=float(best.min_exact_match_frequency)))
    return stable,pd.DataFrame(coverage)


def matched_forthcoming_facilitation(labels):
    x=labels[labels.family=="facilitation72"]
    expected=72*4
    if len(x)!=expected:raise AssertionError("Missing neutral/moderate/strong aliases")
    rows=[]
    for (bg,mode,case),g in x.groupby(["background","mode","case"]):
        if set(g.hypothesis)!={"neutral","moderate","strong"} or len(g)!=3:
            raise ValueError("No paired facilitation contrast at exact original case")
        baseline=g[g.hypothesis=="neutral"].iloc[0]
        for treatment in ("moderate","strong"):
            contrast=g[g.hypothesis==treatment].iloc[0]
            okay=(baseline.calibration_status in CALIBRATION and
                  contrast.calibration_status in CALIBRATION)
            rows.append(dict(background=bg,mode=mode,case=case,
                             treatment=treatment,both_r2_matched=bool(okay),
                             neutral_group=baseline.source_group,
                             treatment_group=contrast.source_group,
                             neutral_soft=float(baseline.soft_joint_agreement),
                             treatment_soft=float(contrast.soft_joint_agreement),
                             delta_soft=float(contrast.soft_joint_agreement-
                                              baseline.soft_joint_agreement),
                             neutral_complete=float(baseline.modal_complete_frequency),
                             treatment_complete=float(contrast.modal_complete_frequency),
                             delta_complete=float(contrast.modal_complete_frequency-
                                                  baseline.modal_complete_frequency),
                             delta_lowS_nearzero=float(contrast.q_lowS_near_zero-
                                                        baseline.q_lowS_near_zero)))
    matched=pd.DataFrame(rows)
    if len(matched)!=24*2*2*2 or matched.groupby(["case","treatment"]).size().ne(4).any():
        raise AssertionError("Incomplete 4 observational contrasts for facilitation")
    summaries=[]
    for (bg,mode,treatment),g in matched.groupby(["background","mode","treatment"]):
        good=g[g.both_r2_matched]
        if len(good)!=24:
            raise ValueError("No full R² calibration for paired comparison")
        summaries.append(dict(background=bg,mode=mode,treatment=treatment,
                              n_cases=len(good),
                              positive_cases=int((good.delta_soft>1e-12).sum()),
                              negative_cases=int((good.delta_soft< -1e-12).sum()),
                              mean_gain=float(good.delta_soft.mean()),
                              median_gain=float(good.delta_soft.median()),
                              min_gain=float(good.delta_soft.min()),
                              max_gain=float(good.delta_soft.max()),
                              n_complete_frequency_gain=int((good.delta_complete>1e-12).sum())))
    return matched,pd.DataFrame(summaries)


def run(new=ROOT,old=OLD):
    new.mkdir(parents=True,exist_ok=True)
    combined,labels,rawsummaries=combine(new,old)
    stable,coverage=robust_three_noise(combined)
    paired,pair_summary=matched_forthcoming_facilitation(labels)
    prior=pd.read_csv(old/"source_family_summary.csv")
    new_summary=rawsummaries.copy()
    compare=pd.concat([prior,new_summary],ignore_index=True)
    if len(compare)!=36:
        raise AssertionError("Expected 24 old + 12 new cohort summaries")
    for name,frame in [("all_group_three_noise_scores",combined),
                       ("source_three_noise_12_context_stability",stable),
                       ("three_noise_family_coverage",coverage),
                       ("empirical_icc_vs_older_025_iid",compare),
                       ("empirical_icc_paired_facilitation_cases",paired),
                       ("empirical_icc_paired_facilitation_summary",pair_summary)]:
        frame.to_csv(new/(name+".csv"),index=False)
    print("THREE_NOISE_CONSENSUS\n"+coverage.to_string(index=False),flush=True)
    print("OBSERVED_ICC_PAIRED_DANGER\n"+pair_summary.to_string(index=False),flush=True)
    print("ALL_EMPIRICAL_ICC_FAMILIES\n"+newsummaries if False else
          "ALL_EMPIRICAL_ICC_FAMILIES\n"+rawsummaries.to_string(index=False),flush=True)
    return dict(coverage=coverage,paired=pair_summary,stability=stable,
                full=combined,new_summary=new_summary)


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--run",action="store_true")
    a.add_argument("--new",type=Path,default=ROOT)
    a.add_argument("--old",type=Path,default=OLD)
    args=a.parse_args()
    if not args.run:a.error("Explicit --run required")
    run(args.new,args.old)
