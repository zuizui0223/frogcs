# Cached environmental follow-up: within-route ecology and transfer error

Date: 2026-10-19. Separate exploratory reuse of NAAMP. No JAE main/submission changes, no external confirmation, no new remote sensing download.

## Purpose and input

Distinguish a regional contrast from covariation within the same survey route. Use the already archived environment/chorus ZIP (run 39195215959, artifact 12161681492; SHA256 e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0). Verify each internal digest. Preserve all 4,045 physically stable pairs, 563 routes, 21 states. The earlier shallow-versus-layer2 exploratory result and its failed within-route/temporal sensitivities are not overwritten.

The cache contains ERA5 0.25-degree reanalysis values, not direct pond measurements or newly combined JRC/MODIS raster observations. Rain-recent versus rain-remote labels are not temporal before/after labels.

## Fixed feature and outcome definitions

Common two-layer difference = [(swvl1_w-swvl1_d)+(swvl2_w-swvl2_d)]/2. Surface excess = (swvl1_w-swvl1_d)-(swvl2_w-swvl2_d). Retain the previous covariates: rain recency contrast, log1p 72-hour rainfall difference, measured air-temperature difference, day-of-year difference, year gap, soil1 midpoint, reanalysis air midpoint, VPD midpoint and relief, and survey RunNumber. Report raw-unit effects per 0.01 m3/m3, not a new tuned drought threshold.

Primary three two-sided tests, Holm-corrected as one new exploratory family:
1. Common difference -> strong_new_count: number of taxon x listening-stop combinations silent in the rain-remote survey and CI>=2 in the rain-recent survey.
2. Surface excess -> strong_new_count, controlling common difference.
3. Common difference -> richness_gain (wet_richness - dry_richness = wet_only - dry_only).

Use OLS with route fixed effects and route-cluster CR1 covariance, retaining the absorbed fixed-effect degrees of freedom. Tests use the same linear model family as the archived analysis; this is not a causal estimator or an abundance/detection model. Response levels and residuals may be non-Gaussian; inference is cluster-robust, not exact. Inspect count identities strong_new_score = 2*strong_new_count + new_ci3_count and richness_gain = wet_only - dry_only.

## Prespecified supporting decompositions

Report the exact same features with route fixed effects for the former strong_new_score and its CI3-count component, and wet_only / dry_only separately. They contextualize the primary tests, not additional successes in a confirmatory family. The linear decomposition must reproduce the direct richness and score coefficients.

Report equal-route between-route regression on route means, adjusted for state, with HC1 uncertainty. Means of within-pair contrasts are NOT climatological wetness, and between-route coefficients must not be described as regional climate causal effects.

Sensitivity: (a) same-observer stable pairs; (b) fixed route x RunNumber strata, testing within the same route and survey-season category; (c) original route FE plus additive earlier-year and later-year effects. Retain every result, including unsupported layer separation. Drop only algebraically constant within-stratum columns; preserve no-estimate flags for unidentified terms. No searching species/years/radii/thresholds for significance.

## Temporal-transfer diagnostic, not a new forecast

Reproduce the previous <=2008 both-survey training / >=2009 both-survey evaluation comparison, training-only feature scaling and the same exclusion of unknown State/RunNumber categories. Do not retune coefficients/cutoff or reinterpret fitted test coefficients as validation. Decompose the already failed test MSE into squared route-equal mean error and centred error variation; additionally report train/test response and exposure distributions and known-versus-new-route descriptive coverage. A mean bias removed using test outcomes is retrospective diagnostic only, not deployable or out-of-sample calibration.

## Boundaries

Route fixed effects remove time-invariant route intercept differences, not time-varying local hydroperiod, community composition, species-specific responses, availability for detection, abundance, or environmental measurement error. Positive call-richness differences are not species colonization, co-existence or true occupancy change. The current analysis does not explain the JAE conditional concentration C and does not identify learned or intergenerational memory. Significance in this family does not correct multiplicity across all past repository exploration. Source cache, code, tests, aggregate outputs and all caveats will be saved; main remains untouched.