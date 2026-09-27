#!/usr/bin/env python3
from pathlib import Path
import json, sys

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC7_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_7.md").read_text(encoding="utf-8")
s=json.loads((root/"NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_SUMMARY_V0_1.json").read_text(encoding="utf-8"))

assert s["decision"]["pass"] is True
assert s["decision"]["strong_pass"] is True
assert s["n_pairs"]==4236 and s["n_routes"]==585 and s["n_states"]==21

required=[
 "all three coefficients retained positive 95% confidence intervals when any one of the 21 states was omitted",
 "The multiscale expansion signal is not driven by any single state",
 "0.346 to 0.433",
 "0.0496 to 0.0955",
 "0.218 to 0.329",
 "broad geographic robustness of the pooled expansion signal with genuine local heterogeneity",
 "plausible activation-threshold interpretation",
 "not a causal pathway identified by the present observational analysis",
 "Oseen, K. L., & Wassersug, R. J. (2002)",
 "Saenz, D., Fitzgerald, L. A., Baum, K. A., & Conner, R. N. (2006)"
]
for x in required:
    if x not in m: raise SystemExit(f"missing manuscript requirement: {x}")

for x in ["strong PASS","Vermont","Massachusetts","route-gamma random-slope model did not converge"]:
    if x not in si: raise SystemExit(f"missing SI requirement: {x}")

for x in ["every one of 21 leave-one-state-out refits","State-specific slopes remained heterogeneous"]:
    if x not in cl: raise SystemExit(f"missing cover-letter requirement: {x}")

forbidden=[
 "the effect occurs in every state",
 "the rainfall association is positive in every state",
 "continental universality"
]
for x in forbidden:
    if x.lower() in m.lower(): raise SystemExit(f"forbidden overclaim in manuscript: {x}")

assert "92.0% crossed at least one spatial or taxonomic matrix boundary" in m
assert "only 8.0% was rearrangement within the existing active core" in m
assert "species-level mechanism remains unresolved" in m.lower()
print("RC7 geographic-generality scientific package QA: PASS")
