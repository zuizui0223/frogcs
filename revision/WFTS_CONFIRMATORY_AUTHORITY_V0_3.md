# WFTS confirmatory authority v0.3

**Status:** frozen before WFTS frog-response outcome access. This v0.3 supersedes v0.2 only by adding a prospectively fixed **secondary** diagnostic chain. The primary WFTS confirmation, its endpoint, comparator, coverage gate, informativeness rule and three-way decision classification are unchanged from v0.2.

## 1. Primary real-data authority — unchanged

The sole authority for the primary WFTS confirmation remains:

1. `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
2. `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_5.md`
3. `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
4. `scripts/wfts/build_daymet_covariates.py`
5. `scripts/wfts/preflight_wfts_structure.py`
6. `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`

All scientific quantities, fail-closed protections, coverage gates and decision rules in `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_2.md` are incorporated here **unchanged**.

The primary execution order remains:

1. build response-free primary Daymet covariates;
2. freeze structural preflight;
3. load frog outcomes only after the preflight PASS gate;
4. execute `run_wfts_confirmatory_analysis_v0_5.py` once;
5. freeze and report exactly one primary decision:
   - `replication_support`;
   - `informative_nonreplication_of_half_discovery_effect`;
   - `inconclusive_nonpass`.

No secondary diagnostic may alter, rescue, replace or retune this primary decision.

## 2. Prospective secondary authority — new in v0.3

Only **after the primary result file has been written and frozen**, the same preflight-covered WFTS bytes may be used for the predeclared secondary chain:

1. `revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json`
2. `scripts/wfts/build_common_environment_covariates.py`
3. `scripts/wfts/run_wfts_secondary_route_night_diagnostics_v0_2.py`

The secondary chain tests, in this fixed order:

1. whether species-specific measured common environment using the **3 complete pre-survey Daymet precipitation days** reproduces the WFTS concentration residual;
2. bounded within-taxon route-night residual dependence under the fixed common-environment `q` matrices;
3. persistence of that dependence at station-number lags 7–9 among dry-route-silent taxa;
4. specieswise IID-versus-clustered uncertainty ratios as a monitoring diagnostic.

The 1-day and 7-day precipitation windows are named sensitivities only. They cannot replace the 3-day primary secondary exposure.

## 3. Response-free secondary weather build

The secondary weather adapter may read only structural station/date/coordinate information. It must fail closed if response-like columns are present.

For each physical station and survey date:

- survey-day precipitation is excluded;
- Daymet precipitation is summed over the 1, 3 and 7 complete prior local-calendar days;
- each station exposure is transformed as `log(1 + precipitation_mm)`;
- route-run exposure is the arithmetic mean across exactly ten station values.

The resulting secondary weather file must be hash-verified by the secondary analysis before frog outcomes are used with it.

## 4. Secondary execution guards

The secondary analysis must refuse to run unless:

- the primary WFTS result has `response_endpoints_read = true`;
- the runs and matrix SHA256 values are exactly those used by the frozen primary result;
- the structural preflight had PASS status;
- the secondary weather receipt records `response_columns_read = false`;
- the secondary weather runs file matches the receipt SHA256;
- route-period-year keys and survey dates align exactly with the canonical primary runs;
- the reconstructed principal pair count and route count equal the frozen primary result.

Secondary results cannot change the primary WFTS replication classification.

## 5. Prespecified secondary quantities

### Common-environment comparator

- route-cross-fit species-specific nonlinear rain-recency response;
- route-cross-fit species-specific nonlinear 3-day precipitation response;
- nonlinear Daymet temperature response;
- fixed rain-recency × precipitation and precipitation × temperature interactions;
- SurveyPeriod fixed effects;
- minimum training information: 20 positive station cells and 5 routes;
- strictly-prior physical-station history;
- dry-state persistence anchor `a = 0.75`;
- pair-level wet-incidence magnitude matching;
- 1,000 simulations, seed **2840226**;
- unchanged conditional concentration regression.

### Bounded route-night dependence

- residual `e_cj = y_cj - q_cj`;
- bounded coefficient  
  `rho_b = 2 Σ_c Σ_{j<k} e_cj e_ck / [9 Σ_c Σ_j e_cj²]`;
- all fixed-support clusters and dry-route-silent clusters;
- 1,000 independent-Bernoulli simulations from fixed `q`;
- seed **2840230**;
- upper-tail support rule fixed before WFTS outcomes.

### Route-position lag profile

- dry-route-silent stratum defined using drier outcomes only;
- lags 1–9;
- near pool 1–3;
- far pool 7–9;
- far-lag positive-dependence prediction fixed prospectively;
- 1,000 simulations, seed **2840231**;
- station-number lag is route topology, not exact geographic distance.

### Monitoring uncertainty

Fixed species eligibility:

- ≥200 risk cells;
- ≥20 positive wetter cells;
- ≥30 pair clusters;
- ≥10 routes.

For each eligible taxon compare model-based IID covariance with:

- focal-pair clustered covariance;
- route-across-years clustered covariance.

These diagnostics do not constitute a re-fit of a published WFTS trend estimator and do not define a universal correction factor.

## 6. Interpretation boundaries

The secondary diagnostics may establish transfer of a species-by-route-night dependence pattern to an external monitoring network. They do **not** by themselves establish:

- rainfall causality;
- hydrological causality;
- synchronized breeding as a unique mechanism;
- social facilitation or social transmission;
- individual movement among stations;
- demographic occupancy or abundance change;
- exact physical-distance decay from station-number lag;
- a universal anuran mechanism.

## 7. QA-only files

The following remain QA-only and are not scientific evidence:

- `scripts/wfts/generate_synthetic_daymet_fixture.py`
- `scripts/wfts/generate_synthetic_wfts_fixture.py`
- `scripts/wfts/generate_synthetic_common_environment_runs.py`
- `.github/workflows/wfts_daymet_code_qa.yml`
- `.github/workflows/wfts_confirmatory_code_qa.yml`
- `.github/workflows/wfts_common_environment_weather_qa.yml`
- `.github/workflows/wfts_route_night_secondary_qa.yml`

## 8. Current secondary blob SHAs

- `revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json`: `415931d7459dc7a89099d63071aa439f0441fd13`
- `scripts/wfts/build_common_environment_covariates.py`: `1945e2532449da626cbf77e092abfd43df2c04d3`
- `scripts/wfts/run_wfts_secondary_route_night_diagnostics_v0_2.py`: `66af77b48b3adf3771d8d321bc637beabf792fba`
- `scripts/wfts/generate_synthetic_common_environment_runs.py`: `12957002aa46c534f1c46cdbbf12d2d64929b2d9`
- `.github/workflows/wfts_route_night_secondary_qa.yml`: `27e7fc08d24ad4a7c65a4a5735a45455e3dab300`

No WFTS species × station × year outcome matrix was inspected to create this authority.
