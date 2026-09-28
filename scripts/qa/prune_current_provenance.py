#!/usr/bin/env python3
from pathlib import Path
import json, re

ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/"provenance"

KEEP={
"provenance/README.md",
"provenance/docs/CURRENT_PAPER_OVERVIEW.md",
"provenance/contracts/CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json",
"provenance/contracts/FROGID_TIMEZONE_REPAIR_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_DETECTION_QUALITY_ROBUSTNESS_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json",
"provenance/contracts/NAAMP_WITHIN_ACTIVE_DEPTH_CONTRACT_V0_1.json",
"provenance/receipts/NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json",
"provenance/repairs/NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json",
"provenance/submission/RC10_SCOPE_UNFREEZE_V0_1.json",
"provenance/submission/RC10_STORY_DECISION_TREE_V0_1.json",
"provenance/submission/RC11_STORY_FREEZE_V0_1.json",
"provenance/submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json",
"provenance/submission_docs/JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md",
"provenance/submission_docs/NOVELTY_AUDIT_V0_11.md",
"provenance/submission_docs/REVIEWER_ATTACK_MATRIX_V0_11.md",
"provenance/submission_docs/SUBMISSION_HANDOFF_RC11.md",
"provenance/summaries/CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json",
"provenance/summaries/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json",
"provenance/summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json",
"provenance/summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json",
"provenance/summaries/NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json",
"provenance/summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json",
}
assert len(KEEP)==31

REF_RE=re.compile(r'(provenance/[A-Za-z0-9_./-]+\.(?:json|md|txt|ya?ml|cff))')
active=[]
for p in [ROOT/"README.md",ROOT/"MANUSCRIPT_JAE_V1_3.md",ROOT/"SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",ROOT/"JAE_TITLE_PAGE_V0_8.template.md"]:
    if p.exists():active.append(p)
for base in [ROOT/"scripts",ROOT/".github/workflows",ROOT/"submission"]:
    active.extend(p for p in base.rglob("*") if p.is_file())

refs=set()
for p in active:
    try:text=p.read_text(encoding="utf-8")
    except UnicodeDecodeError:continue
    refs.update(REF_RE.findall(text))
missing_from_keep=sorted(ref for ref in (refs-KEEP) if "/receipts/" not in ref)
assert not missing_from_keep, {"active_input_refs_not_kept":missing_from_keep}

all_files={p.relative_to(ROOT).as_posix() for p in PROV.rglob("*") if p.is_file()}
assert KEEP<=all_files, sorted(KEEP-all_files)
candidates=sorted(all_files-KEEP)
assert len(candidates)==150, len(candidates)

for rel in candidates:
    (ROOT/rel).unlink()

for p in sorted(PROV.rglob("*"),reverse=True):
    if p.is_dir():
        try:p.rmdir()
        except OSError:pass

remaining={p.relative_to(ROOT).as_posix() for p in PROV.rglob("*") if p.is_file()}
assert remaining==KEEP, {"missing":sorted(KEEP-remaining),"extra":sorted(remaining-KEEP)}

print(json.dumps({
    "status":"PASS",
    "active_provenance_refs":len(refs),
    "deleted":len(candidates),
    "remaining":len(remaining),
},indent=2))
