# Species-pair segregation versus strictly prior physical-site use

2026-10-20. Separate exploratory research; do not change frozen JAE main. The existing fixed-margin C-score result and its environmental analyses have already been inspected. This is a new, prospectively specified comparison within previously explored NAAMP data, not preregistration or independent confirmation.

## Question

Does the excess species-pair checkerboard structure persist when the fixed-row/fixed-column null additionally preserves each taxon's propensity to use individual physical SiteIDs, learned only from surveys strictly earlier than BOTH members of each focal comparison?

A good historical template can reflect habitat, persistent populations, detectability, or past interactions. Explaining a current pattern with that template does not isolate a causal environmental mechanism, disprove competition, or demonstrate learning.

## Fixed population and no leakage

Start with the archived 1,440 informative pairs / 399 routes from the original 4,236-pair design. Require the two focal surveys to use the identical ten physical SiteIDs. Build a COMMON training history for both sides from eligible surveys on the same State:Route and RunNumber with SurveyYear strictly below the earlier focal year; require all ten SiteIDs, and at least TWO such historical surveys. No later, same-year, or focal outcomes enter the template. Do not select species by results. Conditioning on the observed species set and row/column totals is explicit and is not a forecasting model of total activity.

Source: original three USGS CSVs pinned by existing code at main 0871da0c97d97e2a20156e75fda738d708c82883; CallingIndex >=1, preserving operational taxon labels. Export only scientific survey metadata, physical-site keys, and binary incidence matrices; no observer identifiers or personal metadata. Match every archived run's species breadth, incidence total and observed C-score before proceeding.

Minimum for inference: 200 focal pairs / 80 routes. If not met, report feasibility and pair identities descriptively; do not loosen history, date, or SiteID requirements.

## Fixed historical model and randomization

For species s and physical site j, with n prior complete surveys and x prior calling detections, set q_sj=(x+0.5)/(n+1). This Jeffreys-smoothed empirical template has no fitted tuning parameter. Never use current counts to estimate q. Undetected historical taxa receive a constant probability across sites, hence no artificial spatial preference.

Compare TWO distributions on the SAME binary matrices with observed taxon row totals and stop column totals:

1. Uniform fixed margins (the existing Curveball distribution).
2. Historical weighted fixed margins: probability of matrix Y is proportional to exp(sum_sj Y_sj logit(q_sj)). Sample with the same symmetric row-trade proposal and Metropolis acceptance min(1,exp(delta log weight)). This retains totals exactly while preferring historical site use.

For both models use TWO independently seeded chains per focal run/history pair, 256 retained draws per chain, 100*max(3,n_taxa) burn trades and 20*max(3,n_taxa) trades between draws. Fixed seed family 20261020. These counts are fixed before the new data readback; no effect-guided extra iterations. Validate the weighted sampler against exact enumeration on small matrices, as well as row/column invariance, uniform-weight equality and row/column additive-logweight invariance. Report chain disagreements and fail/qualify unstable results instead of escalating iterations to rescue a claim.

C-score is mean (r_s-overlap_st)(r_t-overlap_st) across detected species pairs; it is distinct from within-taxon JAE concentration C. Total overlap remains fixed, so do not test it as an outcome. Record pair-specific contributions and sum-to-community-score identities.

## Fixed inference and descriptive decomposition

For each focal comparison average the wet and dry run residuals. Average comparisons within route, then routes equally. PRIMARY: paired change in expected C-score, mean(C_history)-mean(C_uniform); positive change would account for some of the previously observed positive segregation residual. Route-cluster bootstrap 2,000 replicates, seed 20261021. Report observed-minus-uniform and observed-minus-history side by side on the exact same sample, with uncertainty. Do not claim mediation or a causal proportion explained; no equivalence claim from a CI crossing zero.

Secondary: wet-minus-dry residual differences under both nulls; same-observer sensitivity using the existing pair flag; both chains separately; unique focal RunID sensitivity using only the earliest eligible focal-pair context for each repeated run (fixed deterministic sorting), with route-equal weighting. This last restriction avoids reuse of the same matrix with multiple histories but does not create independent data.

List the largest taxon-pair contributions to the uniform residual and the remaining historical-weighted residual, weighted so their total equals the route-equal community residual. These are descriptive rankings only, not significant interaction networks; include per-pair run and route coverage and positive/negative contributions. Do not select 'competitive' pairs based on sign. Do not promote a handful of conspicuous pairs to causal mechanisms.

No new ERA5/MODIS extraction or broad trait fishing. Current environmental covariate results remain contextual. Main scientific outcome may be that historical site use explains much, little, or none of the segregation. Preserve all outcomes and source hashes; run locally when source snapshot is available and do not claim GitHub Actions validation for a local run.
