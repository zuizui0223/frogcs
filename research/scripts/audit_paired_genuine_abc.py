"""Paired-rate-draw bootstrap and marginal class aggregation for genuine 80y ABC.

The two reverse-edge outcomes under one rate draw are NOT 512 independent
draws. Resample original 256 rate draw IDs, retaining the paired edge results
AND the same draw index across all twelve structural model classes.

Posteriors are conditional on previously declared *hypothetical* process-rate
priors, original 80y model, and exact four-sign artificial observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from model_native_2x2x2_prior import OUT,METRICS,TARGET
from model_native_abc_rf import load_actual_refs,features

BOOT=1999
SEED=20261101
SCALES=("log","raw","marginal_scale")
THRESHOLDS=("default","strict11","loose7")
LOW=0.025
HIGH=0.975


def paired_prior_indicator(reference,scale):
    columns=list(METRICS)
    if scale not in SCALES:raise ValueError("Invalid response-scale prior")
    x=features(reference,scale)
    mask=(x==np.asarray(TARGET,int)).all(axis=1)
    frame=reference[["structure_id","context","family","risk",
                     "draw","reverse_on"]].copy()
    frame["accepted"]=mask
    return frame


def draw_rate_matrix(signs):
    classes=sorted(signs.structure_id.unique())
    draws=sorted(signs.draw.unique())
    if not len(classes)==12 or len(draws)<4:
        raise ValueError("Need 12 equally weighted hypotheses and common rate draws")
    per_class=[]
    pair_identity=[]
    for cls in classes:
        x=signs[signs.structure_id==cls].sort_values(["draw","reverse_on"])
        if len(x)!=len(draws)*2 or x.duplicated(["draw","reverse_on"]).any():
            raise AssertionError("Unbalanced ON/OFF edge source")
        observed=x.draw.to_numpy(int).reshape(-1,2)
        expected=np.asarray(draws,int)[:,None]
        if not np.array_equal(observed,np.repeat(expected,2,axis=1)):
            raise AssertionError("No exact prior rate/edge pairing")
        values=x.accepted.to_numpy(bool).reshape(-1,2)
        per_class.append(values.sum(axis=1))
        pair_identity.append(np.mean(values[:,0]==values[:,1]))
    return classes,np.column_stack(per_class),np.asarray(pair_identity,float)


def paired_bootstrap(signs,n_boot=BOOT,seed=SEED):
    classes,matrix,equal=draw_rate_matrix(signs)
    n_draw=len(matrix)
    observed=matrix.sum(axis=0)
    total=int(observed.sum())
    if total==0:
        # Exact-sign ABC cannot define a relative model posterior then.
        raise ValueError("No four-sign matches; posterior is undefined")
    rng=np.random.default_rng(seed)
    samples=rng.integers(0,n_draw,size=(n_boot,n_draw))
    counts=matrix[samples].sum(axis=1)
    denom=counts.sum(axis=1)
    if (denom<=0).any():
        raise ValueError("One bootstrap repetition has no accepted models")
    shares=counts/denom[:,None]
    rates=counts/(2*n_draw)
    names=signs.drop_duplicates("structure_id").set_index("structure_id")
    rows=[]
    for i,cls in enumerate(classes):
        r=names.loc[cls]
        rows.append(dict(scale="TO_FILL",structure_id=cls,
             context=r.context,family=r.family,risk=bool(r.risk),
             n_effective_paired_rate_draws=n_draw,
             n_reversal_edge_states_per_rate=2,
             n_accepted=int(observed[i]),
             acceptance_rate=float(observed[i]/(2*n_draw)),
             paired_draw_acceptance_ci_low=float(np.quantile(rates[:,i],LOW)),
             paired_draw_acceptance_ci_high=float(np.quantile(rates[:,i],HIGH)),
             conditional_abc_share=float(observed[i]/total),
             paired_draw_abc_share_ci_low=float(np.quantile(shares[:,i],LOW)),
             paired_draw_abc_share_ci_high=float(np.quantile(shares[:,i],HIGH)),
             paired_match_indicator_identical_fraction=float(equal[i])))
    table=pd.DataFrame(rows)
    groups=[]
    for dimension in ("context","family","risk"):
        for value,idx in table.groupby(dimension).indices.items():
            ids=np.asarray(idx,int)
            frac=shares[:,ids].sum(axis=1)
            groups.append(dict(scale="TO_FILL",dimension=dimension,label=str(value),
                 accepted_count=int(observed[ids].sum()),
                 conditional_abc_share=float(observed[ids].sum()/total),
                 paired_draw_ci_low=float(np.quantile(frac,LOW)),
                 paired_draw_ci_high=float(np.quantile(frac,HIGH))))
    return table,pd.DataFrame(groups)


def paired_signature_equivalence(reference):
    records=[]
    for cls,g in reference.groupby("structure_id"):
        a=g[g.reverse_on==0].sort_values("draw")
        b=g[g.reverse_on==1].sort_values("draw")
        if len(a)!=len(b) or not np.array_equal(a.draw,b.draw):
            raise AssertionError("Missing prior-matched reverse cases")
        for scale in ("log","raw"):
            c=[f"sign_{scale}_{m}" for m in METRICS]
            q=a[c].to_numpy(int)==b[c].to_numpy(int)
            full=np.all(q,axis=1)
            target_a=a[f"matches_{scale}"].to_numpy(bool)
            target_b=b[f"matches_{scale}"].to_numpy(bool)
            records.append(dict(structure_id=cls,scale=scale,
                                n_draws=len(a),
                                n_identical_all_four_signs=int(full.sum()),
                                n_identical_ABC_acceptance=int(
                                    np.sum(target_a==target_b)),
                                n_accept_off=int(target_a.sum()),
                                n_accept_on=int(target_b.sum()),
                                n_different_target_state=int(
                                    np.sum(target_a!=target_b))))
    return pd.DataFrame(records)


def tolerance_sensitivity(reference):
    rows=[]
    for scale in ("log","raw"):
        for threshold in THRESHOLDS:
            col=f"matches_{scale}" if threshold=="default" else \
                f"matches_{scale}_{threshold}"
            if col not in reference:raise ValueError("Missing threshold sensitivity "+col)
            counts=reference.groupby("structure_id")[col].sum()
            total=int(counts.sum())
            if total==0:continue
            for cls,value in counts.items():
                rows.append(dict(scale=scale,threshold=threshold,
                                 structure_id=cls,n_accepted=int(value),
                                 conditional_abc_share=float(value/total)))
    return pd.DataFrame(rows)


def run(folder=OUT,boot=BOOT):
    folder=Path(folder)
    reference,priors,receipts=load_actual_refs(folder)
    if int(reference.draw.nunique())!=256 or len(reference)!=6144:
        raise AssertionError("Not the successful 256-prior×12-structure×edge 80y reference")
    samples=[];groups=[]
    for scale in SCALES:
        t,g=paired_bootstrap(paired_prior_indicator(reference,scale),
                             n_boot=boot,seed=SEED)
        t["scale"]=scale;g["scale"]=scale
        samples.append(t);groups.append(g)
    output=dict(
        paired_prior_class_intervals=pd.concat(samples,ignore_index=True),
        paired_prior_higher_level_intervals=pd.concat(groups,ignore_index=True),
        paired_reverse_edge_identifiability=paired_signature_equivalence(reference),
        factorial_sign_precision_sensitivity=tolerance_sensitivity(reference))
    for name,frame in output.items():
        frame.to_csv(folder/(name+".csv"),index=False)
    receipt=dict(status="PAIRED_PRIOR_BOOTSTRAP_EXPLORATORY_80Y_ABC",
        actual_rate_draws_per_model=256,reverse_nuisance_edges=2,
        groups=12,n_boot=boot,seed=SEED,
        retain_correlations="Resample same 256 process draw IDs across 12 structures and both reverse edge states",
        no_external_biological_prior=True,
        notes=["Wilson intervals using 512 ON/OFF rows are not independent-draw intervals",
               "Paired draw intervals reflect only finite Monte Carlo prior library uncertainty",
               "Model shares conditional on exact 4-sign target and hypothetical rate priors",
               "Results do not establish field trophic mechanism"],
        source_hashes={context:hashlib.sha256(
             (folder/(context+"_prior_predictive_reference.csv.gz")).read_bytes()).hexdigest()
             for context in ("original","D_first_S_overtakes","S_first_D_overtakes")},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (folder/"paired_prior_abc_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("PAIRED_PRIOR_CLASS_ABC\n"+output["paired_prior_class_intervals"].to_string(index=False),flush=True)
    print("AGGREGATE_PRIOR_SUPPORT\n"+output["paired_prior_higher_level_intervals"].to_string(index=False),flush=True)
    print("EDGE_FOUR_SIGN_IDENTITY\n"+output["paired_reverse_edge_identifiability"].to_string(index=False),flush=True)
    print("SIGN_TOLERANCE_SENSITIVITY\n"+output["factorial_sign_precision_sensitivity"].to_string(index=False),flush=True)
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true")
    parser.add_argument("--folder",type=Path,default=OUT)
    parser.add_argument("--bootstrap",type=int,default=BOOT)
    a=parser.parse_args()
    if not a.run:parser.error("Explicit --run required")
    run(a.folder,a.bootstrap)
