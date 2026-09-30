#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"paper"/"manuscript_pulse_template_v0_4.md"
text=P.read_text()

TITLE="# Rainfall-associated frog chorus activation shows within-taxon multi-site coherence and species-specific site recurrence"
assert text.startswith(TITLE+"\n")

required=[
    "4,236",
    "2,916",
    "within-taxon concentration",
    "1.650",
    "1.353",
    "0.297",
    "1.332",
    "0.318",
    "β = 0.244",
    "secondary combinatorial check",
    "exchangeability",
    "0.151",
    "0.0245",
    "25 had positive contributions",
    "18.8%",
    "54.2%",
    "0.0855",
    "0.967 to 1.775",
    "post-opening and exploratory",
    "no unexamined NAAMP partition",
    "external prospective replication",
    "(Fig. 1)",
    "(Figs 2–3)",
    "(Fig. 4)",
    "(Fig. 5)",
]
for x in required:
    assert x in text, f"missing required manuscript token: {x}"

for x in [
    "higher-order",
    "was not tested",
    "remains untested",
    "Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts",
    "RC11",
    "first demonstration",
    "first evidence",
    "rain causes",
]:
    assert x not in text, f"legacy/ambiguous/overclaim token present: {x}"

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
for x in [
    "principal spatial comparator",
    "1.650 versus 1.353",
    "held-out rain × history gate",
    "species-specific physical sites",
    "remains exploratory",
    "prospective external confirmation",
]:
    assert x in abstract, f"abstract missing: {x}"
assert "0.244" not in abstract, "secondary exchangeable N,K diagnostic must not be abstract headline"

keywords=text.split("## Keywords",1)[1].split("## Introduction",1)[0].strip()
keylist=[x.strip() for x in keywords.split(";") if x.strip()]
assert len(keylist) <= 8, keylist
assert keylist == sorted(keylist,key=str.lower), f"keywords not alphabetized: {keylist}"

discussion=text.split("## Discussion",1)[1].split("## Data Availability",1)[0]
assert discussion.index("strongest evidence comes from the comparator") < discussion.index("exact N,K-conditioned")
assert "cross-fitting prevents route leakage" in discussion.lower()
assert "does not create a genuinely untouched confirmation dataset" in discussion.lower()

reference_surnames=["Brooke","Brodie","Foreman","Holt","Kusano","Oseen","Ospina","Rowley","Royle","Rush","Saenz","Sarker","Sugai","Switzer","Trenham","Xie","Yang"]
body=text.split("## References",1)[0]
for surname in reference_surnames:
    assert re.search(rf"^{surname},", text, flags=re.M), f"missing reference: {surname}"
    assert surname in body, f"reference listed but not cited in body: {surname}"

print(f"pulse-template manuscript v0.4 QA: PASS ({manuscript_words} manuscript words; {abstract_words} abstract words; {len(keylist)} keywords)")
