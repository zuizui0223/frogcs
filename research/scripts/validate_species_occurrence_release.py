#!/usr/bin/env python3
"""Fail-closed release QA for frogcs species occurrence-first research v1.

Only existing committed aggregate source receipts, original-source event
denominators, taxon crosswalk and observational co-reporting tables.
No original RC6 estimator, no GBIF pseudozeros and no stage/feeding claims.
"""
from pathlib import Path
import json
import math
ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/"research/results/species_occurrence_first"

def read(path):
    with open(path,encoding="utf-8") as h:return json.load(h)
def eq(x,y,where):
    assert x==y,(where,x,y)
def close(x,y):
    assert math.isclose(float(x),float(y),abs_tol=1e-8,rel_tol=0),(x,y)
def main():
    p=read(DIR/"observed_profile.json")
    c=read(DIR/"observed_correlations_summary.json")
    m=read(DIR/"DATASET_MANIFEST_V1.json")
    science=read(ROOT/"provenance/CURRENT_RESULTS.json")
    target=read(ROOT/"research/STAGE_LEGACY_INTEGRATION_MANIFEST_V1.json")
    assert target["current_priority"]["priority"]=="SOURCE_NATIVE_SPECIES_OCCURRENCE_FIRST"
    assert target["current_priority"]["stage_focused_mechanistic_models"].startswith("PAUSED")
    eq(science["population"]["matched_pairs"],4236,"RC6 matched pair science")
    eq(science["population"]["principal_history_pairs"],2916,"RC6 prior history science")
    close(science["principal_within_taxon_comparator"]["conditional_residual"],0.2968537316513371)
    record_by_source=p["n_distinct_event_taxon_method_records_by_source"]
    expected={"naamp_positive_calls":310683,"nps_glkn":147913,
              "inbo_adult_chorus":1286,"inbo_larval_census":1648,"hungary_2024":3411}
    eq(record_by_source,expected,"native occurrence totals")
    eq(sum(record_by_source.values()),464941,"all event×species samples")
    eq(m["total_species_event_rows"],464941,"manifest count")
    eq(p["naamp_completed_stop_survey_opportunities"],198757,"NAAMP separately surveyed stops")
    eq(p["source_records_before_stage_collapse"]["hungary_2024"],3429,"original Hungarian survey rows")
    eq(p["duplicate_original_survey_species_rows_by_source"]["hungary_2024"],18,"Hungary duplicated species survey rows")
    eq(p["contradictory_present_and_zero_within_original_survey_species_by_source"]["hungary_2024"],5,"Hungary conflicting source status")
    assert p["status_by_source"]["hungary_2024"]["unresolved"]==5
    assert "protocol_nondetection" not in p["status_by_source"]["naamp_positive_calls"]
    eq(p["deduplicated_stage_rows_by_source"]["inbo_adult_chorus"],150,"INBO original duplicate row arithmetic")
    eq(p["deduplicated_stage_rows_by_source"]["inbo_larval_census"],1347,"INBO original duplicate row arithmetic")
    naamp_nps=next(x for x in p["cross_source_exact_name_overlap"]
                   if x["source_a"]=="nps_glkn" and x["source_b"]=="naamp_positive_calls")
    eq(naamp_nps["n"],9,"original exact binomial name intersection")
    assert "Lithobates clamitans" in naamp_nps["identical_verbatim_taxon_names"]
    assert not naamp_nps["taxonomic_synonym_mapping_performed"]
    assert not naamp_nps["same_physical_sites"]
    assert p["GBIF_1_degree_presence_only_not_merged_with_ponds"]
    assert p["no_taxon_absences_generated_from_naamp_positive_only"]
    assert p["life_stage_removed_from_occurrence_primary_key"]
    co=c["top_lowest_phi"]+c["top_highest_phi"]
    for pair in co:
        count=sum(pair[k] for k in (
            "co_detection_events_n11",
            "a_detected_b_not_called_or_not_observed_n10",
            "a_not_called_or_not_observed_b_detected_n01",
            "both_protocol_not_detected_n00"))
        eq(pair["both_species_explicitly_assessed_original_events"],count,
           pair["source_id"]+" pair contingency")
        assert not pair["actual_biotic_competition_identified"]
    pair=next(x for x in c["top_lowest_phi"]
              if x["source_id"]=="nps_glkn" and
              x["species_a"]=="Lithobates clamitans" and
              x["species_b"]=="Pseudacris crucifer")
    eq(pair["both_species_explicitly_assessed_original_events"],16561,"NPS jointly assessed source original recording")
    close(pair["phi_same_event"],-0.24684218161273777)
    season=pair["season_site_conditioned_co_detection"]
    eq(season["n_informative_site_year_month_strata"],337,"strict same site-year-month")
    eq(season["n_both_species_assessed_in_informative_strata"],4030,"same-site-month source effort")
    close(season["excess_joint_detection_per_100_same_stratum_assessments"],-2.4134217115255283)
    assert season["site_bootstrap_95ci_conditional_on_fixed_strata"][1]<0
    assert c["n_inference_ready_co_assessed_species_pairs"]==150
    report=(DIR/"REPORT_2026-10-26.md").read_text(encoding="utf-8")
    for note in ("464,941","−2.41","9種","相関","競争","198,757"):
        assert note in report,"Report omitted critical ecological qualification: "+note
    assert m["quality_controls"]["RC6_frozen_science_untouched"] is True
    print(json.dumps({
      "status":"PASS",
      "one_native_event_species_database":True,
      "species_event_rows":464941,
      "source_original_taxonomic_exact_shared_US_species":9,
      "native_NPS_co_detection_source_audio_files":16561,
      "NPS_same_site_year_month_excess_copresence_per100":-2.4134217115255283,
      "inference":"source-scored calls and site reports; not competition, pond-level predation or source absences",
      "stage_analysis_is_primary":False,
      "RC6_frozen_source_modified":False},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
