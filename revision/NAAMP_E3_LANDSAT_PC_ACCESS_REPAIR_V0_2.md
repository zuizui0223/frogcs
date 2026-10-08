# E3 Landsat C2L2 source-access repair — Planetary Computer v0.2 (2026-10-08)

## Scope and reason

The frozen E3 science contract remains
`revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md`.

The first outcome-blind USGS LandsatLook access preflight (GitHub run 37705627835) retrieved historical Landsat scene metadata but the raster asset URLs returned EarthExplorer HTML rather than GeoTIFF bytes. Its preflight was classified `E3_public_asset_access_inconclusive`.

This addendum changes **only the public distribution endpoint** for the **same USGS Landsat Collection 2 Level-2 Surface Reflectance science product**. It does not change the scientific population, the spectral index, the acquisition window, pixel QC, the spatial radius, or any modeling decision.

## Authorized equivalent source

Microsoft Planetary Computer STAC collection:
`https://planetarycomputer.microsoft.com/api/stac/v1`, collection `landsat-c2-l2`.

The STAC asset roles map to the frozen sensor-specific USGS bands as follows:

- `nir08`: near-infrared (Landsat 5/7 SR_B4; Landsat 8 SR_B5);
- `swir16`: shortwave infrared 1 (Landsat 5/7 SR_B5; Landsat 8 SR_B6);
- `qa_pixel`: Landsat C2 QA_PIXEL;
- `qa_radsat`: Landsat C2 QA_RADSAT.

Asset URLs are signed using the Planetary Computer's public SAS signing API. No private subscription key is used. Temporary SAS tokens are never saved in receipts.

The primary NDMI remains `(NIR-SWIR1)/(NIR+SWIR1)`, with SR scale 0.0000275 and offset -0.2, and all unchanged QA rules from E3 v0.1.

## Outcome-blind access gate

Use precisely the existing preflight's three arbitrary non-NAAMP test points/eras (2002, 2008, 2014). For each:

1. Search the Planetary Computer `landsat-c2-l2` STAC collection.
2. Identify a historical TM/ETM+/OLI scene and exact expected band asset roles.
3. Sign NIR, SWIR1, QA_PIXEL, QA_RADSAT URLs via the documented public signing API.
4. Verify that all four signed URLs return TIFF data, not HTML/login redirects.
5. Using rasterio, confirm geotransform/CRS and sample a tiny window at the arbitrary point.
6. Report only asset role, image geometry, access status, and sample/QC code; never raw SAS URLs.

No focal NAAMP coordinates, survey outcomes, or concentration residuals are read.

Pass only if all three eras yield the four verified assets and a usable GeoTIFF sample. Otherwise record `E3_public_asset_access_inconclusive`.

Only after access PASS may the frozen 32-day/500-m/70%-pixel-availability coverage gate be run. E3 remains the final abiotic line, and no additional sensor, index, radius, temporal window, or subset is authorized.

## Comparability boundary

Platform and product equivalence are a precondition for use: STAC metadata must identify USGS Landsat Collection 2 Level-2 SR, not a separately processed reflectance dataset. If this cannot be confirmed, stop as source-incompatible.

No biological conclusion is authorized from an access-only preflight.
