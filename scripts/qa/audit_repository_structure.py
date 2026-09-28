#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

CURRENT_ROOT_FILES = {
    "README.md",
    "MANUSCRIPT_JAE_V1_3.md",
    "SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",
    "JAE_TITLE_PAGE_V0_8.template.md",
}
CURRENT_ROOT_DIRS = {
    ".github", "archive", "figures_ecology_v1_0", "figures_ecology_v1_2",
    "provenance", "scripts", "submission",
}
CURRENT_SUBMISSION_FILES = {
    "CITATION.cff.template",
    "COVER_LETTER_JAE_V0_13.md",
    "HUMAN_FINALIZATION_RC11.md",
    "JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md",
    "JAE_PORTAL_CHECKLIST_V0_10.md",
    "NOVELTY_AUDIT_V0_11.md",
    "PRIVATE_METADATA_SETUP.md",
    "REVIEWER_ATTACK_MATRIX_V0_11.md",
    "SUBMISSION_HANDOFF_RC11.md",
    "SUBMISSION_METADATA_TEMPLATE_V0_7.yml",
    "ZENODO_METADATA_TEMPLATE.json",
}
SCRIPT_LAYOUT = {"naamp": 46, "frogid": 7, "qa": 11, "submission": 5}
TITLE = "Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"

root_files={p.name for p in ROOT.iterdir() if p.is_file()}
root_dirs={p.name for p in ROOT.iterdir() if p.is_dir() and p.name != ".git"}
assert root_files == CURRENT_ROOT_FILES, {"unexpected_root_files": sorted(root_files-CURRENT_ROOT_FILES), "missing": sorted(CURRENT_ROOT_FILES-root_files)}
assert root_dirs == CURRENT_ROOT_DIRS, {"unexpected_root_dirs": sorted(root_dirs-CURRENT_ROOT_DIRS), "missing": sorted(CURRENT_ROOT_DIRS-root_dirs)}

submission=ROOT/"submission"
submission_files={p.name for p in submission.iterdir() if p.is_file()}
assert submission_files == CURRENT_SUBMISSION_FILES, {
    "unexpected_submission_files": sorted(submission_files-CURRENT_SUBMISSION_FILES),
    "missing": sorted(CURRENT_SUBMISSION_FILES-submission_files),
}

scripts=ROOT/"scripts"
assert not list(scripts.glob("*.py")), [p.name for p in scripts.glob("*.py")]
script_dirs={p.name for p in scripts.iterdir() if p.is_dir()}
assert script_dirs == set(SCRIPT_LAYOUT), script_dirs
for name, expected in SCRIPT_LAYOUT.items():
    got=len(list((scripts/name).glob("*.py")))
    assert got == expected, (name, got, expected)

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
    ROOT/"scripts/submission/build_jae_anonymous_docx.py",
    ROOT/".github/workflows/submission_anonymous_docx.yml",
    ROOT/".github/workflows/initial_submission_bundle.yml",
    ROOT/".github/workflows/jae_initial_submission_compliance.yml",
    ROOT/".github/workflows/submission_package_qa.yml",
    ROOT/".github/workflows/scientific_submission_bundle.yml",
]
for p in required:
    assert p.exists(), f"missing current authority file: {p.relative_to(ROOT)}"

archive=ROOT/"archive"
for name in [
    "manuscripts","supporting_information","title_pages","submission_history",
    "workflows","scripts","figures_history","research_notes",
]:
    assert (archive/name).exists(), f"missing archive section: {name}"

prov=ROOT/"provenance"
for name in ["contracts","summaries","receipts","repairs","metadata","submission","docs"]:
    assert (prov/name).is_dir(), f"missing provenance section: {name}"
assert not list(ROOT.glob("*.json"))

root_manifest=json.loads((prov/"ROOT_JSON_MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))
assert root_manifest["moved_json_files"] == 141
assert sum(root_manifest["categories"].values()) == 141
submission_manifest=json.loads((prov/"submission/SUBMISSION_JSON_MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))
script_manifest=json.loads((prov/"SCRIPT_LAYOUT_MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))
assert script_manifest["moved_scripts"] == 69
assert script_manifest["categories"] == SCRIPT_LAYOUT

# Current templates must all describe the current paper.
citation=(submission/"CITATION.cff.template").read_text(encoding="utf-8")
meta=(submission/"SUBMISSION_METADATA_TEMPLATE_V0_7.yml").read_text(encoding="utf-8")
zenodo=json.loads((submission/"ZENODO_METADATA_TEMPLATE.json").read_text(encoding="utf-8"))
private=(submission/"PRIVATE_METADATA_SETUP.md").read_text(encoding="utf-8")
assert TITLE in citation and TITLE in meta and zenodo["title"] == TITLE
assert "SUBMISSION_METADATA_TEMPLATE_V0_7.yml" in private
for phrase in [
    "Recent rainfall predicts week-long richness elevation",
    "species-selective reassembly",
    "SUBMISSION_METADATA_TEMPLATE_V0_2.yml",
]:
    for p in submission.iterdir():
        if not p.is_file():
            continue
        try:
            text=p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        assert phrase not in text, (p.name, phrase)

# Current workflows may not depend on anything archived.
active_workflows=ROOT/".github/workflows"
archived_names={p.name for p in archive.rglob("*") if p.is_file()}
bad_archive_refs={}
for wf in active_workflows.glob("*.yml"):
    text=wf.read_text(encoding="utf-8")
    hits=sorted(name for name in archived_names if name in text)
    if hits:
        bad_archive_refs[wf.name]=hits
assert not bad_archive_refs, bad_archive_refs

# Fail on stale pre-migration paths.
mappings={}
mappings.update(root_manifest["mapping"])
mappings.update(submission_manifest["mapping"])
mappings.update(script_manifest["mapping"])
stale={}
scan_roots=[ROOT/"scripts", ROOT/".github/workflows", ROOT/"submission", ROOT/"README.md"]
for base in scan_roots:
    paths=[base] if base.is_file() else list(base.rglob("*"))
    for p in paths:
        if not p.is_file() or p.suffix.lower() not in {".py",".yml",".yaml",".md",".json",".txt",".cff"}:
            continue
        text=p.read_text(encoding="utf-8")
        bad=[old for old,target in mappings.items() if old in text and target not in text]
        if bad:
            stale[str(p.relative_to(ROOT))]=sorted(bad)
assert not stale, stale

# Superseded figure trees may not reappear at root.
for name in ["figures","figures_ecology_v0_5","figures_ecology_v0_6","figures_ecology_v0_8"]:
    assert not (ROOT/name).exists(), name

report={
    "status":"PASS",
    "root_files":len(root_files),
    "root_json_files":len(list(ROOT.glob("*.json"))),
    "submission_files":len(submission_files),
    "active_workflows":len(list(active_workflows.glob("*.yml"))),
    "active_scripts_recursive":len(list(scripts.rglob("*.py"))),
    "script_layout":SCRIPT_LAYOUT,
    "provenance_json_files":len(list(prov.rglob("*.json"))),
    "archived_files":len([p for p in archive.rglob("*") if p.is_file()]),
}
print(json.dumps(report,indent=2,sort_keys=True))
