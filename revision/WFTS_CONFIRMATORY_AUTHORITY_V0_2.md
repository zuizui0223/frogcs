# WFTS confirmatory authority v0.2

**Status:** frozen before WFTS frog-response outcome access. This v0.2 supersedes v0.1 for real WFTS analysis because it adds a prospectively fixed informativeness classification for non-PASS outcomes.

## Sole real-data authority

The Wisconsin external confirmation may use only this tuple:

1. `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
2. `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_5.md`
3. `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
4. `scripts/wfts/build_daymet_covariates.py`
5. `scripts/wfts/preflight_wfts_structure.py`
6. `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`

The following remain QA-only:
- `scripts/wfts/generate_synthetic_daymet_fixture.py`
- `scripts/wfts/generate_synthetic_wfts_fixture.py`
- `.github/workflows/wfts_daymet_code_qa.yml`
- `.github/workflows/wfts_confirmatory_code_qa.yml`

## Discovery-data overlap boundary

The NAAMP discovery sample contains 21 states and **does not include Wisconsin**, as recorded in `revision/WFTS_EXTERNAL_REPLICATION_ELIGIBILITY_V0_1.md`. Therefore no WFTS route can be the same discovery route used in the NAAMP analysis.

For any future external candidate that does share discovery geography, physical route/site overlap must be identified from metadata before response loading and excluded.

## Execution order

1. Build Daymet covariates from a response-free structural station table.
2. Record Daymet/raw/output SHA256 provenance.
3. Build canonical runs + response matrix without calculating the endpoint.
4. Run `preflight_wfts_structure.py`.
5. Confirm structural gate PASS and freeze its receipt.
6. Run `run_wfts_confirmatory_analysis_v0_5.py` once on the exact same runs/matrix bytes and schema.
7. Report one of the three frozen decisions without retuning:
   - `replication_support`;
   - `informative_nonreplication_of_half_discovery_effect`;
   - `inconclusive_nonpass`.

## Fail-closed protections

The confirmatory core refuses to proceed if:
- the preflight read frog-response columns;
- the coverage gate failed;
- runs or matrix bytes differ from the preflight SHA256 receipt;
- the canonical schema differs from the preflight SHA256;
- the structural pair set changes after response loading.

## Scientific quantities fixed before outcome access

- concentration endpoint: `Σ choose(max(k_i-1,0),2)`;
- taxon support: route × survey-period union across eligible years;
- route-fold cross-fitting;
- minimum species-slope information: 20 positive stop-cells and 5 routes;
- strictly-prior site-history weights;
- prior-run focal-site overlap ≥8/10;
- history shrinkage κ=2;
- dry-state persistence anchor a=0.75;
- pair-level wet-incidence magnitude matching;
- principal null simulations: 1,000;
- principal seed: 2840223;
- coverage gate: ≥30 routes, ≥300 prior-history pairs, ≥10 routes/fold;
- primary support rule: observed conditional residual above the upper 95% null residual bound.

## Frozen informativeness rule

The NAAMP principal-comparator conditional residual is **0.2968537316513371**.

For a WFTS non-PASS result, the prospectively fixed benchmark is **50% of the discovery residual = 0.14842686582566855**.

Sampling uncertainty in the WFTS observed conditional residual is estimated with:
- whole-route cluster bootstrap;
- 1,000 replicates;
- seed 2840224;
- null-regression coefficients held fixed at the WFTS frozen principal-comparator values.

Decision rule:
- primary support gate PASS → `replication_support`;
- otherwise, if the **upper 95% bootstrap bound** is below 0.14842686582566855 → `informative_nonreplication_of_half_discovery_effect`;
- otherwise → `inconclusive_nonpass`.

The informative non-replication class rules out a residual effect at least half the NAAMP discovery magnitude under the aligned endpoint; it does not prove a zero effect. An inconclusive non-PASS must not be described as evidence of absence.

## Development-history boundary

Development history only and not authorized for real WFTS outcomes:
- canonical schema v0.1;
- weather/analysis specs v0.1–v0.4;
- confirmatory analysis scripts v0.1–v0.4;
- confirmatory authority v0.1;
- the removed stale v0.3 QA workflow.

## Current blob SHAs

- `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`: `f27bb78d50b7785349f4ef61f22b7ccf2b11dfe2`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_5.md`: `54056270c8fa32695524751e5941e004bd608dff`
- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`: `5448ca10ae04fae59e7c8083ed18a177ae9181a5`
- `scripts/wfts/build_daymet_covariates.py`: `5a5fd47512cc3195b86e4334e08b0eddb0ec4609`
- `scripts/wfts/preflight_wfts_structure.py`: `b8737a6fb187a2f9a590952430483f6fc041979a`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`: `41b6c802cf9d5c7d2b58cb89d23bd315dd98cdc7`

No WFTS species × station × year outcome matrix was inspected to create this authority manifest.
