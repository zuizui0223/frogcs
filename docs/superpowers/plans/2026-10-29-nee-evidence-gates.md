# NEE evidence gates implementation plan

> **For agentic workers:** Execute inline task-by-task using superpowers:executing-plans. No proactive delegation.

**Goal:** Execute the attainable G1 robustness tests and audit G2/G3 without promoting missing observations to evidence.
**Architecture:** Read frozen source tables; write only dated new outputs. One analysis module owns fixed transforms, weighted route-block fits and diagnostics; a separate report states gate status and next measurement requirements.
**Tech Stack:** Python, numpy, pandas, scipy; existing environment.
**Spec:** research/manuscript/HIGH_IMPACT_SUBMISSION_GATES_2026-10-27.md at 5e2f0a8.

## Global constraints

- Do not modify pinned paper/submission/provenance/reproducibility or 2026-10-27 empirical/simulation receipts.
- No new simulation parameter search. No causal identification from suitability, calling or landscape cover.
- Include both SDM backgrounds and all failures; primary Caudata cohort is the frozen pond-breeding group.
- Publish G2/G3 as unmet if no calibrated observation map or genuine three-guild external endpoint exists.

## Fixed G1 design (before coefficient inspection)

- Cohort: 4,248 frozen sites; 3-km flooded vegetation mean; existing rank-standardized seven main/interaction terms. Primary outcome strong_rate; sensitivity season_equal_strong_rate.
- Rank transforms fixed on the full eligible reference cohort before subgroup or route decomposition; do not re-optimize by result.
- Site survey conditions: n_visits, n_years, mean_air, mean_noise, source season-2/3/4 visit fractions and mean day of year. Derive source season fractions from the original completed surveys with timeout==0; assert visit counts equal the frozen cohort. RunNumber is not a biological season.
- Nested adjustment: none; survey; survey+bio1,bio4,bio12,bio15,water_3000m_mean,herbaceous_3000m_mean; plus lat/lon quadratic surface. This does not measure detection probability or remove all environmental confounding.
- Whole area, within-route (demean products and outcome), between-route (equal-weight route averages of already formed products). Covariates are transformed before decomposition.
- Geographic subsets fixed by route-centroid latitude 38 N and longitude -82 E, four quadrants. These are geographic bins, not ecoregions. Full-adjusted pooled/within analyses in all bins with >=20 routes and >=200 sites; retain ineligible rows. Also leave each bin out. Same dataset geographic sensitivity, not independent external validation.
- 999 route-cluster resamples, seed20261029; fixed cohort transforms, refit coefficients, common cluster draws across matched models. Global/full-adjustment also resample fixed 2-degree route-centroid blocks to probe spatial dependence.
- Report intervals and null-centered bootstrap tail p values with BH adjustment across all focal interaction tests in this new analysis. No p threshold chooses a model. Flag insufficient rank, support and valid-bootstrap count.
- Residual spatial diagnostic: 8-nearest-route-neighbor Moran statistic with 999 fixed-seed permutations for pooled global fits; not a proof that residual dependence is absent.
- Confirm macro unadjusted point coefficients against original saved tables. Test weighted block aggregation against explicit replicated rows and within adjustment against route-dummy regression.

## Tasks

- [x] Implement tested aggregation/fit and support diagnostics, execute G1, save full tables and source hashes.
- [x] Audit existing original datasets for common-unit three-guild observations and the observation/process mapping; inspect primary-source experimental evidence for discriminatory predictions, without speculative data merging.
- [x] Produce G1/G2/G3 status, NEE figure/story update and next concrete empirical test; preserve negative evidence; run checks and open a reviewable PR.

## Review focus

Rank deficiency is not a zero effect. Route bootstrap does not remove spatial confounding. Suitability gradients are generated from environmental variables. Geographic subsets are not independent data. Success of a synthetic sign test is not calibration.

## Execution rulings

All 84 models were run. Four NW models have fewer than the fixed 800 valid bootstrap replicates; p and BH q are withheld, with descriptive subset intervals retained and flagged. Fixed-point coefficient replay against the original pooled and within-route table passed. G1 is partial, G2/G3 are unmet; completing this audit is not completing the NEE submission objective. No simulation tuning was performed. External Dryad files returned 403; no raw-data join or independent validation is claimed.
