# WFTS confirmatory authority v0.1

**Status:** frozen before WFTS frog-response outcome access.

## Sole real-data authority

The Wisconsin external confirmation may use only this tuple:

1. `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
2. `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`
3. `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
4. `scripts/wfts/build_daymet_covariates.py`
5. `scripts/wfts/preflight_wfts_structure.py`
6. `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

The following are QA-only:
- `scripts/wfts/generate_synthetic_daymet_fixture.py`
- `scripts/wfts/generate_synthetic_wfts_fixture.py`
- `.github/workflows/wfts_daymet_code_qa.yml`
- `.github/workflows/wfts_confirmatory_code_qa.yml`

## Execution order

1. Build Daymet covariates from a response-free structural station table.
2. Record Daymet/raw/output SHA256 provenance.
3. Build canonical runs + response matrix without calculating the endpoint.
4. Run `preflight_wfts_structure.py`.
5. Confirm structural gate PASS and freeze its receipt.
6. Run `run_wfts_confirmatory_analysis_v0_4.py` once on the exact same runs/matrix bytes and schema.
7. Report PASS or FAIL without retuning.

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
- 1,000 simulations;
- seed 2840223;
- coverage gate: ≥30 routes, ≥300 prior-history pairs, ≥10 routes/fold;
- primary support rule: observed conditional residual above the upper 95% null residual bound.

## Development-history boundary

The following are development history only and are not authorized for real WFTS outcomes:
- canonical schema v0.1;
- weather/analysis specs v0.1–v0.3;
- confirmatory analysis scripts v0.1–v0.3;
- the removed stale v0.3 QA workflow.

## Current blob SHAs

- `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`: `f27bb78d50b7785349f4ef61f22b7ccf2b11dfe2`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`: `23bcf0557840a18f09f0794ebb3bccc3eafb0146`
- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`: `5448ca10ae04fae59e7c8083ed18a177ae9181a5`
- `scripts/wfts/build_daymet_covariates.py`: `5a5fd47512cc3195b86e4334e08b0eddb0ec4609`
- `scripts/wfts/preflight_wfts_structure.py`: `b8737a6fb187a2f9a590952430483f6fc041979a`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`: `139677ea4807189e6d7375c7fdf9be675ea343a8`
- `.github/workflows/wfts_daymet_code_qa.yml`: `9adb6fc0b982d553f00db30c0317deb047f9eb44`
- `.github/workflows/wfts_confirmatory_code_qa.yml`: `23bf4942fec274552df7640f8accc4d4bf7bf35a`

No WFTS species × station × year outcome matrix was inspected to create this authority manifest.
