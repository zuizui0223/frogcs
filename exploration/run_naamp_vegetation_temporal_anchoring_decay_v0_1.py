#!/usr/bin/env python3
"""NAAMP acoustic taxon site-identity duration gradients, not predictions.

Same physical SiteID / same survey round in adjacent observed years, original
USGS NAAMP 2001-2015 × source-verified USFWS NWI 250m polygon audit.
Post-hoc elapsed-year ecological association with physical route×round FE.
This neither observes plant species in source survey years nor establishes
demographic survival, plant causality, competition or true temporal decay.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/"exploration/run_naamp_vegetation_interannual_site_fidelity_v0_1.py"
SPEC="exploration/NAAMP_VEGETATION_TEMPORAL_ANCHORING_DECAY_SPEC_2026_10_23.md"
MODELS=("mean_F_any","mean_F_strong","difference_PEM_minus_other_any",
        "difference_PEM_minus_other_strong")
CONFOUND=("DOY_gap_per30","temperature_gap_per5","rain_log1p_gap",
          "same_observer","startyear_per5")
FEATURES=("log2_year_gap",)+CONFOUND
N_REPS=4999
SEED=26010423

def import_source():
    sp=importlib.util.spec_from_file_location("previous_NAAMP_exact_temporal_identity",ORIGINAL)
    if sp is None or sp.loader is None:raise RuntimeError("Validated temporal source unavailable")
    m=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m

def construct_design(frame,original_metadata=None,remove_same_observer=False):
    d=frame.copy()
    if not set(["route","state","run_round","year_before","year_gap",
                "DOY_gap_abs","temp_gap_abs","same_observer"]).issubset(d):
        raise ValueError("Original matched site/year pair covariates missing")
    if (d.year_gap<1).any() or (d.year_gap>14).any():
        raise ValueError("Original adjacent survey-year gap outside 1–14")
    if original_metadata is not None:
        rain=[]
        for rec in d.itertuples(index=False):
            early=float(original_metadata[str(rec.rid_before)]["rain"])
            later=float(original_metadata[str(rec.rid_after)]["rain"])
            if early<0 or later<0:raise ValueError("Negative source DaysSinceRain prevents log1p interpretation")
            rain.append(abs(math.log1p(early)-math.log1p(later)))
        d["rain_log1p_gap"]=rain
    if "rain_log1p_gap" not in d.columns:
        raise ValueError("Unreconstructable log1p rainfall gap, refuse to substitute raw rainfall gap")
    d["log2_year_gap"]=np.log2(d.year_gap.astype(float))
    d["DOY_gap_per30"]=d.DOY_gap_abs.astype(float)/30.
    d["temperature_gap_per5"]=d.temp_gap_abs.astype(float)/5.
    d["startyear_per5"]=(d.year_before.astype(float)-2001.)/5.
    d["same_observer"]=d.same_observer.astype(float)
    d["round_cluster"]=d.route.astype(str)+"|"+d.run_round.astype(str)
    group,gi=np.unique(d.round_cluster.to_numpy(),return_inverse=True)
    routes,ri=np.unique(d.route.astype(str).to_numpy(),return_inverse=True)
    states,si=np.unique(d.state.astype(str).to_numpy(),return_inverse=True)
    if d.groupby("round_cluster").route.nunique().max()!=1:
        raise ValueError("Route-round fixed effect combines multiple physical routes")
    freq=np.bincount(gi)
    variance=np.bincount(gi,weights=d.log2_year_gap,minlength=len(group))/freq
    centered_log=d.log2_year_gap.to_numpy()-variance[gi]
    informative_groups=np.bincount(gi,weights=centered_log**2,minlength=len(group))>1e-10
    informative_routes=sorted(set(str(x).split("|")[0] for x in group[informative_groups]))
    features=[c for c in FEATURES if not(remove_same_observer and c=="same_observer")]
    X=d[features].to_numpy(float)
    if not np.isfinite(X).all():raise ValueError("Missing survey covariates on fixed matched-year source")
    for j in range(X.shape[1]):
        X[:,j]-=np.bincount(gi,weights=X[:,j],minlength=len(group))[gi]/freq[gi]
    R=len(routes);S=len(states);H=len(group);N=len(d);K=X.shape[1]
    route_size=np.bincount(ri)
    w=1./route_size[ri]
    if N-K-H+1<=30:raise ValueError("Insufficient residual degrees of freedom after route-round FE")
    if np.linalg.matrix_rank(X*np.sqrt(w[:,None]))<K:raise ValueError("Fitted elapsed-year slope confounded by source nuisance/route-round variables")
    A=X.T@(w[:,None]*X)
    nuisance=X[:,1:]
    An=nuisance.T@(w[:,None]*nuisance)
    if np.linalg.matrix_rank(An)<nuisance.shape[1]:
        raise ValueError("Nuisance variables collinear after survey-round fixed effects")
    out={"frame":d,"features":features,"X":X,"route":routes,"route_i":ri,
         "state":states,"state_i":si,"group":group,"group_i":gi,
         "group_size":freq,"w":w,"A":A,"An":An,
         "N":N,"R":R,"S":S,"H":H,"K":K,
         "n_informative_duration_groups":int(informative_groups.sum()),
         "n_informative_duration_routes":int(len(informative_routes)),
         "sample_richness_not_conditioned":True}
    return out

def fit(d,design,response,seed,do_flips=True):
    N=design["N"];H=design["H"];K=design["K"];R=design["R"];S=design["S"]
    X=design["X"];w=design["w"];i=design["group_i"];count=design["group_size"]
    yy=d[response].to_numpy(float)
    if not np.isfinite(yy).all():raise ValueError("Nonfinite original acoustic site identity outcome")
    y=yy-np.bincount(i,weights=yy,minlength=H)[i]/count[i]
    b=np.linalg.solve(design["A"],X.T@(w*y))
    e=y-X@b
    inv=np.linalg.inv(design["A"])
    def sandwich(g,G):
        z=np.zeros((G,K),float)
        np.add.at(z,g,(w*e)[:,None]*X)
        correction=G/(G-1)*(N-1)/(N-K-H+1)
        V=correction*inv@(z.T@z)@inv
        V=(V+V.T)/2
        if (np.diag(V)<-1e-12).any():raise ValueError("Route/State sandwich covariance negative")
        return V
    Vr=sandwich(design["route_i"],R)
    Vs=sandwich(design["state_i"],S)
    br=float(b[0]);ser=float(math.sqrt(max(0,Vr[0,0])))
    ses=float(math.sqrt(max(0,Vs[0,0])))
    if ser<=1e-12:raise RuntimeError("Ill-defined physical-route clustered elapsed-time confidence interval")
    rc=float(student_t.ppf(.975,R-1));sc=float(student_t.ppf(.975,S-1))
    p=float(2*student_t.sf(abs(br/ser),R-1))
    z=X[:,1:]
    aa=design["An"]
    xr=X[:,0]-z@np.linalg.solve(aa,z.T@(w*X[:,0]))
    yr=y-z@np.linalg.solve(aa,z.T@(w*y))
    fwl=float(np.dot(w*xr,yr)/np.dot(w*xr,xr))
    if not math.isclose(br,fwl,rel_tol=1e-8,abs_tol=1e-10):
        raise RuntimeError("Nuisance-orthogonalized year-gap signal disagrees with full within-round model")
    scores=np.bincount(design["route_i"],weights=w*xr*yr,minlength=R)
    observed=abs(float(scores.sum()))
    empirical=None
    if do_flips:
        rng=np.random.default_rng(seed)
        rejects=0
        for start in range(0,N_REPS,250):
            m=min(250,N_REPS-start)
            mx=rng.choice(np.array([-1.,1.]),size=(m,R))@scores
            rejects+=int((np.abs(mx)>=observed-1e-15).sum())
        empirical={"route_score_flips":N_REPS,"extreme":rejects,
                   "plus_one_two_sided_P":(rejects+1)/(N_REPS+1),
                   "approximate_route_symmetric_score_null_not_plant_randomization":True}
    loo={}
    A=design["A"];rhs=X.T@(w*y)
    for j,state in enumerate(design["state"]):
        keep=design["state_i"]!=j
        remove=~keep
        Az=A-X[remove].T@(w[remove,None]*X[remove])
        ry=rhs-X[remove].T@(w[remove]*y[remove])
        if np.linalg.matrix_rank(Az)<K:loo[str(state)]=None
        else:loo[str(state)]=float(np.linalg.solve(Az,ry)[0])
    valid=[v for v in loo.values() if v is not None]
    valout={
        "outcome":response,
        "log2_gap_beta_taxon_units_per_site_per_gap_doubling":br,
        "log2_gap_95pct_route_CI":[br-rc*ser,br+rc*ser],
        "physical_route_cluster_SE":ser,
        "log2_gap_95pct_State_CI":[br-sc*ses,br+sc*ses],
        "State_cluster_SE":ses,
        "route_cluster_Student_two_sided_P":p,
        "n_route_year_pairs":N,"n_physical_routes":R,"n_states":S,
        "n_route_round_fixed_effect_groups":H,
        "n_routes_with_within_round_yeargap_variation":design["n_informative_duration_routes"],
        "n_round_groups_with_yeargap_variation":design["n_informative_duration_groups"],
        "five_fixed_nuisance_covariates":design["features"][1:],
        "whole_route_score_signflips":empirical,
        "omit_one_State":{
            "n_estimable":len(valid),"n_negative":sum(v<0 for v in valid),
            "n_positive":sum(v>0 for v in valid),
            "range":[min(valid),max(valid)] if valid else None},
        "route_coefficients_for_auditing":{name:float(v) for name,v in zip(design["features"],b)},
        "no_plant_causal_effect_identified":True}
    return valout

def descriptives(data):
    out={}
    for mode in MODELS:
        bins={"1year":data[data.year_gap==1],
              "2years":data[data.year_gap==2],
              "3years":data[data.year_gap==3],
              "4to14years":data[data.year_gap>=4]}
        out[mode]={}
        for key,df in bins.items():
            rr=df.groupby("route")[mode].mean()
            out[mode][key]={
                "route_year_pairs":int(len(df)),"n_routes":int(len(rr)),
                "mean_route_balanced":float(rr.mean()) if len(rr) else None,
                "without_other_covariate_adjustment":True}
    return out

def BH(res):
    ps=[res[m]["route_cluster_Student_two_sided_P"] for m in MODELS]
    ranks=sorted(range(len(ps)),key=lambda i:ps[i])
    q=1.
    for rank in range(len(ranks),0,-1):
        i=ranks[rank-1]
        q=min(q,len(ps)*ps[i]/rank)
        res[MODELS[i]]["BH_q_four_temporal_hypotheses"]=q
    primary=res["mean_F_any"]
    ci=primary["log2_gap_95pct_route_CI"]
    s=primary["log2_gap_95pct_State_CI"]
    p=primary["whole_route_score_signflips"]["plus_one_two_sided_P"]
    gate=bool(primary["log2_gap_beta_taxon_units_per_site_per_gap_doubling"]<0
      and ci[1]<0 and primary["BH_q_four_temporal_hypotheses"]<.05
      and p<.05 and s[0]<=0 and
      primary["omit_one_State"]["n_negative"]>=.75*primary["omit_one_State"]["n_estimable"])
    return "exploratory_route_robust_acoustic_memory_decay" if gate else "no_supported_elapsed_year_decay_on_adjusted_same_footprint"

def validate(real,coverage):
    scope={
      "original_NWI_complete_survey_runs":6236,
      "source_matched_adjacent_year_pairs":2403,
      "source_monitoring_routes":273,"source_States":20,
      "original_year_gap_1_pairs":1573,"original_gap_gt1_pairs":830}
    if coverage["physically_stable_vegetation_mixed_source_run_pairs"]!=2403:
        raise RuntimeError("Source-linked original 2,403 interannual pairs have drifted")
    if len(real)!=2403 or real.route.nunique()!=273 or real.state.nunique()!=20:
        raise RuntimeError("Source whole-route geographic/temporal support drift")
    if int((real.year_gap==1).sum())!=1573:
        raise RuntimeError("Original one-year gap cohort changed")
    if int((real.year_gap>1).sum())!=830:
        raise RuntimeError("Original multi-year gap cohort changed")
    return scope

def synthetic():
    rng=np.random.default_rng(2601999)
    data=[]
    for r in range(110):
        for round_id in (1,2):
            for k in range(8):
                gap=[1,2,3,4,6,8,10,14][(k+round_id+r)%8]
                ystart=2001+(k+r)%10
                doy=float(rng.uniform(0,90))
                temp=float(rng.uniform(0,13))
                rain=float(rng.uniform(0,2))
                same=bool(rng.uniform()<.75)
                log_gap=math.log2(gap)
                val=(.35-.07*log_gap+.016*doy/30.-.004*temp/5.
                     +.009*rain+.01*same+.001*(ystart-2001)/5.
                     +.02*r/110.+float(rng.normal(0,.025)))
                data.append({"route":f"synthr{r}","state":f"S{r%20}","run_round":str(round_id),
                    "year_before":ystart,"year_gap":gap,"DOY_gap_abs":doy,
                    "temp_gap_abs":temp,"rain_log1p_gap":rain,"same_observer":same,
                    "mean_F_any":val})
    x=pd.DataFrame(data)
    d=construct_design(x)
    v=fit(d["frame"],d,"mean_F_any",SEED,do_flips=False)
    beta=v["log2_gap_beta_taxon_units_per_site_per_gap_doubling"]
    if not (-.09<beta<-.05):
        raise RuntimeError("Exact route-round nuisance-adjusted known synthetic −.07 gap slope not recovered")
    if d["n_informative_duration_routes"]!=110:
        raise RuntimeError("Synthetic matched route/season duration variation missing")
    return {"status":"PASS","known_gap_beta":-.07,"recovered_gap_beta":beta,
        "FWL_full_regression_identity":True,
        "whole_physical_route_cluster_unit":True,
        "n_simulated_routes":110,
        "no_naamp_real_outcome_used_for_QA":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_vegetation_memory_decay")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    qa=synthetic()
    if args.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    src=import_source()
    original,calling,source_info=src.read_original()
    frame,source_scope=src.build_matched_pairs(original,calling)
    authority=validate(frame,source_scope)
    frame["mean_F_any"]=(frame.recurrence_excess_PEM_any+
                          frame.recurrence_excess_nonPEM_any)/2.
    frame["mean_F_strong"]=(frame.recurrence_excess_PEM_strong+
                            frame.recurrence_excess_nonPEM_strong)/2.
    frame["difference_PEM_minus_other_any"]=frame.site_fidelity_PEM_minus_other_any
    frame["difference_PEM_minus_other_strong"]=frame.site_fidelity_PEM_minus_other_strong
    d=construct_design(frame,original)
    if (d["N"]<200 or d["R"]<50 or d["S"]<5
        or d["n_informative_duration_routes"]<80):
        raise RuntimeError("Predeclared inferential gap-variation support failed")
    results={}
    for j,mode in enumerate(MODELS):
        results[mode]=fit(d["frame"],d,mode,SEED+j)
    inference=BH(results)
    same=d["frame"].loc[d["frame"]["same_observer"].astype(float)==1.0].copy()
    same_sens={}
    if same.route.nunique()>=100 and len(same)>=500:
        ds=construct_design(same,remove_same_observer=True)
        if ds["n_informative_duration_routes"]>=50:
            for j,name in enumerate(("mean_F_any","mean_F_strong")):
                same_sens[name]=fit(ds["frame"],ds,name,SEED+100+j)
        else:same_sens={"status":"insufficient_within_route_round_duration_variation"}
    else:same_sens={"status":"insufficient_same_observer_source_coverage"}
    raw_diagnostics=descriptives(d["frame"])
    res={
      "analysis":"NAAMP_PEM_wetland_elapsed_year_acoustic_site_identity_gap_macro_ecology",
      "status":"real_NAAMP_longitudinal_wetland_acoustic_memory_decay_test_completed",
      "date":"2026-10-23",
      "spec":SPEC,"exploratory_hypothesis_after_prior_greater_1year_gap_seen":True,
      "source_coverage":authority,"original_temporal_source":source_info,
      "original_matched_year_pair_scope":source_scope,
      "mathematical_QA":qa,
      "primary_and_secondary_elapsed_time_slopes":results,
      "main_inference_verdict":inference,
      "year_gap_bins_unadjusted":raw_diagnostics,
      "same_original_ObserverTrackingID_sensitivity":same_sens,
      "limits":{
         "interannual_adjacent_observed_year_selection_informative":True,
         "same_round_not_exact_calendar_date_match":True,
         "NWI_category_not_contemporaneous_2001_2015_plant_structure":True,
         "acoustic_detections_not_occupancy_or_population_persistence":True,
         "no_physical_individual_frog_fidelity_identified":True,
         "true_ecological_time_decay_causality_not_proven":True,
         "no_frog_frog_or_invertebrate_fish_interaction_data":True,
         "not_prediction_or_heldout_forecast":True,
         "frozen_JAE_RC6_main_manuscript_SI_untouched":True}
    }
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(res,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("NAAMP_TEMPORAL_DURATION_MACRO_BEGIN",flush=True)
    print(json.dumps({
      "status":res["status"],"mathematical_QA":qa,
      "sample":{"N":d["N"],"R":d["R"],"S":d["S"],"H":d["H"],
           "n_informative_duration_groups":d["n_informative_duration_groups"],
           "n_informative_duration_routes":d["n_informative_duration_routes"]},
      "verdict":inference,
      "slopes":{name:{
           k:v for k,v in m.items() if k!="route_coefficients_for_auditing"}
           for name,m in results.items()},
      "same_observer_sensitivity":same_sens,
      "year_gap_unadjusted_descriptives":raw_diagnostics},
      sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_TEMPORAL_DURATION_MACRO_END",flush=True)

if __name__=="__main__":
    main()
