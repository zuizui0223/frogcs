#!/usr/bin/env python3
"""Developmental predation-role timing vs frog-call incidence: source-gated screen.

This produces descriptive correlations for stage-specific observation fractions.
It NEVER infers an attack-direction switch or an alarm response from occurrence.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

CALL_FIELDS = {"cell_id", "season_id", "week_start", "species",
               "positive_recordings", "total_recordings"}
STAGE_FIELDS = {"cell_id", "season_id", "week_start", "species", "stage",
                "count", "total_annotated"}
STAGES = {"egg", "larva", "metamorph", "emerging", "juvenile", "adult"}
GATES = (
    "authenticated_original_rows", "event_id_deduplication",
    "validated_stage_ontology", "coarse_coordinates_safe",
    "same_cell_year_season_support", "program_specific_effort_denominators",
    "original_sources_version_locked"
)
LAGS = (0, 1, 2, 4, 8)


def read_csv(path, fields):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = fields - set(reader.fieldnames or [])
        if missing:
            raise ValueError("missing columns: " + ",".join(sorted(missing)))
        return list(reader)


def week(s):
    d = date.fromisoformat(s)
    if d.weekday() != 0:
        raise ValueError("week_start is not Monday: " + s)
    return d


def fraction(n, d):
    numerator, denominator = int(n), int(d)
    if denominator <= 0 or not 0 <= numerator <= denominator:
        raise ValueError("invalid numerator or denominator")
    return numerator / denominator, denominator, numerator


def parse_calls(path):
    out, denominators = {}, {}
    for row in read_csv(path, CALL_FIELDS):
        group = (row["cell_id"].strip(), row["season_id"].strip(), week(row["week_start"]))
        if not all(group[:2]) or not row["species"].strip():
            raise ValueError("blank call key")
        key = group + (row["species"].strip(),)
        if key in out:
            raise ValueError("duplicate call-week species")
        val, den, num = fraction(row["positive_recordings"], row["total_recordings"])
        if group in denominators and denominators[group] != den:
            raise ValueError("inconsistent total recording opportunities across taxa")
        denominators[group] = den
        out[key] = val
    return out


def parse_stages(path):
    out, denominators, sums = {}, {}, defaultdict(int)
    for row in read_csv(path, STAGE_FIELDS):
        group = (row["cell_id"].strip(), row["season_id"].strip(), week(row["week_start"]), row["species"].strip())
        if not group[0] or not group[1] or not group[3]:
            raise ValueError("blank stage key")
        if row["stage"] not in STAGES:
            raise ValueError("unrecognized stage; never silently normalize unknown")
        key = group + (row["stage"],)
        if key in out:
            raise ValueError("duplicate life-stage count")
        val, den, num = fraction(row["count"], row["total_annotated"])
        if group in denominators and denominators[group] != den:
            raise ValueError("inconsistent annotation denominator")
        denominators[group] = den
        sums[group] += num
        out[key] = val
    if any(sums[key] > denominators[key] for key in sums):
        raise ValueError("stage counts exceed annotation opportunities")
    return out


def read_edges(path):
    fields = {"pair_id", "predator_species", "predator_stage", "prey_species",
              "prey_stage", "evidence_class", "doi", "acoustic_eligible"}
    rows = read_csv(path, fields)
    allowed = {"DIRECT_PAIR_DIRECTION", "PRIMARY_SOURCE_PAIR_DIRECTION"}
    pairs = defaultdict(list)
    for r in rows:
        if r["evidence_class"] not in allowed:
            continue
        if r["predator_stage"] not in STAGES or r["prey_stage"] not in STAGES:
            raise ValueError("invalid direct edge life stage")
        pairs[r["pair_id"]].append(r)
    admitted = {}
    for pair, es in pairs.items():
        if len(es) == 2 and es[0]["predator_species"] == es[1]["prey_species"] and es[1]["predator_species"] == es[0]["prey_species"]:
            admitted[pair] = es
    return admitted


def gate(path):
    if not path or not Path(path).is_file():
        return {"status": "NOT_ESTIMABLE", "missing": ["original_source_gate"]}
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [name for name in GATES if doc.get(name) is not True]
    if doc.get("data_are_synthetic") is True:
        missing.append("synthetic_fixture_not_empirical")
    return {"status": "READY_FOR_DESCRIPTIVE_SCREEN" if not missing else "NOT_ESTIMABLE",
            "missing": missing}


def correlation(samples, min_weeks=4):
    """Within-cell-season centered correlation: descriptive, no independence claim."""
    groups = defaultdict(list)
    for (cell, season, x, y) in samples:
        groups[cell, season].append((x, y))
    groups = [v for v in groups.values() if len(v) >= min_weeks]
    centered = []
    for v in groups:
        mx = sum(x for x, _ in v) / len(v)
        my = sum(y for _, y in v) / len(v)
        centered.extend((x - mx, y - my) for x, y in v)
    if not centered:
        return {"n_cell_seasons": 0, "n_matched_weeks": 0, "r": None,
                "status": "NOT_ESTIMABLE"}
    sx = sum(x*x for x, y in centered)
    sy = sum(y*y for x, y in centered)
    r = (sum(x*y for x, y in centered) / math.sqrt(sx*sy)) if sx > 1e-12 and sy > 1e-12 else None
    return {"n_cell_seasons": len(groups), "n_matched_weeks": len(centered),
            "r": round(r, 6) if r is not None else None,
            "status": "DESCRIPTIVE_ONLY" if r is not None else "ZERO_VARIANCE"}


def scan(calls, stages, call_species, stage_species, stage):
    """Test a single stage fraction, not cross-source co-occurrence or attack."""
    ca = {(c, s, t): p for (c, s, t, sp), p in calls.items() if sp == call_species}
    st = {(c, s, t): p for (c, s, t, sp, v), p in stages.items()
          if sp == stage_species and v == stage}
    series = {}
    for lag in LAGS:
        offset = timedelta(weeks=lag)
        aligned = [(c, s, x, st[c, s, t+offset]) for (c, s, t), x in ca.items()
                   if (c, s, t+offset) in st]
        series[str(lag)] = correlation(aligned)
        if not lag:
            continue
        same_anchor = [(c, s, x, st[c, s, t+offset], st[c, s, t-offset])
                       for (c, s, t), x in ca.items()
                       if (c, s, t+offset) in st and (c, s, t-offset) in st]
        positive = correlation([(c, s, x, y) for c, s, x, y, z in same_anchor])
        negative = correlation([(c, s, x, z) for c, s, x, y, z in same_anchor])
        series["asymmetry_" + str(lag)] = {
            "status": "DESCRIPTIVE_ONLY" if positive["r"] is not None and negative["r"] is not None else "NOT_ESTIMABLE",
            "n_same_anchor_weeks": len(same_anchor),
            "positive_r": positive["r"], "negative_r": negative["r"],
            "positive_minus_negative_r": round(positive["r"] - negative["r"], 6)
            if positive["r"] is not None and negative["r"] is not None else None
        }
    return series


def execute(calls_path, stages_path, edges_path, gate_path, call_species):
    readiness = gate(gate_path)
    if readiness["status"] != "READY_FOR_DESCRIPTIVE_SCREEN":
        return {"status": "NOT_ESTIMABLE", "readiness": readiness, "n_original_rows_analyzed": 0}
    if not (calls_path and stages_path and Path(calls_path).is_file() and Path(stages_path).is_file()):
        return {"status": "NOT_ESTIMABLE", "readiness": {"status": "NOT_ESTIMABLE",
            "missing": ["original_calls_and_stages_rows"]}, "n_original_rows_analyzed": 0}
    calls, stages = parse_calls(calls_path), parse_stages(stages_path)
    pairs = read_edges(edges_path)
    scans = {}
    for pair, edges in pairs.items():
        for edge in edges:
            for species, stage in ((edge["predator_species"], edge["predator_stage"]),
                                   (edge["prey_species"], edge["prey_stage"])):
                k = pair + " | " + species + " | " + stage
                if k not in scans:
                    scans[k] = scan(calls, stages, call_species, species, stage)
    eligible = sum(any(val["n_cell_seasons"] >= 3
                       for key, val in v.items() if key in tuple(str(i) for i in LAGS))
                   for v in scans.values())
    return {"status": "DESCRIPTIVE_ONLY_NO_TROPHIC_SWITCH_OR_WARNING_INFERENCE" if eligible
            else "NOT_ESTIMABLE_INSUFFICIENT_INDEPENDENT_CELL_SEASONS",
            "readiness": readiness, "admitted_direct_reciprocal_pairs": sorted(pairs),
            "n_call_records": len(calls), "n_stage_fraction_records": len(stages),
            "n_stage_series_with_3plus_cell_seasons": eligible,
            "n_original_rows_analyzed": len(calls) + len(stages),
            "scans": scans,
            "limitations": [
                "Call-positive share conditional on submitted recordings; not population calling probability.",
                "Stage share conditional on annotated observations; not abundance, co-occurrence or attack rate.",
                "Cannot date predator/prey reversal without direct dated predation in both directions.",
                "Cannot infer warning-signalling or receiver behaviour from acoustic occurrence.",
                "A positive lag correlation is not an adjusted weather/season effect or prediction validation."
            ]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--calls")
    p.add_argument("--stages")
    p.add_argument("--edges", default=str(Path(__file__).resolve().parent.parent / "registry" / "source_screen_v0_2.csv"))
    p.add_argument("--source-gate")
    p.add_argument("--call-species", default="Litoria aurea")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    result = execute(a.calls, a.stages, a.edges, a.source_gate, a.call_species)
    Path(a.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
