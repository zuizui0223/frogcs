"""ABC-RF *actual* 20% held-out 80-year parameter draws: which structural axes can be recovered?

12-label RF classification OOF/holdout accuracy can be low while coarse stage
timing, food handling, or refuge state has stronger or weaker recoverability.
This takes existing RF confusion from the genuinely executed 256 draw/structure
reference and *does not retrain or retune a classifier*. The chance baselines
of 1/3 timing, 1/2 food handling and 1/2 risk reflect equal synthetic class
priors, not an ecological null or p-value.  Never call RF vote a posterior.
"""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

from model_native_abc_rf import OUT,SCALES

AXES=("context","family","risk")
TARGET_COUNTS={"context":3,"family":2,"risk":2}
EXPECTED_CLASSES=12
EXPECTED_HELD=624


def decompose_class(label):
    x=str(label).split("__")
    if len(x)!=3 or x[2] not in ("risk0","risk1"):
        raise ValueError("Unexpected case label "+str(label))
    return dict(context=x[0],family=x[1],risk=x[2])


def summarize_classifier_errors(confusion):
    mandatory={"scale","true_structure","predicted_structure","n","source_count","fraction"}
    if not mandatory.issubset(confusion):
        raise ValueError("Incomplete genuine RF confusion columns")
    records=[];matrices=[]
    for scale,g in confusion.groupby("scale",sort=False):
        if g.true_structure.nunique()!=EXPECTED_CLASSES:
            raise ValueError("Missing 12 structural models")
        if len(g)!=EXPECTED_CLASSES**2 or len(g)!=len(g.drop_duplicates(
                ["true_structure","predicted_structure"])):
            raise ValueError("Incomplete true×predicted 12-class matrix")
        if int(g.n.sum())!=EXPECTED_HELD:
            raise ValueError("Expected 20% independent held prior draws per structure")
        for name,part in g.groupby("true_structure"):
            if part.source_count.nunique()!=1:
                raise AssertionError("Contradictory true-model sample denominator")
            if int(part.n.sum())!=int(part.source_count.iloc[0]):
                raise AssertionError("RF confusion lost sources")
        df=g.copy()
        df=df.join(df.true_structure.map(decompose_class).apply(pd.Series).add_prefix("true_"))
        df=df.join(df.predicted_structure.map(decompose_class).apply(pd.Series).add_prefix("pred_"))
        group_total=int(df.n.sum())
        for axis in AXES:
            keys=["true_"+axis,"pred_"+axis]
            co=df.groupby(keys).n.sum().reset_index()
            axes_truth=sorted(df["true_"+axis].unique())
            axes_pred=sorted(df["pred_"+axis].unique())
            if len(axes_truth)!=TARGET_COUNTS[axis] or len(axes_pred)!=TARGET_COUNTS[axis]:
                raise ValueError("Missing structural axis "+axis)
            for row in co.itertuples(index=False):
                matrices.append(dict(scale=scale,axis=axis,
                                     true_state=getattr(row,"true_"+axis),
                                     predicted_state=getattr(row,"pred_"+axis),
                                     count=int(row.n)))
            correct=int(df.loc[df["true_"+axis]==df["pred_"+axis],"n"].sum())
            acc=correct/group_total
            ref=1/TARGET_COUNTS[axis]
            records.append(dict(scale=scale,axis=axis,
                n_heldout=int(group_total),
                n_correct=correct,
                heldout_accuracy=float(acc),
                equal_prior_chance_reference=ref,
                accuracy_minus_chance=float(acc-ref),
                chance_adjusted_accuracy=float((acc-ref)/(1-ref)),
                n_true_states=TARGET_COUNTS[axis],
                n_predicted_states=TARGET_COUNTS[axis],
                status="SYNTHETIC_MODEL_CLASSIFICATION_NOT_OBSERVED_ECOLOGICAL_RECOVERY"))
        fullcorrect=int(df.loc[df.true_structure==df.predicted_structure,"n"].sum())
        records.append(dict(scale=scale,axis="full_12_classes",n_heldout=group_total,
                            n_correct=fullcorrect,
                            heldout_accuracy=float(fullcorrect/group_total),
                            equal_prior_chance_reference=1/EXPECTED_CLASSES,
                            accuracy_minus_chance=float(fullcorrect/group_total-1/EXPECTED_CLASSES),
                            chance_adjusted_accuracy=float(
                                (fullcorrect/group_total-1/EXPECTED_CLASSES)/(1-1/EXPECTED_CLASSES)),
                            n_true_states=EXPECTED_CLASSES,
                            n_predicted_states=EXPECTED_CLASSES,
                            status="SYNTHETIC_MODEL_CLASSIFICATION_NOT_OBSERVED_ECOLOGICAL_RECOVERY"))
    result=pd.DataFrame(records)
    matrix=pd.DataFrame(matrices)
    if len(result)!=4*len(SCALES):
        raise AssertionError("Wrong axis count")
    return result,matrix


