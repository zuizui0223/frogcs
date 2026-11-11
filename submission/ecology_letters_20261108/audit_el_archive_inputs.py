#!/usr/bin/env python3
"""Source-file existence/hash receipt for an EL archival handoff.

Does NOT establish source licenses, create an external DOI, submit to a journal,
export species-location data, or rerun any scientific simulations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

# Original source objects / source audits required to evaluate the displayed
# macro / stage-model results, not a claim this list alone is the whole archive.
INPUTS={
    "naamp_observations":[
        "research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz",
        "research/results/naamp_remote_vegetation_20261026/network_rank_coefficients.csv",
        "research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz",
    ],
    "environment_and_occurrence_attributions":[
        "research/results/interaction_species_sdm_20261026/retrieval.json",
        "research/results/interaction_species_sdm_20261026/environment_receipts.json",
        "research/results/regional_species_pool_20261026/gbif_dataset_attribution.csv",
    ],
    "twenty_thousand_original_proposals":[
        *(f"research/results/g12_abc_pom_prior_20261107/original_20k/shard_{i:02d}.csv.gz" for i in range(8)),
        "research/results/g12_abc_pom_prior_20261107/source_receipt/r2_original_source_receipt.json",
    ],
    "g8_first_structures":[
        "research/results/g8_27rate_paired_20261107/audited/g8_all_source_rate_context_paired.csv.gz",
        "research/results/g8_27rate_paired_20261107/audited/g8_completion_receipt.json",
    ],
    "g11_disjoint_structures":[
        "research/results/g11_disjoint_holdout_20261107/audited/g11_disjoint_full_82944_source_scenarios.csv.gz",
        "research/results/g11_disjoint_holdout_20261107/audited/g11_final_independent_validation_receipt.json",
        "research/results/g11_disjoint_holdout_20261107/audited/g11_frozen_structure_selection.json",
    ],
    "g13_null_and_P1":[
        "research/results/g13_abc_structure_null_20261107/G13_source_audit_receipt.json",
        "research/results/g13_abc_structure_null_20261107/G13_4999_exact_stratum_permutation_null.csv.gz",
        "research/results/submission_frozen_sources_20261106/P1/P1_4timing_x_4vegetation_source_rates.csv",
        "research/results/p1_vegetation_benefit_20261106/p1_all_256_background_decompositions.csv",
        "research/results/p1_vegetation_benefit_20261106/p1_decomposition_receipt.json",
    ],
    "si_stage_bridge":[
        "research/results/part2_inbo_hyla_g1/observed_results.json",
        "research/results/g18_USGS_original_stage_observation_20261108/audited/G18_USGS_INDEPENDENT_STAGE_OBSERVATION_RESULT.json",
        "research/results/naamp_species_sensitivity_20261109/interaction_results.csv",
        "research/results/naamp_shared_site_pair_20261109/paired_coefficients.csv",
        "research/results/naamp_shared_site_pair_20261109/timing.csv",
        "research/results/public_larval_overlap_20261109/reviewed_paired_vouchers.csv",
        "research/results/public_larval_overlap_20261109/usgs_brookshire_crosswalk.csv",
    ],
    "si_frog_calendar_simulations":[
        "research/results/frog_arrival_20261109/scenarios.csv.gz",
        "research/results/frog_arrival_20261109/summary.csv",
        "research/results/frog_arrival_20261109/validation.json",
    ],
    "frozen_R5_protocol_and_reproduction_code":[
        "research/R5_VIRTUAL_ECOLOGIST_OBSERVABILITY_FROZEN_PROTOCOL_2026-11-08.md",
        "research/R5_OBSERVABILITY_FULL_VERIFIED_RESULT_2026-11-08.md",
        "research/scripts/r5_virtual_observer_frozen_20261108.py",
        "research/scripts/r5_reporting_only_dtype_repair_20261108.py",
    ],
    "source_code":[
        "research/scripts/final_mechanism_common.py",
        "research/scripts/run_g8_27rate_paired_factorial.py",
        "research/scripts/run_g11_disjoint_structure_27rate.py",
        "research/scripts/run_P1_arrival_duration_plant2x2_true80_20261105.py",
        "research/scripts/frog_arrival_p1.py",
        "research/scripts/audit_submission_claims_20261105.py",
        "submission/ecology_letters_20261108/build_cd_author_review.py",
    ],
    "manuscript_sources_and_frozen_figures":[
        "editorial/MAIN_TEXT_CD_ECOLOGY_LETTERS_2026-11-09.md",
        "editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md",
        "editorial/REFERENCES_R1_R4_P1_G6_2026-11-06.bib",
        "editorial/EL_PRIMARY_LITERATURE_AND_NOVELTY_AUDIT_2026-11-09.md",
        "editorial/figures/Figure1_Observed_ThirdGuild_AcousticAssociation.png",
        "editorial/figures/Figure2_InteractionSignature_VsFrogAbundance.png",
        "editorial/figures/Figure3_D_RateAndDevelopment_EDITORIAL.png",
        "editorial/figures/Figure4_GenuineFinitePopulation_R4.png",
    ],
}
# These are independently authorized public-source inputs, but their derivative
# redistribution rights still need to be assessed for a new third-party deposit.
REVIEW_REQUIRED_GROUPS={
    "naamp_observations",
    "environment_and_occurrence_attributions",
    "si_stage_bridge",
}
EXTERNAL_RECORDS_NOT_ARCHIVED={
    "R5_complete_original_4800_evaluations":"GitHub Actions #42446291543 artifact; must transfer complete original output to permanent repository",
    "R5_reporting_only_repaired_aggregates":"GitHub Actions #42446992844 artifact; must preserve reporting repair without claiming original results changed",
    "raw_WorldClim_and_EarthEnv_rasters":"Fetch and cite provider originals; do not redistribute without separate authorization",
    "full_original_GBIF_provider_records":"60 provider datasets have heterogeneous licenses and no study GBIF download DOI",
    "external_project_DOI_and_peer_review_access":"NOT OBTAINED; authorized depositor action required",
}

def digest(path:Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main(out:Path):
    rows=[]
    for group,paths in INPUTS.items():
        for rel in paths:
            p=ROOT/rel
            exists=p.is_file()
            rows.append({
                "group":group,"path":rel,"present":exists,
                "bytes":p.stat().st_size if exists else None,
                "sha256":digest(p) if exists else None,
                "third_party_rights_review_required":group in REVIEW_REQUIRED_GROUPS,
            })
    present=sum(int(x["present"]) for x in rows)
    missing=[x["path"] for x in rows if not x["present"]]
    root={
        "status":"SOURCE_INPUT_EXISTENCE_HASH_AUDITED_NOT_DOI_ARCHIVED",
        "git_commit":os.getenv("GITHUB_SHA","unresolved_local_git_rev"),
        "required_paths":len(rows),"present_paths":present,"missing_paths":missing,
        "source_bytes_total":sum(x["bytes"] or 0 for x in rows),
        "repo_root_LICENSE_present":(ROOT/"LICENSE").is_file(),
        "repo_root_CITATION_cff_present":(ROOT/"CITATION.cff").is_file(),
        "repo_root_requirements_present":(ROOT/"requirements.txt").is_file(),
        "repo_root_pyproject_present":(ROOT/"pyproject.toml").is_file(),
        "external_missing_or_separately_rights_checked_records":EXTERNAL_RECORDS_NOT_ARCHIVED,
        "external_archive_DOI_registered":False,
        "journal_review_access_verified":False,
        "third_party_redistribution_cleared":False,
        "coauthor_approval":False,
        "complete_archive_ready":False,
        "no_original_ecological_simulations_run":True,
        "files":rows,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(root,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    assert present==len(rows),f"Missing {len(missing)} tracked inputs: {missing}"
    assert not root["complete_archive_ready"] and not root["external_archive_DOI_registered"]
    print("EL_ARCHIVE_INPUT_HASHES_PASS",present,"source_files;",
          "external DOI, rights and R5 artifact backup remain author/depositor gates")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    main(args.out)
