# NWI failed-only point-distance retrieval optimization v0.4 — 2026-10-07

**Status:** frozen after response-blind retrieval preflight and before any NWI-modified frog endpoint was read.

## Evidence for retrieval change

The first NWI coverage pass failed only because 477 SiteIDs on 47 routes had ArcGIS query failures:
- 337 `Error performing query operation`;
- 140 HTTP 503.

The original scientific coverage gate stopped all NWI frog analysis.

A response-blind preflight then tested the official layer's point-distance query at two previously failed SiteIDs and one control point. All three succeeded:
- failed test point 1: 12 candidate features;
- failed test point 2: 13 candidate features;
- control point: 20 candidate features;
- no transfer-limit flag.

## Retrieval optimization

For the already failed SiteIDs only:

1. query the official NWI polygon layer using the SiteID point in EPSG:4326;
2. request candidate polygons within 700 m using the service distance parameter;
3. request returned geometry in EPSG:5070;
4. reconstruct polygon holes as already frozen;
5. calculate exact stop-to-polygon distance and polygon area within the 500-m circle in EPSG:5070;
6. retain only polygons with exact distance <= 500 m;
7. apply the unchanged nearest-distance -> largest in-circle area -> lexicographic ATTRIBUTE tie-break.

The 700-m server query is deliberately over-inclusive and is only a retrieval window. The scientific search distance remains exactly 500 m.

## Everything else unchanged

- keep all 3,481 previously successful SiteID assignments fixed;
- retry only the 477 response-blind service failures;
- successful no-polygon result -> explicit `no_NWI_wetland_500m`;
- primary grouping = official `WATER_REGIME_NAME`;
- `WETLAND_TYPE` remains secondary;
- code-table join occurs once at aggregation;
- >=90% focal-SiteID completeness gate remains unchanged;
- >=1,500 pairs / >=300 routes / >=15 states remain unchanged;
- no threshold relaxation or result-driven regrouping.

No NWI-modified frog endpoint had been read when this optimization was frozen.
