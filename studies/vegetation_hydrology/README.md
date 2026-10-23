# Vegetation × wetland hydrology and frog chorus configuration (independent feasibility line)

**Status 2026-10-23:** environmental-data feasibility and outcome-blind geospatial preprocessing only. **Not** a new NAAMP frog-outcome analysis, a replication, or a modification of the frozen `frogcs` RC6 paper. No numerical vegetation or hydrology effect is established. Never infer breeding success, true occupancy, individual movement or synchronous calling from NAAMP's ordered acoustic stop surveys.

## Ecological target

The parent `frogcs` study found that rain-associated calling is disproportionately concentrated within taxa across separated fixed listening sites, with preferential re-expression at recurrent species-specific chorus locations. The unresolved causal/ecological alternative is **event-varying local wetland condition × taxon-specific breeding requirements**. Static habitat suitability is only partly proxied by previous species × physical SiteID chorus use; measured route-wide weather alone did not reproduce the conditional configuration.

**Study question:** Does local water state interact with vegetation/wetland setting to determine *which* physical sites contribute to a taxon's widespread chorus when conditions become favourable?

### Proposed independent hypotheses (not yet tested)

- H1 / habitat selectivity: forest, woody wetland, emergent wetland, open-water, developed and herbaceous cover in 100-m/500-m buffers predict persistent taxon-specific site suitability (without assuming one universal sign).
- H2 / event-level filter: temporally matched observed surface-water state improves prediction of the spatial arrangement **conditional on overall acoustic response magnitude**, beyond historical site propensity and broad weather.
- H3 / residual: if non-independent multi-site concentration persists when H1 and H2 are modelled, additional species-route-night biological state is plausible but is **not uniquely identified** as social interaction, movement, memory, or synchrony.

All H1–H3 need a new frozen inferential protocol, external independent evaluation, and covariate-coverage gates before accessing any frog outcomes. **Do not run confirmatory tests yet.**

## Verified public geospatial sources

