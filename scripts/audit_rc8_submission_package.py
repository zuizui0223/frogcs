#!/usr/bin/env python3
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_0.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC8_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_9.md").read_text(encoding="utf-8")
nov=(root/"submission/NOVELTY_AUDIT_V0_7.md").read_text(encoding="utf-8")
rev=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_7.md").read_text(encoding="utf-8")
null=json.loads((root/"NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
eq=json.loads((root/"NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
tree=json.loads((root/"submission/RC8_STORY_DECISION_TREE_V0_1.json").read_text(encoding="utf-8"))
scope=json.loads((root/"submission/RC8_SCOPE_UNFREEZE_V0_1.json").read_text(encoding="utf-8"))

title="Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization"
assert m.startswith("# "+title)
assert title in cl
assert null["decision"]=="strong_rejection_of_uniform_activation"
assert null["primary_omnibus"]["monte_carlo_p"] < 0.05
assert eq["decision"]["title_level_equivalence_support"] is True
assert tree["status"]=="frozen_before_uniform_null_readback"
assert scope["status"]=="author_directed_inferential_repair"

for x in [
  "80.9% boundary crossing",
  "95% null interval 74.2–87.4%",
  "92.0% observed",
  "Monte Carlo P = 0.001",
  "Within-core rearrangement was 8.0% observed versus 19.1% expected",
  "90% CI -0.0107 to 0.00968",
  "rejection of the uniform-activation null does not identify a unique species-level mechanism"
]:
    if x not in m:
        raise SystemExit(f"RC8 manuscript missing: {x}")

for x in [
  "| 2 | .000999 | 80.9% | 74.2–87.4% | 92.0% |",
  "The null was strongly rejected under all three specifications",
  "The equivalence claim applies only to the pairwise Sørensen",
  "implementation repairs were versioned before successful endpoint readback"
]:
    if x not in si:
        raise SystemExit(f"RC8 SI missing: {x}")

for x in [
  "predicted a mean boundary-crossing share of 80.9%",
  "four-component allocation rejected uniform activation",
  "without practical homogenization"
]:
    if x not in cl:
        raise SystemExit(f"RC8 cover missing: {x}")

for x in [
  "uniform increase in baseline acoustic propensities",
  "80.9%",
  "route-new taxonomic participation"
]:
    if x not in nov:
        raise SystemExit(f"RC8 novelty missing: {x}")

for x in [
  "A high 92% boundary-crossing share is exactly what uniform activation would produce.",
  "κ=1,2,5",
  "pairwise Sørensen slope"
]:
    if x not in rev:
        raise SystemExit(f"RC8 reviewer matrix missing: {x}")

fig=(root/"figures_ecology_v1_0/FIGURE_2_UNIFORM_NULL_COMPARISON_V0_1.svg").read_text(encoding="utf-8")
for x in ["Obs 36.9%","Null 27.4%","Obs 8.0%","Null 19.1%","Monte Carlo P = 0.001"]:
    if x not in fig:
        raise SystemExit(f"RC8 Figure 2 missing: {x}")

forbidden=[
  "rainfall caused the expansion",
  "uniform activation proves",
  "hydration mediated the expansion",
  "beta diversity is exactly unchanged"
]
for surface,name in [(m,"manuscript"),(cl,"cover")]:
    for x in forbidden:
        if x.lower() in surface.lower():
            raise SystemExit(f"{name} overclaim: {x}")

print("RC8 scientific submission package QA PASS")
