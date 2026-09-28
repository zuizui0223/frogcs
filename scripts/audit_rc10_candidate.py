#!/usr/bin/env python3
from pathlib import Path
import json,re

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_2.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC10_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_13.md").read_text(encoding="utf-8")
nov=(root/"submission/NOVELTY_AUDIT_V0_10.md").read_text(encoding="utf-8")
rev=(root/"submission/REVIEWER_ATTACK_MATRIX_V0_10.md").read_text(encoding="utf-8")
pers=json.loads((root/"NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
contract=json.loads((root/"NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json").read_text(encoding="utf-8"))
tree=json.loads((root/"submission/RC10_STORY_DECISION_TREE_V0_1.json").read_text(encoding="utf-8"))
scope=json.loads((root/"submission/RC10_SCOPE_UNFREEZE_V0_1.json").read_text(encoding="utf-8"))
fig2=(root/"figures_ecology_v1_2/FIGURE_2_ALLOCATION_NULLS_V0_1.svg").read_text(encoding="utf-8")
fig3=(root/"figures_ecology_v1_2/FIGURE_3_CROSS_DATASET_DEPTH_V0_1.svg").read_text(encoding="utf-8")
title_page=(root/"JAE_TITLE_PAGE_V0_7.template.md").read_text(encoding="utf-8")

title="Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"
assert m.startswith("# "+title)
assert title in cl
assert scope["status"]=="author_directed_final_inferential_repair"
assert contract["status"]=="frozen_before_endpoint_readback"
assert tree["status"]=="frozen_before_persistence_null_readback"
assert pers["decision"]=="strong_rejection_under_persistence_anchoring"
assert pers["title_support"]["boundary_biased_title_authorized"] is True

primary=pers["anchor_0_75_primary"]
assert primary["omnibus_p"] < 0.05
assert primary["boundary_ci95"][1] < pers["observed"]["boundary_crossing_share"]
assert pers["anchor_0_50"]["omnibus_p"] < 0.05
assert pers["anchor_0_90"]["omnibus_p"] < 0.05

for x in [
  "persistence-preserving stress test",
  "77.9%",
  "73.4–82.8%",
  "22.1%",
  "directional cross-dataset consistency",
  "not presented as a blind validation exercise",
  "secondary bounded context",
]:
    if x not in m:
        raise SystemExit(f"RC10 manuscript missing: {x}")

if "without practical homogenization" in m.splitlines()[0].lower():
    raise SystemExit("RC10 title still headlines homogenization")
if "external validation" in m.lower():
    raise SystemExit("RC10 manuscript still uses external-validation wording")
if "independent replication" in m.lower():
    raise SystemExit("RC10 manuscript still uses independent-replication wording")

for x in [
  "# Supporting Information — JAE RC10 v1.2",
  "RC10 persistence-preserving uniform-activation stress test",
  "77.9%",
  "Directional cross-dataset consistency",
]:
    if x.lower() not in si.lower():
        raise SystemExit(f"RC10 SI missing: {x}")

for x in [
  "persistence-preserving",
  "77.9%",
  "cross-dataset directional consistency",
  "Pairwise Sørensen change was small",
]:
    if x not in cl:
        raise SystemExit(f"RC10 cover missing: {x}")

for x in ["77.9%","22.1%","FrogID is **not** described as independent validation"]:
    if x not in nov:
        raise SystemExit(f"RC10 novelty audit drift: {x}")

for x in ["Hierarchical shrinkage makes stable cells too exchangeable","title’s old","cross-dataset consistency"]:
    if x.lower() not in rev.lower():
        raise SystemExit(f"RC10 reviewer matrix drift: {x}")

for x in ["Persistence null","Observed 92.0%","Anchor a=.90"]:
    if x not in fig2:
        raise SystemExit(f"RC10 Figure 2 drift: {x}")
for x in ["Cross-dataset consistency only","NAAMP","FrogID"]:
    if x not in fig3:
        raise SystemExit(f"RC10 Figure 3 drift: {x}")

WORD_RE=re.compile(r"\b[\wÀ-ÖØ-öø-ÿĀ-ž’'–—+./×βρκΔ≥≤%-]+\b",re.UNICODE)
wc=lambda s:len(WORD_RE.findall(s))
abstract=re.search(r"## Abstract\s*(.*?)\n## Keywords",m,re.S)
refs=re.search(r"## References\s*(.*?)\n## Figure legends",m,re.S)
assert abstract and refs
assert wc(abstract.group(1)) <= 350
assert wc(m)+wc(title_page) <= 8500

blocks=[x.strip() for x in re.split(r"\n\s*\n",refs.group(1).strip()) if x.strip()]
def key(x): return x.split(",",1)[0].casefold()
assert blocks==sorted(blocks,key=key)

forbidden=[
  "worldwide universality is demonstrated",
  "same effect size across continents",
  "identical mechanism across continents",
  "rainfall caused"
]
for x in forbidden:
    if x.lower() in (m+"\n"+cl).lower():
        raise SystemExit(f"RC10 overclaim: {x}")

print({
  "status":"PASS",
  "title":title,
  "manuscript_words":wc(m),
  "title_page_words":wc(title_page),
  "combined_proxy":wc(m)+wc(title_page),
  "abstract_words":wc(abstract.group(1)),
  "persistence_decision":pers["decision"],
})
