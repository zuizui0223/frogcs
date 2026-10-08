# Independent climate × remote sensing × frog calling — implementation v0.2

Date: 2026-10-08. **Separate scientific project. No changes to RC6 submission.**

## What is already implemented and locally tested

A downloadable, reproducible local package (v0.2) includes:
1. `audit_coordinates.py`: geometry-only audit for the pinned USGS `RouteNumber,SiteID,lat,lon` file. It *never* auto-verifies physical sites; records potentially erroneous longitude signs, geographic outliers and conflicts.
2. `build_extraction_manifest.py`: output-blind requests for **every** needed JRC image month and Annual NLCD prior-year image, at **250 m and 1000 m** buffer scales. Requires a distinct, independently evidenced `verified_external` physical-site ledger.
3. `extract_annual_nlcd.py`: open an **official USGS Annual NLCD Collection 1.2** raster by year, inspect only target pixel windows, mask actual circles in metric CRS, count the 16 NLCD classes, preserve no-data area, fail if versions/years/classes are wrong.
4. `build_remote_sensing_features.py`: join monthly satellite area statistics and annual land-cover summaries to dated survey events **without reading frog responses**. Water is last completed month, plus prior-12-month observation counts/persistence. Landscape is prior calendar year, plus antecedent 5-year change.
5. `build_climate_features.py`: prior 7/30/90 days' temperature/rain anomalies from Daymet (fixed 1981–2000 reference), and past-only 5-year climate state; rejects missing input windows and unverified sites.
6. `build_climate_trend_diagnostics.py`: 1981–2015 descriptive Theil–Sen climate trend, not an event predictor (because future years would leak into early outcomes).
7. A synthetic raster-plus-climate join test demonstrating that the three environmental families share a single exact physical site and survey-date key.

**Local synthetic checks: 31 passed, 0 failed (2026-10-08).** No real frog–satellite overlay performed and no biological effects estimated. The six Python analysis/extraction modules, Earth Engine extraction recipe, detailed protocol, requirements and the entire 31-test suite are now synchronized in this independent branch. A downloadable local ZIP contains the same source package. No real NAAMP satellite outcome estimates exist.

## Main upstream data/access constraint

The pinned NAAMP coordinate table (12,064 source rows, 1,183 routes) contains known geographic transcription errors, including a positive longitude +83.302 for a U.S. station and routes with implausible >100 km spread. The geometry QC **does not** independently verify any station identity. Therefore a verified site-level 30-m satellite overlay is currently **blocked by an external-coordinate evidence gate**, not by a missing regression model.

The official USGS 2026 Annual NLCD Collection 1.2 raster series covers CONUS 1985–2025 at 30 m; *do not substitute an older epoch NLCD Earth Engine collection or unvalidated community mirror.* The monthly JRC GSW 1.4 Earth Engine series covers 1984–2021; code 0 means **no data**, 1 non-water, 2 water. Small/forested temporary pools may remain undetectable.

A GEE monthly export recipe has been checked into:
- `remote_sensing/jrc_monthly_export_gee.js`

It has **not** been executed: an authenticated GEE workspace and a verified-site CSV upload are required.

## Frozen ecological comparisons for a future independent response-stage analysis

- **Cue-only:** recent rainfall + seasonal phenology + taxon/site historical calling state.
- **Dynamic local habitat:** the same cue + prior hydrological water proxies + landscape covariates.
- **Slow climate mismatch and buffering:** antecedent 5-year warmth/deficit × local visible-water persistence and forest/impervious-change metrics.

Evaluate *both* species × site calling intensity and **within-taxon spatial configuration conditional on total response**, on temporal and geographic blocks. The observational endpoint is **acoustic site use**, not confirmed breeding, occupancy, movement, reproductive success, or anthropogenic climate attribution. Fifteen years of NAAMP does not by itself identify causal global-warming effects.

## Immediate reproducibility prerequisites

- Verified-site ledger with `route_id,site_id,latitude,longitude,coordinate_qc_status=verified_external,verification_source_id`.
- Eligible non-skipped, standardized NAAMP stop-survey metadata with `run_id,route_id,site_id,survey_date` (do not use `Counts.csv` during feasibility).
- Month by month JRC areas, preserving no-data pixel area, image ID and valid-pixel fraction.
- Official USGS Annual NLCD Collection 1.2 GeoTIFFs and a per-year raster provenance index.
- Daymet V4 point series from 1981 baseline to each survey event, preserving the documented leap-year calendar exception.
- Immutable source hashes and site/station relocation evidence before any frog response is joined.

### Primary public documentation

- USGS NAAMP release: https://doi.org/10.5066/F7G44NG0
- Annual NLCD v1.2: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover
- JRC MonthlyHistory: https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory
- Daymet calendar: https://daymet.ornl.gov/single-pixel-tool-guide

This status is an engineering and design advance only; all RC6 inference remains frozen.
