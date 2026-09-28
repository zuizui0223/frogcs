#!/usr/bin/env python3
from pathlib import Path
m=(Path(__file__).resolve().parents[1]/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")
required=[
  "retained positive 95% confidence intervals under every single-state omission",
  "remained confidence-interval positive when the drier survey occurred at least four days after rain",
  "92.0% crossed at least one spatial or taxonomic matrix boundary",
  "species-level mechanism remains unresolved"
]
for x in required:
    if x not in m: raise SystemExit(f"missing abstract/frozen anchor: {x}")
for x in ["rainfall caused","causal rainfall effect","positive in every state"]:
    if x.lower() in m.lower(): raise SystemExit(f"overclaim: {x}")
print("RC7 abstract robustness QA: PASS")
