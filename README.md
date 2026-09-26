# Frog active-community response to rainfall — JAE RC6 reproducibility package

This repository contains the reproducibility and submission package for the current
Journal of Animal Ecology candidate:

**Rainfall-associated expansion of frog active communities adds sites and species without detectable beta-diversity change**

## Current scientific authority

The canonical submission state is aligned across:

- `main`
- `release/jae-v1-rc6`
- `submission/jae-v1`

Use these files for the current article:

- manuscript: `MANUSCRIPT_JAE_V0_8.md`
- claim boundary: `ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json`
- community-ecology spine: `COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md`
- species response-trait framework: `SPECIES_RESPONSE_TRAIT_FRAMEWORK_V0_1.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC6_V0_1.md`
- submission handoff: `submission/SUBMISSION_HANDOFF_RC6.md`
- figures: `figures_ecology_v0_8/`
- figure hashes: `ECOLOGICAL_FIGURE_HASHES_V0_3.json`

Older RC1–RC5 manuscripts, figures and handoffs are retained as audit history only.
Do **not** build a current submission from `MANUSCRIPT_JAE_V0_6.md`,
`figures_ecology_v0_6/` or `submission/SUBMISSION_HANDOFF_RC5.md`.

## Main ecological result

Rainfall recency is associated with expansion of the **behaviourally realized
acoustic community** at several spatial scales.

Across 4,236 matched wetter–drier route × seasonal-window comparisons:

- active spatial footprint increases;
- local alpha richness among active stops increases;
- route gamma richness increases;
- measured among-active-site beta-diversity metrics show no detectable shift;
- active species × active-site matrix fill is practically equivalent within a
  frozen ±0.05 connectance-slope margin;
- most rainfall-associated species × stop incidence growth crosses a spatial
  and/or taxonomic matrix boundary rather than rearranging an unchanged core.

The exact community decomposition partitions incidence growth into:

- new species × newly active sites: 36.9%;
- existing species × newly active sites: 15.2%;
- new species × already-active sites: 39.9%;
- existing species × already-active sites: 8.0%.

## Species response geometry

Species differ in **where** wetter-condition gain incidences enter the matrix after
correcting for the number of inactive versus already-active stops available in each
paired survey.

Positive activation geometry denotes a **spatial-edge activator**; negative geometry
denotes a **local taxonomic deepener**.

The response geometry is repeatable in two complementary validations:

- non-overlapping time periods: Spearman rho = 0.774, P = 0.00044;
- completely disjoint deterministic route sets: Spearman rho = 0.785,
  P = 2.1e-6.

Response magnitude and activation geometry are partially coupled but are not treated
as a single response axis. Conventional body-size, clutch-size, offspring-size and
reproductive-output traits do not strongly encode activation geometry in the tested
species set.

## Data sources

Current RC6 analyses use:

- North American Amphibian Monitoring Program (NAAMP):
  DOI **10.5066/F7G44NG0**
- AmphiBIO v1 functional traits:
  article DOI **10.1038/sdata.2017.123**;
  data DOI **10.6084/m9.figshare.4644424.v5**

Raw third-party datasets are not redistributed. Contracts and scripts preserve
source identities, filters, model definitions and deterministic analysis logic.

FrogID and Australian-acoustic analyses belong to earlier manuscript generations and
are **not part of the current RC6 primary article**.

## Inferential boundaries

RC6 concerns acoustic activity. It does not infer:

- occupancy or abundance change;
- colonization or extinction;
- dispersal or demographic connectivity among stops;
- rainfall causality;
- exact invariance of all beta-diversity quantities;
- complete elimination of acoustic detectability or masking;
- phylogenetic independence of activation geometry;
- a response-diversity insurance effect;
- a physiological rainfall-response half-life.

Terms such as “route-new species” and “newly active site” refer only to paired
acoustic detections.

## Submission QA

The submission branch runs `.github/workflows/submission_qa.yml`, which checks:

- the RC6 scientific package;
- current title and metadata rendering;
- archive-DOI finalization dry-run;
- deterministic figure hashes;
- anonymous main-manuscript DOCX;
- anonymous Supporting Information DOCX.

The scientific package, current title, figure package and DOCX pipelines have passed
on the current RC6 lineage.

The remaining real submission inputs are human/finalization items:

- final author set/order and affiliations;
- CRediT roles, acknowledgements and funding;
- corresponding-author details;
- author approvals;
- confirmed repository/archive license;
- published archive DOI.

## Development policy

The current ecological story is frozen around:

1. multiscale active-community expansion;
2. species × site matrix geometry;
3. repeatable species activation geometry;
4. the distinction between conventional functional traits and empirically derived
   response traits.

Negative and rejected mechanisms remain in Supporting Information. Further endpoint
search is not authorized to “rescue” the manuscript; new analyses should answer a
specific reviewer-grade alternative explanation or form a separate future study.
