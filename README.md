# Frog active-community response to rainfall — JAE RC11 reproducibility package

Current manuscript:

**Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts**

## Current authority

The synchronized submission state is:

- `main`
- `release/jae-v1-rc11`
- `submission/jae-v1`

Journal-facing source files:

- `MANUSCRIPT_JAE_V1_3.md`
- `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md`
- `JAE_TITLE_PAGE_V0_8.template.md`
- `submission/COVER_LETTER_JAE_V0_13.md`

## Result in one paragraph

Across 4,236 matched wetter–drier NAAMP comparisons, recent-rain conditions were associated with larger active spatial footprint, higher richness per active stop and higher route richness. Of the rainfall-associated increase in species × stop incidences, **92.0% crossed a spatial or taxonomic boundary**, exceeding both a magnitude-matched uniform-activation null (**80.9%** expected) and a persistence-preserving null (**77.9%** expected). The same boundary share remained **92.0%** in 3,152 same-observer pairs. FrogID provides directional cross-dataset consistency for active-unit taxonomic depth, not independent validation. A null allowing **species-specific rainfall-response shifts** remains untested and is reserved for revision if requested.

## Repository layout

- `scripts/naamp/` — NAAMP analyses
- `scripts/frogid/` — FrogID and cross-dataset analyses
- `scripts/qa/` — repository and submission audits
- `scripts/submission/` — DOCX, metadata and submission-build utilities
- `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json` — bundled frozen analysis definitions, repair record, and scope decisions
- `provenance/summaries/` — compact durable results
- `provenance/receipts/` — runtime receipt destination (historical receipts are not checked in)
- `provenance/submission/` — current RC11 story freeze
- `submission/` — cover letter plus current metadata/citation templates only

Root-level JSON provenance and root-level analysis scripts are intentionally prohibited.

## Current reproducibility anchors

- uniform activation: `provenance/summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`
- persistence-preserving null: `provenance/summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json`
- same-observer robustness: `provenance/summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json`
- cross-dataset depth: `provenance/summaries/CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json`

Detailed inferential boundaries are documented in the Supporting Information; historical development remains available on the history/release branches.

## Workflows

The current branch uses two workflows only:

- `reproduce_current_results.yml` — manual reproduction of the current analysis endpoints;
- `submission_pipeline.yml` — repository structure, scientific package QA, JAE compliance, anonymous DOCX, scientific bundle, and optional private-metadata bundle.

Historical release branches preserve exact earlier layouts and are not current authority.


## Private submission metadata

Human-identifying submission fields are kept out of the public repository. Copy `submission/SUBMISSION_METADATA_TEMPLATE_V0_7.yml`, fill it locally, and store the completed YAML in the GitHub Actions secret `JAE_SUBMISSION_METADATA_YAML`.

Before building the private bundle, confirm author order, affiliations, corresponding-author contact details, CRediT roles, funding/acknowledgements, Conflict of Interest, Statement on Inclusion, approvals, repository license, and (when available) archive DOI.

To build the private-metadata bundle, run **Actions → submission pipeline → Run workflow** with **build_private_bundle = true**. The workflow validates the private YAML, renders the title page/portal metadata/CITATION/Zenodo metadata, and assembles the submission artifact without committing private contact details.


## Historical material

Superseded manuscripts, analyses, workflows, figures, and submission versions are intentionally absent from the current branch. Exact history remains available in:

- `history/pre-deep-cleanup-2026-09-28`;
- `release/jae-v1-rc1` through `release/jae-v1-rc11`;
- ordinary Git history.
