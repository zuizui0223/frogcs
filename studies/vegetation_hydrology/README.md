# Vegetation × wetland hydrology and frog chorus configuration (independent feasibility line)

**Status 2026-10-23:** environmental-data feasibility and outcome-blind geospatial preprocessing only. **Not** a new NAAMP frog-outcome analysis, a replication, or a modification of the frozen `frogcs` RC6 paper. No numerical vegetation or hydrology effect is established. Never infer breeding success, true occupancy, individual movement or synchronous calling from NAAMP's ordered acoustic stop surveys.

## Full 2001–2015 environment panel — DONE, confirmed on real source data

- **USGS Annual NLCD Collection 1.2 / C1V2 (June 2026)** was retrieved directly from MRLC/USGS for all **15 years** 2001–2015. [2001 real source run](https://github.com/zuizui0223/frogcs/actions/runs/39960285085): success. [2002–2015 14-year extraction matrix](https://github.com/zuizui0223/frogcs/actions/runs/39960918335): **15/15 successful jobs**, including shared outcome-blind NAAMP input preparation.
- Exact USGS source SHA256 per year and original TIFF SHA256 are in each annual provenance receipt and the consolidated research artifact. All 64,779 calendar site-year keys matched, with **129,558 valid 100-/500-m categorical buffer rows**, 11,588 SiteIDs across 1,145 routes and 25 states. `Counts.csv` was never downloaded or analysed.
- **Ecologically descriptive but not frog-outcome tested:** Site-balanced mean at 100m vs 500m: developed 35.2% vs 15.6%; forest 21.3% vs 31.4%; agriculture 23.7% vs 32.3%. Route-clustered bootstrap developed difference +19.6 percentage points (95% +19.0–20.1), forest difference −10.1 points (95% −10.7 to −9.5). This is the roadside survey setting; **not** frog habitat preference.
- Of 7,010 sites followed at least 5 years apart, 500-m developed cover absolute first-to-last difference median 0.23 pp; only 1.28% changed by ≥10 pp. Annual land cover is comparatively stable at the measured scale, while the candidate wetland mechanism is **dynamic inundation**, still unmeasured.
- Full research receipt: [FULL_ANNUAL_NLCD_C1V2_PANEL_2001_2015_2026-10-23.md](receipts/FULL_ANNUAL_NLCD_C1V2_PANEL_2001_2015_2026-10-23.md). The locally assembled full panel CSV, time series, summary JSON and year source artifacts were exported as a downloadable research ZIP in the conversation.
- DSWE progression: `scripts/probe_dswe_site_survey_coverage.py` and `.github/workflows/vegetation_hydrology_dswe_metadata_pilot.yml` query the official Landsatlook `landsat-c2l3-dswe` catalogue for **strictly prior 30-day scene metadata** at a small sample of actual station-survey events. Presence of a scene does **not** establish usable cloud-free water pixels or true wetland depth.

**Scientific state:** full annual vegetation environmental measurement succeeded. Water/hydroperiod reconstruction and relation to frog chorus outcomes have not been performed. Main JAE RC6 is frozen and unchanged.

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
3. `extract_nlcd_buffers.py`: use year-matched annual NLCD GeoTIFFs to extract class shares in **100 m and 500 m** buffers around accepted sites; pass `--site-calendar` to process only actually visited physical site × year keys (64,779 in the verified outcome-blind frame, versus a 173,820 full grid). Require >=80% valid pixel coverage; never classify no-data as non-water. Source rasters and checksums must be pinned before outputs are used.
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

Requirements: Python 3.10+, NumPy, rasterio and shapely for NLCD. The analysis/preprocessing scripts read supplied local inputs; separate explicit source-fetch and STAC-probe scripts use public HTTP endpoints and never read `Counts.csv`. USGS source files are SHA-pinned.

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
  --radii-m 100 500 --site-calendar data/qc/survey_site_calendar.csv \
  --out data/qc/nlcd_site_year.csv

python scripts/summarize_dswe_visits.py \
  --site-calendar data/qc/survey_site_calendar.csv \
  --dswe-scenes data/qc/dswe_scenes.csv \
  --radius-m 500 --lookback-days 30 --min-valid-pixels 50 \
  --out data/qc/dswe_site_visit.csv

python -m unittest discover -s tests -v
```

These commands require source-verified local NLCD rasters (Collection 1.2 for final work) and later DSWE scenes. The code-only repository does not store whole remote-sensing mosaics or site coordinates. **Public-source retrieval, coordinate QC, site-year audit, one real original NLCD categorical pixel and a five-NAAMP-site 100/500-m buffer pilot have all passed GitHub Actions.** The real-pixel/pilot source is historical **C1V1**, solely an access/processing smoke test, not the proposed C1.2 final environment or a frog-result analysis. See `receipts/NAAMP_SITE_YEAR_FEASIBILITY_2026-10-23.md`, `receipts/USGS_NLCD_ORIGINAL_BYTE_ACCESS_2026-10-23.md` and `receipts/REAL_NAAMP_2001_NLCD_PILOT_2026-10-23.md`.

## Verified real-data feasibility (2026-10-23)

- [NAAMP source and five-site original NLCD buffer workflow: SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39935061682). 11,668 accepted/396 held physical-site keys; 64,779 observed site-year keys from 2001–2015; 5 actual year-2001 sampled sites × two radii, 10/10 buffers with sufficient pixels. All outcomes remain sealed.
- [Remote categorical pixel STAC/OSN read: SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39934759579): 206 Partial Content and C1V1 original-pixel read, not a rendered WMS image. **C1V1 is not C1.2**.
- [Geospatial synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/39934528768): 14 unit tests passed; dynamic hydrology and ecological model fitting remain unexecuted.

## Parent-project boundary

- `frogcs` RC6: **frozen**. No README, manuscript, figures, claims or analyses in the submitted package are changed.
- Historical WFTS replication: **not pursued** under `revision/WFTS_NOT_PURSUED_2026-10-05.md`; do not reinterpret it as pending.
- Any later frog-outcome link must be explicitly labelled a new, independently designed exploratory/confirmatory sequence; retrospective reuse of NAAMP cannot count as external confirmation.
