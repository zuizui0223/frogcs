#!/usr/bin/env python3
"""Non-predictive continental frog community gamma rarefaction by NWI habitat.

NAAMP 2001–2015, 6,236 environmentally complete ten-stop surveys, USFWS NWI
250m mapped polygon classes, four overlapping habitat strata. Exact analytical
without-replacement detection probabilities; independent inference per route.
The 199 matching-subsample PEM turnover decomposition is secondary descriptive.
Mapped NWI != time-matched field vegetation; calling != stable occupancy.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
HABITATS=("pem","aquatic_bed","woody","all_wetland")
FIELDS=("nwi_emergent_cover_250m","nwi_aquatic_bed_cover_250m",
        "nwi_woody_cover_250m","nwi_all_wetland_cover_250m")
MODES=(("any",1),("strong",2))
SPEC="exploration/NAAMP_RAREFIED_VEGETATION_GAMMA_COMPOSITION_SPEC_2026_10_23.md"
SEED=2601023
FLIPS=4999
POOLED_DRAWS=199
Z=1.959963984540054

def mod(label,path):
    s=importlib.util.spec_from_file_location(label,path)
    if s is None or s.loader is None:raise RuntimeError("Required source file absent: "+str(path))
    o=importlib.util.module_from_spec(s)
    s.loader.exec_module(o)
    return o

def choose(n,m):
    return math.comb(n,m) if 0<=m<=n else 0

def observed_taxon_prob(counts,n,m):
    """Exact inclusion probability under simple random sampling of m of n stops."""
    if not (0<=m<=n):raise ValueError("Invalid rarefaction sample size")
    denominator=choose(n,m)
    if denominator==0:raise ValueError("Empty sampling universe")
    result={}
    for name,k in counts.items():
        if not 0<=k<=n:raise ValueError("Taxon k larger than available sites")
        result[name]=1.-choose(n-k,m)/denominator
    return result

def stats_for_pools(positive,negative,m):
    if m<1 or m>min(len(positive),len(negative)):
        raise ValueError("Positive and negative matched sample sizes invalid")
    kp=Counter(sp for site in positive for sp in site)
    kn=Counter(sp for site in negative for sp in site)
    p=observed_taxon_prob(kp,len(positive),m)
    q=observed_taxon_prob(kn,len(negative),m)
    alltaxa=set(p)|set(q)
    pos=sum(p.values());neg=sum(q.values())
    shared=sum(p.get(t,0.)*q.get(t,0.) for t in alltaxa)
    unique_pos=sum(p.get(t,0.)*(1.-q.get(t,0.)) for t in alltaxa)
    unique_neg=sum(q.get(t,0.)*(1.-p.get(t,0.)) for t in alltaxa)
    delta=pos-neg
    if not math.isclose(delta,unique_pos-unique_neg,abs_tol=1e-11):
        raise RuntimeError("Expected shared/unique gamma exact identity broken")
    return {
       "gamma_positive":pos,"gamma_negative":neg,
       "delta_gamma":delta,"expected_shared_taxa":shared,
       "expected_unique_positive":unique_pos,"expected_unique_negative":unique_neg,
       "number_taxon_units_observed_across_both_groups":len(alltaxa)}

def randomized_pooled_beta(pos,neg,m,seed,draws=POOLED_DRAWS):
    rng=random.Random(seed)
    valid=0
    sor=sim=sne=0.
    for _ in range(draws):
        chosen_pos=rng.sample(range(len(pos)),m)
        chosen_neg=rng.sample(range(len(neg)),m)
        A=set().union(*(pos[i] for i in chosen_pos))
        B=set().union(*(neg[i] for i in chosen_neg))
        if not A or not B:continue
        a=len(A&B);b=len(A-B);c=len(B-A)
        bsor=(b+c)/(2*a+b+c)
        den=a+min(b,c)
        if den==0:continue
        bsim=min(b,c)/den
        bsne=bsor-bsim
        if bsne<-1e-12 or bsim<0 or bsne>1+1e-12:
            raise RuntimeError("Invalid incidence dissimilarity decomposition")
        valid+=1
        sor+=bsor;sim+=bsim;sne+=max(0,bsne)
    return {"valid":valid,"total":draws,
            "sor":sor/valid if valid else None,
            "turnover":sim/valid if valid else None,
            "nestedness_resultant":sne/valid if valid else None}

def source_data():
    source=mod("naamp_nwi_original_vegetation",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=source.read_nwi(
        ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
        ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if (not audit.get("preflight_eligible") or audit.get("mode")!="full"
        or audit["overlay"]["site_records"]!=5147
        or len(audit["overlay"]["shards"])!=12
        or audit["matched_route_source_only_audit"]["frog_outcomes_read"] is not False):
        raise RuntimeError("Frozen 12-shard vegetation source gate failed")
    if len(nwi)!=5147:raise RuntimeError("NWI physical site count changed")
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    if len(runs)!=7848:raise RuntimeError("Source standardized 7,848-run denominator drift")
    eligible=set(runs.RunID.astype(str))
    sampled,_=source.spatial.stop_matrix(raw,eligible)
    sites=source.hist.site_map(raw,eligible)
    ci=source.hist.ci_map(raw,eligible,sampled)
    stopenv=source.get_temps_and_detection(raw,runs,sampled)
    results=[]
    pem_comp=[]
    quality=Counter()
    m_counts=Counter()
    route_states={}
    for obs in runs.itertuples(index=False):
        rid=str(obs.RunID);state=str(obs.State);route=str(obs.route_cluster)
        route_no=str(obs.RouteNumber);year=int(obs.SurveyYear)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:raise RuntimeError("Ten-stop survey unexpectedly incomplete")
        ids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,route_no,str(sid)) not in nwi.index for sid in ids):
            quality["missing_10stop_nwi_link"]+=1
            continue
        if len(set(ids))!=10:
            quality["duplicate_physical_stop_site"]+=1
            continue
        if any(any(not np.isfinite(stopenv.get((rid,st),{}).get(key,np.nan))
            for key in ("stop_air_temp_c","stop_sound_index")) for st in stops):
            quality["missing_temperature_or_sound"]+=1
            continue
        context=nwi.loc[[(state,route_no,str(sid)) for sid in ids],list(FIELDS)]
        vals=context.to_numpy(dtype=float)
        if not np.isfinite(vals).all() or vals.min()<-1e-9 or vals.max()>1+1e-9:
            raise RuntimeError("Missing/out-of-range mapped NWI wetland fraction")
        quality["nwi_and_observation_complete_nights"]+=1
        if route in route_states and route_states[route]!=state:
            raise RuntimeError("Physical route key maps to multiple States")
        route_states[route]=state
        community={}
        for mode,threshold in MODES:
            community[mode]=[{str(t) for t,c in ci.get((rid,st),{}).items()
                              if int(c)>=threshold} for st in stops]
        for j,habitat in enumerate(HABITATS):
            flag=vals[:,j]>0
            nplus=int(flag.sum());nminus=10-nplus
            if not (0<nplus<10):
                quality[f"{habitat}_no_two_context_comparison"]+=1
                continue
            m=min(nplus,nminus)
            m_counts[(habitat,m)]+=1
            posindex=np.flatnonzero(flag).tolist()
            negindex=np.flatnonzero(~flag).tolist()
            for mode,_ in MODES:
                groups=community[mode]
                pos=[groups[k] for k in posindex]
                neg=[groups[k] for k in negindex]
                statistic=stats_for_pools(pos,neg,m)
                results.append({"state":state,"route":route,"run_id":rid,
                    "year":year,"habitat":habitat,"mode":mode,
                    "n_plus":nplus,"n_minus":nminus,"m":m,**statistic})
                quality["analysed_habitat_callmode_run_records"]+=1
                if habitat=="pem" and m>=2:
                    token=f"pem_rarefaction_199|{rid}|{mode}".encode("utf-8")
                    seed=int.from_bytes(hashlib.sha256(token).digest()[:8],"big")
                    p=randomized_pooled_beta(pos,neg,m,seed)
                    pem_comp.append({"state":state,"route":route,"run_id":rid,
                                     "year":year,"mode":mode,"m":m,**p})
    if quality["nwi_and_observation_complete_nights"]!=6236:
        raise RuntimeError(f"Original source-linked eligible sample 6,236 drift: {dict(quality)}")
    coverage={
        "NAAMP_standardized_nights":len(runs),"source_NWI_physical_sites":len(nwi),
        "NWI_complete_route_nights":quality["nwi_and_observation_complete_nights"],
        "NWI_complete_stop_nights":quality["nwi_and_observation_complete_nights"]*10,
        "all_eligible_source_routes":len(route_states),
        "all_eligible_source_states":len(set(route_states.values())),
        "quality_counts":dict(quality),
        "rarefaction_matched_site_number_distribution":{
            h:{str(m):m_counts.get((h,m),0) for m in range(1,6)}
            for h in HABITATS},
        "mapped_NWI_nonoverlap_not_botanical_absence":True
    }
    return pd.DataFrame(results),pd.DataFrame(pem_comp),coverage

def sign_flip(values,seed,draws=FLIPS):
    v=np.asarray(values,float)
    rng=np.random.default_rng(seed)
    ref=abs(float(v.mean()))
    extreme=0
    for start in range(0,draws,300):
        n=min(300,draws-start)
        t=(rng.choice(np.asarray([-1.,1.]),size=(n,len(v)))@v)/len(v)
        extreme+=int(np.count_nonzero(np.abs(t)>=ref-1e-14))
    return {"draws":draws,"extreme_draws":extreme,
       "p_plus_one_two_sided":(extreme+1)/(draws+1),
       "whole_route_independent_symmetric_null_not_plant_randomization":True}

def route_summary(data,seed,require_m_two=True):
    if require_m_two:data=data[data.m>=2]
    if data.empty:return {"status":"no_eligible_mapped_habitat"}
    grouped=data.groupby(["state","route"],sort=False)
    cluster=grouped[["delta_gamma","gamma_positive","gamma_negative",
        "expected_unique_positive","expected_unique_negative",
        "expected_shared_taxa"]].mean().reset_index()
    routes=len(cluster);states=int(cluster.state.nunique())
    d=data["delta_gamma"].to_numpy(float)
    out={
       "status":"estimated" if routes>=30 and states>=5 else "underpowered",
       "matched_route_nights":int(data.run_id.nunique()),
       "routes":routes,"states":states,
       "source_matched_site_number_counts":{str(int(m)):int(v) for m,v in data.m.value_counts().items()},
       "raw_equal_nights_delta_gamma":float(d.mean()),
       "route_equal_expected_gamma_positive":float(cluster.gamma_positive.mean()),
       "route_equal_expected_gamma_negative":float(cluster.gamma_negative.mean()),
       "route_equal_expected_shared_taxa":float(cluster.expected_shared_taxa.mean()),
       "route_equal_expected_unique_positive":float(cluster.expected_unique_positive.mean()),
       "route_equal_expected_unique_negative":float(cluster.expected_unique_negative.mean())}
    vals=cluster.delta_gamma.to_numpy(float)
    effect=float(vals.mean())
    out["route_equal_delta_gamma"]=effect
    out["state_equal_delta_gamma"]=float(cluster.groupby("state").delta_gamma.mean().mean())
    out["routes_positive_fraction"]=float(np.mean(vals>0))
    ss=cluster.groupby("state").delta_gamma.mean()
    out["states_positive_count"]=int((ss>0).sum())
    out["states_covered"]=list(sorted(ss.index))
    out["all_states"]=ss.to_dict()
    for label,subset in (("early",data[data.year<=2009]),("late",data[data.year>=2010])):
        cx=subset.groupby("route").delta_gamma.mean()
        out[label+"_2001_2009" if label=="early" else label+"_2010_2015"]={
            "routes":int(len(cx)),"route_mean":float(cx.mean()) if len(cx) else None}
    loo={}
    for state in sorted(ss.index):
        sub=cluster[cluster.state!=state]
        if len(sub)>=20:
            loo[state]=float(sub.delta_gamma.mean())
    out["omit_one_state_summary"]={
         "tested":len(loo),"positive":sum(v>0 for v in loo.values()),
         "negative":sum(v<0 for v in loo.values()),
         "min":min(loo.values()) if loo else None,
         "max":max(loo.values()) if loo else None}
    if out["status"]=="estimated":
        se=float(vals.std(ddof=1)/math.sqrt(routes))
        crit=float(student_t.ppf(.975,routes-1))
        ci=[effect-crit*se,effect+crit*se]
        p=float(2*student_t.sf(abs(effect/se),routes-1)) if se>0 else 1.
        out.update({"se_route":se,"ci95_route":ci,
                    "p_two_sided_route_t":p,
                    "route_sign_flip":sign_flip(vals,seed)})
    return out

def bh(results):
    if len(results)!=8:raise RuntimeError("All 8 pre-fixed class × call thresholds required")
    ids=sorted(range(len(results)),key=lambda i:
               results[i].get("p_two_sided_route_t",1.) if results[i]["status"]=="estimated" else 1.)
    q=1.
    for ii in range(len(ids)-1,-1,-1):
        i=ids[ii]
        x=results[i]
        p=x["p_two_sided_route_t"] if x["status"]=="estimated" else 1.
        q=min(q,8*p/(ii+1))
        x["BH_q_eight_primary"]=q
        ci=x.get("ci95_route")
        x["route_supported_observational_gamma_excess"]=bool(
              x["status"]=="estimated" and ci is not None
              and (ci[0]>0 or ci[1]<0) and q<.05)

def composition(pem):
    if pem.empty:return {"status":"no_PEM_matched_survey_data"}
    summaries={}
    for mode,_ in MODES:
        x=pem[pem["mode"]==mode].copy()
        if x.empty:
            summaries[mode]={"status":"no_PEM_valid_sample"}
            continue
        x["valid_frac"]=x["valid"]/x["total"]
        accepted=x[x.valid>0].copy()
        if accepted.empty:
            summaries[mode]={"status":"no_both_nonempty_taxon_subsamples",
                             "attempted_subsamples":int(x.total.sum())}
            continue
        route=accepted.groupby(["state","route"],sort=False)[[
            "valid_frac","sor","turnover","nestedness_resultant"]].mean().reset_index()
        # Ratio of route-equal mean component magnitudes, NOT a causal share.
        denom=float(route.sor.mean())
        m1=float(route.turnover.mean())
        m2=float(route.nestedness_resultant.mean())
        summaries[mode]={
            "status":"descriptive_valid" if x.valid.sum()>=.5*x.total.sum() and len(route)>=30
                else "insufficient_both_nonempty_group_subsamples",
            "n_route_nights_attempted":int(len(x)),
            "n_route_nights_with_any_valid_subsample":int(len(accepted)),
            "routes_with_valid_subsamples":int(len(route)),
            "states_with_valid_subsamples":int(route.state.nunique()),
            "subsamples_attempted":int(x.total.sum()),
            "subsamples_both_groups_nonempty":int(x.valid.sum()),
            "fraction_subsamples_valid":float(x.valid.sum()/x.total.sum()),
            "route_equal_beta_sorensen":denom,
            "route_equal_beta_simpson_turnover":m1,
            "route_equal_beta_nestedness_resultant":m2,
            "nestedness_fraction_of_route_balanced_Sorensen":m2/denom if denom>0 else None,
            "turnover_fraction_of_route_balanced_Sorensen":m1/denom if denom>0 else None,
            "numeric_sampling_draws_are_NOT_independent_biological_replicates":True}
        if not math.isclose(denom,m1+m2,abs_tol=1e-10):
            raise RuntimeError("Turnover+nestedness did not reconstruct route-balanced Sorensen")
    return summaries

def synthetic():
    # Complete enumeration validates E_gamma, unique/shared identities, and
    # correct without-replacement rarefaction, not a biology simulation.
    plus=[{"A","B"},{"A"},{"B","C"}]
    minus=[{"A"},{"D"},{"A","D"}]
    m=2
    out=stats_for_pools(plus,minus,m)
    import itertools
    gamma_p=np.mean([len(set().union(*(plus[i] for i in inds)))
                   for inds in itertools.combinations(range(3),m)])
    gamma_n=np.mean([len(set().union(*(minus[i] for i in inds)))
                   for inds in itertools.combinations(range(3),m)])
    if not math.isclose(out["gamma_positive"],gamma_p,abs_tol=1e-12):
        raise AssertionError("Exact expected gamma plus doesn't match enumeration")
    if not math.isclose(out["gamma_negative"],gamma_n,abs_tol=1e-12):
        raise AssertionError("Exact expected gamma minus doesn't match enumeration")
    q=randomized_pooled_beta(plus,minus,m,2601023,draws=199)
    if q["valid"]!=199 or not math.isclose(
        q["sor"],q["turnover"]+q["nestedness_resultant"],abs_tol=1e-12):
        raise AssertionError("Paired community beta decomposition invalid")
    result={"status":"PASS","manual_enumerated_3choose2_gamma_positive":gamma_p,
            "manual_enumerated_3choose2_gamma_negative":gamma_n,
            "exact_probability_matches_bruteforce":True,
            "expected_unique_shared_identity":True,
            "sorensen_partition":True}
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_rarefied_vegetation_gamma")
    ap.add_argument("--synthetic-only",action="store_true")
    args=ap.parse_args()
    qa=synthetic()
    if args.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    df,pem,scope=source_data()
    main_results=[]
    secondary={}
    idx=0
    for h in HABITATS:
        for mode,_ in MODES:
            subset=df[(df.habitat==h)&(df["mode"]==mode)]
            fitted=route_summary(subset,SEED+idx,require_m_two=True)
            fitted["habitat"]=h
            fitted["mode"]=mode
            main_results.append(fitted)
            simplified=route_summary(subset,SEED+idx+100,require_m_two=False)
            secondary[h+"|"+mode]=simplified
            idx+=1
    bh(main_results)
    comp=composition(pem)
    result={
        "analysis":"NAAMP_250m_NWI_rarefied_community_gamma_and_PEM_beta_parts_v0_1",
        "status":"source_matched_real_community_rarefaction_executed",
        "date":"2026-10-23",
        "hypothesis_plan":SPEC,
        "original_study_is_posthoc":True,
        "synthetic_QA":qa,
        "source_coverage":scope,
        "main_m_at_least_2_stratified_gamma":main_results,
        "m_at_least_1_coverage_sensitivity":secondary,
        "PEM_subsampled_pool_composition":comp,
        "science_boundaries":{
            "inference_is_species_detection_not_occupancy":True,
            "wetland_mapped_class_not_actual_2001_2015_plant":True,
            "same_run_sites_visited_sequentially":True,
            "independent_unit_for_t_and_signflip_is_route":True,
            "field_measured_insects_or_fish_available":False,
            "plant_causal_gamma_effect_identified":False,
            "species_interaction_or_three_body_effect_identified":False,
            "JAE_RC6_main_SI_submission_modified":False}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(
      json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("NAAMP_RAREFIED_GAMMA_RESULT_BEGIN",flush=True)
    print(json.dumps({"status":result["status"],"source":scope,
           "qa":qa,"main":main_results,
           "PEM_beta":comp,
           "secondary_m1":{k:{"routes":v.get("routes"),
                    "delta_gamma":v.get("route_equal_delta_gamma"),
                    "status":v["status"]} for k,v in secondary.items()}},
           sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_RAREFIED_GAMMA_RESULT_END",flush=True)

if __name__=="__main__":
    main()
