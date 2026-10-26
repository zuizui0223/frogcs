#!/usr/bin/env python3
"""Reproducibility QA: never refit or alter frozen RC6, read published receipts."""
from pathlib import Path
import json
import math
import re
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/"research/manuscript/INTEGRATED_FROG_ECOLOGY_DRAFT_V0_1.md"

def load(name):
    p=ROOT/name
    assert p.is_file(), "Missing cited source: "+name
    return json.loads(p.read_text(encoding="utf-8"))

def close(a,b):
    assert math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-8),(a,b)

def main():
    j=load("research/STAGE_LEGACY_INTEGRATION_MANIFEST_V1.json")
    rc6=load("provenance/CURRENT_RESULTS.json")
    nps=load("research/results/nps_stage_crosslag/observed_results.json")
    own=load("research/results/nps_glkn_history/observed_results.json")
    g0=load("research/results/part2_g0/observed_source_eligibility.json")
    tax=load("research/results/part2_g0/inbo_species_time_eligibility.json")
    hyla=load("research/results/part2_inbo_hyla_g1/observed_results.json")

    full=load("research/results/full_globi_2026_stage_gbif_grid/observed_results.json")
    shift=load("research/results/month_shift_globi_gbif/observed_results.json")
    matched=load("research/results/expanded_stage_specificity/observed_results.json")
    flooded=load("research/results/earthenv_gbif_matched_stage/observed_results.json")
    monthly_rain=load("research/results/globi_gbif_rain_contrast/observed_results.json")
    assert full["source_integrity"]["full_source_parquet_rows"]==24453954
    assert full["full_globi_stages"]["valid_certain_nonself_raw_stage_rows"]==1240
    assert full["full_globi_stages"]["unique_valid_nonself_directed_stage_pairs"]==881
    sh=next(x for x in shift["per_threshold"] if x["threshold_records_per_species_stage_grid_month"]==1)
    assert sh["all_eligible_gloBI_species_stage_pairs"]==18
    assert sh["pairs_observed_above_11_shift_mean"]==16
    assert sh["pooled_exact_reports_observed"]==16605
    m1=next(x for x in matched["matched_pairs_each_threshold"] if x["minimum_GBIF_records_per_taxon_stage_gridmonth"]==1)
    m5=next(x for x in matched["matched_pairs_each_threshold"] if x["minimum_GBIF_records_per_taxon_stage_gridmonth"]==5)
    assert m1["matched_GloBI_directed_stage_pairs"]==56 and m1["focal_phase_ratio_greater_than_median_control"]==31
    assert m5["matched_GloBI_directed_stage_pairs"]==56 and m5["focal_phase_ratio_greater_than_median_control"]==26
    assert m5["median_focal_minus_control_phase_ratio"]<0
    env=next(x for x in flooded["source_pairs_with_both_nearzero_and_high_flooded_bins"] if x["threshold"]==1)
    assert env["n_matched_source_pairs"]==32
    close(env["median_high_minus_nearzero_focal_specificity"],-0.028117363791445027)
    rain=next(x for x in monthly_rain["per_threshold"] if x["min_records_per_taxon_stage_grid_month"]==1)
    assert rain["pairs_with_enough_informative_grid_years"]==15
    assert rain["pairs_where_monthly_rain_co_report_is_greater_than_single_report"]==10
    assert j["paper_strategy"]["target"]=="one_conditional_integrated_flagship_manuscript_in_frogcs"
    assert j["paper_strategy"]["rc6_standalone_submission"]=="deferred_not_deleted_not_claimed_submitted"
    assert j["paper_strategy"]["future_manuscript_ready"] is False
    assert rc6["population"]["matched_pairs"]==4236
    assert rc6["population"]["principal_history_pairs"]==2916
    close(rc6["principal_within_taxon_comparator"]["conditional_residual"],0.2968537316513371)
    close(own["adjusted_strict_prior_strong"]["own_prior_strong_beta"],0.46418762439474126)
    cross=next(x for x in nps["comparisons"] if x["comparison"]=="primary_green_prior_to_wood_call")["main_adjusted"]
    assert cross["eligible_rows"]==431
    close(cross["primary_exposure_previous_year_beta_risk_difference"],0.014321148927807066)
    assert cross["site_cluster_approx_ci95"][0]<0<cross["site_cluster_approx_ci95"][1]
    assert j["prior_claims"]["NPS_green_to_wood_annual_acoustic_suppression_supported"] is False
    assert g0["inbo_between_protocol_join"]["exact_shared_location_ids"]==96
    assert g0["inbo_between_protocol_join"]["exact_shared_site_years"]==247
    assert tax["focal_taxa"]["Hyla arborea"]["chorus_event_precedes_larval_event_site_year"]==245
    assert tax["focal_taxa"]["Pelobates fuscus"]["chorus_event_precedes_larval_event_site_year"]==2
    assert hyla["complete_case_site_years"]==245 and hyla["independent_site_ids"]==93
    assert hyla["outcome_recorded_present"]==149 and hyla["outcome_recorded_absent"]==96
    assert hyla["model_config"]["use_permanent"] is False
    assert hyla["model_config"]["permanent_water_coverage"]==0
    assert hyla["simultaneous_measured_predator_stage"] is False
    b0=hyla["models"]["M0_time_hydrology_recording"]["held_out_site_group_brier"]
    b1=hyla["models"]["M1_add_prior_chorus"]["held_out_site_group_brier"]
    assert b1<b0
    late=hyla["temporal_2024_2025_validation"]
    t0=late["models"]["M0"]["brier"]
    t1=late["models"]["M1"]["brier"]
    assert late["estimable"] and t1>t0
    txt=DOC.read_text(encoding="utf-8")
    for h in ("## Working abstract","## 1. Introduction","## 2. Methods",
              "## 3. Results","## 4. Discussion","## 5. Conclusion",
              "## Table 1.","## Reproducibility and references"):
        assert h in txt, "Missing manuscript section: "+h
    for phrase in ("0.296854","+0.014321","0.242712","0.347862",
                   "not supporting the predicted negative suppression",
                   "no local hydroperiod term was fitted",
                   "not estimable","not submission-ready",
                   "16/18","31/56","26/56","not a demonstration of recorded predation"):
        assert phrase.lower() in txt.lower(),"Missing scientific claim boundary: "+phrase
    assert txt.count(chr(96)*3)%2==0
    links=re.findall(r"\[[^\]]+\]\(([^)\s]+)\)",txt)
    check=0
    for link in links:
        if link.startswith(("https:","http:","mailto:","/")):continue
        target=(DOC.parent/link.split("#")[0]).resolve()
        assert target.is_relative_to(ROOT),"External relative reference: "+link
        assert target.is_file(),"Broken manuscript source link: "+link
        check+=1
    print(json.dumps({"status":"PASS","rc6_original_readout_unchanged":True,
          "one_integrated_paper_selected":True,"nps_H1A_negative_result_retained":True,
          "inbo_early_site_gain":round(b0-b1,6),
          "inbo_future_year_loss":round(t1-t0,6),
          "global_stage_shift_above_null":16,
          "global_matched_specificity_strict":26,
          "global_predation_identified":False,
          "measured_stage_predation_identified":False,
          "relative_source_links_resolved":check,
          "manuscript_submission_ready":False},indent=2))

if __name__=="__main__":
    main()