def posterior_uncertainty(abc):
    if not {"scale","structure_id","conditional_abc_model_share","n_accepted"}.issubset(abc):
        raise ValueError("No reproducible ABC class posterior summaries")
    rows=[]
    for scale,g in abc.groupby("scale"):
        p=g.conditional_abc_model_share.to_numpy(float)
        if len(p)!=EXPECTED_CLASSES or not np.isclose(p.sum(),1,atol=1e-9):
            raise AssertionError("ABC source classes do not normalize")
        if (p<0).any() or not np.isfinite(p).all():
            raise ValueError("Invalid ABC class weights")
        H=float(-(p[p>0]*np.log(p[p>0])).sum())
        p2=float(np.sort(p)[-2:].sum())
        modes=g.sort_values(["conditional_abc_model_share","structure_id"],
                            ascending=[False,True]).head(2)
        rows.append(dict(scale=scale, n_classes=EXPECTED_CLASSES,
                         n_distinct_structures_with_positive_support=int((p>0).sum()),
                         conditional_entropy_nats=H,
                         conditional_effective_number_of_models=float(np.exp(H)),
                         top_two_class_share=p2,
                         top_class=str(modes.iloc[0].structure_id),
                         second_class=str(modes.iloc[1].structure_id),
                         unidentifiable_field_causality=True,
                         status="CONDITIONAL_ABC_PRIOR_DEPENDENT_NOT_REAL_FIELD_MODEL_PROBABILITY"))
    return pd.DataFrame(rows)


def run(directory=OUT):
    folder=Path(directory)
    cf=folder/"abc_rf_holdout_confusion.csv"
    af=folder/"abc_rejection_model_acceptance.csv"
    if not cf.is_file() or not af.is_file():
        raise FileNotFoundError("Must retrieve successful model-native 80-year RF/ABC artifact")
    c=pd.read_csv(cf)
    a=pd.read_csv(af)
    axes,matrices=summarize_classifier_errors(c)
    posterior=posterior_uncertainty(a)
    outputs=dict(rf_structural_axis_recoverability=axes,
                 rf_structural_axis_confusion=matrices,
                 conditional_abc_posterior_concentration=posterior)
    for name,s in outputs.items():
        s.to_csv(folder/(name+".csv"),index=False)
    receipt=dict(status="POST_RESULT_GENUINE_80YEAR_ABC_RF_AXIS_IDENTIFIABILITY",
        original_rf_retrained=False,full_12_class_source_count=EXPECTED_CLASSES,
        holdout_rate_draws=EXPECTED_HELD,
        error_definition="exact original RF predictions on completely held-out shared rate draw IDs",
        source_sha256={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in [cf,af]},
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limits=["Actual 80-year synthetic scenarios, not observations of larval predator interactions",
                "Only four signs, small set of possible summaries",
                "Posterior concentration depends on synthetic prior and 12-class list",
                "Chance reference reflects balanced synthetic classes; no null-model p-value",
                "RF vote fractions are not posterior model probabilities"])
    (folder/"abc_rf_axis_receipt.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print("RF_ECOLOGICAL_AXIS_IDENTIFIABILITY\n"+axes.to_string(index=False),flush=True)
    print("ABC_CONDITIONAL_POSTERIOR_CONCENTRATION\n"+
          posterior.to_string(index=False),flush=True)
    return axes,matrices,posterior


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    p.add_argument("--folder",type=Path,default=OUT)
    args=p.parse_args()
    if not args.run:p.error("Explicit --run required")
    run(args.folder)
