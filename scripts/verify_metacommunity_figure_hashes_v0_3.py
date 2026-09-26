#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/"ECOLOGICAL_FIGURE_HASHES_V0_3.json"
obj=json.loads(manifest.read_text(encoding="utf-8"))
figs=obj.get("figures") or {}
if len(figs)!=3:
    raise SystemExit(f"expected 3 frozen figures, found {len(figs)}")
for rel,expected in sorted(figs.items()):
    p=ROOT/rel
    if not p.is_file():
        raise SystemExit(f"missing figure: {rel}")
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=expected:
        raise SystemExit(f"figure hash mismatch {rel}: {got} != {expected}")
print("JAE v0.8 figure hashes PASS")
