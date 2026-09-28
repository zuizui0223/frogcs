#!/usr/bin/env python3
from pathlib import Path

root=Path(__file__).resolve().parents[1]
n=(root/"submission/NOVELTY_AUDIT_V0_6.md").read_text(encoding="utf-8")
r=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_6.md").read_text(encoding="utf-8")
c=(root/"submission/COVER_LETTER_JAE_V0_8.md").read_text(encoding="utf-8")
m=(root/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")

for x in [
    "Xie et al. (2017",
    "Sugai et al. (2021",
    "Sarker et al. (2022",
    "Zhang et al. (2014",
    "approximately **92% crosses at least one spatial and/or taxonomic matrix boundary**",
    "robust to omission of any single sampled state",
    "not confined to comparisons entirely within the 0–3 day protocol-target window",
    "Preferred one-sentence novelty statement"
]:
    if x not in n:
        raise SystemExit(f"novelty audit missing: {x}")

for x in [
    "Xie et al. (2017) already showed lagged rainfall associations",
    "Sarker et al. (2022) already showed inundation-driven richness",
    "Joint alpha–beta–gamma responses to precipitation are not new.",
    "The paper's novelty depends on a null beta-diversity result.",
    "The rainfall signal could still be created entirely by the programme's 0–3 day rain-target scheduling.",
    "Geographic heterogeneity undermines the broad claim."
]:
    if x not in r:
        raise SystemExit(f"reviewer matrix missing: {x}")

for x in [
    "We do not claim any of those phenomena as new.",
    "lagged rainfall associations with frog calling activity and observed species richness",
    "fine-temporal changes in calling-assemblage composition and beta diversity",
    "wetting/inundation-associated changes in frog richness, chorusing and community composition",
    "localization of that response within a fixed spatial incidence matrix"
]:
    if x not in c:
        raise SystemExit(f"cover letter missing: {x}")

forbidden=[
    "first evidence that rain",
    "first demonstration that rain",
    "first alpha–beta–gamma",
    "rainfall causes community expansion",
    "positive in every state",
    "continental universality"
]
# Novelty/reviewer audit files intentionally quote prohibited claims as risks/attacks.
# Enforce overclaim language only on the user-facing cover letter.
for x in forbidden:
    if x.lower() in c.lower():
        raise SystemExit(f"cover contains forbidden overclaim: {x}")

title="Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without detectable homogenization"
assert title in m and title in c
print("RC7 novelty-positioning QA: PASS")
