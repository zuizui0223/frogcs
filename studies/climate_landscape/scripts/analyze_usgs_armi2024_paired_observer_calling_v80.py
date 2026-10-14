#!/usr/bin/env python3
"""Original USGS 2024 CC0 frog source 2026 v1.1, matched human-observer/device
package detected anuran assemblage uncertainty. Positive AND explicit no-call
visits; NOT an instrument causal effect or actual water-state inference.

Frozen BEFORE reading outcome columns:
USGS_ARMI2024_FROZEN_PAIRED_OBSERVER_DETECTION_DISCORDANCE.md
"""
from __future__ import annotations
from collections import Counter,defaultdict
from dataclasses import dataclass,field
from datetime import datetime
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,random,statistics

import audit_armi2024_original_visit_observer_v80 as source

OUTPUT="studies/climate_landscape/receipts/USGS_ARMI2024_REAL_PAIRED_OBSERVER_FROG_CALLING_V80.json"
SEED=20261014
NBOOT=5000

@dataclass
class Visit:
    site:str
    day:str
    observer:str
    times:set=field(default_factory=set)
    methods:set=field(default_factory=set)
    taxa:set=field(default_factory=set)
    none_rows:int=0
    nrows:int=0
    n_missing_individual_count:int=0

def parse(raw,strict:bool=True):
    import csv,io
    rd=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    required={"Site","Date","Observer","Arrival_time","Method","Species","Number_heard"}
    if not rd.fieldnames or not required.issubset(rd.fieldnames):
        raise ValueError("REQUIRED_SOURCE_COLUMNS_MISSING")
    visits={}
    nrows=0; none=0; blanks=0
    for row in rd:
        nrows+=1
        if None in row or nrows>100000:raise ValueError("RAW_ROW_SHAPE_OR_SOURCE_VOLUME_CHANGED")
        site=(row["Site"] or "").strip()
        day=(row["Date"] or "").strip()
        observer=(row["Observer"] or "").strip()
        clock=(row["Arrival_time"] or "").strip()
        method=(row["Method"] or "").strip()
        species=(row["Species"] or "").strip()
        heard=(row["Number_heard"] or "").strip()
        if not site or not observer or not clock or method not in {"Ear","Microphone"}:
            raise ValueError("ORIGINAL_SURVEY_ID_OR_METHOD_MISSING")
        try: datetime.strptime(day,"%Y-%m-%d")
        except ValueError as e:raise ValueError("SOURCE_DATE_CHANGED") from e
        if source.to_minutes(clock) is None:
            raise ValueError("SOURCE_TIME_CHANGED")
        key=(site,day,observer)
        if key not in visits:visits[key]=Visit(site,day,observer)
        obj=visits[key]
        obj.nrows+=1
        obj.times.add(clock)
        obj.methods.add(method)
        if species.upper() in source.SPECIES_NO_CALL_ALIASES:
            none+=1
            obj.none_rows+=1
            if heard.upper() not in {"","NA","N/A","NULL"}:
                raise ValueError("NO_FROG_WITH_NONMISSING_INDIVIDUAL_COUNT")
        else:
            if not species:raise ValueError("EMPTY_REAL_SPECIES")
            if heard.upper() in {"","NA","N/A","NULL"}:
                raise ValueError("DETECTED_FROG_WITH_MISSING_NUMBER")
            obj.taxa.add(species)
    if strict:
        if nrows!=1934 or len(visits)!=797 or none!=220 or len({v.site for v in visits.values()})!=343:
            raise ValueError("PINNED_PUBLIC_SOURCE_GRANULARITY_CHANGED")
    mixed=sum(bool(v.taxa) and v.none_rows>0 for v in visits.values())
    repeated_none=sum(v.none_rows>1 for v in visits.values())
    if mixed or repeated_none:
        raise ValueError("MIXED_OR_DUPLICATED_SOURCE_NO_CALL_SURVEY")
    ambiguous=[v for v in visits.values() if len(v.times)!=1 or len(v.methods)!=1]
    if strict and len(ambiguous)!=1:
        raise ValueError("SOURCE_AMBIGUOUS_SURVEY_TIMES_CHANGED")
    good={k:v for k,v in visits.items() if len(v.times)==len(v.methods)==1}
    srcprof={
        "n_original_source_species_rows":nrows,
        "n_original_site_date_observer_keys":len(visits),
        "n_distinct_source_site_ids":len({v.site for v in visits.values()}),
        "n_all_source_no_anuran_heard_rows":none,
        "n_distinct_explicit_no_anuran_heard_opportunities":sum(v.none_rows>0 for v in visits.values()),
        "n_valid_unambiguous_opportunities_after_one_multiple_time_exclusion":len(good),
        "n_ambiguous_original_observer_opportunities":len(ambiguous),
        "n_valid_opportunities_with_any_species_reported":sum(bool(v.taxa) for v in good.values()),
        "n_valid_explicit_no_anuran_heard_opportunities":sum(v.none_rows>0 for v in good.values()),
        "no_frog_sentinel_and_genuine_species_mixed_in_a_source_visit":False,
        "number_heard_is_range_or_count_not_proportional_singing_abundance":True,
        "raw_site_or_observer_identifiers_published":False
    }
    return good,srcprof

