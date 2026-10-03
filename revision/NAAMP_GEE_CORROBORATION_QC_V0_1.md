# GEE corroboration quality audit v0.1

Date: 2026-10-03

## Purpose

A post-reopening methodological sensitivity attempted to corroborate the fixed-q route-night dependence result with an exchangeable binomial GEE using `logit(q)` as an offset. This audit determines whether that fitted GEE is numerically interpretable.

## Receipt

`exploration/NAAMP_ROUTE_NIGHT_GEE_WORKING_CORRELATION_RECEIPT_V0_1.json`

Coverage:
- 2,835 focal pairs;
- 18,769 species × route-night clusters;
- 187,690 species × stop cells.

## Fit diagnostics

The all-cluster fit returned:

- intercept = **−2,172,135.85**;
- robust SE = **0**;
- exchangeable working-correlation alpha = 0.5625.

The dry-route-active fit returned:

- intercept = **−1,688.53**;
- robust SE = **0**;
- alpha = 0.6029.

These estimates are numerically degenerate and cannot be interpreted as valid fitted mean/covariance parameters.

The dry-route-silent fit was numerically ordinary (intercept 0.322 ± 0.033; alpha 0.338), but because the same fixed model is unstable in the full and active strata, the GEE exercise is **not used as an authoritative corroboration** of the route-night dependence claim.

## Decision

- retain the GEE receipt and code for provenance;
- do **not** cite its alpha values in the manuscript, Supporting Information or headline synthesis;
- rely on the bounded residual-pair coefficient with an exact simulation reference distribution, the stop-number-lag profile, same-observer sensitivity and direct clustered-SE diagnostics;
- do not tune the GEE mean model after seeing this failure.

This is a numerical-quality failure of the attempted corroboration, not evidence against or for the biological dependence pattern.
