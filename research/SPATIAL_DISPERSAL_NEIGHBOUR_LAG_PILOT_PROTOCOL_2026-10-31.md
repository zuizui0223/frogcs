# Frogcs: real NAAMP annual neighbour-lag pattern versus dispersal-like coupling

Date 2026-10-31. New exploratory source-verified analysis toward the SINGLE macroecology→ABC–POM mechanistic manuscript. No new wild sampling.

## Original sources and independent biological units

- Original PR146 source commit: c5ad81b1fb29a9bb92d742ee7004ae66a404dca9.
- Actual NAAMP cohort: 4,248 repeatedly visited physical acoustic listening sites, 63,180 completed survey opportunities.
- Annual response: fraction of completed visits recording strong calling at the site in that calendar year; NOT presence/absence of larvae or egg recruitment.
- Geometry: nearest and farthest OTHER stops within each recorded route, using actual latitude/longitude and haversine distances. A listening station may overlap more than one pond.
- A valid comparison requires documented own, nearest and farthest records in the *strictly previous calendar year*, repeated source site records and at least three site-year observations per route×year. Missing prior years remain missing, not biologically inactive zeroes.
- Physical site FE and route×year FE; prior self, prior nearest, prior farthest together, current air temperature, survey noise and day of year; WLS by current visit count. Route-cluster conditional bootstrap of FE-residualized score moments (399 draws). The interval conditions on the original FE projections and is NOT a full FE-refit confidence interval.

## Competing original-source-matched synthetic models

- M0 SHARED_ENVIRONMENT_NO_MIGRATION: source actual route/sample geometry, temporally autocorrelated route-year environmental shock, spatially correlated site effects, site state persistence, NO neighbour lag coupling.
- M1 SPATIAL_NEIGHBOUR_LAG: all same components plus a hypothetical previous-year nearest-state coupling 0.65. This is *dispersal-like numerical coupling* and not the actual original cohort larval/adult movement modes or a field-calibrated migration rate.
- Both simulate binomial acoustic response with exactly the observed annual site×year visit-count mask. Thirty-two independent RNG labels per model, 75% simulated training/25% simulated holdout and one preselected near-minus-far historical coefficient as the recovery statistic.

Important: even if M1 and M0 are perfectly distinguishable in a strong synthetic experiment, the actual source coefficient may be compatible with zero. Conversely a significant lagged neighbour statistic can arise from temporally persistent **local** environmental forcing not represented by the simple M0 route-year shock. Source posterior probabilities over animal dispersal cannot be inferred from the model comparison.

## Execution and hard gates

1. Original fixed site and visit denominators must match.
2. Five tests confirm temporal source joins, near/far geometry, site/route-year FE controls, negative synthetic tests and null model sampling.
3. Observed near and far lag estimates and their difference must be saved even if negligible, with the source original site-year denominator and route count.
4. Synthetic M0/M1 AUC, held-out balanced accuracy, and explicit coupling/no-wild-calibration warnings must be saved even if classification fails.
5. Never call a strong model-internal recovery AUC evidence for observed frog larval dispersal. This is only a feasibility/identifiability gate before committing to full 96-structure ABC–POM.

## Source and workflow

Implementation: research/scripts/observed_neighbour_lag_dispersal_identifiability.py
Tests: research/scripts/test_observed_neighbour_lag_dispersal_identifiability.py
GitHub Actions: .github/workflows/research_neighbour_lag_environment_disperse_pilot.yml
Original data are checked out by immutable PR146 source SHA in a separate folder and left untouched.
