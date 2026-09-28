#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")

required=[
  "A proximal hydric route is also biologically plausible",
  "Tracy et al., 2014; Lemenager et al., 2022",
  "Hydration is one candidate proximal route within this interpretation, not a mediator identified by the present analysis.",
  "https://doi.org/10.1086/674537",
  "https://doi.org/10.1002/ece3.8597",
  "92.0% crossed at least one spatial or taxonomic matrix boundary",
  "all three coefficients retained positive 95% confidence intervals when any one of the 21 states was omitted",
  "NAAMP sampling was not exposure-randomized",
  "DaysSinceRain therefore reflects both weather history and programme scheduling"
]
for x in required:
    if x not in m:
        raise SystemExit(f"missing RC7 hydric-context anchor: {x}")

forbidden=[
  "hydration mediated the expansion",
  "hydration causes the expansion",
  "rainfall caused the expansion"
]
for x in forbidden:
    if x.lower() in m.lower():
        raise SystemExit(f"mechanistic overclaim: {x}")

print("RC7 hydric mechanistic-context QA: PASS")
