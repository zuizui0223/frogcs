# Frog active-community response to rainfall — JAE RC6 reproducibility package

Current Journal of Animal Ecology candidate:

**Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without detectable homogenization**

## Current scientific authority

The canonical submission state is intended to be aligned across:

- `main`
- `release/jae-v1-rc6`
- `submission/jae-v1`

Current article files:

- manuscript: `MANUSCRIPT_JAE_V0_8.md`
- claim boundary: `ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json`
- community-ecology spine: `COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC6_V0_1.md`
- activation-geometry falsification: `NAAMP_ACTIVATION_GEOMETRY_PLACEBO_SUMMARY_V0_1.json`
- submission handoff: `submission/SUBMISSION_HANDOFF_RC6.md`
- main figures: `figures_ecology_v0_8/`
- figure hashes: `ECOLOGICAL_FIGURE_HASHES_V0_3.json`

Older RC1–RC5 manuscripts, figures and handoffs remain audit history only.

## Main ecological result

Across 4,236 matched wetter–drier route × seasonal-window comparisons:

- active spatial footprint increases;
- local alpha richness among active stops increases;
- route gamma richness increases;
- measured among-active-site beta-diversity metrics show no detectable shift;
- active species × active-site matrix fill is practically equivalent within a frozen ±0.05 connectance-slope margin;
- most rainfall-associated species × stop incidence growth crosses a spatial and/or taxonomic matrix boundary rather than rearranging an unchanged core.

Exact incidence coefficient shares:

- new species × newly active sites: **36.9%**;
- existing species × newly active sites: **15.2%**;
- new species × already-active sites: **39.9%**;
- existing species × already-active sites: **8.0%**.

## Species-level mechanism: falsified rather than rescued

A post-opening “activation geometry” candidate was highly repeatable across time and disjoint route sets, but it failed a separately frozen placebo gate.

Wet-gain geometry was strongly reproduced by:

- reverse dry-gain geometry: rho = **0.929**;
- low-rain-contrast geometry: rho = **0.953**;
- opportunity-corrected baseline solitude geometry: rho = **0.782**;
- raw singleton-calling fraction: rho = **0.876**.

Therefore activation geometry is **not** treated as a rainfall-specific response trait. Its repeatability is more compatible with a stable acoustic co-occurrence / solitude tendency.

The manuscript does not residualize, redefine or replace geometry after this failed gate.

## Historical v0.4 reconciliation

The earlier v0.4 manuscript reported a null pooled stop-level rain effect on multispecies probability conditional on acoustic activity (OR = 0.988, P = .402).

RC6 instead analyses wet-minus-dry changes in run-level alpha and in the fraction of active stops with >=2 species under matched route × seasonal-window comparisons. The small >=2 component is positive, but ~71% of the alpha slope comes from multiplicity beyond the second species.

These are different estimands and weightings. Supporting Information Section S7 preserves the explicit comparison.

## Data sources

- NAAMP: DOI **10.5066/F7G44NG0**
- AmphiBIO v1: article DOI **10.1038/sdata.2017.123**; data DOI **10.6084/m9.figshare.4644424.v5**

Raw third-party datasets are not redistributed.

## Inferential boundaries

RC6 concerns acoustic activity. It does not infer:

- occupancy or abundance change;
- colonization or extinction;
- dispersal or demographic connectivity;
- rainfall causality;
- exact invariance of beta diversity;
- elimination of all acoustic detectability or masking;
- a validated rainfall-specific species trait;
- response-diversity insurance;
- a physiological rainfall-response half-life.

## Submission QA

The submission pipeline checks:

- RC6 scientific package;
- current title and metadata rendering;
- archive-DOI finalization dry-run;
- deterministic hashes for the two main figures;
- anonymous main-manuscript DOCX;
- anonymous Supporting Information DOCX.

## Development policy

The RC6 story is now frozen around:

1. multiscale active-community expansion;
2. species × site matrix boundary expansion;
3. practical equivalence of active-matrix fill;
4. no detectable beta-diversity shift;
5. recorded detection-condition robustness.

Activation geometry failed its final placebo gate. No additional endpoint search, residualization, or replacement post-opening species trait is authorized for this manuscript.

Future mechanistic work should start a new hypothesis family using independent data or independently sourced proximal traits.
