#!/usr/bin/env python3
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
m=(root/"MANUSCRIPT_JAE_V1_2.md").read_text(encoding="utf-8")
si=(root/"SUPPORTING_INFORMATION_JAE_RC10_V0_1.md").read_text(encoding="utf-8")
cl=(root/"submission/COVER_LETTER_JAE_V0_13.md").read_text(encoding="utf-8")
title=(root/"JAE_TITLE_PAGE_V0_8.template.md").read_text(encoding="utf-8")

WORD_RE=re.compile(r"\b[\wÀ-ÖØ-öø-ÿĀ-ž’'–—+./×βρκΔ≥≤%-]+\b",re.UNICODE)
wc=lambda s:len(WORD_RE.findall(s))
am=re.search(r"## Abstract\s*(.*?)\n## Keywords",m,re.S)
km=re.search(r"## Keywords\s*(.*?)\n## Introduction",m,re.S)
rm=re.search(r"## References\s*(.*?)\n## Figure legends",m,re.S)
assert am and km and rm
abstract=am.group(1)
keywords=[x.strip() for x in km.group(1).strip().split(";") if x.strip()]
refs=[x.strip() for x in re.split(r"\n\s*\n",rm.group(1).strip()) if x.strip()]
def key(x): return x.split(",",1)[0].casefold()

assert wc(m)+wc(title) <= 8500
assert wc(abstract)<=350
assert len(re.findall(r"(?m)^\d+\. ",abstract))==5
assert len(keywords)<=8
assert keywords==sorted(keywords,key=str.casefold)
assert refs==sorted(refs,key=key)
assert "(Fig. 1)" in m and "(Fig. 2)" in m and "(Fig. 3)" in m
assert "## Data Availability" in m
for x in ["10.5066/F7G44NG0","10.3897/zookeys.912.38253","10.6084/m9.figshare.4644424.v5"]:
    assert x in m
assert "involved no new animal capture, handling or field sampling" in m
assert wc(cl)<=500
assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",m+"\n"+si)
assert "https://github.com/" not in m+si

print({
 "status":"PASS",
 "manuscript_words":wc(m),
 "title_words":wc(title),
 "combined_proxy_words":wc(m)+wc(title),
 "abstract_words":wc(abstract),
 "cover_words":wc(cl),
 "references":len(refs)
})
