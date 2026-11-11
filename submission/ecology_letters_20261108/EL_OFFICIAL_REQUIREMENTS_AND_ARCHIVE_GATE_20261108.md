# Ecology Letters initial submission — verified publisher rules and unresolved archive gate

**Checked 2026-11-08 (JST)** against the [Ecology Letters official author guidelines](https://onlinelibrary.wiley.com/page/journal/14610248/homepage/ForAuthors.html). **Original G8/G11/R5 scientific source results are unchanged by the literature revision. The 2026-11-09 frog-arrival, species and stage-voucher analyses are exploratory additional recorded work; this file manages only editorial requirements.**

## Publisher requirements verified

| Field | Publisher requirement | This C→D Letter candidate status |
|---|---|---|
| Type / scope | Letter, original ecology contribution | Letter; pattern reproduction ≠ demographic benefit |
| Main text | ≤5,000 scientific words excluding abstract, figure legends and references | **4,035 words in 2026-11-09 literature-integrated C→D candidate; abstract 150 words; journal-reference list includes 36 cited records (35 source-register entries plus original USGS G18 release); source QA to be rerun** |
| Abstract | ≤150 words | **150** |
| Main graphics/tables/text boxes | ≤6 combined | 3 author-review main figure candidates, no main tables or boxes (original R4 Figure4 moved to SI S5) |
| Manuscript | Double-spaced; author-approved text; separate figures or combined .doc/PDF initial submission | Word copies exist; original model Figure2 and SI R4 PNGs copied unchanged; new B/C and D figures are editorial source-backed composites |
| Title page | All author names, institutional addresses/emails, running title <45 characters, word/reference/figure counts, corresponding-author postal/phone/fax/email, contributions, data accessibility | **New dedicated Ecology Letters template made; author-specific fields still missing** |
| Cover letter | Specific novelty and general ecological contribution, **plus explicit novelty relative to cited recent publications of authors/coauthors** | Core letter ready; prior-work comparison requires real author review |
| Prior author's papers | Upload PDFs of **recent cited work by present author/coauthors** (published this/last year, in press, submitted, as applicable) | Eligibility not verified; do not assert none |
| Reviewer/editor candidates | Suggested and opposed names, real conflict reasons | Need coauthor input; do not invent individuals |
| Conflict and ethics | All authors disclose actual conflicts; grant and permits statements checked | Author confirmation required |
| Data/code | At **initial submission**, raw/source subsets, derived data, code, README, column metadata, and actual **DOI(s)** in accessible external repository; readers/editors/reviewers must access | **BLOCKED: no project-specific DOI or complete rights-cleared archive confirmed** |
| Submission | Via official **Research Exchange**; automatic uploaded proof reviewed by author | **NOT SUBMITTED; no journal receipt** |

## Pre-deposit source inventory and redistribution triage

This is an inventory of *known repository paths*, not certification of archive completeness or reuse rights.

**Source datasets and provenance**
- NAAMP primary original source: Foreman et al. (2017), DOI [10.5066/F7G44NG0](https://doi.org/10.5066/F7G44NG0), USGS CC0. Actual 4,248-site/63,180 completed-visit analysis files: `research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz`, `research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz`; derived use and source checks in [DATA_CODE_AND_REFERENCE_PROVENANCE](../../editorial/DATA_CODE_AND_REFERENCE_PROVENANCE_2026-11-06.md). The site's derived columns combine differently licensed upstream products; review before redistribution.
- Independent INBO *Hyla arborea* SI-only cross-stage event data: CC0 published adult calls [10.15468/d4bu8j](https://doi.org/10.15468/d4bu8j), larval surveys [10.15468/swgure](https://doi.org/10.15468/swgure), original 245 matched same-location/year opportunities, site-heldout benefit but negative future-year transfer. Data provenance and output [INBO source report](../../research/results/part2_inbo_hyla_g1/REPORT.md). Do not expose sensitive publisher locality IDs or assert unverified φ=+0.262.
- Mohonk vernal-pool programme (SI-only source premise): Garretson et al. (2020), DOI [10.3897/BDJ.8.e50121](https://doi.org/10.3897/BDJ.8.e50121); source EDI package edi.398. Original paired source tables not acquired in current audit; 29/30 and 29/59 proposed counts are excluded pending direct source access and proof of physical pond/date stage matching.
- Independent G18 original USGS stage data: Glorioso & Waddle 2025, DOI [10.5066/P9T71JCO](https://doi.org/10.5066/P9T71JCO), CC0. Anonymized derived result matrices: `research/results/g18_USGS_original_stage_observation_20261108/audited/`. Source seven original CSVs and metadata should be retrieved from USGS using original scripts, not mirrored without vetting personal/sensitive site coordinates.
- GBIF occurrence inputs: acquired with `occurrence/search` on 2026-10-26; original 60 provider attributions/DOIs/rights in `research/results/regional_species_pool_20261026/gbif_dataset_attribution.csv`. **No project GBIF occurrence download DOI**. Respect CC0/CC-BY/CC-BY-NC item-level conditions and provider citations; retain query scripts, not a blanket rights claim.
- WorldClim 2.1 and EarthEnv 1 input rasters: reference original providers and retrieval/checksum instructions, **do not put original restricted rasters into the deposit without permission**. WorldClim permits academic/noncommercial use but has separate redistribution permission; EarthEnv is CC BY-NC. Original Odonata checklist whole-PDF copyright permission was not verified; exclude that PDF.
- Model original and derived source: `research/results/submission_frozen_sources_20261106/` (44-claim verified input bundle); `research/results/g8_27rate_paired_20261107/audited/`, `research/results/g12_abc_pom_prior_20261107/`, `research/results/g13_abc_structure_null_20261107/`, `research/results/g14_abc_pom_field_ensemble_20261107/`, `research/results/g15_abc_acoustic_specificity_20261107/audited/`, plus G16/G17b and R4/P1 source receipts. Establish actual complete relative paths from the manuscript's source registers, don't guess missing results.
- R5: full **24×100×2 observer outputs**, negative controls and reporting repair artifacts available from original [run #42446291543](https://github.com/zuizui0223/frogcs/actions/runs/42446291543) and [source-QA #42446992844](https://github.com/zuizui0223/frogcs/actions/runs/42446992844). **GitHub Actions artifacts expire; preserve complete outputs in DOI archive**, along with frozen protocol, original G4 eight-corner source, 4,248-site covariate/visit inputs, scripts and environment/pinned version requirements. Original model-source G4 artifact [run #42173236906](https://github.com/zuizui0223/frogcs/actions/runs/42173236906) must be preserved likewise.

**Repository and project-created assets:** Python analysis/simulation/test scripts under `research/scripts/`, frozen `.github/workflows/` used for original claims, self-generated figures and their source tables/receipts, manuscript/SI with source references, code/runtime dependencies, file hash manifest, row/column/unit descriptions and README of reproducibility steps. **No repository-wide LICENSE or CITATION.cff has been published in the checked R5 source; author chooses allowable license for project-owned materials.** Do not claim the whole repository (including third-party inputs) is under a project-chosen license.

## DOI deposit completion gate

1. Choose a DOI-assigning public repository (Zenodo, Dryad, Figshare or equivalent) with peer-review-only access appropriate to Ecology Letters. A DOI requires action by an authorized depositor; **no DOI has been issued by this workflow**.
2. Prepare a rights-cleared data/code/metadata package; for restricted sources, include source citation, retrieval scripts and an access note rather than unauthorized data copies. A GitHub PR and journal-attachment SI are not a substitute for independently accessible data.
3. Deposit with a verified DOI and reviewer-access URL; insert exact ID(s) on the title page and manuscript's data-availability statement; have an authorized coauthor verify actual access from an external account.
4. Verify **all coauthors' author order/contributions and consent**, conflicts, prior author's cited publications, publication-size figures and the auto-generated journal proof. Only then can Research Exchange submission be finalized.

**Freeze statement:** All G12–G18/R5 simulation and field-validation findings remain unchanged. No post-hoc tests or favorable scenario cherry-picking are authorized to satisfy journal preparation.
