# JAE submission handoff — RC6 metacommunity synthesis candidate

## RC6 scientific package status

The RC6/v0.8 metacommunity synthesis has passed scientific-package QA, anonymous-DOCX QA and deterministic figure/hash QA and has now been promoted.

Current submission authority is aligned across:
- `main`
- `release/jae-v1-rc6`
- `submission/jae-v1`

The original synthesis branch `revision/community-metacommunity-synthesis-v1` remains the pre-promotion development record. Human author metadata and the final archive DOI remain intentionally external/finalization-stage inputs.

## Article

**Title:** Rainfall-associated expansion of frog active communities has repeatable species-specific spatial geometry

**Target:** Journal of Animal Ecology — Research Article

## Scientific authority

- manuscript: `MANUSCRIPT_JAE_V0_8.md`
- claim boundary: `ECOLOGICAL_CLAIM_BOUNDARY_V0_3.json`
- argument spine: `COMMUNITY_ECOLOGY_ARGUMENT_SPINE_V0_1.md`
- metacommunity summary: `NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json`
- matrix summary: `NAAMP_SPECIES_STOP_QUADRANTS_SUMMARY_V0_1.json`
- within-active depth: `NAAMP_WITHIN_ACTIVE_DEPTH_SUMMARY_V0_1.json`
- functional community: `NAAMP_FUNCTIONAL_COMMUNITY_EXPANSION_SUMMARY_V0_1.json`
- functional-response decoupling: `NAAMP_FUNCTIONAL_RESPONSE_DECOUPLING_SUMMARY_V0_1.json`
- detection robustness: `NAAMP_DETECTION_QUALITY_ROBUSTNESS_SUMMARY_V0_1.json`
- matrix-density equivalence: `NAAMP_MATRIX_DENSITY_INVARIANCE_SUMMARY_V0_1.json`
- species activation geometry: `NAAMP_SPECIES_ACTIVATION_GEOMETRY_REPEATABILITY_SUMMARY_V0_1.json`
- response magnitude vs geometry diagnostic: `NAAMP_RESPONSE_GEOMETRY_VS_MAGNITUDE_SUMMARY_V0_1.json`
- response-trait framework: `SPECIES_RESPONSE_TRAIT_FRAMEWORK_V0_1.md`

## Core ecological story

1. **Spatial footprint expands:** rain contrast predicts +0.384 active stops.
2. **Local alpha rises:** +0.079 species per active stop.
3. **Route gamma rises:** +0.286 active species.
4. **Beta metrics do not detectably shift:** pairwise Sørensen beta=-0.00049 (P=.937); normalized Whittaker beta=-0.00482 (P=.339); turnover and nestedness are likewise null.
5. **Active-matrix fill is practically equivalent:** beta=-0.00936; 90% equivalence interval -0.0194 to 0.00070 lies within the frozen ±0.05 margin; exact-year sensitivity also passes.
6. **Expansion is two-dimensional:** species × stop incidence slope partitions into 36.9% new species × new sites, 15.2% existing species × new sites, 39.9% new species × already-active sites and 8.0% within-core rearrangement.
7. **Local deepening is real:** the same numbered stops active in both runs gain richness; 71.1% of the active-stop alpha slope comes from multiplicity beyond the second species.
8. **Recorded detection conditions do not explain the pattern:** hearing impairment + timeout + wind adjustment retains all three positive CIs; traffic and MassNoiseIndex sensitivities agree.
9. **Species activation geometry is repeatable:** early–late rho=.774 (P=.00044), WLS slope=.910, and 15/16 species retain the same spatial-edge versus local-deepening sign. Geometry and later wet/dry response magnitude are best treated as partially coupled response coordinates (cross-period rho=.415, P=.110; weighted slope=.354).
10. **Functional and response dimensions are partly decoupled:** taxonomic richness expands without detectable MPD/CWM shift; functional distance does not predict rainfall-response distance (P=.797; within-family P=.739), and the four tested life-history traits do not strongly encode activation geometry.
11. **Response-diversity buffering is unsupported:** held-out interaction P=.419.

## Secondary only

- rain-recency curve: evidence that the association is not strictly same-day; do not use “week-long pulse” as headline;
- between-year turnover: primary P=.104; exact-year sensitivity positive;
- species-specific wet/dry forest plot and simple trait follow-ups;
- latent spatial heterogeneity moderator: frozen positive prediction failed; opposite-sign full-validation association is secondary only;
- early spatial niche breadth: frozen specialist prediction failed; opposite pooled direction is not family-robust.

## Hard wording boundaries

Do not claim:
- occupancy, abundance, colonization or extinction change;
- demographic metacommunity connectivity or dispersal;
- rainfall causality;
- beta diversity is proven equivalent/unchanged;
- all acoustic detectability or masking explanations are eliminated;
- measured functional traits exhaust ecological function;
- functional traits explain rainfall response;
- response-diversity insurance;
- week-long compositional reassembly.

Preferred wording:
- behaviourally realized acoustic community;
- metacommunity-scale spatial organization;
- active spatial footprint;
- local alpha / route gamma / among-active-site beta;
- two-dimensional spatial and taxonomic expansion;
- no detectable beta-diversity shift;
- measured functional centroid and dispersion show no detectable shift;
- rainfall-response diversity is not represented by the tested life-history trait space.

## Main figures

- `figures_ecology_v0_8/FIGURE_1_METACOMMUNITY_EXPANSION_V0_1.svg`
- `figures_ecology_v0_8/FIGURE_2_MATRIX_EXPANSION_V0_1.svg`
- `figures_ecology_v0_8/FIGURE_3_FUNCTIONAL_RESPONSE_DIVERSITY_V0_1.svg`
  - Panel C: early-versus-late species activation geometry (rho=.774; 15/16 same sign)

Figure hashes: `ECOLOGICAL_FIGURE_HASHES_V0_3.json`

## Submission text files

- `MANUSCRIPT_JAE_V0_8.md`
- `submission/COVER_LETTER_JAE_V0_6.md`
- existing title-page/author metadata templates after title synchronization

## Promotion gate

Completed and promoted:

1. [x] deterministic figure build/hash workflow passes;
2. [x] v0.8 metacommunity QA passes;
3. [x] title-page template, portal checklist, metadata and citation templates use the RC6 title;
4. [x] all core summaries/scripts/contracts cited by v0.8 are present;
5. [x] anonymous DOCX builds from v0.8 and passes structural/anonymity QA;
6. [x] RC6 scientific submission-package QA passes.

Still intentionally unresolved because they require human/final archive input:

- [ ] final author metadata / affiliations / CRediT / approvals;
- [ ] published archive DOI and repository license confirmation.

## Endpoint policy

No additional endpoint hunting should be used to rescue the manuscript. New analyses are justified only for a specific mechanistic question or reviewer-grade alternative explanation, with a frozen specification before readback.
