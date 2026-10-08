# E3 Planetary Computer final network access check v0.4 — 2026-10-08

**Final, outcome-blind source-access repair.** No NAAMP site locations, calling data, E3 NDMI values, or biological residuals have been read in any source preflight.

The frozen E3 science contract v0.1, USGS Collection 2 Level-2 source equivalence, NDMI definition, 500-m radius, 32-day prior acquisition, 70% QA-pixel requirement and biological coverage gates remain unchanged.

## Why one last technical check is justified

The v0.3 preflight (GitHub Actions 37711221995) verified all four public Landsat C2L2 assets for non-NAAMP test locations in 2002 and 2008. For 2014, the first Tier-1 candidate's NIR asset passed but a later public signing request raised HTTPError. Other 2014 Tier-1 candidates failed at signing. The v0.2 access check had independently verified all four 2014 assets. These observations suggest public signing/access instability, not an absence of USGS imagery.

## Deterministic final preflight procedure

- Use the same three unrelated 2002, 2008 and 2014 test locations and windows.
- Keep Tier-1-first lexicographic choice. Test the first matching Tier-1 item per era; **do not scan extra items** on a signing failure.
- Pause 3 seconds between public SAS signature requests.
- For transient HTTP 408/429/500/502/503/504, retry at most three times and honor capped Retry-After when supplied. Record numeric HTTP error code, not URL.
- Verify NIR, SWIR1, QA_PIXEL and QA_RADSAT as GeoTIFFs with rasterio/CRS transform and non-NAAMP point sample.
- Run this workflow **once in isolation** with no concurrent copies.
- Pass only if all three eras have all four verified asset roles. Otherwise E3 is **final source-inconclusive**; no change to the scientific NDMI/radius/time rules and no further source substitutions or retries.

The sole purpose is to prevent a transient public-service rate limit from being mistaken for Landsat data absence.
