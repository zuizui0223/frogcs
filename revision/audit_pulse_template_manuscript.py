#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"paper"/"manuscript_pulse_template_v0_3.md"
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
    "1.332",
    "β = 0.244",
    "0.254",
    "25 had positive contributions",
    "18.8%",
    "54.2%",
    "0.0855",
    "0.967 to 1.775",
    "Brooke et al., 2000",
    "Trenham et al., 2003",
    "post-opening and exploratory",
    "higher-order spatial organization",
    "recurrent species × site",
    "(Fig. 1)",
    "(Figs 2–3)",
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
    "rain causes",
]:
    assert x not in text, f"legacy/overclaim token present: {x}"

for n in range(1,6):
    assert f"**Figure {n}." in text, f"missing Figure {n} legend"

assert "not literal synchrony" in text
assert "not abundance, occupancy, colonization, spawning or reproductive success" in text
assert "not proposed as universal" in text
assert "Universality of the full mechanism remains unestablished" in text

manuscript_words=len(text.split())
assert manuscript_words <= 8000, f"anonymous manuscript exceeds 8000-word safety target: {manuscript_words}"

abstract=text.split("## Abstract",1)[1].split("## Keywords",1)[0]
abstract_words=len(abstract.split())
assert abstract_words <= 350, f"abstract exceeds JAE 350-word limit: {abstract_words}"

keywords=text.split("## Keywords",1)[1].split("## Introduction",1)[0].strip()
keylist=[x.strip() for x in keywords.split(";") if x.strip()]
assert len(keylist) <= 8, keylist
assert keylist == sorted(keylist,key=str.lower), f"keywords not alphabetized: {keylist}"
for x in [
    "structured community-state transition",
    "higher-order within-taxon structure",
    "same-observer + same-site pairs",
    "cross-fitted species rainfall sensitivity",
    "historically strong sites",
    "lower-level biological generator remains unresolved",
]:
    assert x in abstract, f"abstract missing: {x}"

# The Discussion must foreground the positive ecological result before null failures.
discussion=text.split("## Discussion",1)[1].split("## Data Availability",1)[0]
assert discussion.index("higher-order spatial coherence") < discussion.index("First-order species and site processes")
assert "The inference is therefore not that “other factors exist,”" in discussion

# Every key bibliography item remains represented.
reference_surnames=["Brooke","Brodie","Foreman","Holt","Kusano","Oseen","Ospina","Rowley","Royle","Rush","Saenz","Sarker","Sugai","Switzer","Trenham","Xie","Yang"]
body=text.split("## References",1)[0]
for surname in reference_surnames:
    assert re.search(rf"^{surname},", text, flags=re.M), f"missing reference: {surname}"
    assert surname in body, f"reference listed but not cited in body: {surname}"

print(f"pulse-template manuscript v0.3 QA: PASS ({manuscript_words} manuscript words; {abstract_words} abstract words; {len(keylist)} keywords)")
