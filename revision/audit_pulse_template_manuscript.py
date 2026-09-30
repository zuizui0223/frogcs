#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"paper"/"manuscript_pulse_template_v0_2.md"
text=P.read_text()

TITLE="# Rainfall-associated frog chorus activation shows higher-order spatial coherence and species-specific site recurrence"
assert text.startswith(TITLE+"\n")

required=[
    "4,236",
    "higher-order within-species mass",
    "β = 1.524",
    "1.817",
    "0.326",
    "0.297",
    "25 had positive contributions",
    "18.8%",
    "54.2%",
    "0.0855",
    "0.967 to 1.775",
    "Brooke et al., 2000",
    "Trenham et al., 2003",
    "post-opening and exploratory",
    "(Fig. 1)",
    "(Figs. 2–3)",
    "(Fig. 4)",
    "(Fig. 5)",
]
for x in required:
    assert x in text, f"missing required manuscript token: {x}"

for x in [
    "was not tested",
    "remains untested",
    "Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts",
    "RC11",
    "first demonstration",
    "first evidence",
]:
    assert x not in text, f"legacy/overclaim token present: {x}"

for n in range(1,6):
    assert f"**Figure {n}." in text, f"missing Figure {n} legend"

assert "not literal synchrony" in text
assert "not abundance, occupancy, colonization, spawning or reproductive success" in text
assert "not proposed here as universal" in text
assert "Universality of the full mechanism remains unestablished" in text

# Abstract must foreground the new biological hierarchy.
abstract=text.split("## Abstract",1)[1].split("## Keywords",1)[0]
abstract_words=len(abstract.split())
assert abstract_words <= 350, f"abstract exceeds JAE 350-word limit: {abstract_words}"
for x in [
    "cross-site synchrony are well known in frogs",
    "higher-order within-taxon structure",
    "same-observer + same-site pairs",
    "species rainfall sensitivity",
    "historically strong sites",
]:
    assert x in abstract, f"abstract missing: {x}"

# Every bibliography item remains represented once at minimum.
for surname in ["Brooke","Brodie","Kusano","Oseen","Ospina","Rush","Saenz","Sugai","Switzer","Trenham","Yang"]:
    assert re.search(rf"^{surname},", text, flags=re.M), f"missing reference: {surname}"

print("pulse-template manuscript QA: PASS")
