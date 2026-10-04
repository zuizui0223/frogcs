# NAAMP behavioural-landscape extension — scope v0.1

## Separation from RC6

This is a **post-RC6 exploratory landscape extension**.

It must not:
- change RC6 numerical endpoints;
- be merged into the locked RC6 scientific claim without a separate reopening decision;
- be described as independent confirmation;
- repair or reinterpret the previously invalidated exact-coordinate distance analysis after seeing frog outcomes.

RC6 authority remains:
- `release/jae-multisite-rc6`
- `submission/jae-multisite-v6`
- `revision/CURRENT_ENDPOINT_SCIENCE_LOCK_2026-10-04.md`

## Landscape question

RC6 established that response magnitude does not fully describe the realised multi-site pattern.

The landscape extension asks a more geometric question:

> **When a taxon's activity is expressed across several route stops, what shape does that active set take along the repeated route — a compact block, a broad continuous spread, or a spatially selective set of separated locations?**

This explicitly distinguishes configurations that the RC6 concentration endpoint treats as identical.

Example:
- active stops 1,2,3 and
- active stops 1,5,10

both have k=3, but very different route geometry.

## Stage A — route-topology geometry

Stage A requires no latitude/longitude coordinates.

For each dry-route-silent taxon with wet-state active stop set S among the ten ordered route stops:

- **k** = number of active stops;
- **span** = max(S) − min(S), in stop-number steps;
- **holes** = span + 1 − k, the number of inactive route positions inside the active-set hull;
- **components** = number of contiguous runs of active StopNumbers;
- **mean pairwise lag** = mean |i−j| over active-stop pairs.

Interpretation:
- large span = broad route-order extent;
- positive holes / multiple components = selective or discontinuous expression rather than one contiguous block;
- large mean pairwise lag = active sites are dispersed in route order.

The **primary Stage-A endpoint is q-conditioned holes excess among deep k≥4 activation clusters**.

Reason:
- k is fixed exactly;
- holes directly asks whether broad activation remains spatially selective;
- it complements, rather than duplicates, the existing k-depth and recurrent-site results.

Secondary metrics:
- span excess;
- component excess;
- mean-pairwise-lag excess.

## Null model

Use the same strongest fixed-q structure already used for the post-RC6 structural diagnostics:

- ERA5-eligible strictly-prior-history subset;
- route-cross-fitted environmental/species response;
- prior species × physical-SiteID history;
- dry-state persistence;
- matched wet incidence.

For each observed taxon × pair cluster:
1. fix observed k exactly;
2. enumerate all choose(10,k) stop subsets;
3. weight each subset by the exact conditional independent-Bernoulli probability implied by fixed q;
4. calculate the expected topology metric;
5. define observed excess = observed metric − q-conditioned expectation.

No coordinate threshold or frog-outcome-dependent geometry rule enters Stage A.

## Stage B — exact geographic geometry

Stage B is **gated**.

The pinned USGS SiteID coordinate table is not accepted as-is because a response-blind QC found gross transcription errors, including:
- one positive U.S. longitude;
- five routes with raw within-route maximum distance >100 km;
- several isolated coordinates inconsistent with their routes.

Therefore:
- no exact-km endpoint may be interpreted until a response-blind external coordinate-validation table is frozen;
- no manual correction may be chosen because it improves frog results;
- no post-result distance cutoff or winsorization is allowed.

A validated Stage B may later quantify:
- great-circle extent;
- mean pairwise geographic distance;
- distance-decay of dependence;
- recurrent-site network extent.

## Stage C — landscape composition and connectivity

An independent published NAAMP-derived dataset from Marsh et al. (Dryad DOI 10.5061/dryad.8ns60) reports SiteID-linked landscape variables for 587 NAAMP survey sites, including:
- wetland proportion;
- impervious surface;
- forest/developed/agricultural cover;
- road lengths;
- buffers from 300 m to 10 km.

Before any biological moderator test, Stage C requires a **response-blind SiteID coverage audit** against the RC6 focal SiteIDs.

Potential later questions, only if coverage is adequate:
- does within-route habitat heterogeneity predict stronger selective multi-site expression?
- do deep active sets preferentially link sites with similar wetland/land-use context?
- does road/development structure weaken recurrent-site coupling?

No Stage-C frog outcome may be read before the join and coverage rule are frozen.

## Spatial interpretation boundary

Stop-number topology is not exact Euclidean distance.

Under the NAAMP protocol:
- equidistant-route consecutive stops were exactly 0.5 miles apart;
- habitat-stratified consecutive stops were at least 0.5 miles apart.

Thus stop-number lag is a valid ordered route-topology axis and implies a minimum number of inter-stop segments, but it is not a direct straight-line distance measurement.

## Scientific status

Stage A: post-RC6, post-opening, exploratory but pre-specified before topology-metric readback.

Stage B: blocked pending independent coordinate validation.

Stage C: blocked pending response-blind external SiteID coverage audit.
