# DSWEmod reproductive-activity prediction contract v0.1 — 2026-10-07

## Status

Frozen after the surface-hydrology concentration mechanism was found unsupported, but before evaluating whether DSWEmod hydrology improves out-of-route prediction of total reproductive acoustic activity.

This is a distinct question from the concentration mechanism.

## Question

> Even if hydrology does not explain how activity is allocated among stops after total activation is fixed, does dynamic hydrology help predict whether and how strongly a taxon becomes reproductively acoustically active?

## Fixed data population

Use the unique RunIDs and physical SiteIDs from the frozen 500-m DSWEmod M3-complete population underlying the 1,649-pair concentration sequence.

Coverage already established: 1,649 focal pairs; 324 routes; 19 states.

Use the existing route × RunNumber species pool from the NAAMP pipeline. This pool is defined from eligible historical observations within the stratum and is not reselected from the focal hydrology outcome.

## Cell

Species × RunID × physical SiteID.

Each RunID contributes its ten focal stops once even if the RunID participates in multiple adjacent-year pairs.

## Primary response

strong = 1 when CallingIndex >=2, else 0.

This is primary because CI>=2 is already an established strong reproductive acoustic state in the paper.

Secondary response: calling = 1 when CallingIndex >=1, else 0. Secondary cannot replace the primary result.

## Hydrology variables

From the frozen 500-m DSWEmod class-1–3 metric:
- route_current = mean current_D across ten focal SiteIDs;
- route_recent3 = mean recent_D_3m across ten focal SiteIDs;
- route_variability12 = mean DSWE_sd_12m across ten focal SiteIDs;
- local_current = current_D minus route_current.

The primary magnitude question uses route-level variables. local_current is retained only as a control so route-mean effects are not forced to absorb local placement.

## Cross-fitting

Use the existing deterministic route folds A/B. Fit on one route fold and evaluate only on the opposite fold; repeat in both directions.

## Species models

Fit each species separately.

Eligibility: >=20 primary-positive cells in the training fold; positives on >=5 routes; at least one negative cell.

For ineligible species, use the Laplace-smoothed training-fold strong-chorus prevalence, (positive+0.5)/(n+1), as B0 and use the identical prediction for B1-B3. Thus ineligible species remain in scoring and contribute exactly zero hydrology gain rather than being dropped.

For eligible species, if ordinary B0 fitting and the fixed ridge fallback both fail, use the same smoothed-prevalence fallback for B0-B3. If any B1-B3 model also fails both ordinary and ridge fitting, fail closed for that species × training fold by using the same smoothed-prevalence prediction for all B0-B3; do not drop the species or allow a later model to rescue the fit.

B0 — weather/season baseline:
strong ~ log1p(DaysSinceRain) + mean_air_temperature + sin(doy) + cos(doy) + State + RunNumber

B1 — B0 + route_current + local_current

B2 — B1 + route_recent3

B3 — B2 + route_variability12

Use binomial GLM with ridge fallback alpha=0.01 for separation/nonfinite estimates. The same training cells must be used for B0–B3 within each species/fold.

## Out-of-route prediction endpoint

For each eligible species × test-fold cell, retain predicted probabilities from B0–B3.

Primary scoring unit: species, so common taxa cannot dominate.

For each species calculate mean held-out Bernoulli log loss under each model.

Species-level improvements:
- current_gain = logloss_B0 - logloss_B1
- recent_gain = logloss_B1 - logloss_B2
- variability_gain = logloss_B2 - logloss_B3
- total_gain = logloss_B0 - logloss_B3

Positive values mean better held-out prediction.

Primary statistic: equal-species mean total_gain.
Primary variability statistic: equal-species mean variability_gain.

## Uncertainty

Route-block bootstrap of the held-out prediction table:
- resample route_cluster with replacement;
- retain all cells/species within selected routes;
- recompute species-level log losses and their equal-species mean;
- 10,000 replicates;
- seed 2840330.

Hydrology support requires the 95% bootstrap interval of mean total_gain wholly above 0.

Environmental-variability support requires the 95% bootstrap interval of mean variability_gain wholly above 0.

Report current_gain and recent_gain regardless of direction.

## Calibration diagnostic

Also report equal-species mean Brier score for B0–B3. Log loss remains primary.

## Directional coefficient summary

For each hydrology term report across estimable species: median coefficient, interquartile range, and number positive/negative.

Do not test or headline a pooled coefficient when species responses are heterogeneous.

## Interpretation

If B3 improves prediction, dynamic wetland state contains transferable information about reproductive acoustic activity even though it did not explain the higher-order concentration pattern.

If B3 does not improve prediction, the tested remotely sensed surface-hydrology variables do not provide transferable information for either total strong-chorus activity or its conditional spatial concentration.

This concerns reproductive acoustic activity, not spawning success, larval production, recruitment, abundance or fitness.

## Secondary any-calling endpoint

Repeat the identical frozen B0–B3 pipeline for CallingIndex >=1 only after the CI>=2 result is frozen. It is secondary and cannot reverse the primary CI>=2 conclusion.

## Anti-tuning

After CI>=2 predictions are evaluated, do not change species pool, 500-m DSWEmod class set, hydrology definitions, CI threshold, route folds, eligibility thresholds, model sequence, equal-species weighting, bootstrap unit, seed, or log-loss endpoint.
