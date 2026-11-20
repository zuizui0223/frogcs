#!/usr/bin/env python3
"""Build a restricted-use PRE-DEPOSIT, model-only archive candidate.

Intentionally EXCLUDES all NAAMP site/route observations, independent INBO/USGS
records, sensitive locality vouchers, GBIF occurrence rows, original remote-
sensing rasters and source G4 site geometry. No source redistribution license,
DOI, author consent or journal peer-review access is implied.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = [
    *(f"research/results/g12_abc_pom_prior_20261107/original_20k/shard_{i:02d}.csv.gz" for i in range(8)),
    "research/results/g12_abc_pom_prior_20261107/source_receipt/r2_original_source_receipt.json",
    "research/results/g8_27rate_paired_20261107/audited/g8_all_source_rate_context_paired.csv.gz",
    "research/results/g8_27rate_paired_20261107/audited/g8_full_27rate_compatibility_abundance_summary.csv",
    "research/results/g8_27rate_paired_20261107/audited/g8_completion_receipt.json",
    "research/results/g11_disjoint_holdout_20261107/audited/g11_disjoint_full_82944_source_scenarios.csv.gz",
    "research/results/g11_disjoint_holdout_20261107/audited/g11_disjoint_20736_matched_source_rate_context.csv.gz",
    "research/results/g11_disjoint_holdout_20261107/audited/g11_final_independent_validation_receipt.json",
    "research/results/g11_disjoint_holdout_20261107/audited/g11_frozen_structure_selection.json",
    "research/results/g13_abc_structure_null_20261107/G13_4999_exact_stratum_permutation_null.csv.gz",
    "research/results/g13_abc_structure_null_20261107/G13_source_audit_receipt.json",
    "research/results/g10_standardized_sign_benefit_20261107/g10_standardized_comparisons.csv",
    "research/results/submission_frozen_sources_20261106/P1/P1_4timing_x_4vegetation_source_rates.csv",
    "research/results/p1_vegetation_benefit_20261106/p1_all_256_background_decompositions.csv",
    "research/results/p1_vegetation_benefit_20261106/p1_decomposition_receipt.json",
    "research/results/frog_arrival_20261109/scenarios.csv.gz",
    "research/results/frog_arrival_20261109/summary.csv",
    "research/results/frog_arrival_20261109/validation.json",
]
CODE = [
    "research/scripts/final_mechanism_common.py",
    "research/scripts/run_g8_27rate_paired_factorial.py",
    "research/scripts/audit_g8_27rate_paired_factorial.py",
    "research/scripts/run_g11_disjoint_structure_27rate.py",
    "research/scripts/audit_g11_disjoint_structure_27rate.py",
    "research/scripts/run_P1_arrival_duration_plant2x2_true80_20261105.py",
    "research/scripts/audit_P1_arrival_duration_plant2x2_true80_20261105.py",
    "research/scripts/p1_vegetation_benefit_decomposition.py",
    "research/scripts/frog_arrival_p1.py",
    "research/scripts/plot_frog_arrival_p1.py",
    "research/scripts/g13_abc_pom_conditional_structure_null.py",
    "research/scripts/audit_submission_claims_20261105.py",
]
ENVIRONMENT_WORKFLOWS = [
    ".github/workflows/research_g8_27rate_paired_factorial.yml",
    ".github/workflows/research_g11_disjoint_structure_holdout.yml",
    ".github/workflows/research_P1_isolated_stage_true80.yml",
    ".github/workflows/research_g13_abc_conditional_structure_null.yml",
]
DOCUMENTATION = [
    "editorial/MAIN_TEXT_CD_ECOLOGY_LETTERS_2026-11-09.md",
    "editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md",
    "editorial/REFERENCES_R1_R4_P1_G6_2026-11-06.md",
    "editorial/REFERENCES_R1_R4_P1_G6_2026-11-06.bib",
    "editorial/EL_PRIMARY_LITERATURE_AND_NOVELTY_AUDIT_2026-11-09.md",
    "submission/ecology_letters_20261108/CLAIM_EVIDENCE_REVIEWER_CHECKLIST_20261109.md",
    "submission/ecology_letters_20261108/DATA_CODE_DOI_ARCHIVE_PREFLIGHT_20261109.md",
    "submission/ecology_letters_20261108/ZENODO_PRIVATE_REVIEW_AND_AUTHOR_ACTIONS_20261109.md",
]
# No G4 original site geometry, no site-level NAAMP response data, and no
# source raw field data in this model-only candidate.
EXPLICIT_EXCLUSIONS = [
    "research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz",
    "research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz",
    "research/results/naamp_species_sensitivity_20261109/",
    "research/results/naamp_shared_site_pair_20261109/",
    "research/results/public_larval_overlap_20261109/",
    "research/results/part2_inbo_hyla_g1/",
    "research/results/g18_USGS_original_stage_observation_20261108/",
    "G4_all_4248_site_source_tertile_assignments.csv.gz",
    "WorldClim / EarthEnv original rasters, GBIF occurrence rows, Odonata checklist PDF",
]

README = """# Ecology Letters frogcs MODEL-ONLY candidate (NOT a finished public data deposit)

