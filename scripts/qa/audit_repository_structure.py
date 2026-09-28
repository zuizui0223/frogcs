#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]
TITLE="Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"

CURRENT_ROOT_FILES={
    "README.md","MANUSCRIPT_JAE_V1_3.md",
    "SUPPORTING_INFORMATION_JAE_RC11_V0_1.md","JAE_TITLE_PAGE_V0_8.template.md",
}
CURRENT_ROOT_DIRS={
    ".github","figures_ecology_v1_0","figures_ecology_v1_2",
    "provenance","scripts","submission",
}
CURRENT_SUBMISSION_FILES={
    "CITATION.cff.template",
    "COVER_LETTER_JAE_V0_13.md",
    "SUBMISSION_METADATA_TEMPLATE_V0_7.yml",
}
SCRIPT_LAYOUT={"naamp":11,"frogid":1,"qa":4,"submission":2}
CURRENT_WORKFLOWS={
    "reproduce_current_results.yml",
    "submission_pipeline.yml",
}

root_files={p.name for p in ROOT.iterdir() if p.is_file()}
root_dirs={p.name for p in ROOT.iterdir() if p.is_dir() and p.name!=".git"}
assert root_files==CURRENT_ROOT_FILES, {
    "unexpected_root_files":sorted(root_files-CURRENT_ROOT_FILES),
    "missing_root_files":sorted(CURRENT_ROOT_FILES-root_files),
}
assert root_dirs==CURRENT_ROOT_DIRS, {
    "unexpected_root_dirs":sorted(root_dirs-CURRENT_ROOT_DIRS),
    "missing_root_dirs":sorted(CURRENT_ROOT_DIRS-root_dirs),
}
assert not list(ROOT.glob("*.json"))

submission=ROOT/"submission"
submission_files={p.name for p in submission.iterdir() if p.is_file()}
assert submission_files==CURRENT_SUBMISSION_FILES, {
    "unexpected_submission_files":sorted(submission_files-CURRENT_SUBMISSION_FILES),
    "missing_submission_files":sorted(CURRENT_SUBMISSION_FILES-submission_files),
}

scripts=ROOT/"scripts"
assert not list(scripts.glob("*.py")), [p.name for p in scripts.glob("*.py")]
script_dirs={p.name for p in scripts.iterdir() if p.is_dir()}
assert script_dirs==set(SCRIPT_LAYOUT), script_dirs
for name,expected in SCRIPT_LAYOUT.items():
    got=len(list((scripts/name).glob("*.py")))
    assert got==expected,(name,got,expected)

active_workflows=ROOT/".github/workflows"
active_names={p.name for p in active_workflows.glob("*.yml")}
assert active_names==CURRENT_WORKFLOWS, {
    "unexpected_workflows":sorted(active_names-CURRENT_WORKFLOWS),
    "missing_workflows":sorted(CURRENT_WORKFLOWS-active_names),
}

required=[
    ROOT/"MANUSCRIPT_JAE_V1_3.md",
    ROOT/"SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",
    ROOT/"JAE_TITLE_PAGE_V0_8.template.md",
    submission/"COVER_LETTER_JAE_V0_13.md",
    submission/"CITATION.cff.template",
    submission/"SUBMISSION_METADATA_TEMPLATE_V0_7.yml",
    ROOT/"provenance/submission/RC11_STORY_FREEZE_V0_1.json",
    ROOT/"scripts/qa/audit_rc11_submission_package.py",
    ROOT/"scripts/qa/audit_jae_initial_submission_rc11_2026.py",
    ROOT/"scripts/qa/audit_repository_structure.py",
    ROOT/"scripts/qa/audit_naamp_sciencebase_file_manifest.py",
    ROOT/"scripts/submission/build_jae_anonymous_docx.py",
    ROOT/"scripts/submission/render_submission_metadata.py",
]
for p in required:
    assert p.exists(),f"missing current file: {p.relative_to(ROOT)}"

