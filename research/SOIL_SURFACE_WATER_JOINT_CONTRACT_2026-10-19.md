# Soil versus satellite surface water: fixed exploratory joint comparison

Date: 2026-10-19. User-directed reuse of acquired environmental data, separate from frozen JAE main. The previous ERA5-only and surface-water-only results are known. This is a new post-hoc joint analysis, not independent confirmation or a reclassification of the earlier negative concentration tests.

## Question

Does the within-route association between soil water and strong calling persist after remotely sensed surface-water context is included on exactly the same observations? Does surface water carry separate information, or moderate the soil-water association?

## Inputs and untouched definitions

- Existing ERA5/NAAMP cache ZIP, artifact 12161681492, SHA256 e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0: 4108 pairs, 4045 with stable physical sites; two soil layers, rain72, air, VPD and acoustic aggregate responses.
- Existing MODIS DSWEmod extraction, run 37615425574, artifact 11479971642; ZIP SHA256 8db94922a6a4de804b6711b0d2a5ab5e39f18f0a1561deb8392ee13e38100cef; CSV SHA256 9d2967923d7c31ace8007cf51f502c1dc56d41ffcf32383dc1b9edd133b94042. Contains 33260 RunID x SiteID rows, 3326 surveys. No new raster extraction, requests or metadata reinterpretation.
- Preserve primary 500 m buffers and DSWE classes 1/2/3. Require exactly ten unique, matching SiteIDs in both survey records and finite current, recent-three-month and 12-month SD fields at every site, matching the original M3 completeness rule. Select stable pair records and verify State/route/RunNumber/year correspondence. No imputation or favourable species/threshold selection. These strict histories need not yield the same sample size after the ERA5 intersection.
- Average the existing ten stop-buffer fractions with equal stop weights. This is NOT the fraction of the entire route landscape under water: overlapping buffers and repeated pixels are not independent areas.
- Current = observation-month fractional water/potential wetland. Recent-three-month = mean of that month and previous two calendar months. Derive prior-two-month mean algebraically as (3*recent-current)/2; this is an exact reparameterization of the existing current+recent predictor space, not a new searched time window. Validate reconstruction and [0,1] bounds.
- Observation-month composites can contain imagery later than the call survey; this is retrospective association, NOT prospective prediction or causal timing.

## Outcomes and fixed primary comparison family

Primary response: strong_new_count, the number of taxon x stop cells silent in the rain-distant survey but CI>=2 in the rain-nearer survey. Not individual abundance, reproduction, chronological recruitment or original concentration C. All four two-sided tests below form ONE Holm-corrected family.

1. Common soil-water difference (mean of layer1 and layer2 differences), adjusting surface water.
2. Current surface-water difference, adjusting antecedent surface water and soil.
3. Prior-two-month surface-water difference, adjusting current surface water and soil.
4. Common soil-water difference x mean prior-two-month surface-water amount (centered), controlling all three main effects.

Direction hypotheses: positive soil and antecedent-water associations; positive soil-by-water moderation is consistent with complementarity of terrestrial wetness and aquatic habitat. Opposite/null results must be retained. Positive coefficients are associations, not identified biological mechanisms.

## Model, scale and uncertainty

Route-fixed-effect linear regression, with original rain-recency contrast, log1p rain72 difference, air-temperature difference, day-of-year difference, year gap, RunNumber, mean soil1 across the two surveys, layer1-minus-layer2 difference, mean and difference VPD, mean air temperature, and means of current/prior surface water. The primary interaction uses mean prior surface water centered at its joint-sample mean. Soil slopes reported per 0.01 m3/m3; water slopes per 0.10 fraction (10 percentage points); interaction as soil slope change per 0.10 higher prior-water fraction. Fixed effects control constant route intercepts only.

Use CR1 covariance clustered by route, preserving absorbed-effect parameter degrees of freedom; independently compare primary coefficients/SE against explicit route-dummy statsmodels OLS. Check rank; never silently drop a primary exposure. All models including soil-only, joint additive and interaction use the identical complete sample. No cutoff selected by effect size. Conditional confidence intervals are pointwise; multiplicity applies to the stated four tests, not all historical repo exploration.

## Named sensitivities, reported regardless of direction

- Same observer, unchanged sample-selection rule.
- Route x survey-period fixed effects.
- Route and both paired-year effects (omit redundant year_gap).
- 250 m buffer, previously named spatial sensitivity only; require complete physical-site matching again and report any sample change.
- Secondary responses: calling-taxon richness difference, new full-chorus cells. No relabeling them as primary if the primary count tests fail.
- Describe sparse water exposure, within-route correlation/variation, all-10-dry records, missingness, selection by state, and route-level leverage. No excluding all-dry routes or outliers to rescue results.

## Boundaries

No changes to main, submissions, or the original JAE concentration null. Lack of support for water is not proof of biological irrelevance. ERA5 coarse grid and MODIS monthly 250 m water classes measure different constructs/spatial supports; raw coefficients or P values cannot rank their ecological importance. Terrain, individual presence, true local pond hydroperiod and observation probabilities remain incompletely controlled. Store reproducible joined cache, tests and complete results; do not repeat source acquisition or environmental significance searches.
