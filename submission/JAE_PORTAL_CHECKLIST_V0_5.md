# JAE initial-submission checklist v0.5 — metacommunity expansion paper

**Manuscript title:** Recent rainfall expands frog active communities across sites and species without detectable change in beta diversity

## Scientific authority

- [x] manuscript: `MANUSCRIPT_JAE_V0_8.md`
- [x] claim boundary: `ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json`
- [x] argument spine: `COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md`
- [x] metacommunity alpha–beta–gamma summary
- [x] species × stop matrix decomposition
- [x] within-active-site depth decomposition
- [x] functional-community expansion
- [x] functional-response decoupling
- [x] detection-quality robustness
- [x] response-diversity buffering falsification
- [x] exact ecological Figure 1–3 hashes
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
- [x] recorded hearing impairment / timeout / wind robustness passes
- [x] traffic-count and Massachusetts noise-index sensitivities agree
- [x] trait-covered taxonomic richness expands without detectable functional MPD/CWM shift
- [x] functional distance does not predict rainfall-response distance
- [x] held-out response-diversity buffering prediction unsupported and reported as such

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
- [x] `figures_ecology_v0_8/FIGURE_3_FUNCTIONAL_RESPONSE_DIVERSITY_V0_1.svg`
- [x] exact hashes in `ECOLOGICAL_FIGURE_HASHES_V0_3.json`

## JAE formatting / package

- [x] Research Article route
- [x] five-point abstract
- [x] double-anonymized main-manuscript workflow prepared
- [x] separate title-page template v0.5
- [x] versioned metadata template v0.3
- [x] versioned cover letter v0.6
- [x] RC6 handoff
- [ ] build and inspect v0.8 anonymous DOCX artifact
- [ ] run RC6 initial-submission package QA at final branch head
- [ ] promote tested synthesis commit to main / release branch before archive or submission

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

**Do not use RC5/main submission workflows while main still points to the v0.6 week-scale manuscript.**

The submission authority is currently:
`revision/community-metacommunity-synthesis-v1`

Only after RC6 package QA passes should that tested commit be promoted to a release branch / main.

## Final archive stage

Archive license, public snapshot and DOI remain deferred until finalization. The DOI must be inserted into the final manuscript and rendered metadata only after the archive is published.
