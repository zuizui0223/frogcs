#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
audit_path=ROOT/"provenance/PROVENANCE_REACHABILITY_AUDIT.json"
audit=json.loads(audit_path.read_text(encoding="utf-8"))

assert audit["status"]=="PASS"
candidates=audit["candidates"]
keep=set(audit["keep"])
assert len(candidates)==150, len(candidates)
assert not (set(candidates)&keep)

deleted=[]
for rel in candidates:
    p=ROOT/rel
    if not p.is_file():
        raise SystemExit(f"candidate missing before prune: {rel}")
    p.unlink()
    deleted.append(rel)

# Remove empty provenance subdirectories, but preserve current top-level role dirs.
for p in sorted((ROOT/"provenance").rglob("*"),reverse=True):
    if p.is_dir():
        try:p.rmdir()
        except OSError:pass

remaining=[p.relative_to(ROOT).as_posix() for p in (ROOT/"provenance").rglob("*") if p.is_file()]
assert all(x in keep for x in remaining), sorted(set(remaining)-keep)
assert len(remaining)==len(keep), (len(remaining),len(keep))

print(json.dumps({
    "status":"PASS",
    "deleted":len(deleted),
    "remaining_provenance":len(remaining),
},indent=2))
