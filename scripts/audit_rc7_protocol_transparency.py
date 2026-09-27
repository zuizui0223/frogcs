#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")
r=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_5.md").read_text(encoding="utf-8")

required=[
  "NAAMP sampling was not exposure-randomized",
  "routes in those regions were intended to be surveyed within three days of rain",
  "DaysSinceRain therefore reflects both weather history and programme scheduling",
  "do not remove time-varying confounding or protocol-based selection",
  "Royle & Link, 2005",
  "U.S. Geological Survey. (2016). *North American Amphibian Monitoring Program*",
  "plausible activation-threshold interpretation",
  "not a causal pathway identified by the present observational analysis"
]
for x in required:
    if x not in m:
        raise SystemExit(f"missing manuscript transparency anchor: {x}")

for x in [
  "Rain recency is partly protocol-conditioned",
  "leave-one-state-out audit shows no single state drives footprint, alpha or gamma",
  "neither step removes protocol selection or time-varying confounding"
]:
    if x not in r:
        raise SystemExit(f"missing reviewer-response anchor: {x}")

forbidden=[
  "rainfall causes the active community",
  "rainfall caused the active community",
  "causal rainfall effect"
]
for x in forbidden:
    if x.lower() in m.lower():
        raise SystemExit(f"causal overclaim: {x}")

assert "92.0% crossed at least one spatial or taxonomic matrix boundary" in m
assert "all three coefficients retained positive 95% confidence intervals when any one of the 21 states was omitted" in m
print("RC7 protocol-selection transparency QA: PASS")
