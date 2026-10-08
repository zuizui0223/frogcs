# Remote-sensing extraction contract — independent climate/landscape study v0.2

**Status**: executable offline CSV/pixel processing and an unexecuted GEE extraction recipe. The assistant has **not** accessed Earth Engine, downloaded USGS Annual NLCD GeoTIFFs, or linked validated NAAMP station positions to frog outcomes.

## Why two upstream extractors?

The USGS official **Annual NLCD Collection 1.2** (June 2026 update) has **30-m CONUS land cover for 1985–2025**. Its official distribution is through USGS EarthExplorer, MRLC/ScienceBase or AWS. **Do not silently substitute the older `USGS/NLCD_RELEASES/...` Earth Engine epoch product or unverified community mirrors**: collections, processing definitions, coverage and publication vintages can differ.

The **JRC `JRC/GSW1_4/MonthlyHistory`** Earth Engine collection has monthly 30-m images from March 1984 to December 2021. Per-pixel: `0=no data`, `1=nonwater`, `2=water`. Cloud or missing observation is not a dry pool.

### Step 0: audited, independently verified physical sites

```bash
python scripts/audit_coordinates.py \
  --coords pinned_usgs_sitecoordinates.csv \
  --expect-sha256 f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83 \
  --out coordinate_geometry_qc.csv --receipt coordinate_geometry_qc.json
```

The audit **does not verify** any coordinates. Prepare an **independent geographic evidence ledger** (from actual route descriptions, station records, maps, or traceable field sources) with: `route_id,site_id,latitude,longitude,coordinate_qc_status,verification_source_id`. Set `verified_external` **only** after independent verification of coordinates **and** stable site identity. An empty pilot verified ledger is preferable to pretending all 12,064 USGS rows are accurate. Preserve suspected relocations as different physical site entities after documented review.

Survey inputs are metadata only, e.g. `run_id,route_id,site_id,survey_date` from eligible, non-skipped NAAMP stops; do not read `Counts.csv` during geometry/export feasibility. Then:

```bash
python scripts/build_extraction_manifest.py \
  --events eligible_survey_site_dates.csv \
  --ledger independent_site_verification.csv \
  --output-dir outputs/manifest
```

Creates `verified_survey_events.csv`, `jrc_month_requests.csv`, `nlcd_year_requests.csv`, and a hash-bearing receipt. The requests contain **only image months/land-cover years strictly before the survey**. An eligible survey in July 2011 requests JRC months July 2010–June 2011, and official Annual NLCD for 2010 and 2005, for each 250-m and 1000-m circle.

### Step 1a: JRC monthly imagery by image, with no-data

Upload the CSV `jrc_month_requests.csv` as an Earth Engine table asset. Open `remote_sensing/jrc_monthly_export_gee.js`; replace the asset ID and set a YEAR with requested months; run the export and retain the task metadata. Combine the resulting annual CSVs **without dropping missing image/month rows**. GEE access is user-authenticated; the script has not been run in this environment.

Each JRC output row: `route_id,site_id,buffer_m,year,month,water_area_m2,nonwater_area_m2,nodata_area_m2,source_image_id,source_version`. Areas are computed from `pixelArea` at 30-m target scale and geographic buffer, not assumed exactly equal to nominal 250-m/1000-m circle area. Need to review edge pixels, image masking, georeferencing, effective observation fraction. No-data coverage and source image identifiers are retained.

### Step 1b: official Annual NLCD Collection 1.2 GeoTIFFs

Download official year-specific mosaics or mosaic relevant official tiles **without mixing versions**, then prepare an index:

```csv
year,raster_path,source_image_id,source_version
2005,/data/nlcd/c1_2/LC_2005.tif,USGS_ANNUAL_NLCD_C1_2_LC_2005,ANNUAL_NLCD_C1_2
2010,/data/nlcd/c1_2/LC_2010.tif,USGS_ANNUAL_NLCD_C1_2_LC_2010,ANNUAL_NLCD_C1_2
```

Run:

```bash
python scripts/extract_annual_nlcd.py \
  --year-requests outputs/manifest/nlcd_year_requests.csv \
  --raster-index nlcd_official_raster_index.csv \
  --out outputs/nlcd_landcover_areas.csv
```

The extractor reads only a small window around each independently verified station from the **locally available** categorical raster, requires projected CRS in meters, performs circle masking and emits metric class areas, sampled pixel count and no-data area. The official 16-class legend is grouped as: forest 41/42/43, agriculture 81/82, developed 21–24, wetland 90/95, open water 11, and other valid (12/31/52/71). It fails on unrecognized classification codes or missing years. Raster loading via approved local downloads is not automated.

**Note**: `extract_annual_nlcd.py` does not itself validate claims about the local raster's origin; the trusted input raster index, USGS retrieval metadata and pixel classifications must be archived alongside results. A legitimate source name in a CSV alone is not provenance verification.

### Step 2: temporal water/land features

```bash
python scripts/build_remote_sensing_features.py \
  --events outputs/manifest/verified_survey_events.csv \
  --monthly-water all_jrc_monthly_area.csv \
  --annual-landcover outputs/nlcd_landcover_areas.csv \
  --out outputs/site_event_remote_sensing.csv \
  --receipt outputs/site_event_remote_sensing_receipt.json
```

- **No survey-day or later images.** Water state uses last completed calendar month; rainfall/snow supplied by separate climate adapter uses strictly prior days. NLCD is **year preceding survey**; 5-year land-cover contrast is preceding year minus six years before survey.
- Water measures: last month visible water fraction, fraction of 12 prior months adequately observed, mean water fraction of **at least 4 valid months** (area extent, NOT hydroperiod); frequency of satellite-visible water in adequately observed months requires **at least 9 valid months**, with a nominal ≥900 m² water detection threshold; the 12-month lower/upper bounds keep missing months unresolved. Months with less than 50% observed pixel area remain NA, not classified dry.
- Land measures: forest, agriculture, developed, wetland and water fractions, local and landscape 250/1000-m scale, and prior-five-year fraction shifts.
- **Same species calling twice is not proof of individual site fidelity.** The site-level acoustic endpoint requires a separate frozen response-stage analysis, after geometry and exposure QC are complete.
- **Missing 30-m pond water is not proof of absence.** Microponds and shaded waters may be subpixel or cloud-limited; target a stratified ground-photo validation subset if possible.

## Sources and transparent ceilings

- Official USGS Annual NLCD v1.2: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover
- Official USGS land classes: https://www.mrlc.gov/data/legends/annual-nlcd-land-cover-legend
- Official JRC monthly history: https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory
- ORNL Daymet calendar caveat: https://daymet.ornl.gov/single-pixel-tool-guide

This study is separate from the locked RC6 frogcs submission; neither the previous post-lock landscape-direction analysis nor its negative result is reclassified here.

### v0.3: distinguish extent from persistence
- `water_mean_visible_fraction_valid_months_12m`: average visible water share among sufficiently observed monthly images (≥4 observed months). This is **area extent**, NOT hydroperiod or persistence.
- `water_detected_months_12m`: number of months meeting the ≥900 m² detectable water criterion, after adequate image coverage.
- `water_detected_fraction_observed_12m`: rate over observed months; NA unless at least 9/12 were adequately observed.
- `water_detection_lower_bound_12m` and `water_detection_upper_bound_12m`: if missing months were all dry vs all wet, bounding satellite-visible water detection (NOT true water availability at subpixel wetland scale).
- These bounds indicate observation uncertainty but cannot bound unobserved small ponds. The classifications derive from **retrospective** mapping; prior-year product labels do not guarantee the classification algorithm lacked later supporting Landsat scenes.
