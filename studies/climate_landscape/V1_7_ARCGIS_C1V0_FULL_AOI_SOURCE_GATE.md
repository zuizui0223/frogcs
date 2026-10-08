# Iowa 360417: homogeneous original Annual NLCD C1V0 pixel pilot (v1.7)

2026-10-08. Separate independent climate–landscape exploratory study. **Do not alter RC6.**

## Source-specific correction

The 2004 and 2014 GeoTIFFs successfully retrieved in the preceding public USGS/Esri ImageServer run [37753672602](https://github.com/zuizui0223/frogcs/actions/runs/37753672602) are **Collection 1.0**, explicitly named `Annual_NLCD_LndCov_{year}_CU_C1V0` and described by the service as Collection 1.0. They are **not Collection 1.1 or Collection 1.2**. The 2009 read in the earlier small-pilot run timed out. The old USGS GeoServer/WCS endpoint instead returned an XML exception `startTime is null` for all attempted temporal encodings. Do not reclassify source versions or call a WCS XML exception GeoTIFF.

## New bounded full-AOI source pilot

Use exactly the previously frozen ten DNR point coordinates (2001–2015 physical-station continuity independently verified at **zero** points) and the full EPSG:5070 bbox `[179220,2044410,184320,2056680]`, containing all ten stations plus 1km buffer. Request 2004, 2009, and 2014 categorical rasters through the **same** ArcGIS ImageServer service, verifying `OBJECTID`, original `Name` ending `C1V0`, `Year`, `Version`, a single U8 categorical band, numeric NLCD class codes, complete identical 30m grid, and source SHA256. Treat `0`/`255` as unknown and never as a dry wetland or 0% forest. Reject unexpected data or incomplete site buffer coverage.

Compute per-year land-cover fractions and paired same-pixel transitions for each of 10 stops × 250m/1000m buffers; do not treat 20 buffer summaries or 10 stops as independent ecological replicates. Threshold 80% paired valid native pixels for a comparison, set before reading any pixel differences. Preserve explicit fractional cover, changed pixel counts, forest→developed/agriculture and forest gains/losses. If only two image years are available, report a **partial two-year source-only result**, never invent a missing 2009 layer.

**Scientific authorization:** This is a *pipeline verification and mapped environmental description from Collection 1.0*, not the preferred official **C1.2** primary inference. C1.2 remains separately available through MRLC Viewer/ScienceBase/USGS S3 and must be retrieved and independently verified before any final multi-year environmental result. DNR's 2021 map and USGS archived coordinates can share an origin; no validated historical physical-station continuity, frog acoustic effects, reproduction, population occupancy or causal climate-effect conclusion is authorized here. NAAMP Counts.csv is not read. Existing v0.9 negative climate predictive results and JRC/DSWEmod hydrology negatives remain frozen.

## Run and verify

`python -m pytest -q studies/climate_landscape/tests/test_arcgis_c1v0_full_aoi.py`

`python studies/climate_landscape/scripts/arcgis_c1v0_full_aoi.py --stations studies/climate_landscape/reference_routes/iowa_dnr_360417_source_only_stops_v16.csv --out /tmp/iowa360417_nlcd_c1v0`

This workflow can report a failure due to service access, missing images or metadata mismatch; such failure is informative and must not be repaired by silently switching collection version or thresholds after reading outcomes.
