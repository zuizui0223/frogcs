# WFTS prospective secondary diagnostics authority v0.1

**Status:** frozen before inspection of any WFTS species × station × survey outcome matrix.

This authority governs only analyses run **after** the frozen WFTS primary replication has completed and its raw result has been written. It cannot alter the primary replication endpoint, comparator, coverage gate, informativeness rule or three-way decision.

## Required execution order

1. Build the canonical WFTS primary weather and structural files under the existing primary authority.
2. Run the response-blind structural preflight and freeze its receipt.
3. Run `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py` once and freeze the primary result.
4. Only then build the response-free 1/3/7-day common-environment weather covariates.
5. Run `scripts/wfts/run_wfts_secondary_route_night_diagnostics_v0_2.py` on the exact primary runs/matrix bytes.

The secondary script must refuse execution when the primary result has not reached `response_endpoints_read=true` or when primary input hashes differ.

## Sole secondary specification

- scientific contract: `revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json`
- response-free weather adapter: `scripts/wfts/build_common_environment_covariates.py`
- secondary analysis: `scripts/wfts/run_wfts_secondary_route_night_diagnostics_v0_2.py`
- weather QA: `.github/workflows/wfts_common_environment_weather_qa.yml`
- end-to-end secondary QA: `.github/workflows/wfts_secondary_route_night_qa.yml`

The superseded v0.1 common-environment contract remains historical provenance only.

## Frozen secondary sequence

### 1. Common-environment falsification

Primary route-run precipitation exposure is the arithmetic mean across ten stations of station-level `log(1 + precipitation mm)` summed over the three complete local calendar days before survey. Survey-day precipitation is excluded.

Named sensitivities are one and seven prior complete days. The three-day window remains primary regardless of which result is strongest.

Cross-fitted taxon models include:
- rain recency spline, 4 df;
- three-day precipitation spline, 4 df;
- route-run temperature spline, 4 df;
- rain-recency × precipitation interaction;
- precipitation × temperature interaction;
- SurveyPeriod fixed effects.

The fixed q generator then retains strictly-prior physical-station propensity, a=0.75 drier-state persistence and pair-level total-incidence matching.

### 2. Bounded species × route-night dependence

Using the fixed three-day common-environment q matrices:

`rho_b = 2 * sum_c sum_{j<k} e_cj e_ck / [9 * sum_c sum_j e_cj^2]`,

where `e_cj = y_cj - q_cj`.

Report:
- all fixed-support taxon × route-night clusters;
- dry-route-silent taxa defined from the drier survey only.

Reference distribution: 1,000 independent Bernoulli draws from the fixed q matrices, seed 2840230.

### 3. Route-position lag profile

Within dry-route-silent taxa, calculate residual dependence separately for stop-number lags 1–9.

Predefined pooled contrasts:
- near = lags 1–3;
- far = lags 7–9.

The prospective NAAMP-derived prediction is that the far-lag coefficient is positive and above the independent-null upper 95% bound. Stop-number lag is route topology, not exact geographic distance.

Reference distribution: 1,000 independent Bernoulli draws, seed 2840231.

### 4. Monitoring uncertainty

For each information-eligible taxon, compare IID, pair-clustered and route-clustered covariance for the same stop-level wet-activation regression.

Fixed eligibility:
- ≥200 risk cells;
- ≥20 wet-positive cells;
- ≥30 focal-pair clusters;
- ≥10 routes.

Report ratios and their distribution. This is not a reanalysis of a published WFTS trend estimator.

## Interpretation boundary

The secondary analyses may describe:
- whether measured common environment is sufficient for the WFTS allocation pattern;
- whether residual station outcomes show shared taxon × route-night state;
- whether that dependence persists to far route positions;
- whether independence assumptions materially change uncertainty in the representative activation regression.

They may **not**:
- rescue a primary WFTS non-replication;
- downgrade a primary replication;
- change any primary threshold;
- select the best weather window;
- identify social facilitation, synchronized breeding, movement or a unique hydrological mechanism;
- reinterpret station-number lag as exact geographic distance.

## Outcome-access boundary

No WFTS frog-response outcome was inspected in creating this authority.
