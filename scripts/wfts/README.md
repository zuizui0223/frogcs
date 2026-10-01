# WFTS prospective external replication code

This directory contains the analysis implementation frozen **before access to WFTS response outcomes**.

Primary inputs are canonical CSV files defined by:

`revision/WFTS_CANONICAL_SCHEMA_V0_2.json`

Scientific specification:

`revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`

Main analysis:

`run_wfts_confirmatory_analysis_v0_4.py`

The script implements:
- adjacent-year pairing within traditional RouteID × SurveyPeriod;
- deterministic route-fold cross-fitting;
- taxon-specific rain-response slopes learned in the opposite fold;
- strictly-prior taxon × physical-site propensity;
- a = 0.75 dry-state persistence;
- pair-level wet-incidence magnitude matching;
- the frozen within-taxon multi-site concentration endpoint;
- 1,000 null simulations;
- the conditional residual test.

`generate_synthetic_wfts_fixture.py` produces only artificial data for code QA. Synthetic PASS/FAIL direction has **no scientific meaning**.

Do not change endpoint/comparator terms after WFTS outcome readback. Any necessary schema adapter from raw WFTS files to the canonical CSVs must be frozen and audited before running the confirmatory endpoint.


## Version note

Earlier schemas/specs/scripts v0.1–v0.3 are retained only as pre-data development history.

v0.2 introduced route × survey-period candidate support matching NAAMP.

## v0.3 safeguard

The structural coverage gate is evaluated before the analysis loads `taxon_key` or `call_index`. If the route/pair/fold gate fails, the receipt is written and the program exits without opening the frog-response endpoint.


## v0.4 authority

The sole real-data authority is the tuple:

- `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`
- `scripts/wfts/preflight_wfts_structure.py`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

`run_wfts_confirmatory_analysis_v0_4.py` is the only analysis script authorized for real WFTS confirmation.

It combines:
- the v0.3 internal pre-response structural gate;
- route-period candidate support;
- exact runs/matrix date validation;
- required outcome-blind preflight receipt;
- SHA256 equality between preflight and analysis inputs;
- canonical-schema SHA256 equality.

The analysis refuses to parse frog response columns unless the preflight receipt passed and all hashes match.

Earlier scripts are retained only as development history and must not be used on real WFTS response data.
