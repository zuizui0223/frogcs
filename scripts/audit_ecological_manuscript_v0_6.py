#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("--manuscript",default=str(ROOT/"MANUSCRIPT_JAE_V0_6.md"))
parser.add_argument("--review-stage",choices=["initial","final"],default="initial")
args=parser.parse_args()

MS=Path(args.manuscript)
text=MS.read_text(encoding="utf-8")
expected="# Recent rainfall predicts week-long richness elevation and species-selective reassembly in active frog communities"
assert text.startswith(expected)

# Core ecological claims and exact timescale boundary.
for required in [
    "+0.654 species",
    "+0.544",
    "+0.411",
    "+0.381",
    "days 4–7",
    "Q = 144.0",
    "52.1%",
    "P = 8.28 × 10^-8",
    "β = 0.0184",
    "species-selective",
]:
    assert required in text, required

# Hard guards against overclaiming.
lower=text.lower()
assert "compositional memory" not in lower
assert "rainfall causes" not in lower
assert "colonization" in lower  # present only as a boundary/negation
assert "occupancy" in lower
assert "days 4–7" in text
assert "precise physiological recovery time" in lower
assert "compositional memory" not in lower

abstract=text.split("## Abstract",1)[1].split("## Keywords",1)[0]
abstract_words=len(re.findall(r"\b[\wÀ-ÿα-ωΑ-Ω≥≤×−–]+\b",abstract))
assert abstract_words<=350,abstract_words
for i in range(1,6):
    assert re.search(rf"^\s*{i}\. ",abstract,re.M)
assert "body-size" not in abstract.lower()
assert "body size" not in abstract.lower()

keywords=text.split("## Keywords",1)[1].split("## Introduction",1)[0]
ks=[x.strip() for x in keywords.strip().split(";") if x.strip()]
assert len(ks)<=8,ks
assert ks==sorted(ks,key=str.lower),ks

total_words=len(re.findall(r"\b[\wÀ-ÿα-ωΑ-Ω≥≤×−–]+\b",text))
assert total_words<=8500,total_words

# Three main figures only.
assert "Figure 4." not in text
assert "Figure 1." in text and "Figure 2." in text and "Figure 3." in text

# Initial review stays anonymous.
if args.review_stage=="initial":
    assert "github.com/zuizui0223/frogcs" not in text
    assert "10.5281/zenodo." not in lower

print({
    "manuscript":str(MS),
    "abstract_words":abstract_words,
    "keywords":len(ks),
    "total_words":total_words,
    "status":"PASS",
})