| Source | Coverage / role | Guardrail |
|---|---|---|
| **USGS Annual NLCD Collection 1.2 Land Cover**, [data release](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover), [legend](https://www.mrlc.gov/data/legends/annual-nlcd-land-cover-legend), DOI [10.5066/P94UXNTS](https://doi.org/10.5066/P94UXNTS) | CONUS 1985–2025, 30 m; year-specific class shares | Broad land-cover map **not** direct canopy %, calling substrate or wetland vegetation height. Annual maps are retrospectively produced. |
| **USGS Landsat Collection 2 Level-3 DSWE**, [data description](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-3-dynamic-surface-water-extent-science-product), DOI [10.5066/P9DPWBUS](https://doi.org/10.5066/P9DPWBUS) | Per-acquisition surface-water class, 30 m, includes NAAMP 2001–2015 | Scene dates must be pre-survey; cloud/snow/no-data remain missing; shallow and vegetated water can be missed; does not directly measure depth or hydroperiod. |
| **USFWS National Wetlands Inventory**, [FAQ](https://www.fws.gov/page/national-wetlands-inventory-frequently-asked-questions) | Wetland spatial classification | Historical mapping dates and coverage differ; never describe current NWI as 2001–2015 wetland state without metadata. Secondary only. |

The raw USGS NAAMP data are at [DOI 10.5066/F7G44NG0](https://doi.org/10.5066/F7G44NG0). The separate coordinate file used by previous `frogcs` analyses has known gross transcription anomalies and the canonical SHA256 `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`. This new line never silently fixes errors to make distance or vegetation associations look significant.

## Pipeline (all steps before outcome access)

0. `fetch_pinned_naamp_sources.py` (optional public-source fetch): download SHA256-pinned `Runs.csv`, `Stops.csv` and the coordinate CSV from ScienceBase. **Never fetch `Counts.csv`.** The GitHub source-audit workflow runs this first.
1. `audit_site_coordinates.py`: ingest the original `RouteNumber,SiteID,lat,lon` CSV, verify checksum, quarantine malformed coordinates and geometrically implausible routes; do **not** substitute neighbouring-site locations. The 25/50 km flags are **review gates**, not ecological claims or proof of invalidity. Log held/accepted counts by geography before outcome access.
2. `prepare_survey_site_calendar.py`: join accepted locations to NAAMP `Runs.csv` and `Stops.csv` using physical site IDs; never load `Counts.csv`. This is a *coverage calendar* and **not** the manuscript's exact eligible sample.
3. `extract_nlcd_buffers.py`: use year-matched annual NLCD GeoTIFFs to extract class shares in **100 m and 500 m** buffers around accepted sites. Require >=80% valid pixel coverage; never classify no-data as non-water. Source rasters and checksums must be pinned before outputs are used.
4. Geospatial DSWE preprocessing (data acquisition still pending): classify per-scene water using explicit official band definitions and QA, construct `dswe_scenes.csv` (`RouteNumber,SiteID,radius_m,scene_id,acquisition_date,valid_pixel_n,water_pixel_n`), and run `summarize_dswe_visits.py` to compile **500-m**, **strictly earlier**, **30-day** site-survey water fractions. Require at least 50 valid scene-pixel observations, while preserving scene and cloud-coverage audits. This is a coverage/proxy choice, **not** proof the water state on the calling night was known.
5. Feasibility audit only: summarize retention/geometry flags by study geography, year and ecological setting, then **freeze a separate inference protocol** (covariates, missing-data exclusions, outcome, testing family, blocked validation and independent replication) before linking acoustic outcomes.

### Frozen candidate vegetation metrics

- 100-m and 500-m fractions: `forest` [41,42,43], `woody_wetland` [90], `emergent_wetland` [95], `open_water` [11], `developed` [21–24], `shrub` [52], `grass_herb` [71,72], `agriculture` [81,82].
- Do not equate annual forest fraction with continuous canopy cover, wetland cover with water depth, or the 500-m mean with the focal microhabitat.
- Evaluate composition and availability before inferring changes. The broad categories are collinear; a later model must preregister regularization/reference categories and avoid interpreting all coefficients as independent causal effects.

### Proposed model comparison (explicitly future work)

M0: species-specific meteorology + previously observed SiteID calling propensity + dry-state persistence + matched activation magnitude (historical reference only).

M1: M0 + static/annual vegetation/wetland structure and species interactions.

M2: M1 + *measured event-level surface inundation* + taxon-specific local-water interactions.

M3: M2 + route-night taxon state; test if residual within-taxon configuration still exceeds a simulation envelope and if recurrent-site targeting attenuates.

The primary target is change in **conditional taxon-by-site configuration** at matched response magnitude, not simply an improvement in prediction of marginal CallingIndex. All geographic/temporal train/test splits must be decided before frog-outcome inspection. Same NAAMP data cannot be portrayed as independent replication. DSWE+NLCD are imperfect satellite proxies; if their coverage is low, the valid conclusion is **non-estimable**, not no vegetation/water effect.

## Local execution

Requirements: Python 3.10+, NumPy, rasterio, shapely for NLCD; standard library only for the other three scripts. All scripts intentionally have **no API calls**. Their inputs are downloaded **separately**, pinned and audited.

```bash
python scripts/fetch_pinned_naamp_sources.py --out data/source

python scripts/audit_site_coordinates.py \
  --coordinates data/source/NAAMP_SiteCoordinates.csv \
  --expected-sha256 f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83 \
  --out data/qc

python scripts/prepare_survey_site_calendar.py \
  --runs data/source/Runs.csv --stops data/source/Stops.csv \
  --accepted-coordinates data/qc/accepted_coordinates.csv \
  --out data/qc/survey_site_calendar.csv

python scripts/extract_nlcd_buffers.py \
  --accepted-coordinates data/qc/accepted_coordinates.csv \
  --raster-template 'data/nlcd/annual_nlcd_{year}.tif' \
  --years 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 \
  --radii-m 100 500 --out data/qc/nlcd_site_year.csv

python scripts/summarize_dswe_visits.py \
  --site-calendar data/qc/survey_site_calendar.csv \
  --dswe-scenes data/qc/dswe_scenes.csv \
  --radius-m 500 --lookback-days 30 --min-valid-pixels 50 \
  --out data/qc/dswe_site_visit.csv

python -m unittest discover -s tests -v
```

These commands require independently obtained remote-sensing data. There are **no actual processed NAAMP coordinates, NLCD GeoTIFFs or DSWE scenes in this code-only package**. A separate GitHub Actions job attempts the pinned public-source download and writes QC receipts; its success is not assumed or reported here. Passed synthetic tests prove implementation behavior, not environmental coverage in the research sites.

## Parent-project boundary

- `frogcs` RC6: **frozen**. No README, manuscript, figures, claims or analyses in the submitted package are changed.
- Historical WFTS replication: **not pursued** under `revision/WFTS_NOT_PURSUED_2026-10-05.md`; do not reinterpret it as pending.
- Any later frog-outcome link must be explicitly labelled a new, independently designed exploratory/confirmatory sequence; retrospective reuse of NAAMP cannot count as external confirmation.
