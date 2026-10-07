> **Superseded:** this fallback proposal is superseded by `revision/NAAMP_MODIS_DSWEMOD_SOURCE_REPAIR_V0_3.md`, which freezes 2004 as source-unavailable after the official child link returned 404 and the 2.04-GB parent ZIP proved non-range-readable. No 2004 DSWEmod focal value was read.

# DSWEmod 2004 source-acquisition fallback — 2026-10-07

## Problem

The official 2004 ScienceBase child item exists and documents the 2004 DSWEmod raster, but its child-item GeoTIFF download URI currently returns HTTP 404 and reports size 0 in ScienceBase metadata.

USGS documentation states that the parent release ZIP contains all 17 annual DSWEmod images from 2003 through 2019, including 2004.

## Frozen fallback

For YEAR=2004 only:
1. attempt the official child-item GeoTIFF URI first;
2. if and only if it returns HTTP 404 / unavailable, access the official parent release ZIP from ScienceBase;
3. retrieve the ZIP member whose basename is exactly `DSWEmod_US_2004.tif`;
4. verify it opens as a 12-band EPSG:5070 250-m raster before focal extraction.

No other mirror, reconstructed raster, temporal substitution or neighboring-year value is authorized.

## Scientific boundary

This is a source-delivery repair only. It was specified after observing the 2004 HTTP 404 and before any 2004 DSWEmod focal raster value was available to the mechanism analysis.

It does not change the class definitions, spatial radius, temporal windows, coverage gates, route population or frog endpoint.
