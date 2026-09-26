#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_TITLE="Rainfall-associated expansion of frog active communities has repeatable species-specific spatial geometry"
OLD_TITLE="Recent rainfall predicts week-long richness elevation and species-selective reassembly in active frog communities"

required=[
    "MANUSCRIPT_JAE_V0_8.md",
    "ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json",
    "COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md",
    "NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json",
    "NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_SUMMARY_V0_1.json",
    "NAAMP_SPECIES_STOP_QUADRANTS_SUMMARY_V0_1.json",
    "NAAMP_WITHIN_ACTIVE_DEPTH_SUMMARY_V0_1.json",
    "NAAMP_FUNCTIONAL_COMMUNITY_EXPANSION_SUMMARY_V0_1.json",
    "NAAMP_FUNCTIONAL_RESPONSE_DECOUPLING_SUMMARY_V0_1.json",
    "NAAMP_RESPONSE_DIVERSITY_BUFFERING_SUMMARY_V0_1.json",
    "NAAMP_DETECTION_QUALITY_ROBUSTNESS_SUMMARY_V0_1.json",
    "NAAMP_MATRIX_DENSITY_INVARIANCE_SUMMARY_V0_1.json",
    "NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_SUMMARY_V0_1.json",
    "NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_SUMMARY_V0_1.json",
    "SPECIES_RESPONSE_TRAIT_FRAMEWORK_V0_1.md",
    "SUPPORTING_INFORMATION_JAE_RC6_V0_1.md",
    "ECOLOGICAL_FIGURE_HASHES_V0_3.json",
    "JAE_TITLE_PAGE_V0_5.template.md",
    "submission/COVER_LETTER_JAE_V0_6.md",
    "submission/JAE_PORTAL_CHECKLIST_V0_5.md",
    "submission/SUBMISSION_HANDOFF_RC6.md",
    "submission/SUBMISSION_METADATA_TEMPLATE_V0_3.yml",
    "submission/CITATION_V0_2.cff.template",
]
for rel in required:
    if not (ROOT/rel).is_file():
        raise SystemExit(f"missing RC6 file: {rel}")

surfaces=[
    "MANUSCRIPT_JAE_V0_8.md",
    "JAE_TITLE_PAGE_V0_5.template.md",
    "submission/COVER_LETTER_JAE_V0_6.md",
    "submission/JAE_PORTAL_CHECKLIST_V0_5.md",
    "submission/SUBMISSION_HANDOFF_RC6.md",
    "submission/SUBMISSION_METADATA_TEMPLATE_V0_3.yml",
    "submission/CITATION_V0_2.cff.template",
]
for rel in surfaces:
    text=(ROOT/rel).read_text(encoding="utf-8")
    if EXPECTED_TITLE not in text:
        raise SystemExit(f"current title missing from {rel}")
    if OLD_TITLE in text:
        raise SystemExit(f"superseded RC5 title leaked into {rel}")

claim=json.loads((ROOT/"ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json").read_text(encoding="utf-8"))
if claim.get("working_title")!=EXPECTED_TITLE:
    raise SystemExit("claim-boundary title drift")

subprocess.run(
    [sys.executable,str(ROOT/"scripts/audit_jae_v0_8_metacommunity.py"),
     "--manuscript",str(ROOT/"MANUSCRIPT_JAE_V0_8.md")],
    check=True
)
subprocess.run(
    [sys.executable,str(ROOT/"scripts/verify_metacommunity_figure_hashes_v0_3.py")],
    check=True
)

print("RC6 scientific submission package QA PASS")
