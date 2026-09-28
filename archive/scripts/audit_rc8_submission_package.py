#!/usr/bin/env python3
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_0.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC8_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_10.md").read_text(encoding="utf-8")
nov=(root/"submission/NOVELTY_AUDIT_V0_7.md").read_text(encoding="utf-8")
rev=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_7.md").read_text(encoding="utf-8")
null=json.loads((root/"NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
eq=json.loads((root/"NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
tree=json.loads((root/"submission/RC8_STORY_DECISION_TREE_V0_1.json").read_text(encoding="utf-8"))
scope=json.loads((root/"submission/RC8_SCOPE_UNFREEZE_V0_1.json").read_text(encoding="utf-8"))

freeze=json.loads((root/"submission/RC8_STORY_FREEZE_V0_1.json").read_text(encoding="utf-8"))
readme=(root/"README.md").read_text(encoding="utf-8")
title_page=(root/"JAE_TITLE_PAGE_V0_6.template.md").read_text(encoding="utf-8")
metadata_template=(root/"submission/SUBMISSION_METADATA_TEMPLATE_V0_5.yml").read_text(encoding="utf-8")
human_guide=(root/"submission/HUMAN_FINALIZATION_RC8.md").read_text(encoding="utf-8")
metadata_renderer=(root/"scripts/render_submission_metadata.py").read_text(encoding="utf-8")
citation_template=(root/"submission/CITATION_V0_3.cff.template").read_text(encoding="utf-8")
handoff=(root/"submission/SUBMISSION_HANDOFF_RC8.md").read_text(encoding="utf-8")
checklist=(root/"submission/JAE_PORTAL_CHECKLIST_V0_7.md").read_text(encoding="utf-8")
jae_audit=(root/"submission/JAE_INITIAL_SUBMISSION_AUDIT_2026_09_28.md").read_text(encoding="utf-8")
compliance_receipt=json.loads((root/"submission/RC8_POSTFREEZE_JAE_INITIAL_SUBMISSION_COMPLIANCE_RECEIPT_V0_1.json").read_text(encoding="utf-8"))
hypothesis_receipt=json.loads((root/"submission/RC8_POSTFREEZE_HYPOTHESIS_SPINE_RECEIPT_V0_1.json").read_text(encoding="utf-8"))

generic_docx=(root/".github/workflows/anonymous_docx.yml").read_text(encoding="utf-8")
docx_builder=(root/"scripts/build_jae_anonymous_docx.py").read_text(encoding="utf-8")
doi_finalizer=(root/"scripts/finalize_archive_doi.py").read_text(encoding="utf-8")

title="Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization"
assert m.startswith("# "+title)
assert title in cl
assert null["decision"]=="strong_rejection_of_uniform_activation"
assert null["primary_omnibus"]["monte_carlo_p"] < 0.05
assert eq["decision"]["title_level_equivalence_support"] is True
assert tree["status"]=="frozen_before_uniform_null_readback"
assert scope["status"]=="author_directed_inferential_repair"

assert freeze["status"]=="frozen_for_submission"
assert freeze["manuscript"]=="MANUSCRIPT_JAE_V1_0.md"
assert freeze["title"]==title

for x in [
  "80.9% boundary crossing",
  "95% null interval 74.2–87.4%",
  "92.0% observed",
  "Monte Carlo P = 0.001",
  "Within-core rearrangement was 8.0% observed versus 19.1% expected",
  "90% CI -0.0107 to 0.00968",
  "null rejection does not identify a unique species-level mechanism"
]:
    if x not in m:
        raise SystemExit(f"RC8 manuscript missing: {x}")

for x in [
  "# Supporting Information — JAE RC8 v1.0",
  "Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization",
  "| 2 | .000999 | 80.9% | 74.2–87.4% | 92.0% |",
  "The null was strongly rejected under all three specifications",
  "The equivalence claim applies only to the pairwise Sørensen",
  "implementation repairs were versioned before successful endpoint readback"
]:
    if x not in si:
        raise SystemExit(f"RC8 SI missing: {x}")

for x in [
  "It predicted 80.9% boundary crossing",
  "four-component allocation rejected uniform activation",
  "without practical homogenization"
]:
    if x not in cl:
        raise SystemExit(f"RC8 cover missing: {x}")

for x in [
  "uniform increase in baseline acoustic propensities",
  "80.9%",
  "route-new taxonomic participation"
]:
    if x not in nov:
        raise SystemExit(f"RC8 novelty missing: {x}")

for x in [
  "A high 92% boundary-crossing share is exactly what uniform activation would produce.",
  "κ=1,2,5",
  "pairwise Sørensen slope"
]:
    if x not in rev:
        raise SystemExit(f"RC8 reviewer matrix missing: {x}")

fig1=(root/"figures_ecology_v1_0/FIGURE_1_METACOMMUNITY_EXPANSION_V0_1.svg").read_text(encoding="utf-8")
if "without practical Sørensen homogenization" not in fig1:
    raise SystemExit("RC8 Figure 1 wording drift")

fig=(root/"figures_ecology_v1_0/FIGURE_2_UNIFORM_NULL_COMPARISON_V0_1.svg").read_text(encoding="utf-8")
for x in ["Obs 36.9%","Null 27.4%","Obs 8.0%","Null 19.1%","Monte Carlo P = 0.001"]:
    if x not in fig:
        raise SystemExit(f"RC8 Figure 2 missing: {x}")


for x in [
  "JAE RC8 reproducibility package",
  "release/jae-v1-rc8",
  "MANUSCRIPT_JAE_V1_0.md",
  "SUPPORTING_INFORMATION_JAE_RC8_V0_1.md",
  "observed: **92.0%**",
  "80.9%"
]:
    if x not in readme:
        raise SystemExit(f"RC8 README authority drift: {x}")

for x in [
  "address: \"[INSTITUTIONAL POSTAL ADDRESS]\"",
  "relevant_institutions_approve_submission: false",
  "work_original_and_acknowledged: false",
  "legal_requirements_confirmed: false",
  "conflict_of_interest:",
  "statement_on_inclusion:"
]:
    if x not in metadata_template:
        raise SystemExit(f"RC8 metadata template missing JAE-required field: {x}")

for x in [
  "SUBMISSION_METADATA_TEMPLATE_V0_5.yml",
  "JAE_SUBMISSION_METADATA_YAML",
  "relevant_institutions_approve_submission",
  "Do not claim collaboration or stakeholder engagement that did not occur."
]:
    if x not in human_guide:
        raise SystemExit(f"RC8 human-finalization guide drift: {x}")

for x in [
  "conflict_of_interest statement required for JAE submission",
  "relevant_institutions_approve_submission",
  "work_original_and_acknowledged",
  "legal_requirements_confirmed",
  '"incidence matrix"',
  '"species richness"'
]:
    if x not in metadata_renderer:
        raise SystemExit(f"RC8 metadata renderer drift: {x}")

for name,surface in [
    ("title page",title_page),
    ("metadata template",metadata_template),
    ("citation template",citation_template)
]:
    if title not in surface:
        raise SystemExit(f"RC8 title missing from {name}")

for x in [
  "release/jae-v1-rc8",
  "submission/jae-v1",
  "RC8_STORY_FREEZE_V0_1.json",
  "MANUSCRIPT_JAE_V1_0.md"
]:
    if x not in handoff:
        raise SystemExit(f"RC8 handoff drift: {x}")

for x in [
  "RC8_STORY_FREEZE_V0_1.json",
  "MANUSCRIPT_JAE_V1_0.md",
  "NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json",
  "NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json"
]:
    if x not in checklist:
        raise SystemExit(f"RC8 checklist drift: {x}")


for x in [
  "canonical RC8/v1.0 anonymous-DOCX workflow",
  "MANUSCRIPT_JAE_V1_0.md",
  "SUPPORTING_INFORMATION_JAE_RC8_V0_1.md"
]:
    if x not in generic_docx:
        raise SystemExit(f"generic anonymous-DOCX alias drift: {x}")

if 'default=str(BASE / "MANUSCRIPT_JAE_V1_0.md")' not in docx_builder:
    raise SystemExit("anonymous-DOCX default source is not RC8 v1.0")
if 'default="MANUSCRIPT_JAE_V1_0.md"' not in doi_finalizer:
    raise SystemExit("archive-finalization default source is not RC8 v1.0")


for x in [
  "combined current proxy: ~7,204 words",
  "current: ~293 words",
  "current `submission/COVER_LETTER_JAE_V0_10.md`: ~347 words",
  "References are alphabetically ordered",
  "Automated requirements"
]:
    if x not in jae_audit:
        raise SystemExit(f"JAE compliance audit drift: {x}")

assert compliance_receipt["scientific_unfreeze"] is False
assert compliance_receipt["verified_current_metrics"]["manuscript_words_approx"] == 7091
assert compliance_receipt["verified_current_metrics"]["combined_proxy_words_approx"] == 7204
assert compliance_receipt["verified_current_metrics"]["abstract_words_approx"] == 293
assert compliance_receipt["verified_current_metrics"]["cover_letter_words_approx"] == 347

assert hypothesis_receipt["scientific_unfreeze"] is False
for x in [
  "**Q1: Does recent-rain activity expand the realized community along both spatial and taxonomic axes?**",
  "**Q2: Is the resulting matrix geometry distinguishable from simple uniform amplification?**",
  "**Q3: Does expansion materially erode local compositional differentiation?**",
  "**community amplification** and **community recruitment**"
]:
    if x not in m:
        raise SystemExit(f"RC8 question-spine drift: {x}")

forbidden=[
  "rainfall caused the expansion",
  "uniform activation proves",
  "hydration mediated the expansion",
  "beta diversity is exactly unchanged"
]
for surface,name in [(m,"manuscript"),(cl,"cover")]:
    for x in forbidden:
        if x.lower() in surface.lower():
            raise SystemExit(f"{name} overclaim: {x}")

print("RC8 scientific submission package QA PASS")
