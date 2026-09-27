#!/usr/bin/env python3
from pathlib import Path
import json, sys

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V0_9.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC7_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_8.md").read_text(encoding="utf-8")
s=json.loads((root/"NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
pw=json.loads((root/"NAAMP_PROTOCOL_WINDOW_SENSITIVITY_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
nov=(root/"submission/NOVELTY_AUDIT_V0_6.md").read_text(encoding="utf-8")
rev=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_6.md").read_text(encoding="utf-8")

assert s["decision"]["pass"] is True
assert s["decision"]["strong_pass"] is True
assert s["n_pairs"]==4236 and s["n_routes"]==585 and s["n_states"]==21
assert pw["decision"]["pass"] is True and pw["decision"]["strong_pass"] is True
assert pw["primary_crosses_three_day_window"]["n_pairs"]==1769
assert pw["primary_crosses_three_day_window"]["n_routes"]==425

required=[
 "all three coefficients retained positive 95% confidence intervals when any one of the 21 states was omitted",
 "The multiscale expansion signal is not driven by any single state",
 "0.346 to 0.433",
 "0.0496 to 0.0955",
 "0.218 to 0.329",
 "broad geographic robustness of the pooled expansion signal with genuine local heterogeneity",
 "plausible activation-threshold interpretation",
 "Hydration is one candidate proximal route within this interpretation, not a mediator identified by the present analysis.",
 "NAAMP sampling was not exposure-randomized",
 "DaysSinceRain therefore reflects both weather history and programme scheduling",
 "Tracy et al., 2014; Lemenager et al., 2022",
 "Oseen, K. L., & Wassersug, R. J. (2002)",
 "Saenz, D., Fitzgerald, L. A., Baum, K. A., & Conner, R. N. (2006)",
 "The headline expansion persists beyond the protocol-target three-day window",
 "1,769 comparisons from 425 routes in 20 states",
 "β = 0.374, 95% CI 0.198–0.551",
 "β = 0.0839, 0.0140–0.154",
 "β = 0.289, 0.133–0.446",
 "not confined to comparisons entirely inside the 0–3 day protocol-target window",
 "do not identify a randomized rainfall effect"
]
for x in required:
    if x not in m: raise SystemExit(f"missing manuscript requirement: {x}")

for x in ["strong PASS","Vermont","Massachusetts","route-gamma random-slope model did not converge","The prespecified primary gate therefore achieved **strong PASS**","Active stops | 1,769 | 425 | 0.374","All point estimates remained positive, but alpha and gamma were imprecise"]:
    if x not in si: raise SystemExit(f"missing SI requirement: {x}")

for x in ["We do not claim any of those phenomena as new.","localization of that response within a fixed spatial incidence matrix","every one of 21 leave-one-state-out refits","State-specific slopes remained heterogeneous","retained 1,769 pairs whose drier survey occurred at least four days after rain","rather than as causal evidence"]:
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

freeze=json.loads((root/"submission/RC7_STORY_FREEZE_V0_1.json").read_text(encoding="utf-8"))
assert freeze["status"]=="frozen_for_submission"
assert freeze["manuscript"]=="MANUSCRIPT_JAE_V0_9.md"
assert "single sampled state" in freeze["frozen_geographic_interpretation"]
assert "not a causal mechanism identified" in freeze["frozen_mechanistic_interpretation"]

handoff=(root/"submission/SUBMISSION_HANDOFF_RC7.md").read_text(encoding="utf-8")
for x in ["release/jae-v1-rc7","submission/jae-v1","RC7 story freeze","post-freeze mechanistic-context receipt","protocol-window sensitivity summary","Protocol-window robustness","NOVELTY_AUDIT_V0_6.md","REVIEWER_ATTACK_MATRIX_V0_6.md","COVER_LETTER_JAE_V0_8.md"]:
    if x not in handoff: raise SystemExit(f"RC7 handoff drift: {x}")


mech_receipt=json.loads((root/"submission/RC7_POSTFREEZE_MECHANISTIC_CONTEXT_RECEIPT_V0_1.json").read_text(encoding="utf-8"))
assert mech_receipt["scientific_unfreeze"] is False
assert "not identified as a mediator" in mech_receipt["explicit_boundary"]

pw_receipt=json.loads((root/"submission/RC7_POSTFREEZE_PROTOCOL_WINDOW_SENSITIVITY_RECEIPT_V0_1.json").read_text(encoding="utf-8"))
assert pw_receipt["scientific_unfreeze"] is False
assert pw_receipt["primary_result"]["decision"]=="strong_pass"
assert "not confined" in pw_receipt["authorized_interpretation"]

nov_receipt=json.loads((root/"submission/RC7_POSTFREEZE_NOVELTY_POSITIONING_RECEIPT_V0_1.json").read_text(encoding="utf-8"))
assert nov_receipt["scientific_unfreeze"] is False

for x in [
    "Xie et al. (2017",
    "Sugai et al. (2021",
    "Sarker et al. (2022",
    "Zhang et al. (2014",
    "approximately **92% crosses at least one spatial and/or taxonomic matrix boundary**"
]:
    if x not in nov:
        raise SystemExit(f"RC7 novelty audit drift: {x}")

for x in [
    "Xie et al. (2017) already showed lagged rainfall associations",
    "The paper's novelty depends on a null beta-diversity result.",
    "The rainfall signal could still be created entirely by the programme's 0–3 day rain-target scheduling."
]:
    if x not in rev:
        raise SystemExit(f"RC7 reviewer matrix drift: {x}")

checklist=(root/"submission/JAE_PORTAL_CHECKLIST_V0_6.md").read_text(encoding="utf-8")
for x in ["RC7_STORY_FREEZE_V0_1.json","[x] RC7 scientific-package QA","[x] anonymous v0.9 DOCX QA","## RC7 protocol-window robustness","NAAMP_PROTOCOL_WINDOW_SENSITIVITY_SUMMARY_V0_1.json","NOVELTY_AUDIT_V0_6.md","REVIEWER_ATTACK_MATRIX_V0_6.md","COVER_LETTER_JAE_V0_8.md"]:
    if x not in checklist: raise SystemExit(f"RC7 checklist drift: {x}")
print("RC7 geographic-generality scientific package QA: PASS")
