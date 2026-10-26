# NAAMP prior community and calling allocation: exploratory test

Date: 2026-10-26. User-directed follow-up: keep NAAMP rain-associated calling concentration central; test whether biotic competition could contribute beyond measured environmental explanations. Existing outcomes have been inspected; this is NOT preregistration or independent confirmation.

## Estimand and predictions

First executable contrast: among species silent throughout a matched dry survey and detected on 1–9 of ten stops on the wet survey, does strictly prior OTHER-taxon recorded calling richness predict the allocation of those detections beyond own-taxon local history? Negative association with held-out predictive improvement is consistent with acoustic segregation; positive association favors shared site suitability/aggregation over simple competitor avoidance. Neither identifies competition.

Use the existing 2,916 history-eligible matched pairs/439 routes without changing their selection. Same route/season and stable physical SiteIDs, history strictly before the earlier paired year, all ten stops previously observed at least once. Retain all eligible species, not only a favorable pair. No whole-species biological absences are inferred: matrix zero means no recorded calling in a completed survey under the established frozen NAAMP pipeline. CI 1/2/3 are detections; this test is NOT a CI>=2 strong-chorus endpoint.

M0 fixed offset: logit(0.25 * smoothed own-taxon prior detection probability), inherited from the existing 0.75 dry-anchor comparator for dry-route-silent taxa. Exact-k conditional subset likelihood over the ten stops. M1 adds one pooled coefficient for strictly prior mean count of other recorded taxa per surveyed stop, centered within cluster; no data-driven covariate/species selection. Exclude focal taxon from the covariate. Missing history is not zero. Histories use only the existing candidate taxon pool for that matched route stratum.

Two deterministic route folds (existing SHA256 fold rule); estimate one coefficient in the opposite fold and score held-out exact subsets. Fixed coefficient bounds [-5,5]; boundary optima flagged. Report both coefficients, held-out log-score gain per cluster, route-bootstrap 95% interval (2,000 draws, seed 20261026), route/fold/sample counts. Require >=30 independent routes and >=100 clusters in each fold; otherwise not estimable. All eligible clusters remain in prediction, including constant other-richness covariates.

## What this does not test

Exact k fixes the number of activated stops and therefore cannot explain away the original RC6 concentration-depth statistic, which depends on k. This is a conditional LOCATION-ALLOCATION test. Route-night weather is common to all ten alternatives and cancels in this conditional likelihood; unmeasured stop-level water, vegetation, detectability and spatial structure remain. Do not label this fully environmentally adjusted or a percentage of the RC6 residual explained. No same-night other-taxon outcome is a prospective predictor.

Next stages of the goal: assess environmental covariate support, evaluate biotic predictors for held-out activation magnitude and the original concentration statistic with matched samples, and use source-native NPS/Hungary tests as external acoustic/habitat comparisons. Do not pool those endpoints. Preserve adverse results and unidentifiable mechanisms.

## Implementation plan

1. Test exact subset probabilities against hand-enumerated k=1 and k=2 cases; verify constant covariate has no effect, target exclusion and missing-history rejection.
2. Add research-only script reusing source hash validation and frozen pair/history construction. Cache validated source locally outside tracked result files. Never write frozen receipt paths.
3. Run synthetic tests then actual source. Save aggregate JSON, source/code provenance and Japanese readout; no raw SiteIDs in deliverables.
4. Review likelihood, temporal exclusions, route holdout and interpretation. Verify frozen paths unchanged.

Alternative rejected: GBIF neighborhood absences as competition exposure (retrieval incomplete and presence-only). Alternative deferred: full environmental/biotic concentration decomposition, until compatible stop-level covariates and prediction evaluation are ready.
