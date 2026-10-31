"""Paired matched-R² POM: actual S-facilitated danger versus its exact baseline.

No new noise fitting, model running, or candidate selection. Consumes the six
completed source-backed artifacts from the 2026-10-31 R² matched POM workflow.
The 24 structural cases are paired separately within each noise/background/
signal mode; only the hypothesis strength differs. Differences are descriptive
under a post-hoc observation model, not biologically calibrated posterior odds.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from r2_calibrated_directional_pom import FAMILIES,NOISE_TYPES,MODES,BACKGROUNDS

OUT=Path("research/results/macro_r2_matched_directional_20261031")
LEVELS=("neutral","moderate","strong")
POSITIVE_TOL=1e-12
ROBUST_FREQUENCY=.10  # descriptive >=13 of 128 independent noise draws


def read_all(root):
    s=[];c=[]
    for fam in FAMILIES:
        for noise in NOISE_TYPES:
            stem=f"{fam}_{noise}"
            a=pd.read_csv(root/(stem+"_source_group_scores.csv"))
            if a.duplicated(["background","mode","source_group"]).any():
                raise AssertionError("Source group repeated")
            s.append(a)
            if fam=="facilitation72":
                b=pd.read_csv(root/(stem+"_candidate_scores.csv"))
                if len(b)!=72*2*2:
                    raise ValueError("Wrong hypothesis×case count")
                if b.duplicated(["background","mode","hypothesis","case"]).any():
                    raise ValueError("Repeated matched hypothetical case")
                c.append(b)
    return pd.concat(s,ignore_index=True),pd.concat(c,ignore_index=True)


def paired_facilitation(candidate):
    cols=("background","mode","case")
    rows=[]
    for noise in NOISE_TYPES:
        frame=candidate[candidate.noise_type==noise]
        for key,group in frame.groupby(list(cols)):
            if set(group.hypothesis)!=set(LEVELS) or len(group)!=3:
                raise AssertionError("Unbalanced baseline / experimental hypothesis")
            base=group[group.hypothesis=="neutral"].iloc[0]
            for level in ("moderate","strong"):
                arm=group[group.hypothesis==level].iloc[0]
                if (arm.calibration_status not in ("MATCHED_R2","MATCHED_WITHOUT_NOISE")
                    or base.calibration_status not in ("MATCHED_R2","MATCHED_WITHOUT_NOISE")):
                    # No credible claim for an arm whose R² could not be matched.
                    status="NOT_BOTH_R2_MATCHED"
                else:
                    status="BOTH_R2_MATCHED"
                rows.append(dict(noise_type=noise,background=key[0],mode=key[1],
                                 case=key[2],hypothesis=level,
                                 status=status,
                                 neutral_soft=float(base.soft_joint_agreement),
                                 tested_soft=float(arm.soft_joint_agreement),
                                 gain_joint_soft=float(arm.soft_joint_agreement-
                                                       base.soft_joint_agreement),
                                 neutral_modal_complete=float(base.modal_complete_frequency),
                                 tested_modal_complete=float(arm.modal_complete_frequency),
                                 gain_modal_complete=float(arm.modal_complete_frequency-
                                                           base.modal_complete_frequency),
                                 neutral_q_lowS_zero=float(base.q_lowS_near_zero),
                                 tested_q_lowS_zero=float(arm.q_lowS_near_zero),
                                 gain_q_lowS_zero=float(arm.q_lowS_near_zero-
                                                       base.q_lowS_near_zero),
                                 neutral_r2=float(base.r2_evaluation_mean),
                                 tested_r2=float(arm.r2_evaluation_mean)))
    table=pd.DataFrame(rows)
    if len(table)!=2*2*2*24*2:
        raise ValueError("Wrong number of paired hypothesis cases")
    summary=[]
    for key,g in table.groupby(["noise_type","background","mode","hypothesis"]):
        gain=g.gain_joint_soft.to_numpy(float)
        summary.append(dict(noise_type=key[0],background=key[1],
                            mode=key[2],hypothesis=key[3],n_cases=len(g),
                            positive_gain_cases=int(np.sum(gain>POSITIVE_TOL)),
                            negative_gain_cases=int(np.sum(gain<-POSITIVE_TOL)),
                            equal_gain_cases=int(np.sum(np.abs(gain)<=POSITIVE_TOL)),
                            mean_joint_gain=float(np.mean(gain)),
                            median_joint_gain=float(np.median(gain)),
                            maximum_joint_gain=float(gain.max()),
                            minimum_joint_gain=float(gain.min()),
                            n_positive_modal_gain=int((g.gain_modal_complete>POSITIVE_TOL).sum())))
    stable=[]
    for (case,level),g in table.groupby(["case","hypothesis"]):
        gain=g.gain_joint_soft.to_numpy()
        if len(g)!=8:raise AssertionError("Incomplete 8-way sensitivity")
        stable.append(dict(case=case,hypothesis=level,
                           n_noise_background_mode_conditions=len(g),
                           n_positive_joint_gain=int(np.sum(gain>POSITIVE_TOL)),
                           n_negative_joint_gain=int(np.sum(gain<-POSITIVE_TOL)),
                           min_joint_gain=float(gain.min()),
                           mean_joint_gain=float(gain.mean()),
                           all_eight_strictly_positive=bool(np.all(gain>POSITIVE_TOL)),
                           all_eight_nonnegative=bool(np.all(gain>=-POSITIVE_TOL))))
    return table,pd.DataFrame(summary),pd.DataFrame(stable)


def eight_condition_stability(groups):
    records=[]
    leaders=[]
    for family,g in groups.groupby("family"):
        expected={"frozen132":104,"realrate192":128,"facilitation72":48}[family]
        unique=g.source_group.nunique()
        if unique!=expected or len(g)!=expected*8:
            raise AssertionError("Missing scenarios or noise modes")
        for label,q in g.groupby("source_group"):
            if len(q)!=8 or q.duplicated(["noise_type","background","mode"]).any():
                raise AssertionError("Missing a background/noise/mode condition")
            allowed=q.calibration_status.isin(["MATCHED_R2","MATCHED_WITHOUT_NOISE"])
            complete=q.modal_complete_count.to_numpy()
            entry=dict(family=family,source_group=label,
                       n_conditions=8,n_r2_matched_conditions=int(allowed.sum()),
                       n_conditions_with_any_complete=int((complete>0).sum()),
                       n_conditions_with_at_least_10pct_complete=int(
                           (q.modal_complete_frequency>=ROBUST_FREQUENCY).sum()),
                       minimum_complete_frequency=float(q.modal_complete_frequency.min()),
                       mean_complete_frequency=float(q.modal_complete_frequency.mean()),
                       minimum_soft=float(q.soft_joint_agreement.min()),
                       mean_soft=float(q.soft_joint_agreement.mean()),
                       q_lowS_zero_min=float(q.q_lowS_near_zero.min()),
                       all_eight_nonzero=bool(np.all(complete>0)),
                       all_eight_ge_10pct=bool(
                           np.all(q.modal_complete_frequency>=ROBUST_FREQUENCY)))
            records.append(entry)
    t=pd.DataFrame(records)
    summary=[]
    for fam,sub in t.groupby("family"):
        top=sub.sort_values(["minimum_soft","source_group"],
                            ascending=[False,True]).iloc[0]
        summary.append(dict(family=fam,n_source_groups=len(sub),
                            n_all_8_with_any_complete=int(sub.all_eight_nonzero.sum()),
                            n_all_8_at_least_10pct=int(sub.all_eight_ge_10pct.sum()),
                            top_worst_case_group=top.source_group,
                            top_worst_case_soft=float(top.minimum_soft),
                            top_worst_case_complete=float(top.minimum_complete_frequency)))
    return t,pd.DataFrame(summary)


def run(path=OUT):
    root=Path(path)
    source,candidate=read_all(root)
    paired,summary,stable=paired_facilitation(candidate)
    eight,coverage=eight_condition_stability(source)
    result=dict(paired_hypothesis_case_differences=paired,
                amplification_paired_summary=summary,
                amplification_eight_condition_stability=stable,
                all_group_eight_condition_stability=eight,
                family_eight_condition_coverage=coverage)
    for name,frame in result.items():
        frame.to_csv(root/(name+".csv"),index=False)
    print("AMPLIFICATION_PAIRED_GAIN\n"+summary.to_string(index=False),flush=True)
    print("AMPLIFICATION_STABILITY\n"+stable.to_string(index=False),flush=True)
    print("FAMILY_ALL_EIGHT_CONDITION_STABILITY\n"+coverage.to_string(index=False),flush=True)
    print("TOP_WORST_CASE_LEADS\n"+
          eight.sort_values(["family","minimum_soft"],
                            ascending=[True,False]).groupby("family").head(5).to_string(index=False),
          flush=True)
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",action="store_true")
    ap.add_argument("--directory",type=Path,default=OUT)
    args=ap.parse_args()
    if not args.run:ap.error("Explicit --run required")
    run(args.directory)
