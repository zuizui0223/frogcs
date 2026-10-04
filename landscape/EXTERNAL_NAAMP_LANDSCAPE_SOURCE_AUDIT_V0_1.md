# External NAAMP landscape-source audit v0.1

## Purpose

Identify external, independently generated landscape layers that can turn the post-RC6 route-topology result into a genuine behavioural-landscape analysis without repairing the known-bad NAAMP coordinate table from frog outcomes.

## Source 1 — Marsh et al. 2017 / Dryad

Dataset:
- Marsh et al. 2017, Dryad DOI: 10.5061/dryad.8ns60
- file: `DDI_Marshetal.csv`

Published usage notes report:
- 587 NAAMP survey sites;
- unique SiteID identifiers;
- landscape variables measured within 300 m, 600 m, 1 km, 5 km and 10 km buffers;
- wetland proportion;
- impervious surface;
- forest, developed and agricultural cover;
- total/primary/secondary/other road length;
- survey count, years sampled, traffic and noise measures.

Biological-outcome access is **not needed** for the first step.

First authorized task:
- acquire the file;
- inspect schema;
- join SiteID values to the RC6 focal physical SiteIDs;
- report coverage only.

Do not inspect frog response associations during this coverage audit.

## Source 2 — Marsh & Cosentino 2019 nested NAAMP landscape data

The published methods describe a nested dataset with:
- **406 NAAMP routes** from 13 states;
- multiple stops per route;
- stops **1, 4, 7 and 10** retained to limit overlap among buffers;
- 1-km landscape characterization around each retained stop;
- forest, agriculture, development, wetland area and road density;
- landscape layers derived from NLCD, NWI and TIGER.

This source is particularly valuable because it contains repeated stops within routes rather than one landscape value per route.

A second compilation in the same study used one random stop from **567 routes**; that version is useful for broad route coverage but cannot quantify within-route landscape heterogeneity by itself.

## Response-blind coverage gate

Before any ecological response is joined, freeze:

1. number of external SiteIDs that match the RC6/landscape focal SiteIDs;
2. number of matched routes;
3. number of routes with >=2 matched external stops;
4. number of routes with all of StopNumbers 1,4,7,10 represented where applicable;
5. state coverage;
6. missingness by landscape variable and buffer scale.

No biological moderator model is authorized until this coverage table is written to a receipt.

## Candidate landscape metrics

If stop-level overlap is sufficient:

### Local habitat
- wetland proportion / area;
- forest cover;
- agriculture;
- developed land;
- impervious cover;
- road density.

### Within-route landscape heterogeneity
For each landscape variable:
- route mean;
- route SD;
- range;
- pairwise absolute difference among retained stops.

### Landscape similarity of active sites
For each taxon × route-night:
- mean pairwise environmental distance among active sites;
- environmental similarity relative to exact-k fixed-q site subsets.

### Recurrent-site landscape contrast
Compare recurrent strong-chorus sites with non-recurrent focal sites in:
- wetland context;
- development/road exposure;
- route-relative habitat rank.

## Future biological questions

These are not yet authorized tests.

Potential questions after the coverage gate:

1. **Does landscape heterogeneity preserve spatial selectivity?**
   - prediction: routes with stronger habitat heterogeneity show larger q-conditioned topology holes/components or stronger recurrent-site targeting.

2. **Do deep active sets connect environmentally similar sites?**
   - prediction: active-site environmental distance is lower than exact-k fixed-q expectation.

3. **Do recurrent strong-chorus sites form a habitat-defined backbone?**
   - prediction: recurrent sites occupy consistent within-route wetland/land-use ranks even after taxon-specific history is represented.

4. **Does development disrupt multi-site organization?**
   - exploratory moderator only unless a directional hypothesis is frozen before response readback.

## Coordinate boundary

The external landscape datasets are valuable because their landscape summaries were generated independently of the current frogcs outcome analyses.

They do **not** automatically validate the raw USGS latitude/longitude table.

Exact geographic-distance analysis remains blocked until coordinate concordance is independently established.

## Current status

- Stage A route-topology geometry: RUNNING under frozen contract.
- Stage B exact geographic geometry: BLOCKED by coordinate validation.
- Stage C external landscape covariates: SOURCE IDENTIFIED; response-blind acquisition/coverage audit pending.
