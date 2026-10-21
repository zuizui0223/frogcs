#!/usr/bin/env python3
"""Plant (NWI PEM) x survey-month-inclusive 3-mo MODIS wetness as frog calling-site modifier.

This new *post-hoc observational* exploration deliberately preserves each taxon's
run-specific CI>=2 activation amount (k), fits on opposite routes, and applies a
fixed-row/fixed-column weighted Curveball only for the secondary checkerboard test.
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
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[1]
MIN_TRAIN_RUNS=30
MIN_TRAIN_ROUTES=12
RIDGE=3.0
LIMIT=3.0
NBOOT=2000
BOOT_SEED=2840274
SIM_SEED=2840275
BSIM=199
EARLY={2003,2005,2006,2007,2008,2009}
LATE=set(range(2010,2016))
MODELS={"H0":[0,1,2,3],"H1":[0,1,2,3,4]}
Z=1.959963984540054

def mod(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

checker=mod("frozen_nwi_check_weighted",ROOT/"exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py")
nwisource=mod("frozen_nwi_history",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
MASKS=checker.MASKS

def make_features(v4):
    v=np.asarray(v4,dtype=np.float64)
    if v.shape!=(10,4) or not np.isfinite(v).all():
        raise RuntimeError("Not exactly ten fully measured NWI/DSWE stops")
    route_three=float(v[:,3].mean())
    # Predeclared hydroperiod context × local mapped emergent cover.
    interaction=v[:,1]*route_three
    return np.column_stack([v,interaction])

def load_records(manifest,preflight):
    authority=json.loads(Path(preflight).read_text())
    if not authority.get("preflight_eligible") or authority.get("counts_outcome_file_read") is not False:
        raise RuntimeError("Outcome-blind coverage authority missing")
    if authority["eligibility"]["complete_runs"]<600 or not all(authority["gates"].values()):
        raise RuntimeError("Predeclared source gate not passed")
    manifest_lines=Path(manifest).read_text().splitlines()
    info={}
    for line in manifest_lines:
        row=json.loads(line)
        rid=str(row["RunID"])
        if rid in info:raise RuntimeError("Duplicate RunID in source-only selection")
        route=str(row["route_cluster"])
        if checker.route_fold(route)!=row["run_fold"]:
            raise RuntimeError("Holdout route hash drift")
        if len(row["stop_numbers"])!=10 or len(set(row["site_ids"]))!=10:
            raise RuntimeError("Stop/SiteID identities drift")
        v=make_features(row["v4"])
        info[rid]={"RunID":rid,"route":route,"fold":row["run_fold"],
                   "year":int(row["SurveyYear"]), "state":str(row["State"]),
                   "stop_numbers":[str(z) for z in row["stop_numbers"]],
                   "SiteIDs":[str(z) for z in row["site_ids"]],
                   "v":v}
    if len(info)!=authority["eligibility"]["complete_runs"]:
        raise RuntimeError("Preflight manifest membership drift")
    raw=nwisource.hist.load_retry()
    runs,sets=nwisource.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=nwisource.spatial.stop_matrix(raw,eligible)
    site=nwisource.hist.site_map(raw,eligible)
    ci=nwisource.hist.ci_map(raw,eligible,sampled)
    missing=set(info)-eligible
    if missing:raise RuntimeError("Source-only run selection not found in base NAAMP "+str(list(missing)[:5]))
    mode_count=Counter()
    for rid,run in info.items():
        actual_stops=sorted(sampled[rid],key=int)
        if actual_stops!=run["stop_numbers"]:
            raise RuntimeError("Stop identity changed from source-only gate")
        actual_ids=[str(site.get((rid,st))) for st in actual_stops]
        if actual_ids!=run["SiteIDs"]:
            raise RuntimeError("SiteID identity changed from source-only gate")
        act={}
        for label,thr in [("strong",2),("any",1)]:
            bytax=defaultdict(set)
            for idx,stop in enumerate(actual_stops):
                for species,cidx in ci.get((rid,stop),{}).items():
                    if cidx>=thr:bytax[str(species)].add(idx)
            act[label]=dict(bytax)
            mode_count[label+"_taxon_active_run_clusters"]+=len(bytax)
        run["act"]=act
    scope={k:int(v) for k,v in mode_count.items()}
    scope.update({"survey_runs":len(info),
                 "routes":len({x["route"] for x in info.values()}),
                 "state_count":len({x["state"] for x in info.values()}),
                 "early_runs":sum(x["year"] in EARLY for x in info.values()),
                 "late_runs":sum(x["year"] in LATE for x in info.values()),
                 "source_only_preflight_run":39518202016,
                 "NWI_overlay_run":39450277196,
                 "DSWEmod_source_run":37615425574})
    return info,scope

def conditional_training_rows(runs,mode):
    folds={"A":defaultdict(list),"B":defaultdict(list)}
    for run in runs.values():
        for species,occupied in run["act"][mode].items():
            k=len(occupied)
            if not 1<=k<=9:continue
            v=run["v"]
            obs=np.sum(v[sorted(occupied)],axis=0)
            folds[run["fold"]][species].append({
                "v":v, "obs":obs, "k":k,
                "route":run["route"],"year":run["year"]})
    return folds

def fit_exact_conditional(data,features):
    # One species, training routes only; fixed observed k in each survey.
    q=len(features)
    n=len(data)
    routes=len({x["route"] for x in data})
    # rank after within-run demeaning: prevent singular plant×water interaction.
    if n<MIN_TRAIN_RUNS or routes<MIN_TRAIN_ROUTES:
        return np.zeros(q),{"status":"ineligible","n_train":n,"routes":routes}
    X=np.concatenate([x["v"][:,features]-x["v"][:,features].mean(axis=0)
                      for x in data],axis=0)
    if np.linalg.matrix_rank(X,tol=1e-8)<q:
        return np.zeros(q),{"status":"nonidentifiable","n_train":n,"routes":routes}
    counts=np.sum([x["obs"][features] for x in data],axis=0)
    blocks=[]
    for k in range(1,10):
        batch=[z["v"][:,features] for z in data if z["k"]==k]
        if batch:
            mm=np.stack(batch)
            combos=np.einsum("mjd,sj->msd",mm,MASKS[k],optimize=True)
            blocks.append(combos)
    def fn(par):
        loss=.5*RIDGE*float(par@par)-float(par@counts)
        grad=RIDGE*par-counts.copy()
        for pts in blocks:
            eta=np.einsum("msd,d->ms",pts,par,optimize=True)
            zz=logsumexp(eta,axis=1)
            weight=np.exp(eta-zz[:,None])
            loss+=float(zz.sum())
            grad+=np.einsum("ms,msd->d",weight,pts,optimize=True)
        return loss,grad
    fit=minimize(fn,np.zeros(q,float),method="L-BFGS-B",jac=True,
                 bounds=[(-LIMIT,LIMIT)]*q,
                 options={"maxiter":100,"ftol":1e-10})
    coef=np.asarray(fit.x,float)
    if not fit.success or not np.isfinite(coef).all():
        return np.zeros(q),{"status":"fit_fail_closed","n_train":n,"routes":routes,
                             "message":str(fit.message)[:120]}
    return coef,{"status":"fitted","n_train":n,"routes":routes,
                 "coef":coef.tolist(),"iterations":int(fit.nit)}

def train_models(rows,fold=None,early_only=False):
    groups=defaultdict(list)
    for sp,values in rows.items():
        z=[x for x in values if (not early_only or x["year"] in EARLY)]
        groups[sp]=z
    coefs={}
    diagnostics={}
    for sp in sorted(groups):
        z=groups[sp]
        pars={}
        audits={}
        for name,idx in MODELS.items():
            coef,audit=fit_exact_conditional(z,idx)
            pars[name]=coef
            audits[name]=audit
        coefs[sp]=pars
        diagnostics[sp]=audits
    summary={
        "taxa_training":len(groups),
        "eligible_taxa_H0":sum(v["H0"]["status"]=="fitted" for v in diagnostics.values()),
        "eligible_taxa_H1":sum(v["H1"]["status"]=="fitted" for v in diagnostics.values()),
        "H1_positive_interactions":sum(v["H1"]["status"]=="fitted" and coefs[sp]["H1"][-1]>0
                                     for sp,v in diagnostics.items()),
        "H1_negative_interactions":sum(v["H1"]["status"]=="fitted" and coefs[sp]["H1"][-1]<0
                                     for sp,v in diagnostics.items()),
        "time_training_early_only":early_only,
        "trained_fold":fold
    }
    return coefs,summary,diagnostics

def model_for_run(run,by_train):
    return by_train[checker.complementary(run["fold"])]

def logprob_site(v,occupied,theta,idx):
    k=len(occupied)
    if not 1<=k<=9:raise ValueError("Non-informative fixed-k")
    pred=v[:,idx]@theta
    return float(pred[sorted(occupied)].sum() -
                 logsumexp(MASKS[k]@pred))

def heldout_logscore(records,mode,params,only_late=False):
    rows=[]
    for rid,run in records.items():
        if only_late and run["year"] not in LATE:continue
        trained=params if only_late else model_for_run(run,params)
        for sp,occupied in run["act"][mode].items():
            if not 1<=len(occupied)<=9:continue
            p=trained.get(sp,{})
            h0=p.get("H0",np.zeros(4,float))
            h1=p.get("H1",np.zeros(5,float))
            ll0=logprob_site(run["v"],occupied,h0,MODELS["H0"])
            ll1=logprob_site(run["v"],occupied,h1,MODELS["H1"])
            rows.append({"RunID":rid,"route":run["route"],"fold":run["fold"],
                         "year":run["year"],"taxon":sp,
                         "log_H0":ll0,"log_H1":ll1,"increment":ll1-ll0})
    df=pd.DataFrame(rows)
    return df

def route_bootstrap(df,seed):
    if df.empty:return {"status":"no_information"}
    route=df.groupby("route").increment.agg(["sum","size"])
    n=len(route)
    sums=route["sum"].to_numpy(float)
    counts=route["size"].to_numpy(float)
    idx=np.random.default_rng(seed).integers(0,n,size=(NBOOT,n))
    vals=sums[idx].sum(axis=1)/counts[idx].sum(axis=1)
    avg=float(df.increment.mean())
    ci=[float(z) for z in np.quantile(vals,[.025,.975])]
    return {"status":"fitted","n_taxon_runs":len(df),"n_routes":n,
            "n_taxa":int(df.taxon.nunique()),
            "heldout_mean_increment_nats_per_taxon_run":avg,
            "route_bootstrap_95ci":ci,"positive_ci":bool(ci[0]>0),
            "bootstrap_replicates":NBOOT,
            "fold_mean":{str(f):float(g.increment.mean()) for f,g in df.groupby("fold")},
            "n_pre2010":int(df.year.isin(EARLY).sum()),
            "n_late":int(df.year.isin(LATE).sum())}

def fixed_margin_checkerboard(runs,reference,params,mode="strong"):
    ref=pd.read_csv(reference,dtype={"RunID":str})
    needed={"RunID","observed_cscore","null_mean","null_sd"}
    if not needed.issubset(ref.columns):
        raise RuntimeError("Required frozen C-score fields missing")
    if ref.RunID.duplicated().any():raise RuntimeError("Duplicate frozen C-score RunID")
    ref=ref.set_index("RunID",drop=False)
    ids=sorted(set(runs)&set(ref.index))
    if len(ids)<300 or len({runs[r]["route"] for r in ids})<60:
        raise RuntimeError(f"Checkerboard insufficient eligible sample {len(ids)}")
    global_null={"H0":np.zeros(BSIM,float),"H1":np.zeros(BSIM,float)}
    notes={m:[] for m in MODELS}
    outputs=[]
    for i,rid in enumerate(ids,1):
        run=runs[rid]
        taxa=sorted(run["act"][mode])
        rows=[run["act"][mode][sp] for sp in taxa]
        if not checker.exchangeable(rows):
            raise RuntimeError("Matched C-score source contains a nonexchangeable matrix")
        obs=checker.cscore(rows)
        prior=ref.loc[rid]
        if not np.isclose(obs,float(prior.observed_cscore),atol=1e-8,rtol=0):
            raise RuntimeError(f"Frozen C-score reference drift {rid}, stop/order/schema mismatch")
        trained=model_for_run(run,params)
        record={"rid":rid,"route":run["route"],"fold":run["fold"],
                "observed":obs,"baseline":float(prior.null_mean),
                "baseline_residual":obs-float(prior.null_mean)}
        for name,idx in MODELS.items():
            theta=np.stack([trained.get(sp,{}).get(name,np.zeros(len(idx)))
                            for sp in taxa],axis=0)
            score=theta@run["v"][:,idx].T
            seed=int.from_bytes(hashlib.sha256(f"{SIM_SEED}|{name}|{rid}".encode()).digest()[:8],"big")
            rnd=random.Random(seed)
            draws,stats=checker.fixed_margin_sampler(rows,score,rnd)
            record[name+"_expected"]=float(draws.mean())
            record[name+"_residual"]=obs-float(draws.mean())
            record[name+"_mixed"]=int(float(prior.null_sd)>1e-8 and stats["n_distinct_cscore_draws"]>1)
            record[name+"_unmixed"]=int(float(prior.null_sd)>1e-8 and stats["n_distinct_cscore_draws"]<2)
            notes[name].append(stats)
            global_null[name]+=draws
        record["interaction_increase_expected"]=record["H1_expected"]-record["H0_expected"]
        outputs.append(record)
        if i%250==0:
            print(f"Checkerboard: {i}/{len(ids)} matrices verified and simulated",flush=True)
    df=pd.DataFrame(outputs)
    def mean_se(field):
        fit=sm.OLS(df[field].to_numpy(float),np.ones((len(df),1))).fit(
            cov_type="cluster",cov_kwds={"groups":df.route})
        b=float(fit.params[0]); se=float(fit.bse[0])
        return {"estimate":b,"route_se":se,"ci95":[b-Z*se,b+Z*se],
                "p_two_sided":float(fit.pvalues[0])}
    result={"heldout_checkerboard_runs":len(df),"routes":int(df.route.nunique()),
            "observed_Cscore":float(df.observed.mean()),
            "baseline_Cscore":float(df.baseline.mean()),
            "reference_fixed_fixed_excess":mean_se("baseline_residual"),
            "H0_additive_excess":mean_se("H0_residual"),
            "H1_plant_x_water_excess":mean_se("H1_residual"),
            "plant_x_water_expected_Cscore_increment":mean_se("interaction_increase_expected"),
            "folds":{f:{"n_runs":len(g),"routes":int(g.route.nunique()),
                         "mean_expected_gain":float(g.interaction_increase_expected.mean()),
                         "H1_mean_residual":float(g.H1_residual.mean())}
                     for f,g in df.groupby("fold")}}
    for name in MODELS:
        distribution=global_null[name]/len(df)
        info=int((ref.loc[ids].null_sd.astype(float)>1e-8).sum())
        flat=int(df[name+"_unmixed"].sum())
        result[name]={
            "null_Cscore_mean":float(distribution.mean()),
            "null_95ci":[float(x) for x in np.quantile(distribution,[.025,.975])],
            "upper_tail_plus_one_P":float((1+np.sum(distribution>=df.observed.mean()))/(BSIM+1)),
            "reference_informative_matrices":info,
            "unmixed_matrices":flat,
            "fraction_unmixed":flat/info if info else None,
            "sampling_unreliable":bool(info and flat/info>.2),
            "mean_accepted_fraction_given_feasible":float(np.mean([x["accepted_given_feasible"] for x in notes[name]]))}
    return df,result

def selftests():
    old=checker.synth_test()
    w=np.arange(40,dtype=float).reshape(10,4)/100
    mat=make_features(w)
    assert mat.shape==(10,5)
    assert np.allclose(mat[:,4],mat[:,1]*mat[:,3].mean())
    assert np.allclose(
        logprob_site(mat,{0,2,4},np.asarray([.1,-.2,.3,.4]),[0,1,2,3]),
        logprob_site(mat,{0,2,4},np.asarray([.1,-.2,.3,.4,0.]),[0,1,2,3,4]),
        atol=1e-9
    )
    return {"weighted_Curveball":old,"interaction_algebra":"PASS",
            "H1_reduces_to_H0_at_zero_interaction":"PASS"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-manifest",type=Path)
    parser.add_argument("--preflight",type=Path)
    parser.add_argument("--reference-strong",type=Path)
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"plant_wetness_joint")
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    tests=selftests()
    print("PLANT_WETNESS_SYNTHETIC_QA",json.dumps(tests,sort_keys=True),flush=True)
    if args.synthetic_only:return
    if not(args.source_manifest and args.preflight and args.reference_strong):
        raise SystemExit("Missing response-blind source manifest, preflight or frozen checkerboard reference")
    records,scope=load_records(args.source_manifest,args.preflight)
    training=conditional_training_rows(records,"strong")
    params={}
    trained={}
    for fold in ("A","B"):
        coef,summ,details=train_models(training[fold],fold=fold)
        params[fold]=coef
        trained[fold]=summ
        print("CROSSFIT_TRAIN_COMPLETE",fold,json.dumps(summ,sort_keys=True),flush=True)
    route_scores=heldout_logscore(records,"strong",params)
    route_result=route_bootstrap(route_scores,BOOT_SEED)
    # Temporal training uses only early-year survey responses.
    # The fitted classifier can be applied to later years on overlapping
    # routes, but this does not repair satellite survey-month data leakage.
    all_early=defaultdict(list)
    for folddict in training.values():
        for sp,lst in folddict.items():
            all_early[sp].extend(z for z in lst if z["year"] in EARLY)
    early_params,early_info,early_diag=train_models(all_early,fold="all_early_2003_2009",early_only=True)
    future_scores=heldout_logscore(records,"strong",early_params,only_late=True)
    temporal_result=route_bootstrap(future_scores,BOOT_SEED+1)
    df,cb=fixed_margin_checkerboard(records,args.reference_strong,params)
    # Fails closed for sample artifacts or inaccessible original route data
    # before a biological claim is calculated.
    if len(df)<300 or cb["H1"]["sampling_unreliable"]:
        raise RuntimeError("Insufficient C-score population or weighted null sampling reliability")
    classification={
        "route_heldout_interaction_prediction_supported":bool(route_result["positive_ci"]),
        "temporal_transfer_supported":bool(temporal_result["positive_ci"]),
        "H1_increases_checkerboard_expected_over_H0":bool(cb["plant_x_water_expected_Cscore_increment"]["ci95"][0]>0),
        "H1_adjusted_checkerboard_excess_remains":bool(cb["H1_plant_x_water_excess"]["ci95"][0]>0),
        "full_checkerboard_explanation":bool(
            route_result["positive_ci"]
            and cb["plant_x_water_expected_Cscore_increment"]["ci95"][0]>0
            and cb["H1_plant_x_water_excess"]["ci95"][0]<=0
            and cb["H1"]["null_95ci"][0]<=cb["observed_Cscore"]<=cb["H1"]["null_95ci"][1])
    }
    output={
        "analysis":"naamp_NWI_PEM_x_DSWEmod_survey_month_wetness_v0_1",
        "contract":"exploration/NAAMP_PLANT_WETNESS_INTERACTION_CONTRACT_2026_10_21.md",
        "status":"posthoc_exploratory_no_RC6_reopening",
        "synthetic_QA":tests,
        "source_coverage":scope,
        "fit_summary":{"route_fold_training":trained,
                       "early_only":early_info},
        "route_heldout_strong_chorus_location":route_result,
        "strict_year_holdout_strong_chorus_location":temporal_result,
        "checkerboard_same_run_fixed_fixed":cb,
        "classification":classification,
        "boundaries":{
            "recent3_includes_survey_month":True,
            "recent3_may_use_post_survey_satellite_observations":True,
            "NWI_mapped_PEM_not_historic_plant_measurement":True,
            "historical_DSWEmod_temporal_readiness_prediction_failed":True,
            "frog_occupation_or_spawning_inferred":False,
            "species_competition_identified":False,
            "water_depth_or_water_under_vegetation_measured":False,
            "RC6_science_or_submission_modified":False}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    df.to_csv(args.outdir/"checkerboard_per_run.csv",index=False)
    route_scores.to_csv(args.outdir/"route_heldout_taxon_run_scores.csv",index=False)
    future_scores.to_csv(args.outdir/"time_heldout_taxon_run_scores.csv",index=False)
    print("PLANT_WETNESS_INTERACTION_RESULT_BEGIN",flush=True)
    print(json.dumps(output,sort_keys=True),flush=True)
    print("PLANT_WETNESS_INTERACTION_RESULT_END",flush=True)

if __name__=="__main__":
    main()
