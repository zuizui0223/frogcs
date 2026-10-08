# v0.8 — route-year historical climate exposure bridge

Date: 2026-10-08. Independent frog climate–landscape study; RC6 untouched.

## Scientific distinction

The Daymet v0.7 route-climate acquisition run was still queued at the start of this pass. This v0.8 does **not** claim the run has completed or that frogs have responded to climatic warming/drying.

Created `scripts/build_daymet_survey_exposure_panel.py`, which accepts only a **completed**, source-pinned 1981–2015 Daymet route pilot receipt, the outcome-blind sample selection receipt, and the publicly pinned USGS Runs/Stops tables. It rejects any partial Daymet receipt, missing route-year or 365-day source coverage, mismatched route identities, nonfinite exposure and prospective/retrospective leakage.

It maps **strictly previous-five-complete-year** anomalies relative to the fixed 1981–2000 climate reference to standardized NAAMP survey dates. Each climate quantity is at the route × survey-year level, not one independent observation per frog stop or repeated run. The model-level metric `distinct_climate_route_years` is the correctly supported exposure-grain count.

The full-period 1981–2015 Theil–Sen slope is deliberately absent from early-year event predictor columns (descriptive only). Physical site coordinates remain geometry-pass/unverified and cannot justify 30 m land-cover overlay. It reads **no Counts.csv**, species detections, chorus states or frog reproductive success measures.

## Validation

- v0.7 local synthetic tests: 98/98.
- v0.8 combined local synthetic test suite: 104 passed, 0 failed, after adding six tests for strict source completeness, temporal precedence, route identity, missing historical years, observer metadata, and avoiding pseudoreplication.
- Test file committed under `qa/` to avoid generating more redundant long-running NAAMP source-feasibility workflow runs; invoke manually with `pytest -q studies/climate_landscape/qa/test_daymet_survey_exposure_panel.py`.

## Run once upstream source artifact actually exists

```bash
python studies/climate_landscape/scripts/build_daymet_survey_exposure_panel.py \
  --sample /path/frog_daymet_route_sample.json \
  --climate-receipt /path/frog_daymet_route_climate_receipt.json \
  --runs /path/pinned/Runs.csv \
  --stops /path/pinned/Stops.csv \
  --out out/frog_route_survey_climate.csv \
  --receipt out/frog_route_survey_climate_receipt.json
```

This is environmental feature construction only. A future taxon-level strong-chorus model must independently define the response cohort, zero-detection semantics, historical site use, temporal/geographic holdouts and competition with baseline weather/season, and report association not anthropogenic climate causation.
