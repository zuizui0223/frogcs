# E3 public Landsat access preflight repair v0.3 — 2026-10-08

**Response-blind source-only repair.** The frozen E3 NDMI biological contract v0.1 and access repair v0.2 remain unchanged.

The v0.2 Planetary Computer source preflight verified every required Landsat C2 L2 image/QA asset for unrelated 2008 and 2014 test points, but the 2002 test stopped during signing/access after the deterministic lexical selector chose a Tier-2 (`_T2`) Landsat 7 item. It did not inspect NAAMP outcomes, focal coordinates, NDMI values, or mechanism residuals.

This v0.3 repair changes **only arbitrary-era source preflight selection and transient network handling**:

1. Retain the same three non-NAAMP test points, historical windows, STAC collection `landsat-c2-l2`, public signing API, four required asset roles, and raster-value/geometry checks.
2. Prefer USGS Tier-1 (`_T1`) items over Tier-2, then lexicographic item ID. This is a source-quality preference, not a frog-result-based scene choice.
3. Try at most **three** deterministic matching items per era, stopping at the first for which all four TIFF roles are accessible and sampleable. Unsuccessful item is recorded by item ID and sanitized error **type only**, never signed URLs.
4. Permit at most three attempts for transient STAC/signing network failures with fixed delays. Do not change search geography, dates, sensor family, pixel/QC rules, or the required three-era pass criterion.
5. E3 access PASS requires **all three eras** (2002, 2008, 2014) to pass. Otherwise stop as `E3_public_asset_access_inconclusive`. Never proceed to focal coverage on partial success.

No further alternate satellite index/sensor/radius/window may replace a failed E3. Source compatibility remains USGS Landsat Collection 2 Level-2 surface reflectance.
