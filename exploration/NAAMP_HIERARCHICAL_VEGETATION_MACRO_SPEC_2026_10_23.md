# Ecology-first macro analysis: wetland vegetation and nested frog acoustic metacommunities

2026-10-23. Exploratory, locked before the new outcome readback. These are the already explored public NAAMP/NWI sources, so this is NOT preregistration. No predictive models or literature searching. JAE RC6 main/paper/SI unchanged.

## Questions, not forecasts

1. At which scale does mapped vegetation variation reside versus where frog acoustic taxon richness varies? Spatial hierarchy: State > physical route > route-run night > stop. Repeated physical SiteIDs are crossed with survey nights, so nested variance is a descriptive decomposition, NOT a unique pure-site random effect.
2. On the SAME ten-stop survey night, is locally mapped NWI wetland vegetation related to the number of acoustically detected taxa per listening stop? Compare positive/negative mapped exposures within each run and average differences within independent physical routes.
3. How do site alpha, route-night gamma and standardized Whittaker beta diversity compare across states/routes, and what do existing species, pair and triplet results imply about distinct biological levels of organization?

## Fixed source, taxonomic units and GIS definitions

Original USGS NAAMP 2001–2015: exactly 7,848 standardized ten-stop surveys. Join to the original validated USFWS NWI 250m 12-shard source (Actions #39450277196): 5,147 physical mapped SiteIDs; exact old sample with 6,236 environmental-complete ten-stop survey nights = 62,360 stop measurements. Never classify failed NWI requests as zero vegetation.

Four overlapping mapped fraction predictors: PEM emergent wetland, aquatic-bed, woody/shrub wetland and any wetland. Presence means positive NWI polygon-buffer overlap, NOT contemporaneous live plants. NWI classes overlap; report class intersections. CI>=1 all recorded calls is main acoustic outcome and CI>=2 strong calling is secondary. Taxon complexes are kept as monitoring taxon units, not asserted to be independently evolving species.

## Primary hierarchical decomposition — exact identity, no p-value

For each variable (four mapped wetland cover fractions, CI>=1 acoustic richness, CI>=2 acoustic richness, any acoustic activity), decompose total weighted stop-level variance into four nonnegative components that sum exactly:

V_total = V_States + E_State[V_routes within State] + E_route[V_nights within route] + E_night[V_stops within night].

Equal States, equal routes within State, equal nights within route, equal 10 stops within night: primary geography-balanced decomposition. Repeat weighting routes equally nationwide (sensitivity), since some States have much denser sampling. Report components and shares in percent. Within-night plant heterogeneity can coexist with between-night frog activity variation; this is a SCALE PATTERN, not an inferred plant mechanism.

## Secondary paired vegetation–richness associations (8 fixed comparisons)

At each ten-stop night with both mapped-positive and mapped-negative stops, compute mean number of detected taxa on positive stops minus mean on negative stops for each mapped vegetation class. Keep true zero frog acoustic detections. Include all nights (no filtering on frog positivity), one mean per physical route for inference.

For 4 vegetation indicators x (CI>=1, CI>=2), report 8 route-mean paired differences, route-cluster Student-t 95% CI, two-sided t P and 4,999 Rademacher route sign flips. Benjamini–Hochberg correction across ALL eight fixed comparisons (ineligible comparisons count as P=1). Require >=30 independent routes and >=5 states; otherwise call underpowered. Report equal-State versus equal-route effect and 2001–09/2010–15 directions as descriptive stability (NWI map itself is not time matched). Route-night/site repeats are not independent inferential units. Never claim a direct plant or interspecific causal effect.

## Metacommunity alpha/beta/gamma

From all 10 stops of every eligible route-night, compute mean stop taxon richness (alpha), number of distinct taxon units across route-night (gamma), normalized Whittaker beta = ((gamma/alpha)-1)/9 if alpha>0, otherwise NA. Report geography-balanced and route-balanced means, number of zero-gamma nights and total sites. No inferential significance hunting with different site/radius thresholds.

## Biological hierarchy from independently existing outputs (do not promote)

Taxon-level previously supported association: five BH-positive PEM strong-calling taxon units among 25 eligible. Species-pair level: 43/127 CI>=1 and 14/57 CI>=2 pairs had NWI-weighted, fixed-margins BH/fold-supported acoustic residual links (NOT direct biotic interactions). Global triplet moment neither any-call nor strong-call establishes genuine third-order excess; no causal triadic effect. Original sample sizes and statistical targets differ; never treat these numbers as one shared binomial denominator.

## Constraints and decision

New primary contribution is multi-scale descriptive hierarchy plus predeclared (for this exploratory followup) local associations. If adjusted richness contrasts fail, retain it as non-support; do not choose regions, scales or species post hoc. Static NWI polygon attributes are not historical plant cover/identity; hydrology, fish/insect predators, plant structure, detection and dispersal are not directly measured. No inference of plant > fish/insect > frog trophic mediation or causal higher-order species interactions.

Code and aggregate numerical receipt isolated from frozen JAE RC6 main/paper/SI.
