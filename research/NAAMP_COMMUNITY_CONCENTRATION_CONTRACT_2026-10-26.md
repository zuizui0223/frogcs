# NAAMP prior community and original concentration endpoint

2026-10-26. Exploratory continuation of the user-authorized NAAMP-centered programme. The exact-k location result has already been seen and is positive; it is not independent evidence confirming this follow-up. No species/pair selection based on signs.

## Fixed comparison before new result

Start with the frozen 2,916 paired surveys / 439 routes. Require previous-year survey exposure at every aligned physical SiteID, identical to the previous allocation analysis (38 pairs excluded). Reproduce the full-cohort observed concentration beta 1.6503201354367818 before exclusions. Evaluate M0 and M1 on exactly the same eligible rows, all candidate source taxa and all ten surveyed stops. CI>=1 means recorded calling, not organism occupancy or strong-chorus-only response.

M0: existing principal comparator's species-specific rainfall-response slopes, trained on one route fold; strictly prior focal-site history; fixed 0.75 dry-state anchor. M1: same offset plus a single coefficient for mean strictly-prior OTHER-taxon detection richness per site survey, excluding focal taxon and centering over the pair's species×stop cells. Site exposure must be positive; no missing-history zeros. Existing route-stratum species pools are retained, so this is retrospective configuration evaluation, not a prospectively defined species roster.

For each outer fold, fit the environmental species slopes on that training fold's runs only, then fit M1's coefficient on training-fold pairs only using profiled pair intercepts. Apply both fitted models to the other fold. Do not feed test-fold outcomes into fitted slope/biotic coefficients. Coefficient bounds [-5,5], boundary flagged. At least 30 routes and 100 pairs per training fold.

Pair intercepts are adjusted to match the observed wet TOTAL species×stop detections in expectation, consistent with the existing principal comparator. This uses a held-out response total deliberately: scores are **oracle-total-calibrated configuration diagnostics**, not unconditional held-out predictions. No per-species k is fixed; the species-specific spread and original depth C can vary. Endpoints N (newly active taxa), L (extra active stops beyond the first), C (sum choose(k-1,2) for newly active taxa) use frozen definitions and the same residualized-rain regression.

Report: observed N/L/C, raw Monte Carlo prediction means, conditional C residual given N/L using the existing simulator regression, both fold coefficients, held-out configuration log-score difference per cell, and fixed-model route-bootstrap CI (2,000 draws). Use 2,000 common-random-number Bernoulli simulations for M0/M1, seed 20261027. Conditional upper-tail simulation values are posthoc diagnostics, not confirmatory hypothesis p-values. Compare residuals only on this identical subset and simulation design; never divide by the rounded/full-cohort RC6 residual to claim a causal fraction.

Negative coefficients with improved configuration scores and smaller residual are consistent with aggregate avoidance; positive coefficients with gain suggest shared site suitability/aggregation, not competition. Any persistence or increase of residual means the aggregate history predictor is insufficient in this model. Species-pair-specific competition remains untested. Rainfall model is the existing simple days-since-rain slope plus recorded season/temperature/state/run controls, NOT measured pond water/vegetation or a complete environmental adjustment.

## Plan and validation

- Add tests for vectorized profiled probabilities versus per-pair solve_shift, endpoint hand calculations, equal model zero gain, and fold partition rejection.
- Execute from original SHA-pinned files in Actions (local ScienceBase responds 403). Write only new research outputs. No frozen file mutation.
- Review fold isolation, Monte Carlo interpretation and missingness; preserve all outcomes in report/JSON and existing draft PR.
- Keep environment-specific external comparison and GBIF retrieval tasks active after this diagnostic.
