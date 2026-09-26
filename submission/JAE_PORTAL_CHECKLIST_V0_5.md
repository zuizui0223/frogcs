# JAE initial-submission checklist v0.5 — metacommunity expansion paper

**Current manuscript title:** Rainfall-associated expansion of frog active communities adds sites and species without detectable beta-diversity change


## Scientific authority

- [x] manuscript: `MANUSCRIPT_JAE_V0_8.md`
- [x] claim boundary: `ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json`
- [x] argument spine: `COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md`
- [x] metacommunity alpha–beta–gamma summary
- [x] species × stop matrix decomposition
- [x] within-active-site depth decomposition
- [x] detection-quality robustness
- [x] activation-geometry placebo falsification
- [x] functional / response-diversity analyses retained in Supporting Information
- [x] exact ecological Figure 1–2 hashes
- [x] JAE v0.8 scientific-claim QA

## Current article claim

> Recent rainfall is associated with expansion of the behaviourally realized frog active community across both sites and species. Active spatial footprint, local alpha richness and route gamma richness increase with rainfall contrast, whereas the measured among-active-site beta metrics show no detectable shift.

## Main evidence

- [x] 4,236 matched wetter–drier route × seasonal-window pairs
- [x] active-stop coefficient +0.384, 95% CI 0.240–0.528
- [x] local-alpha coefficient +0.079, 95% CI 0.023–0.136
- [x] route-gamma coefficient +0.286, 95% CI 0.165–0.407
- [x] same-stop local-richness increase
- [x] exact species × stop decomposition sums to total incidence coefficient
- [x] ~92% of incidence slope crosses at least one spatial/taxonomic matrix boundary
- [x] pairwise Sørensen and normalized Whittaker beta show no detectable rainfall-associated shift
- [x] active-matrix fill passes the prespecified ±0.05 practical-equivalence margin in primary and exact-year samples
- [x] recorded hearing impairment / timeout / wind robustness passes
- [x] traffic-count and Massachusetts noise-index sensitivities agree
- [x] activation geometry fails the frozen placebo gate and is removed from the main mechanism
- [x] reverse-direction geometry reproduces wet geometry (rho=0.929)
- [x] low-rain-contrast geometry reproduces wet geometry (rho=0.953)
- [x] baseline solitude tendency reproduces wet geometry (rho=0.782)
- [x] functional and response-diversity follow-ups are reported as secondary/falsification analyses

## Secondary only

- rain-recency curve: evidence association is not strictly same-day; **not** a week-long headline
- between-year turnover/nestedness
- species-response forest plot
- body-size, hydroperiod, breeding-season and context follow-ups
- latent spatial heterogeneity moderator
- early spatial niche-breadth response test

## Hard inference boundaries

- no occupancy or abundance change
- no colonization / extinction
- no demographic metacommunity connectivity or dispersal inference
- no rainfall causality
- no claim that beta diversity is proven unchanged/equivalent
- no claim that all acoustic detectability or masking is eliminated
- no claim that the tested functional traits exhaust ecological function
- no functional-trait mechanism for species rain responses
- no response-diversity insurance effect
- no week-long compositional reassembly
- no physiological half-life

## Current main figures

- [x] `figures_ecology_v0_8/FIGURE_1_METACOMMUNITY_EXPANSION_V0_1.svg`
- [x] `figures_ecology_v0_8/FIGURE_2_MATRIX_EXPANSION_V0_1.svg`
- [x] exact hashes in `ECOLOGICAL_FIGURE_HASHES_V0_3.json`

## JAE formatting / package

- [x] Supporting Information: `SUPPORTING_INFORMATION_JAE_RC6_V0_1.md`
- [x] submission workflows build a separate anonymous Supporting Information DOCX
- [x] Research Article route
- [x] five-point abstract
- [x] double-anonymized main-manuscript workflow prepared
- [x] separate title-page template v0.5
- [x] versioned metadata template v0.3
- [x] versioned cover letter v0.6
- [x] RC6 handoff
- [x] build and inspect v0.8 anonymous DOCX artifact
- [x] run RC6 initial-submission package QA at final branch head
- [ ] promote placebo-gated fallback commit to main / release / submission after final QA

## Human metadata still required

- [ ] final author set/order
- [ ] affiliations and institutional addresses
- [ ] corresponding author postal address/email
- [ ] CRediT roles
- [ ] funding / acknowledgements
- [ ] Conflict of Interest statement
- [ ] Statement on Inclusion
- [ ] all-author approval
- [ ] all entitled authors included
- [ ] no concurrent submission
- [ ] store completed metadata as Actions secret `JAE_SUBMISSION_METADATA_YAML`

## Submission-source guard

Current submission authority must be aligned across `main`, `release/jae-v1-rc6` and `submission/jae-v1`.

Older RC1–RC5 manuscripts and the superseded activation-geometry title are audit history only.

## Final archive stage

Archive license, public snapshot and DOI remain deferred until finalization. The DOI must be inserted into the final manuscript and rendered metadata only after the archive is published.
