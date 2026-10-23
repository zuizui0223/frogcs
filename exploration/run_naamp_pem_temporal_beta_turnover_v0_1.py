#!/usr/bin/env python3
"""Real NAAMP mapped PEM frog acoustic temporal Sørensen, turnover and nestedness.

Exactly the original 1115 route-year / 2869 night / 274 physical-route within-
year source archive, USFWS NWI 250m wetland map. Matched two physical stations
held constant across same two survey rounds; analytic hypergeometric taxon-
count expectations, NOT mean of pair-subsample beta indices. Six pre-fixed
route-cluster/State/BH tests, conditioning on both habitat pools having calls
in both rounds. No species interactions, vegetation causality or forecasting.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
WITHINYEAR=ROOT/"exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py"
TWO_ROUND=ROOT/"exploration/run_naamp_wetland_seasonal_complementarity_v0_1.py"
SPEC="exploration/NAAMP_PEM_TEMPORAL_BETA_TURNOVER_NESTEDNESS_SPEC_2026_10_23.md"
MODE=("any","strong")
MODES=(("any",1),("strong",2))
TESTS=("delta_beta_sim_any","delta_beta_sor_any","delta_beta_sne_any",
       "delta_beta_sim_strong","delta_beta_sor_strong","delta_beta_sne_strong")
SEED=26010521
FLIPS=4999

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise RuntimeError("Original source dependency missing "+str(path))
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def ratios_of_expected_taxon_counts(A,B,m,two):
    if len(A)!=len(B) or m!=2 or len(A)<2:
        raise ValueError("Only original exactly same station sampling across rounds allowed")
    g=two.exact_two_round_pool(A,B,m)
    early=g["gamma_early"]
    late=g["gamma_late"]
    union=g["gamma_union_two_rounds"]
    a=early+late-union
    b=union-late
    c=union-early
    for k,v in (("shared",a),("early_only",b),("later_only",c)):
        if v< -1e-10:raise ValueError("Invalid negative acoustic incidence "+k)
    a=max(0.,a);b=max(0.,b);c=max(0.,c)
    if abs(union-(a+b+c))>1e-10:raise ValueError("Taxonomic union expected-count conservation failed")
    if abs(g["bonus_temporal_complementarity"]-(b+c)/2)>1e-10:
        raise ValueError("Source exact seasonal bonus not half of expected temporal unique labels")
    good=(early>1e-12 and late>1e-12 and a+min(b,c)>1e-12)
    sor=(b+c)/(2*a+b+c) if union>1e-12 else None
    if good:
        sim=min(b,c)/(a+min(b,c))
        sne=sor-sim
        if min(sor,sim,sne)<-1e-10 or max(sor,sim,sne)>1+1e-10:
            raise ValueError("Expected acoustic Sørensen component outside 0..1")
        if abs(sor-sim-sne)>1e-10:raise ValueError("Temporal beta decomposition not exact")
        sim=max(0.,sim);sne=max(0.,sne)
    else:
        sim=None;sne=None
    return {
        "status":"both_rounds_active" if good else ("silent_both_rounds" if union<=1e-12 else "single_round_silent_or_Simpson_undefined"),
        "gamma_early":early,"gamma_late":late,"gamma_union":union,
        "a_expected_shared":a,"b_expected_early_only":b,"c_expected_later_only":c,
        "bonus_original_temporal":g["bonus_temporal_complementarity"],
        "beta_sor_ratio_expected":sor,
        "beta_sim_ratio_expected":sim,
        "beta_sne_ratio_expected":sne,
        "jaccard_ratio_expected":(b+c)/union if union>1e-12 else None,
        "half_jaccard_equals_B_over_union":abs(.5*(b+c)/union-g["bonus_temporal_complementarity"]/union)<1e-12 if union>1e-12 else None,
        "valid_for_six_test_family":good}

def qa():
    original=load("original_exact_two_round",TWO_ROUND)
    known={
      "persistent":([{"a"},{"b"}],[{"a"},{"b"}]),
      "replacement":([{"a"},{"b"}],[{"c"},{"d"}]),
      "nestedness":([{"a","b"},{"a"}],[{"a"},{"a"}]),
      "silent":([set(),set()],[set(),set()]),
      "one_round_silent":([{"a"},set()],[set(),set()]),
      "mixed":([{"a","b"},{"a"},{"c"},set()],
               [{"a"},{"d"},{"b","c"},{"d"}])
    }
    out={}
    for key,(A,B) in known.items():
        computed=ratios_of_expected_taxon_counts(A,B,2,original)
        raw=[]
        for subset in itertools.combinations(range(len(A)),2):
            p=set().union(*(A[i] for i in subset))
            q=set().union(*(B[i] for i in subset))
            raw.append([len(p&q),len(p-q),len(q-p)])
        a,b,c=np.mean(np.asarray(raw,float),axis=0)
        if not all(math.isclose(computed[k],v,abs_tol=1e-12) for k,v in (
                ("a_expected_shared",a),("b_expected_early_only",b),
                ("c_expected_later_only",c))):
            raise AssertionError("Incorrect expected taxon overlap from fixed two-station subsampling "+key)
        if computed["valid_for_six_test_family"]:
            assert math.isclose(computed["beta_sor_ratio_expected"],
                       computed["beta_sim_ratio_expected"]+
                       computed["beta_sne_ratio_expected"],abs_tol=1e-12)
        out[key]={"status":computed["status"],
                  "beta_sor":computed["beta_sor_ratio_expected"],
                  "beta_sim":computed["beta_sim_ratio_expected"],
                  "beta_sne":computed["beta_sne_ratio_expected"]}
    assert out["persistent"]["beta_sor"]==0
    assert out["replacement"]["beta_sim"]==1 and out["replacement"]["beta_sne"]==0
    assert out["nestedness"]["beta_sne"]>0 and out["nestedness"]["beta_sim"]==0
    assert out["silent"]["status"]=="silent_both_rounds"
    assert out["one_round_silent"]["status"]=="single_round_silent_or_Simpson_undefined"
    return {
        "status":"PASS","all_fixed_two_station_subsets_enumerated_exact":True,
        "ratio_of_expected_taxon_overlap_NOT_average_of_beta_indices":True,
        "turnover_vs_nestedness_and_silence_gates":True,
        "all_source_free_test_cases":out,
        "no_NAAMP_outcomes_seen_in_qa":True}

def exact_source():
    src=load("original_naamp_same_site_season",WITHINYEAR)
    prior=load("original_NAAMP_two_round_pool",TWO_ROUND)
    good,calling,rare,source=src.source()
    census,coverage=src.build_rounds(good,calling,rare)
    if not (source["source_NAAMP_standard_runs"]==7848
       and source["source_NWI_complete_run_nights"]==6236
       and source["source_NWI_original_physical_SiteIDs"]==5147
       and len(census)==2869 and census.route_year_id.nunique()==1115
       and census.route.nunique()==274 and census.state.nunique()==20):
        raise RuntimeError("Original real NAAMP×NWI 1115 route-year cohort changed")
    return prior,good,calling,census,source,coverage

def observations(prior,good,calling,source_nights):
    bymode={mode:[] for mode in MODE}
    coverage=Counter()
    invalid={mode:Counter() for mode in MODE}
    roundcounts={mode:Counter() for mode in MODE}
    full_count=0
    anyunion_both={}
    for group,history in source_nights.groupby("route_year_id",sort=True):
        visits=[good[str(rid)] for rid in history.sort_values("round").rid]
        same=visits[0]
        pos=np.flatnonzero(np.asarray(same["pem"],bool)&np.asarray(same["wet"],bool))
        neg=np.flatnonzero(np.asarray(same["wet"],bool)&~np.asarray(same["pem"],bool))
        if len(pos)<2 or len(neg)<2:
            raise RuntimeError("Previously source-qualified vegetation context vanished")
        if any(v["physical_sites"]!=same["physical_sites"] or
               v["stoplabels"]!=same["stoplabels"] or
               v["pem"]!=same["pem"] or v["wet"]!=same["wet"]
               for v in visits[1:]):
            raise RuntimeError("Cannot call temporal turnover at relocated physical wetland stations")
        sets={}
        for v in visits:
            sets[int(v["round"])]={}
            for mode,threshold in MODES:
                sets[int(v["round"])][mode]=[
                  {str(t) for t,c in calling.get((v["rid"],st),{}).items() if int(c)>=threshold}
                  for st in same["stoplabels"]]
        for prev,nxt in itertools.combinations(visits,2):
            full_count+=1
            rlabel=str(prev["round"])+"-"+str(nxt["round"])
            for mode in MODE:
                x={}
                for cls,indices in (("PEM",pos),("other",neg)):
                    A=[sets[int(prev["round"])][mode][k] for k in indices]
                    B=[sets[int(nxt["round"])][mode][k] for k in indices]
                    res=ratios_of_expected_taxon_counts(A,B,2,prior)
                    x[cls]=res
                    invalid[mode][cls+"_"+res["status"]]+=1
                roundcounts[mode][rlabel]+=1
                if not x["PEM"]["valid_for_six_test_family"] or not x["other"]["valid_for_six_test_family"]:
                    invalid[mode]["ineligible_either_habitat_composition"]+=1
                    continue
                record={
                    "route_year_id":group,"state":same["state"],"route":same["route"],
                    "year":same["year"],"round_pair":rlabel,
                    "m_fixed_physical_sites":2,
                    "n_PEM_mapped_station_buffers":int(len(pos)),
                    "n_other_mapped_wetland_station_buffers":int(len(neg))
                }
                for habitat in ("PEM","other"):
                    h=x[habitat]
                    for old,new in (("beta_sor","beta_sor_ratio_expected"),
                                    ("beta_sim","beta_sim_ratio_expected"),
                                    ("beta_sne","beta_sne_ratio_expected"),
                                    ("jaccard","jaccard_ratio_expected"),
                                    ("shared_expected","a_expected_shared"),
                                    ("early_only_expected","b_expected_early_only"),
                                    ("late_only_expected","c_expected_later_only"),
                                    ("union_expected","gamma_union"),
                                    ("bonus_expected","bonus_original_temporal")):
                        record[f"{habitat}_{old}"]=h[new]
                for idx in ("beta_sor","beta_sim","beta_sne","jaccard",
                            "shared_expected","early_only_expected","late_only_expected",
                            "union_expected","bonus_expected"):
                    record["delta_"+idx]=record["PEM_"+idx]-record["other_"+idx]
                if abs(record["delta_beta_sor"]-record["delta_beta_sim"]-record["delta_beta_sne"])>1e-10:
                    raise RuntimeError("Temporal dissimilarity plant-class difference failed exact algebra")
                bymode[mode].append(record)
    expected=sum(math.comb(len(x),2) for gid,x in source_nights.groupby("route_year_id"))
    if full_count!=expected or full_count!=2475:
        raise RuntimeError("Original 2475 source survey-round pair opportunities drift")
    data={m:pd.DataFrame(rows) for m,rows in bymode.items()}
    out={
       "geographically_eligible_original_route_years":1115,
       "geographically_eligible_original_round_pairs":2475,
       "original_same_physical_site_survey_visits":2869,
       "original_independent_routes":274,"original_States":20,
       "by_call_threshold":{
         mode:{
           "n_original_round_pairs":int(sum(roundcounts[mode].values())),
           "n_valid_same_site_two_round_pairs_both_habitat_both_active":int(len(data[mode])),
           "n_excluded_one_or_more_habitat_silent":int(invalid[mode]["ineligible_either_habitat_composition"]),
           "n_valid_route_years":int(data[mode].route_year_id.nunique()),
           "n_valid_independent_routes":int(data[mode].route.nunique()),
           "n_valid_states":int(data[mode].state.nunique()),
           "habitat_silence_or_Simpson_diagnostics":dict(invalid[mode]),
           "original_round_pair_source_counts":dict(roundcounts[mode]),
           "valid_round_pair_counts":{str(k):int(v) for k,v in data[mode].round_pair.value_counts().items()}
         } for mode in MODE},
       "full_source_no_frog_outcome_filter_before_valid_beta_denominators":True,
       "beta_denominator_conditioning_uses_observed_calling":True
    }
    return data,out

def route_flips(x,seed):
    rng=np.random.default_rng(seed)
    v=np.asarray(x,float)
    obs=abs(float(np.mean(v)))
    ext=0
    for begin in range(0,FLIPS,320):
        k=min(320,FLIPS-begin)
        a=(rng.choice(np.asarray([-1.,1.]),size=(k,len(v)))@v)/len(v)
        ext+=int(np.count_nonzero(abs(a)>=obs-1e-14))
    return {"draws":FLIPS,"extreme":ext,"two_sided_plus_one_P":(ext+1)/(FLIPS+1),
            "one_flip_per_independent_physical_route":True,
            "route_symmetry_assumption_not_vegetation_randomized":True}

def estimates(df,outcome,seed):
    if df.empty:raise RuntimeError("No valid two-habitat acoustic beta pair")
    routeyear=df.groupby(["state","route","route_year_id"],sort=False)[outcome].mean().reset_index()
    groups=len(routeyear)
    routes=routeyear.groupby(["state","route"],sort=False)[outcome].mean().reset_index()
    n=len(routes);state=routes.groupby("state")[outcome].mean()
    S=len(state)
    if groups<150 or n<50 or S<5:
        raise RuntimeError("Fixed source matched-round beta validity too sparse; do not claim unsupported experiment")
    x=routes[outcome].to_numpy(float)
    mean=float(x.mean());se=float(x.std(ddof=1)/math.sqrt(n))
    if se<=1e-12:raise RuntimeError("No route-level acoustic beta variation")
    rc=float(student_t.ppf(.975,n-1))
    ps=float(2*student_t.sf(abs(mean/se),n-1))
    vals=state.to_numpy(float)
    s_mean=float(vals.mean())
    s_se=float(vals.std(ddof=1)/math.sqrt(S))
    sc=float(student_t.ppf(.975,S-1))
    leave={str(k):float(routes.loc[routes.state!=k,outcome].mean()) for k in state.index}
    return {
       "outcome":outcome,"n_original_valid_round_pairs":len(df),
       "n_route_year_averaged_groups":groups,
       "n_independent_routes":n,"n_States":S,
       "route_equal_beta_component_contrast":mean,
       "CI95_physical_route":[mean-rc*se,mean+rc*se],
       "route_Student_two_sided_P":ps,
       "route_signflip":route_flips(x,seed),
       "State_equal_contrast":s_mean,
       "CI95_States":[s_mean-sc*s_se,s_mean+sc*s_se],
       "State_mean_count_positive":int(np.count_nonzero(vals>0)),
       "omit_one_State":{"n_estimable":len(leave),
              "n_positive":sum(v>0 for v in leave.values()),
              "n_negative":sum(v<0 for v in leave.values()),
              "range":[min(leave.values()),max(leave.values())]},
       "m_fixed_sites_and_two_actual_rounds":True,
       "ratio_of_expected_counts_NOT_mean_of_subsample_beta":True,
       "conditioning_on_both_habitat_active_both_rounds":True}

def six_tests(bymode):
    definitions=(
       ("delta_beta_sim_any","any","delta_beta_sim"),
       ("delta_beta_sor_any","any","delta_beta_sor"),
       ("delta_beta_sne_any","any","delta_beta_sne"),
       ("delta_beta_sim_strong","strong","delta_beta_sim"),
       ("delta_beta_sor_strong","strong","delta_beta_sor"),
       ("delta_beta_sne_strong","strong","delta_beta_sne")
    )
    tests={}
    for i,(name,mode,col) in enumerate(definitions):
        tests[name]=estimates(bymode[mode],col,SEED+i)
    order=sorted(definitions,key=lambda t:tests[t[0]]["route_Student_two_sided_P"])
    running=1.
    for rank in range(len(order),0,-1):
        name=order[rank-1][0]
        running=min(running,6*tests[name]["route_Student_two_sided_P"]/rank)
        tests[name]["BH_q_six_original"]=running
    for name in tests:
        t=tests[name]
        direction=1 if t["route_equal_beta_component_contrast"]>0 else -1
        r=t["CI95_physical_route"];s=t["CI95_States"];p=t["route_signflip"]["two_sided_plus_one_P"]
        t["supported_exploratory_same_direction_across_routes_states"]=bool(
             ((r[0]>0 and s[0]>0) if direction>0 else (r[1]<0 and s[1]<0))
             and t["BH_q_six_original"]<.05 and p<.05
             and max(t["omit_one_State"]["n_positive"],
                     t["omit_one_State"]["n_negative"])>=.75*t["omit_one_State"]["n_estimable"])
    return tests

def description(bymode):
    result={}
    for mode,data in bymode.items():
        pyear=data.groupby(["state","route","route_year_id"],sort=False).mean(numeric_only=True).reset_index()
        routes=pyear.groupby(["state","route"],sort=False).mean(numeric_only=True)
        habitat={}
        for habitat_name in ("PEM","other"):
            habitat[habitat_name]={name:float(routes[f"{habitat_name}_{name}"].mean()) for name in (
                   "beta_sor","beta_sim","beta_sne","jaccard",
                   "shared_expected","early_only_expected","late_only_expected",
                   "union_expected","bonus_expected")}
            x=habitat[habitat_name]
            if abs(x["beta_sor"]-x["beta_sim"]-x["beta_sne"])>1e-10:
                raise RuntimeError("Population-level acoustic Sørensen partition identity lost")
            x["turnover_fraction_of_sorensen_at_equal_route_mean"] =(
                x["beta_sim"]/x["beta_sor"] if x["beta_sor"]>0 else None)
            x["nestedness_fraction_of_sorensen_at_equal_route_mean"] =(
                x["beta_sne"]/x["beta_sor"] if x["beta_sor"]>0 else None)
        between={}
        for pair,sub in data.groupby("round_pair"):
            rr=sub.groupby(["state","route","route_year_id"],sort=False).mean(numeric_only=True).reset_index()
            routes_pair=rr.groupby(["state","route"]).mean(numeric_only=True)
            between[pair]={"n_original_round_pairs":len(sub),
                           "route_year_groups":len(rr),
                           "independent_routes":int(sub.route.nunique()),
                           "n_States":int(sub.state.nunique()),
                           "delta_beta_sor":float(routes_pair.delta_beta_sor.mean()),
                           "delta_beta_sim":float(routes_pair.delta_beta_sim.mean()),
                           "delta_beta_sne":float(routes_pair.delta_beta_sne.mean()),
                           "no_additional_P_tests":True}
        result[mode]={"habitats":habitat,"round_pair_descriptives":between,
                      "route_year_groups_with_beta_defined":int(len(pyear)),
                      "physical_routes_with_beta_defined":int(data.route.nunique()),
                      "observed_beta_gated_not_same_as_full_gamma_source_population":True}
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_pem_temporal_beta")
    a.add_argument("--synthetic-only",action="store_true")
    args=a.parse_args()
    quality=qa()
    if args.synthetic_only:
        print(json.dumps(quality,sort_keys=True));return
    prior,good,calling,census,source,previous=exact_source()
    bymode,scope=observations(prior,good,calling,census)
    if any(scope["by_call_threshold"][m]["n_valid_route_years"]<150 for m in MODE):
        raise RuntimeError("Observed-call active source is too sparse for the predeclared 6-test ecological beta inference")
    tests=six_tests(bymode)
    descriptive=description(bymode)
    primary=tests["delta_beta_sim_any"]
    final=("exploratory_PEM_specific_temporal_acoustic_replacement"
           if primary["supported_exploratory_same_direction_across_routes_states"]
           else "no_robust_PEM_specific_temporal_replacement")
    out={
      "analysis":"NAAMP_same_footprint_PEM_vegetation_frog_temporal_beta_turnover_nestedness",
      "status":"real_source_complete_temporal_turnover_and_nestedness_macroanalysis_executed",
      "date":"2026-10-23",
      "frozen_spec":SPEC,
      "post_hoc_same_original_NAAMP_source_previously_examined":True,
      "synthetic_QA":quality,
      "source":{
         "original_NAAMP_standardized_route_nights":7848,
         "original_NWI_complete_route_nights":6236,
         "original_NWI_mapped_physical_SiteIDs":5147,
         "GIS_original_source_workflow":39450277196},
      "original_2869_same_site_acoustic_nights":previous,
      "per_call_threshold_conditioning_and_sample":scope,
      "six_frozen_two_sided_route_and_state_tests":tests,
      "primary_turnover_verdict":final,
      "route_balanced_component_and_round_pair_descriptives":descriptive,
      "scientific_boundaries":{
         "indices_are_ratios_of_exact_expected_taxon_counts_not_expected_indices":True,
         "observed_activity_eligibility_is_an_explicit_conditional_population":True,
         "NWI_polygon_not_contemporaneous_live_vegetation":True,
         "acoustic_taxa_are_source_monitoring_labels_not_demographic_individuals":True,
         "temporal_turnover_nonnestedness_not_proof_of_true_species_replacement":True,
         "no_frog_frog_or_fish_insect_causal_effects_identified":True,
         "not_a_prediction_or_forecasting_model":True,
         "JAE_RC6_main_SI_manuscript_submissions_unmodified":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("NAAMP_PEM_TEMPORAL_BETA_BEGIN",flush=True)
    print(json.dumps({"status":out["status"],"QA":quality,"scope":scope,
                       "six_tests":tests,"verdict":final,"description":descriptive},
                       sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_PEM_TEMPORAL_BETA_END",flush=True)

if __name__=="__main__":
    main()
