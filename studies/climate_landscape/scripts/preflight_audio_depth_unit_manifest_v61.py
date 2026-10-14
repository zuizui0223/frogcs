#!/usr/bin/env python3
"""v6.1 metadata-only wetland/recorder/logger join preflight.

SYNTHETIC QA ONLY. No animal responses, source locations or raw acoustic data.
Real-world decisions require a custodian-authenticated original deployment
manifest, source quality codes, measurement units and data-use permission.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime
import json

def stamp(v):
    """Require explicit timezone, preserving instant (never assume local clock)."""
    x = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if x.tzinfo is None or x.utcoffset() is None:
        raise ValueError("TIMEZONE_MISSING")
    return x

def preflight(deployments, opportunities, depth_times, max_gap_seconds):
    """Return aggregate QC only; do NOT return source rows or site identifiers.

    deployments: [{wetland, recorder, logger, start, end}, ...]
    opportunities: [{recorder, start, status}, ...] valid/missing/uncertain
    depth_times: [{logger, timestamp}, ...]; no original depth values
    max_gap_seconds: source-defined tolerance, no guessed default.
    """
    if not isinstance(max_gap_seconds, int) or max_gap_seconds < 0:
        raise ValueError("TOLERANCE_MUST_BE_SOURCE_DEFINED")
    if not deployments:
        raise ValueError("NO_DEPLOYMENTS")
    parsed = []
    for d in deployments:
        if not all(isinstance(d.get(k), str) and d[k].strip()
                   for k in ("wetland", "recorder", "logger", "start", "end")):
            raise ValueError("INCOMPLETE_SOURCE_CROSSWALK")
        a, b = stamp(d["start"]), stamp(d["end"])
        if not a < b:
            raise ValueError("INVALID_DEPLOYMENT_INTERVAL")
        parsed.append((d["wetland"], d["recorder"], d["logger"], a, b))
    by_recorder = defaultdict(list)
    for d in parsed:
        by_recorder[d[1]].append(d)
    for rec, ds in by_recorder.items():
        ordered = sorted(ds, key=lambda x: x[3])
        for a, b in zip(ordered, ordered[1:]):
            if b[3] < a[4]:
                raise ValueError("RECORDER_DOUBLE_ASSIGNED_SAME_TIME")

    loggers = defaultdict(list)
    for row in depth_times:
        if not isinstance(row.get("logger"), str):
            raise ValueError("DEPTH_LOGGER_MISSING")
        loggers[row["logger"]].append(stamp(row["timestamp"]))
    loggers = {k: sorted(v) for k, v in loggers.items()}
    counts = Counter()
    wetland_good = set()
    recorded_wetlands = set()
    recorder_n = len(by_recorder)
    for event in opportunities:
        rec, status = event.get("recorder"), event.get("status")
        if status not in ("VALID", "MISSING", "UNCERTAIN"):
            raise ValueError("UNRECOGNISED_AUDIO_OPPORTUNITY_STATUS")
        t = stamp(event["start"])
        active = [d for d in by_recorder.get(rec, []) if d[3] <= t < d[4]]
        if len(active) != 1:
            counts["unmapped_or_out_of_deployment"] += 1
            continue
        wet, _, logger, _, _ = active[0]
        recorded_wetlands.add(wet)
        counts["opportunities_in_deployment"] += 1
        counts["status_" + status] += 1
        if status != "VALID":
            continue
        dts = loggers.get(logger, [])
        # A source-defined timestamp alignment tolerance, not a derived
        # exposure or a guess about water presence.
        matched = any(abs((x - t).total_seconds()) <= max_gap_seconds for x in dts)
        if matched:
            counts["valid_with_temporally_aligned_logger_timestamp"] += 1
            wetland_good.add(wet)
        else:
            counts["valid_without_aligned_logger_timestamp"] += 1
    return {
        "status": "SYNTHETIC_SCHEMA_PREFLIGHT_NOT_BIOLOGICAL_QA",
        "n_source_defined_deployment_rows": len(parsed),
        "n_distinct_recorder_ids": recorder_n,
        "n_distinct_declared_independent_wetland_ids": len({x[0] for x in parsed}),
        "n_distinct_wetlands_with_any_opportunity": len(recorded_wetlands),
        "n_distinct_wetlands_with_valid_audio_and_aligned_logger_time": len(wetland_good),
        "opportunity_counts": dict(sorted(counts.items())),
        "site_independence_source_authenticated": False,
        "local_water_depth_values_read": False,
        "frog_call_values_read": False,
        "source_rights_verified": False,
        "jae_RC6_changed": False,
    }

def tests():
    ds = [
      {"wetland":"W1","recorder":"R1","logger":"L1","start":"2025-01-01T00:00:00+00:00","end":"2026-01-01T00:00:00+00:00"},
      {"wetland":"W1","recorder":"R2","logger":"L1","start":"2025-01-01T00:00:00+00:00","end":"2026-01-01T00:00:00+00:00"},
      {"wetland":"W2","recorder":"R3","logger":"L2","start":"2025-01-01T00:00:00+00:00","end":"2026-01-01T00:00:00+00:00"},
    ]
    opp = [
      {"recorder":"R1","start":"2025-02-01T00:00:00+00:00","status":"VALID"},
      {"recorder":"R2","start":"2025-02-01T00:00:00+00:00","status":"VALID"},
      {"recorder":"R3","start":"2025-02-01T00:00:00+00:00","status":"VALID"},
      {"recorder":"R3","start":"2025-02-01T01:00:00+00:00","status":"MISSING"},
    ]
    logs = [{"logger":"L1","timestamp":"2025-02-01T00:00:00+00:00"},
            {"logger":"L2","timestamp":"2025-02-01T00:00:00+00:00"}]
    z = preflight(ds, opp, logs, max_gap_seconds=0)
    assert z["n_distinct_recorder_ids"] == 3
    assert z["n_distinct_declared_independent_wetland_ids"] == 2
    assert z["n_distinct_wetlands_with_valid_audio_and_aligned_logger_time"] == 2
    assert z["opportunity_counts"]["status_MISSING"] == 1
    assert z["opportunity_counts"]["valid_with_temporally_aligned_logger_timestamp"] == 3
    assert not z["site_independence_source_authenticated"]
    for label, bad in (
        ("double_recorder", [*ds, {"wetland":"W3","recorder":"R1","logger":"L3",
                                   "start":"2025-02-01T00:00:00+00:00","end":"2025-05-01T00:00:00+00:00"}]),
        ("missing_tz", [dict(ds[0], start="2025-01-01T00:00:00"), *ds[1:]])
    ):
        try:
            preflight(bad, opp, logs, 0)
        except ValueError:
            pass
        else:
            raise AssertionError(label + " passed incorrectly")
    q = preflight(ds, opp, [], 0)
    assert q["n_distinct_wetlands_with_valid_audio_and_aligned_logger_time"] == 0
    try:
        preflight(ds, opp, logs, None)
    except ValueError as ex:
        assert str(ex) == "TOLERANCE_MUST_BE_SOURCE_DEFINED"
    else:
        raise AssertionError("non-source-defined timestamp tolerance accepted")
    safe = json.dumps(z)
    assert "W1" not in safe and "R1" not in safe and "L1" not in safe
    print(json.dumps(z, sort_keys=True))
    print("PASS: synthetic recorder≠wetland, missed visits, logger gaps, overlap and timezone fail-closed")

if __name__ == "__main__":
    tests()
