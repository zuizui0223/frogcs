# Exploratory multivariable site-vegetation hierarchy after positive macro richness finding

**Date 2026-10-23.** This additional analysis was chosen **AFTER** the completed same-night mapped-wetland positive richness results, and must be reported as a post-readback explanatory sensitivity, not preregistration or independent discovery. No prediction, forecast or literature search; 6,236 original NAAMP/NWI complete 10-stop nights, 62,360 stop observations, 499 physical routes, 20 states. Frozen RC6 main/paper/SI unchanged.

## Ecological question

Does the positive same-night association of mapped PEM emergent wetland sites with more acoustically detected frog taxon units remain **within the same night** after accounting for overlapping NWI wetland categories, extent of mapped wetland, local sound masking, local air temperature and fixed stop position?

Existing unadjusted (route-equal) within-night matched contrasts: all-calling +0.27150 taxa/stop (95% CI 0.22505–0.31795, n=388 routes, 19/20 states positive), strong calling +0.17637 (95% CI 0.14317–0.20957), 8-class test family FDR supported. Other woody/aquatic/any-wetland indicators were also positive unadjusted, but all map classes overlap. Does **PEM-specific descriptive information persist**, or is the original indicator proxying general wetland cover and sound/thermal context?

## Fixed model — no source or sample selection

Population is exactly **all 62,360 source stop measurements**, including acoustic zeroes (no conditioning on calling), from the same original response-blind 12-shard NWI source. Two outcomes: number of CI>=1 calling taxon units at stop (primary), number of CI>=2 strong-calling taxon units (secondary).

Use a **single within-route-run fixed-effects** linear probability/count mean-difference model (OLS response is count, not a binary probability). De-mean outcome and all predictors *within each complete ten-stop survey*, thereby conditioning on common night/weather/route/taxon availability.

Pre-fixed 15 explanatory predictors, in the same analysis across both outcomes:
- three overlapping binary mapped site classes: NWI PEM emergent (>0), woody/shrub (>0), aquatic-bed (>0);
- mapped **total wetland 250m fractional overlap ×10**, so the coefficient refers to +10 percentage points mapped wetland;
- local air temperature (°C) and acoustic masking/sound index as already present in original eligibility gate;
- standardized listening stop order 2–10 (9 dummies, stop 1 reference). These physical stop positions are not literal distance measures.

No custom vegetation interactions, geography carve-outs, new map radii, species-selection or outcome-dependent covariates. Same 62,360 records for CI>=1 and CI>=2. Complete-time stop mapping and original 6,236 nights verified before model fit.

## Replication and uncertainty

Weight each route equally overall, independent of its total number of repeated nights. 499 monitoring routes = inferential clusters; repeated 10 stops and many nights do NOT provide independent replications.

For the four focal mapped-context coefficients in each of two endpoints (8 pre-fixed tests), calculate route-cluster sandwich SE with finite-route correction G/(G−1) × (N−1)/(N−K), Student t(df=G−1) 95% intervals and two-sided P. BH over 8 coefficients (not merely the ones passing nominal thresholds). Retain all coefficient signs whether supported or not.

**State-level stability**, not another primary hypothesis: recompute route-weighted PEM coefficient after omitting each of the 20 geographic States and report sign, range and number of positive exclusions; also compute State-cluster sandwich 95% interval using only 20 independent State clusters. This is a sensitivity to geographic clustering, **not causal confirmation**.

## Explicit ecological claim boundary

An adjusted positive PEM association can mean structured wetland habitats have **independent statistical local richness correlates**, conditional on these measured covariates. It is NOT a plant manipulation, preference, insect/fish mediation, greater survival, abundance or proof of interacting frog taxa. NWI polygons are not plant-species or time-matched macrophyte measurements. Prior same-night PEМ boundary nonassociation with Sørensen community turnover remains legitimate: differences in **how many taxa call** can occur without systematically different **which taxa call** under a richer adjusted assemblage comparison.
