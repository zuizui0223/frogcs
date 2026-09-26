# Species response-trait framework v0.1 — magnitude versus activation geometry

## Purpose

RC6 now resolves species responses to recent-rain conditions along two conceptually distinct coordinates.

The framework is descriptive and observational. It does not infer occupancy, dispersal, colonization, demographic connectivity or rainfall causality.

## Coordinate 1 — response magnitude

**Question:** Is a species more likely to appear only in the wetter or only in the drier member of a matched route × seasonal-window comparison?

Operational quantity:
- adjusted wet-versus-dry species log odds from discordant matched pairs;
- positive values indicate wetter-associated acoustic participation;
- negative values indicate drier-associated acoustic participation.

This coordinate describes **how much / in which direction** a species' acoustic participation changes.

## Coordinate 2 — activation geometry

**Question:** Conditional on a species gaining a species × stop incidence in the wetter run, where does that gain enter the spatial matrix?

Operational quantity:
- success = wet-gain incidence at a stop inactive in the paired drier run;
- failure = wet-gain incidence at a stop already active in the paired drier run;
- opportunity correction = offset logit(q_pair), where q_pair is the fraction of drier-run stops available in the inactive state.

Interpretation:
- geometry > 0: **spatial-edge activator** — gains disproportionately open newly active sites;
- geometry < 0: **local taxonomic deepener** — gains disproportionately add species to already-active sites;
- geometry = 0: gain placement proportional to available inactive versus active stops.

This coordinate describes **where** a species' wetter-condition gains enter the matrix.

## Why these are different response traits

A single wet-versus-dry response coefficient cannot tell whether a positive responder:
1. spreads into sites that were acoustically inactive;
2. joins sites already containing other callers;
3. does a mixture of both.

Conversely, two species with similar activation geometry can differ in the overall frequency with which they are wetter-associated.

The coordinates should therefore be interpreted as a response plane, not collapsed unless data demonstrate strong coupling.

## Temporal evidence for activation geometry

Non-overlapping temporal validation:
- early period: 2001–2007;
- late period: 2008–2015;
- overlap species: 16;
- Spearman early–late rho = 0.774;
- P = 0.000439;
- inverse-variance weighted late-on-early slope = 0.910, 95% CI 0.816–1.003;
- sign concordance = 15/16, one-sided exact P = 0.000259.

Thus activation geometry has substantial within-species temporal repeatability.

## Relation to conventional functional traits

For the overlap species, descriptive correlations between early activation geometry and:
- log body size;
- log clutch size;
- log offspring size;
- log reproductive output

are all weak to moderate and imprecise (absolute rho <= 0.31; all P >= 0.287).

This does not establish independence from morphology, life history, family or phylogeny. It does establish that the frozen four-axis trait panel does not provide an obvious proxy for activation geometry.

## Relation to response-diversity theory

Response-diversity methodology distinguishes:
- low-level traits used as proxies for environmental sensitivity; and
- higher-level empirically measured species–environment responses.

Activation geometry belongs to the second category: it is estimated directly from the spatial placement of a species' observed response under a defined environmental contrast.

This is useful because the RC6 data show that:
- conventional functional distance does not predict rainfall-response dissimilarity;
- activation geometry itself is strongly repeatable;
- a separate held-out response-diversity buffering hypothesis is unsupported.

Repeatable response traits therefore need not imply a community-level insurance effect under a pulse disturbance.

## Community-level interpretation

The community-wide four-way matrix decomposition can be viewed as the aggregate outcome of species with different response geometries.

At the community level, rainfall-associated incidence growth is dominated by:
- new species × newly active sites;
- new species × already-active sites;
- existing species × newly active sites;

with little pure within-core rearrangement.

At the species level, repeatable activation geometry identifies which taxa disproportionately contribute to the **spatial-edge** versus **local-deepening** pathways.

## What RC6 may say

> Species differ not only in the magnitude of their rainfall-associated acoustic response, but also in a temporally repeatable response geometry describing where their gains enter the species × site matrix.

> Activation geometry is an empirically derived response trait of the behaviourally realized community.

> Conventional life-history functional traits do not strongly encode this response geometry in the tested species set.

## What RC6 must not say

- activation geometry is a dispersal trait;
- activation geometry measures colonization tendency;
- activation geometry is an occupancy niche;
- activation geometry is phylogenetically independent;
- activation geometry is a physiological rainfall-sensitivity trait;
- response magnitude and response geometry are statistically independent unless explicitly supported;
- repeatable activation geometry demonstrates community stability or an insurance effect.

## Endpoint policy

The temporal-repeatability test is the confirmatory gate for promoting activation geometry as a response trait within the post-opening RC6 extension.

Additional trait fishing is not authorized to redefine or rescue activation geometry. Future mechanistic work should use independently sourced, proximal traits or independent monitoring systems.
