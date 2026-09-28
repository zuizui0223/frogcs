#!/usr/bin/env python3
from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_1.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC9_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_12.md").read_text(encoding="utf-8")
nov=(root/"submission/NOVELTY_AUDIT_V0_9.md").read_text(encoding="utf-8")
rev=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_9.md").read_text(encoding="utf-8")
freeze=json.loads((root/"submission/RC9_STORY_FREEZE_V0_1.json").read_text(encoding="utf-8"))
cross=json.loads((root/"CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
null=json.loads((root/"NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
eq=json.loads((root/"NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
readme=(root/"README.md").read_text(encoding="utf-8")
handoff=(root/"submission/SUBMISSION_HANDOFF_RC9.md").read_text(encoding="utf-8")
checklist=(root/"submission/JAE_PORTAL_CHECKLIST_V0_8.md").read_text(encoding="utf-8")
meta=(root/"submission/SUBMISSION_METADATA_TEMPLATE_V0_6.yml").read_text(encoding="utf-8")
guide=(root/"submission/HUMAN_FINALIZATION_RC9.md").read_text(encoding="utf-8")

title="Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization"
assert m.startswith("# "+title)
assert title in cl
assert freeze["status"]=="frozen_for_submission"
assert freeze["manuscript"]=="MANUSCRIPT_JAE_V1_1.md"
assert cross["decision"]=="STRONG_PASS"
assert cross["generalization_boundary"]["cross_continental_consistency_authorized"] is True
assert cross["generalization_boundary"]["worldwide_universality_authorized"] is False
assert cross["generalization_boundary"]["pooled_effect_size_authorized"] is False
assert null["decision"]=="strong_rejection_of_uniform_activation"
assert eq["decision"]["title_level_equivalence_support"] is True

for x in [
  "40,754",
  "β = -0.0818",
  "95% CI -0.0982 to -0.0654",
  "cross-continental consistency",
  "OR = 0.988",
  "80.9% boundary crossing",
  "92.0% observed",
  "±0.025",
]:
    if x not in m:
        raise SystemExit(f"RC9 manuscript missing: {x}")

for x in [
  "Cross-continental external validation of active-unit taxonomic depth",
  "STRONG PASS",
  "-0.08176",
  "-0.09984",
  "0.8458",
  "-0.04833",
]:
    if x not in si:
        raise SystemExit(f"RC9 SI missing: {x}")

for x in [
  "40,754 expert-validated Australian FrogID recordings",
  "community amplification",
  "community recruitment",
  "cross-continentally consistent",
]:
    if x not in cl:
        raise SystemExit(f"RC9 cover missing: {x}")

for x in [
  "cross-continental component",
  "uniform amplification",
  "worldwide universality",
  "independent north american and australian monitoring systems",
]:
    if x not in nov.lower():
        raise SystemExit(f"RC9 novelty drift: {x}")

for x in [
  "Two continents do not establish a global rule.",
  "FrogID cannot replicate the main matrix analysis.",
  "old NAAMP activity-conditioned",
]:
    if x not in rev:
        raise SystemExit(f"RC9 reviewer matrix missing: {x}")

for x in [
  "JAE RC9 reproducibility package",
  "release/jae-v1-rc9",
  "MANUSCRIPT_JAE_V1_1.md",
  "SUPPORTING_INFORMATION_JAE_RC9_V0_1.md",
  "STRONG PASS",
]:
    if x not in readme:
        raise SystemExit(f"RC9 README authority drift: {x}")

for x in [
  "MANUSCRIPT_JAE_V1_1.md",
  "SUPPORTING_INFORMATION_JAE_RC9_V0_1.md",
  "CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json",
]:
    if x not in handoff or x not in checklist:
        raise SystemExit(f"RC9 handoff/checklist drift: {x}")

for x in [
  "FrogID dataset",
  "10.3897/zookeys.912.38253",
]:
    if x not in meta:
        raise SystemExit(f"RC9 metadata template missing FrogID source: {x}")

for x in [
  "SUBMISSION_METADATA_TEMPLATE_V0_6.yml",
  "MANUSCRIPT_JAE_V1_1.md",
  "SUPPORTING_INFORMATION_JAE_RC9_V0_1.md",
]:
    if x not in guide:
        raise SystemExit(f"RC9 human guide drift: {x}")

forbidden=[
  "worldwide universality is demonstrated",
  "universal rainfall response across frogs",
  "same effect size across continents",
  "identical mechanism across continents",
  "FrogID replicates the four-component matrix geometry",
  "rainfall caused"
]
for surface,name in [(m,"manuscript"),(cl,"cover"),(nov,"novelty")]:
    low=surface.lower()
    for x in forbidden:
        if x.lower() in low:
            raise SystemExit(f"{name} overclaim: {x}")

print("RC9 scientific submission package QA PASS")
