"""Audit and summarize completed R²-calibrated directional POM source families.

This only aggregates fixed GHA output. It does not select noise scales or
candidate scenarios by inspecting empirical direction patterns.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from r2_calibrated_directional_pom import FAMILIES,NOISE_TYPES,MODES,BACKGROUNDS

N_CALIBRATED=("MATCHED_R2","MATCHED_WITHOUT_NOISE")


def combine(folder):
    root=Path(folder)
    frame=[];orig=[];receipts=[]
    for family in FAMILIES:
        for noise in NOISE_TYPES:
            stem=f"{family}_{noise}"
            p=root/(stem+"_source_group_scores.csv")
            observed=root/(stem+"_observed_r2_and_patterns.csv")
            receipt=root/(stem+"_receipt.json")
            if not all(z.is_file() for z in (p,observed,receipt)):
                raise FileNotFoundError("Missing completed input group "+stem)
            s=pd.read_csv(p)
            o=pd.read_csv(observed)
            rc=json.loads(receipt.read_text())
            expect={"frozen132":132,"realrate192":192,"facilitation72":72}[family]
            if rc["n_candidate_labels"]!=expect or len(o)!=10:
                raise AssertionError("Bad evidence family metadata "+stem)
            if len(s)!=len(BACKGROUNDS)*len(MODES)*rc["n_distinct_source_groups"]:
                raise AssertionError("Incomplete group scores "+stem)
            if s.duplicated(["background","mode","source_group"]).any():
                raise AssertionError("Double-counted mechanism source")
            if not s.eval_reps.eq(rc["n_independent_evaluation_noise_fields"]).all():
                raise AssertionError("Wrong noise ensemble sample size")
            if not s["soft_joint_agreement"].between(0,1).all():
                raise AssertionError("Invalid categorical scores")
            for (bg,mode),g in s.groupby(["background","mode"]):
                if not np.allclose(g.r2_target,g.r2_target.iloc[0]):
                    raise AssertionError("Noise targets differ across mechanisms")
            frame.append(s)
            orig.append(o)
            receipts.append(dict(family=family,noise_type=noise,
                                 n_exact_source_groups=rc["n_distinct_source_groups"],
                                 n_case_labels=rc["n_candidate_labels"],
                                 n_eval_reps=rc["n_independent_evaluation_noise_fields"]))
    scores=pd.concat(frame,ignore_index=True)
    obs=pd.concat(orig,ignore_index=True)
    unique=obs.drop_duplicates(["background","pattern"])[
        ["background","pattern","observed_value","r2_observed","lowS_zero_band","selected"]]
    for bg in BACKGROUNDS:
        x=unique[unique.background==bg]
        if len(x)!=5 or x.r2_observed.nunique()!=1:
            raise AssertionError("Cross-family observed regression R² mismatch")
    overview=[];chosen=[]
    for (family,noise,bg,mode),g in scores.groupby(
            ["family","noise_type","background","mode"],sort=True):
        matching=g[g.calibration_status.isin(N_CALIBRATED)].copy()
        nonmatch=g[~g.calibration_status.isin(N_CALIBRATED)].copy()
        if len(matching)+len(nonmatch)!=len(g):
            raise AssertionError("Missing R² status")
        sort=matching.sort_values(
            ["soft_joint_agreement","source_group"],ascending=[False,True])
        best=sort.iloc[0] if len(sort) else None
        complete=matching[matching.modal_complete_count>0]
        # A zero in 128 draws is a numerical sample absence, not proof that
        # the compatibility probability is exactly zero.
        overview.append(dict(
            family=family,noise_type=noise,background=bg,mode=mode,
            observed_r2=float(g.r2_target.iloc[0]),
            n_source_groups=len(g),n_r2_matched_groups=len(matching),
            n_r2_unreachable_groups=int((g.calibration_status=="NOISE_ONLY_R2_UNREACHABLE").sum()),
            n_r2_not_bracketed=int((g.calibration_status=="NOISE_R2_NOT_BRACKETED").sum()),
            n_r2_unconverged=int((g.calibration_status=="APPROXIMATE_R2_UNMATCHED").sum()),
            max_r2_calibration_error=float(matching.r2_abs_error.max()) if len(matching) else np.nan,
            median_eval_r2_abs_error=float(abs(matching.r2_evaluation_mean-matching.r2_target).median())
                if len(matching) else np.nan,
            n_groups_with_any_joint_complete=int(len(complete)),
            n_groups_lowS_nearzero_majority=int((matching.q_lowS_near_zero>=.5).sum()),
            n_groups_joint_complete_and_lowS_majority=int(
                ((matching.modal_complete_count>0)&(matching.q_lowS_near_zero>=.5)).sum()),
            best_matched_group=best.source_group if best is not None else "NONE",
            best_matched_joint_score=float(best.soft_joint_agreement) if best is not None else np.nan,
            best_matched_complete_frequency=float(best.modal_complete_frequency)
                if best is not None else np.nan,
            best_matched_lowS_nearzero_frequency=float(best.q_lowS_near_zero)
                if best is not None else np.nan))
        if best is not None:
            for row in sort.head(5).itertuples(index=False):
                chosen.append(dict(
                    family=family,noise_type=noise,background=bg,mode=mode,
                    source_group=row.source_group,
                    soft_joint_agreement=row.soft_joint_agreement,
                    modal_complete_count=row.modal_complete_count,
                    modal_complete_frequency=row.modal_complete_frequency,
                    q_lowS_near_zero=row.q_lowS_near_zero,
                    r2_target=row.r2_target,r2_evaluation_mean=row.r2_evaluation_mean,
                    relative_sigma=row.relative_sigma,
                    calibration_status=row.calibration_status))
    overview=pd.DataFrame(overview).sort_values(
        ["family","noise_type","background","mode"]).reset_index(drop=True)
    crossing=[]
    for family in FAMILIES:
        for noise in NOISE_TYPES:
            for mode in MODES:
                group=scores[(scores.family==family)&(scores.noise_type==noise)&
                             (scores.mode==mode)&
                             (scores.calibration_status.isin(N_CALIBRATED))]
                passes=group[group.modal_complete_count>0]
                v=passes.groupby("source_group").background.nunique()
                both=v[v==2].index
                crossing.append(dict(family=family,noise_type=noise,mode=mode,
                                     n_both_backgrounds_with_joint_simulated_match=len(both),
                                     groups=";".join(sorted(both))))
    return dict(all_source_group_scores=scores,source_family_summary=overview,
                top5_eligible_source_groups=pd.DataFrame(chosen),
                cross_background_directional_matches=pd.DataFrame(crossing),
                unique_observed_r2_and_patterns=unique,
                source_family_receipt=pd.DataFrame(receipts))


def run(folder):
    p=Path(folder)
    tables=combine(p)
    for name,data in tables.items():
        data.to_csv(p/(name+".csv"),index=False)
    print("ACOUSTIC_R2_CALIBRATED_OVERVIEW\n"+
          tables["source_family_summary"].to_string(index=False),flush=True)
    print("CROSS_BACKGROUND_JOINT_REPRODUCTION\n"+
          tables["cross_background_directional_matches"].to_string(index=False),flush=True)
    print("OBSERVED_R2\n"+
          tables["unique_observed_r2_and_patterns"].to_string(index=False),flush=True)
    return tables


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--directory",type=Path,default=
                   Path("research/results/macro_r2_matched_directional_20261031"))
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.directory)
