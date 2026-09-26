#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import re

parser=argparse.ArgumentParser()
parser.add_argument("--manuscript", default="MANUSCRIPT_JAE_V0_8.md")
args=parser.parse_args()

MAN=Path(args.manuscript)
CLAIM=Path("ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json")
SPINE=Path("COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md")

for p in [MAN,CLAIM,SPINE]:
    if not p.is_file():
        raise SystemExit(f"missing required file: {p}")

text=MAN.read_text(encoding="utf-8")
claim=json.loads(CLAIM.read_text(encoding="utf-8"))
spine=SPINE.read_text(encoding="utf-8")

expected_title="# Recent rainfall expands frog active communities across sites and species without detectable change in beta diversity"
if not text.startswith(expected_title+"\n"):
    raise SystemExit("v0.8 title drift")

if text.count("## Materials and Methods") != 1:
    raise SystemExit(f"Materials and Methods heading count = {text.count('## Materials and Methods')}")

abstract=text.split("## Abstract",1)[1].split("## Keywords",1)[0]
for bad in [
    "week-long richness elevation",
    "week-long community",
    "preserving beta diversity",
    "beta diversity is preserved",
    "beta diversity was unchanged",
    "rainfall causes"
]:
    if bad.lower() in abstract.lower():
        raise SystemExit(f"overclaim in abstract: {bad}")

required_abstract=[
    "4,236",
    "β = 0.384",
    "β = 0.079",
    "β = 0.286",
    "P = 0.937",
    "36.9%",
    "39.9%",
    "P = 0.797",
    "P = 0.739"
]
for x in required_abstract:
    if x not in abstract:
        raise SystemExit(f"missing abstract anchor: {x}")

required_body=[
    "The original rainfall endpoint in the broader analysis programme was frozen before effect readback.",
    "metacommunity-scale",
    "species × stop incidence matrix",
    "response-sign diversity",
    "does not assume or demonstrate that all stops form a demographic metacommunity"
]
for x in required_body:
    if x not in text:
        raise SystemExit(f"missing provenance/boundary text: {x}")

if claim.get("working_title") != expected_title[2:]:
    raise SystemExit("claim-boundary title mismatch")

for phrase in [
    "beta diversity is proven unchanged or equivalent across rainfall contrasts",
    "week-long compositional reassembly",
    "response diversity provides an insurance effect in these data"
]:
    if phrase not in claim.get("prohibited",[]):
        raise SystemExit(f"claim boundary missing prohibition: {phrase}")

for doi in ["10.1038/s41467-026-70192-x","10.1111/ele.70299"]:
    if doi not in text:
        raise SystemExit(f"missing verified response-diversity reference DOI: {doi}")

print("JAE v0.8 metacommunity QA PASS")