This ZIP contains the original *synthetic stage-structured food-web* source
results, computation/verification scripts and the manuscript/source-evidence
documents selected at the stated Git commit. It does NOT contain the original
4,248-site NAAMP survey observations, landscape cells, GBIF occurrences,
independent stage-survey raw rows, localities or remote-sensing rasters.

Scientific scope:
* Model R2: 20,000 original stage×rate proposals, acceptance of 4 model-native signs
* G8/G11: paired original 27 hypothetical rates, two disjoint 256 model structures
* G10/G13: conditional standardized controls and structural null
* P1: original salamander arrival × duration, vegetation 2×2 counterfactuals
* 11/9 exploratory frog-arrival offsets and original model replay
This is synthetic-model output. It does not demonstrate natural predation, real
frog hatch timing, or a calibrated adult-chorus-to-tadpole density relationship.

Reproduction depends on the upstream original catalog/input generation and the
separate USGS NAAMP, EarthEnv, WorldClim and GBIF records with their own rights.
The R5 full 4,800-virtual-observer outcome backup and G4 site-geometry source
are preserved privately for author review; they are NOT in this model-only ZIP.

Filenames and SHA256 values for all included files are in MANIFEST_SHA256.tsv.
COLUMN_DICTIONARY_AUTHOR_COMPLETION_REQUIRED.tsv lists the original CSV
headers with their scientific meanings and units intentionally left PENDING.
These must be completed from original variable definitions before depositing.
Original execution workflow YAML files are included as environment provenance,
not proof that this candidate is independently turnkey-reproducible.
See DEPOSIT_LIMITATIONS.json and SOURCE_DOI_ACCESS.md before public distribution.

IMPORTANT: This is a pre-deposit REVIEW CANDIDATE, NOT a licensed public
repository release, not Zenodo/Dryad submission, not a real project DOI, and
not proof of all coauthors' agreement. The project owner/coauthors must decide
the appropriate license, screen original rights and confirm a complete
accessible external archive before Ecology Letters submission.
"""

DOI_SOURCE_INFO = """# Independently original publisher data and follow-up access

- NAAMP Foreman et al. (2017), USGS DOI 10.5066/F7G44NG0.
- INBO adult calling (GBIF dataset DOI 10.15468/d4bu8j) and larval surveys
  (10.15468/swgure); supporting S22 observations, not source-model rates.
- USGS G18 Glorioso & Waddle (2025), DOI 10.5066/P9T71JCO.
- WorldClim 2.1: Fick & Hijmans 2017, DOI 10.1002/joc.5086.
- EarthEnv Consensus Land Cover v1: Tuanmu & Jetz 2014, DOI 10.1111/geb.12182.
- GBIF study acquisition used occurrence/search API (2026-10-26), 60
  independently attributed source datasets; no study-specific GBIF download
  DOI was issued. Provider rights are heterogeneous, see the main repository
  source provenance and attribution table.
- R5 original complete observer outcomes: original GitHub Actions
  #42446291543 artifact 13603733316, repaired aggregate #42446992844
  artifact 13603674015. Both are excluded from this public-model-only
  staging ZIP and independently preserved for author review.