def jaccard_if_detected(a:set,b:set):
    union=a|b
    return len(a&b)/len(union) if union else None

def percentile(xs,q):
    xs=sorted(xs)
    if not xs:return None
    p=(len(xs)-1)*q
    a=int(p)
    b=min(len(xs)-1,a+1)
    return xs[a]+(p-a)*(xs[b]-xs[a])

def paired(studies):
    site_day=defaultdict(list)
    for v in studies.values():
        site_day[(v.site,v.day)].append(v)
    count=Counter()
    paired_records=[]
    same_method=[]
    for (site,day),visits in site_day.items():
        if len(visits)!=2 or len({v.observer for v in visits})!=2:continue
        a,b=visits
        t1=source.to_minutes(next(iter(a.times)))
        t2=source.to_minutes(next(iter(b.times)))
        gap=min(abs(t1-t2),1440-abs(t1-t2))
        if gap>5:
            count["pair_start_gap_gt_5min"]+=1
            continue
        ma,mb=next(iter(a.methods)),next(iter(b.methods))
        if ma==mb:
            same_method.append((site,day,ma))
            continue
        ea,mi=(a,b) if ma=="Ear" else (b,a)
        paired_records.append((site,ea,mi,gap))
    return paired_records,same_method,count

def summarize_pairs(pairs):
    by_site=defaultdict(list)
    discord=Counter()
    jlist=[]
    both_zero=0
    for site,ear,mic,gap in pairs:
        diff=len(mic.taxa)-len(ear.taxa)
        by_site[site].append(diff)
        anyear=bool(ear.taxa)
        anymic=bool(mic.taxa)
        if anyear and anymic:discord["both_heard"]+=1
        elif not anyear and not anymic:
            discord["both_explicitly_no_anurans_heard"]+=1
            both_zero+=1
        elif anymic:discord["microphone_only_heard"]+=1
        else:discord["ear_only_heard"]+=1
        j=jaccard_if_detected(ear.taxa,mic.taxa)
        if j is not None:jlist.append(j)
    sites=sorted(by_site)
    diffs=[statistics.mean(by_site[s]) for s in sites]
    if not diffs:raise ValueError("NO_COMPARABLE_INDEPENDENT_OBSERVERS")
    means={
        "Ear":round(statistics.mean(len(ear.taxa) for _,ear,mic,_ in pairs),6),
        "Microphone":round(statistics.mean(len(mic.taxa) for _,ear,mic,_ in pairs),6),
    }
    rng=random.Random(SEED)
    # Cluster site summaries, NOT every species detection row.
    boot=[statistics.mean(rng.choice(diffs) for _ in diffs) for _ in range(NBOOT)]
    return {
        "n_eligible_independent_observer_mixed_method_pairs":len(pairs),
        "n_original_physical_source_site_clusters":len(sites),
        "n_site_paired_method_observer_package_richness_pos":sum(x>0 for x in diffs),
        "n_site_paired_method_observer_package_richness_neg":sum(x<0 for x in diffs),
        "n_site_paired_richness_equal":sum(x==0 for x in diffs),
        "mean_distinct_detected_frog_taxa_per_opportunity_by_method":means,
        "mean_site_paired_microphone_minus_ear_detected_taxon_richness":round(statistics.mean(diffs),6),
        "paired_median_microphone_minus_ear_detected_taxon_richness":
            statistics.median(len(m.taxa)-len(e.taxa) for _,e,m,_ in pairs),
        "site_bootstrap_95_DESCRIPTIVE":
            [round(percentile(boot,.025),6),round(percentile(boot,.975),6)] if len(sites)>=5 else None,
        "binary_anuran_call_presence_observer_device_package_crosstab":dict(discord),
        "share_paired_opportunities_any_frog_status_discordant":round(
            (discord["microphone_only_heard"]+discord["ear_only_heard"])/len(pairs),6),
        "n_paired_observer_species_union_positive":len(jlist),
        "n_paired_observer_both_no_frogs_separate":both_zero,
        "mean_jaccard_for_paired_positive_union_source_lists":
            round(statistics.mean(jlist),6) if jlist else None,
        "median_jaccard_for_paired_positive_union_source_lists":
            round(statistics.median(jlist),6) if jlist else None,
        "n_paired_observer_species_lists_different_among_nonempty_union":
            sum(j<1 for j in jlist),
        "observer_identity_and_method_nearly_confounded":True,
        "no_causal_microphone_advantage_claim":True,
        "no_individual_site_or_species_records_exported":True,
    }

