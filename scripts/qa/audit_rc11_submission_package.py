#!/usr/bin/env python3
from pathlib import Path
import json
import re

root=Path(__file__).resolve().parents[2]
m=(root/"MANUSCRIPT_JAE_V1_3.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC11_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_13.md").read_text(encoding="utf-8")
freeze=json.loads((root/"provenance/submission/RC11_STORY_FREEZE_V0_1.json").read_text(encoding="utf-8"))
obs=json.loads((root/"provenance/summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
pers=json.loads((root/"provenance/summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
orig=json.loads((root/"provenance/summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
readme=(root/"README.md").read_text(encoding="utf-8")
title_page=(root/"JAE_TITLE_PAGE_V0_8.template.md").read_text(encoding="utf-8")
meta=(root/"submission/SUBMISSION_METADATA_TEMPLATE_V0_7.yml").read_text(encoding="utf-8")
citation=(root/"submission/CITATION.cff.template").read_text(encoding="utf-8")
fig2=(root/"figures_ecology_v1_2/FIGURE_2_ALLOCATION_NULLS_V0_1.svg").read_text(encoding="utf-8")
fig3=(root/"figures_ecology_v1_2/FIGURE_3_CROSS_DATASET_DEPTH_V0_1.svg").read_text(encoding="utf-8")

title="Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"
assert m.startswith("# "+title)
for surface in (cl,title_page,meta,citation):
    assert title in surface

assert freeze["status"]=="frozen_for_submission"
assert freeze["parent_release"]=="RC10"
assert freeze["scientific_story_changed_from_rc10"] is False
assert freeze["manuscript"]=="MANUSCRIPT_JAE_V1_3.md"
assert freeze["supporting_information"]=="SUPPORTING_INFORMATION_JAE_RC11_V0_1.md"
assert freeze["reserved_revision_analysis"]["species_specific_activation_null"]["status"]=="not_run"
assert freeze["reserved_revision_analysis"]["species_specific_activation_null"]["authorized_pre_submission"] is False

assert obs["prefrozen_classification"]=="observer_robust"
assert obs["coverage"]["same_observer_pairs"]==3152
assert obs["coverage"]["same_observer_routes"]==500
assert obs["coverage"]["same_observer_unique_observers"]==542
assert obs["observed_matrix"]["boundary_crossing_share"] > obs["uniform_null"]["kappa_2"]["ci95"][1]
assert obs["observed_matrix"]["boundary_crossing_share"] > obs["persistence_preserving_null"]["anchor_0_75"]["ci95"][1]
for v in obs["headline_models"].values():
    assert v["ci95"][0] > 0

assert pers["decision"]=="strong_rejection_under_persistence_anchoring"
assert orig["decision"]=="strong_rejection_of_uniform_activation"

# Submission-facing scientific checks after copyediting.
assert not re.search(r"\bRC\d+\b",m+"\n"+si)
assert "readback" not in (m+"\n"+si).lower()
for x in [
    "β = 0.384",
    "β = 0.0794",
    "0.2859",
    "92.0% observed",
    "80.9%",
    "77.9%",
    "3,152 same-observer pairs",
    "cross-dataset consistency",
    "not as a replication claim",
    "a null allowing species-specific shifts",
    "not a unique causal pathway",
]:
    assert x.lower() in m.lower(), x

for x in [
    "### Same-observer sensitivity",
    "3,152 of 4,236 pairs (74.4%)",
    "500 routes and 542 observer identifiers",
    "80.3%",
    "79.1%",
    "observer robust",
]:
    assert x.lower() in si.lower(), x


for x in [
    "JAE RC11 reproducibility package",
    "MANUSCRIPT_JAE_V1_3.md",
    "SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",
    "provenance/summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json",
    "species-specific rainfall-response shifts",
]:
    assert x in readme, x


for x in ["Persistence null","Observed 92.0%","Anchor a=.90"]:
    assert x in fig2
for x in ["Cross-dataset consistency only","NAAMP","FrogID"]:
    assert x in fig3

forbidden=[
    "worldwide universality is demonstrated",
    "same effect size across continents",
    "identical mechanism across continents",
    "rainfall caused",
    "species-specific heterogeneity is excluded",
]
for surface,name in [(m,"manuscript"),(si,"supporting_information"),(cl,"cover")]:
    for x in forbidden:
        if x.lower() in surface.lower():
            raise SystemExit(f"{name} overclaim: {x}")

print({
    "status":"PASS",
    "release":"RC11",
    "submission_surface_internal_labels_removed": True,
    "same_observer_pairs":obs["coverage"]["same_observer_pairs"],
    "same_observer_classification":obs["prefrozen_classification"],
    "species_specific_null":"reserved_not_run",
})
