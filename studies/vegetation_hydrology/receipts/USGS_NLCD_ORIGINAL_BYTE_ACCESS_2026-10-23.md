# Original categorical NLCD raster access proof (2026-10-23)

## Status
**Completed technical validation; not an ecological effect estimate.** This independent branch keeps RC6 and `main` unchanged. Calling data were never loaded.

- [GitHub Actions original-byte and one-pixel read success](https://github.com/zuizui0223/frogcs/actions/runs/39934759579)
- USGS Water Mission Area [STAC item](https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection/nlcd/nlcd-LndCov/Annual_NLCD_LndCov_2001_CU_C1V1?f=json) confirms **Annual NLCD Collection 1.1** for 2001, source path `s3://hytest/nlcd/annual-nlcd-cu-c1v1/mosaic/Annual_NLCD_LndCov_2001_CU_C1V1.tif`.
- Open Storage Network anonymous HTTPS range (0–1023) yielded **206 Partial Content**, original TIFF magic and source size **1,367,828,587 bytes**.
- Rasterio `/vsicurl/` accessed a **single original categorical pixel** at fixed longitude **−80.0**, latitude **40.0**, returned categorical value **22** (developed low intensity in NLCD legend), projected Albers Equal Area with metre units; raster extent 160,000×105,000 native 30-m pixels. No full raster mosaic downloaded.
- This fixed smoke coordinate is **not** an NAAMP site, and this record does not support any statement about frogs or sampled habitat conditions.

## Source-version gates
The desired final environmental source is **Annual NLCD Collection 1.2 (June 2026, 1985–2025)**. The public STAC mosaic that passed this technical smoke is **C1V1**, not C1V2. Strictly refuse to label C1V1 pixels as C1.2. Historical source may validate remote access and extraction machinery, but final study environmental metrics must pin their own collection, DOI, pixel-product semantics and content hashes before response analysis.

The MRLC mirror HEAD candidates from `https://s3-us-west-2.amazonaws.com/mrlc/Annual_NLCD_LndCov_{year}_CU_C1V{n}.tif` returned HTTP **403** for 2001/2008/2015 and candidate n=0,1,2. That is an access-path failure, **not evidence that the product is unavailable**. The separately confirmed USGS STAC/OSN route succeeds for old C1.1 data.

## Next stage
Run a bounded, deterministic **2001 site-level pilot** using NAAMP `Runs.csv`, `Stops.csv` and accepted coordinate QC, without `Counts.csv`. Probe five sampled SiteIDs for 100-m and 500-m original categorical buffer values, record coverage status and source C1V1 label. Do not calculate frog associations or transfer ecological claims to C1.2.