def temporal_repeats(studies):
    groups=defaultdict(list)
    # Among a fixed original source site AND same person+method, compare
    # only different survey dates ≤30 days apart; no repeated raw taxon rows.
    for v in studies.values():
        k=(v.site,v.observer,next(iter(v.methods)))
        groups[k].append(v)
    pairs=0
    site_j=defaultdict(list)
    all_repeat_sites=set()
    for (site,person,method),visits in groups.items():
        visits.sort(key=lambda x:x.day)
        for a,b in combinations(visits,2):
            d=(datetime.strptime(b.day,"%Y-%m-%d")-datetime.strptime(a.day,"%Y-%m-%d")).days
            if not (1<=d<=30):continue
            pairs+=1
            all_repeat_sites.add(site)
            j=jaccard_if_detected(a.taxa,b.taxa)
            if j is not None:site_j[site].append(j)
    per_site=[statistics.mean(x) for x in site_j.values() if x]
    return {
        "n_same_site_same_observer_same_method_date_pairs_within_30_days":pairs,
        "n_sites_with_repeated_same_observer_same_method_source_opportunities":len(all_repeat_sites),
        "n_sites_with_temporal_pairs_nonempty_detected_taxon_union":len(per_site),
        "equal_site_mean_source_detected_assemblage_jaccard_if_nonempty_union":
            round(statistics.mean(per_site),6) if len(per_site)>=5 else None,
        "source_visit_events_not_independent_frog_presence_states":True,
        "not_a_matched_control_for_same_night_observer_pair":True,
    }

def unit_test():
    sample=("Site,Date,Observer,Arrival_time,Method,Species,Number_heard\n"
        "S1,2024-06-06,A,20:10,Ear,None,NA\n"
        "S1,2024-06-06,B,20:12,Microphone,Species1,1 to 5\n"
        "S2,2024-06-06,A,20:14,Ear,Species1,1\n"
        "S2,2024-06-06,B,20:14,Microphone,Species1,2\n"
        "S2,2024-06-06,B,20:14,Microphone,Species2,1\n").encode()
    visits,prof=parse(sample,strict=False)
    assert prof["n_original_site_date_observer_keys"]==4
    pairs,same,err=paired(visits)
    assert len(pairs)==2
    p=summarize_pairs(pairs)
    assert p["binary_anuran_call_presence_observer_device_package_crosstab"]["microphone_only_heard"]==1
    assert p["binary_anuran_call_presence_observer_device_package_crosstab"]["both_heard"]==1
    assert p["n_paired_observer_species_lists_different_among_nonempty_union"]==2
    assert jaccard_if_detected(set(),set()) is None
    mixed=("Site,Date,Observer,Arrival_time,Method,Species,Number_heard\n"
        "S,2024-06-06,A,20:10,Ear,None,NA\n"
        "S,2024-06-06,A,20:10,Ear,Species1,1\n").encode()
    try:parse(mixed,strict=False)
    except ValueError as e:assert str(e)=="MIXED_OR_DUPLICATED_SOURCE_NO_CALL_SURVEY"
    else:raise AssertionError("mixed silence/animal call accepted")
    print("PASS: original explicit no-frog visit parsing, matched Ear/Mic dual observer, no species ID export, mixed-code rejection")

def main():
    unit_test()
    raw=source.get_source()
    if sha256(raw).hexdigest()!=source.EXPECTED_SHA256:raise ValueError("ORIGINAL_SOURCE_SHA_CHANGED")
    visits,profile=parse(raw)
    pairs,same,err=paired(visits)
    if len(pairs)<5:
        raise ValueError("TOO_FEW_COMPARABLE_DUAL_OBSERVER_SITE_PAIRS")
    result={
        "status":"ORIGINAL_CC0_USGS2024_REAL_FROG_SAME_SITE_PAIRED_OBSERVER_RESULT",
        "source_doi":"https://doi.org/10.5066/P19ZCGWM",
        "input_original_csv_sha256":sha256(raw).hexdigest(),
        "source_protocol":"studies/climate_landscape/USGS_ARMI2024_FROZEN_PAIRED_OBSERVER_DETECTION_DISCORDANCE.md",
        "source_survey_opportunities":profile,
        "strict_paired_dual_observer_mixed_method":summarize_pairs(pairs),
        "source_same_date_same_method_observer_pair_count_excluded":len(same),
        "source_clock_or_method_noncomparable_pairs":dict(err),
        "source_within_site_repeated_visit_detected_assemblages":temporal_repeats(visits),
        "source_methods_almost_perfectly_confound_observer_identity":True,
        "any_zero_code_inferred_from_missing_species":False,
        "original_site_coordinates_or_taxon_names_exported":False,
        "site_is_field_site_not_spatially_independent_wetland_authenticated":True,
        "no_water_level_hysteresis_or_memory_fitness_claim":True,
        "previous_2026_cricket_frog_northward_reexpansion_result_not_claimed_new":True,
        "no_experiment_randomization_or_confirmatory_p_values":True,
        "main_jae_rc6_unchanged":True
    }
    p=Path(OUTPUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ORIGINAL_FROG_PAIRED_RESULT "+json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
