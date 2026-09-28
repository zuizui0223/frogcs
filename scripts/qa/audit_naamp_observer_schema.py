#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "naamp"

def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

base = loadmod("pulse_base", ROOT / "run_naamp_ecological_pulse.py")

PATTERN = re.compile(r"(observer|volunteer|surveyor|listener|user|person|participant|obs.*(?:id|num|number))", re.I)

def fieldnames(rows):
    keys = set()
    for r in rows[:100]:
        keys.update(r.keys())
    return sorted(k for k in keys if k is not None)

def summarize_candidate(rows, field):
    vals = [str(r.get(field) or "").strip() for r in rows]
    nonempty = [v for v in vals if v]
    return {
        "field": field,
        "n_rows": len(rows),
        "n_nonempty": len(nonempty),
        "fraction_nonempty": len(nonempty) / len(rows) if rows else None,
        "n_unique_nonempty": len(set(nonempty)),
        "top_frequency": Counter(nonempty).most_common(1)[0][1] if nonempty else 0,
    }

def main():
    raw = base.load()
    receipt = {
        "analysis": "naamp_observer_schema_audit_v0_1",
        "purpose": "Determine whether the frozen public NAAMP release exposes an observer identifier suitable for same-observer sensitivity analysis. No observer values are emitted.",
        "files": {},
        "runs_candidate_fields": [],
        "conclusion": None,
    }
    for name, rows in raw.items():
        fields = fieldnames(rows)
        candidates = [f for f in fields if PATTERN.search(f)]
        receipt["files"][name] = {
            "n_rows": len(rows),
            "fieldnames": fields,
            "candidate_observer_like_fields": candidates,
        }
        if name == "Runs.csv":
            receipt["runs_candidate_fields"] = [summarize_candidate(rows, f) for f in candidates]

    usable = [
        x for x in receipt["runs_candidate_fields"]
        if x["n_nonempty"] > 0 and x["n_unique_nonempty"] > 1
    ]
    if usable:
        receipt["conclusion"] = {
            "observer_identifier_available_in_runs": True,
            "candidate_fields": [x["field"] for x in usable],
            "next_step": "Freeze and run a same-observer matched-pair sensitivity before using it in the manuscript.",
        }
    else:
        receipt["conclusion"] = {
            "observer_identifier_available_in_runs": False,
            "candidate_fields": [],
            "next_step": "Add observer turnover as an explicit limitation; a same-observer sensitivity cannot be reconstructed from Runs.csv alone.",
        }

    Path("NAAMP_OBSERVER_SCHEMA_AUDIT_RECEIPT_V0_1.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
