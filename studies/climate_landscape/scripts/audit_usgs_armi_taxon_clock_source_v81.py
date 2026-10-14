#!/usr/bin/env python3
"""v8.1 post-outcome SOURCE QUALITY ONLY for CC0 USGS original 2003–08/2024
calling records: era-private taxon labels and ambiguous same-person day clocks.

Precommitted plan in USGS_ARMI_REAL_20Y_FROG_DETECTED_COMMUNITY_COMPARISON.md.
No alternate Jaccard, species effect, site-level records or raw positions.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime
from hashlib import sha256
from io import StringIO
from pathlib import Path
import csv,json,re

import analyze_usgs_armi_historic2024_original_detected_assemblages as base

OUT="studies/climate_landscape/receipts/USGS_ARMI_ORIGINAL_TAXON_KEY_AND_AMBIGUOUS_VISITS_QC_V81.json"

def classify_label(s):
    words=s.replace("("," ").split()
    if re.search(r"\bsp\.?\b|cf\.|aff\.|spp\.?",s,re.I):
        return "uncertain_sp_or_affinity_label"
    if len(words)==2 and all(words):
        return "binomial_literal"
    if len(words)==3:
        return "trinomial_literal_or_other"
    return "unclassified_literal"

def ambiguous_field_keys(data):
    seen=defaultdict(set)
    original_rows=Counter()
    for row in csv.DictReader(StringIO(data.decode("utf-8-sig"))):
        site=(row.get("Site") or "").strip()
        day=(row.get("Date") or "").strip()
        who=(row.get("Observer") or "").strip()
        method=(row.get("Method") or "").strip()
        clock=(row.get("Arrival_time") or "").strip()
        if not site or not day or not who:continue
        key=(site,day,who)
        seen[key].add((method,clock))
        original_rows[key]+=1
    ambiguous={k:v for k,v in seen.items() if len(v)>1}
    cats=Counter()
    all_event_count=0
    for k,v in ambiguous.items():
        c=len({clock for _,clock in v})
        m=len({method for method,_ in v})
        if c>1 and m>1: cats["both_clock_and_method_vary"]+=1
        elif c>1:cats["multiple_start_clocks_only"]+=1
        elif m>1:cats["multiple_methods_only"]+=1
        else:cats["other_source_multiplicity"]+=1
        all_event_count+=len(v)
    return ambiguous,dict(sorted(cats.items())),{
        "n_source_site_date_observer_keys":len(seen),
        "n_source_same_site_date_observer_keys_with_multiple_clock_or_method":len(ambiguous),
        "n_distinct_start_time_method_event_keys_within_ambiguous_groups":all_event_count,
        "n_original_species_line_rows_within_ambiguous_groups":
             sum(original_rows[k] for k in ambiguous),
        "source_repeat_ambiguity_caused_by":dict(sorted(cats.items())),
        "source_event_multiplicity_may_be_true_repeat_surveys":True,
    }

def count_ambiguity_in_cohort(keys,all_sites,matched_sites,release):
    in_sites={k for k in keys if k[0] in all_sites}
    in_matched={k for k in keys if k[0] in matched_sites}
    return {
        "era":release,
        "n_ambiguous_source_person_days_among_292_geo_consistent_sites":len(in_sites),
        "n_ambiguous_source_person_days_among_67_frozen_selected_sites":len(in_matched),
        "n_distinct_original_matched_sites_with_ambiguous_person_days":
            len({k[0] for k in in_matched}),
        "n_distinct_all_geometry_pass_sites_with_ambiguous_person_days":
            len({k[0] for k in in_sites}),
    }

def removed_matching_site_potential(ambiguous_keys,oldraw,newvalid,sites):
    """No outcomes inspected. Source *opportunity* only, not J recalculation."""
    from collections import defaultdict
    import audit_armi2024_original_visit_observer_v80 as clock_source
    modern=defaultdict(list)
    for e in newvalid.values():
        if e.site in sites and e.method=="Microphone" and e.day.month in (6,7,8):
            modern[(e.site,e.day.month)].append(e)
    found_sites=set()
    matching_distinct_events=0
    for key,values in ambiguous_keys.items():
        site,ds,person=key
        if site not in sites:continue
        try: day=datetime.strptime(ds,"%Y-%m-%d").date()
        except ValueError:continue
        if day.month not in (6,7,8):continue
        for method,time in values:
            if method!="Microphone":continue
            t=clock_source.to_minutes(time)
            if t is None:continue
            pool=modern.get((site,day.month),[])
            if any(min(abs(t-e.times),1440-abs(t-e.times))<=60 for e in pool):
                found_sites.add(site)
                matching_distinct_events+=1
    return {
        "n_geo_consistent_sites_with_a_historical_ambiguous_original_clock_event_potentially_matching_modern_mic_start":len(found_sites),
        "n_historical_ambiguous_clock_events_with_source_method_month_start_match":matching_distinct_events,
        "source_eligibility_only_not_observed_frog_reanalysis":True
    },found_sites

def study(raw,accepted,matched_sites,oldraw,newvalid,oldtaxa,newtaxa,pairs):
    oldonly=oldtaxa-newtaxa
    newonly=newtaxa-oldtaxa
    globalnames={
        "historic_release_literal_taxon_count":len(oldtaxa),
        "new_2024_literal_taxon_count":len(newtaxa),
        "exact_literal_source_names_shared":len(oldtaxa&newtaxa),
        "historic_release_only_taxon_count":len(oldonly),
        "new_release_only_taxon_count":len(newonly),
        # Original taxon NAME strings only (no site/animal observation rows).
        # These are public taxonomy vocabulary, not protected locations.
        "historic_only_public_taxon_name_vocabulary":sorted(oldonly),
        "new_only_public_taxon_name_vocabulary":sorted(newonly),
        "historic_only_taxon_label_grammar":dict(Counter(map(classify_label,oldonly))),
        "new_only_taxon_label_grammar":dict(Counter(map(classify_label,newonly))),
        "source_synonym_mappings_performed":0,
        "external_taxonomic_name_to_concept_matching_is_not_verified":True,
        "ITIS_example_taxon_note":"Acris crepitans blanchardi is an ITIS synonym of Acris blanchardi; Acris crepitans is a DISTINCT currently accepted species and must not be blindly merged.",
        "ITIS_taxonomic_reference":"https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=TSN&search_value=774220",
    }
    names=Counter()
    for site,a,b in pairs:
        h=bool(a.taxa&oldonly)
        n=bool(b.taxa&newonly)
        if h and n:names["both_eras_with_release_private_taxon_label"]+=1
        elif h:names["historical_release_private_only"]+=1
        elif n:names["new_release_private_only"]+=1
        else:names["no_release_private_taxon_in_either_selected_species_list"]+=1
    taxa_exposure={
        "n_frozen_67_site_pairs":len(pairs),
        "selected_pairs_by_taxonomic_comparability_flag":dict(sorted(names.items())),
        "n_selected_pairs_affected_by_any_era_private_literal_taxon":
           len(pairs)-names["no_release_private_taxon_in_either_selected_species_list"],
        "does_not_refit_or_harmonise_original_jaccard":True,
        "released_species_labels_appear_only_in_global_vocabulary":True,
        "no_taxon_by_site_or_time_table_published":True,
    }
    groups={}
    for era,key in (("old","history_2003_2008"),("new","new_2024")):
        ambiguous,types,stats=ambiguous_field_keys(raw[key])
        groups[key]={"grouping":stats,
            "selected_cohort_ambiguity":count_ambiguity_in_cohort(
                ambiguous,accepted,matched_sites,era),
        }
        if era=="old":
            match,match_sites=removed_matching_site_potential(ambiguous,raw[key],newvalid,accepted)
            groups[key]["source_opportunity_possible_unexamined_valid_visit_match"]=match
            groups[key]["selected_67_sites_with_any_potential_missing_valid_historical_match"]={
                "n_sites":len(match_sites&matched_sites),
                "original_67_site_cohort_still_unchanged":True
            }
    return {"global_literal_taxon_alignment":globalnames,
             "same_original_67_site_pair_label_impact_without_jaccard_refit":taxa_exposure,
             "original_site_date_observer_multiple_times_quality":groups}

def tests():
    mock=("Site,Date,Observer,Method,Arrival_time,Species\n"
          "LOC,2005-06-01,O1,Microphone,20:05,Frog1\n"
          "LOC,2005-06-01,O1,Microphone,20:05,Frog2\n"
          "LOC,2005-06-01,O1,Microphone,21:20,Frog3\n"
          "LOC,2005-06-01,O2,Ear,20:05,Frog3\n").encode()
    groups,types,result=ambiguous_field_keys(mock)
    assert len(groups)==1 and result["n_source_site_date_observer_keys"]==2
    assert result["n_distinct_start_time_method_event_keys_within_ambiguous_groups"]==2
    assert result["source_repeat_ambiguity_caused_by"]["multiple_start_clocks_only"]==1
    assert classify_label("Rana sp.")=="uncertain_sp_or_affinity_label"
    assert classify_label("Acris blanchardi")=="binomial_literal"
    assert classify_label("Acris crepitans blanchardi")=="trinomial_literal_or_other"
    print("PASS: original multi-clock vs duplicate species-line distinction; uncertain taxon syntax")

def main():
    tests()
    raw,sourceprofile,loc=base.full_originals()
    accepted,_=base.physical_site_candidates(loc["history_2003_2008"],loc["new_2024"])
    hist,hprofile,oldtaxa=base.original_events(raw["history_2003_2008"],"2003–08")
    newer,nprofile,newtaxa=base.original_events(raw["new_2024"],"2024")
    if len(oldtaxa)!=14 or len(newtaxa)!=10 or len(oldtaxa&newtaxa)!=9:
        raise ValueError("ORIGINAL_SOURCE_TAXON_VOCABULARY_CHANGED")
    matched=base.eligible_epoch_pairs(hist,newer,accepted,60)
    if len(matched)!=67:raise ValueError("ORIGINAL_FROZEN_67_SITE_MATCH_CHANGED")
    orig=base.observational_summary(matched)
    if abs(orig["source_detected_species_list_Jaccard_mean"]-.416414)>1e-6:
        raise ValueError("FROZEN_CALCULATION_CHANGED")
    frozen_sites={s for s,_,_ in matched}
    qc=study(raw,accepted,frozen_sites,raw,newer,oldtaxa,newtaxa,matched)
    out={
        "status":"ORIGINAL_USGS_PUBLIC_TAXON_NAME_AND_MULTI_CLOCK_SOURCE_QC_EXECUTED",
        "historic_sha256":sha256(raw["history_2003_2008"]).hexdigest(),
        "new2024_sha256":sha256(raw["new_2024"]).hexdigest(),
        "source_files":"USGS 2003-08 and 2024 ver.1.1 April 2026 CC0 original CSV",
        "original_separate_source_verification": "https://github.com/zuizui0223/frogcs/actions/runs/38493167832",
        "plan_committed_before_this_diagnostic_result":True,
        "previous_ecological_outcome_was_already_read":True,
        "existing_67_site_frozen_jaccard_unmodified":orig["source_detected_species_list_Jaccard_mean"],
        "n_source_geospatial_consistent_sites":len(accepted),
        "new_diagnostics":qc,
        "no_merged_taxonomic_concepts_or_refit":True,
        "ambiguous_original_clock_keys_not_assumed_corrupt_or_independent":True,
        "no_original_site_person_exact_dates_coordinates_or_taxon_by_site_values_published":True,
        "not_an_occupancy_change_or_causal_water_test":True,
        "JAE_RC6_main_unchanged":True,
    }
    p=Path("studies/climate_landscape/receipts/USGS_ARMI_V81_TAXON_CLOCK_SOURCE_DIAGNOSTIC.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("USGS_V81_QC "+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__":main()
