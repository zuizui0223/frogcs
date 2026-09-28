#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/"MANUSCRIPT_JAE_V1_0.md"
SI=ROOT/"SUPPORTING_INFORMATION_JAE_RC8_V0_1.md"
COVER=ROOT/"submission/COVER_LETTER_JAE_V0_10.md"
TITLE=ROOT/"JAE_TITLE_PAGE_V0_6.template.md"

WORD_RE=re.compile(r"\b[\wÀ-ÖØ-öø-ÿĀ-ž’'–—+./×βρκΔ≥≤%-]+\b",re.UNICODE)

def wc(text:str)->int:
    return len(WORD_RE.findall(text))

m=MAN.read_text(encoding="utf-8")
si=SI.read_text(encoding="utf-8")
cover=COVER.read_text(encoding="utf-8")
title=TITLE.read_text(encoding="utf-8")

am=re.search(r"## Abstract\s*(.*?)\n## Keywords",m,re.S)
km=re.search(r"## Keywords\s*(.*?)\n## Introduction",m,re.S)
rm=re.search(r"## References\s*(.*?)\n## Figure concepts",m,re.S)
assert am and km and rm

abstract=am.group(1)
keywords=[x.strip() for x in km.group(1).strip().split(";") if x.strip()]
refs=[x.strip() for x in re.split(r"\n\s*\n",rm.group(1).strip()) if x.strip()]

def refkey(block:str)->str:
    x=block.split(",",1)[0]
    return x.casefold()

assert wc(m)+wc(title) <= 8500, (wc(m),wc(title))
assert wc(abstract) <= 350, wc(abstract)
assert len(re.findall(r"(?m)^\d+\. ",abstract)) == 5
assert len(keywords) <= 8, keywords
assert keywords == sorted(keywords,key=str.casefold), keywords
assert refs == sorted(refs,key=refkey), [refkey(x) for x in refs]
assert "(Fig. 1)" in m and "(Fig. 2)" in m
assert "## Data Availability" in m
assert "10.5066/F7G44NG0" in m
assert "persistent archive identifier will be added at finalization" in m
assert "involved no new animal capture, handling or field sampling" in m
assert wc(cover) <= 500, wc(cover)
assert "Anonymous cover letter" in cover
assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",m+"\n"+si)
assert "https://github.com/" not in m+si

for x in [
    "## Acknowledgements",
    "## Conflict of Interest",
    "## Author Contributions",
    "## Statement on Inclusion",
]:
    assert x in title, x

print({
    "status":"PASS",
    "manuscript_words":wc(m),
    "title_template_words":wc(title),
    "combined_proxy_words":wc(m)+wc(title),
    "abstract_words":wc(abstract),
    "keywords":len(keywords),
    "references":len(refs),
    "cover_words":wc(cover),
})
