#!/usr/bin/env python3
from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_2.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC10_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_13.md").read_text(encoding="utf-8")
nov=(root/"submission/NOVELTY_AUDIT_V0_10.md").read_text(encoding="utf-8")
rev=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_10.md").read_text(encoding="utf-8")
freeze=json.loads((root/"submission/RC10_STORY_FREEZE_V0_1.json").read_text(encoding="utf-8"))
pers=json.loads((root/"NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
orig=json.loads((root/"NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
cross=json.loads((root/"CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
readme=(root/"README.md").read_text(encoding="utf-8")
handoff=(root/"submission/SUBMISSION_HANDOFF_RC10.md").read_text(encoding="utf-8")
checklist=(root/"submission/JAE_PORTAL_CHECKLIST_V0_9.md").read_text(encoding="utf-8")
meta=(root/"submission/SUBMISSION_METADATA_TEMPLATE_V0_7.yml").read_text(encoding="utf-8")
guide=(root/"submission/HUMAN_FINALIZATION_RC10.md").read_text(encoding="utf-8")
title_page=(root/"JAE_TITLE_PAGE_V0_8.template.md").read_text(encoding="utf-8")
citation=(root/"submission/CITATION_V0_5.cff.template").read_text(encoding="utf-8")
fig2=(root/"figures_ecology_v1_2/FIGURE_2_ALLOCATION_NULLS_V0_1.svg").read_text(encoding="utf-8")
fig3=(root/"figures_ecology_v1_2/FIGURE_3_CROSS_DATASET_DEPTH_V0_1.svg").read_text(encoding="utf-8")

title="Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"
assert m.startswith("# "+title)
assert title in cl
assert title in meta
assert title in title_page
assert title in citation
assert freeze["status"]=="frozen_for_submission"
assert freeze["manuscript"]=="MANUSCRIPT_JAE_V1_2.md"
assert pers["decision"]=="strong_rejection_under_persistence_anchoring"
assert pers["title_support"]["boundary_biased_title_authorized"] is True
assert orig["decision"]=="strong_rejection_of_uniform_activation"

for a in ("anchor_0_50","anchor_0_75_primary","anchor_0_90"):
    assert pers[a]["omnibus_p"] < 0.05

for x in [
  "persistence-preserving stress test",
  "77.9%",
  "73.4–82.8%",
  "22.1%",
  "directional cross-dataset consistency",
  "secondary bounded context",
]:
    if x not in m:
        raise SystemExit(f"RC10 manuscript missing: {x}")

assert "external validation" not in m.lower()
assert "independent replication" not in m.lower()
assert "without practical homogenization" not in m.splitlines()[0].lower()

for x in [
  "# Supporting Information — JAE RC10 v1.2",
  "RC10 persistence-preserving uniform-activation stress test",
  "77.9%",
  "cross-dataset consistency",
]:
    if x.lower() not in si.lower():
        raise SystemExit(f"RC10 SI drift: {x}")

for x in ["persistence-preserving stress test","77.9%","cross-dataset directional consistency"]:
    if x not in cl:
        raise SystemExit(f"RC10 cover drift: {x}")

for x in ["77.9%","22.1%","FrogID is **not** described as independent validation"]:
    if x not in nov:
        raise SystemExit(f"RC10 novelty drift: {x}")

for x in ["Hierarchical shrinkage makes stable cells too exchangeable","title’s old","cross-dataset consistency"]:
    if x.lower() not in rev.lower():
        raise SystemExit(f"RC10 reviewer matrix drift: {x}")

for x in [
  "JAE RC10 reproducibility package",
  "release/jae-v1-rc10",
  "MANUSCRIPT_JAE_V1_2.md",
  "NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json",
]:
    if x not in readme:
        raise SystemExit(f"RC10 README drift: {x}")

for x in ["MANUSCRIPT_JAE_V1_2.md","SUPPORTING_INFORMATION_JAE_RC10_V0_1.md","NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json"]:
    if x not in handoff or x not in checklist:
        raise SystemExit(f"RC10 handoff/checklist drift: {x}")

for x in ["JAE_TITLE_PAGE_V0_8.template.md","SUBMISSION_METADATA_TEMPLATE_V0_7.yml","CITATION_V0_5.cff.template"]:
    if x not in readme and x not in handoff:
        raise SystemExit(f"RC10 template authority drift: {x}")

for x in ["Persistence null","Observed 92.0%","Anchor a=.90"]:
    if x not in fig2:
        raise SystemExit(f"RC10 Figure 2 drift: {x}")
for x in ["Cross-dataset consistency only","NAAMP","FrogID"]:
    if x not in fig3:
        raise SystemExit(f"RC10 Figure 3 drift: {x}")

forbidden=[
  "worldwide universality is demonstrated",
  "same effect size across continents",
  "identical mechanism across continents",
  "rainfall caused"
]
for surface,name in [(m,"manuscript"),(cl,"cover"),(nov,"novelty")]:
    for x in forbidden:
        if x.lower() in surface.lower():
            raise SystemExit(f"{name} overclaim: {x}")

print("RC10 scientific submission package QA PASS")
