#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
receipt=json.loads((ROOT/"REVISION_FIGURE_HASHES_V0_1.json").read_text(encoding="utf-8"))
bad=[]
for rel,expected in receipt["figures"].items():
    p=ROOT/rel
    if not p.is_file():
        bad.append({"path":rel,"error":"missing"})
        continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=expected:
        bad.append({"path":rel,"expected":expected,"got":got})
if bad:
    raise SystemExit("figure hash mismatch: "+json.dumps(bad,sort_keys=True))
print({"figures_verified":len(receipt["figures"]),"status":"PASS"})
