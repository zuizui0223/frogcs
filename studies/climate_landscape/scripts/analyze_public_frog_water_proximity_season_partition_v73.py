#!/usr/bin/env python3
"""v7.3 real public frog detections: source water-proximity labels vs 2+2
site-level alternative plot partitions, with seasonal heterogeneity.

Exploratory, source-pinned and outcome-positive-only. Full design frozen at
V7_3_PUBLIC_FROG_WATER_PROXIMITY_FOUR_PLOT_SEASON_TEST_CONTRACT.md BEFORE
this version's observed biological Jaccard values were examined.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import json
import random
import statistics

import analyze_hoefer_biological_summer_and_plot_category_v72 as src
import analyze_public_hoefer_seasonal_recurrence_v71 as common

LABELS=("DryA","DryB","WetA","WetB")
SEASONS=("autumn","winter","spring","summer")
# The three and only three unordered partitions of four named plots into two
# unordered pairs. Actual physical proximity grouping is index 0.
PARTITIONS=(
    (("DryA","DryB"),("WetA","WetB")),
    (("DryA","WetA"),("DryB","WetB")),
    (("DryA","WetB"),("DryB","WetA")),
)
N_BOOT=5000
SEED=20261013+73
OUTPUT="studies/climate_landscape/receipts/HOEFER_2026_REAL_PUBLIC_WATER_PROXIMITY_SEASON_PARTITIONS_V73.json"

def pair_key(a,b):
    return tuple(sorted((a,b)))

def score_partition(pairs,partition):
    inside={pair_key(*p) for p in partition}
    if len(inside)!=2 or any(p not in pairs for p in inside):
        raise ValueError("BAD_SOURCE_PLOT_PAIR_PARTITION")
    between=set(pairs)-inside
    if len(between)!=4: raise ValueError("PAIR_COMPLEMENT_IS_NOT_FOUR")
    return statistics.mean(pairs[p] for p in inside)-statistics.mean(pairs[p] for p in between)

def complete_groups(cells,dates,min_detected_days=0):
    # Never fabricate source-negative listening opportunities.
    groups=defaultdict(dict)
    for (site,plot,season,cycle),species in cells.items():
        if plot not in LABELS or season not in SEASONS:
            raise ValueError("UNEXPECTED_AUTHOR_PLOT_OR_SEASON")
        if len(dates[(site,plot,season,cycle)])>=min_detected_days:
            groups[(site,season,cycle)][plot]=species
    out=[]
    for (site,season,cycle),plots in sorted(groups.items()):
        if set(plots)!=set(LABELS):continue
        d={pair_key(a,b):common.jaccard(plots[a],plots[b])
           for a,b in combinations(LABELS,2)}
        if len(d)!=6:raise ValueError("PAIR_COUNT_NOT_SIX")
        scores=tuple(score_partition(d,partition) for partition in PARTITIONS)
        if abs(sum(scores))>1e-10:
            raise ValueError("COMPETING_PARTITIONS_SUM_SHOULD_BE_ZERO")
        out.append((site,season,cycle,scores))
    return out

def quantile(values,q):
    return common.percentile(values,q)

def summarize(frames,site_threshold=3):
    # Original site labels retained in memory but never emitted.
    by_site=defaultdict(lambda:defaultdict(list))
    by_season=defaultdict(lambda:defaultdict(list))
    for site,season,_,scores in frames:
        for k,value in enumerate(scores):
            by_site[site][k].append(value)
            by_season[season][site].append(scores)
    sites=sorted(by_site)
    if len(sites)<site_threshold:
        return {
            "status":"INSUFFICIENT_SITE_SUPPORT",
            "n_complete_four_plot_positive_groups":len(frames),
            "n_sites_with_complete_groups":len(sites),
            "observed_equal_site_mean":None,
            "seasonality_not_evaluated":True,
        }
    site_scores={site:tuple(statistics.mean(by_site[site][k]) for k in range(3))
                 for site in sites}
    observed=statistics.mean(v[0] for v in site_scores.values())
    rng=random.Random(SEED)
    obsvals=[v[0] for v in site_scores.values()]
    boots=[statistics.mean(rng.choice(obsvals) for _ in obsvals) for _ in range(N_BOOT)]
    partition_refs=[
       statistics.mean(site_scores[site][choice] for site,choice in zip(sites,idxs))
       for idxs in product(range(3),repeat=len(sites))
    ]
    if len(partition_refs)!=3**len(sites):raise ValueError("BAD_REFERENCE_PARTITION_COUNT")
    season_summaries={}
    for season in SEASONS:
        matched={site:by_season[season][site] for site in sites
                 if by_season[season].get(site)}
        if matched:
            site_means=[
                statistics.mean(scores[0] for scores in v)
                for v in matched.values()
            ]
            season_summaries[season]={
                "n_sites_with_complete_frames":len(matched),
                "n_complete_four_plot_positive_groups":sum(map(len,matched.values())),
                "n_positive_sites":sum(v>0 for v in site_means),
                "equal_site_mean_grouping_score":round(statistics.mean(site_means),6),
                "range_site_mean_grouping_scores":
                    [round(min(site_means),6),round(max(site_means),6)]
            }
        else:
            season_summaries[season]={
                "n_sites_with_complete_frames":0,
                "n_complete_four_plot_positive_groups":0,
                "equal_site_mean_grouping_score":None,
                "n_positive_sites":0,
            }
    all_seasons=[site for site in sites if all(by_season[s].get(site) for s in SEASONS)]
    heterogeneity={
        "status":"INSUFFICIENT_ALL_SEASON_SITES",
        "n_sites_with_complete_four_plot_groups_in_every_season":len(all_seasons),
        "observed_seasonal_max_minus_min":None,
        "pseudo_label_partition_reference":None
    }
    if len(all_seasons)>=site_threshold:
        # Reuse the EXACT SAME site-specific partition assignment across ALL
        # calendar cycles and all four seasons. No pseudo-independent days.
        per_season_scores={
            site:{seas:tuple(statistics.mean(g[k] for g in by_season[seas][site])
                             for k in range(3)) for seas in SEASONS}
            for site in all_seasons
        }
        def get_range(partitions):
            means=[statistics.mean(per_season_scores[site][seas][p]
                   for site,p in zip(all_seasons,partitions))
                   for seas in SEASONS]
            return max(means)-min(means)
        obs_range=get_range((0,)*len(all_seasons))
        ref=[get_range(idx) for idx in product(range(3),repeat=len(all_seasons))]
        heterogeneity={
            "status":"EXPLORATORY_SEASON_MODULATION_WITH_MATCHED_SITES",
            "n_sites_with_complete_four_plot_groups_in_every_season":len(all_seasons),
            "observed_seasonal_max_minus_min":round(obs_range,6),
            "site_fixed_label_reference_n":len(ref),
            "pseudo_label_partition_reference":{
               "q025_q975":[round(quantile(ref,.025),6),
                            round(quantile(ref,.975),6)],
               "fraction_reference_greater_equal_observed":
                   round(sum(v>=obs_range-1e-12 for v in ref)/len(ref),6)
            },
            "not_randomised_or_causal":True
        }
    return {
        "status":"SOURCE_SITE_LEVEL_PUBLIC_ASSEMBLAGE_GROUPING_COMPUTED",
        "n_complete_four_plot_positive_groups":len(frames),
        "n_sites_with_complete_groups":len(sites),
        "observed_equal_site_mean":round(observed,6),
        "site_mean_minmax":[round(min(obsvals),6),round(max(obsvals),6)],
        "n_sites_positive":sum(v>0 for v in obsvals),
        "n_sites_negative":sum(v<0 for v in obsvals),
        "site_bootstrap_95_descriptive":
             [round(quantile(boots,.025),6),round(quantile(boots,.975),6)],
        "site_fixed_exact_three_way_plot_grouping_reference":{
            "n_possible_unordered_plot_partition_assignments_per_site":3,
            "total_reference_assignments":len(partition_refs),
            "reference_mean":round(statistics.mean(partition_refs),6),
            "reference_q025_q975":
                [round(quantile(partition_refs,.025),6),
                 round(quantile(partition_refs,.975),6)],
            "fraction_reference_scores_greater_equal_observed":
                round(sum(v>=observed-1e-12 for v in partition_refs)
                      /len(partition_refs),6),
            "NOT_a_randomisation_test_p_value":True,
            "source_grouping_not_randomly_assigned":True
        },
        "all_four_author_seasons_reported_in_fixed_order":season_summaries,
        "seasonal_heterogeneity":heterogeneity
    }

def test():
    assert len(PARTITIONS)==3
    assert set().union(*({pair_key(*p) for p in q} for q in PARTITIONS))=={
        pair_key(*p) for p in combinations(LABELS,2)}
    # Detect held-out conditional score when observed Dry category aligns
    # perfectly with species lists; alternative groupings must be smaller.
    sets={"DryA":{"F1"},"DryB":{"F1"},"WetA":{"F2"},"WetB":{"F2"}}
    paired={pair_key(a,b):common.jaccard(sets[a],sets[b])
            for a,b in combinations(LABELS,2)}
    values=[score_partition(paired,q) for q in PARTITIONS]
    assert values==[1.0,-0.5,-0.5]
    sample={}
    dates={}
    for site in ("X","Y","Z","Q","W","E"):
        for plot in LABELS:
            key=(site,plot,"summer",2020)
            sample[key]=sets[plot]
            dates[key]={1,2,3,4,5}
    frames=complete_groups(sample,dates)
    assert len(frames)==6
    result=summarize(frames)
    assert result["site_fixed_exact_three_way_plot_grouping_reference"]["total_reference_assignments"]==729
    assert sum(z["n_complete_four_plot_positive_groups"] for z in result["all_four_author_seasons_reported_in_fixed_order"].values())==result["n_complete_four_plot_positive_groups"], "SEASON_FRAME_COUNT_REPEATED"
    assert result["observed_equal_site_mean"]==1.0
    assert result["site_fixed_exact_three_way_plot_grouping_reference"]["fraction_reference_scores_greater_equal_observed"]==round(1/729,6)
    assert summarize(complete_groups(sample,dates,6))["status"]=="INSUFFICIENT_SITE_SUPPORT"
    # Full four plots in same season-year necessary: remove one plot,
    # entire positive-frame is missing, NOT imputed 0.
    sample.pop(("E","WetB","summer",2020))
    assert len(complete_groups(sample,dates))==5
    print("PASS: exact 3-way plot partitions, 729 site-fixed assignments, missing-group stop, true season grouping")

def main():
    test()
    raw=common.source_fetch()
    cells,dates,profile=src.biological_cells(raw)
    if len(cells)!=197 or profile["source_positive_detection_rows"]!=13577:
        raise ValueError("SOURCE_FRAME_CHANGED")
    frames=complete_groups(cells,dates,0)
    frames5=complete_groups(cells,dates,5)
    out={
        "status":"ACTUAL_PUBLIC_FROG_DISTANCE_TO_WATER_PLOT_PARTITION_RESULT",
        "source":"Hoefer et al. 2026, Zenodo v2.0, original frog_data_season.csv",
        "source_git_blob_sha1":common.EXPECTED_BLOB,
        "source_sha256":sha256(raw).hexdigest(),
        "source_total_positive_detection_rows":profile["source_positive_detection_rows"],
        "n_source_site_labels":profile["n_author_sites"],
        "n_source_corrected_positive_cells":len(cells),
        "plot_definition":{
            "near_water":"WetA/WetB <=50m from waterbody",
            "far_water":"DryA/DryB >500m from water source",
            "source":"Hoefer et al. (2026) frog study Figure 1 / authors same survey design 2025 mammal methods",
            "not_measured_inundation_or_randomised":True
        },
        "all_four_positive_plots_matched_source_frames":summarize(frames),
        "min_five_positive_detection_days_in_each_of_four_plots":summarize(frames5),
        "min_positive_date_threshold":5,
        "source_has_actual_complete_recorder_effort_ledger":False,
        "negative_species_or_unsampled_recording_assumed_absent":False,
        "author_plot_habitat_label_is_not_time_varying_water_depth":True,
        "site_coordinates_species_names_and_raw_rows_published":False,
        "no_hydrological_causality_memory_or_fitness_claim":True,
        "exploratory_not_preregistered_prior_v72_results_were_seen":True,
        "rc6_main_unchanged":True
    }
    p=Path(OUTPUT)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
