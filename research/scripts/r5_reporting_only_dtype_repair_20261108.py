"""R5 reporting-only categorical-ID repair and complete source-linked QA.

Reads the successful 24x100x2 source artefact from Github Actions run 42446291543.
The original source simulations are NOT re-executed or cherry-picked.
Problem repaired: pandas read_csv parsed literal categorical arm "00" as integer 0,
making the original JSON primary true-ON matching-background subgroup empty.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_RUN=42446291543
N_REPLICATE_OBSERVERS=4800
SCENARIOS=24
EXPECTED_CELLS=48
REPS=100

def check(v, why):
    if not bool(v):raise AssertionError(why)

def wilson(k,n,z=1.96):
    p=k/n; den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    err=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return mid-err,mid+err

def normarm(s):
    return s.astype(str).str.zfill(2)

def run(root:Path,out:Path):
    orig={
        "full":root/"R5_all_4800_original_fold_observer_results.csv",
        "table":root/"R5_complete_48_world_observer_recovery_summary.csv",
        "oracle":root/"R5_expected_call_oracle_48_rows.csv",
        "receipt":root/"R5_FULL_FIXED_PROSPECTIVE_SOURCE_AUDIT.json",
    }
    check(all(p.is_file() for p in orig.values()),"Original source audited artefact incomplete")
    oldsha={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in orig.items()}
    r=json.loads(orig["receipt"].read_text())
    check(r["status"]=="R5_FULL_24_SCENARIOS_COMPLETE" and r["n_scenarios"]==SCENARIOS
          and r["n_simulated_field_outcomes"]==SCENARIOS*REPS
          and r["n_original_field_sites"]==4248 and r["n_original_completed_visits"]==63180
          and r["n_original_geographic_blocks"]==56
          and r["all_replicates_reported_including_failures"],
          "Original all-source fail-closed gates missing")
    full=pd.read_csv(orig["full"],dtype={"true_source_arm":str})
    tbl=pd.read_csv(orig["table"],dtype={"true_source_arm":str})
    oracle=pd.read_csv(orig["oracle"],dtype={"true_source_arm":str})
    for df in [full,tbl,oracle]:
        df["true_source_arm"]=normarm(df.true_source_arm)
        check(set(df.true_source_arm)=={"00","11"},"Literal ON/OFF IDs altered")
    check(len(full)==N_REPLICATE_OBSERVERS and len(tbl)==EXPECTED_CELLS
          and len(oracle)==EXPECTED_CELLS,"Result table incompleteness")
    keys=["true_background","true_source_arm","gamma","pond_V_flip","observer_background"]
    check(tbl[keys].drop_duplicates().shape[0]==EXPECTED_CELLS,
          "Source 48 analysis cells not unique")
    check(full.groupby(keys).size().eq(REPS).all(),
          "Each true-case/observer comparison needs exactly 100 replicates")
    check(full[["source11_gain_over_flexadd","source11_gain_over_source00",
                "source11_gain_over_flexall"]].notna().all().all(),
          "Nonfinite source original CV results")
    # Recheck the fixed binary rule directly from the saved original 56-block CIs.
    decision=(full.source11_gain_over_flexadd_low>0)&(full.source11_gain_over_source00_low>0)
    check(np.array_equal(decision.to_numpy(bool),full.source11_recovered.to_numpy(bool)),
          "Primary recovery decision not reproducible from saved original CIs")
    fromrep=full.groupby(keys).source11_recovered.agg(["mean","size"]).reset_index()
    match=tbl.merge(fromrep,on=keys,validate="one_to_one")
    check(np.max(np.abs(match.source11_recovery-match["mean"]))<1e-12
          and match["size"].eq(REPS).all(),
          "Original 48-cell recovery table not reproduced by 4,800 source rows")

    primary=tbl[(tbl.true_source_arm=="11")&
                (tbl.true_background==tbl.observer_background)]
    check(len(primary)==12 and primary.groupby(["true_background","gamma"]).size().eq(2).all(),
          "Fixed true-ON, same-background primary table missing/incorrect")
    negative=full[full.gamma==0]
    n0=int(negative.source11_recovered.sum());N0=len(negative)
    check(N0==1600,"All zero-signal control conditions absent")
    fp=wilson(n0,N0)
    off=full[(full.true_source_arm=="00")&(full.gamma>0)]
    check(len(off)==1600,"All OFF-truth alternatives absent")
    wrong=int(off.source11_recovered.sum())
    differences=[]
    for truth in ["uniform","target_group"]:
        wrong_bg=next(bg for bg in ["uniform","target_group"] if bg!=truth)
        for gamma in [0.25,1.0]:
            select=tbl[(tbl.true_source_arm=="11")&(tbl.true_background==truth)&
                       (tbl.gamma==gamma)]
            def take(bg,flip):
                a=select[(select.observer_background==bg)&(select.pond_V_flip==flip)]
                check(len(a)==1,"Missing fixed observability contrast")
                return a.iloc[0]
            aligned=take(truth,0.0);v_only=take(truth,.25)
            rank_only=take(wrong_bg,0.0);both=take(wrong_bg,.25)
            # Conservative bounds from Wilson intervals across independently
            # generated condition replicates; these are sensitivity intervals.
            diff=float(aligned.source11_recovery-both.source11_recovery)
            lower=float(aligned.source11_recovery_Wilson95_low-
                        both.source11_recovery_Wilson95_high)
            upper=float(aligned.source11_recovery_Wilson95_high-
                        both.source11_recovery_Wilson95_low)
            differences.append(dict(
                true_background=truth,gamma=gamma,replications_per_condition=REPS,
                aligned_power=float(aligned.source11_recovery),
                V_error_only_power=float(v_only.source11_recovery),
                rank_error_only_power=float(rank_only.source11_recovery),
                combined_rank_and_V_error_power=float(both.source11_recovery),
                combined_minus_aligned_power=float(-diff),
                aligned_minus_combined_power=diff,
                conservative_Wilson_components_95low=lower,
                conservative_Wilson_components_95high=upper,
                observational_gamma_empirically_calibrated=False,
                V_mismatch_25pct_empirically_calibrated=False,
            ))
    comp=pd.DataFrame(differences)
    out.mkdir(parents=True,exist_ok=True)
    full.to_csv(out/"R5_all_4800_original_holdout_results_ARM_IDS_FIXED.csv",index=False)
    tbl.to_csv(out/"R5_all_48_conditional_recovery_cells_ARM_IDS_FIXED.csv",index=False)
    oracle.to_csv(out/"R5_all_48_oracle_scores_ARM_IDS_FIXED.csv",index=False)
    comp.to_csv(out/"R5_frozen_proxy_mismatch_detection_power_contrasts.csv",index=False)
    result={
        "status":"R5_REPORTING_ONLY_LABEL_REPAIR_QA_PASS",
        "source_run_id":SOURCE_RUN,
        "original_result_sha256":oldsha,
        "original_R5_source_simulations_recomputed":False,
        "original_source_model_refit":False,
        "repair":"Preserve two-character categorical arm IDs 00/11 while reading CSV; recreate the 12-row ON/matched observer subgroup from 48 verified result cells.",
        "all_24_scenarios_verified":True,
        "all_2400_simulations_verified":True,
        "all_4800_observer_predictions_verified":True,
        "n_original_sites":4248,
        "n_original_site_surveys":63180,
        "n_spatial_blocks":56,
        "n_main_true_on_matching_cells":len(primary),
        "negative_control_gamma_zero_false_11_calls":n0,
        "negative_control_gamma_zero_total_observer_trials":N0,
        "negative_control_false_11_rate":n0/N0,
        "negative_control_false_11_Wilson95":list(map(float,fp)),
        "off_truth_nonzero_gamma_wrong_11_recoveries":wrong,
        "off_truth_nonzero_gamma_trials":len(off),
        "false_positive_nominal5pct_calibrated":fp[0]<=.05<=fp[1],
        "true_on_matching_background":primary.to_dict("records"),
        "proxy_comparison_all_not_selected":comp.to_dict("records"),
        "causal_reasons_for_actual_G14_failure_identified":False,
        "actual_natural_trophic_model_identified":False,
    }
    (out/"R5_VERIFIED_REPORTING_ONLY_CORRECTED_AUDIT.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("R5_REPORTING_ONLY_LABEL_REPAIR_QA_PASS",
          "24x100 source simulations verified, 4800 heldout comparisons",
          "original runs NOT repeated, false positive controls",n0,"/",N0,flush=True)
    print("R5_ALL_FIXED_MODEL_POWER_CONTRASTS\n"+comp.to_string(index=False),flush=True)
    return result

if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--source",type=Path,required=True)
    pa.add_argument("--out",type=Path,required=True)
    a=pa.parse_args()
    run(a.source,a.out)
