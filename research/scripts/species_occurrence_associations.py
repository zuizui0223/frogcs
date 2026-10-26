#!/usr/bin/env python3
"""Observed within-original-survey species co-detection and habitat association.

Uses stage-collapsed, source-namespaced species event table.  A species
pair's 2x2 contingency includes ONLY survey events in which BOTH source
taxa have explicit observations.  No unassessed zeros are invented.
Pairwise phi is a reporting association, not a competition mechanism.

Hungary species-specific Spearman correlations: source wetland (n=29)
is the independent unit, not repeated survey rows. No variable tuning.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
import gzip
from itertools import combinations,groupby
import json
import math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

NBOOT=1000
SEED=20261026

def pair_phi(n11,n10,n01,n00):
    val=(n11+n10)*(n01+n00)*(n11+n01)*(n10+n00)
    return (n11*n00-n10*n01)/math.sqrt(val) if val else None

def pair_audit(events):
    edges=defaultdict(lambda:{"cells":Counter(),"site_cells":defaultdict(Counter),"site_year_month_cells":defaultdict(Counter)})
    source_events=Counter()
    positive_only=Counter()
    richer=defaultdict(Counter)
    # Original species projection is sorted by source/event/species/method;
    # group by source+method+event to prevent collisions in source token scope.
    with gzip.open(events,"rt",encoding="utf-8",newline="") as f:
        groups=groupby(csv.DictReader(f),key=lambda r:(r["source_id"],r["source_event_token"],r["method"]))
        for (src,eid,method),group in groups:
            items=list(group)
            source_events[src]+=1
            uniq={}
            for d in items:
                sp=d["taxon"];st=d["occurrence_status"]
                if sp in uniq:
                    raise ValueError("Duplicate projected source event×species: "+src)
                uniq[sp]=d
            present={k for k,v in uniq.items() if v["occurrence_status"]=="recorded_present"}
            richer[src][len(present)]+=1
            all_assessed={k:v for k,v in uniq.items() if v["occurrence_status"]!="unresolved"}
            for a,b in combinations(sorted(all_assessed),2):
                s1=int(all_assessed[a]["occurrence_status"]=="recorded_present")
                s2=int(all_assessed[b]["occurrence_status"]=="recorded_present")
                key=(src,method,a,b)
                cell=f"{s1}{s2}"
                ent=edges[key];ent["cells"][cell]+=1
                ent["site_cells"][items[0]["site_token"]][cell]+=1
                ent["site_year_month_cells"][(items[0]["site_token"],items[0]["year"],items[0]["month"])][cell]+=1
            if src=="naamp_positive_calls":
                # Presence-only: pair counting without any missing-based zero.
                for a,b in combinations(sorted(present),2):
                    positive_only[(a,b)]+=1
    records=[]
    rng=np.random.default_rng(SEED)
    for (src,method,a,b),o in sorted(edges.items()):
        c=o["cells"]
        n11,n10,n01,n00=(c[x] for x in ("11","10","01","00"))
        n=sum((n11,n10,n01,n00))
        sites=sorted(o["site_cells"])
        rho=pair_phi(n11,n10,n01,n00)
        interval=None
        if rho is not None and n>=30 and len(sites)>=5:
            cells=np.array([[o["site_cells"][site][x] for x in ("11","10","01","00")] for site in sites])
            ind=rng.integers(0,len(sites),size=(NBOOT,len(sites)))
            sums=np.sum(cells[ind],axis=1)
            p=[]
            for v in sums:
                z=pair_phi(*v)
                if z is not None:p.append(z)
            if len(p)>=700:
                interval=[float(z) for z in np.quantile(p,[.025,.975])]
        # Compare observed co-detection with the independence expectation
        # conditional on each same-site × calendar-year × month survey margin.
        # This does NOT remove hour-of-day, weather and detection bias.
        informative=0;informative_events=0
        observed11=0.0;expected11=0.0
        site_excess=defaultdict(lambda:[0.0,0])
        for (site,year,month),cellcounts in o["site_year_month_cells"].items():
            n=sum(cellcounts.values())
            ap=cellcounts["11"]+cellcounts["10"]
            bp=cellcounts["11"]+cellcounts["01"]
            if n<2 or ap in (0,n) or bp in (0,n):
                continue
            informative+=1;informative_events+=n
            obs=cellcounts["11"]
            exp=ap*bp/n
            observed11+=obs;expected11+=exp
            site_excess[site][0]+=obs-exp
            site_excess[site][1]+=n
        conditional={"conditioning":"source native site × calendar year × month, species event-assessment margins",
                     "n_informative_site_year_month_strata":informative,
                     "n_original_sites_in_informative_strata":len(site_excess),
                     "n_both_species_assessed_in_informative_strata":informative_events,
                     "n_exact_co_detections_observed":int(observed11),
                     "independence_expected_co_detections_given_source_site_month":float(expected11),
                     "excess_joint_detection_per_100_same_stratum_assessments":(
                         float(100*(observed11-expected11)/informative_events)
                         if informative_events else None),
                     "site_bootstrap_95ci_conditional_on_fixed_strata":None,
                     "within_site_month_signal_estimable":False,
                     "inference_ceiling":"Within-site-month reporting residual, not competition or direct species interactions"}
        if informative>=10 and len(site_excess)>=5 and informative_events>=50:
            vals=np.array(list(site_excess.values()),dtype=float)
            idx=rng.integers(0,len(vals),size=(NBOOT,len(vals)))
            numer=np.sum(vals[idx,0],axis=1)
            denom=np.sum(vals[idx,1],axis=1)
            scored=100*numer/denom
            conditional["site_bootstrap_95ci_conditional_on_fixed_strata"]=[float(z) for z in np.quantile(scored,[.025,.975])]
            conditional["within_site_month_signal_estimable"]=True
        records.append({
          "source_id":src,"method":method,"species_a":a,"species_b":b,
          "both_species_explicitly_assessed_original_events":n,
          "distinct_original_sites_with_joint_assessment":len(sites),
          "co_detection_events_n11":n11,
          "a_detected_b_not_called_or_not_observed_n10":n10,
          "a_not_called_or_not_observed_b_detected_n01":n01,
          "both_protocol_not_detected_n00":n00,
          "phi_same_event":rho,
          "site_resample_ci95_phi":interval,
          "season_site_conditioned_co_detection":conditional,
          "estimable_reporting_association":interval is not None,
          "source_stop_semantics":"Detection-scoped 0; not verified ecological species absence",
          "actual_biotic_competition_identified":False,
        })
    valid=[z for z in records if z["estimable_reporting_association"]]
    strongest=sorted(valid,key=lambda x:x["phi_same_event"])
    result={
      "source_original_events_count":dict(source_events),
      "source_event_detected_species_histogram":{s:dict(c) for s,c in richer.items()},
      "pair_estimands_total":len(records),
      "pairs_meeting_fixed_n30_sites5_and_usable_site_CI":len(valid),
      "pair_models":records,
      "top_12_lowest_phi":strongest[:12],
      "top_12_highest_phi":strongest[-12:][::-1],
      "naamp_positive_only_taxon_pairs_count":len(positive_only),
      "naamp_source_co_positive_pairs_total":sum(positive_only.values()),
      "naamp_absence_based_phi_not_estimable":True,
      "interpretation":"Within-original-event co-detection, not measured interspecific competition or trophic predation",
    }
    return result

def hungary_species_correlations(events):
    # The same Hungarian visit method assesses all nine listed target taxa;
    # one occurrence row per event/taxon. Site-level fractions and static
    # environmental covariates are aggregated only WITHIN THAT SOURCE.
    site_species=defaultdict(lambda:{"n":0,"positive":0,"rain":[],"depth":[],"emergent":[],"submerged":[],"class":[]})
    species=defaultdict(set)
    with gzip.open(events,"rt",encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            if r["source_id"]!="hungary_2024" or r["method"]!="acoustic":continue
            if r["occurrence_status"]=="unresolved":continue
            site=r["site_token"];sp=r["taxon"]
            v=site_species[(site,sp)]
            v["n"]+=1
            v["positive"]+=int(r["occurrence_status"]=="recorded_present")
            for col,k in [("precip_source_value","rain"),("water_depth_source_value","depth"),
                          ("emergent_cover_percent","emergent"),("submerged_cover_percent","submerged")]:
                if r[col]!="":v[k].append(float(r[col]))
            v["class"].append(r["site_management_class"])
            species[sp].add(site)
    species_results=[]
    for sp in sorted(species):
        agg=[v for (site,taxon),v in sorted(site_species.items()) if taxon==sp]
        sites=len(agg)
        if not agg:continue
        detection=np.array([v["positive"]/v["n"] for v in agg])
        positives=sum(v["positive"]>0 for v in agg)
        items={}
        for name,field in [("rain_at_visited_days","rain"),("source_one_time_water_depth","depth"),
                           ("static_emergent_plant_cover_pct","emergent"),
                           ("static_submerged_plant_cover_pct","submerged")]:
            xs=np.array([float(np.mean(v[field])) if v[field] else np.nan for v in agg])
            valid=np.isfinite(xs)&np.isfinite(detection)
            if valid.sum()<15 or len(set(detection[valid]))<2 or len(set(xs[valid]))<3 or positives<5:
                items[name]={"status":"INSUFFICIENT_SITE_COVERAGE_OR_DETECTION_VARIATION",
                             "n_sites":int(valid.sum()),"spearman_rho":None}
                continue
            rho=spearmanr(xs[valid],detection[valid]).statistic
            items[name]={"status":"DESCRIPTIVE_SPEARMAN_NO_CAUSAL_CLAIM",
                         "n_sites":int(valid.sum()),"rho":float(rho) if np.isfinite(rho) else None}
        species_results.append({
           "species":sp,"sites_scored_under_acoustic_protocol":sites,
           "sites_with_positive_acoustic_detection":positives,
           "source_acoustic_events_scored":int(sum(v["n"] for v in agg)),
           "environment_associations":items,
           "not_CI2plus_and_not_pond_predator_count":True
        })
    return {
      "study":"Hungary 2024 exact source wetlands with static cover and visit rain",
      "independent_original_wetlands":len({site for (site,taxon) in site_species}),
      "acoustic_species_response_species_count":len(species_results),
      "species":species_results,
      "fish_predator_stage_richness_estimated":False,
      "water_depth_equivalent_to_hydroperiod_days":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--event-table",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    if not args.event_table.is_file():raise ValueError("Source species-only events absent")
    pairs=pair_audit(args.event_table)
    hungary=hungary_species_correlations(args.event_table)
    report={
       "analysis":"source_event_species_only_occurrence",
       "protocol":"research/SPECIES_OCCURRENCE_FIRST_CONTRACT_2026-10-26.md",
       "pairs":pairs,
       "hungary":hungary,
       "world_GBIF_grid_occurrence_not_an_exact_pond_event":True,
       "regression_or_causal_community_competition_fit":False,
       "life_stage_required_for_any_species_occurrence_analyses":False,
       "status":"OBSERVED_SOURCE_ONLY_SPECIES_CO_DETECTION_EXPLORATORY"
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_SPECIES_CO_OCCURRENCE_RESULTS")
    print(json.dumps({
      "status":report["status"],
      "n_paired_original_source_event_species_contingencies":pairs["pair_estimands_total"],
      "n_inference_ready_co_assessed_species_pairs":pairs["pairs_meeting_fixed_n30_sites5_and_usable_site_CI"],
      "source_event_counts":pairs["source_original_events_count"],
      "top_lowest_phi":pairs["top_12_lowest_phi"],
      "top_highest_phi":pairs["top_12_highest_phi"],
      "hungary_species":hungary["species"],
      "no_inferred_competition_from_cooccurrence":True
    },ensure_ascii=False,indent=2))
    print("END_SPECIES_CO_OCCURRENCE_RESULTS")
if __name__=="__main__":
    main()
