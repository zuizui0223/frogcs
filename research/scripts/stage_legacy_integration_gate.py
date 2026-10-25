#!/usr/bin/env python3
"""frogcs-only prospective integration preflight.

Reads *existing* RC6 and independent NPS summary receipts without re-fitting.
Optionally audits an externally verified same-pond stage/effort coverage CSV.
Does not inspect acoustic/tadpole outcome counts from that CSV or infer predation.
No network downloads, imports beyond Python's standard library, or external writes
unless --out is explicitly given.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from io import StringIO
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research/STAGE_LEGACY_INTEGRATION_MANIFEST_V1.json"
STAGES = {
    "adult_call", "egg", "early_tadpole", "late_tadpole",
    "overwintered_tadpole_verified", "egg_survival", "metamorph",
    "juvenile", "adult", "salamander_larva", "odonate_nymph",
    "fish_predator",
}
REQUIRED = {
    "observation_id", "source_id", "wetland_id", "verified_wetland",
    "taxon", "year", "date", "stage", "effort", "protocol",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict:
    require(path.is_file(), f"Missing pinned source/manifest: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_numeric(observed, expected, label: str) -> float:
    number = float(observed)
    require(math.isfinite(number), f"Nonfinite source readout: {label}")
    require(math.isclose(number, float(expected), rel_tol=0.0, abs_tol=1e-10),
            f"Frozen source readout changed: {label} {number} != {expected}")
    return number


def validate_receipts(manifest: dict) -> dict:
    require(manifest["repository"] == "zuizui0223/frogcs",
            "Integration cannot be owned by a different repository")
    source = manifest["frozen_rc6"]
    require(source["source_ref"] == "release/jae-multisite-rc6",
            "Frozen release authority changed")
    require(source["submission_ref"] == "submission/jae-multisite-v6",
            "Frozen submission authority changed")
    protected = source["immutable_scientific_paths"]
    for section in ("paper/", "submission/", "provenance/", "scripts/naamp/"):
        require(section in protected, f"Frozen source directory not protected: {section}")
    require(all(str(Path(m["result"])).startswith(("provenance/", "research/results/"))
                for m in manifest["source_modules"] if "result" in m),
            "Integration result path must remain within frogcs")
    ids = [s["id"] for s in manifest["source_modules"]]
    require(len(ids) == len(set(ids)), "Duplicate source module id")
    requires = {"naamp_rc6", "nps_glkn", "carroll_8pond",
                "globi_stage", "hydroperiod_observed", "larval_predation_survival"}
    require(requires <= set(ids), "Missing source module")

    rc6 = read_json(ROOT / source["source_result"])
    targets = source["frozen_readout"]
    count_pairs = check_numeric(
        rc6["population"]["matched_pairs"], targets["population_matched_pairs"],
        "RC6 matched pairs")
    count_hist = check_numeric(
        rc6["population"]["principal_history_pairs"],
        targets["principal_history_pairs"], "RC6 history pairs")
    measure = rc6["principal_within_taxon_comparator"]
    for key, field in (
        ("observed_beta", "spatial_observed"),
        ("predicted_beta", "spatial_null"),
        ("conditional_residual", "spatial_residual"),
    ):
        check_numeric(measure[key], targets[field], f"RC6 {field}")
    check_numeric(
        rc6["historical_site_structure"]["prior_strong_site_to_wet_ci2_ci3_beta"],
        targets["prior_site_beta"], "RC6 strictly prior site beta")

    nps = next(m for m in manifest["source_modules"] if m["id"] == "nps_glkn")
    nps_result = read_json(ROOT / nps["result"])
    require(nps_result["informative_site_taxon_year_rows"] ==
            nps["expected_informative_rows"], "NPS informative sample changed")
    nps_beta = check_numeric(
        nps_result["adjusted_strict_prior_strong"]["own_prior_strong_beta"],
        nps["expected_adjusted_beta"], "NPS adjusted same-species site-history beta")

    require(not manifest["prior_claims"]["NAAMP_predator_proxy_validated"],
            "Proxy not yet validated from a co-located pond-stage panel")
    require(not manifest["prior_claims"]["drought_larval_reset_observed"],
            "No independently verified joint drought-reset evidence")
    require(not manifest["prior_claims"]["stage_predation_population_effect_identified"],
            "No measured predation mechanism available")
    return {
        "rc6_science_lock": "MATCHES_FROZEN_READOUT_NO_REFIT",
        "rc6_matched_pairs": int(count_pairs),
        "rc6_principal_history_pairs": int(count_hist),
        "rc6_conditional_spatial_residual": targets["spatial_residual"],
        "nps_independent_acoustic_history": "MATCHES_SOURCE_RECEIPT",
        "nps_informative_site_taxon_year_rows": nps["expected_informative_rows"],
        "nps_adjusted_history_beta": nps_beta,
        "scientific_conclusion": "ACOUSTIC_SPATIAL_AND_HISTORY_RESULTS_ONLY",
    }


def audit_coverage(reader: csv.DictReader) -> dict:
    """Response-blind stage/effort coverage. NO outcomes or inferred zeros read."""
    require(reader.fieldnames is not None, "Empty coverage CSV")
    missing = REQUIRED - set(reader.fieldnames)
    require(not missing, f"Missing coverage columns: {sorted(missing)}")
    seen = set()
    observed = []
    for idx, row in enumerate(reader, 2):
        obs = row["observation_id"].strip()
        require(obs and obs not in seen, f"Missing/duplicate ID at row {idx}")
        seen.add(obs)
        for field in ("source_id", "wetland_id", "taxon", "protocol"):
            require(row[field].strip(), f"Missing {field} at row {idx}")
        require(row["verified_wetland"].strip().lower() in ("true", "1"),
                f"Unverified physical pond at row {idx}; no joins allowed")
        yr = int(row["year"])
        d = date.fromisoformat(row["date"].strip())
        require(d.year == yr, f"Year/date mismatch at row {idx}")
        effort = float(row["effort"])
        require(math.isfinite(effort) and effort > 0,
                f"Nonpositive/nonfinite measurement effort at row {idx}")
        stage = row["stage"].strip()
        require(stage in STAGES, f"Uncalibrated stage label {stage} at row {idx}")
        observed.append((row["wetland_id"].strip(),
                         row["taxon"].strip(), yr, stage, row["source_id"].strip()))
    require(observed, "Coverage CSV contains no measured survey events")
    prior_calls = {(pond, taxon, yr)
                   for pond, taxon, yr, stage, _ in observed if stage == "adult_call"}
    winter_verified = {(pond, taxon, yr)
                       for pond, taxon, yr, stage, _ in observed
                       if stage == "overwintered_tadpole_verified"}
    eggs = {(pond, taxon, yr)
            for pond, taxon, yr, stage, _ in observed if stage == "egg"}
    egg_survival = {(pond, taxon, yr)
                    for pond, taxon, yr, stage, _ in observed
                    if stage == "egg_survival"}
    proxy_pairs = {pair for pair in winter_verified
                   if (pair[0], pair[1], pair[2] - 1) in prior_calls}
    # Co-presence in a pond/year is only a coverage candidate. It does NOT
    # demonstrate stage overlap in days, predation, or recruitment.
    candidate_exposure = {
        (p, y) for p, _, y in winter_verified
        if any(p == pond and y == yr and taxon != ptaxon
               for pond, taxon, yr in eggs
               for pp, ptaxon, yy in winter_verified
               if pp == p and yy == y)
    }
    # Better explicit pair matching for distinct predator/prey species.
    candidate_exposure = {
        (pond, yr) for pond, taxon, yr in winter_verified
        if any(p == pond and y == yr and prey != taxon
               for p, prey, y in eggs)
    }
    stages = sorted(set(r[3] for r in observed))
    return {
        "kind": "SOURCE_BLIND_COVERAGE_ONLY_NO_OUTCOMES_OPENED",
        "events_with_verified_physical_wetland": len(observed),
        "distinct_wetlands": len({r[0] for r in observed}),
        "distinct_taxa": len({r[1] for r in observed}),
        "distinct_years": len({r[2] for r in observed}),
        "distinct_provenance_sources": len({r[4] for r in observed}),
        "observed_stage_labels": stages,
        "same_pond_same_taxon_prior_year_call_to_verified_winter_larva_coverage": len(proxy_pairs),
        "pond_years_with_winter_larva_and_other_taxon_eggs_NOT_ATTACKS": len(candidate_exposure),
        "pond_taxon_years_with_egg_survival_measurements": len(egg_survival),
        "proxy_model_fitted": False,
        "predation_mechanism_identified": False,
        "dry_reset_effect_tested": False,
        "note": "Only dates/taxonomy/effort and validated waterbody IDs read; co-reporting does not establish predation or breeding success.",
    }


def status_report(manifest: dict, coverage=None) -> dict:
    receipt = validate_receipts(manifest)
    gates = {g["id"]: g["status"] for g in manifest["gates"]}
    if coverage is not None:
        gates["G0"] = ("COVERAGE_PRESENT_NEEDS_INDEPENDENT_SOURCE_VALIDATION"
                       if coverage["same_pond_same_taxon_prior_year_call_to_verified_winter_larva_coverage"]
                       else "COVERAGE_CHECKED_NO_CALIBRATION_PAIRS")
    return {
        "programme": manifest["schema_version"],
        "repository": manifest["repository"],
        "branch_role": "FUTURE_INTEGRATION_ONLY_NOT_RC6_SUBMISSION",
        "existing_receipts": receipt,
        "stage_pond_coverage": coverage,
        "gates": gates,
        "mechanistic_inference_authorized": False,
        "integrated_paper_ready": False,
    }


def self_test() -> None:
    fieldnames = [
        "observation_id", "source_id", "wetland_id", "verified_wetland",
        "taxon", "year", "date", "stage", "effort", "protocol",
    ]
    header = ",".join(fieldnames)
    synthetic_rows = [
        "1,TEST,pond01,true,green_frog,2020,2020-06-15,adult_call,1,recorder",
        "2,TEST,pond01,true,green_frog,2021,2021-03-14,overwintered_tadpole_verified,1,net",
        "3,TEST,pond01,true,wood_frog,2021,2021-03-16,egg,1,egg_mass",
        "4,TEST,pond01,true,wood_frog,2021,2021-04-20,egg_survival,1,egg_mass",
    ]
    csv_text = header + "\n" + "\n".join(synthetic_rows) + "\n"
    coverage = audit_coverage(csv.DictReader(StringIO(csv_text)))
    require(coverage["same_pond_same_taxon_prior_year_call_to_verified_winter_larva_coverage"] == 1,
            "Synthetic lagged proxy coverage failure")
    require(coverage["pond_years_with_winter_larva_and_other_taxon_eggs_NOT_ATTACKS"] == 1,
            "Synthetic egg/overwintered-tadpole same-pond coverage failure")
    failed = False
    try:
        audit_coverage(csv.DictReader(StringIO(
            csv_text.replace("pond01,true,wood_frog", "pond01,false,wood_frog")
        )))
    except ValueError as exc:
        failed = "Unverified physical pond" in str(exc)
    require(failed, "Unverified pond should fail closed")
    failed = False
    try:
        audit_coverage(csv.DictReader(StringIO(
            csv_text.replace("2021-03-14", "2020-03-14")
        )))
    except ValueError as exc:
        failed = "Year/date mismatch" in str(exc)
    require(failed, "Year/date mismatch should fail closed")
    print("SELF_TEST_PASS: synthetic coverage and fail-closed geography/time checks")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path,
                        help="Response-blind same-pond stage coverage CSV (no outcomes used)")
    parser.add_argument("--out", type=Path, help="Optional readiness JSON output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    manifest = read_json(MANIFEST)
    coverage = None
    if args.panel:
        with args.panel.open("r", encoding="utf-8-sig", newline="") as handle:
            coverage = audit_coverage(csv.DictReader(handle))
    report = status_report(manifest, coverage)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
