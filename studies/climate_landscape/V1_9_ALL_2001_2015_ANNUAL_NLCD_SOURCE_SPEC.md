# v1.9 complete 2001–2015 terrestrial land-cover time series: independent source-only pilot

**2026-10-08. Exploratory source-only extension after three-year environmental readback.** This is not preregistered before the previous 2004/2009/2014 environmental images were read, does not modify JAE RC6, and does not restart the frozen negative nine-route climate–frog acoustic prediction experiment.

## Fixed scientific motivation

The starting question was about synchronizing each satellite image with the repeated NAAMP survey calendar, not only contrasting three arbitrarily chosen snapshots. Accordingly request exactly **all 15 years, 2001–2015**, the standardized NAAMP observation period, for the same nominal ten Iowa 360417 stations and frozen 250m and 1000m circles.

The independently identified state-map coordinates numerically agree with original USGS coordinates, but the 2021 map does not verify historical station continuity. This study explicitly reads **zero frog CallingIndex or Counts.csv records**. No acoustic site reallocation, occupancy shift, breeding success, individual movement, or anthropogenic warming attribution follows from land cover by itself.

## Source/extraction contract

- Use one officially authored / Esri-served Annual NLCD Collection **1.0, C1V0** categorical ImageServer product. Require exactly one year-specific mosaic catalog row (correct `Year, Name, Version, OBJECTID`), categorical TIFF, EPSG:5070, native 30m, original 409×170 aligned grid, and a fixed 10-station map source SHA. Refuse classes outside the official 16 values and refuse missing pixels in the fixed crop.
- Retrieve and archive **all years from 2001 through 2015**; missing years are a recorded source-quality failure, not a reason to skip them or interpolate a desired transition.
- For each of 10 sites × two buffers × 15 years, record mapped forest/agriculture/developed/wetland/open-water fractions. For each adjacent year, record 16-class changes and coarser ecological-group changes, forest-loss/gain pixels, forest→agriculture/developed, and agriculture 81↔82 subtype changes.
- To distinguish temporary classification changes from apparently persistent changes, for a group change between `t-1` and `t`, also record whether the new group is still present in `t+1` (when `t+1 ≤ 2015`). No future data is used to explain earlier-year frog responses. This is a *retrospective descriptive persistence annotation*, never an antecedent model predictor.
- Expected complete source-only output: **15 TIFFs, 300 station×buffer×year records, 280 station×buffer×adjacent-year records**, exact source hashes and status. Quality/confidence source (C1.2) remains unavailable and is necessary before ecological interpretation or manuscript escalation.

## What cannot be inferred

The source is **not Collection 1.2**. C1V0 interannual class transitions may reflect algorithmic classification or smoothing, not physical land alteration. The `2021` state map could share an older coordinate source; **zero 2001–2015 independently field-confirmed physical stations** means no definitive stop-level land–frog attribution. Neighboring 1km buffers overlap. No ecological endpoint is opened or tuned based on annual imagery.

Source-only `scripts/annual_nlcd_c1v0_series_360417_v19.py` and `tests/test_annual_nlcd_c1v0_series_v19.py`; Actions workflow `.github/workflows/climate_nlcd_c1v0_annual_series_v19.yml` records success/failure and keeps the raw small cropped TIFFs for source audits, not the full original national products.
