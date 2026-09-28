#!/usr/bin/env python3
from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_1.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC9_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_12.md").read_text(encoding="utf-8")
summary=json.loads((root/"CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
contract=json.loads((root/"CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json").read_text(encoding="utf-8"))
tree=json.loads((root/"submission/RC8_CROSSCONTINENTAL_DEPTH_DECISION_TREE_V0_1.json").read_text(encoding="utf-8"))
unfreeze=json.loads((root/"submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json").read_text(encoding="utf-8"))

WORD_RE=re.compile(r"\b[\wÀ-ÖØ-öø-ÿĀ-ž’'–—+./×βρκΔ≥≤%-]+\b",re.UNICODE)
wc=lambda s:len(WORD_RE.findall(s))

title="Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization"
assert m.startswith("# "+title)
assert title in cl
assert summary["decision"]=="STRONG_PASS"
assert summary["generalization_boundary"]["cross_continental_consistency_authorized"] is True
assert summary["generalization_boundary"]["worldwide_universality_authorized"] is False
assert summary["generalization_boundary"]["pooled_effect_size_authorized"] is False
assert contract["status"]=="frozen_before_australian_continuous_depth_readback"
assert tree["status"]=="frozen_before_australian_continuous_depth_readback"
assert unfreeze["status"]=="author_directed_external_validation_unfreeze"

aus=summary["australia"]
assert aus["n_recordings"]==40754
assert aus["weather_cells"]==1623
assert aus["primary_excess_richness"]["beta_per_sd_log1p_dry_days"] < 0
assert aus["primary_excess_richness"]["ci95"][1] < 0
assert aus["recorder_cluster_sensitivity"]["ci95"][1] < 0
assert aus["within_era5_cell_sensitivity"]["ci95"][1] < 0
assert summary["north_america"]["ci95"][0] > 0

required_m=[
 "Australian FrogID",
 "40,754",
 "β = -0.0818",
 "95% CI -0.0982 to -0.0654",
 "strong PASS",
 "OR = 0.846",
 "β = -0.0483",
 "cross-continental consistency",
 "OR = 0.988",
 "not as worldwide universality",
 "do not pool effect sizes",
]
for x in required_m:
    if x not in m:
        raise SystemExit(f"RC9 manuscript missing: {x}")

required_si=[
 "Cross-continental external validation of active-unit taxonomic depth",
 "STRONG PASS",
 "-0.08176",
 "-0.09984",
 "0.8458",
 "-0.04833",
 "worldwide or universal rainfall response",
]
for x in required_si:
    if x not in si:
        raise SystemExit(f"RC9 SI missing: {x}")

required_cover=[
 "40,754 expert-validated Australian FrogID recordings",
 "0.0818 species",
 "cross-continentally consistent",
 "community amplification",
 "community recruitment",
 "worldwide universality",
]
for x in required_cover:
    if x not in cl:
        raise SystemExit(f"RC9 cover missing: {x}")

abstract=re.search(r"## Abstract\s*(.*?)\n## Keywords",m,re.S)
refs=re.search(r"## References\s*(.*?)\n## Figure legends",m,re.S)
assert abstract and refs
assert wc(abstract.group(1)) <= 350
assert wc(m)+113 <= 8500
assert wc(cl) <= 500

blocks=[x.strip() for x in re.split(r"\n\s*\n",refs.group(1).strip()) if x.strip()]
def key(x): return x.split(",",1)[0].casefold()
assert blocks==sorted(blocks,key=key)

assert "Rowley, J. J. L., & Callaghan, C. T. (2020)." in m
assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",m+"\n"+si)
assert "https://github.com/" not in m+si

forbidden=[
 "worldwide generality",
 "universal rainfall response across frogs",
 "same effect size across continents",
 "identical mechanism across continents",
 "FrogID replicates the four-component matrix geometry",
 "rainfall caused"
]
for x in forbidden:
    if x.lower() in (m+"\n"+cl).lower():
        raise SystemExit(f"RC9 overclaim: {x}")

print({
 "status":"PASS",
 "manuscript_words":wc(m),
 "abstract_words":wc(abstract.group(1)),
 "cover_words":wc(cl),
 "australia_primary_beta":aus["primary_excess_richness"]["beta_per_sd_log1p_dry_days"],
 "cross_continental_decision":summary["decision"],
})
