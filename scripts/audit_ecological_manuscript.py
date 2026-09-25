#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MS=ROOT/"MANUSCRIPT_JAE_V0_5.md"
text=MS.read_text(encoding="utf-8")

expected_title="# Rainfall pulses increase frog active-community richness through species-selective reassembly"
assert text.startswith(expected_title)
assert "FrogID" not in text
assert "environmental filtering" not in text.lower()
assert "family-stratified permutation" in text
assert "two-sided P = 0.314" in text
assert "species-selective" in text
assert "Q = 144.01" in text
assert "β = 0.01840" in text

abstract=text.split("## Abstract",1)[1].split("## Keywords",1)[0]
abstract_words=len(re.findall(r"\b[\wÀ-ÿα-ωΑ-Ω≥≤×−–]+\b",abstract))
assert abstract_words <= 350, abstract_words
for i in range(1,6):
    assert re.search(rf"^\s*{i}\. ",abstract,re.M)

keywords=text.split("## Keywords",1)[1].split("## Introduction",1)[0]
ks=[x.strip() for x in keywords.strip().split(";") if x.strip()]
assert len(ks)<=8,ks
assert ks==sorted(ks,key=str.lower),ks

total_words=len(re.findall(r"\b[\wÀ-ÿα-ωΑ-Ω≥≤×−–]+\b",text))
assert total_words <= 8500,total_words

assert "Figure 4." not in text
assert "Figure 1." in text and "Figure 2." in text and "Figure 3." in text
assert "Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017)" in text
assert "Severgnini, M. R." in text

print({
  "abstract_words":abstract_words,
  "keywords":len(ks),
  "total_words":total_words,
  "status":"PASS"
})
