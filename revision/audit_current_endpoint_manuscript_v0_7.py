#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"paper"/"manuscript.md"
SI=ROOT/"paper"/"supporting_information.md"

text=MANUSCRIPT.read_text()
si=SI.read_text()

TITLE="# Rainfall-associated frog chorus activation is concentrated within taxa across multiple sites"
assert text.startswith(TITLE+"\n")

required=[
    "4,236",
    "2,916",
    "within-taxon multi-site concentration",
    "1.650",
    "1.353",
    "0.297",
    "1.332",
    "0.151",
    "0.0245",
    "18.8%",
    "54.2%",
    "0.0855",
    "0.967 to 1.775",
    "dependence structure",
    "post-opening and exploratory",
    "independent monitoring programmes",
    "(Fig. 1)",
    "(Figs 2–3)",
    "(Fig. 4)",
    "(Fig. 5)",
]
for x in required:
    assert x in text, f"missing required manuscript token: {x}"

# Main-text routing: these are deliberately SI-only in the novelty-maximized track.
for x in [
    "### Cross-dataset taxonomic-depth consistency",
    "### Taxonomic deepening has the same recent-rain direction in Australian FrogID",
    "### Exact species × stop allocation",
    "### Multi-site concentration accompanies a broader matrix-allocation shift",
    "98.1%",
    "98.9%",
    "92.0%",
]:
    assert x not in text, f"secondary/defence result leaked back into main text: {x}"

for x in [
    "higher-order",
    "was not tested",
    "remains untested",
    "Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts",
    "first demonstration",
    "first evidence",
    "rain causes",
]:
    assert x not in text, f"legacy/ambiguous/overclaim token present: {x}"

for n in range(1,6):
    assert f"**Figure {n}." in text, f"missing Figure {n} legend"

assert "not abundance, occupancy, colonization, spawning or reproductive success" in text
assert "rather than a universal law" in text
assert "do **not** claim novelty for spatially structured pulses, environmental synchrony, response diversity or marginal-versus-joint structure in general" in text
assert "Universality of the full mechanism remains unestablished" in text

manuscript_words=len(text.split())
assert manuscript_words <= 8000, f"anonymous manuscript exceeds 8000-word safety target: {manuscript_words}"

abstract=text.split("## Abstract",1)[1].split("## Keywords",1)[0]
abstract_words=len(abstract.split())
assert abstract_words <= 350, f"abstract exceeds JAE 350-word limit: {abstract_words}"
for x in [
    "focal endpoint",
    "1.650",
    "1.353",
    "0.297",
    "1.332",
    "recurrent taxon-specific sites",
    "independent monitoring programmes",
]:
    assert x in abstract, f"abstract missing: {x}"
for x in [
    "1.61-fold",
    "2.69-fold",
]:
    assert x in abstract, f"abstract missing concrete monitoring implication: {x}"
assert "0.244" not in abstract, "secondary exchangeable N,K diagnostic must not be abstract headline"
assert "We ask three linked questions" not in text, "legacy equal-weight three-question framing remains in manuscript"
assert "### Focal endpoint: recruited taxa show excess within-taxon multi-site concentration" in text
assert "### Response magnitude does not fully describe the spatial pattern of activation" in text
assert "marginal activation" in text
assert "response magnitude alone may be insufficient to describe a short behavioural pulse" in text

keywords=text.split("## Keywords",1)[1].split("## Introduction",1)[0].strip()
keylist=[x.strip() for x in keywords.split(";") if x.strip()]
assert len(keylist) <= 8, keylist
assert keylist == sorted(keylist,key=str.lower), f"keywords not alphabetized: {keylist}"

discussion=text.split("## Discussion",1)[1].split("## Data Availability",1)[0]
assert "dependence structure" in discussion
assert "cross-fitting prevents route leakage" in discussion.lower()
assert "does not create an untouched confirmation dataset" in discussion.lower()

# SI must carry the defence/falsification layer removed from the main text.
for x in [
    "## S0. Evidence routing and reviewer-defence map",
    "## S6. Activation geometry: repeatability followed by placebo falsification",
    "## S11. Spatial depth of recruited route species",
    "### S11.7 Secondary exact N,K-conditioned combinatorial diagnostic",
    "## S12. Historical recurrence of apparent wet-state recruitment",
    "## S15. Nested mechanism-null sequence",
    "FrogID",
    "92.0%",
    "98.1%",
]:
    assert x in si, f"SI missing routed defence/falsification content: {x}"

reference_surnames=["Brooke","Brodie","Ceron","Dormann","Foreman","Gotelli","Guzy","Holt","Jenkins","Jentsch","Kunze","Kusano","Liebhold","McGeoch","Oseen","Ospina","Picardi","Pollock","Rowley","Royle","Saenz","Sarker","Sugai","Switzer","Thompson","Tikhonov","Trenham","Xie","Yang"]
body=text.split("## References",1)[0]
for surname in reference_surnames:
    assert re.search(rf"^{surname},", text, flags=re.M), f"missing reference: {surname}"
    assert surname in body, f"reference listed but not cited in body: {surname}"

refs_block=text.split("## References",1)[1].split("## Figure legends",1)[0].strip()
ref_entries=[x.strip() for x in re.split(r"\n\s*\n",refs_block) if x.strip()]
first_authors=[x.split(",",1)[0].strip() for x in ref_entries]
assert first_authors == sorted(first_authors,key=str.casefold), f"references not alphabetized: {first_authors}"
for surname in sorted(set(first_authors),key=str.casefold):
    assert surname in body, f"uncited reference remains: {surname}"

print(
    f"current-endpoint manuscript v0.7 QA: PASS "
    f"({manuscript_words} manuscript words; {abstract_words} abstract words; "
    f"{len(keylist)} keywords; SI routing intact)"
)