prov=ROOT/"provenance"
CURRENT_PROVENANCE_FILES={
    "contracts/CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json",
    "contracts/FROGID_TIMEZONE_REPAIR_CONTRACT_V0_1.json",
    "contracts/NAAMP_DETECTION_QUALITY_ROBUSTNESS_CONTRACT_V0_1.json",
    "contracts/NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1.json",
    "contracts/NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1.json",
    "contracts/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1.json",
    "contracts/NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json",
    "contracts/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1.json",
    "contracts/NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json",
    "contracts/NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1.json",
    "contracts/NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_CONTRACT_V0_1.json",
    "contracts/NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json",
    "contracts/NAAMP_WITHIN_ACTIVE_DEPTH_CONTRACT_V0_1.json",
    "repairs/NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json",
    "receipts/README.md",
    "submission/RC10_SCOPE_UNFREEZE_V0_1.json",
    "submission/RC10_STORY_DECISION_TREE_V0_1.json",
    "submission/RC11_STORY_FREEZE_V0_1.json",
    "submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json",
    "summaries/CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json",
    "summaries/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json",
    "summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json",
    "summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json",
    "summaries/NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json",
    "summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json",
}
prov_files={p.relative_to(prov).as_posix() for p in prov.rglob("*") if p.is_file()}
assert prov_files==CURRENT_PROVENANCE_FILES, {
    "unexpected_provenance_files":sorted(prov_files-CURRENT_PROVENANCE_FILES),
    "missing_provenance_files":sorted(CURRENT_PROVENANCE_FILES-prov_files),
}

# Current templates must describe the current paper and contain no superseded story.
citation=(submission/"CITATION.cff.template").read_text(encoding="utf-8")
meta=(submission/"SUBMISSION_METADATA_TEMPLATE_V0_7.yml").read_text(encoding="utf-8")
assert TITLE in citation and TITLE in meta
for phrase in [
    "Recent rainfall predicts week-long richness elevation",
    "species-selective reassembly",
    "SUBMISSION_METADATA_TEMPLATE_V0_2.yml",
]:
    for p in submission.iterdir():
        if not p.is_file():
            continue
        try:text=p.read_text(encoding="utf-8")
        except UnicodeDecodeError:continue
        assert phrase not in text,(p.name,phrase)

# Active surfaces must use categorized script/provenance paths rather than historical flat paths.
legacy={}
legacy_patterns=[
    re.compile(r'(?<![A-Za-z0-9_./-])scripts/(?:run_|audit_|build_|render_|finalize_)[A-Za-z0-9_.-]+\\.py'),
    re.compile(r'(?<![A-Za-z0-9_./-])submission/RC[0-9][A-Za-z0-9_.-]*\\.json'),
]
for base in [scripts,active_workflows,submission,ROOT/"README.md"]:
    paths=[base] if base.is_file() else list(base.rglob("*"))
    for p in paths:
        if not p.is_file() or p.suffix.lower() not in {".py",".yml",".yaml",".md",".json",".txt",".cff"}:
            continue
        text=p.read_text(encoding="utf-8")
        hits=sorted({m.group(0) for pat in legacy_patterns for m in pat.finditer(text)})
        if hits:legacy[str(p.relative_to(ROOT))]=hits
assert not legacy,legacy

# Active workflow file references must resolve to live paths.
missing_refs={}
for wf in active_workflows.glob("*.yml"):
    text=wf.read_text(encoding="utf-8")
    refs=set()
    refs.update(re.findall(r'(scripts/[A-Za-z0-9_./-]+\.py)',text))
    refs.update(re.findall(r'(provenance/[A-Za-z0-9_./-]+\.json)',text))
    refs.update(re.findall(r'(figures_ecology_v[0-9_]+/[A-Za-z0-9_./-]+\.svg)',text))
    bad=sorted(
        ref for ref in refs
        if "/receipts/" not in ref and not (ROOT/ref).exists()
    )
    if bad:missing_refs[wf.name]=bad
assert not missing_refs,missing_refs

# Active code/workflows may not use bare uppercase JSON paths (repo-root provenance).
pat=re.compile(r'(?<![/A-Za-z0-9_.-])([A-Z][A-Z0-9_]*(?:CONTRACT|SUMMARY|RECEIPT|REPAIR)[A-Z0-9_]*\.json)')
bare={}
for base in [scripts,active_workflows]:
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".py",".yml",".yaml"}:
            continue
        hits=sorted(set(pat.findall(p.read_text(encoding="utf-8"))))
        if hits:bare[str(p.relative_to(ROOT))]=hits
assert not bare,bare

for name in ["figures","figures_ecology_v0_5","figures_ecology_v0_6","figures_ecology_v0_8"]:
    assert not (ROOT/name).exists(),name

report={
    "status":"PASS",
    "root_files":len(root_files),
    "root_json_files":0,
    "submission_files":len(submission_files),
    "active_workflows":len(active_names),
    "active_scripts_recursive":len(list(scripts.rglob("*.py"))),
    "script_layout":SCRIPT_LAYOUT,
    "provenance_json_files":len(list(prov.rglob("*.json"))),
}
print(json.dumps(report,indent=2,sort_keys=True))
