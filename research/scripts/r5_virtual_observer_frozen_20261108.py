"""R5 original-source virtual observer test. Protocol frozen before simulation outcomes.
See research/R5_VIRTUAL_ECOLOGIST_OBSERVABILITY_FROZEN_PROTOCOL_2026-11-08.md.
One complete scenario per shard: 100 generated strong-call site-count datasets.
This tests conditional identifiability, NOT real pond predator effects.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from acoustic_mechanism_cv import (
    RIDGE, N_FOLDS, BACKGROUNDS, log_score, train_predict
)
from g14_abc_ensemble_geographic_acoustic_holdout import read_field
from g5_source_constrained_acoustic_holdout_20261106 import (
    read_corner_source, constrained_train_predict, features_by_background
)
from g4_field_model_alignment_8corner_audit_20261106 import (
    original_rank01, predictor_basis
)

SEED = 20261108
REPS = 100
N_BOOT = 999
N_BLOCK = 56
N_SITES = 4248
N_VISITS = 63180
N_STRONG = 36554
N_VEG = 506
MODELS = ("flex_add", "flex_all", "source_00", "source_11")
GAMMAS = (0.0, 0.25, 1.0)
FLIPS = (0.0, 0.25)
ARMS = ("00", "11")
N_EXPECTED_SCENARIOS = 24

def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)

def seed_for(*tokens):
    h = hashlib.sha256("|".join(map(str,(SEED,)+tokens)).encode()).digest()
    return int.from_bytes(h[:8],"little")

def scenario_name(bg, arm, gamma, flip):
    return "truth-"+bg+"_arm-"+arm+"_gamma-"+str(gamma).replace(".","p")+"_Vflip-"+str(flip).replace(".","p")

def all_scenarios():
    return list(itertools.product(BACKGROUNDS, ARMS, GAMMAS, FLIPS))

def scale(train, test):
    mu, sd = train.mean(axis=0), train.std(axis=0)
    ok = sd > 1e-12
    require(np.any(ok), "All field predictors constant")
    a = np.column_stack((np.ones(len(train)), (train[:,ok]-mu[ok])/sd[ok]))
    b = np.column_stack((np.ones(len(test)), (test[:,ok]-mu[ok])/sd[ok]))
    require(np.isfinite(a).all() and np.isfinite(b).all(),"Invalid standardized field matrix")
    return a, b

def optimizer_predict(z,t,k,n,constrained):
    """Numerical implementation of frozen G5/R1 ridge-binomial fit;
    G5 same optimizer/penalty, including positive LAST source slope."""
    p0 = np.clip(np.sum(k)/np.sum(n), 1e-6, 1-1e-6)
    initial = np.zeros(z.shape[1], dtype=float)
    initial[0] = np.log(p0/(1-p0))
    def objective(coef):
        lin = z@coef
        loss = np.logaddexp(0,lin)@n - lin@k + RIDGE*(coef[1:]@coef[1:])/2
        grad = z.T@(n*expit(lin)-k)
        grad[1:] += RIDGE*coef[1:]
        return float(loss), grad
    bounds = ([(None,None)]*(len(initial)-1)+[(0,None)]) if constrained else None
    result = minimize(
        objective, initial, jac=True, method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter":650 if constrained else 500, "ftol":1e-11},
    )
    grad_limit = .15 if constrained else .1
    require(result.success or np.linalg.norm(result.jac,ord=np.inf)<grad_limit,
            "Frozen fit convergence failure: "+str(result.message))
    if constrained:
        require(result.x[-1]>=-1e-12,"Nonnegative original source slope inverted")
    return np.clip(expit(t@result.x),1e-10,1-1e-10), (
        float(result.x[-1]) if constrained else float("nan")
    )

def construct_designs(d, folds, source):
    prep = {}
    for bg in BACKGROUNDS:
        mat, features = features_by_background(d,bg,source)
        full = {
            "flex_add":np.asarray(mat["flex_add"],float),
            "flex_all":np.asarray(mat["flex_all"],float),
            "source_00":np.column_stack((mat["flex_add"],features["00"])),
            "source_11":np.column_stack((mat["flex_add"],features["11"])),
        }
        for fold in range(N_FOLDS):
            train = folds != fold
            test = folds == fold
            require(train.sum()>2000 and test.sum()>100,"Missing frozen geo-fold support")
            for name in MODELS:
                z,t=scale(full[name][train],full[name][test])
                prep[(bg,fold,name)] = (z,t,train,np.flatnonzero(test))
    return prep

def fit_all_cv(k,n,prep):
    fitted={}
    for bg in BACKGROUNDS:
        pred={name:np.zeros(len(n),float) for name in MODELS}
        slopes={name:[] for name in ("source_00","source_11")}
        for fold in range(N_FOLDS):
            for name in MODELS:
                z,t,train,ix = prep[(bg,fold,name)]
                p,slope = optimizer_predict(
                    z,t,np.asarray(k[train],float),np.asarray(n[train],float),
                    name.startswith("source_")
                )
                pred[name][ix]=p
                if name in slopes:slopes[name].append(slope)
        for name in MODELS:
            require(np.isfinite(pred[name]).all() and np.min(pred[name])>0
                    and np.max(pred[name])<1,"Out-of-fold prediction incomplete")
        fitted[bg]=(pred,slopes)
    return fitted

def verify_solver_equivalence(d,folds,source,prep):
    """Original code versus pre-standardized cache, on genuine frozen k/n."""
    bg="uniform";fold=0;name="flex_add"
    k=d.k.to_numpy(float); n=d.n.to_numpy(float)
    z,t,train,ix=prep[(bg,fold,name)]
    x=features_by_background(d,bg,source)[0]["flex_add"]
    original=train_predict(x[train],k[train],n[train],x[ix],ridge=RIDGE)
    ours,_=optimizer_predict(z,t,k[train],n[train],False)
    require(np.max(np.abs(original-ours))<1e-7,
            "R5 accelerated null model does not match original G5/R1 solver")
    name="source_11"
    z,t,train,ix=prep[(bg,fold,name)]
    matrices,features=features_by_background(d,bg,source)
    x=np.column_stack((matrices["flex_add"],features["11"]))
    original,orig_slope=constrained_train_predict(
        x[train],k[train],n[train],x[ix],ridge=RIDGE)
    ours,slope=optimizer_predict(z,t,k[train],n[train],True)
    require(np.max(np.abs(original-ours))<1e-7
            and abs(orig_slope-slope)<1e-6,
            "R5 cached source predictor does not match original G5")
    return True

def original_environment_baseline(d, bg):
    """Original data only inform a FIXED environmental nuisance in simulations."""
    mats=features_by_background(d,bg,_SOURCES)[0]
    x=mats["flex_add"]
    return train_predict(x,d.k.to_numpy(float),d.n.to_numpy(float),x,ridge=RIDGE)

_SOURCES = None

def virtual_true_signal(d, source, bg,arm, flip):
    o=original_rank01(d["mean_suitability_Odonata_"+bg])
    s=original_rank01(d["mean_suitability_pond_breeding_Caudata_"+bg])
    v=d.V.to_numpy(float).copy()
    if flip>0:
        rng=np.random.default_rng(seed_for("vegetation-mask"))
        nflip=int(round(flip*len(v)))
        indices=rng.permutation(len(v))[:nflip]
        v[indices]=1-v[indices]
        require(int((v!=d.V.to_numpy(float)).sum())==nflip,
                "Frozen response-blind V error mask changed")
    x=predictor_basis(o,s,v)
    # Only the four *interaction* terms are allowed in adult-call operator,
    # matching G5 source basis. Main effects remain in fixed environmental p0.
    phi=x[:,4:]@source[arm][4:]
    sd=float(np.std(phi))
    require(sd>1e-9,"Original source interaction shape has no variation")
    z=(phi-float(np.mean(phi)))/sd
    return z, dict(
        rank_truth=bg, arm_truth=arm, proposed_V_mismatch=flip,
        true_site_veg_positive=int(np.sum(v)),original_proxy_veg_positive=int(d.V.sum()),
        true_source_log_interaction_sd=sd,
        original_source_vertex_sha256="G4-genuine-256x3-eightcorner",
        observational_gamma_is_hypothetical=True,
    )

def logloss_by_block(k,n,p,block_ix):
    losses=log_score(k,n,p)
    return np.bincount(block_ix,weights=losses,minlength=N_BLOCK)

def intervals_for_models(k,n, predictions, block_ix, bootstrap_ix):
    block_n=np.bincount(block_ix, weights=n,minlength=N_BLOCK)
    require(len(block_n)==N_BLOCK and block_n.sum()==N_VISITS,"Block weights changed")
    losses={name:logloss_by_block(k,n,p,block_ix) for name,p in predictions.items()}
    out={}
    for left,right,label in [
        ("flex_add","source_11","source11_gain_over_flexadd"),
        ("source_00","source_11","source11_gain_over_source00"),
        ("flex_all","source_11","source11_gain_over_flexall"),
        ("flex_add","source_00","source00_gain_over_flexadd")
    ]:
        difference=losses[left]-losses[right]
        all_gain=float(difference.sum()/N_VISITS)
        draw_gain=difference[bootstrap_ix].sum(axis=1)/block_n[bootstrap_ix].sum(axis=1)
        lo,hi=np.quantile(draw_gain,[.025,.975])
        out[label]=all_gain
        out[label+"_low"]=float(lo)
        out[label+"_high"]=float(hi)
    for name in MODELS:
        out["nll_"+name]=float(losses[name].sum()/N_VISITS)
    return out

def evaluate(k,n,prep,block_ix,bootstrap_ix,scenario,repl,oracle=False):
    fitted=fit_all_cv(k,n,prep)
    results=[]
    for evalbg in BACKGROUNDS:
        preds,slopes=fitted[evalbg]
        row={
            **scenario,"replicate":repl,
            "observer_background":evalbg,
            "rank_background_matches_truth":bool(evalbg==scenario["true_background"]),
            "oracle_fractional_calls":bool(oracle),
            **intervals_for_models(k,n,preds,block_ix,bootstrap_ix)
        }
        row["source11_recovered"] = bool(
            row["source11_gain_over_flexadd_low"]>0
            and row["source11_gain_over_source00_low"]>0
        )
        row["source00_favors_over_11"] = bool(
            row["source11_gain_over_source00_high"]<0
        )
        row["source11_all_5fold_slopes_positive"] = bool(
            sum(x>1e-6 for x in slopes["source_11"])==5
        )
        results.append(row)
    return results

def scenario_run(args):
    global _SOURCES
    source_path=Path(args.source)
    d,folds=read_field()   # exact pinned original site/visit SHA, counts and folds
    _SOURCES=read_corner_source(source_path)
    require(int(d.n.sum())==N_VISITS and int(d.k.sum())==N_STRONG
            and d.V.sum()==N_VEG and d.spatial_block.nunique()==N_BLOCK
            and d.route.nunique()==432,"Frozen original field denominators changed")
    require(args.truth_bg in BACKGROUNDS and args.arm in ARMS
            and args.gamma in GAMMAS and args.flip in FLIPS,
            "Only preregistered scenarios permitted")
    require(args.reps==REPS,"Fixed 100 replicates per scenario cannot be reduced")
    prep=construct_designs(d,folds,_SOURCES)
    require(verify_solver_equivalence(d,folds,_SOURCES,prep),
            "Frozen model solver source check failure")
    baseline=original_environment_baseline(d,args.truth_bg)
    phi,src=virtual_true_signal(d,_SOURCES,args.truth_bg,args.arm,args.flip)
    n=d.n.to_numpy(dtype=int)
    p=np.clip(expit(np.log(baseline/(1-baseline))+args.gamma*phi),1e-8,1-1e-8)
    rng=np.random.default_rng(seed_for("responses",args.truth_bg,args.arm,args.gamma,args.flip))
    labels=sorted(d.spatial_block.unique())
    block_ix=np.array(pd.Categorical(d.spatial_block,categories=labels).codes)
    require(set(block_ix)==set(range(N_BLOCK)),"Original geographic 56-block identity lost")
    bootstrap_ix=np.random.default_rng(seed_for("boot",args.truth_bg,args.arm,args.gamma,args.flip)).integers(
        0,N_BLOCK,size=(N_BOOT,N_BLOCK)
    )
    scenario={
        "true_background":args.truth_bg,
        "true_source_arm":args.arm,
        "gamma":args.gamma,"pond_V_flip":args.flip,
    }
    rows=[]
    # Expected-response oracle: no binomial acoustic sampling, identical sites/folds;
    # reflects assumed gamma link, never direct evidence about nature.
    oracle=evaluate(n*p,n,prep,block_ix,bootstrap_ix,scenario,-1,oracle=True)
    for rep in range(REPS):
        k=rng.binomial(n,p)
        rows.extend(evaluate(k,n,prep,block_ix,bootstrap_ix,scenario,rep))
    require(len(rows)==REPS*len(BACKGROUNDS),"R5 did not complete all fixed replicates")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    name=scenario_name(args.truth_bg,args.arm,args.gamma,args.flip)
    csv=out/(name+"_all_replicates.csv")
    pd.DataFrame(rows).to_csv(csv,index=False,float_format="%.12g")
    summary={
        "status":"R5_FROZEN_VIRTUAL_OBSERVER_SCENARIO_COMPLETE",
        "scenario":scenario,"scenario_id":name,
        "replicate_count":REPS,"observer_backgrounds":list(BACKGROUNDS),
        "original_sites":N_SITES,"original_visits":N_VISITS,
        "original_blocks":N_BLOCK,"original_vegetated_sites":N_VEG,
        "source_detail":src,
        "original_G14_field_and_G4_source_replayed":True,
        "original_R1_G5_solver_equivalence_passed":True,
        "expected_oracle_call_fractional_counts":oracle,
        "scenario_stochastic_seed":seed_for("responses",args.truth_bg,args.arm,args.gamma,args.flip),
        "simulated_adult_acoustic_visits_only":True,
        "real_natural_pond_mechanism_identified":False,
        "field_causes_of_G14_failure_established":False,
        "result_file":csv.name,
        "source_file_sha256":hashlib.sha256(source_path.read_bytes()).hexdigest(),
    }
    jpath=out/(name+"_scenario_receipt.json")
    jpath.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print("R5_SCENARIO_COMPLETE",name,len(rows),"original source verified",flush=True)

def wilson(count,n,z=1.96):
    p=count/n
    den=1+z*z/n
    mid=(p+z*z/(2*n))/den
    err=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(mid-err),float(mid+err)]

def aggregate(args):
    root=Path(args.input)
    receipts=sorted(root.rglob("truth-*_scenario_receipt.json"))
    require(len(receipts)==N_EXPECTED_SCENARIOS,
            "R5 incomplete: 24 fixed scenarios required; found "+str(len(receipts)))
    all_data=[];oracle=[];receipt_rows=[]
    expected={scenario_name(*c) for c in all_scenarios()}
    seen=set()
    for f in receipts:
        q=json.loads(f.read_text())
        require(q["status"]=="R5_FROZEN_VIRTUAL_OBSERVER_SCENARIO_COMPLETE"
                and q["replicate_count"]==REPS
                and q["original_sites"]==N_SITES and q["original_visits"]==N_VISITS
                and q["original_blocks"]==N_BLOCK
                and q["original_G14_field_and_G4_source_replayed"]
                and q["original_R1_G5_solver_equivalence_passed"],
                "R5 source or 100-replicate completeness gate failed")
        name=q["scenario_id"]
        require(name not in seen and name in expected,"Duplicate/unknown R5 scenario")
        seen.add(name)
        df=pd.read_csv(f.parent/q["result_file"])
        require(len(df)==200 and df.replicate.nunique()==100,
                "Source scenario lacks all both-background 100 replicates")
        require(set(df.observer_background)==set(BACKGROUNDS)
                and not df.duplicated(["replicate","observer_background"]).any(),
                "Per-simulation heldout outcome incomplete")
        for c in ("source11_gain_over_flexadd","source11_gain_over_source00",
                  "source11_gain_over_flexall"):
            require(np.isfinite(df[c]).all(),"R5 cannot pool partial/nonfinite results")
        all_data.append(df.assign(scenario_id=name))
        oracle += [dict(scenario_id=name,**v) for v in q["expected_oracle_call_fractional_counts"]]
        receipt_rows.append(q)
    require(seen==expected,"R5 missing fixed scenarios")
    full=pd.concat(all_data,ignore_index=True)
    require(len(full)==N_EXPECTED_SCENARIOS*REPS*len(BACKGROUNDS),
            "R5 4800 scenario×replicate×observer outcomes incomplete")
    table=[]
    for key,g in full.groupby(
        ["true_background","true_source_arm","gamma","pond_V_flip","observer_background"],sort=True):
        label=dict(zip(["true_background","true_source_arm","gamma","pond_V_flip","observer_background"],key))
        rec=int(g.source11_recovered.sum())
        row={**label,"n_replicates":len(g),
             "source11_recovery":rec/len(g),
             "source11_recovery_Wilson95_low":wilson(rec,len(g))[0],
             "source11_recovery_Wilson95_high":wilson(rec,len(g))[1],
             "source00_beats11_fraction":float(g.source00_favors_over_11.mean()),
             "mean_source11_vs_additive_gain":float(g.source11_gain_over_flexadd.mean()),
             "mean_source11_vs_off_gain":float(g.source11_gain_over_source00.mean()),
             "mean_source11_vs_saturated_gain":float(g.source11_gain_over_flexall.mean())}
        table.append(row)
    t=pd.DataFrame(table)
    require(len(t)==48 and t.n_replicates.eq(REPS).all(),"Aggregated scenario table incomplete")
    # No arbitrary selection; primary matching-background ON truth comparisons only.
    main=t[(t.true_source_arm=="11") &
           (t.true_background==t.observer_background)].sort_values(
        ["true_background","gamma","pond_V_flip"])
    # Explicit finite Monte Carlo uncertainty of power difference via paired replicate seeds
    # is not promised because response streams for different scenarios are independent.
    diagnostic={
        "negative_control":t[t.gamma==0].to_dict("records"),
        "true_on_matching_background":main.to_dict("records"),
        "overall_scenarios":len(receipts),
        "all_replicate_observer_scores":len(full),
        "original_source_models_rerun":0,
        "real_pond_mechanism_identified":False,
        "actual_cause_of_original_field_failure_proven":False,
    }
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    full.to_csv(out/"R5_all_4800_original_fold_observer_results.csv",index=False)
    t.to_csv(out/"R5_complete_48_world_observer_recovery_summary.csv",index=False)
    pd.DataFrame(oracle).to_csv(out/"R5_expected_call_oracle_48_rows.csv",index=False)
    (out/"R5_FULL_FIXED_PROSPECTIVE_SOURCE_AUDIT.json").write_text(json.dumps({
        "status":"R5_FULL_24_SCENARIOS_COMPLETE",
        "source": "pre-outcome R5 freeze 2026-11-08",
        "scenario_ids":sorted(seen),
        "gamma":GAMMAS,"V_error":FLIPS,
        "real_unreported_larval_call_link":True,
        "n_scenarios":len(receipts),
        "n_simulated_field_outcomes":N_EXPECTED_SCENARIOS*REPS,
        "n_original_field_sites":N_SITES,
        "n_original_completed_visits":N_VISITS,
        "n_original_geographic_blocks":N_BLOCK,
        "all_replicates_reported_including_failures":True,
        "primary":diagnostic,
    },indent=2)+"\n")
    print("R5_FULL_24_SCENARIOS_COMPLETE",
          "observer_rows",len(full),"summary_cells",len(t),flush=True)
    print("R5_ON_TRUTH_MATCHING_BG\n"+main.to_string(index=False),flush=True)
    print("R5_OBSERVATION_DIAGNOSTIC_NOT_NATURAL_MECHANISM_IDENTIFICATION",flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("scenario","aggregate"),required=True)
    p.add_argument("--source",type=Path)
    p.add_argument("--truth-bg",choices=BACKGROUNDS)
    p.add_argument("--arm",choices=ARMS)
    p.add_argument("--gamma",type=float)
    p.add_argument("--flip",type=float)
    p.add_argument("--reps",type=int,default=REPS)
    p.add_argument("--input",type=Path)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.mode=="scenario":
        require(args.source and args.truth_bg and args.arm and args.gamma is not None
                and args.flip is not None,"Missing fixed scenario")
        scenario_run(args)
    else:
        require(args.input,"Missing all 24 prospective scenario artifacts")
        aggregate(args)

if __name__ == "__main__":
    main()
