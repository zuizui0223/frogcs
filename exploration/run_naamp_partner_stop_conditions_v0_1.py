#!/usr/bin/env python3
"""Stop-level air temperature, noise and sequence adjustment of same-run frog pair contrast.

New post-hoc, fixed hypotheses. Crossfit site-choice weights by route;
compare same species-by-stop row/column margins under M0 NWI and M1 NWI
plus local stop observation conditions. No direct biotic interaction inference.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
B=199
BURN=40
THIN=8
SEED=2840311
BOOT=2000
BOOT_SEED=2840310
RIDGE=3.0
BETA_LIMIT=3.0
SOURCE_NWI_RUN=39516056663

def json_native(x):
    """Only convert NumPy container/scalar wrappers in diagnostics."""
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,np.ndarray):return x.tolist()
    raise TypeError(f"Cannot JSON serialize {type(x).__name__}")

EXPECTED={"any":{"Hyla versicolor":744,"Anaxyrus fowleri":538},
          "strong":{"Hyla versicolor":171,"Anaxyrus fowleri":72}}

def imp(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(obj)
    return obj

prev=imp("same_night_partner_frozen",ROOT/"exploration/run_naamp_same_run_partner_switch_v0_1.py")
pairmod=prev.pairmod
prior=prev.prior
source=imp("stop_observation_covariates",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")

def synthetic():
    original=prev.synth()
    orig=np.arange(10,dtype=float)
    t=20+1.2*orig
    sound=orig%3
    v=np.column_stack([np.linspace(0,4,10),np.linspace(0,1,10),
                       (t-t.mean())/5,(sound-sound.mean())/2,
                       (orig-4.5)/4.5])
    assert v.shape==(10,5) and np.max(abs(v[:,2].mean()))<1e-12
    assert np.max(abs(v[:,3].mean()))<1e-12 and np.max(abs(v[:,4].mean()))<1e-12
    assert np.isclose(
        prior.conditional_logprob(v,{0,2,6},np.array([.2,.3]),[0,1]),
        prior.conditional_logprob(v,{0,2,6},np.array([.2,.3,0,0,0]),[0,1,2,3,4]))
    return {"status":"PASS","same_night_prev_null":original,
            "same_observed_matrix_and_preexisting_NWI_null":True,
            "stop_covariates_centered":True,"M1_reduces_to_M0_at_zero_local_coefficients":True}

def source_augmented(records):
    raw=source.hist.load_retry()
    runs,sets=source.base.build_runs(raw)
    sampled,_=source.spatial.stop_matrix(raw,set(runs.RunID.astype(str)))
    environments=source.get_temps_and_detection(raw,runs,sampled)
    year=dict(zip(runs.RunID.astype(str),runs.SurveyYear.astype(int)))
    audit=Counter()
    for rid,row in records.items():
        if rid not in year:raise RuntimeError("NWI validated RunID does not exist in pinned NAAMP")
        steps=sorted(sampled[rid],key=int)
        if len(steps)!=10:raise RuntimeError(f"Incorrect stop count {rid}")
        env=[environments.get((rid,s),{}) for s in steps]
        arr=np.asarray([[z.get("stop_air_temp_c",np.nan),
                         z.get("stop_sound_index",np.nan)] for z in env],dtype=float)
        if arr.shape!=(10,2) or not np.isfinite(arr).all():
            raise RuntimeError(f"Missing stop air/noise in originally complete-case NWI run {rid}")
        order=np.asarray([int(s) for s in steps],float)
        assert np.unique(order).size==10
        cond=np.column_stack([(arr[:,0]-arr[:,0].mean())/5.,
                              (arr[:,1]-arr[:,1].mean())/2.,
                              (order-5.5)/4.5])
        v=np.column_stack([row["v"],cond])
        if v.shape!=(10,5) or not np.isfinite(v).all():
            raise RuntimeError("Site-level NWI augmented feature sample invalid")
        row["v5"]=v
        row["SurveyYear"]=year[rid]
        audit["augmented_10_stop_runs"]+=1
        audit["has_site_air_temp_spread"]+=int(np.ptp(arr[:,0])>0)
        audit["has_site_noise_spread"]+=int(np.ptp(arr[:,1])>0)
    if len(records)!=6236:
        raise RuntimeError("Full source-blind NWI sample changed, expected 6236")
    return dict(audit)

def train_by_mode(records,mode):
    byfold={"A":defaultdict(list),"B":defaultdict(list)}
    for row in records.values():
        for sp,places in row["activity"][mode].items():
            k=len(places)
            if not 1<=k<=9:continue
            cov=row["v5"]
            byfold[row["fold"]][sp].append({
                "v":cov,"k":k,
                "obs":np.sum(cov[sorted(places)],axis=0),
                "route":row["route"]})
    return byfold

def estimate_conditional_location(rows):
    n=len(rows)
    routes=len({z["route"] for z in rows})
    if n<30 or routes<12:
        return None,{"status":"insufficient","training_taxon_runs":n,"routes":routes}
    byk=defaultdict(list)
    count=np.zeros(5,dtype=float)
    for obj in rows:
        byk[obj["k"]].append(obj["v"])
        count+=obj["obs"]
    blocks=[]
    for k,seq in byk.items():
        a=np.stack(seq,axis=0)
        blocks.append(np.einsum("mjd,sj->msd",a,prior.MASKS[k],optimize=True))
    def fn(theta):
        ll=.5*RIDGE*float(theta@theta)-float(theta@count)
        grad=RIDGE*theta-count.copy()
        for block in blocks:
            score=np.einsum("msd,d->ms",block,theta,optimize=True)
            z=logsumexp(score,axis=1)
            probs=np.exp(score-z[:,None])
            ll+=float(z.sum())
            grad+=np.einsum("ms,msd->d",probs,block,optimize=True)
        return ll,grad
    fit=minimize(fn,np.zeros(5),method="L-BFGS-B",jac=True,
                 bounds=[(-BETA_LIMIT,BETA_LIMIT)]*5,
                 options={"maxiter":100,"ftol":1e-10})
    if not fit.success or not np.isfinite(fit.x).all():
        return None,{"status":"optimizer_failed","training_taxon_runs":n,"routes":routes}
    return np.asarray(fit.x,float),{"status":"fitted","training_taxon_runs":n,
               "routes":routes,"coefficients":fit.x.tolist(),
               "iterations":int(fit.nit)}

def fit_all(records,mode,oldcoef):
    split=train_by_mode(records,mode)
    trained={}
    audit={}
    for fold in ("A","B"):
        b={}
        diagnostics={}
        for sp in sorted(split[fold]):
            theta,meta=estimate_conditional_location(split[fold][sp])
            if theta is not None:b[sp]=theta
            diagnostics[sp]=meta
        trained[fold]=b
        audit[fold]={"n_taxon_units":len(diagnostics),
                     "n_fitted":len(b),
                     "n_fallback":len(diagnostics)-len(b),
                     "n_temperature_positive":sum(x[2]>0 for x in b.values()),
                     "n_noise_positive":sum(x[3]>0 for x in b.values()),
                     "n_stop_order_positive":sum(x[4]>0 for x in b.values()),
                     "per_taxon":diagnostics}
        print("M1_TAXON_TRAIN_COMPLETE",mode,fold,
              json.dumps({k:v for k,v in audit[fold].items() if k!="per_taxon"},default=json_native),flush=True)
    return trained,audit

def coefficients_for_run(row,mode,trained,oldcoef):
    src=prior.complementary(row["fold"])
    base=oldcoef[src]
    new=trained[src]
    def for_sp(sp):
        beta0=np.asarray(base.get(sp,{}).get("wetland_and_emergent",np.zeros(2)),float)
        beta1=np.asarray(new.get(sp,np.r_[beta0,np.zeros(3)]),float)
        if beta1.shape!=(5,) or beta0.shape!=(2,):
            raise RuntimeError("Species-specific NWI coefficients drift")
        return beta0,beta1
    return for_sp

def validate_locations(records,mode,trained,oldcoef):
    rows=[]
    for row in records.values():
        get=coefficients_for_run(row,mode,trained,oldcoef)
        for sp,spots in row["activity"][mode].items():
            if not 1<=len(spots)<=9:continue
            b0,b1=get(sp)
            l0=prior.conditional_logprob(row["v5"],spots,b0,[0,1])
            l1=prior.conditional_logprob(row["v5"],spots,b1,[0,1,2,3,4])
            rows.append({"route":row["route"],"fold":row["fold"],"taxon":sp,
                         "gain":l1-l0})
    df=pd.DataFrame(rows)
    if df.empty:raise RuntimeError("No fixed-k crossfold scoring cells")
    grouped=df.groupby("route").gain.agg(["sum","size"])
    sums=grouped["sum"].to_numpy(dtype=float)
    counts=grouped["size"].to_numpy(dtype=float)
    n=len(sums)
    rng=np.random.default_rng(BOOT_SEED+(0 if mode=="any" else 1))
    idx=rng.integers(n,size=(BOOT,n))
    sampled=sums[idx].sum(axis=1)/counts[idx].sum(axis=1)
    ci=[float(x) for x in np.quantile(sampled,[.025,.975])]
    return {"n_taxon_runs":len(df),"n_routes":n,
            "mean_heldout_conditional_logscore_gain":float(df.gain.mean()),
            "bootstrap_ci95":ci,"predictive_loss_supported":bool(ci[1]<0),
            "fold_means":{f:float(z.gain.mean()) for f,z in df.groupby("fold")},
            "N_boot":BOOT}

def sample_weighted_null(rows,theta,v,rng):
    state=[set(s) for s in rows]
    margins=prior.fixed_margins(state)
    score=theta@v.T
    n=len(rows)
    feasible=accepted=0
    for _ in range(BURN*n):
        f,a=prior.weighted_trade(state,score,rng);feasible+=f;accepted+=a
    observed=[]
    for k in range(B):
        for _ in range(THIN*n):
            f,a=prior.weighted_trade(state,score,rng);feasible+=f;accepted+=a
        observed.append(pairmod.cov_matrix(state))
        if k in (0,B//2,B-1) and prior.fixed_margins(state)!=margins:
            raise RuntimeError("Curveball changed taxon or stop richness margin")
    if not feasible or not accepted:
        raise RuntimeError("No accepted swap on eligible same-run matrix")
    arr=np.stack(observed,axis=0)
    return arr,accepted/feasible

def robust_stats(records,mode,trained,oldcoef,ref,yearmap,outdir):
    if ref.RunID.duplicated().any():raise RuntimeError("Duplicate frozen checkerboard RunID")
    old=ref.set_index("RunID")
    allids=sorted(set(records)&set(old.index.astype(str)))
    if len(allids)!=(3659 if mode=="any" else 1766):
        raise RuntimeError("Reference selected study population changed")
    rows_by=defaultdict(list)
    qualified=0
    for nrun,rid in enumerate(allids,1):
        row=records[rid]
        taxa,ss=prior.ref_rows(row,mode)
        if not np.isclose(prior.cscore(ss),float(old.loc[rid,"observed"]),atol=1e-8,rtol=0):
            raise RuntimeError("Original NWI reference observed C-score differs")
        idx={s:i for i,s in enumerate(taxa)}
        trios=[t for t in prev.TRIOS if set(t).issubset(idx)]
        if not trios:continue
        qualified+=1
        get=coefficients_for_run(row,mode,trained,oldcoef)
        b=[get(sp) for sp in taxa]
        obs_cov=pairmod.cov_matrix(ss)
        means={}
        acceptance={}
        for model in ["M0","M1"]:
            theta=np.stack([v[0 if model=="M0" else 1] for v in b])
            cov=row["v5"][:,[0,1]] if model=="M0" else row["v5"]
            key=f"{SEED}|{mode}|{model}|{rid}".encode()
            rng=random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8],"big"))
            mat,acc=sample_weighted_null(ss,theta,cov,rng)
            means[model]=mat.mean(axis=0)
            acceptance[model]=acc
        for t in trios:
            c,p,n=t
            i,j,k=idx[c],idx[p],idx[n]
            record={"RunID":rid,"route":row["route"],"fold":row["fold"],
                    "State":row["state"],"SurveyYear":int(yearmap[rid]),
                    "n_taxa":len(taxa),
                    "n_mapped_PEM_stops":int((row["v5"][:,1]>0).sum()),
                    "M0_null_acceptance":acceptance["M0"],
                    "M1_null_acceptance":acceptance["M1"]}
            for model in ["M0","M1"]:
                pos=float(obs_cov[i,j]-means[model][i,j])
                neg=float(obs_cov[i,k]-means[model][i,k])
                record[f"{model}_CP"]=pos
                record[f"{model}_CN"]=neg
                record[f"{model}_D"]=pos-neg
            record["adjustment_difference"]=record["M1_D"]-record["M0_D"]
            rows_by[n].append(record)
        if qualified%300==0:print(f"{mode}: {qualified} complete focal triples simulated",flush=True)
    result={}
    for n in prev.NEGATIVES:
        frame=pd.DataFrame(rows_by.get(n,[]))
        count=prev.EXPECTED if hasattr(prev,"EXPECTED") else None
        if frame.empty:
            result[n]={"status":"no_shared_three_taxon_runs"}
            continue
        expected=EXPECTED[mode][n]
        if len(frame)!=expected:
            raise RuntimeError(f"Triad {mode}/{n} membership drift: {len(frame)}!={expected}")
        frame.to_csv(outdir/f"{mode}_{n.replace(' ','_')}_contexts.csv",index=False)
        desc={"trio":[prev.CENTRAL,prev.POSITIVE,n],
              "n":len(frame),"routes":int(frame.route.nunique()),
              "states":int(frame.State.nunique()),
              "null_mean_acceptance":{
                  "M0":float(frame.M0_null_acceptance.mean()),
                  "M1":float(frame.M1_null_acceptance.mean())},
              "models":{}}
        for model in ["M0","M1"]:
            inner={}
            for field in ["CP","CN","D"]:
                name=f"{model}_{field}"
                inner[field]={"overall":prev.estimate(frame,name,min_runs=60,min_routes=25),
                              "folds":prev.folds(frame,name),
                              "early":prev.estimate(frame[frame.SurveyYear<=2009],name),
                              "late":prev.estimate(frame[frame.SurveyYear>=2010],name)}
            desc["models"][model]=inner
        desc["adjustment_D_change"]=prev.estimate(frame,"adjustment_difference",min_runs=60,min_routes=25)
        result[n]=desc
    eligible=[(name,x) for name,x in result.items() if x.get("models",{}).get("M1",{}).get("D",{}).get("overall",{}).get("status")=="fitted"]
    if eligible:
        qs=multipletests([x["models"]["M1"]["D"]["overall"]["p_two_sided"] for name,x in eligible],
                        method="fdr_bh")[1]
        for (name,x),q in zip(eligible,qs):
            x["M1_BH_q"]=float(q)
            m=x["models"]["M1"]
            bpos=m["CP"]["overall"];bneg=m["CN"]["overall"];bd=m["D"]["overall"]
            f=m["D"]["folds"]
            x["M1_signed_contrast_supported"]=bool(q<.05 and bd["ci95"][0]>0
                and bpos["ci95"][0]>0 and bneg["ci95"][1]<0
                and f.get("A",{}).get("mean",0)>0
                and f.get("B",{}).get("mean",0)>0)
    return result,{"original_checked_runs":len(allids),
                   "unique_original_selected_triple_runs":qualified}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-nwi",type=Path)
    p.add_argument("--outdir",type=Path,default=ROOT/"build"/"partner_stop_context")
    p.add_argument("--synthetic-only",action="store_true")
    arg=p.parse_args()
    q=synthetic()
    print("STOP_CONTEXT_SYNTHETIC_QA",json.dumps(q,default=json_native),flush=True)
    if arg.synthetic_only:return
    if arg.frozen_nwi is None:raise RuntimeError("Need original frozen NWI coefficients and C-score")
    records,refs,coef,source_scope=pairmod.prior_inputs(arg.frozen_nwi)
    aug=source_augmented(records)
    arg.outdir.mkdir(parents=True,exist_ok=True)
    result={
        "analysis":"naamp_frog_same_survey_partner_stop_microclimate_noise_control_v0_1",
        "status":"posthoc_observational_sensitivity_not_biological_causation",
        "contract":"exploration/NAAMP_PARTNER_STOP_CONDITIONS_SENSITIVITY_CONTRACT_2026_10_21.md",
        "original_NWI_crossfit_workflow":SOURCE_NWI_RUN,
        "original_same_run_partner_workflow":39597933440,
        "original_geography_run":39450277196,
        "synthetic_QA":q,"source":{**source_scope,**aug},
        "method":{
           "M0":"frozen opposite-route NWI wetland plus emergent coefficients",
           "M1":"M0 predictors plus within-run local temperature, noise index and stop order; reroute-crossfit ridge=3 bounded ±3",
           "M1_unestimable_taxa_fall_back_to_M0":True,
           "fixed_row_margins":True,"fixed_column_margins":True,
           "draws":B,"seed":SEED,"B_bootstrap":BOOT,
           "new_partner_taxa_selected_after_results":False},
        "modes":{}}
    for mode in ["any","strong"]:
        train,audits=fit_all(records,mode,coef[mode])
        scores=validate_locations(records,mode,train,coef[mode])
        contrasts,scope=robust_stats(records,mode,train,coef[mode],refs[mode],{rid:int(row["SurveyYear"]) for rid,row in records.items()},arg.outdir)
        result["modes"][mode]={"fit_summary":{k:{j:v for j,v in row.items() if j!="per_taxon"}
                                            for k,row in audits.items()},
                               "heldout_location":scores,
                               "coverage":scope,"trios":contrasts}
        for name,row in contrasts.items():
            if "M1_signed_contrast_supported" in row:
                row["stop_adjusted_partner_configuration_supported"]=bool(
                    row["M1_signed_contrast_supported"] and
                    not scores["predictive_loss_supported"])
        print("STOP_CONTEXT_MODE_COMPLETE",mode,json.dumps({
           "n_original_runs":scope["original_checked_runs"],
           "n_shared_triplet_runs":scope["unique_original_selected_triple_runs"],
           "predictive_log_score_gain":scores["mean_heldout_conditional_logscore_gain"],
           "predictive_ci":scores["bootstrap_ci95"],
           "candidate_results":{name:{
               "n":v.get("n"),
               "M1_D":v.get("models",{}).get("M1",{}).get("D",{}).get("overall"),
               "M1_CP":v.get("models",{}).get("M1",{}).get("CP",{}).get("overall"),
               "M1_CN":v.get("models",{}).get("M1",{}).get("CN",{}).get("overall"),
               "supported":v.get("stop_adjusted_partner_configuration_supported")}
               for name,v in contrasts.items()}
        },sort_keys=True,default=json_native),flush=True)
    result["interpretation_boundaries"]={
      "stop_noise_and_temperature_are_contemporaneous":True,
      "crossfit_first_order_NWI_source_trained_both_time_blocks":True,
      "site_hydrology_fish_and_predator_invertebrates_unmeasured":True,
      "biological_pairwise_causation_proven":False,
      "genuine_third_order_biotic_interactions_proven":False,
      "RC6_unchanged":True}
    (arg.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True,default=json_native)+"\n")
    print("STOP_CONTEXT_PARTNER_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True,default=json_native),flush=True)
    print("STOP_CONTEXT_PARTNER_RESULT_END",flush=True)

if __name__=="__main__":
    main()