No original third-party source data are redistributed with this candidate.
"""

FORBIDDEN_PATHS = (
    "/naamp_three_guild_occurrence/", "/naamp_remote_vegetation_20261026/",
    "/naamp_species_sensitivity_20261109/", "/naamp_shared_site_pair_20261109/",
    "/public_larval_overlap_20261109/", "/part2_inbo_hyla_g1/",
    "/g18_USGS_original_stage_observation_20261108/",
)
FORBIDDEN_COLUMNS = {
    "site", "site_id", "route", "route_id", "lat", "latitude",
    "long", "longitude", "locality", "locality_id", "decimalLatitude",
    "decimalLongitude", "gbifid", "occurrenceid"
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def test_csv_schema(path: str) -> str | None:
    if not path.endswith((".csv",".csv.gz")):
        return None
    p = ROOT/path
    openf = gzip.open if path.endswith(".gz") else open
    with openf(p, "rt", encoding="utf-8", newline="") as stream:
        head = next(csv.reader(stream))
    hits=sorted(set(head)&FORBIDDEN_COLUMNS)
    if hits:
        raise ValueError(f"Field-site/spatial/sensitive schema unexpectedly present in model-only result {path}: {hits}")
    return ",".join(head)

def main(archive:Path,receipt:Path) -> None:
    entries=[]
    sets={
        "generated_model_results":RESULTS,
        "analysis_and_audit_code":CODE,
        "original_execution_workflows":ENVIRONMENT_WORKFLOWS,
        "source_documentation":DOCUMENTATION,
    }
    assert len(set(RESULTS+CODE+ENVIRONMENT_WORKFLOWS+DOCUMENTATION))==sum(map(len,sets.values()))
    for label,files in sets.items():
        for rel in files:
            assert rel.startswith(("research/results/","research/scripts/","editorial/","submission/",".github/workflows/"))
            assert not any(token in rel for token in FORBIDDEN_PATHS),rel
            p=ROOT/rel
            if not p.is_file():
                raise FileNotFoundError(f"Archival model-only original source missing: {rel}")
            schema=test_csv_schema(rel)
            entries.append({
                "section":label,"path":rel,"bytes":p.stat().st_size,
                "sha256":sha(p.read_bytes()),"schema":schema
            })
    meta={
      "status":"MODEL_ONLY_PREDEPOSIT_SOURCE_PARTITION_QA_PASS_NOT_PUBLIC_ARCHIVED",
      "head_commit":os.getenv("GITHUB_SHA","unknown_local_commit"),
      "project_doi_issued":False,"public_distribution_authorized":False,
      "third_party_redistribution_cleared":False,"all_author_submitting_approval":False,
      "journal_submission_completed":False,
      "original_simulations_rerun":False,
      "included_files":len(entries),
      "total_original_source_bytes":sum(e["bytes"] for e in entries),
      "selected_result_files":len(RESULTS),"selected_code_files":len(CODE),
      "documentation_files":len(DOCUMENTATION),
      "original_execution_workflows":len(ENVIRONMENT_WORKFLOWS),
      "column_dictionary_author_verified":False,
      "complete_units_and_data_definitions_included":False,
      "site_level_or_coordinate_raw_records_exported":False,
      "missing_elements":[
         "Third-party-data rights-cleared source observations and geospatial inputs",
         "Exact original R5 observer outcomes in separately private author backup",
         "Final authorship approval and external peer-review-access DOI",
         "Source variable dictionaries, pinned environment and complete external retrieval procedure before claiming independent reproduction"
      ],
      "excluded_sources":EXPLICIT_EXCLUSIONS,
      "files":entries,
    }
    # Do not invent variable definitions: expose every original CSV column
    # to coauthors in an explicit review-required metadata table.
    dictionary=[("source_file","column_name","column_meaning_EN","unit","author_verified")]
    for e in entries:
        if e["schema"]:
            for col in e["schema"].split(","):
                dictionary.append((e["path"],col,"[AUTHOR DEFINE]","[AUTHOR VERIFY]","NO"))
    meta["unverified_column_dictionary_rows"]=len(dictionary)-1
    dictionary_text=io.StringIO()
    dw=csv.writer(dictionary_text,dialect="excel-tab",lineterminator="\n")
    dw.writerows(dictionary)
    # Keep canonical ZIP layout and an inspectable manifest in archive root.
    index="section\tpath\tbytes\tsha256\n" + "\n".join(
        f"{e['section']}\t{e['path']}\t{e['bytes']}\t{e['sha256']}" for e in entries
    )+"\n"
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        z.writestr("README_MODEL_ONLY_PREDEPOSIT.md",README)
        z.writestr("SOURCE_DOI_ACCESS.md",DOI_SOURCE_INFO)
        z.writestr("MANIFEST_SHA256.tsv",index)
        z.writestr("COLUMN_DICTIONARY_AUTHOR_COMPLETION_REQUIRED.tsv",dictionary_text.getvalue())
        z.writestr("DEPOSIT_LIMITATIONS.json",json.dumps({
           k:v for k,v in meta.items() if k!="files"
        },ensure_ascii=False,indent=2)+"\n")
        for e in entries:
            rel=e["path"]
            z.write(ROOT/rel,arcname="SOURCE_FILES/"+rel)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(entries)+5
        assert "research/results/naamp_three_guild_occurrence" not in " ".join(z.namelist())
    meta["archive_bytes"]=archive.stat().st_size
    meta["archive_sha256"]=sha(archive.read_bytes())
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("EL_MODEL_ONLY_ARCHIVE_CANDIDATE_SOURCE_SHA256_PASS",
          len(entries),"source_files",archive.stat().st_size,"ZIP_bytes",
          "no_original_biology_rerun",flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--receipt",required=True,type=Path)
    args=ap.parse_args()
    main(args.out,args.receipt)
