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
    ".github","archive","figures_ecology_v1_0","figures_ecology_v1_2",
    "provenance","scripts","submission",
}
CURRENT_SUBMISSION_FILES={
    "CITATION.cff.template","COVER_LETTER_JAE_V0_13.md",
    "HUMAN_FINALIZATION_RC11.md","JAE_PORTAL_CHECKLIST_V0_10.md",
    "PRIVATE_METADATA_SETUP.md","SUBMISSION_METADATA_TEMPLATE_V0_7.yml",
    "ZENODO_METADATA_TEMPLATE.json",
}
SCRIPT_LAYOUT={"naamp":11,"frogid":1,"qa":4,"submission":2}
CURRENT_WORKFLOWS={
    "crosscontinental_active_depth.yml","detection_quality_robustness.yml",
    "geographic_generality_audit.yml","initial_submission_bundle.yml",
    "jae_initial_submission_compliance.yml","metacommunity_alpha_beta_gamma.yml",
    "naamp_ecological_pulse.yml","naamp_source_manifest_audit.yml",
    "persistence_preserving_null.yml","protocol_window_sensitivity.yml",
    "repository_structure_qa.yml","same_observer_robustness.yml",
    "scientific_submission_bundle.yml","sorensen_equivalence.yml",
    "spatial_taxonomic_activation_decomposition.yml","submission_anonymous_docx.yml",
    "submission_package_qa.yml","uniform_activation_null.yml",
    "within_active_depth_decomposition.yml",
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
    ROOT/"provenance/submission_docs/JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md",
    ROOT/"provenance/submission_docs/NOVELTY_AUDIT_V0_11.md",
    ROOT/"provenance/submission_docs/REVIEWER_ATTACK_MATRIX_V0_11.md",
    ROOT/"provenance/submission_docs/SUBMISSION_HANDOFF_RC11.md",
    ROOT/"provenance/docs/CURRENT_PAPER_OVERVIEW.md",
    ROOT/"scripts/qa/audit_rc11_submission_package.py",
    ROOT/"scripts/qa/audit_jae_initial_submission_rc11_2026.py",
    ROOT/"scripts/qa/audit_repository_structure.py",
    ROOT/"scripts/qa/audit_naamp_sciencebase_file_manifest.py",
    ROOT/"scripts/submission/build_jae_anonymous_docx.py",
    ROOT/"scripts/submission/render_submission_metadata.py",
]
for p in required:
    assert p.exists(),f"missing current file: {p.relative_to(ROOT)}"

archive=ROOT/"archive"
for name in [
    "manuscripts","supporting_information","title_pages","submission_history",
    "workflows","scripts","figures_history","research_notes",
]:
    assert (archive/name).exists(),f"missing archive section: {name}"

prov=ROOT/"provenance"
for name in [
    "contracts","summaries","receipts","repairs","metadata","submission",
    "submission_docs","docs",
]:
    assert (prov/name).is_dir(),f"missing provenance section: {name}"

root_manifest=json.loads((prov/"ROOT_JSON_MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))
submission_manifest=json.loads((prov/"submission/SUBMISSION_JSON_MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))
script_manifest=json.loads((prov/"SCRIPT_LAYOUT_MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))
assert root_manifest["moved_json_files"]==141
assert sum(root_manifest["categories"].values())==141
assert script_manifest["moved_scripts"]==69

# Current templates must describe the current paper and contain no superseded story.
citation=(submission/"CITATION.cff.template").read_text(encoding="utf-8")
meta=(submission/"SUBMISSION_METADATA_TEMPLATE_V0_7.yml").read_text(encoding="utf-8")
zenodo=json.loads((submission/"ZENODO_METADATA_TEMPLATE.json").read_text(encoding="utf-8"))
private=(submission/"PRIVATE_METADATA_SETUP.md").read_text(encoding="utf-8")
assert TITLE in citation and TITLE in meta and zenodo["title"]==TITLE
assert "SUBMISSION_METADATA_TEMPLATE_V0_7.yml" in private
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

# No active surface may retain a pre-migration path.
mappings={}
mappings.update(root_manifest["mapping"])
mappings.update(submission_manifest["mapping"])
mappings.update(script_manifest["mapping"])
stale={}
for base in [scripts,active_workflows,submission,ROOT/"README.md"]:
    paths=[base] if base.is_file() else list(base.rglob("*"))
    for p in paths:
        if not p.is_file() or p.suffix.lower() not in {".py",".yml",".yaml",".md",".json",".txt",".cff"}:
            continue
        text=p.read_text(encoding="utf-8")
        bad=[old for old,target in mappings.items() if old in text and target not in text]
        if bad:stale[str(p.relative_to(ROOT))]=sorted(bad)
assert not stale,stale

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
    "archived_files":len([p for p in archive.rglob("*") if p.is_file()]),
}
print(json.dumps(report,indent=2,sort_keys=True))
