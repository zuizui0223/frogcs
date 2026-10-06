# frogcs — RC6 frog chorus analysis

## Current paper

**Rainfall-associated frog chorus activation is concentrated within taxa across multiple sites**

This repository contains the analysis, provenance and submission package for the current **Journal of Animal Ecology** Research Article candidate.

Current scientific/submission refs:

- `release/jae-multisite-rc6`
- `submission/jae-multisite-v6`
- validated RC6 scientific source: `ea2bea7fd9ac8856f880a7f3302e193fa19705bd`
- current project closure: `submission/RC6_FINAL_PROJECT_CLOSURE_2026-10-05.md`

The scientific analysis path is closed. Initial submission now depends only on author-side metadata/approvals; archive license/release/DOI finalization is a later pre-publication step.

## Main result

Across **4,236** matched wetter–drier NAAMP comparisons, recent-rain conditions were associated with rapid switching from acoustic silence into strong chorus states.

The focal analysis uses **2,916** comparisons with strictly prior physical-site history. Observed within-taxon multi-site concentration was **1.6503**, versus **1.3535** under the principal comparator. The conditional residual was **0.2969**, outside the simulated 95% range (**−0.1319 to 0.1187**; plus-one **P = 0.000999**). A stronger held-out rain × history gate predicted **1.3323**.

The principal comparator represents:

- route-cross-fitted taxon-specific rainfall response;
- strictly prior species × physical-site use;
- dry-state persistence;
- total wet-state activation magnitude.

The excess was concentrated in a deeper multi-site tail, and strong wet-state chorusing preferentially reappeared at recurrent taxon-specific strong-chorus sites (**β = 0.1511**).

## Ecological interpretation

The result is not simply that frogs call more after rain.

The NAAMP pattern falls between two simpler spatial pictures:

- independent local wetland responses; and
- a uniform route-wide switch.

Instead, favourable nights were associated with **within-taxon multi-site organization that remained spatially selective after response magnitude and first-order taxon/site propensities were represented**.

The broader hypothesis is:

> **Response magnitude alone may be insufficient to describe a short behavioural pulse because the spatial pattern of the realised response can retain additional ecological structure.**

This remains an exploratory manuscript-level inference. It does not establish rainfall causality, demographic occupancy change, literal synchrony among sequentially surveyed stops, individual movement, individual memory or philopatry, reproductive success, or a unique lower-level mechanism.

## Data scale

The public NAAMP source release contains:

- **21,934** run rows;
- **219,340** stop rows;
- **337,848** positive calling records.

Current filters retain **7,848** standardized survey nights and **78,480** fixed-stop visits.

The matched analysis contains **6,074** unique nights, **60,740** fixed-stop visits and **88,737** positive species × stop calling records across **53 taxa**.

Full data-volume audit:
- `revision/DATA_VOLUME_AUDIT_2026-10-03.md`

## Canonical scientific files

Reader-facing scientific package:

- `paper/manuscript.md`
- `paper/supporting_information.md`
- `paper/title_page.template.md`
- `figures_pulse_template/`
- `provenance/CURRENT_RESULTS.json`
- `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json`
- `revision/CURRENT_ENDPOINT_PAPER_SPINE_V0_2.md`
- `revision/EVIDENCE_CLAIM_LEDGER_V0_1.md`
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_3.md`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_4.md`
- `revision/CURRENT_ENDPOINT_SCIENCE_LOCK_2026-10-04.md`
- `revision/PUBLIC_DATA_SCALE_VALIDATION_SYNTHESIS_V0_1.md`
- `revision/PUBLIC_DATA_SCALE_VALIDATION_CLOSURE_2026-10-06.md`
- `submission/SUBMISSION_READINESS.md`
- `submission/RC6_RELEASE_RECEIPT.md`
- `submission/RC6_FINAL_PROJECT_CLOSURE_2026-10-05.md`
- `submission/INITIAL_SUBMISSION_HANDOFF_2026-10-05.md`
- `submission/FINAL_INITIAL_SUBMISSION_RECEIPT_2026-10-06.md`
- `submission/FINAL_PRE_SUBMISSION_AUDIT_2026-10-05.md`

Historical drafts, exploratory branches and superseded analysis records are retained for provenance rather than duplicated in the reader-facing path.

## Reproducibility

Current submission/rebuild workflows:

- `.github/workflows/pulse_template_manuscript_qa.yml`
- `.github/workflows/build_pulse_template_figures.yml`
- `.github/workflows/pulse_template_submission_pipeline.yml`

The original NAAMP analysis scripts remain under `scripts/naamp/`; post-freeze analyses remain auditable in the repository history and frozen exploration branches.

Historical WFTS prospective code and QA are retained for provenance only and are not an active analysis path.

## Closed analysis paths

### WFTS

A prospective Wisconsin Frog and Toad Survey replication was specified but **not pursued**.

- no WFTS data were requested;
- no WFTS response data were received or analysed;
- WFTS contributes no evidence to RC6;
- no WFTS acquisition or execution step is currently authorized.

Current decision authority:
- `revision/WFTS_NOT_PURSUED_2026-10-05.md`

Earlier WFTS specifications and code remain only as historical prospective-design records.

### Post-RC6 landscape exploration

The landscape branches are **closed for the current project**. The prespecified dispersion/fragmentation prediction failed; post-readback compactness is retained as exploratory provenance and is not promoted into RC6.

Current authority:
- `revision/LANDSCAPE_LINES_CLOSED_2026-10-05.md`

## Submission and archive status

The scientific package is closed.

### Initial submission

Final handoff: `submission/INITIAL_SUBMISSION_HANDOFF_2026-10-05.md`

Remaining blockers are author-side only:

- final author set/order and affiliations;
- corresponding-author details;
- CRediT roles where applicable;
- funding/acknowledgements;
- Conflict of Interest;
- final Statement on Inclusion approval;
- final author/institutional approvals.

### Pre-publication archive finalization

Still pending:

- repository/archive license choice;
- final release/archive source;
- persistent archive DOI;
- final `CITATION.cff` / Zenodo metadata.

Archive handoff:
- `submission/ARCHIVE_HANDOFF_2026-10-05.md`

The manuscript already states that the code and derived analysis package will be archived in Zenodo at finalization. Raw third-party source datasets are not redistributed.

- `revision/ENVIRONMENTAL_FACTOR_COVERAGE_AUDIT_V0_1.md`

- `revision/ENVIRONMENTAL_FACTOR_COVERAGE_AUDIT_V0_2.md`
- `revision/PROSPECTIVE_LOCAL_HYDROLOGY_DISCRIMINATION_SPEC_V0_1.md`
