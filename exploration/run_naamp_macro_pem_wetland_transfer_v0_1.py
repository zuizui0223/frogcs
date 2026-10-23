#!/usr/bin/env python3
"""NAAMP macro wetland-continuity vs NWI PEM category: held-out route predictions.

Reuses the 2026-10-23 real NAAMP within-route 10-stop Sørensen community
cohort. Predictive only, selected after a null PEM boundary result.
All site/richness predictor/outcome centering uses the *same* survey night.
Whole physical routes are held out; no site-pair pseudoreplication.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"exploration/run_naamp_macro_pem_boundary_turnover_v0_1.py"
SEED=2601123
NULL_REPS=4999
BASE_COLS=("dist_2","dist_3","dist_4","dist_5","dist_6","dist_7","dist_8","dist_9",
           "abs_airtemp_c_diff","abs_noise_index_diff",
           "abs_acoustic_richness_diff","mean_acoustic_richness")
EXTRA_COLS=("boundary","abs_wetland_frac_diff")
COLS=BASE_COLS+EXTRA_COLS
MODELS={
 "M0": BASE_COLS,
 "M_PEM": BASE_COLS+("boundary",),
 "M_WET": BASE_COLS+("abs_wetland_frac_diff",),
 "M_BOTH": COLS
}
TESTS={
 "WET_over_M0":("M0","M_WET"),
 "PEM_over_M0":("M0","M_PEM"),
 "PEM_increment_over_WET":("M_WET","M_BOTH"),
 "WET_increment_over_PEM":("M_PEM","M_BOTH")
}
def load(path):
    spec=importlib.util.spec_from_file_location("naamp_boundary_macro",path)
    if spec is None or spec.loader is None:raise RuntimeError("No available locked NAAMP boundary macro source")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def fold_of_route(route):
    return "A" if hashlib.sha256(route.encode("utf-8")).digest()[0]%2==0 else "B"

def demean(v,index,sizes):
    return v-np.bincount(index,weights=v,minlength=len(sizes))[index]/sizes[index]

def prepare(d):
    if d.empty:raise ValueError("Empty original NAAMP community data")
    for field in COLS+("sorensen",):
        if field not in d:raise ValueError(f"Missing original locked field: {field}")
    if not np.isfinite(d[list(COLS)+["sorensen"]].to_numpy(float)).all():
        raise ValueError("Non-finite raw NAAMP pair values")
    runs,run_idx=np.unique(d.run_id.astype(str).to_numpy(),return_inverse=True)
    routes,route_idx=np.unique(d.route.astype(str).to_numpy(),return_inverse=True)
    G=len(routes)
    if G<50:raise ValueError("Insufficient whole-route geographic replication")
    run_sizes=np.bincount(run_idx)
    y=demean(d["sorensen"].to_numpy(float),run_idx,run_sizes)
    X=np.column_stack([demean(d[field].to_numpy(float),run_idx,run_sizes) for field in COLS])
    route_sizes=np.bincount(route_idx)
    folds=np.array([fold_of_route(route) for route in routes])
    if min(np.count_nonzero(folds=="A"),np.count_nonzero(folds=="B"))<20:
        raise ValueError("Insufficient heldout routes per geographic fold")
    return {"y":y,"X":X,"runs":runs,"routes":routes,"run_idx":run_idx,
            "route_idx":route_idx,"route_sizes":route_sizes,"folds":folds,
            "run_n":len(runs),"pair_n":len(d)}

def route_signflip(scores,seed,draws=NULL_REPS):
    rng=np.random.default_rng(seed)
    obs=float(scores.mean())
    extreme=0
    for start in range(0,draws,400):
        n=min(400,draws-start)
        signs=rng.choice([-1.,1.],size=(n,len(scores)))
        sm=(signs@scores)/len(scores)
        extreme+=int(np.count_nonzero(np.abs(sm)>=abs(obs)-1e-15))
    return {"draws":draws,"two_sided_plus_one_p":(1+extreme)/(1+draws),
            "extreme_draws":extreme,"assumes_independent_symmetric_route_level_loss_differences":True}

def fit_fold(inputs,fold):
    r=inputs["route_idx"]
    routes=inputs["routes"]
    foldvec=inputs["folds"][r]
    train=foldvec!=fold
    test=foldvec==fold
    ntrain=int(np.count_nonzero(train));ntest=int(np.count_nonzero(test))
    if ntrain<500 or ntest<500:raise ValueError("Insufficient route-held-out testing data")
    trainroutes=np.unique(r[train])
    testroutes=np.unique(r[test])
    trainweights=1./inputs["route_sizes"][r[train]]
    xtrain=inputs["X"][train]
    sd=xtrain.std(axis=0)
    if np.any(sd<1e-10):
        raise ValueError("Design lacks frozen variation in at least one feature")
    Xtr=xtrain/sd
    Xte=inputs["X"][test]/sd
    ytr=inputs["y"][train]
    yte=inputs["y"][test]
    scales={col:float(v) for col,v in zip(COLS,sd)}
    losses={}
    betas={}
    for name,selected in MODELS.items():
        indices=np.array([COLS.index(x) for x in selected],int)
        A=Xtr[:,indices]
        b=Xte[:,indices]
        w=np.sqrt(trainweights)
        beta,_,rank,_=np.linalg.lstsq(A*w[:,None],ytr*w,rcond=None)
        if rank!=len(indices):raise ValueError("Locked feature set not identifiable in the training route fold")
        predicted=b@beta
        sqerr=(yte-predicted)**2
        total=np.bincount(r[test],weights=sqerr,minlength=len(routes))
        n=np.bincount(r[test],minlength=len(routes))
        means=np.divide(total,n,out=np.full(len(routes),np.nan),where=n>0)
        losses[name]=means
        betas[name]={col:float(x) for col,x in zip(selected,beta)}
    return {
       "fold":fold,"train_route_count":len(trainroutes),
       "heldout_route_count":len(testroutes),
       "train_pair_rows":ntrain,"heldout_pair_rows":ntest,
       "test_routes_idx":testroutes,
       "errors":losses,"coefficients_training_scaled":betas,
       "nuisance_training_within_run_SD":scales}

def inference(route_values,folds,seed):
    if len(route_values)<50 or not np.isfinite(route_values).all():
        raise ValueError("Cannot infer from fewer than 50 independent route-level matched losses")
    n=len(route_values)
    m=float(route_values.mean())
    se=float(np.std(route_values,ddof=1)/math.sqrt(n))
    crit=float(student_t.ppf(.975,n-1))
    p=float(2*student_t.sf(abs(m/se),n-1)) if se>0 else None
    fold_report={}
    for fold in ("A","B"):
        val=route_values[folds==fold]
        fold_report[fold]={"n_routes":int(len(val)),"mean_gain":float(val.mean()),
                            "positive_routes":int(np.count_nonzero(val>0))}
    return {"n_independent_routes":n,
            "mean_gain_sorensen_squared":m,
            "ci95_route_t":[m-crit*se,m+crit*se],
            "route_t_P":p,
            "positive_fraction_of_routes":float(np.mean(route_values>0)),
            "folds":fold_report,
            "route_signflip":route_signflip(route_values,seed)}

def analyze_mode(d,mode):
    inp=prepare(d)
    G=len(inp["routes"])
    loss={name:np.full(G,np.nan,float) for name in MODELS}
    fold_details={}
    for fold in ("A","B"):
        r=fit_fold(inp,fold)
        idx=r.pop("test_routes_idx")
        for name in MODELS:loss[name][idx]=r["errors"][name][idx]
        del r["errors"]
        fold_details[fold]=r
    if any(not np.isfinite(v).all() for v in loss.values()):
        raise ValueError("Route losses did not cover every heldout route exactly once")
    base_mse=float(loss["M0"].mean())
    if base_mse<=0:raise ValueError("Invalid baseline Sørensen MSE")
    contrasts={}
    for j,(k,(a,b)) in enumerate(TESTS.items()):
        route_gain=loss[a]-loss[b]
        q=inference(route_gain,inp["folds"],SEED+j+(0 if mode=="any" else 110))
        q["gain_as_percent_of_M0_MSE"]=100*q["mean_gain_sorensen_squared"]/base_mse
        q["source_model"]=a;q["compared_model"]=b
        contrasts[k]=q
    primary=contrasts["WET_over_M0"]
    transferred=(primary["mean_gain_sorensen_squared"]>0
              and primary["ci95_route_t"][0]>0
              and all(primary["folds"][x]["mean_gain"]>0 for x in ("A","B")))
    return {
       "mode":mode,"n_heldout_routes":G,"n_survey_nights":inp["run_n"],
       "n_stop_pairs":inp["pair_n"],"m0_mse":base_mse,
       "mse_by_model":{name:float(v.mean()) for name,v in loss.items()},
       "contrasts":contrasts,
       "fold_source_fit_summaries":fold_details,
       "primary_transfer_supported_if_mode_any":bool(transferred),
       "evaluation":"geographically whole-route-heldout conditional within-run MSE",
       "equal_weight_per_independent_route":True,
       "no_site_pair_as_independent_unit":True}

def synthetic():
    rng=np.random.default_rng(2602008)
    rows=[]
    for rr in range(80):
        wet=rng.uniform(0,1,size=10)
        pem=rng.random(10)>.6
        temp=rng.normal(15,2.5,size=10)
        sound=rng.uniform(0,4,size=10)
        rich=rng.integers(1,6,size=10)
        for k in range(2):
            for i in range(10):
                for j in range(i+1,10):
                    row={"route":f"synthetic_{rr}","run_id":f"night{rr}-{k}",
                          "boundary":int(pem[i]!=pem[j]),
                          "abs_wetland_frac_diff":float(abs(wet[i]-wet[j])),
                          "abs_airtemp_c_diff":float(abs(temp[i]-temp[j])),
                          "abs_noise_index_diff":float(abs(sound[i]-sound[j])),
                          "abs_acoustic_richness_diff":float(abs(rich[i]-rich[j])),
                          "mean_acoustic_richness":float((rich[i]+rich[j])/2)}
                    for z in range(2,10):row[f"dist_{z}"]=int(j-i==z)
                    y=.22+.20*row["abs_wetland_frac_diff"]+.013*row["abs_airtemp_c_diff"]+.05*row["boundary"]+.02*row["abs_acoustic_richness_diff"]+.005*rr/80
                    y+=float(rng.normal(0,.027))
                    if y<0 or y>1:raise AssertionError("Synthetic Sørensen outside valid unit")
                    row["sorensen"]=y
                    rows.append(row)
    res=analyze_mode(pd.DataFrame(rows),"any")
    gain=res["contrasts"]["WET_over_M0"]["mean_gain_sorensen_squared"]
    if not gain>0 or min(res["contrasts"]["WET_over_M0"]["folds"][f]["mean_gain"] for f in ("A","B"))<=0:
        raise AssertionError(f"Known synthetic continuous wetland effect not recovered {gain}")
    return {"status":"PASS","whole_routes_in_holdout":80,
            "known_wetland_MSE_gain":gain,
            "no_test_route_in_train":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_macro_wetland_transfer")
    ap.add_argument("--synthetic-only",action="store_true")
    a=ap.parse_args()
    qa=synthetic()
    if a.synthetic_only:
        print(json.dumps(qa,sort_keys=True))
        return
    orig=load(BASE)
    dd,scope=orig.records()
    if scope["source_NAAMP_standard_runs"]!=7848 or scope["source_10stop_NWI_complete"]!=6236:
        raise ValueError("Real public-NAAMP/NWI source sample has changed")
    out={
       "analysis":"NAAMP_macro_whole_route_heldout_continuous_wetland_cover_versus_NWI_PEM_boundary",
       "status":"empirical_NAAMP_whole_route_heldout_ecological_prediction_completed",
       "date":"2026-10-23","source":scope,
       "post_readback_protocol":"exploration/NAAMP_MACRO_WETLAND_CONTINUOUS_TRANSFER_SPEC_2026_10_23.md",
       "synthetic_QA":qa,
       "results":{},
       "primary_mode":"CallingIndex>=1",
       "causal_plant_or_interspecific_interaction_established":False,
       "NWI_is_observation_date_matched_aquatic_plants":False,
       "not_an_advance_or_independent_individual_occupancy_forecast":True,
       "frozen_JAE_RC6_main_SI_submission_unchanged":True
    }
    for mode in ("any","strong"):
        out["results"][mode]=analyze_mode(dd[mode],mode)
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("MACRO_WETLAND_TRANSFER_BEGIN")
    print(json.dumps({"status":out["status"],
         "QA":qa,"source_summary":{"initial":scope["source_NAAMP_standard_runs"],"linked":scope["source_10stop_NWI_complete"]},
         "modes":{m:{
             "n_routes":x["n_heldout_routes"],"n_survey_nights":x["n_survey_nights"],
             "n_stop_pairs":x["n_stop_pairs"],"m0_mse":x["m0_mse"],
             "mse_by_model":x["mse_by_model"],
             "primary_supported":x["primary_transfer_supported_if_mode_any"],
             "contrasts":{name:{
                "mean_gain":v["mean_gain_sorensen_squared"],
                "ci95_route_t":v["ci95_route_t"],
                "p_route_t":v["route_t_P"],
                "relative_M0_pct":v["gain_as_percent_of_M0_MSE"],
                "folds":v["folds"],
                "route_signflip_P":v["route_signflip"]["two_sided_plus_one_p"]
                } for name,v in x["contrasts"].items()}}
                for m,x in out["results"].items()}},sort_keys=True,allow_nan=False),flush=True)
    print("MACRO_WETLAND_TRANSFER_END",flush=True)

if __name__=="__main__":
    main()
