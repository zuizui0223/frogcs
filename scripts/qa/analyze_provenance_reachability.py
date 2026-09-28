#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROV=ROOT/"provenance"

REF_RE=re.compile(r'(provenance/[A-Za-z0-9_./-]+\.(?:json|md|txt|ya?ml|cff))')
TEXT_SUFFIX={".py",".yml",".yaml",".md",".json",".txt",".cff",".template"}

all_files=sorted(p for p in PROV.rglob("*") if p.is_file())
all_rel={p.relative_to(ROOT).as_posix():p for p in all_files}
by_name={}
for rel,p in all_rel.items():
    by_name.setdefault(p.name,[]).append(rel)

active_sources=[]
for p in [
    ROOT/"README.md", ROOT/"MANUSCRIPT_JAE_V1_3.md",
    ROOT/"SUPPORTING_INFORMATION_JAE_RC11_V0_1.md",
    ROOT/"JAE_TITLE_PAGE_V0_8.template.md",
]:
    if p.exists(): active_sources.append(p)
for base in [ROOT/"scripts",ROOT/".github/workflows",ROOT/"submission"]:
    active_sources += [p for p in base.rglob("*") if p.is_file()]

def read_text(p):
    try:return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError,OSError):return ""

def refs_from_text(text):
    out=set(m.group(1) for m in REF_RE.finditer(text))
    # Also resolve unique provenance basenames used without a path.
    for name,rels in by_name.items():
        if len(rels)==1 and name in text:
            out.add(rels[0])
    return {r for r in out if r in all_rel}

seed=set()
source_refs={}
for p in active_sources:
    text=read_text(p)
    refs=refs_from_text(text)
    if refs:
        source_refs[p.relative_to(ROOT).as_posix()]=sorted(refs)
        seed |= refs

# Human navigation files should remain even when no code points to them.
for rel in [
    "provenance/README.md",
    "provenance/docs/CURRENT_PAPER_OVERVIEW.md",
]:
    if rel in all_rel: seed.add(rel)

# Current-main policy: keep only provenance directly referenced by active
# scripts/workflows/submission surfaces plus the two human navigation files.
# References among provenance files are historical context, not a reason to
# duplicate their targets on the current branch; history branches retain them.
keep=set(seed)
candidates=sorted(set(all_rel)-keep)
edges={}

report={
    "status":"PASS",
    "total_provenance_files":len(all_rel),
    "seed_files":len(seed),
    "reachable_files":len(keep),
    "prune_candidates":len(candidates),
    "keep":sorted(keep),
    "candidates":candidates,
    "active_source_references":source_refs,
    "provenance_edges":edges,
}
out=PROV/"PROVENANCE_REACHABILITY_AUDIT.json"
out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({
    "status":"PASS",
    "total":len(all_rel),
    "seed":len(seed),
    "reachable":len(keep),
    "candidates":len(candidates),
},indent=2))
print("\nCANDIDATES")
for x in candidates:print(x)

# trigger provenance reachability audit
