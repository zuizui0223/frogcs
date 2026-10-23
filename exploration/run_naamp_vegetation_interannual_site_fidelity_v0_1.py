#!/usr/bin/env python3
"""Exact interannual frog acoustic site-identity recurrence in PEM vs other wetlands.

Source: unchanged USGS NAAMP 2001–2015 source, USFWS NWI verified 250m
5,147 physical site geography. All 6,236 NWI-complete ten-stop surveys.
Uses same physical stations at adjacent observed monitoring YEARS and the
same annual RunNumber. The full assemblage of the later year is compared
with itself versus habitat-constrained swaps across different physical sites.

Post-hoc temporal macroecology, NOT plant manipulation, interspecific
interactions, true occupied sites, animal survival or model prediction.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
SPEC="exploration/NAAMP_VEGETATION_INTERANNUAL_SITE_FIDELITY_SPEC_2026_10_23.md"
FLIPS=4999
SEED=26010231
MODES=(("any",1),("strong",2))

def loader(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    if spec is None or spec.loader is None:raise RuntimeError("Missing vetted previous source "+str(path))
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def habitat_match(A,B,m,activation_only=False):
    """Exact E[m-site own-site overlap - random match within selected m stops]."""
    if len(A)!=len(B):
        raise ValueError("Time series should have the same physical sites and order")
    n=len(A)
    if not 2<=m<=n:raise ValueError("At least two and at most n matched sites")
    X=np.zeros((n,n),float)
    for i in range(n):
        for j in range(n):
            if activation_only:
                X[i,j]=float(bool(A[i]) and bool(B[j]))
            else:
                X[i,j]=len(A[i]&B[j])
    diag=float(np.trace(X)/n)
    off=float((np.sum(X)-np.trace(X))/(n*(n-1)))
    matched=(m-1)/m*(diag-off)
    return {"n_sites":n,"matched_n_sites":m,
            "own_exact_same_site_overlap":diag,
            "unmatched_different_site_overlap":off,
            "expected_equal_m_site_fidelity":matched}

def synthetic_qa():
    a=[{"x","y"},{"x"},{"z"},{"t","x"}]
    b=[{"x","y"},{"z"},{"x"},{"t"}]
    for m in (2,3,4):
        result=habitat_match(a,b,m)
        brute=[]
        for subset in itertools.combinations(range(len(a)),m):
            own=np.mean([len(a[i]&b[i]) for i in subset])
            perm=np.mean([
                np.mean([len(a[i]&b[j]) for i,j in zip(subset,permidx)])
                for permidx in itertools.permutations(subset)])
            brute.append(own-perm)
        if not math.isclose(float(np.mean(brute)),
                            result["expected_equal_m_site_fidelity"],abs_tol=1e-12):
            raise AssertionError("Exact hypergeometric within-habitat site-fidelity identity failed")
        A=habitat_match(a,b,m,activation_only=True)
        bruteact=[]
        for subset in itertools.combinations(range(len(a)),m):
            own=np.mean([float(bool(a[i]) and bool(b[i])) for i in subset])
            null=np.mean([np.mean([
                      float(bool(a[i]) and bool(b[j])) for i,j in zip(subset,permidx)])
                for permidx in itertools.permutations(subset)])
            bruteact.append(own-null)
        if not math.isclose(A["expected_equal_m_site_fidelity"],float(np.mean(bruteact)),abs_tol=1e-12):
            raise AssertionError("Binary acoustic activation identity failed")
    single=[{"s1"},{"s2"},{"s3"}]
    same=habitat_match(single,single,2)
    if not same["expected_equal_m_site_fidelity"]>0:
        raise AssertionError("Cannot detect known stable species-specific site identity")
    empty=habitat_match([set(),set()],[set(),set()],2)
    if empty["expected_equal_m_site_fidelity"]!=0:
        raise AssertionError("Two silent sites must yield zero identity recurrence")
    return {
        "status":"PASS",
        "exact_all_subset_all_permutation_identity":True,
        "site_activation_formula_identical":True,
        "two_silent_sites_zero":True,
        "known_same_species_same_site_signal_detected":True,
        "no_NAAMP_outcomes_used_for_QA":True}

def read_original():
    src=loader("source_vegetation",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=src.read_nwi(
       ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
       ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if not audit.get("preflight_eligible") or audit.get("mode")!="full":
        raise RuntimeError("Original NWI response-blind GIS preflight no longer passes")
    if len(audit["overlay"]["shards"])!=12 or audit["overlay"]["site_records"]!=5147 or len(nwi)!=5147:
        raise RuntimeError("NWI original geographical source drift")
    if audit["matched_route_source_only_audit"]["frog_outcomes_read"] is not False:
        raise RuntimeError("Spatial NWI source is not response-blind")
    raw=src.hist.load_retry()
    runs,_=src.base.build_runs(raw)
    if len(runs)!=7848:
        raise RuntimeError("7,848 original normalized source survey nights unexpectedly changed")
    elig=set(runs.RunID.astype(str))
    sampled,_=src.spatial.stop_matrix(raw,elig)
    sites=src.hist.site_map(raw,elig)
    calling=src.hist.ci_map(raw,elig,sampled)
    env=src.get_temps_and_detection(raw,runs,sampled)
    observers={str(o.get("RunID") or "").strip():str(o.get("ObserverTrackingID") or "").strip()
               for o in raw["Runs.csv"]}
    good={}
    coverage=Counter()
    state_routes=defaultdict(set)
    for item in runs.itertuples(index=False):
        rid=str(item.RunID)
        st=sorted(sampled.get(rid,set()),key=int)
        if len(st)!=10:raise RuntimeError("Normalized input no longer has exactly ten stops")
        ids=[sites.get((rid,x)) for x in st]
        if any(sid is None or (str(item.State),str(item.RouteNumber),str(sid)) not in nwi.index
               for sid in ids):
            coverage["NWI_missing_full_10_stops"]+=1
            continue
        if len(set(ids))!=10:
            coverage["nonunique_stop_SiteIDs"]+=1
            continue
        if any(any(not np.isfinite(env.get((rid,s),{}).get(k,np.nan))
                   for k in ("stop_air_temp_c","stop_sound_index")) for s in st):
            coverage["missing_sound_or_temperature"]+=1
            continue
        matched=nwi.loc[[(str(item.State),str(item.RouteNumber),str(sid)) for sid in ids],
                        ["nwi_emergent_cover_250m","nwi_all_wetland_cover_250m"]]
        V=matched.to_numpy(dtype=float)
        if not np.isfinite(V).all() or (V<-1e-9).any() or (V>1+1e-9).any():
            raise RuntimeError("Source NWI fractional overlap is invalid, cannot impute mapped absence")
        if np.any((V[:,0]>0)&(V[:,1]<=0)):
            raise RuntimeError("PEM mapped polygon site is not included in total mapped wetlands")
        state=str(item.State)
        route=str(item.route_cluster)
        if route!=state+":"+str(item.RouteNumber):raise RuntimeError("Route key mismatch")
        key=(state,str(item.RouteNumber),str(item.RunNumber))
        good[rid]={
            "rid":rid,"route":route,"state":state,
            "route_no":str(item.RouteNumber),"round":str(item.RunNumber),
            "year":int(item.SurveyYear),"doy":int(item.doy),
            "rain":float(item.DaysSinceRain),"mean_temp":float(item.mean_temp_c),
            "observer":observers.get(rid,""),
            "runstratum":key,"SiteIDs":tuple(str(v) for v in ids),
            "PEM":tuple(bool(v) for v in V[:,0]>0),
            "wetland":tuple(bool(v) for v in V[:,1]>0),
            "stops":tuple(st)}
        coverage["NWI_and_env_complete_run_nights"]+=1
        state_routes[state].add(route)
    if coverage["NWI_and_env_complete_run_nights"]!=6236 or len(good)!=6236:
        raise RuntimeError(f"Original 6,236 NWI-complete survey nights drift: {dict(coverage)}")
    if len({x["route"] for x in good.values()})!=499 or len(state_routes)!=20:
        raise RuntimeError("Source 499-route/20-State ecosystem coverage changed")
    metadata={"original_normalized_nights":7848,
              "NWI_environment_complete_nights":6236,
              "source_SiteID_records":len(nwi),
              "source_physical_routes":499,"source_states":20,
              "source_original_GIS_run":39450277196,
              "source_coverage_QA":dict(coverage)}
    return good,calling,metadata

def build_matched_pairs(good,calling):
    strata=defaultdict(lambda:defaultdict(list))
    for rid,row in good.items():
        strata[row["runstratum"]][row["year"]].append(rid)
    observations=[]
    counters=Counter()
    site_m_distribution=Counter()
    gap_distribution=Counter()
    for stratum,years in strata.items():
        unique={}
        for year,ids in years.items():
            if len(ids)==1:unique[year]=ids[0]
            else:
                counters["ambiguous_duplicate_year_groups_excluded"]+=1
                counters["duplicate_year_survey_runs_excluded"]+=len(ids)
        order=sorted(unique)
        if len(order)<2:continue
        for y1,y2 in zip(order[:-1],order[1:]):
            before=good[unique[y1]]
            after=good[unique[y2]]
            counters["adjacent_observed_year_pairs_before_SiteID_and_NWI_gate"]+=1
            if y2<=y1:raise RuntimeError("Chronological years not strictly increasing")
            if before["stops"]!=after["stops"] or before["SiteIDs"]!=after["SiteIDs"]:
                counters["same_route_moved_physical_station_SiteID_pairs_excluded"]+=1
                continue
            if before["PEM"]!=after["PEM"] or before["wetland"]!=after["wetland"]:
                raise RuntimeError("Static NWI source unexpectedly changed across actual physical sites")
            wet=np.asarray(before["wetland"],bool)
            pem=np.asarray(before["PEM"],bool)
            ip=np.flatnonzero(wet&pem)
            ineg=np.flatnonzero(wet&~pem)
            m=min(len(ip),len(ineg))
            if m<2:
                counters["static_environment_lacks_2_PEM_and_2_other_wetland_stops"]+=1
                continue
            counters["paired_year_exact_SiteIDs_and_mixed_PEM_wetland"]+=1
            gap_distribution[y2-y1]+=1
            site_m_distribution[m]+=1
            same_obs=bool(before["observer"] and before["observer"]==after["observer"])
            counters["same_observer_adjacent_pairs"]+=int(same_obs)
            row={
                "state":before["state"],"route":before["route"],
                "run_round":before["round"],
                "rid_before":before["rid"],"rid_after":after["rid"],
                "year_before":y1,"year_after":y2,"year_gap":y2-y1,
                "DOY_gap_abs":abs(before["doy"]-after["doy"]),
                "temp_gap_abs":abs(before["mean_temp"]-after["mean_temp"]),
                "days_since_rain_gap_abs":abs(before["rain"]-after["rain"]),
                "same_observer":same_obs,
                "m":m,"n_PEM":len(ip),"n_other_wetland":len(ineg)}
            for mode,threshold in MODES:
                A=[{t for t,c in calling.get((before["rid"],s),{}).items() if c>=threshold}
                   for s in before["stops"]]
                B=[{t for t,c in calling.get((after["rid"],s),{}).items() if c>=threshold}
                   for s in after["stops"]]
                p=habitat_match([A[i] for i in ip],[B[i] for i in ip],m)
                n=habitat_match([A[i] for i in ineg],[B[i] for i in ineg],m)
                pa=habitat_match([A[i] for i in ip],[B[i] for i in ip],m,True)
                na=habitat_match([A[i] for i in ineg],[B[i] for i in ineg],m,True)
                row[f"recurrence_excess_PEM_{mode}"]=p["expected_equal_m_site_fidelity"]
                row[f"recurrence_excess_nonPEM_{mode}"]=n["expected_equal_m_site_fidelity"]
                row[f"site_fidelity_PEM_minus_other_{mode}"]=p["expected_equal_m_site_fidelity"]-n["expected_equal_m_site_fidelity"]
                row[f"activation_excess_PEM_{mode}"]=pa["expected_equal_m_site_fidelity"]
                row[f"activation_excess_nonPEM_{mode}"]=na["expected_equal_m_site_fidelity"]
                row[f"activation_PEM_minus_other_{mode}"]=pa["expected_equal_m_site_fidelity"]-na["expected_equal_m_site_fidelity"]
                row[f"same_site_taxa_PEM_{mode}"]=p["own_exact_same_site_overlap"]
                row[f"other_site_taxa_PEM_{mode}"]=p["unmatched_different_site_overlap"]
                row[f"same_site_taxa_nonPEM_{mode}"]=n["own_exact_same_site_overlap"]
                row[f"other_site_taxa_nonPEM_{mode}"]=n["unmatched_different_site_overlap"]
            observations.append(row)
    if not observations:raise RuntimeError("No mapped vegetation-matched interannual frog route pairs")
    scope={
      "source_NWI_complete_run_nights":6236,
      "adjacent_observed_year_pairs_before_SiteID_and_NWI_gate":counters["adjacent_observed_year_pairs_before_SiteID_and_NWI_gate"],
      "physically_stable_vegetation_mixed_source_run_pairs":len(observations),
      "n_physical_routes":len({o["route"] for o in observations}),
      "n_states":len({o["state"] for o in observations}),
      "n_distinct_study_year_pair_windows":len({(o["year_before"],o["year_after"]) for o in observations}),
      "year_gap_distribution":{str(k):int(v) for k,v in sorted(gap_distribution.items())},
      "equal_m_site_matching_distribution":{str(k):int(v) for k,v in sorted(site_m_distribution.items())},
      "source_exclusions":dict(counters),
      "no_frog_outcome_based_pair_sampling":True,
      "exact_physical_SiteID_alignment":True,
      "same_seasonal_RunNumber_across_years":True}
    return pd.DataFrame(observations),scope

def signflip(x,seed,draws=FLIPS):
    rng=np.random.default_rng(seed)
    target=abs(float(np.mean(x)))
    extreme=0
    for start in range(0,draws,350):
        batch=min(350,draws-start)
        vals=(rng.choice(np.array([-1.,1.]),size=(batch,len(x)))@x)/len(x)
        extreme+=int(np.count_nonzero(np.abs(vals)>=target-1e-14))
    return {"draws":draws,"extreme":extreme,
            "p_two_sided_plus_one":(extreme+1)/(draws+1),
            "assumes_independent_symmetric_physical_route_effects":True}

def clustered_contrast(df,mode,seed):
    col=f"site_fidelity_PEM_minus_other_{mode}"
    route=df.groupby(["state","route"],sort=False)[col].mean().reset_index()
    n=len(route);states=route.state.nunique()
    result={
        "run_year_pair_count":int(len(df)),
        "physical_route_count":int(n),
        "state_count":int(states),
        "survey_pair_mean_unbalanced":float(df[col].mean()),
        "route_equal_mean":float(route[col].mean()),
        "route_equal_mean_PEM_excess":float(df.groupby("route")[f"recurrence_excess_PEM_{mode}"].mean().mean()),
        "route_equal_mean_other_wetland_excess":float(df.groupby("route")[f"recurrence_excess_nonPEM_{mode}"].mean().mean()),
        "route_equal_mean_PEM_same_site_taxa":float(df.groupby("route")[f"same_site_taxa_PEM_{mode}"].mean().mean()),
        "route_equal_mean_other_wetland_same_site_taxa":float(df.groupby("route")[f"same_site_taxa_nonPEM_{mode}"].mean().mean()),
        "route_equal_mean_PEM_other_site_taxa":float(df.groupby("route")[f"other_site_taxa_PEM_{mode}"].mean().mean()),
        "route_equal_mean_nonPEM_other_site_taxa":float(df.groupby("route")[f"other_site_taxa_nonPEM_{mode}"].mean().mean()),
        "activation_site_identity_PEM_minus_other_descriptive":float(
            df.groupby("route")[f"activation_PEM_minus_other_{mode}"].mean().mean()),
        "route_positive_fraction":float(np.mean(route[col]>0)),
        "state_equal_mean":float(route.groupby("state")[col].mean().mean()),
        "positive_state_count":int((route.groupby("state")[col].mean()>0).sum()),
        "note":"A/B groups equal-m rarefaction recurrence beyond random B-site identity within each mapped wetland stratum"}
    if n<30 or states<5 or len(df)<100:
        result["status"]="insufficient_spatiotemporal_replication"
        return result
    x=route[col].to_numpy(float)
    effect=float(np.mean(x))
    sd=float(np.std(x,ddof=1));se=sd/math.sqrt(n)
    if se<=1e-12:raise RuntimeError("No route variation; cannot calculate route-cluster uncertainty")
    tcrit=float(student_t.ppf(.975,n-1))
    ci=[effect-tcrit*se,effect+tcrit*se]
    result.update({
        "status":"estimated_observational_temporal_context",
        "route_se":se,"route_Student_CI95":ci,
        "route_t_two_sided_P":float(2*student_t.sf(abs(effect/se),n-1)),
        "whole_route_signflip":signflip(x,seed)})
    state=route.groupby("state")[col].mean()
    if states>=5:
        se_state=float(state.std(ddof=1)/math.sqrt(states))
        qs=float(student_t.ppf(.975,states-1))
        result["state_equal_Student_CI95"]=[
            float(state.mean()-qs*se_state),float(state.mean()+qs*se_state)]
    loo={name:float(route.loc[route.state!=name,col].mean()) for name in state.index}
    result["omit_one_State"]={
        "n_checked":len(loo),
        "n_positive":sum(v>0 for v in loo.values()),
        "n_negative":sum(v<0 for v in loo.values()),
        "range":[min(loo.values()),max(loo.values())]}
    result["descriptive_year_gap"]={}
    for name,dd in (("exactly_one_year",df.loc[df.year_gap==1]),
                    ("longer_than_one_year",df.loc[df.year_gap>1])):
        grouped=dd.groupby("route")[col].mean()
        result["descriptive_year_gap"][name]={
            "route_pairs":int(len(dd)),
            "routes":int(len(grouped)),
            "mean_route":float(grouped.mean()) if len(grouped)>0 else None}
    sample=df.loc[df.same_observer]
    same=sample.groupby("route")[col].mean()
    result["same_ObserverTrackingID_only"]={
        "route_year_pairs":int(len(sample)),"routes":int(len(same)),
        "mean_route":float(same.mean()) if len(same) else None}
    if len(same)>=30 and len(sample)>=100:
        se_same=float(same.std(ddof=1)/math.sqrt(len(same)))
        if se_same>0:
            t=float(student_t.ppf(.975,len(same)-1))
            result["same_ObserverTrackingID_only"]["route_CI95"]=[
                float(same.mean()-t*se_same),float(same.mean()+t*se_same)]
    return result

def apply_BH(results):
    ps=[results[m].get("route_t_two_sided_P",1.) for m,_ in MODES]
    order=sorted(range(len(ps)),key=lambda i:ps[i])
    q=[1.,1.];running=1.
    for rank in range(2,0,-1):
        idx=order[rank-1]
        running=min(running,2*ps[idx]/rank)
        q[idx]=running
    for idx,(mode,threshold) in enumerate(MODES):
        x=results[mode]
        x["BH_q_two_call_modes"]=q[idx]
        ci=x.get("route_Student_CI95")
        x["positive_temporal_PEM_site_identity_excess_supported"]=bool(
            x["status"]=="estimated_observational_temporal_context"
            and ci is not None and ci[0]>0 and q[idx]<.05
            and x["omit_one_State"]["n_positive"]==x["omit_one_State"]["n_checked"])


def post_readback_individual_habitat_recurring_taxa(df):
    """Four post-readback route-cluster checks of each habitat's own F.
    This is a SECONDARY analysis added after observing positive means in the
    original execution; not an independent hypothesis or proof of site causality.
    """
    family=[]
    for mode,th in MODES:
        for envname in ("PEM","nonPEM"):
            col=f"recurrence_excess_{envname}_{mode}"
            route=df.groupby(["state","route"],sort=False)[col].mean().reset_index()
            n=len(route);states=route.state.nunique()
            mean=float(route[col].mean())
            state_means=route.groupby("state")[col].mean()
            o={"mode":mode,"habitat":envname,
               "route_year_pairs":int(len(df)),
               "physical_routes":int(n),"states":int(states),
               "route_mean_excess_recalled_taxa":mean,
               "State_equal_mean":float(state_means.mean()),
               "positive_State_means":int((state_means>0).sum()),
               "positive_route_fraction":float((route[col]>0).mean()),
               "post_readback_individual_habitat_question":True,
               "not_a_frog_demographic_persistence_estimate":True}
            if n<30 or states<5 or len(df)<100:
                o.update({"status":"insufficient_replication",
                          "route_t_p":1.})
                family.append(o);continue
            x=route[col].to_numpy(dtype=float)
            se=float(x.std(ddof=1)/math.sqrt(n))
            if se<=1e-12:raise RuntimeError("No variance in within-habitat temporal recurrence")
            ciwidth=float(student_t.ppf(.975,n-1))*se
            p=float(2*student_t.sf(abs(mean/se),n-1))
            o.update({"status":"estimated_post_readback",
                      "route_se":se,
                      "route_Student_CI95":[mean-ciwidth,mean+ciwidth],
                      "route_t_p":p,
                      "route_signflip":signflip(x,SEED+200+10*(th-1)+(0 if envname=="PEM" else 1))})
            loo={state:float(route.loc[route.state!=state,col].mean())
                 for state in state_means.index}
            o["omit_one_State"]={
                "n_checks":len(loo),
                "n_positive":sum(z>0 for z in loo.values()),
                "range":[min(loo.values()),max(loo.values())]}
            for gap,part in (
                ("one_year_gap",df.loc[df.year_gap==1]),
                ("multi_year_gap",df.loc[df.year_gap>1])):
                rr=part.groupby("route")[col].mean()
                o[gap]={"n_run_pairs":int(len(part)),
                        "n_routes":int(len(rr)),
                        "route_mean":float(rr.mean()) if len(rr) else None}
            same=df.loc[df.same_observer]
            sr=same.groupby("route")[col].mean()
            o["same_ObserverTrackingID_only"]={
                "n_adjacent_survey_year_pairs":int(len(same)),
                "n_routes":int(len(sr)),
                "route_mean":float(sr.mean()) if len(sr) else None}
            if len(sr)>=30 and len(same)>=100:
                ss=float(sr.std(ddof=1)/math.sqrt(len(sr)))
                if ss>0:
                    sc=float(student_t.ppf(.975,len(sr)-1))
                    o["same_ObserverTrackingID_only"]["route_CI95"]=[
                        float(sr.mean()-sc*ss),float(sr.mean()+sc*ss)]
            family.append(o)
    if len(family)!=4:raise RuntimeError("Post-readback family 2 classes x 2 calling thresholds lost")
    order=sorted(range(4),key=lambda i:family[i]["route_t_p"])
    q=1.
    for rank in range(4,0,-1):
        i=order[rank-1]
        q=min(q,4*family[i]["route_t_p"]/rank)
        family[i]["BH_q_four_post_readback_habitat_checks"]=q
        ci=family[i].get("route_Student_CI95")
        family[i]["positive_acoustic_site_identity_excess_exploratory"]=bool(
            family[i]["status"]=="estimated_post_readback"
            and ci is not None and ci[0]>0 and q<.05
            and family[i]["omit_one_State"]["n_positive"]==
                 family[i]["omit_one_State"]["n_checks"])
    return family

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,
                   default=ROOT/"build/naamp_interannual_PEM_site_fidelity")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    qa=synthetic_qa()
    if args.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    good,calling,source=read_original()
    pairs,coverage=build_matched_pairs(good,calling)
    output={mode:clustered_contrast(pairs,mode,SEED+offset)
            for offset,(mode,th) in enumerate(MODES)}
    apply_BH(output)
    within_habitat_postreadback=post_readback_individual_habitat_recurring_taxa(pairs)
    out={
        "analysis":"NAAMP_hierarchical_NWI_PEM_interannual_exact_physical_site_recurrence",
        "status":"real_NAAMP_repeated_physical_site_temporal_vegetation_macroanalysis_completed",
        "date":"2026-10-23",
        "locked_observational_spec":SPEC,
        "exploratory_not_preregistered_original_NAAMP_archive":True,
        "synthetic_QA":qa,
        "original_source":source,
        "interannual_pairs_scope":coverage,
        "acoustic_results":output,
        "post_readback_individual_habitat_route_tests":within_habitat_postreadback,
        "post_readback_spec":"exploration/NAAMP_TEMPORAL_SITE_ANCHORING_POSTREADBACK_SPEC_2026_10_23.md",
        "post_readback_tests_not_independent_original_hypothesis":True,
        "scientific_limits":{
            "not_predicting_any_future_site_outcomes":True,
            "survey_round_is_only_coarse_season_control":True,
            "NWI_250m_PEM_polygon_not_botanical_2001_2015_cover":True,
            "acoustic_taxon_recurrence_not_demographic_site_persistence":True,
            "no_evidence_of_individual_same_frogs":True,
            "site_recurrence_could_be_unmeasured_static_habitat":True,
            "not_causal_plant_or_multispecies_interaction":True,
            "species_listening_stations_visited_sequentially":True,
            "JAE_RC6_original_and_main_untouched":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("NAAMP_TEMPORAL_PEM_FIDELITY_BEGIN",flush=True)
    print(json.dumps({
        "status":out["status"],"synthetic_QA":qa,
        "original_source":source,"interannual_pairs_scope":coverage,
        "modes":output,
        "within_habitat_postreadback":within_habitat_postreadback,
        "scientific_limits":out["scientific_limits"]},
        sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_TEMPORAL_PEM_FIDELITY_END",flush=True)

if __name__=="__main__":
    main()
