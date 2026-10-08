# Climate × remote sensing × anuran acoustic-site use — implementation v0.3

**Date:** 2026-10-08. **Research lane:** `study/climate-landscape-acoustic-sites-v0`, separate from RC6 Journal of Animal Ecology paper. **Status:** computational design validated using *synthetic fixtures*, not a real station-satellite association or a climate-effect result.

## What changed since v0.2

1. **Repaired a biologically consequential feature-name error.** The mean areal fraction of satellite-detected surface water over observed months is **not** water persistence/hydroperiod. The v0.3 extractor separates annual *water extent* (`water_mean_visible_fraction_valid_months_12m`) from detection frequency (`water_detected_fraction_observed_12m`). The latter is only estimable if ≥9 of the preceding 12 completed calendar months have ≥50% valid pixels; it uses a prespecified ≥900 m² water-detected threshold, chosen as a nominal 30-m-pixel equivalent (not an ecological breeding threshold).
2. **Interval for observation gaps.** Every event also reports `water_detection_lower_bound_12m` and `water_detection_upper_bound_12m`: all missing months considered *not detected* vs *detected*. These are intervals for the satellite detection count, not confidence intervals and not bounds for subpixel ponds or field hydroperiod.
3. **Separate extent, water/no-data, and terrestrial change.** The 250-m and 1000-m buffers use monthly JRC water, prior-year USGS Annual NLCD and lagged 5-year land-cover differences. The last completed satellite month and all 12 prior months are chronologically before the survey date. Retrospectively trained Annual NLCD classifications **may** use later source imagery; a prior-year label is not a strict historical data-availability claim.
4. **Metadata-only observation panel.** `scripts/build_naamp_observation_panel.py` reads only the exact pinned public `Runs.csv` and `Stops.csv` hashes and reconstructs the 2001–2015 *survey opportunities*. It **never** reads `Counts.csv`, avoids inferring nondetections from absent sparse-positive records, retains physical SiteID, State, RouteNumber, route-specific ID and survey round; excludes missing/duplicate physical IDs. The resulting cohort must be compared with 7,848 standardized runs/78,480 visits from the separate earlier analysis: identity is *not assumed*.
5. **Temporal matched-site design.** `scripts/build_environment_transition_pairs.py` builds survey-year changes in climate, visible water and land cover for the **same route × verified physical site × RunNumber**, exact consecutive calendar years, at most 21 calendar-day difference in observation timing. Changes in CallingIndex are **not** read. Gaps, shifted survey season and unverified coordinates are recorded/refused rather than assigned artificial zeros.
6. **Outcome-blind provenance and independent-coordinate gate remain.** No 30-m NAAMP overlay until external evidence of station identity/position is recorded. The original published coordinate table is known to contain gross errors; geometry passing does not suffice.

## Tests and real-world gates

- **45 passed, 0 failed** using synthetic data in this working container on 2026-10-08. Test families: NAAMP run/stop metadata eligibility, coordinates, JRC nodata/detection bounds, Annual NLCD categorical raster pixels, prior-day climate, antecedent event matching, and same-site annual environmental contrasts. The tests are reproducible but not proof of field-data coverage.
- No new real NAAMP coordinate CSV, Daymet-by-site record, JRC export or USGS NLCD GeoTIFF was successfully downloaded/analyzed in this session. Direct ScienceBase retrieval was attempted but unavailable in the working runtime.
- **Actual** verified-site count, extractable site-years, hydroclimatic trends at NAAMP stations, spatial call changes and any habitat effect are presently **unknown**.
- Prior independent JAE RC6 results and its non-supportive prespecified landscape-fragmentation test are unchanged. No retrospective change of their status or claim.

## Data requirements to execute

- Official USGS NAAMP pinned `Runs.csv`, `Stops.csv`, `SiteID` coordinate table, independently verified station positions/identities; site relocations tracked independently.
- Complete daily Daymet or PRISM 1981–2000 reference, previous five years and days before event for each verified site, with time-series source hashes and time-zone/calendar metadata.
- Pixel-area exports from JRC monthly history, with source image ID, valid fraction and no-data area (small/shaded wetlands may be invisible).
- Official USGS Annual NLCD Collection 1.2 land-cover tiles/mosaics and version/hash manifest, with integer class area rather than a mismatched historical NLCD product.

## Mechanistic comparisons reserved for a separate outcome analysis

**M0.** Weather and phenology + historical taxon-site calling propensity.

**M1.** M0 + measured prior water-detection extent/frequency + lagged surrounding land cover.

**M2.** M1 + antecedent hydroclimatic anomalies interacting with local water state and surrounding forest/development, to test environmental buffering/temporal decoupling.

Before joining calls, freeze geography-specific folds, temporal holdout (2001–2010 training vs 2011–2015 evaluation where available), event/phenology eligibility, and primary joint species-by-site configuration endpoint conditional on calling magnitude. Report acoustic-site use, **not occupancy, successful breeding, movement, philopatry or anthropogenic climate attribution**. A significant land-cover or climate effect requires independent testing and detection/survey-adjustment.

Official sources: [NAAMP](https://doi.org/10.5066/F7G44NG0), [USGS Annual NLCD C1.2](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover), [JRC MonthlyHistory](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory), [Daymet V4](https://developers.google.com/earth-engine/datasets/catalog/NASA_ORNL_DAYMET_V4).
