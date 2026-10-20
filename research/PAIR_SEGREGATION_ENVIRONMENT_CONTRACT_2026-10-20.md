# Species-pair structure × measured water: exploratory extension, 2026-10-20

## Question and evidence boundary

Does the measured hydric condition explain changes in species-pair spatial arrangement AFTER conditioning each species' number of calling stops and each stop's number of calling taxa? This is a continuation of the user's competition/niche question, not a return to the known rainfall–calling-richness association. It tests acoustic assembly patterns, not competitive fitness effects, co-existence mechanisms, actual niche resources, egg deposition or reproductive success. All NAAMP analyses remain exploratory, not independent validation.

The prior completed fixed-margin analysis has already been inspected: 1,440 informative pairs / 399 routes / 20 states, primary rain-near-minus-far residual difference +0.00957256 (95% route bootstrap −0.01667 to +0.03510). Thus this is NOT a preregistered untouched analysis. No new joint environment-versus-pair-residual association has been read at this specification commit. Schema/header inspection and SHA checking only have been performed for the new merge.

## Correct an output-label error without changing the old test

The original RESULT.json key `primary.wet_route_equal_excess` incorrectly summarizes `wet_observed_cscore` (about 2.484), NOT observed minus its fixed-margin expectation. Raw C-score positivity or a test against zero is not evidence of segregation. Reconstruct wet_excess = wet_observed_cscore − wet_null_mean_cscore and dry_excess analogously. Preserve the archived result unchanged; mark its misleading raw summary key as superseded. Recompute the original delta_excess to 1e−10 tolerance and report true baseline residuals separately, labelled post hoc descriptive additions. No changes to original random chains, margins, taxon inclusion, draws or seeds.

## Fixed inputs (already downloaded)

1. NAAMP_2026-10-19_species_pair_checkerboard_fixed_margins.zip, SHA256 0690c24e72172a0d6a5a4a0144bac9bda9c78bacee9651b69b49e2cbb2275e19; original workflow 39213495870, artifact 12169665296.
2. NAAMP_environment_state_response_2026-10-19.zip, SHA256 e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0; original workflow 39195215959. Uses route-scale ERA5 reanalysis, not 300-m soil sensors.
3. NAAMP_soil_and_MODIS_joint_2026-10-19.zip, SHA256 ee72dd9b436b5d036fbd43a8c9220038f046aa57dc8f097ec76a08e88a48b366. Its `output/joined_environment_and_chorus.csv.gz` holds previously acquired monthly DSWEmod surface-current and prior values. No new remote-sensing retrieval or version switch.

Verify outer and all inner checksums. Join on BOTH wet_RunID and dry_RunID, one-to-one, and verify State, RouteNumber, RunNumber, route cluster, survey years, rain contrasts and richness agree on overlapping records. Use only exact-site-stable records in both caches. Missing join values are excluded with a receipt, never zero-filled. Compare retained versus original pair/route/state counts. Neither calling outcomes nor environment effect directions may be used to choose subsets.

## New models locked before their fitted effects

Response: delta_excess = (Cobs−Cnull)_nearer_rain − (Cobs−Cnull)_farther_rain. This is NOT the JAE within-taxon concentration endpoint.

Model A, ERA5 intersection: route fixed effects; original rain_contrast, log1p(72h rain)_wet−log1p(72h rain)_dry, temp_difference, doy_difference, year_gap, RunNumber indicators, VPD relief/average, air-temperature average, mean surface soil water, two-layer common soil difference and surface-vs-second-layer imbalance. Current two layers: 0–7 and 7–28 cm. Estimate CR1 route-cluster uncertainty accounting for absorbed route degrees of freedom. Primary contrast A: common_soil_delta, per +0.01 m³/m³.

Model B, existing MODIS-complete intersection: identical Model A terms plus current surface-water difference/average and prior surface-water difference/average. No new interaction. Primary contrasts B1 common_soil_delta per +0.01 m³/m³ and B2 surface_current_delta per +0.10 (10 percentage points of the already defined water-fraction proxy). Other coefficients are adjustment variables, not discoveries. The three primary contrasts A/B1/B2 receive a joint Holm correction; signs are evaluated two-sided. If a model has fewer than 200 pairs or 80 routes, or a target is rank-deficient, mark it not estimable; do not relax.

Secondary diagnostic: on EXACTLY the same samples and identical designs, estimate strong_new_count versus water. This compares responsiveness of calling magnitude with spatial configuration; a significant magnitude coefficient and nonsignificant configuration coefficient are NOT a direct test of equality/difference between biological effects. Report their distinct units and uncertainty.

Sensitivity: same-observer records; route×RunNumber fixed effects; original independent random-chain-0 and random-chain-1 residuals on identical supports. Apply the same minimum support rule. No time-lag, guild, radius or sign-guided new models. Known chain agreement does not prove uniform mixing.

## Baseline residual estimates and independent verification

For the original 1,440 informative pairs, report true wet and dry excess with routes equally weighted (average comparisons within a route, then average routes); 2,000 route bootstraps, seed 20261020. Also report run-deduplicated residuals among the runs appearing in these comparisons, avoiding a claim that repeated runs are independent. The prior difference must reproduce regardless of the output-key correction. Baseline positive C excess indicates more checkerboard structure under this SPECIFIC fixed-margin null, not that all species pairs avoid one another.

Independently recompute all primary slopes and CR1 SEs using explicit route-dummy OLS in addition to within-demeaned regression. Add synthetic regression tests for nonzero raw C with zero excess, mismatched/reversed pair identifiers, join duplication, taxon-richness disagreements, and fixed-route inference versus explicit dummies. Preserve any failure and all fitted positive/negative results. Do not interpret P>0.05 as ecological equivalence or absence of competition.

## Deliverable and governance

Save new source-linked report, result JSON, joined analysis tables, code, tests and SHA manifest on this research branch and as a local ZIP. Do not modify/merge JAE main, ask for new datasets, switch product versions, or create an additional monitoring workflow. Local execution is sufficient and avoids repeated Actions queue polling.
