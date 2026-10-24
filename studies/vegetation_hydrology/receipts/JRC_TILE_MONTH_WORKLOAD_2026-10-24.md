# Outcome-blind JRC previous-month source-request budget — 2026-10-24

## Source and scope
USGS NAAMP original accepted physical SiteID coordinates and 2001–2015 `Runs.csv` + `Stops.csv` calendar only, using checksum-pinned GH source-frame artifact. No `Counts.csv` or frog calling outcomes read. The EC JRC/Google MonthlyHistory VER5-0 original TIFF file path is determined by 10° × 10° tile and the strictly **preceding calendar month** (not rolling past 30 days). Category `0` = no water observation, `1` = non-water, `2` = water.

## Verified planning scale
- **185,221** NAAMP station visits in the environmental calendar (18,778 survey runs).
- **172,153** unique physical SiteID × preceding calendar month combinations.
- Only **700** distinct `tile × previous calendar month` GeoTIFF files, across **9** 10-degree US tiles and **125** distinct months (pre-2001 months included for early 2001 surveys). A sample site requires no additional file if another site in the same month and 10° tile has already fetched it.
- At **20–40MB/file**, a complete full-resolution source-transfer budget is roughly **14–28 GB**, not 185,221 per-site downloads. Actual bytes and missingness must be measured, not inferred from this estimate.
- Year **2001**: **8,394** valid station visits, **2,901** sampled site-years, **7,511** distinct site × previous-month combinations, **42** distinct source tile-month files.

## Execution rules
1. Validate pinned coordinate/calendar SHA256 before starting a year, check the 0/1/2 product identity and georeferencing.
2. Download each `tile-month` **only once per annual job**, deduplicate by RouteNumber × physical SiteID × preceding month, then read a 500m geodesic buffer.
3. Record clear observation fraction, water among observed fraction, raw water/land/no-observation counts; never impute no-observation as nonwater. Upload a row for every site-month, including source download failures or low pixel coverage. Discard bulky original tiles after extracting.
4. Begin with year **2001** before authorising 2002–2015 jobs. The 2001 job is `.github/workflows/vegetation_hydrology_jrc_year2001.yml`. Do not open frog `Counts.csv` or infer chorus-habitat effects from this environmental feasibility line.
5. Treat satellite monthly water as a coarse proxy and subject to observational and measurement biases, especially for small or vegetated ponds and weather-dependent Landsat visibility.

## Prior 9-event diagnostics
- Early geographical selection: 9/9 source raster opens; 8/9 have >=50% valid 500m pixels but almost no detected open-water pixels.
- NLCD habitat-stratified selection (source frozen before reading JRC water): 9/9 source raster opens; 7/9 have >=50% valid pixels; open-water-prone sites sometimes had substantial surface-water fractions (e.g. 2008 Minnesota 44.7%, 2008 Missouri vegetated wetland 45.4%). This validates varying pixel detectability in a small nonrepresentative sample, not frog ecology.

## Inference boundary
This is an environmental preprocessing/availability audit, **not** a hypothesis test of rainfall causality, vegetation selection, demographic occupancy, habitat quality, frog abundance or reproductive success. JAE RC6's original scientific branch is unchanged.
