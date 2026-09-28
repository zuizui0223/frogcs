#!/usr/bin/env python3
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_0.md").read_text(encoding="utf-8")

required=[
  "**Q1: Does recent-rain activity expand the realized community along both spatial and taxonomic axes?**",
  "**Q2: Is the resulting matrix geometry distinguishable from simple uniform amplification?**",
  "**Q3: Does expansion materially erode local compositional differentiation?**",
  "This was the central structural test",
  "**First, recent-rain conditions expanded the behaviourally realized community along both axes:**",
  "**Second, that expansion was not reproduced by uniform amplification.**",
  "**Third, expansion did not require practical homogenization.**",
  "**community amplification** and **community recruitment**",
  "**selective recruitment into the realized community without practical homogenization**"
]
for x in required:
    if x not in m:
        raise SystemExit(f"RC8 hypothesis spine missing: {x}")

for x in [
  "rainfall caused the expansion",
  "uniform activation proves",
  "heterogeneous activation thresholds are proven",
  "rainfall causality"
]:
    if x.lower() in m.lower():
        raise SystemExit(f"RC8 hypothesis spine overclaim: {x}")

abstract=re.search(r"## Abstract\s*(.*?)\n## Keywords",m,re.S)
assert abstract
word_re=re.compile(r"\b[\wÀ-ÖØ-öø-ÿĀ-ž’'–—+./×βρκΔ≥≤%-]+\b",re.UNICODE)
wc=lambda s:len(word_re.findall(s))
assert wc(abstract.group(1)) <= 350
assert wc(m) < 8400
assert "80.9% boundary crossing" in m
assert "92.0% observed" in m
assert "8.0% observed versus 19.1% expected" in m
assert "±0.025" in m
assert "activation geometry is not interpreted as a rainfall-specific response trait" in m

print({
  "status":"PASS",
  "manuscript_words":wc(m),
  "abstract_words":wc(abstract.group(1))
})
