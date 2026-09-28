#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/"provenance"
REF=re.compile(r'(provenance/[A-Za-z0-9_./-]+\.(?:json|md|txt|ya?ml|cff))')

all_files={p.relative_to(ROOT).as_posix():p for p in PROV.rglob("*") if p.is_file()}

sources=[]
for p in [ROOT/"README.md",ROOT/"MANUSCRIPT_JAE_V1_3.md",ROOT/"SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",ROOT/"JAE_TITLE_PAGE_V0_8.template.md"]:
    sources.append(("surface",p))
for p in (ROOT/"scripts").rglob("*.py"):sources.append(("script",p))
for p in (ROOT/".github/workflows").glob("*.yml"):sources.append(("workflow",p))
for p in (ROOT/"submission").rglob("*"):
    if p.is_file():sources.append(("submission",p))

keep={"provenance/README.md","provenance/docs/CURRENT_PAPER_OVERVIEW.md"}
source_refs={}
for kind,p in sources:
    try:text=p.read_text(encoding="utf-8")
    except UnicodeDecodeError:continue
    refs={m.group(1) for m in REF.finditer(text)}
    refs={r for r in refs if r in all_files}
    # Receipt paths in workflows/scripts are generated outputs, not required checked-in inputs.
    if kind in {"workflow","script"}:
        refs={r for r in refs if not r.startswith("provenance/receipts/")}
    if refs:
        source_refs[p.relative_to(ROOT).as_posix()]=sorted(refs)
        keep|=refs

# Keep current submission provenance explicitly used to describe the frozen paper.
for rel in [
    "provenance/submission/RC11_STORY_FREEZE_V0_1.json",
    "provenance/submission_docs/JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md",
    "provenance/submission_docs/NOVELTY_AUDIT_V0_11.md",
    "provenance/submission_docs/REVIEWER_ATTACK_MATRIX_V0_11.md",
    "provenance/submission_docs/SUBMISSION_HANDOFF_RC11.md",
]:
    if rel in all_files:keep.add(rel)

# Migration/audit manifests are one-time history, not current scientific provenance.
for rel in list(keep):
    if rel.endswith("MIGRATION_MANIFEST.json") or rel.endswith("PROVENANCE_REACHABILITY_AUDIT.json"):
        keep.discard(rel)

candidates=sorted(set(all_files)-keep)
by_category={}
for rel in sorted(keep):
    key=rel.split("/")[1] if "/" in rel else "root"
    by_category[key]=by_category.get(key,0)+1
candidate_by_category={}
for rel in candidates:
    key=rel.split("/")[1]
    candidate_by_category[key]=candidate_by_category.get(key,0)+1

report={
 "status":"PASS",
 "total_provenance_files":len(all_files),
 "keep_count":len(keep),
 "candidate_count":len(candidates),
 "keep_by_category":by_category,
 "candidate_by_category":candidate_by_category,
 "keep":sorted(keep),
 "candidates":candidates,
 "source_references":source_refs,
}
(PROV/"CURRENT_PROVENANCE_PRUNE_PLAN.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in {"keep","candidates","source_references"}},indent=2))
