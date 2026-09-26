# Community ecology argument spine v0.1 — two-dimensional metacommunity expansion

## Working title

**Recent rainfall expands frog active metacommunities across spatial and taxonomic dimensions without erasing beta diversity**

Alternative:
**Rainfall expands the behaviourally realized frog metacommunity while preserving spatial and functional structure**

## Biological question

Rainfall-driven frog calling is established. The community-ecology question is not whether frogs call after rain, but **how a short environmental pulse changes the spatial organization of the active metacommunity**.

A ten-stop NAAMP route is treated as a behaviourally realized metacommunity:
- local community = one standardized stop;
- active spatial footprint = stops with >=1 calling species;
- local alpha = mean richness among active stops;
- gamma = route-level active-species richness;
- beta = among-active-stop compositional differentiation.

Three alternatives are distinguished:

1. **local intensification** — the same active sites and species simply become more detectable;
2. **homogenizing expansion** — more sites/species become active but assemblages converge among stops;
3. **structure-preserving expansion** — spatial footprint, local alpha and route gamma expand while among-stop beta structure remains approximately unchanged.

The observed pattern supports the third description.

## Claim 1 — rainfall expands the active spatial footprint

Matched wet-dry route x seasonal-window pairs: n=4,236, 585 routes.

Rain-contrast effect on wet-minus-dry active-stop count:
- beta = **+0.3837 stops**;
- 95% CI 0.2396 to 0.5278;
- P = 1.80e-7.

Exact consecutive-year pairs:
- beta = +0.2923;
- P = 5.77e-4.

This is **spatial dilation of acoustic activity**, not an occupancy claim.

## Claim 2 — rainfall increases local alpha and route gamma simultaneously

Local alpha among active stops:
- beta = **+0.0794 species per active stop**;
- 95% CI 0.0231 to 0.1357;
- P = .00569.

Route gamma:
- beta = **+0.2859 active species**;
- 95% CI 0.1646 to 0.4072;
- P = 3.81e-6.

Exact consecutive-year sensitivities remain positive for both.

Within the exact same StopNumber active in both paired surveys, local richness also rises:
- beta = **+0.0953 species/stop**;
- 95% CI 0.0347 to 0.1559;
- P = .00204.

Therefore the alpha increase is not produced only by adding newly active sites.

## Claim 3 — active-site beta diversity is preserved

Rain-contrast effects on among-active-stop beta structure are near zero:

- mean pairwise Sorensen: beta = **-0.00049**, P = .937;
- normalized Whittaker beta: beta = **-0.00482**, P = .339;
- pairwise turnover: beta = -0.00097, P = .885;
- pairwise nestedness: beta = +0.00048, P = .877.

Exact consecutive-year results are likewise null.

Thus alpha and gamma expansion do **not** come with detectable spatial homogenization or differentiation among active sites.

## Claim 4 — the species x site incidence matrix expands at its boundaries

Total rainfall-associated increase in species-stop incidence:
- beta = **+1.3654**;
- 95% CI 0.7567 to 1.9741;
- P = 1.10e-5.

Exact algebraic decomposition of that coefficient:

- **new species x newly active site (corner expansion)**:
  beta = +0.5040, **36.9%** of total, P = 5.07e-7;
- **route-existing species x newly active site (spatial spread)**:
  beta = +0.2080, **15.2%**, P = .00623;
- **route-new species x already-active site (taxonomic deepening)**:
  beta = +0.5444, **39.9%**, P = .00159;
- **route-existing species x already-active site (within-core rearrangement)**:
  beta = +0.1090, **8.0%**, P = .252.

Exact consecutive-year fractions are approximately 33%, 11%, 47%, and 9%.

The response is therefore dominated by **boundary expansion in both dimensions**, not reshuffling of an unchanged core.

## Claim 5 — local taxonomic deepening is mostly deeper multispecies assembly

The increase in mean species richness per active stop decomposes exactly into:

- crossing from one to >=2 species:
  beta = +0.0230, **28.9%** of the alpha slope;
- additional multiplicity beyond the second species:
  beta = +0.0565, **71.1%**;
  P = .0147.

The >=3-species fraction also rises (beta = +0.0226, P = .00670).

Thus local deepening is not merely a binary single-species to multispecies transition.

## Claim 6 — taxonomic expansion largely preserves conventional functional structure

Frozen four-axis AmphiBIO functional space:
- log body size;
- clutch size;
- offspring size;
- reproductive output.

Trait-covered route richness increases:
- beta = **+0.2813**, P = 2.14e-5.

