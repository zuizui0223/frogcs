#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

OLD = (
    "The standalone analysis repository will preserve the exact source digests, frozen analysis "
    "contracts, derived non-sensitive weather linkage, result receipts and figure-generation code. "
    "We intend to archive that repository on Zenodo for the submitted version and will insert the "
    "resulting DOI before final submission."
)

NEW_TEMPLATE = (
    "The standalone analysis repository preserves the exact source digests, frozen analysis "
    "contracts, derived non-sensitive weather linkage, result receipts and figure-generation code. "
    "The submitted reproducibility archive is available on Zenodo at DOI {doi}."
)

def normalize_doi(raw: str) -> str:
    doi = raw.strip()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    if not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        raise SystemExit(f"Invalid DOI syntax: {raw!r}")
    return doi

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--doi", required=True)
    p.add_argument("--input", default="MANUSCRIPT_JAE_V0_3.md")
    p.add_argument("--output", default="build/MANUSCRIPT_JAE_FINAL.md")
    args = p.parse_args()

    doi = normalize_doi(args.doi)
    src = Path(args.input)
    out = Path(args.output)
    text = src.read_text(encoding="utf-8")

    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"Expected exactly one archive placeholder paragraph, found {count}")

    updated = text.replace(OLD, NEW_TEMPLATE.format(doi=doi), 1)
    if updated == text:
        raise SystemExit("DOI insertion produced no change")

    # Scientific endpoint guard: only Data Availability may change.
    before_results = text.split("## Data Availability", 1)[0]
    after_results = updated.split("## Data Availability", 1)[0]
    if before_results != after_results:
        raise SystemExit("Scientific content before Data Availability changed unexpectedly")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(updated, encoding="utf-8")
    print({"doi": doi, "output": str(out), "status": "PASS"})

if __name__ == "__main__":
    main()
