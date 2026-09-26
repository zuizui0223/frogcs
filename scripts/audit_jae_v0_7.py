#!/usr/bin/env python3
from pathlib import Path
import re

P=Path("MANUSCRIPT_JAE_V0_7.md")
s=P.read_text(encoding="utf-8")
errors=[]

title=s.splitlines()[0] if s.splitlines() else ""
if "week-long" in title.lower():
    errors.append("week-long remains in title")
if "reassembly" in title.lower():
    errors.append("reassembly remains in title")

if s.count("## Materials and Methods") != 1:
    errors.append(f"Materials and Methods heading count={s.count('## Materials and Methods')}")

required=[
    "4,236",
    "585 routes",
    "0.384 active stops",
    "0.0794 species per active stop",
    "0.2859 species per unit contrast",
    "36.9%",
    "15.2%",
    "39.9%",
    "8.0%",
    "71.1%",
    "P = 0.937",
    "P = 0.339",
    "P = 0.797",
    "P = 0.739",
    "P = 0.419",
]
for x in required:
    if x not in s:
        errors.append(f"required result missing: {x}")

prohibited_patterns=[
    (r"rainfall causes", "causal rainfall wording"),
    (r"caused by rainfall", "causal rainfall wording"),
    (r"colonized the route", "colonization wording"),
    (r"went extinct", "extinction wording"),
    (r"week-long (?:community|richness|reassembly|pulse)", "week-long headline wording"),
    (r"response diversity (?:buffers|stabilizes) route", "unsupported response-diversity buffering"),
]
low=s.lower()
for pat,label in prohibited_patterns:
    if re.search(pat,low):
        errors.append(label)

# Ensure old v0.6 abstract claim is not retained.
if "multi-day expansion and species-selective reassembly" in low:
    errors.append("old v0.6 headline conclusion remains")

# Transparency statements.
for phrase in [
    "post-opening",
    "not evidence of demographic connectivity",
    "do not use “week-long pulse” as a headline inference",
    "does not assume or demonstrate that all stops form a demographic metacommunity",
]:
    if phrase not in s:
        errors.append(f"boundary statement missing: {phrase}")

if errors:
    print("JAE v0.7 QA FAILED")
    for e in errors:
        print("-",e)
    raise SystemExit(1)

print("JAE v0.7 QA PASS")
print("title:",title)
print("characters:",len(s))
print("words:",len(re.findall(r"\b\w+[\w’'-]*\b",s)))
