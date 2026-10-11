#!/usr/bin/env python3
"""v5.6: official CEWH MDMS attribute equality counts, never identities/coordinates.

The pre-read contract is:
studies/climate_landscape/V5_6_MDMS_CANDIDATE_PARENT_UNIT_ATTRIBUTE_CONTRACT.md
This is NOT a parent-wetland crosswalk or frog-outcome analysis.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import urllib.error
import urllib.parse

import audit_mdms_flowmer_exact_site_labels_v55 as v55

EXPECTED_MDMS_SHA256 = "2fe0672aec63b032594a14d125c644461284ed2099b793e390f6df77d274f9d2"
FIELDS = ("DESCRIPTIO", "ANAE_TYPE", "DATATYPENA", "SystemType",
          "SAMPLECOUN", "COMMENTS", "POINT_CATE", "PROGRAM")
EXPECTED = {"Gwydir River System": 6, "Lachlan River System": 14,
            "Murrumbidgee River": 28}
EXPECTED_MDMS_KEYS = {
    "ANAE_TYPE", "COMMENTS", "DATATYPENA", "DESCRIPTIO", "FID",
    "LATITUDE", "LONGITUDE", "NAME", "NORTHING", "OBJECTID",
    "POINT_CATE", "PROGRAM", "SAMO_ID", "SAMPLECOUN", "SystemType",
}


def summarize(mdms: dict, frog: dict) -> dict:
    """Compute only safe, programme-aggregated equality summaries."""
    feats = mdms.get("features")
    if mdms.get("type") != "FeatureCollection" or not isinstance(feats, list) or len(feats) != 681:
        raise ValueError("UNEXPECTED_MDMS_SOURCE_FRAME")
    lookup = defaultdict(list)
    for index, f in enumerate(feats):
        if not isinstance(f, dict) or f.get("type") != "Feature":
            raise ValueError("INVALID_FEATURE")
        p = f.get("properties")
        if not isinstance(p, dict) or set(p) != EXPECTED_MDMS_KEYS:
            raise ValueError("UNEXPECTED_MDMS_ATTRIBUTE_SCHEMA")
        label = v55.norm(p.get("NAME"))
        if not label:
            raise ValueError("EMPTY_MDMS_LABEL")
        lookup[label].append(index)
    if len(lookup) != len(feats) or any(len(x) != 1 for x in lookup.values()):
        raise ValueError("DUPLICATE_MDMS_NAME")
    if frog.get("success") is not True:
        raise ValueError("INVALID_CKAN_PROJECTION")
    fr = frog.get("result")
    if not isinstance(fr, dict) or fr.get("total") != 673:
        raise ValueError("UNEXPECTED_FROG_ROW_COUNT")
    if {f.get("id") for f in fr.get("fields", [])} != {"Program", "SamplePoint"}:
        raise ValueError("UNAUTHORIZED_FROG_FIELDS")
    records = fr.get("records")
    if not isinstance(records, list) or len(records) != 673:
        raise ValueError("INCOMPLETE_FROG_PROJECTION")
    named = defaultdict(set)
    for r in records:
        if not isinstance(r, dict) or (set(r) - {"Program", "SamplePoint", "_id"}):
            raise ValueError("UNAUTHORIZED_FROG_ROW_DATA")
        prog = str(r.get("Program") or "").strip()
        label = v55.norm(r.get("SamplePoint"))
        if not prog or not label:
            raise ValueError("MISSING_FROG_LABEL")
        named[prog].add(label)
    if {prog: len(labels) for prog, labels in named.items()} != EXPECTED:
        raise ValueError("CHANGED_FROG_POINT_FRAME")
    if len(set.union(*named.values())) != 48:
        raise ValueError("CROSS_PROGRAM_POINT_LABEL_OVERLAP")
    for labels in named.values():
        if any(label not in lookup for label in labels):
            raise ValueError("UNMATCHED_FROG_POINT_NAME")

    group_summary = {}
    for prog, labels in sorted(named.items()):
        p = [feats[lookup[label][0]]["properties"] for label in sorted(labels)]
        by_field = {}
        for field in FIELDS:
            counts = Counter(v55.norm(x.get(field)) for x in p if v55.norm(x.get(field)))
            by_field[field] = {
                "n_nonmissing": sum(counts.values()),
                "n_distinct_nonempty": len(counts),
                "n_groups_size_2plus": sum(n > 1 for n in counts.values()),
                "n_points_in_groups_size_2plus": sum(n for n in counts.values() if n > 1),
                "largest_group_size": max(counts.values(), default=0)
            }
        group_summary[prog] = {
            "n_matched_official_MDMS_point_names": len(p),
            "aggregate_attribute_equality_only": by_field,
            "nonprogramme_fields_with_repeated_value_groups":
                [field for field in FIELDS if field != "PROGRAM"
                 and by_field[field]["n_groups_size_2plus"] > 0]
        }
    return {
        "status": "SOURCE_ATTRIBUTE_EQUALITY_ONLY_NOT_WETLAND_CROSSWALK",
        "source_mdms_sha256_required": EXPECTED_MDMS_SHA256,
        "n_MDMS_original_features": len(feats),
        "n_distinct_frog_public_point_labels": 48,
        "per_programme": group_summary,
        "semantics_of_MDMS_description_and_type_fields_verified": False,
        "physical_independent_wetland_units_verified": False,
        "prior_source_event_stability_verified": False,
        "original_larval_field_taxonomy_verified": False,
        "frog_response_outcome_values_accessed": False,
        "coordinates_or_individual_site_names_reported": False,
        "submitted_JAE_RC6_modified": False,
        "decision": "REQUEST_OFFICIAL_POINT_TO_WETLAND_UNIT_DICTIONARY_ONLY_IF_AUTHORIZED",
    }


def synthetic_test() -> None:
    """Extend the 48-point fixture without ever emitting synthetic site values."""
    fake = []
    records = []
    for prog, n in EXPECTED.items():
        for i in range(n):
            name = "SENSITIVE_TEST_LABEL_" + prog + str(i)
            p = {f: None for f in EXPECTED_MDMS_KEYS}
            p.update(NAME=name, SAMO_ID=str(i), PROGRAM=prog, DESCRIPTIO="PRIVATE_PARENT" if i < 2 else "PRIVATE_" + str(i))
            fake.append({"type": "Feature", "properties": p,
                         "geometry": {"type": "Point", "coordinates": [140 + i, -34]}})
            records.append({"Program": prog, "SamplePoint": name})
    # Pad unmatched official features to the original 681, with unique sensitive labels.
    for i in range(681 - len(fake)):
        p = {f: None for f in EXPECTED_MDMS_KEYS}
        p.update(NAME="UNMATCHED_PRIVATE_" + str(i), SAMO_ID=str(i))
        fake.append({"type": "Feature", "properties": p,
                     "geometry": {"type": "Point", "coordinates": [130, -30]}})
    # Pad additional source entries by repeating approved programme labels.
    while len(records) < 673:
        records.append(dict(records[0]))
    frog = {"success": True, "result": {
        "total": 673, "fields": [{"id": "Program"}, {"id": "SamplePoint"}], "records": records
    }}
    result = summarize({"type": "FeatureCollection", "features": fake}, frog)
    p = result["per_programme"]["Murrumbidgee River"]["aggregate_attribute_equality_only"]["DESCRIPTIO"]
    assert p["n_groups_size_2plus"] == 1 and p["largest_group_size"] == 2
    assert not result["physical_independent_wetland_units_verified"]
    text = json.dumps(result)
    assert "SENSITIVE" not in text and "PRIVATE" not in text and '"coordinates":' not in text
    assert "140" not in text
    fake[0]["properties"]["NAME"] = fake[1]["properties"]["NAME"]
    try:
        summarize({"type": "FeatureCollection", "features": fake}, frog)
    except ValueError as exc:
        assert str(exc) == "DUPLICATE_MDMS_NAME"
    else:
        raise AssertionError("DUPLICATE SOURCE LABEL ACCEPTED")
    print("PASS: synthetic same-description vs distinct-points test, fail-closed identity and zero data leakage")


def main() -> None:
    synthetic_test()
    outcome = {
        "status": "SOURCE_UNAVAILABLE",
        "contract": "studies/climate_landscape/V5_6_MDMS_CANDIDATE_PARENT_UNIT_ATTRIBUTE_CONTRACT.md",
        "original_biological_inference_gate": "NOT_VERIFIED",
        "no_frog_outcomes_or_coordinates_emitted": True,
    }
    try:
        meta, _ = v55.get(v55.BASE + "resource_show?" + urllib.parse.urlencode({"id": v55.MDMS_RESOURCE}), 400000)
        url = v55.source(meta)
        mdms, source_hash = v55.get(url, 1_200_000)
        if source_hash != EXPECTED_MDMS_SHA256:
            raise ValueError("SOURCE_HASH_CHANGED_STOP")
        frog, _ = v55.get(v55.BASE + "datastore_search?" + urllib.parse.urlencode({
            "resource_id": v55.FROG_RESOURCE, "limit": 1000, "fields": "Program,SamplePoint"
        }), 800000)
        outcome.update(summarize(mdms, frog))
    except urllib.error.HTTPError as exc:
        outcome.update(status="HTTP_SOURCE_UNAVAILABLE", http_status=exc.code)
    except (urllib.error.URLError, TimeoutError) as exc:
        outcome.update(status="NETWORK_SOURCE_UNAVAILABLE", error_type=type(exc).__name__)
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        outcome.update(status="SOURCE_FAILED_CLOSED", error_type=type(exc).__name__,
                       error_code=str(exc) if str(exc) in {
                         "SOURCE_HASH_CHANGED_STOP", "UNEXPECTED_MDMS_SOURCE_FRAME",
                         "UNEXPECTED_MDMS_ATTRIBUTE_SCHEMA", "CHANGED_FROG_POINT_FRAME",
                         "UNAUTHORIZED_FROG_FIELDS", "UNMATCHED_FROG_POINT_NAME",
                         "DUPLICATE_MDMS_NAME", "INCOMPLETE_FROG_PROJECTION",
                       } else "UNRECOGNIZED_SOURCE_VARIATION")
    out = Path("studies/climate_landscape/receipts/MDMS_CANDIDATE_PARENT_ATTRIBUTE_EQUALITY_V56.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outcome, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcome, sort_keys=True))


if __name__ == "__main__":
    main()
