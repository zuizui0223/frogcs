# Iowa 360417: verified download AOI, not historical-site verification (v1.5)

Date: 2026-10-08. **Independent climate–landscape study. No RC6 amendment.**

## Completed source-only milestone

Original source evidence: [2021 Iowa DNR route 360417 PDF](https://www.iowadnr.gov/media/1999/download?inline=) and exact USGS 2017-published NAAMP Runs, Stops and Coordinates pin. Ten out of ten *numbered* state-map stops correspond to unique 2001–2015 archive SiteIDs (7271–7280); median state-map-to-archive coordinate separation 4.150m, maximum 5.844m. Verified without reading frog outcomes: [workflow 37749856908](https://github.com/zuizui0223/frogcs/actions/runs/37749856908); full source-only receipt [artifact 11537855061](https://github.com/zuizui0223/frogcs/actions/runs/37749856908/artifacts/11537855061); project record `receipts/IOWA_360417_STATE_MAP_USGS_COORDINATE_AGREEMENT_V1_5.json`.

**This is coordinate-source concordance, not independent verification of field-station continuity between 2001 and 2015.** The PDF is dated after those surveys and could share its coordinate source with USGS. Numbering consistency and numerical coordinate matches do not prove a physical pond was unchanged. Field-history verification remains 0.

## Completed extraction geometry

A locally generated distribution package `frog_iowa_360417_nlcd_aoi_v15_verified.zip` contains:

- `nominal_10_stops.geojson` and `nominal_10_stops.csv`: the ten DNR document stop coordinates and unambiguous original SiteIDs, all tagged **not historically field verified**;
- `singlepart_1km_buffer_envelope_aoi.geojson`: a singlepart WGS84 clipping polygon enclosing each site's true EPSG:5070 1-km radial buffer, plus **150 m clip-only guard** for projection/straightening; approximate AOI **42.04984 km²**;
- a source/hashes receipt and full reproducer `scripts/make_iowa_360417_aoi.py`, synthetic containment test, and user guide.

The *42 km² clipping envelope is not* the scientific sampling area. Reproject points/raster as appropriate, measure land classes separately at **250 m and 1 km radius around each numbered stop**, and remove the 150-m engineering guard from all ecological calculations. The full 1-km inclusion was actually tested after roundtripping the exported GeoJSON from EPSG:4326 back into the 5070 equal-area projection (ten/ten pass).

## Official raster acquisition boundary

Source must be **USGS Annual NLCD Collection 1.2 categorical GeoTIFF pixels**, not colored map-rendered WMS/PNG, and source product/version/metadata plus pixel completeness must be verified. [Official USGS access documentation](https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access) confirms the [MRLC Viewer](https://www.mrlc.gov/viewer/) accepts a **singlepart GeoJSON polygon** for geographic and year/product filtering and provides original clipped GeoTIFF by emailed retrieval instructions. The viewer requires user-directed interaction and an email address; **this study has not submitted a download request or received pixel files**. The direct USGS AWS S3 route is described as **requester pays**, not a free anonymous fallback. No older NLCD epoch mosaic, alternate product version, fake raster, or visually rendered classification substitute is authorized.

Pre-outcome environmental-only pilot: inspect candidate raster years 2004, 2009 and 2014 as predeclared five-year snapshots. Preserve original class codes, product version, confidence layer provenance, nodata area, grid alignment and the existing **at least 80% pairwise valid-pixel coverage** gate before any same-pixel land-conversion estimates. These years are **illustrative image years, not newly fitted frog-response lags**. Under no circumstances use a same-survey-year map or after-survey image to predict an earlier visit.

## Science / stop gates

- No actual 30-m NLCD pixels have yet been downloaded, intersected, or assessed.
- No forest-to-developed, agriculture, impervious surface, wetland persistence, or land change estimate yet.
- No evidence of delayed decline, adaptive tracking, acoustic-site legacy or frog movement from this source-only result.
- The earlier route-scale +past-five-year climate predictor was worse on the 2011–2015 heldout routes and **is frozen negative**; previous JRC and DSWEmod hypotheses were negative, also frozen.
- Historic NAAMP station relocation evidence, raw annual NLCD C1.2 pixels and cloud/source QA must be resolved independently before any ecological change inference.
