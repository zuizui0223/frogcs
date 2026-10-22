#!/usr/bin/env python3
"""Partner identity as out-of-route predictor of frog site allocation under exact margins.

Each pseudolikelihood event reallocates exclusive sites between central frog C
and one nonfocal active frog j. This leaves every row sum and stop richness
fixed, while held-out partner rows P,N do not change.

The original NWI weights are trained on opposite routes; historical
species-SiteID scores are constructed from strictly prior YEARS only. The
study is observational, post-selected and outside the frozen JAE RC6 paper.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.special import logsumexp
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
PENALTY=3.
BOUND=3.
BOOT=2000
SEED=2840327
Z=1.959963984540054
CENTRAL="Lithobates clamitans"
POSITIVE="Lithobates catesbeianus"
NEGATIVES=("Anaxyrus fowleri","Hyla versicolor")
FEATURE_LABELS=("generic_other_taxa","positive_partner","negative_partner")
MODEL_COLS={"M0_generic_richness":[0],"M_P_positive_partner":[0,1],"M1_plus_partner_identity":[0,1,2]}
BASE_ANY=3659
BASE_STRONG=1766
CACHE={}

def importmodule(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module

pairmod=importmodule("choice_from_fixed_NWI",ROOT/"exploration/run_naamp_plant_conditioned_pair_network_v0_1.py")
prior=pairmod.prior
histmod=importmodule("choice_from_prior_SiteID",ROOT/"exploration/run_naamp_same_run_prior_site_history_null_v0_1.py")
ecology=histmod.ecology

def choose_mask(n,k):
    key=(int(n),int(k))
    if key not in CACHE:
        subset=list(itertools.combinations(range(n),k))
        m=np.zeros((len(subset),n),float)
        for ix,sites in enumerate(subset):
            m[ix,list(sites)]=1.
        CACHE[key]=m
    return CACHE[key]

def exact_event(rows,central_index,opponent_index,positive_index,negative_index,offsets):
    ci=int(central_index);j=int(opponent_index)
    ip=int(positive_index);ineg=int(negative_index)
    assert len({ci,j,ip,ineg})==4
    unique_C=rows[ci]-rows[j]
    unique_j=rows[j]-rows[ci]
    if not unique_C or not unique_j:
        return None
    pool=sorted(unique_C|unique_j)
    m=len(pool);k=len(unique_C)
    assert 2<=m<=10 and 1<=k<m
    mask=choose_mask(m,k)
    if mask.shape[0]>252:raise RuntimeError("Unexpected cardinality of exact conditional row-swap sample")
    base=(offsets[ci]-offsets[j])[pool]
    nonfocal=[t for t in range(len(rows)) if t not in {ci,j,ip,ineg}]
    generic=np.asarray([sum(site in rows[t] for t in nonfocal) for site in pool],float)
    xP=np.asarray([int(site in rows[ip]) for site in pool],float)
    xN=np.asarray([int(site in rows[ineg]) for site in pool],float)
    site_matrix=np.column_stack([base,generic,xP,xN])
    candidates=mask@site_matrix
    obs_mask=np.asarray([float(site in unique_C) for site in pool],float)
    obs=obs_mask@site_matrix
    if obs_mask.sum()!=k:raise RuntimeError("Observed C-only sites lost identity")
    return {
        "candidates_base":candidates[:,0],
        "candidates_features":candidates[:,1:],
        "obs_base":float(obs[0]),
        "obs_features":obs[1:],
        "n_candidate_sets":int(len(candidates)),
        "variable_P":bool(np.ptp(candidates[:,2])>1e-12),
        "variable_N":bool(np.ptp(candidates[:,3])>1e-12),
        "variable_generic":bool(np.ptp(candidates[:,1])>1e-12)
    }

def assert_same_margins_candidate():
    rows=[{0,2,4},{1,2,5},{3,4,5},{0,6},{1,7}]
    fixed=prior.fixed_margins(rows)
    base=np.zeros((len(rows),10))
    q=exact_event(rows,0,3,1,2,base)
    if q is None:raise RuntimeError("Synthetic exact-swap event lacks candidates")
    cset=q["n_candidate_sets"]
    assert cset==math.comb(len((rows[0]-rows[3])|(rows[3]-rows[0])),len(rows[0]-rows[3]))
    pool=sorted((rows[0]-rows[3])|(rows[3]-rows[0]))
    common=rows[0]&rows[3]
    initial_i=len(rows[0]-rows[3])
    for mask in choose_mask(len(pool),initial_i):
        x={pool[j] for j,flag in enumerate(mask) if flag}
        newrows=[set(z) for z in rows]
        newrows[0]=common|x
        newrows[3]=common|(set(pool)-x)
        assert prior.fixed_margins(newrows)==fixed
    return q

def choose_event_probability(event,theta,columns):
    offsets=event["candidates_base"]
    f=event["candidates_features"][:,columns]
    z=offsets+f@theta
    observed=event["obs_base"]+event["obs_features"][columns]@theta
    return float(observed-logsumexp(z))

def rank_group(events_by_run,columns):
    chunks=[]
    for events in events_by_run.values():
        for e in events:
            feats=e["candidates_features"][:,columns]
            chunks.append(feats-feats.mean(axis=0))
    if not chunks:return 0
    return int(np.linalg.matrix_rank(np.concatenate(chunks,axis=0),tol=1e-9))

def fit_model(events_by_run,columns):
    columns=list(columns)
    nr=len(events_by_run)
    nroute=len({info["route"] for info in events_by_run.values()})
    nevent=sum(len(x["events"]) for x in events_by_run.values())
    info={"training_runs":nr,"training_routes":nroute,
          "training_swap_events":int(nevent),
          "features":[FEATURE_LABELS[z] for z in columns]}
    if nr<30 or nroute<15 or nevent<40:
        return np.zeros(len(columns)),{**info,"status":"insufficient_train"}
    # Tests both known partner features and the generic richness nuisance,
    # preventing otherwise silent collinearity.
    groups={rid:info["events"] for rid,info in events_by_run.items()}
    rank=rank_group(groups,columns)
    if rank<len(columns):
        return np.zeros(len(columns)),{**info,"status":"rank_deficient","matrix_rank":rank}
    # Per-survey equal weighting, not per-swap; otherwise routes with more
    # co-calling species would dominate the training objective.
    prepared=[]
    for group in groups.values():
        n=float(len(group))
        for e in group:
            prepared.append((e["candidates_base"],
                            e["candidates_features"][:,columns],
                            float(e["obs_base"]),
                            e["obs_features"][columns],
                            1.0/n))
    q=len(columns)
    def objective(theta):
        loss=PENALTY*float(theta@theta)/2.
        grad=PENALTY*theta.copy()
        for base,x,obs0,obsx,weight in prepared:
            z=base+x@theta
            ln=logsumexp(z)
            lp=obs0+obsx@theta
            prob=np.exp(z-ln)
            loss+=weight*(ln-lp)
            grad+=weight*(prob@x-obsx)
        return float(loss),grad
    opt=minimize(objective,np.zeros(q,float),method="L-BFGS-B",
                 jac=True,bounds=[(-BOUND,BOUND)]*q,
                 options={"maxiter":70,"ftol":1e-10})
    beta=np.asarray(opt.x,float)
    if not opt.success or not np.isfinite(beta).all():
        return np.zeros(q),{**info,"status":"optimizer_failed",
                            "optimizer_message":str(opt.message)[:100]}
    return beta,{**info,"status":"fitted","matrix_rank":rank,
                 "optimizer_success":True,
                 "iterations":int(opt.nit),
                 "coefficients":beta.tolist(),
                 "ridge":PENALTY,"bounds":[-BOUND,BOUND]}

def train_both(events_by_run,stage):
    coefs={};audits={}
    for name,columns in MODEL_COLS.items():
        coefs[name],audits[name]=fit_model(events_by_run,columns)
    return {"stage":stage,"coefs":coefs,"audit":audits,
            "fitted":all(v["status"]=="fitted" for v in audits.values())}

def bootstrap_route(table,seed):
    if table.empty:return {"status":"empty"}
    p=table.groupby("route").gain.agg(["sum","size"])
    totals=p["sum"].to_numpy(float)
    sizes=p["size"].to_numpy(float)
    n=len(p)
    # 2k route-block draws; repeated surveys on a route remain together.
    picks=np.random.default_rng(seed).integers(0,n,(BOOT,n))
    boots=totals[picks].sum(axis=1)/sizes[picks].sum(axis=1)
    ci=[float(x) for x in np.quantile(boots,[.025,.975])]
    y=table.gain.to_numpy(float)
    f=sm.OLS(y,np.ones((len(y),1))).fit(
        cov_type="cluster",cov_kwds={"groups":table.route.astype(str)})
    return {
        "status":"fitted","n_runs":int(len(table)),
        "n_routes":int(n),
        "gain_nats_per_heldout_run":float(y.mean()),
        "route_bootstrap_ci95":ci,
        "route_cluster_ci95":[float(f.params[0]-Z*f.bse[0]),
                              float(f.params[0]+Z*f.bse[0])],
        "p_two_sided_route_cluster":float(f.pvalues[0]),
        "positive_bootstrap_ci":bool(ci[0]>0),
        "fold_means":{str(f):float(z.gain.mean())
                      for f,z in table.groupby("fold")},
        "year_early":int((table.year<=2009).sum()),
        "year_late":int((table.year>=2010).sum()),
        "bootstrap_replicates":BOOT
    }

def heldout_score(events_by_run,model):
    out=[]
    c0=model["coefs"]["M0_generic_richness"]
    cp=model["coefs"]["M_P_positive_partner"]
    c1=model["coefs"]["M1_plus_partner_identity"]
    if not model["fitted"]:return pd.DataFrame()
    for rid,info in sorted(events_by_run.items()):
        events=info["events"]
        score0=float(np.mean([choose_event_probability(e,c0,[0]) for e in events]))
        scorep=float(np.mean([choose_event_probability(e,cp,[0,1]) for e in events]))
        score1=float(np.mean([choose_event_probability(e,c1,[0,1,2]) for e in events]))
        gain_P=scorep-score0
        gain_N=score1-scorep
        gain=score1-score0
        if not np.isclose(gain,gain_P+gain_N,atol=1e-12,rtol=0):
            raise RuntimeError("Nested positive+negative score decomposition changed sample")
        out.append({"RunID":rid,"route":info["route"],"fold":info["fold"],
                    "year":info["year"],"n_swaps":len(events),
                    "gain":gain,"gain_P":gain_P,"gain_N":gain_N,
                    "log_M0":score0,"log_M_P":scorep,"log_M1":score1})
    return pd.DataFrame(out)

def gather_source(frozen_dir):
    records,refs,coefs,scope=pairmod.prior_inputs(frozen_dir)
    raw=ecology.hist.load_retry()
    runs,_=ecology.base.build_runs(raw)
    years=dict(zip(runs.RunID.astype(str),runs.SurveyYear.astype(int)))
    histories,audit=histmod.historical_provenance(raw,runs,records)
    return records,refs,coefs,scope,years,histories,audit

def mode_events(mode,records,refs,coef,years,histories):
    if refs.RunID.duplicated().any():raise RuntimeError("Original C-score run identity duplicated")
    df=refs.set_index("RunID",drop=False)
    selected=sorted(set(records)&set(df.index.astype(str)))
    expected=BASE_ANY if mode=="any" else BASE_STRONG
    if len(selected)!=expected:
        raise RuntimeError("Original frozen NWI exact study population changed")
    saved={name:{} for name in NEGATIVES}
    scope=Counter()
    for rid in selected:
        row=records[rid]
        taxa,positions=prior.ref_rows(row,mode)
        # Identity check on all 3659/1766 original matrices.
        if not np.isclose(prior.cscore(positions),float(df.loc[rid].observed),
                          atol=1e-8,rtol=0):
            raise RuntimeError("Original observed matrix C-score mismatch "+rid)
        scope["original_observed_Cscore_verified"]+=1
        if rid not in histories:continue
        h=histories[rid]
        if not h["past_survey_years_only"]:
            raise RuntimeError("History includes current/future year")
        scope["seasonal_prior_SiteID_eligible"]+=1
        index={t:i for i,t in enumerate(taxa)}
        if CENTRAL not in index or POSITIVE not in index:continue
        c_idx=index[CENTRAL];p_idx=index[POSITIVE]
        # Nested two-stage geographic split: stage-2 training for fold F
        # uses first-order NWI coefficients learned exclusively on F.
        # Heldout fold not used anywhere in that stage-2 training offset.
        def frozen_offset(fitted_route_fold):
            source_weights=coef[fitted_route_fold]
            return np.stack([
                np.asarray(source_weights.get(t,{}).get(
                    "wetland_and_emergent",np.zeros(2)),float)
                for t in taxa
            ])@row["v"][:,[0,1]].T
        hmat=np.stack([
            np.asarray(h["scores"][mode].get(t,np.zeros(10)),float)
            for t in taxa
        ])
        offset_own_fold=frozen_offset(row["fold"])+hmat
        offset_opposite_fold=frozen_offset(
            prior.complementary(row["fold"]))+hmat
        if (offset_own_fold.shape!=(len(taxa),10)
            or offset_opposite_fold.shape!=(len(taxa),10)
            or not np.isfinite(offset_own_fold).all()
            or not np.isfinite(offset_opposite_fold).all()):
            raise RuntimeError("Bad nested NWI+prior-SiteID offset")
        for negative in NEGATIVES:
            if negative not in index:continue
            n_idx=index[negative]
            events=[]
            events_within_fold=[]
            for j in range(len(taxa)):
                if j in {c_idx,p_idx,n_idx}:continue
                heldout_event=exact_event(
                    positions,c_idx,j,p_idx,n_idx,offset_opposite_fold)
                in_training_event=exact_event(
                    positions,c_idx,j,p_idx,n_idx,offset_own_fold)
                if (heldout_event is None)!=(in_training_event is None):
                    raise RuntimeError("Nested first-order fold changed event membership")
                if heldout_event is not None:
                    events.append(heldout_event)
                    events_within_fold.append(in_training_event)
            scope[f"{negative}_trio_coactive"]+=1
            if not events:continue
            scope[f"{negative}_trio_with_nonfocal_swaps"]+=1
            scope[f"{negative}_swap_events"]+=len(events)
            saved[negative][rid]={
                "RunID":rid,"route":row["route"],"fold":row["fold"],
                "year":int(years[rid]),
                "n_taxa":len(taxa),"events":events,
                "events_within_training_fold":events_within_fold,
                "n_events":len(events),
                "variable_P":any(e["variable_P"] for e in events),
                "variable_N":any(e["variable_N"] for e in events)}
    return saved,dict(scope)

def evaluate_one(trio_runs,mode,negative,outdir):
    early={rid:x for rid,x in trio_runs.items() if x["year"]<=2009}
    late={rid:x for rid,x in trio_runs.items() if x["year"]>=2010}
    folds={f:{rid:x for rid,x in trio_runs.items() if x["fold"]==f} for f in ("A","B")}
    counts={
        "n_runs":len(trio_runs),
        "n_routes":len({x["route"] for x in trio_runs.values()}),
        "n_early":len(early),"n_late":len(late),
        "n_events":sum(len(x["events"]) for x in trio_runs.values()),
        "median_alternates":float(np.median([len(x["events"]) for x in trio_runs.values()])) if trio_runs else None,
        "n_runs_partner_P_variable":sum(x["variable_P"] for x in trio_runs.values()),
        "n_runs_partner_N_variable":sum(x["variable_N"] for x in trio_runs.values()),
        "fold_A":len(folds["A"]),"fold_B":len(folds["B"])
    }
    eligible=(counts["n_runs"]>=60 and counts["n_routes"]>=25
              and counts["fold_A"]>=20 and counts["fold_B"]>=20
              and counts["n_events"]>=40
              and counts["n_runs_partner_P_variable"]>=20
              and counts["n_runs_partner_N_variable"]>=20)
    out={"trio":[CENTRAL,POSITIVE,negative],
         "population":counts,"eligible":bool(eligible),
         "rank_failures_fail_closed":True}
    if not eligible:
        out["classification"]="insufficient_scope"
        return out
    fits={}
    predictions=[]
    for train_fold in ("A","B"):
        # Never allow original first-order NWI coefficients learned on
        # the heldout route fold into stage-2 training events.
        train={
            rid:{**v,"events":v["events_within_training_fold"]}
            for rid,v in folds[train_fold].items()
        }
        test=folds[prior.complementary(train_fold)]
        if any(row["fold"]!=train_fold for row in train.values()):
            raise RuntimeError("Stage-2 training route leakage")
        fitted=train_both(train,"route_train_"+train_fold)
        fits[train_fold]={"audit":fitted["audit"],"fitted":fitted["fitted"]}
        if fitted["fitted"]:
            fits[train_fold]["coefficients"]={
                 key:vals.tolist() for key,vals in fitted["coefs"].items()}
            result=heldout_score(test,fitted)
            predictions.append(result)
    out["geographic_route_folds"]=fits
    if len(predictions)!=2:
        out["classification"]="nonidentifiable_or_optimizer_failed"
        return out
    x=pd.concat(predictions,ignore_index=True)
    if x.RunID.duplicated().any() or len(x)!=counts["n_runs"]:
        raise RuntimeError("Heldout data left out or duplicated original eligible run")
    route=bootstrap_route(x,SEED+(0 if negative==NEGATIVES[0] else 1)
                          +(0 if mode=="any" else 20))
    signs={}
    for f in ("A","B"):
        coef=fits[f]["coefficients"]["M1_plus_partner_identity"]
        signs[f]={"generic_richness":coef[0],"P":coef[1],"N":coef[2],
                  "P_positive":coef[1]>0,"N_negative":coef[2]<0}
    out["route_heldout"]=route
    out["training_partner_direction"]=signs
    out["both_folds_expected_signs"]=bool(
       all(z["P_positive"] and z["N_negative"] for z in signs.values()))
    out["both_heldout_fold_gains_positive"]=bool(
        route["fold_means"].get("A",0)>0 and
        route["fold_means"].get("B",0)>0)
    # Fixed secondary temporal transfer, acknowledging that the original
    # first-order NWI species coefficients used both eras.
    if len(early)>=30 and len({z["route"] for z in early.values()})>=15 and len(late)>=30 and len({z["route"] for z in late.values()})>=15:
        trained=train_both(early,"early_years_2001_2009")
        if trained["fitted"]:
            predicted=heldout_score(late,trained)
            out["early_trained_late_test"]={
                "fit_status":"fitted",
                "early_training_audit":trained["audit"],
                "late_prediction":bootstrap_route(predicted,SEED+140),
                "original_NWI_coefficients_trained_both_year_periods":True}
        else:
            out["early_trained_late_test"]={"fit_status":"insufficient_or_failed","audit":trained["audit"]}
    else:
        out["early_trained_late_test"]={
            "fit_status":"underpowered",
            "early_runs":len(early),"late_runs":len(late),
            "historical_coefficients_not_chronologically_independent":True}
    out["classification"]="pending_fdr_gate"
    x.to_csv(outdir/f"{mode}_{negative.replace(' ','_')}_route_heldout_scoring.csv",index=False)
    return out

def synthetic_checks():
    r=assert_same_margins_candidate()
    fixed=prior.fixed_margins([{0,2,4},{1,2,5},{3,4,5},{0,6},{1,7}])
    assert r["n_candidate_sets"]>=2
    # Proper probability over candidate reassignments, not a density ratio.
    z=r["candidates_base"]
    x=r["candidates_features"]
    theta=np.asarray([.2,.8,-.7])
    probs=np.exp(z+x@theta-logsumexp(z+x@theta))
    assert np.allclose(probs.sum(),1.0)
    # Simulated conditional choice sign recovery under a known identity effect.
    combo=choose_mask(6,3)
    R=np.asarray([0,2,1,0,2,1],float)
    XP=np.asarray([1,1,0,0,0,0],float)
    XN=np.asarray([0,0,1,1,0,0],float)
    s=np.column_stack([np.zeros(6),R,XP,XN])
    cand=combo@s
    true=np.asarray([.20,1.3,-1.1])
    logits=cand[:,1:]@true
    probs=np.exp(logits-logsumexp(logits))
    random=np.random.default_rng(2840328)
    samples=random.choice(np.arange(len(cand)),size=140,p=probs)
    cases={}
    for ix,j in enumerate(samples):
        cases[str(ix)]={
            "route":f"simulation_route_{ix%35}","fold":("A" if ix%2==0 else "B"),
            "year":2007,"events":[{
                "candidates_base":cand[:,0],
                "candidates_features":cand[:,1:],
                "obs_base":float(cand[j,0]),
                "obs_features":cand[j,1:]
            }]}
    fit=train_both(cases,"synthetic_sign_recovery")
    if not fit["fitted"]:
        raise RuntimeError("Synthetic conditional optimizer or full-rank check failed")
    recovered=fit["coefs"]["M1_plus_partner_identity"]
    assert recovered[1]>0.25 and recovered[2]<-.25, recovered
    return {"status":"PASS","exact_swap_fixed_row_column_margins":True,
            "candidate_probabilities_normalized":True,
            "synthetic_positive_partner_recovered":True,
            "synthetic_negative_partner_recovered":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-nwi",type=Path)
    p.add_argument("--outdir",type=Path,default=ROOT/"build"/"partner_choice_crossfit")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    qa=synthetic_checks()
    print("PARTNER_HELDOUT_SYNTHETIC_QA",json.dumps(qa,sort_keys=True),flush=True)
    if args.synthetic_only:return
    if args.frozen_nwi is None:raise RuntimeError("Source NWI crossfit artifact required")
    records,refs,coefs,scope,years,histories,hist_audit=gather_source(args.frozen_nwi)
    args.outdir.mkdir(parents=True,exist_ok=True)
    result={
        "analysis":"NAAMP_frog_partner_exact_fixed_margin_heldout_choice_v0_1",
        "status":"posthoc_partner_identity_predictive_question_not_causal",
        "contract":"exploration/NAAMP_PARTNER_FIXED_MARGIN_HELDOUT_CHOICE_CONTRACT_V0_2.md",
        "source_NWI_crossfit_run":39516056663,
        "source_strict_prior_SiteID_null_run":39603785733,
        "source_same_survey_residual_trio_run":39597933440,
        "source_NWI_geometry_run":39450277196,
        "synthetic_QA":qa,
        "source_context":scope,"historical_source_gate":hist_audit,
        "parameters":{"ridge":PENALTY,"bound":BOUND,"bootstrap":BOOT,
                      "site_history_strength":1.0,
                      "exact_fixed_C_vs_other_row_swap":True,
                      "same_night_partner_presence_conditioned":True,
                      "opposite_geographic_route_fold_training":True,
                      "first_order_NWI_nested_with_second_stage_training":True,
                      "original_species_site_NWI_coefficients_frozen":True,
                      "original_NWI_trained_both_eras":True,
                      "original_RC6_paper_unchanged":True},
        "modes":{}}
    for mode in ("any","strong"):
        eligible,mc=mode_events(mode,records,refs[mode],coefs[mode],years,histories)
        out={"scope":mc,"partners":{}}
        for neg in NEGATIVES:
            out["partners"][neg]=evaluate_one(eligible[neg],mode,neg,args.outdir)
            q=out["partners"][neg]
            print("PARTNER_HELDOUT_MODE_RESULT",mode,neg,json.dumps({
                "population":q["population"],
                "classification":q.get("classification"),
                "gain":q.get("route_heldout",{}).get("gain_nats_per_heldout_run"),
                "CI":q.get("route_heldout",{}).get("route_bootstrap_ci95"),
                "signed_betas":q.get("training_partner_direction"),
                "temporal":q.get("early_trained_late_test",{}).get("late_prediction",{}).get("gain_nats_per_heldout_run")},sort_keys=True),flush=True)
        eligible_fit=[(n,x) for n,x in out["partners"].items() if x.get("classification")=="pending_fdr_gate"]
        if eligible_fit:
            qs=multipletests([x["route_heldout"]["p_two_sided_route_cluster"]
                             for _,x in eligible_fit],method="fdr_bh")[1]
            for (name,x),q in zip(eligible_fit,qs):
                x["route_heldout_BH_q_two_focal_trios"]=float(q)
                p=x["route_heldout"]
                x["signed_partner_prediction_candidate"]=bool(
                    q<.05 and p["positive_bootstrap_ci"]
                    and x["both_heldout_fold_gains_positive"]
                    and x["both_folds_expected_signs"])
                x["classification"]=(
                    "supported_predictive_partner_identity_candidate"
                    if x["signed_partner_prediction_candidate"]
                    else "heldout_partner_increment_not_supported")
        result["modes"][mode]=out
    result["inference_boundaries"]={
        "independent_mechanistic_biological_replication":False,
        "causal_social_acoustic_interaction_proven":False,
        "other_species_rows_are_observed_not_intervened":True,
        "conditional_pseudolikelihood_not_full_community_likelihood":True,
        "fixed_margins_condition_on_observed_site_richness":True,
        "survey_stops_sequential_not_simultaneous":True,
        "species_SiteID_history_strictly_prior_years":True,
        "first_order_NWI_coefficients_fit_crossroute_not_crosstime":True,
        "aquatic_plant_species_measured":False,
        "frozen_RC6_manuscript_changed":False}
    (args.outdir/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("PARTNER_FIXED_MARGIN_HELDOUT_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("PARTNER_FIXED_MARGIN_HELDOUT_RESULT_END",flush=True)

if __name__=="__main__":
    main()
