#!/usr/bin/env python3
"""NAAMP×NWI frog seasonal community complementarity, not prediction.

Same exact ten physical monitoring stops in one route and calendar year,
2–4 source survey rounds, two uniformly selected rounds, equal m>=2 wetland
stations in mapped emergent/PEM and mapped nonPEM wetland. Uses exact site
hypergeometric probabilities to disentangle a two-round taxon pool from
one-round pool size, instead of re-testing source vegetation alpha richness.

Ecological unit: State > physical route > route-year > two-round subsets >
same physically aligned stops > acoustic taxon labels (not individuals).
All route-year round pairs are averaged BEFORE the route-level analysis.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py"
PROTOCOL="exploration/NAAMP_WETLAND_WITHINYEAR_TEMPORAL_COMPLEMENTARITY_SPEC_2026_10_23.md"
MODES=(("any",1),("strong",2))
HABITATS=("PEM","other")
TESTS=("bonus_any","bonus_strong","gamma_two_any","gamma_two_strong")
SEED=26010235
FLIPS=4999

def import_source():
    spec=importlib.util.spec_from_file_location("naamp_existing_withinyear_source",SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Original validated site and round source unavailable")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def absence_probability(n,k,m):
    if not 0<=k<=n or not 1<=m<=n:
        raise ValueError("Invalid site richness frequencies for exact m-site sampling")
    return math.comb(n-k,m)/math.comb(n,m) if n-k>=m else 0.

def exact_two_round_pool(sites_before,sites_after,m):
    """Uniformly choose SAME m physical stations in both acoustic rounds."""
    if len(sites_before)!=len(sites_after) or m<2 or m>len(sites_before):
        raise ValueError("Matched physical-site group or sample effort changed")
    n=len(sites_before)
    before=[set(x) for x in sites_before]
    after=[set(x) for x in sites_after]
    per_site_union=[before[i]|after[i] for i in range(n)]
    taxa=set().union(*per_site_union)
    g1=g2=g_union=new_after=early_only=0.
    for taxon in taxa:
        k1=sum(taxon in x for x in before)
        k2=sum(taxon in x for x in after)
        ku=sum(taxon in x for x in per_site_union)
        if ku<max(k1,k2):
            raise RuntimeError("Union site incidence lost an observed taxon")
        p1=absence_probability(n,k1,m)
        p2=absence_probability(n,k2,m)
        pu=absence_probability(n,ku,m)
        g1+=1-p1
        g2+=1-p2
        g_union+=1-pu
        new_after+=p1-pu   # later round detected but not earlier
        early_only+=p2-pu  # earlier round detected but not later
    singles=.5*(g1+g2)
    bonus=g_union-singles
    if bonus<-1e-10 or g_union+1e-10<max(g1,g2):
        raise RuntimeError("Two-round acoustic species pool must include each visit")
    if not math.isclose(bonus,.5*(new_after+early_only),abs_tol=1e-10):
        raise RuntimeError("Temporal gain versus loss accounting identity not exact")
    if not math.isclose(g_union,singles+bonus,abs_tol=1e-10):
        raise RuntimeError("Two-round acoustic pooled gamma decomposition broken")
    shared=g1+g2-g_union
    if shared< -1e-10:
        raise RuntimeError("Negative early/late acoustic species overlap")
    return {
      "n_sites":n,"matched_m_sites":m,
      "gamma_early":g1,"gamma_late":g2,
      "gamma_single_round_mean":singles,
      "gamma_union_two_rounds":g_union,
      "bonus_temporal_complementarity":max(0.,bonus),
      "first_heard_only_later_round":new_after,
      "heard_only_earlier_round":early_only,
      "shared_acoustic_taxa_across_round_pools":shared,
      "normalized_bonus_if_nonempty":bonus/g_union if g_union>1e-12 else None,
      "all_original_taxon_labels_including_complexes":True
    }

def qa():
    src=import_source()
    # n=4 and m=2/3: all possible fixed site subsets to verify that
    # one chosen station set is used for BOTH observation rounds.
    A=[{"a","b"},{"a"},{"c"},set()]
    B=[{"a"},{"d"},{"b","c"},{"d"}]
    for m in (2,3,4):
        s=exact_two_round_pool(A,B,m)
        brute=[]
        for subset in itertools.combinations(range(4),m):
            before=set().union(*(A[i] for i in subset))
            after=set().union(*(B[i] for i in subset))
            combined=before|after
            brute.append((len(before),len(after),len(combined),
                          len(after-before),len(before-after),
                          len(before&after)))
        x=np.array(brute,float).mean(axis=0)
        for key,target in zip(("gamma_early","gamma_late","gamma_union_two_rounds",
                                "first_heard_only_later_round","heard_only_earlier_round",
                                "shared_acoustic_taxa_across_round_pools"),x):
            if not math.isclose(s[key],float(target),abs_tol=1e-12):
                raise AssertionError(f"Exact matched-site sample sum failed: m={m} key={key}")
        if not math.isclose(s["bonus_temporal_complementarity"],
            .5*(x[3]+x[4]),abs_tol=1e-12):
            raise AssertionError("Exactly one shared physical station subsample for both rounds")
    empty=exact_two_round_pool([set(),set()],[set(),set()],2)
    assert empty["gamma_union_two_rounds"]==0 and empty["normalized_bonus_if_nonempty"] is None
    stable=exact_two_round_pool([{"a"},{"b"}],[{"a"},{"b"}],2)
    assert stable["bonus_temporal_complementarity"]==0
    # Structural aggregation identity over nonidentical acoustic trajectories.
    assert abs(s["gamma_union_two_rounds"]-s["gamma_single_round_mean"]-s["bonus_temporal_complementarity"])<1e-10
    return {"status":"PASS","all_fixed_physical_site_subsets_enumerated":True,
         "joint_not_independent_resampling_across_rounds":True,
         "gamma_union_equals_single_plus_temporal_complementarity":True,
         "temporal_bonus_equals_half_later_new_plus_earlier_only":True,
         "empty_ten_stop_silent_cases_handled":True,
         "known_no_temporal_taxon_turnover_has_zero_bonus":True,
         "no_NAAMP_acoustic_biological_data_used":True}

def original_cohort():
    source=import_source()
    good,ci,rare,scope=source.source()
    d,cohort=source.build_rounds(good,ci,rare)
    assert scope["source_NAAMP_standard_runs"]==7848
    assert scope["source_NWI_complete_run_nights"]==6236
    assert scope["source_NWI_original_physical_SiteIDs"]==5147
    if (len(d)!=2869 or d.route_year_id.nunique()!=1115
        or d.route.nunique()!=274 or d.state.nunique()!=20):
        raise RuntimeError("Previous verified seasonal NAAMP×NWI population changed")
    if cohort["eligible_source_run_nights"]!=2869:
        raise RuntimeError("Original same-physical-site source cohort does not match")
    return good,ci,d,scope,cohort

def make_pairs(good,ci,source_d):
    rec=[]
    history=Counter()
    for group, df in source_d.groupby("route_year_id",sort=True):
        ordered=df.sort_values("round")
        ids=ordered.rid.astype(str).tolist()
        visits=[good[rid] for rid in ids]
        rounds=[int(v["round"]) for v in visits]
        if len(set(rounds))!=len(rounds) or not 2<=len(rounds)<=4:
            raise ValueError("Unexpected duplicate or missing seasonal survey-round identity")
        reference=visits[0]
        if any(x["physical_sites"]!=reference["physical_sites"]
               or x["wet"]!=reference["wet"] or x["pem"]!=reference["pem"]
               or x["stoplabels"]!=reference["stoplabels"] for x in visits[1:]):
            raise RuntimeError("Same site and vegetation eligibility did not remain fixed")
        pos=np.flatnonzero(np.asarray(reference["pem"],bool)
                          &np.asarray(reference["wet"],bool)).tolist()
        neg=np.flatnonzero(np.asarray(reference["wet"],bool)
                          &~np.asarray(reference["pem"],bool)).tolist()
        m=min(len(pos),len(neg))
        if not 2<=m<=5:raise RuntimeError("Existing 2–5 m-site geographic matching drift")
        if not np.all(ordered.m_rarefaction.astype(int).to_numpy()==m):
            raise RuntimeError("Existing exact m-site rarefaction population changed")
        original_sets={}
        for v in visits:
            original_sets[v["round"]]={mode:[
               {str(t) for t,c in ci.get((v["rid"],st),{}).items() if int(c)>=threshold}
               for st in reference["stoplabels"]]
               for mode,threshold in MODES}
        for i,j in itertools.combinations(range(len(visits)),2):
            a,b=visits[i],visits[j]
            label=str(a["round"])+"-"+str(b["round"])
            history[label]+=1
            row={"route_year_id":group,"route":reference["route"],
                 "state":reference["state"],"year":reference["year"],
                 "earlier_round":int(a["round"]),"later_round":int(b["round"]),
                 "round_pair":label,"original_rounds_in_year":len(visits),
                 "m_matched_physical_sites":m,"n_PEM_sites":len(pos),
                 "n_other_wetland_sites":len(neg)}
            for mode,threshold in MODES:
                results={}
                for name,sites in (("PEM",pos),("other",neg)):
                    A=[original_sets[a["round"]][mode][k] for k in sites]
                    B=[original_sets[b["round"]][mode][k] for k in sites]
                    r=exact_two_round_pool(A,B,m)
                    for attr in ("gamma_union_two_rounds","gamma_single_round_mean",
                                 "bonus_temporal_complementarity",
                                 "first_heard_only_later_round","heard_only_earlier_round",
                                 "shared_acoustic_taxa_across_round_pools"):
                        row[f"{name}_{attr}_{mode}"]=r[attr]
                    row[f"{name}_normalized_bonus_{mode}"]=(
                        np.nan if r["normalized_bonus_if_nonempty"] is None
                        else float(r["normalized_bonus_if_nonempty"]))
                    results[name]=r
                for target,key in (
                    ("gamma_two","gamma_union_two_rounds"),
                    ("gamma_single","gamma_single_round_mean"),
                    ("bonus","bonus_temporal_complementarity"),
                    ("new_later","first_heard_only_later_round"),
                    ("early_only","heard_only_earlier_round")):
                    row[f"delta_{target}_{mode}"]=results["PEM"][key]-results["other"][key]
                if not math.isclose(row[f"delta_gamma_two_{mode}"],
                    row[f"delta_gamma_single_{mode}"]+row[f"delta_bonus_{mode}"],abs_tol=1e-10):
                    raise RuntimeError("PEM−other cumulative gamma not decomposable by one-round and time bonus")
                if not math.isclose(row[f"delta_bonus_{mode}"],
                    .5*(row[f"delta_new_later_{mode}"]+row[f"delta_early_only_{mode}"]),abs_tol=1e-10):
                    raise RuntimeError("PEM−other temporal bonus not conserved by later new and early only")
            rec.append(row)
    if not rec:raise RuntimeError("No same route-year successive-round habitat pairs available")
    d=pd.DataFrame(rec)
    combos=len(d)
    expected=int(sum(math.comb(int(v),2)
                     for v in source_d.groupby("route_year_id").size().to_numpy()))
    if combos!=expected or set(d.route_year_id)!=set(source_d.route_year_id):
        raise RuntimeError("Fixed 2869-visit route-year population not exactly preserved")
    audit={
        "source_same_site_same_year_route_groups":int(source_d.route_year_id.nunique()),
        "same_site_source_route_nights":int(len(source_d)),
        "source_round_pairs_all_combinations":combos,
        "independent_physical_routes":int(d.route.nunique()),
        "States":int(d.state.nunique()),
        "round_pair_counts":dict(sorted(history.items())),
        "per_route_year_round_pair_counts":{
            str(k):int(v) for k,v in d.groupby("route_year_id").size().value_counts().sort_index().items()},
        "all_round_pairs_averaged_within_route_year_before_route_inference":True,
        "matched_physical_sites_same_m_across_both_rounds":True,
        "no_outcome_filter_on_frog_acoustic_activity":True}
    return d,audit

def signflip(vals,seed):
    rng=np.random.default_rng(seed)
    count=len(vals)
    observed=abs(float(np.mean(vals)))
    n_extreme=0
    for s in range(0,FLIPS,300):
        m=min(300,FLIPS-s)
        signs=rng.choice(np.asarray([-1.,1.]),size=(m,count))
        values=(signs@vals)/count
        n_extreme+=int(np.count_nonzero(np.abs(values)>=observed-1e-14))
    return {"route_null_signflips":FLIPS,
            "extreme":n_extreme,
            "route_plus_one_two_sided_P":(n_extreme+1)/(FLIPS+1),
            "signflip_whole_route_once_not_survey_pair_or_individual_taxa":True,
            "assumes_approximately_symmetric_independent_route_effects":True}

def estimate(groups,field,seed):
    allroutes=groups.groupby(["state","route"],sort=False)[field].mean().reset_index()
    n=len(allroutes);s=allroutes.state.nunique()
    if n<50 or s<5 or groups.route_year_id.nunique()<150:
        raise RuntimeError("Original ecological cohort lacks required physical route/State support")
    x=allroutes[field].to_numpy(float)
    mean=float(x.mean())
    se=float(x.std(ddof=1)/math.sqrt(n))
    if se<1e-12:raise RuntimeError("Whole-route climatic context variation too small for CI")
    q=float(student_t.ppf(.975,n-1))
    ss=allroutes.groupby("state")[field].mean()
    states=int(len(ss))
    s_mean=float(ss.mean())
    s_se=float(ss.std(ddof=1)/math.sqrt(states))
    qs=float(student_t.ppf(.975,states-1))
    loo={name:float(allroutes.loc[allroutes.state!=name,field].mean())
         for name in ss.index}
    return {
       "outcome":field,
       "n_original_route_year_groups":int(groups.route_year_id.nunique()),
       "n_independent_physical_routes":n,
       "n_States":s,
       "route_equal_delta":mean,
       "route_cluster_se":se,
       "route_Student_CI95":[mean-q*se,mean+q*se],
       "route_t_two_sided_P":float(2*student_t.sf(abs(mean/se),n-1)),
       "route_signflip":signflip(x,seed),
       "State_equal_delta":s_mean,
       "State_CI95":[s_mean-qs*s_se,s_mean+qs*s_se],
       "n_positive_State_means":int(np.count_nonzero(ss.to_numpy()>0)),
       "physical_routes_positive_fraction":float(np.mean(x>0)),
       "omit_one_State":{
         "n_estimable":len(loo),
         "n_positive":sum(v>0 for v in loo.values()),
         "n_negative":sum(v<0 for v in loo.values()),
         "range":[min(loo.values()),max(loo.values())]},
       "interpretation":"physical_route_equal_observational_PEM_minus_nonPEM_acoustic_taxon_pool_units"
    }

def BH(scores):
    fields=("delta_bonus_any","delta_bonus_strong",
            "delta_gamma_two_any","delta_gamma_two_strong")
    if set(scores)!=set(fields):raise RuntimeError("Four declared ecological complementarity endpoints mismatch")
    order=sorted(range(len(fields)),key=lambda i:scores[fields[i]]["route_t_two_sided_P"])
    last=1.
    for rank in range(len(order),0,-1):
        i=order[rank-1]
        name=fields[i]
        last=min(last,len(fields)*scores[name]["route_t_two_sided_P"]/rank)
        scores[name]["BH_q_four_fixed_tests"]=last
    for name in fields:
        z=scores[name]
        ci=z["route_Student_CI95"]
        st=z["State_CI95"]
        fl=z["route_signflip"]["route_plus_one_two_sided_P"]
        z["supported_positive_observational_PEM_ecological_context"] = bool(
            ci[0]>0 and st[0]>0 and fl<.05 and z["BH_q_four_fixed_tests"]<.05)
    return (
      "exploratory_positive_PEM_temporal_acoustic_complementarity"
      if scores["delta_bonus_any"]["supported_positive_observational_PEM_ecological_context"]
      else "no_supported_additional_PEM_temporal_taxon_complementarity")

def describe(df,routeyears,estimates):
    # Every route-year gets equal weight, then physical route gets equal weight.
    habitat={}
    for mode,_ in MODES:
        data={}
        for name in HABITATS:
            vals={}
            for p in ("gamma_union_two_rounds","gamma_single_round_mean",
                      "bonus_temporal_complementarity",
                      "first_heard_only_later_round","heard_only_earlier_round",
                      "shared_acoustic_taxa_across_round_pools"):
                col=f"{name}_{p}_{mode}"
                vals[p]=float(routeyears.groupby("route")[col].mean().mean())
            unnormalized=(routeyears.groupby("route")[f"{name}_normalized_bonus_{mode}"]
                          .mean().dropna())
            vals["normalized_bonus_fraction_conditional_nonempty"] =(
                float(unnormalized.mean()) if len(unnormalized)>0 else None)
            vals["n_routes_with_nonempty_normalized_bonus"]=int(len(unnormalized))
            vals["n_route_years_with_nonempty_pools"]=int(routeyears[f"{name}_normalized_bonus_{mode}"].notna().sum())
            vals["route_years_total"]=int(len(routeyears))
            data[name]=vals
        habitat[mode]=data
    between_round={}
    for round_pair,x in df.groupby("round_pair"):
        record={"source_route_year_round_pairs":int(len(x)),
                "independent_routes":int(x.route.nunique()),
                "States":int(x.state.nunique())}
        for mode,_ in MODES:
            for name in ("delta_bonus","delta_gamma_two","delta_gamma_single"):
                record[f"{name}_{mode}"]=float(x.groupby("route")[f"{name}_{mode}"].mean().mean())
        between_round[round_pair]=record
    return {"within_habitat_temporal_pool_architecture":habitat,
            "between_round_pair_summaries_NO_new_P_tests":between_round,
            "no_temporal_colonization_extinction_observed":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,
                   default=ROOT/"build/naamp_wetland_seasonal_complementarity")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    validated=qa()
    if args.synthetic_only:
        print(json.dumps(validated,sort_keys=True));return
    good,ci,observed,full_scope,cohort=original_cohort()
    df,sample=make_pairs(good,ci,observed)
    # An individual run-pair is NOT an independent replicate.
    # First average across R choose 2 comparisons WITHIN route-year.
    numeric=[c for c in df.columns if c.startswith(("delta_","PEM_","other_"))]
    means=df.groupby(["state","route","route_year_id"],sort=False)[numeric].mean().reset_index()
    if len(means)!=1115 or means.route.nunique()!=274:
        raise ValueError("Original eligible route-year geographic population not preserved")
    for mode,_ in MODES:
        z=means[f"delta_gamma_two_{mode}"]-means[f"delta_gamma_single_{mode}"]-means[f"delta_bonus_{mode}"]
        if float(np.max(np.abs(z)))>1e-10:
            raise ValueError("Time pooled gamma minus single-round gamma not equal temporal complementarity at full-group grain")
    fields=("delta_bonus_any","delta_bonus_strong",
            "delta_gamma_two_any","delta_gamma_two_strong")
    results={field:estimate(means,field,SEED+j)
             for j,field in enumerate(fields)}
    decision=BH(results)
    source_summary=describe(df,means,results)
    # Bonus difference accounting is a source-independent algebraic identity:
    for mode,_ in MODES:
        delta=results["delta_gamma_two_"+mode]["route_equal_delta"] - results["delta_bonus_"+mode]["route_equal_delta"]
        other=float(means.groupby("route")[f"delta_gamma_single_{mode}"].mean().mean())
        if not math.isclose(delta,other,abs_tol=1e-10):
            raise ValueError("Global physical-route ecological time-complementarity accounting failure")
    out={
       "analysis":"NAAMP_NWI_wetland_PEM_seasonal_acoustic_taxon_pool_temporal_complementarity",
       "status":"real_source_verified_equal_site_equal_two_round_frog_acoustic_complementarity_analysis",
       "date":"2026-10-23",
       "frozen_before_this_outcome":"exploration/NAAMP_WETLAND_WITHINYEAR_TEMPORAL_COMPLEMENTARITY_SPEC_2026_10_23.md",
       "exploratory_after_previous_same_archive_alpha_gamma_season_results":True,
       "source_coverage":full_scope,
       "original_withinyear_same_site_population":cohort,
       "two_round_full_source_sampling":sample,
       "synthetic_mathematical_QA":validated,
       "four_fixed_route_robust_ecological_tests":results,
       "primary_complementarity_verdict":decision,
       "biological_hierarchy":source_summary,
       "scientific_boundaries":{
          "NWI_polygon_not_actual_live_2001_2015_vegetation":True,
          "NAAMP_survey_rounds_not_uniform_calendar_dates":True,
          "observed_calling_taxon_labels_not_established_species_occupancy":True,
          "acoustic_later_new_not_actual_ecological_colonization":True,
          "acoustic_earlier_only_not_actual_extinction":True,
          "no_predator_mediation_or_biotic_higher_order_causality":True,
          "no_frog_frog_direct_interactions_observed":True,
          "not_a_forecast_or_prediction_model":True,
          "JAE_RC6_main_manuscript_SI_unchanged":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("NAAMP_WETLAND_SEASONAL_COMPLEMENTARITY_BEGIN",flush=True)
    print(json.dumps({
       "status":out["status"],"QA":validated,
       "source":full_scope,"matched_population":sample,
       "four_tests":results,"primary_verdict":decision,
       "descriptive":source_summary},sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_WETLAND_SEASONAL_COMPLEMENTARITY_END",flush=True)

if __name__=="__main__":
    main()
