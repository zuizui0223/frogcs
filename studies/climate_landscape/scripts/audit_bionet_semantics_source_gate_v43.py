#!/usr/bin/env python3
"""v4.3 synthetic, fail-closed NSW BioNet → frog-chorus data-contract checks.

Authoritative semantic source: NSW BioNet Species Sighting Data Standard 6.3
(2026-02), NOT an observation dump. No external/API calls, secrets or raw frog
records. The script never converts a sighting-only table into a visit census.
"""
from __future__ import annotations
import json

SOURCE = ("NSW BioNet Species Sighting Data Standard 6.3, February 2026;"
          " https://www.environment.nsw.gov.au/publications/"
          "bionet-species-sighting-data-standard")
FORBIDDEN_DEFAULT_FIELDS = {"abundanceScore", "individualCount",
                            "reproductiveCondition", "measurementValue"}


def resolve_visit_key(row):
    """eventID and visitID are aliases, not independent replication."""
    ev = str(row.get("eventID") or "").strip()
    visit = str(row.get("visitID") or "").strip()
    if ev and visit and ev != visit:
        raise ValueError("eventID and visitID conflict (duplicate census-key fields)")
    return ev or visit or None


def classify_occurrence(row, *, verified_protocol=False):
    """A recorded taxon status is NOT automatically a frog acoustic CI state."""
    status = str(row.get("occurrenceStatus") or "").strip()
    if status == "Present":
        return "RECORDED_TAXON_PRESENT_CALL_STATE_UNSPECIFIED"
    if status == "Absent":
        return "EXPLICIT_RECORDED_TAXON_ABSENCE_CALL_STATE_UNSPECIFIED"
    if not status:
        return "UNKNOWN_NO_RECORDED_TAXON_STATUS"
    raise ValueError("unknown source occurrence status; look up controlled vocabulary")


def authorize_calling_index_map(*, proposed_field, original_frog_dictionary=False,
                                verified_visit_denominator=False):
    if proposed_field in FORBIDDEN_DEFAULT_FIELDS:
        raise ValueError("generic BioNet field is not the original amphibian call category")
    if not original_frog_dictionary:
        raise ValueError("original 5-minute frog categorical field dictionary not authenticated")
    if not verified_visit_denominator:
        raise ValueError("source-authoritative complete survey opportunity denominator missing")
    if proposed_field not in {"source_original_frog_call_category"}:
        raise ValueError("original frog category field not explicitly mapped")
    return "SOURCE_ORIGINAL_FROG_CATEGORY_ADMISSIBLE_NOT_YET_VALIDATED"


def authorize_effort(row):
    value = row.get("samplingEffortValue")
    unit = row.get("samplingEffortUnit")
    if value in (None, "") or unit in (None, ""):
        raise ValueError("no complete effort value/unit pair")
    if str(unit) not in ("Minutes", "Hours", "Person Hours", "Trap Nights",
                         "Units Unknown"):
        raise ValueError("effort unit unsupported without original dictionary")
    try:
        value = float(value)
    except (TypeError, ValueError) as ex:
        raise ValueError("non-numeric effort") from ex
    if not (value > 0 and value < float("inf")):
        raise ValueError("invalid effort magnitude")
    if unit == "Minutes":
        return {"effort_minutes": value, "amphibian_method_verified": False}
    if unit == "Hours":
        return {"effort_minutes": value * 60, "amphibian_method_verified": False}
    raise ValueError("unit is valid BioNet unit but cannot establish frog 5-min audio effort")


def admit_recruitment_link(*, real_metamorph_followup=False,
                           measured_hydroperiod=False,
                           independently_verified_site_crosswalk=False):
    if not all((real_metamorph_followup, measured_hydroperiod,
                independently_verified_site_crosswalk)):
        raise ValueError("no verified same-site metamorph and hydrology linkage")
    return "DESIGN_ELIGIBLE_IF_SAMPLES_AND_ABSENCE_MANIFEST_ARE_VALID"


def self_test():
    # Aliased census columns must not double count. One-sided source fields
    # are permitted only as a putative key, NOT proof all visits were sampled.
    assert resolve_visit_key({"eventID": "E7", "visitID": "E7"}) == "E7"
    assert resolve_visit_key({"visitID": "E7"}) == "E7"
    assert resolve_visit_key({}) is None

    # Explicit Absent is recorded status, not a manufactured calling zero.
    assert classify_occurrence({"occurrenceStatus": "Absent"}).startswith("EXPLICIT_")
    assert "CALL_STATE_UNSPECIFIED" in classify_occurrence(
        {"occurrenceStatus": "Present"})
    assert classify_occurrence({}) == "UNKNOWN_NO_RECORDED_TAXON_STATUS"

    bad = [
        lambda: resolve_visit_key({"eventID": "E7", "visitID": "E8"}),
        lambda: classify_occurrence({"occurrenceStatus": "Probably"}),
        lambda: authorize_calling_index_map(proposed_field="abundanceScore",
                    original_frog_dictionary=True, verified_visit_denominator=True),
        lambda: authorize_calling_index_map(
                    proposed_field="source_original_frog_call_category",
                    original_frog_dictionary=False, verified_visit_denominator=True),
        lambda: authorize_calling_index_map(
                    proposed_field="source_original_frog_call_category",
                    original_frog_dictionary=True, verified_visit_denominator=False),
        lambda: authorize_effort({"samplingEffortValue": 5}),
        lambda: authorize_effort({"samplingEffortValue": 5, "samplingEffortUnit": "Trap Nights"}),
        lambda: admit_recruitment_link(real_metamorph_followup=True,
                        measured_hydroperiod=False,
                        independently_verified_site_crosswalk=True),
    ]
    for i, fn in enumerate(bad):
        try:
            fn()
        except ValueError:
            pass
        else:
            raise AssertionError(f"Unsafe source mapping fixture {i} accepted")

    good = authorize_calling_index_map(
        proposed_field="source_original_frog_call_category",
        original_frog_dictionary=True, verified_visit_denominator=True)
    assert good.startswith("SOURCE_ORIGINAL")
    assert authorize_effort({"samplingEffortValue": "5",
                             "samplingEffortUnit": "Minutes"})["effort_minutes"] == 5.0

    print(json.dumps({
        "result": "PASS",
        "source": SOURCE,
        "synthetic_checks": "visitID/eventID alias, explicit-absence semantics, "
                            "amphibian CI disallowed plant abundance, "
                            "verified acoustic protocol/denominator, effort and hydroperiod join",
        "negative_fixtures": len(bad),
        "real_amphibian_records_read": False,
        "new_ecological_effect_estimated": False,
        "main_rc6_unchanged": True
    }, sort_keys=True))


if __name__ == "__main__":
    self_test()
