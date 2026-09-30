# WFTS prospective external replication code

This directory contains the analysis implementation frozen **before access to WFTS response outcomes**.

Primary inputs are canonical CSV files defined by:

`revision/WFTS_CANONICAL_SCHEMA_V0_1.json`

Scientific specification:

`revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_1.md`

Main analysis:

`run_wfts_confirmatory_analysis.py`

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
