# Independent NAAMP terrestrial-change study — v1.0 site-identity gate

**2026-10-08.** This is a separate, response-blind feasibility extension. The RC6/JAE manuscript is unchanged. All numeric frog outcomes from the v0.9 route-climate holdout remain frozen; none are retuned.

## Established empirical result (not a new analysis here)

The completed 12-route source-selected Daymet/frog v0.9 exploratory pilot found **no held-out predictive gain** from adding two past-five-year climate variables to recent rain, recorded air temperature, season and route: Bernoulli log-loss 0.561468 (baseline) versus 0.563726 (plus climate); gain -0.002257 per stop, with 9 temporally eligible routes and 57 held-out runs. See `V0_9_REAL_FROG_RESULT.md` and `receipts/real_frog_heldout/frog_strong_calling_heldout_v09.json`. No new lag, species, threshold, regularization or temporal-split search is permitted to rescue this negative pilot. No population, reproduction, anthropogenic attribution, or continent-level inference follows.

## Why historical physical-site identity is now the binding question

The historical USGS NAAMP standardized 2001–2015 sample includes 7,848 ten-stop runs, 8,223 route × SiteID keys and 29,986 candidate adjacent-year same-season *stop comparisons* in a successful original USGS source-QC run. The coordinate file has known transcription errors; the geometry-only successful site-visit screen included 74,861/78,480 surveyed visits, but **zero station locations were independently corroborated** against historical physical-route records.

Before attempting 30-m Annual NLCD land-cover conversion × within-route taxon-specific acoustic allocation, a new necessary-but-insufficient check audits whether each `State:RouteNumber × SiteID` keeps the same numeric `StopNumber` through repeated survey years. It also checks whether its pinned USGS coordinate passes the previously fixed geometry screen. The audit is **not** allowed to repair stop IDs/coordinates, read `Counts.csv`, declare a station externally verified, or rerank routes using frog outcomes.

Script: `scripts/audit_naamp_historical_site_stability.py`. Tests: `tests/test_naamp_historical_site_stability.py`. Both are reproducible with the pinned original `Runs.csv`, `Stops.csv`, `Coordinates.csv` and no acoustic response file. A matching stop number is only *record continuity*, not evidence that the physical wetland did not move or that a route was not relocated.

## Data sources and next gateway

- USGS NAAMP release: https://www.usgs.gov/data/north-american-amphibian-monitoring-program-naamp-anuran-detection-data-eastern-and-central
- Official USGS protocol records that routes were field-groundtruthed, but not every later route alteration necessarily reached the national route maps. https://www.usgs.gov/centers/eesc/science/north-american-amphibian-monitoring-program
- Annual NLCD Collection 1.2 official 30-m annual land cover and change, 1985–2025, provides raster tiles, a land-cover **confidence layer**, land-cover change and imperviousness. An actual pixel-level disturbance score needs paired-year valid masks, confidence and stable historical locations. https://www.usgs.gov/centers/eros/science/annual-national-land-cover-database

An additional prior-study boundary matters: Cosentino et al. (2014, *Biological Conservation*, DOI 10.1016/j.biocon.2014.09.027) already used 1,617 NAAMP stops to associate frog richness/distributions with road traffic/density, forest, wetlands and developed cover, finding especially strong adverse **road** effects and no universal negative developed-land association. The novel question must therefore be longitudinal **within-the-same-verified-site land-use conversion / delayed acoustic response** rather than merely re-estimating a static urbanization association. https://doi.org/10.1016/j.biocon.2014.09.027

### Required release gates

1. Check source hashes and inspect route × SiteID × StopNumber consistency *without* Counts data. Archive only aggregated QC receipts, not the raw third-party tables.
2. Independently corroborate stable route-stop locations, relocation history and coordinates from distinct historical route maps/GPS field forms or reliable contemporaneous documentation. Mark unresolved as **unverified**, regardless of the geometry QC result.
3. Read actual official USGS Annual NLCD Collection 1.2 **landcover and confidence** pixels for the same verified physical buffer in two historical years and calculate transitions at jointly valid pixels; do not interpret WMS rendered colors as classes.
4. Distinguish mapped forest→development, forest→agriculture, forest retention, class confidence, route road-traffic effects, and climate-specific annual precipitation/temperature history. Then use prospectively frozen species × route × physical-site allocation contrasts with temporal and geography blocks.

If the site verification yields too few usable repeated physical locations, classify the 30m site-allocation experiment as **infeasible** rather than loosening the gate after inspecting frog responses. Remaining pilot climate-effects null stays intact.

## Empirical readback, source-only QA (2026-10-08)

GitHub Actions run [37744065229](https://github.com/zuizui0223/frogcs/actions/runs/37744065229) completed successfully with pinned USGS raw metadata. The file `receipts/site_identity/NAAMP_SITE_IDENTITY_STABILITY_ACTUAL_V1_0.json` is the exact source audit receipt.

- 8,223 distinct route × SiteID keys, of which 6,423 were visited in at least two years.
- 8,128 keys held one StopNumber throughout, **95** did not (93 of the 95 were surveyed in multiple years).
- 29,986 site × adjacent-year × season-round matched opportunities; 29,558 held invariant StopNumber; **28,330** additionally passed the existing geometry-only coordinate screen.
- 7,560 route × SiteID keys had invariant StopNumber and passed geometry-only checks. **Zero site locations were independently field-record verified.**

The 95 inconsistent SiteIDs are indicators for record/route audits, **not 95 confirmed relocations**. The 28,330 comparisons are *potential* pairs, not independent species-level or route-level replicates. No 30-m land-cover overlay or frog spatial-allocation outcome was computed.