But functional mean pairwise distance does not increase:
- beta = -0.0153, P = .285;
- richness-adjusted sensitivity P = .437.

Community-weighted means for all four traits show no supported shift after FDR correction.

Functional novelty balance is weakly positive:
- beta = +0.0419, P = .0422;
- exact-consecutive sensitivity beta = +0.0483, P = .0640.

Interpret conservatively: taxonomic additions are not confined to identical trait values, but the overall functional centroid and dispersion remain approximately stable.

## Claim 7 — conventional functional similarity does not predict rainfall-response similarity

Among 24 response-eligible species with complete frozen functional traits:
- 276 species pairs;
- Mantel-style correlation between functional distance and absolute adjusted rain-response difference:
  **r = -0.0328**;
- 100,000 unrestricted label permutations: **P = .797**;
- 100,000 within-family permutations: **P = .739**.

Opposite rain-response signs occur in:
- 36.2% of the lowest functional-distance quartile;
- 40.6% of the highest quartile.

Therefore the measured life-history trait space does not provide a proxy for rainfall response diversity. **Response diversity is partly cryptic relative to conventional functional traits.**

## A mechanism that was tested and rejected — response-diversity buffering

A held-out test estimated species response signs in 2001-2007 and asked whether early route-level sign diversity buffered richness responses in 2008-2015.

Primary interaction:
- beta = -0.954;
- 95% CI -3.267 to 1.359;
- P = .419.

Exact-year sensitivity P = .868.

Do not claim an insurance effect or richness stabilization by response diversity.

## Secondary / exploratory results

### Species-specific wet-dry heterogeneity
Species responses are strongly heterogeneous, including within major families. This supports nonuniform participation but is no longer the main story.

### Rain-recency timescale
The 0, 1, 2-3 and 4-7 day bins are richer than the >=8-day reference in the route-season fixed-effects analysis. Because the reference is sparse and the stricter matched sensitivity is imprecise at 4-7 days, use only as evidence that the association is not strictly same-day. Do not headline "week-long pulse".

### Static trait follow-ups
Body size, coarse hydroperiod flags, breeding-season breadth, baseline recurrence, seasonal concentration and historical route dryness do not provide a robust mechanism. These results support the boundary that no simple static trait axis currently explains species rain responses.

## Central ecological interpretation

> **Recent rainfall expands the behaviourally realized frog metacommunity in two dimensions: more sites become acoustically active and more species participate within both new and already-active sites. Local alpha and route gamma increase without detectable change in among-site beta diversity, so the active metacommunity expands without measurable spatial homogenization. Conventional life-history functional structure is largely retained, while species-specific rainfall responses remain poorly represented by those traits.**

## Conceptual contribution

The paper should distinguish three diversity objects:

1. **taxonomic diversity** — alpha and gamma richness increase;
2. **spatial metacommunity structure** — beta diversity remains approximately stable;
3. **response diversity** — species differ in rainfall response, but this difference is not predicted by the measured functional trait space and does not demonstrably buffer richness.

This is stronger than a generic rainfall-calling result because it asks **where in the metacommunity matrix an environmental pulse enters**.

## Main figures

### Figure 1 — environmental pulse across scales
Matched design plus coefficients for:
- active-stop count;
- local alpha;
- route gamma;
- active-site beta metrics.

Visual message: **space + alpha + gamma expand; beta stays flat**.

### Figure 2 — species x site matrix expansion
Four exact incidence components:
- new species x new sites;
- existing species x new sites;
- new species x existing sites;
- existing species x existing sites.

Visual message: ~92% of the slope involves opening at least one matrix boundary; only ~8% is within-core rearrangement.

### Figure 3 — taxonomic, functional and response dimensions
Panel A: taxonomic richness gain vs null functional MPD/CWM change.
Panel B: pairwise functional distance vs rainfall-response dissimilarity with permutation result.
Panel C: conceptual separation of functional traits from response traits.

Timescale, species forest plots, turnover/nestedness between years, and failed simple trait mechanisms move to Supplement.

## Hard boundaries

Do not claim:
- occupancy, abundance, colonization or extinction;
- causal rainfall effects;
- demographic metacommunity dynamics;
- biotic homogenization in the occupancy sense;
- functional equivalence of added species;
- functional traits explain rainfall response;
- response diversity buffers community richness;
- week-long compositional reassembly;
- a physiological rainfall-response half-life.

Use:
- behaviourally realized active metacommunity;
- spatial dilation;
- local taxonomic deepening;
- alpha-gamma expansion;
- preserved among-active-site beta structure;
- species x site incidence matrix;
- conventional functional trait space;
- cryptic rainfall response diversity.
