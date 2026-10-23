# Frog vegetation × hydrology — independent feasibility study (2026-10-23)

## Status and scientific boundary
**Outcome-blind feasibility only.** This document is on an independent research branch. The RC6 Journal of Animal Ecology scientific source, manuscript, conclusions and main branch are unchanged. No plant-cover effect, water-state effect, or independent replication has been estimated. WFTS remains explicitly not pursued.

## Ecological question
Does variation in local vegetation and transient water availability explain **which recurrent physical locations** participate in a frog taxon's multi-site chorus on favourable nights, beyond species-specific meteorological response and past SiteID use? This is distinct from asking only how many calls occur after rain.

1. H1: land-cover structure (forest / woody wetland / emergent wetland / water / open herbaceous / developed) modulates recurrent taxon-specific chorus-site propensity. Do not presume one universal sign.
2. H2: event-level inundation changes spatial configuration beyond broad meteorology, historical site use and the total magnitude of activation.
3. H3: any post-hydrology residual dependence would motivate further ecological hypotheses but would **not** prove movement, social coordination, memory, rainfall causation or simultaneous calling.

## Verified data sources for NAAMP 2001–2015
- [USGS Annual NLCD Collection 1.2](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover), 30 m annual land-cover classes 1985–2025. Codes: 41–43 forest; 90 woody wetland; 95 emergent wetland; 11 open water; 21–24 developed; 52 shrub; 71–72 grass/herb; 81–82 agriculture. Summarize in 100-m and 500-m buffers. **Do not call forest fraction measured canopy cover or vegetation height.**
- [USGS Landsat C2 Level-3 DSWE](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-3-dynamic-surface-water-extent-science-product), 30 m acquisition-level inundation (Landsat 5/7/8 provide period coverage). Only strictly pre-survey images may contribute to a 30-day, 500-m water-detection proxy. It is **not** measured water depth or instantaneous pond hydroperiod.
- [USFWS NWI](https://www.fws.gov/page/national-wetlands-inventory-frequently-asked-questions) for secondary wetland classification; mapping dates vary and **must not be equated with historical field years**.
- [NAAMP USGS original public data](https://doi.org/10.5066/F7G44NG0) — no Counts.csv read during feasibility.

## Geometry and history constraints
The earlier pinned SiteID coordinate table (SHA256 `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`) has known impossible coordinates (including a positive U.S. longitude). Use RouteNumber × physical SiteID; quarantine out-of-bounds, inconsistent duplicate coordinates and implausibly long routes rather than fixing by eye. The 25-km review / 50-km quarantine route-span values are **engineering flags only**, not proof long routes cannot exist. Report exclusions by route/state before reading outcomes.

## Locked feasibility pipeline
1. Quality-audit original coordinate rows and original source checksums, retaining accepted vs held sites and their reasons. Do not infer anything from calls.
2. Build a date × accepted SiteID calendar from *Runs.csv* and *Stops.csv*, without using *Counts.csv*. Calendar coverage is **not** the original paper's final eligible sample.
3. Extract class fractions from year-matched NLCD local GeoTIFFs (100/500 m buffers, valid-pixel coverage ≥80%), preserving no-data and years. Require source raster identities/checksums.
4. Construct QA-filtered DSWE scene summaries. For each survey/site, use acquisition dates strictly earlier than survey date and within 30 days, 500 m buffers and at least 50 valid scene-pixel observations; otherwise mark missing. Pin the exact DSWE band/class/QA semantics **before** creating scene summaries.
5. Audit site × year × event coverage without consulting frog outcomes. Only *after* feasibility and a new protocol freeze define primary tests and out-of-block splits.

## Future ecological comparison (not executed)
M0 = taxon-specific weather + historical SiteID use + dry-state persistence + fixed activation magnitude.
M1 = M0 + vegetation/habitat; M2 = M1 + event-specific water state × taxon; M3 = M2 + taxon–route-night state.
Main endpoint must evaluate **configuration conditional on response magnitude** as well as location recurrence, not merely marginal activity. No model fitted to the same NAAMP observations is independent confirmation. Allow the explicit result **non-estimable** if geospatial coverage is inadequate.

## Execution receipt
A separate downloadable Python toolkit contains five stage-specific preprocessing scripts (coordinate QC, survey-site calendar, NLCD buffered extraction, DSWE coverage compilation), unit tests and a study manifest. On 2026-10-23, **7 of 7 synthetic tests passed**, with zero true NAAMP coordinate, vegetation raster, DSWE scene or calling outcome rows processed. Public remote sensing data and site coordinates still have to be supplied and verified. This research branch does not authorize reopening the RC6 analysis.
