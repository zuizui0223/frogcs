# NWI response-blind retrieval repair v0.3 — 2026-10-07

**Status:** frozen after the first NWI coverage preflight failed and before any NWI-modified frog endpoint was read.

## Observed failure mode

The first EPSG:5070 NWI preflight assigned 3,481 / 3,968 focal SiteIDs (87.73%), below the predeclared 90% coverage gate.

All 477 failed assignment rows were service/query failures rather than ecological absence:
- 337 rows: ArcGIS `Error performing query operation`;
- 140 rows: HTTP 503 Service Unavailable;
- 47 routes affected.

`no_NWI_wetland_500m` is already an explicit successful assignment and is not part of this repair.

## Fixed retrieval repair

The scientific spatial rule remains unchanged:
- 500-m radius;
- exact geometry in EPSG:5070;
- nearest polygon, then greatest area in the 500-m circle, then lexicographically smallest ATTRIBUTE;
- successful no-polygon query => `no_NWI_wetland_500m`.

Retrieval is repaired only as follows:
1. retry transient HTTP/ArcGIS requests;
2. attempt the existing route-envelope query first;
3. if that route query still fails, query each SiteID separately using a 0.01-degree retrieval envelope around the stop;
4. apply the unchanged exact 500-m EPSG:5070 polygon-distance rule to the returned candidates.

The 0.01-degree envelope is only an over-inclusive retrieval window. It does not alter the scientific 500-m eligibility distance.

The official NWI code table is also fetched with transient-error retries.

## Gate unchanged

The original gate remains:
- >=90% primary-complete focal SiteIDs;
- >=1,500 complete pairs;
- >=300 routes;
- >=15 states.

No threshold is lowered after seeing the first coverage result.

## Outcome boundary

No NWI-modified frog endpoint was calculated in the failed preflight because the coverage gate stopped the mechanism analysis.
