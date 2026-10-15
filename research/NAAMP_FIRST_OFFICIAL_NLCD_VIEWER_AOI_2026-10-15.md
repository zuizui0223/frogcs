# Original C1V2 access: actual fixed NAAMP source-only AOI prepared

**Date:** 2026-10-15  
**Status:** SOURCE-ONLY GEOJSON DELIVERED, NO USGS C1V2 PIXELS OBTAINED.

## Objective and outcome-blind selection

To avoid national 1.4–7.7 GB archive downloads and unverified WMS colour
surrogates, supply the official MRLC Viewer with a single predetermined
study-relevant AOI. The existing exact-ten-source-coordinate × paper-history
cohort (358 routes, 2,422 pairs, all 20 states) was recovered **without**
loading NAAMP \`Counts.csv\` or any acoustic outcomes. The pilot route was
selected by the **lexicographically first** eligible State:RouteNumber key.

Actual outcome-blind pilot:
- **Route:** \`Delaware:210302\`
- **Eligible focal NAAMP survey pairs for this route:** 12, by Runs/Stops metadata.
- **Unambiguous source coordinates:** 10 physical SiteIDs.
- **AOI:** ten stop-centre convex hull + 1,000 metre outward buffer in EPSG:5070,
  exported as WGS84 GeoJSON polygon for MRLC Viewer import.
- **AOI area:** 127.4488 square kilometres.
- **GeoJSON SHA256:** \`307b1923fd221cc9f6dfe40f32b24ebbaee8cb27907e3d4b10f0c62e8248c3da\`
- **Field verification of 2001–2015 physical station continuity:** none.
- **Original C1V2 \`LndCov\` and \`LndCnf\` pixels:** not yet obtained.
- **Acoustic response/species identity used in selection:** none.

[GitHub Actions run 38718741980 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38718741980)

[Download source-only GeoJSON + manifest archive (artifact 11964571575)](https://github.com/zuizui0223/frogcs/actions/runs/38718741980/artifacts/11964571575)

The artifact contains:
- \`NAAMP_SOURCE_ONLY_LANDSCAPE_MRLC_VIEWER_AOI_V0_1.geojson\`
- \`NAAMP_SOURCE_ONLY_MRLC_VIEWER_AOI_V0_1.json\`

## Original C1V2 acquisition gate

Per [USGS Annual NLCD Data Access](https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access), the [official MRLC NLCD Viewer](https://www.mrlc.gov/viewer/) supports uploading GeoJSON AOIs and requesting clipped categorical GeoTIFF via email.

User-visible UI method if an AOI export is desired:
1. Open official MRLC Viewer, use AOI **GeoJSON upload** with the file above.
2. Select **2012 Land Cover and 2012 Land Cover Confidence**, **Collection 1.2 / C1V2** only. Product combination/version and AOI availability must be verified in the viewer; do not infer C1V2 merely from the site release announcement.
3. Enter the preferred delivery email in the official interface and inspect both delivered GeoTIFFs and metadata. No email request was submitted by this research branch.
4. Preserve original product metadata/provenance and raster hashes; verify categorical classes 41,42,43, class-confidence 1..100, identical CRS/grid/year and native 30-m original pixel identity.
5. Run \`research/scripts/nlcd_c1v2_forest_patch_features_v0_1.py\` only after the above source gate succeeds. Crop to the fixed route-wide domain, never infer forest connectivity from geometric buffer overlaps alone.

If the MRLC Viewer supplies C1V1 or an RGB/WMS map, STOP the original-C1V2 model. Do not switch sources or radii because of an outcome.

## What is and is not achieved

**Achieved:** real original-source geometry; deterministic source-only selection;
validated AOI polygon and SHA; transferable AOI import file.

**Not achieved:** actual Collection 1.2 class+confidence pixels; site-level
mapped forest fraction; forest patch connections; a forest × taxon effect;
closure of the frozen JAE conditional concentration residual.

The new exact-(K,N) generator is available for subsequent genuine
classification-value analyses, but the primary scientific test must additionally
control generic same-taxon coactivation before attributing any effect to forest
corridors. This remains a post-hoc new study and does not alter the submitted
JAE manuscript or its estimand.
