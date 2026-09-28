#!/usr/bin/env python3
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC7_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_7.md").read_text(encoding="utf-8")
s=json.loads((root/"NAAMP_PROTOCOL_WINDOW_SENSITIVITY_SUMMARY_V0_1.json").read_text(encoding="utf-8"))

assert s["decision"]["pass"] is True
assert s["decision"]["strong_pass"] is True
p=s["primary_crosses_three_day_window"]
assert p["n_pairs"]==1769 and p["n_routes"]==425 and p["n_states"]==20

for x in [
  "The headline expansion persists beyond the protocol-target three-day window",
  "1,769 comparisons from 425 routes in 20 states",
  "β = 0.374, 95% CI 0.198–0.551",
  "β = 0.0839, 0.0140–0.154",
  "β = 0.289, 0.133–0.446",
  "not confined to comparisons entirely inside the 0–3 day protocol-target window",
  "do not identify a randomized rainfall effect"
]:
    if x not in m: raise SystemExit(f"missing manuscript protocol-window anchor: {x}")

for x in [
  "The prespecified primary gate therefore achieved **strong PASS**",
  "Active stops | 1,769 | 425 | 0.374",
  "Local alpha | 1,729 | 419 | 0.0839",
  "Route gamma | 1,769 | 425 | 0.289",
  "All point estimates remained positive, but alpha and gamma were imprecise"
]:
    if x not in si: raise SystemExit(f"missing SI protocol-window anchor: {x}")

for x in [
  "retained 1,769 pairs whose drier survey occurred at least four days after rain",
  "rather than as causal evidence"
]:
    if x not in cl: raise SystemExit(f"missing cover-letter protocol-window anchor: {x}")

forbidden=[
  "protocol selection is eliminated",
  "rainfall causality is established",
  "proves persistence at long lags"
]
for x in forbidden:
    if x.lower() in m.lower() or x.lower() in si.lower():
        raise SystemExit(f"protocol-window overclaim: {x}")

assert "92.0% crossed at least one spatial or taxonomic matrix boundary" in m
assert "all three coefficients retained positive 95% confidence intervals when any one of the 21 states was omitted" in m
assert "Hydration is one candidate proximal route within this interpretation, not a mediator identified by the present analysis." in m
print("RC7 protocol-window integration QA: PASS")
