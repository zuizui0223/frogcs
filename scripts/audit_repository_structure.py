#!/usr/bin/env python3
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]

required = [
    root / "MANUSCRIPT_JAE_V1_3.md",
    root / "SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",
    root / "JAE_TITLE_PAGE_V0_8.template.md",
    root / "submission" / "COVER_LETTER_JAE_V0_13.md",
    root / "submission" / "NOVELTY_AUDIT_V0_11.md",
    root / "submission" / "REVIEWER_ATTACK_MATRIX_V0_11.md",
    root / "submission" / "JAE_PORTAL_CHECKLIST_V0_10.md",
    root / "submission" / "SUBMISSION_HANDOFF_RC11.md",
    root / "submission" / "HUMAN_FINALIZATION_RC11.md",
    root / "submission" / "RC11_STORY_FREEZE_V0_1.json",
    root / "scripts" / "audit_rc11_submission_package.py",
    root / "scripts" / "audit_jae_initial_submission_rc11_2026.py",
    root / ".github" / "workflows" / "submission_anonymous_docx.yml",
    root / ".github" / "workflows" / "initial_submission_bundle.yml",
    root / ".github" / "workflows" / "jae_initial_submission_compliance.yml",
    root / ".github" / "workflows" / "submission_package_qa.yml",
    root / ".github" / "workflows" / "scientific_submission_bundle.yml",
]
for p in required:
    assert p.exists(), f"missing current authority file: {p.relative_to(root)}"

assert [p.name for p in root.glob("MANUSCRIPT_JAE_*.md")] == ["MANUSCRIPT_JAE_V1_3.md"]
assert [p.name for p in root.glob("SUPPORTING_INFORMATION_JAE_*.md")] == ["SUPPORTING_INFORMATION_JAE_RC11_V0_1.md"]
assert [p.name for p in root.glob("JAE_TITLE_PAGE_*.template.md")] == ["JAE_TITLE_PAGE_V0_8.template.md"]

archive = root / "archive"
for name in [
    "manuscripts", "supporting_information", "title_pages",
    "submission_history", "workflows", "scripts", "figures_history"
]:
    assert (archive / name).exists(), f"missing archive section: {name}"

# Current submission surfaces should be singular, not a stack of historical versions.
submission = root / "submission"
expected_singular = {
    "COVER_LETTER_JAE_": "COVER_LETTER_JAE_V0_13.md",
    "JAE_PORTAL_CHECKLIST_": "JAE_PORTAL_CHECKLIST_V0_10.md",
    "NOVELTY_AUDIT_": "NOVELTY_AUDIT_V0_11.md",
    "REVIEWER_ATTACK_MATRIX_": "REVIEWER_ATTACK_MATRIX_V0_11.md",
    "SUBMISSION_HANDOFF_": "SUBMISSION_HANDOFF_RC11.md",
    "HUMAN_FINALIZATION_": "HUMAN_FINALIZATION_RC11.md",
}
for prefix, expected in expected_singular.items():
    got = sorted(p.name for p in submission.iterdir() if p.is_file() and p.name.startswith(prefix))
    assert got == [expected], (prefix, got)

retired_workflows = {
    "anonymous_docx.yml", "anonymous_docx_v0_8.yml", "anonymous_docx_v0_9.yml",
    "anonymous_docx_v1_0.yml", "anonymous_docx_v1_1.yml", "anonymous_docx_v1_2.yml",
    "initial_submission_bundle.yml", "initial_submission_bundle_rc6.yml",
    "final_submission_bundle.yml", "final_submission_bundle_rc6.yml",
    "rc10_candidate_qa.yml", "rc10_submission_package_qa.yml",
    "rc6_submission_package_qa.yml", "rc7_submission_package_qa.yml",
    "rc8_submission_package_qa.yml", "rc9_submission_package_qa.yml",
    "submission_qa.yml", "revision_manuscript_qa.yml",
}
active_workflows = root / ".github" / "workflows"
active_names = {p.name for p in active_workflows.glob("*.yml")}
assert not (retired_workflows & active_names), sorted(retired_workflows & active_names)

# Active workflows must not depend on paths that were archived.
archived_dependency_names = set()
for d in [
    archive / "manuscripts",
    archive / "supporting_information",
    archive / "title_pages",
    archive / "scripts",
    archive / "submission_history",
]:
    archived_dependency_names.update(p.name for p in d.iterdir() if p.is_file())

bad_refs = {}
for wf in active_workflows.glob("*.yml"):
    text = wf.read_text(encoding="utf-8")
    hits = sorted(name for name in archived_dependency_names if name in text)
    if hits:
        bad_refs[wf.name] = hits
assert not bad_refs, bad_refs

# Superseded figure trees should not remain at repository root.
for name in ["figures", "figures_ecology_v0_5", "figures_ecology_v0_6", "figures_ecology_v0_8"]:
    assert not (root / name).exists(), name
for name in ["figures_ecology_v1_0", "figures_ecology_v1_2"]:
    assert (root / name).is_dir(), name

report = {
    "status": "PASS",
    "root_manuscripts": len(list(root.glob("MANUSCRIPT_JAE_*.md"))),
    "root_supporting_information": len(list(root.glob("SUPPORTING_INFORMATION_JAE_*.md"))),
    "root_title_pages": len(list(root.glob("JAE_TITLE_PAGE_*.template.md"))),
    "active_workflows": len(list(active_workflows.glob("*.yml"))),
    "active_scripts": len(list((root / "scripts").glob("*.py"))),
    "current_submission_files": len([p for p in submission.iterdir() if p.is_file()]),
    "archived_manuscripts": len(list((archive / "manuscripts").iterdir())),
    "archived_submission_files": len(list((archive / "submission_history").iterdir())),
    "archived_workflows": len(list((archive / "workflows").iterdir())),
    "archived_scripts": len(list((archive / "scripts").iterdir())),
}
print(json.dumps(report, indent=2, sort_keys=True))
