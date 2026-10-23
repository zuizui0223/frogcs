# Strictly prior DSWE 30-day sample availability — access-bound result (2026-10-23)

## State
**Scene metadata: verified. Inundation pixels: inaccessible in current unauthenticated environment. No frog outcomes read.**

Official source: USGS Landsat Collection 2 Level-3 Dynamic Surface Water Extent (DSWE) `landsat-c2l3-dswe`, [collection STAC](https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l3-dswe), dataset DOI 10.5066/P9DPWBUS. The `INWAM` band is interpreted water with cloud, cloud-shadow and other masks applied, not a direct water-depth sensor.

[Final prior-scene metadata run 39964527520](https://github.com/zuizui0223/frogcs/actions/runs/39964527520):
- Source: independently SHA-pinned public `Runs.csv`, `Stops.csv`, accepted physical SiteID coordinates; no `Counts.csv`.
- Sample: 3 alphabetically selected states with surveyed physical sites in each year 2001, 2008, 2015 (total **9 sampled site-survey events**). One deterministic survey site/event chosen per state-year without frog response access.
- Query: Landsat C2-L3 DSWE STAC `INWAM` scene **strictly before** date of NAAMP survey (previous 30 days), local ~500m bbox. Metadata included complete returned vs matched counts; **9/9 sampled events had one or more prior scene metadata candidates**, and **9/9 queries had complete pagination** (matched == returned).
- Per survey event, returned candidate scene counts were **6,4,7** in 2001; **3,6,2** in 2008; **7,7,4** in 2015 (site-intersecting bounding boxes, not actual clear pixels).
- This demonstrates archive scene search availability at *a small, nonrepresentative sample*, not 64,779 site-year complete coverage or direct local hydrology.

[Attempted real 500m water-raster read 39964782002](https://github.com/zuizui0223/frogcs/actions/runs/39964782002):
- Attempted **6** STAC-linked `INWAM.TIF` remote COG assets across **3 actual sampled site-survey dates**.
- **0/6** actual rasters could be opened using anonymous `/vsicurl/`; Rasterio reported unrecognised image format. A separate direct endpoint fetch classified one source URL as **`login_required`**. Hence this is an **access blocker**, *not* evidence of zero surface water, zero cloud-free scenes or an ecological negative result.
- Pixel counts, water area, direct inundation, hydrological mediation and frog relationships are **NOT estimated**.
- Do not evade authentication, assume AWS requester-pays costs, or relabel STAC metadata as pixel measurements.

## What to do next without distorting the science
1. Keep the complete USGS Annual NLCD C1.2 site-year land-cover panel as the validated **relatively static habitat context**.
2. Seek public, permissible C2 DSWE annual proportions (USGS doi:10.5066/P16Q2FUD) or EC JRC Global Surface Water monthly data **as separate water-history proxies**. Record products' temporal granularity and source vintage. Monthly water state is not equivalent to day-of-survey inundation.
3. Only after pixel data are accessible may strictly prior event-level inundation be extracted with frozen class/QA/no-data definitions (INWAM valid 0–4, 9 cloud/cloud shadow, 255 fill; and predeclared 500m spatial buffer).
4. **Do not** run frog outcome analysis until environmental coverage is audited and a separate prospective test specification is fixed. Existing JAE RC6 remains unchanged.
