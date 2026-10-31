"""Conditional ABC-RF and rejection-ABC model selection using ACTUAL simulated data.

Prior predictive = 12 structural types × 256 independently sampled synthetic
demographic rate vectors × 2 exactly integrated reversal on/off modes, each
a genuine 80-year 2×2×2 seasonal+annual demographic simulation.

A RF *vote fraction is NOT a posterior*. Pudlo et al. (2016) estimates the
selected-model posterior using a SECOND regression forest of OOB 0/1 errors.
The full discrete four-sign rejection-ABC conditional shares are separate.

The prior ranges are invented ecological sensitivity scenarios, NOT field
calibrated. Scientific claim ceiling is model compatibility under those priors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from model_native_2x2x2_prior import (
    ROOT,OUT,CONTEXTS,METRICS,TARGET,YEARS,WINDOW,DT,EPS
)

SCALES=("log","raw","marginal_scale")
N_TREES=450
SEED=20261031
SIGN_LABELS=(-1,0,1)
RF_N_CLASSES=12
PRIOR_PARAMS=("attack_scale","s_growth_multiplier","d_growth_multiplier",
              "rho","conversion","f_juvenile_survival","f_adult_survival","f_delay")
MIN_ACCEPTED_FOR_STABLE_QUANTILES=20


def load_actual_refs(folder=OUT):
    folder=Path(folder)
    frames=[];prior=None;receipts={}
    for context in CONTEXTS:
        p=folder/(context+"_prior_predictive_reference.csv.gz")
        receipt=folder/(context+"_receipt.json")
        params=folder/(context+"_parameter_draws.csv")
        reverse=folder/(context+"_reverse_edge_signature_pairs.csv")
        for name in (p,receipt,params,reverse):
            if not name.is_file():
                raise FileNotFoundError("Missing actual model-native source output "+str(name))
        j=json.loads(receipt.read_text())
        if (j["n_structural_classes"]!=4 or j["years"]!=YEARS or
            j["window"]!=WINDOW or j["dt"]!=DT or
            j["original_source_replay_max_error"]["F_B"]>1e-8 or
            j["original_source_replay_max_error"]["F_fraction"]>1e-8):
            raise AssertionError("Unreplayed original 80-year demographic source")
        r=pd.read_csv(p)
        if len(r)!=4*j["n_draws_per_structure"]*2 or r.structure_id.nunique()!=4:
            raise AssertionError("Prior predictive output not full factorial")
        if (r.groupby(["structure_id","draw"]).reverse_on.nunique()!=2).all():
            raise AssertionError("Missing exact reversal-on/off matched parameter pairs")
        q=pd.read_csv(params)
        if prior is None:prior=q
        else:pd.testing.assert_frame_equal(prior,q)
        check=pd.read_csv(reverse)
        if len(check)!=4*j["n_draws_per_structure"]:
            raise AssertionError("Incomplete reversed-edge matched sign audit")
        j["source_sha256_for_reference"]=hashlib.sha256(p.read_bytes()).hexdigest()
        frames.append(r);receipts[context]=j
    reference=pd.concat(frames,ignore_index=True)
    n=int(receipts[CONTEXTS[0]]["n_draws_per_structure"])
    if (len(reference)!=12*n*2 or reference.structure_id.nunique()!=12 or
        reference.groupby("structure_id").size().ne(n*2).any()):
        raise AssertionError("Not equal 12 class priors")
    if reference.duplicated(["structure_id","draw","reverse_on"]).any():
        raise AssertionError("Duplicate parameter/edge source")
    for scale in ("log","raw"):
        fields=[f"sign_{scale}_{p}" for p in METRICS]
        if not np.isin(reference[fields].to_numpy(int),SIGN_LABELS).all():
            raise AssertionError("Not a directional ABC source")
        observed=(reference[fields].to_numpy(int)==np.asarray(TARGET)).all(axis=1)
        if not np.array_equal(observed,reference[f"matches_{scale}"].to_numpy(bool)):
            raise AssertionError("Source ABC success count was not reproduced")
    return reference,prior,receipts


def features(ref,scale,seed=SEED):
    if scale not in SCALES:raise ValueError("Unknown response scale prior")
    if scale in ("log","raw"):
        return ref[[f"sign_{scale}_{k}" for k in METRICS]].to_numpy(dtype=np.int8)
    n=ref.draw.nunique()
    keys=[(i,j) for i in sorted(ref.draw.unique()) for j in (0,1)]
    if len(keys)!=2*n:raise AssertionError("Incomplete latent reversal pairs")
    decision=np.array([0,1]*n,int)
    rng=np.random.default_rng(seed+9)
    decision=decision[rng.permutation(len(decision))]
    map_to_scale=dict(zip(keys,decision))
    want=np.asarray([map_to_scale[(int(r.draw),int(r.reverse_on))]
                     for r in ref.itertuples(index=False)],int)
    if want.mean()!=.5:
        raise AssertionError("Unbalanced 50/50 response-scale nuisance")
    a=features(ref,"log");b=features(ref,"raw")
    return np.where(want[:,None]==0,a,b)


def wilson_ci(success,n,z=1.959963984540054):
    if n<1 or not 0<=success<=n:raise ValueError("Invalid acceptance count")
    p=success/n
    d=1+z*z/n
    center=(p+z*z/(2*n))/d
    radius=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0.,center-radius),min(1.,center+radius)


def reject_four_sign_abc(ref,params,scale,seed=SEED):
    """Exact categorical ABC posterior conditional on declared synthetic prior."""
    x=features(ref,scale,seed)
    target=np.asarray(TARGET,dtype=int)
    passed=(x==target).all(axis=1)
    d=ref[["structure_id","context","family","risk","draw","reverse_on"]].copy()
    d["accepted"]=passed
    allq=d.merge(params,on="draw",validate="many_to_one")
    rows=[];marginal=[]
    for cls,g in allq.groupby("structure_id"):
        n=len(g);k=int(g.accepted.sum())
        lo,hi=wilson_ci(k,n)
        rows.append(dict(scale=scale,structure_id=cls,context=g.context.iloc[0],
                         family=g.family.iloc[0],risk=bool(g.risk.iloc[0]),
                         n_actual_simulations=n,n_process_rate_draws=g.draw.nunique(),
                         n_accepted=k,acceptance_rate=k/n,
                         acceptance_wilson_low=lo,acceptance_wilson_high=hi,
                         reversal_on_given_match=float(g.loc[g.accepted,"reverse_on"].mean())
                          if k else np.nan))
        accepted=g[g.accepted]
        for p in PRIOR_PARAMS:
            x=accepted[p].to_numpy(float)
            priorvalues=g[p].to_numpy(float)
            marginal.append(dict(scale=scale,structure_id=cls,parameter=p,
                                 n_accepted=k,n_actual_priors=len(g),
                                 prior_median=float(np.median(priorvalues)),
                                 accepted_q10=float(np.quantile(x,.1)) if k else np.nan,
                                 accepted_median=float(np.median(x)) if k else np.nan,
                                 accepted_q90=float(np.quantile(x,.9)) if k else np.nan,
                                 n_enough_for_interpretation=bool(k>=MIN_ACCEPTED_FOR_STABLE_QUANTILES)))
    table=pd.DataFrame(rows)
    if len(table)!=RF_N_CLASSES or table.n_actual_simulations.nunique()!=1:
        raise AssertionError("Unequal class priors in model-type ABC")
    s=table.acceptance_rate.sum()
    table["conditional_abc_model_share"]=table.acceptance_rate/s if s>0 else np.nan
    table["posterior_status"]=(
        "HYPOTHETICAL_PRIOR_CONDITIONAL_DISCRETE_ABC"
        if s>0 else "TARGET_SIGN_VECTOR_ABSENT_POSTERIOR_UNDEFINED")
    return table,pd.DataFrame(marginal),allq


def rf_model_choice(ref,scale,seed=SEED):
    x=features(ref,scale,seed)
    labels=ref.structure_id.to_numpy(str)
    draws=np.asarray(ref.draw,int)
    unique=np.unique(draws)
    training_ids,held_ids=train_test_split(unique,test_size=.2,random_state=seed+10,
                                           shuffle=True)
    train=np.isin(draws,training_ids)
    hold=np.isin(draws,held_ids)
    if not train.any() or not hold.any() or np.any(train&hold):
        raise AssertionError("Paired reverse models leaked process-rate draw")
    if len(set(labels[train]))!=RF_N_CLASSES or len(set(labels[hold]))!=RF_N_CLASSES:
        raise AssertionError("Did not preserve every structural class")
    clf=RandomForestClassifier(
        n_estimators=N_TREES,min_samples_leaf=4,max_features=2,
        bootstrap=True,oob_score=True,n_jobs=1,
        random_state=seed+11)
    clf.fit(x[train],labels[train])
    valid=np.isfinite(clf.oob_decision_function_).all(axis=1)
    if valid.sum()!=train.sum():
        raise ValueError("Some reference rows lack OOB probability")
    oob_pred=clf.classes_[np.argmax(clf.oob_decision_function_,axis=1)]
    oob_error=(oob_pred!=labels[train]).astype(float)
    forest=RandomForestRegressor(
        n_estimators=N_TREES,min_samples_leaf=5,max_features=2,
        bootstrap=True,oob_score=True,n_jobs=1,
        random_state=seed+12)
    # Pudlo et al. stage 2: regression of first-stage *OOB* misclassification.
    forest.fit(x[train],oob_error)
    selected=str(clf.predict(np.asarray(TARGET).reshape(1,-1))[0])
    conditional_selected=float(np.clip(
        1-forest.predict(np.asarray(TARGET).reshape(1,-1))[0],0,1))
    vote=float(clf.predict_proba(np.asarray(TARGET).reshape(1,-1))[0,
         np.flatnonzero(clf.classes_==selected)[0]])
    holdpred=clf.predict(x[hold])
    holdacc=float(np.mean(holdpred==labels[hold]))
    classes=np.sort(np.unique(labels))
    confusion=confusion_matrix(labels[hold],holdpred,labels=classes)
    rows=[]
    for i,cls in enumerate(classes):
        for j,called in enumerate(classes):
            rows.append(dict(scale=scale,true_structure=cls,predicted_structure=called,
                             n=int(confusion[i,j]),
                             source_count=int(np.sum(labels[hold]==cls)),
                             fraction=float(confusion[i,j]/np.sum(labels[hold]==cls))))
    matches=(x==np.asarray(TARGET)).all(axis=1)
    diag=dict(scale=scale,chosen_structure=selected,
              conditional_rf_selected_class_support=conditional_selected,
              rf_class_vote_fraction_not_posterior=vote,
              prior_oob_error=float(oob_error.mean()),
              prior_oob_accuracy=float(1-oob_error.mean()),
              holdout_model_accuracy=holdacc,
              baseline_equal_prior_guess_accuracy=1/RF_N_CLASSES,
              training_unique_sign_patterns=len(np.unique(x[train],axis=0)),
              n_process_draws_train=len(training_ids),
              n_process_draws_holdout=len(held_ids),
              n_reference_train=int(train.sum()),n_reference_holdout=int(hold.sum()),
              reference_exact_target_sign_rows=int(matches.sum()),
              selected_structure_target_sign_rows=int(
                  np.sum(matches&(labels==selected))),
              rf_error_regression_oob_r2=float(forest.oob_score_),
              decision="CONDITIONAL_RF_CLASSIFICATION_NOT_EMPIRICALLY_CALIBRATED_POSTERIOR")
    importances=pd.DataFrame(dict(scale=scale,pattern=list(METRICS),
                                  classification_importance=clf.feature_importances_,
                                  conditional_error_importance=forest.feature_importances_))
    return diag,pd.DataFrame(rows),importances


def sign_fingerprint_equivalence(reference):
    """Classes indistinguishable at the sign level over shared prior draws."""
    classes=sorted(reference.structure_id.unique())
    rows=[]
    for scale in ("log","raw"):
        signatures={}
        for structure in classes:
            g=reference[reference.structure_id==structure].sort_values(["draw","reverse_on"])
            signature=tuple(map(tuple,features(g,scale).tolist()))
            signatures[structure]=signature
        grouping={}
        for model,signature in signatures.items():
            grouping.setdefault(signature,[]).append(model)
        for members in grouping.values():
            rows.append(dict(scale=scale,n_structures=len(members),
                             representative_structure=min(members),
                             structures=";".join(sorted(members)),
                             prior_matched_direction_vectors_exactly_identical=True))
    return pd.DataFrame(rows)


def run(folder=OUT,seed=SEED):
    folder=Path(folder)
    reference,prior,source_receipts=load_actual_refs(folder)
    acceptance=[];posterior_parameters=[];rf=[];confusions=[];importances=[]
    for scale in SCALES:
        x,param,m=reject_four_sign_abc(reference,prior,scale,seed=seed)
        diag,conf,imp=rf_model_choice(reference,scale,seed=seed)
        acceptance.append(x);posterior_parameters.append(param)
        rf.append(diag);confusions.append(conf);importances.append(imp)
        print("GENUINE_SIGN_ABC",scale,
              "compatible_classes",int((x.n_accepted>0).sum()),
              "accepted_samples",int(x.n_accepted.sum()),
              "class_with_highest_acceptance",
              str(x.sort_values(["acceptance_rate","structure_id"],
                                ascending=[False,True]).iloc[0].structure_id),
              "RF_OOB_prior_error",diag["prior_oob_error"],
              "RF_holdout_accuracy",diag["holdout_model_accuracy"],
              "RF_selected_structure",diag["chosen_structure"],
              "selected_conditional_RF_probability",diag["conditional_rf_selected_class_support"],
              flush=True)
    tbl=dict(abc_rejection_model_acceptance=pd.concat(acceptance,ignore_index=True),
             posterior_parameter_ranges=pd.concat(posterior_parameters,ignore_index=True),
             abc_rf_model_choice=pd.DataFrame(rf),
             abc_rf_holdout_confusion=pd.concat(confusions,ignore_index=True),
             abc_rf_feature_importance=pd.concat(importances,ignore_index=True),
             sign_fingerprint_equivalence=sign_fingerprint_equivalence(reference))
    for name,data in tbl.items():
        data.to_csv(folder/(name+".csv"),index=False)
    receipt=dict(status="MODEL_NATIVE_80_YEAR_TRUE_SIMULATION_ABC_RF_WITH_HYPOTHETICAL_PRIORS",
                 structure_classes=RF_N_CLASSES,actual_model_simulations=len(reference),
                 rate_draws_per_class=reference.draw.nunique(),reversal_prior="paired equal 0.5",
                 target=dict(zip(METRICS,TARGET)),
                 scales=list(SCALES),source_hashes={
                      context:source_receipts[context]["source_sha256"]
                      for context in CONTEXTS},
                 scientific_limits=[
                     "Model probabilities conditional on synthetic, not empirical, rate priors",
                     "Four sign features have <=16 nonzero combinations; zero signs add states",
                     "RF classification vote is not a class posterior",
                     "RF selected-model conditional support is second-stage OOB-error regression approximation",
                     "No independent ecological field verification, acoustic detection process, or observation-scale fit",
                     "Model identifiability must be evaluated from confusion/prior OOB error",
                     "Rate-dependent reversal ON/OFF tested explicitly at every draw",
                     "Uncalibrated exact sign contrast and no 4,248-site predictor transport"],
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (folder/"abc_rf_receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("ABC_ACCEPTANCE\n"+tbl["abc_rejection_model_acceptance"].to_string(index=False))
    print("ABC_RF_PRIOR_ERROR_AND_SELECTED\n"+tbl["abc_rf_model_choice"].to_string(index=False))
    print("INDISTINGUISHABLE_DIRECTIONAL_GROUPS\n"+
          tbl["sign_fingerprint_equivalence"].to_string(index=False))
    return tbl


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",action="store_true")
    ap.add_argument("--folder",type=Path,default=OUT)
    a=ap.parse_args()
    if not a.run:ap.error("Explicit --run required")
    run(folder=a.folder)
