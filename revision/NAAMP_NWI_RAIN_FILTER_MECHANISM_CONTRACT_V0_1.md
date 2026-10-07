# NAAMP NWI rain-filter mechanism contract v0.1 — 2026-10-07

**Status:** frozen after satellite surface-hydrology mechanisms were negative and before any NWI habitat value is joined to frog outcomes.

## Scientific role

This is a distinct landscape-mechanism follow-up, not a retuning of JRC or DSWEmod.

Question:
> Does static wetland hydrogeomorphic type determine where a common rainfall pulse is converted into reproductive acoustic activation?

The existing within-taxon concentration endpoint remains unchanged.

## Why this is distinct from prior SiteID propensity

Strictly-prior species × SiteID propensity represents persistent baseline use of each physical location.

NWI is tested only as a modifier of the rainfall response: a static wetland class may make a site more or less responsive to the same rain event even after its baseline use is represented.

## Source

U.S. Fish & Wildlife Service National Wetlands Inventory Wetlands feature layer, official REST service:
`https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0`

Use fields `ATTRIBUTE` and `WETLAND_TYPE` plus polygon geometry.

## Spatial rule

For each strict-coordinate-gate SiteID:
1. query NWI polygons intersecting a 500-m distance search from the stop coordinate;
2. if one or more polygons are returned, choose the polygon with the smallest geodesic distance from the stop to the polygon boundary/interior; a polygon containing the stop has distance zero;
3. ties are broken by largest polygon area within the 500-m search circle, then by lexicographically smallest ATTRIBUTE code;
4. if no polygon occurs within 500 m, classify the stop as `no_NWI_wetland_500m`.

No radius search is allowed after outcome readback.

## Primary habitat grouping

Use the NWI `WETLAND_TYPE` field without outcome-driven regrouping.

Primary broad levels expected from the official renderer include:
- Freshwater Emergent Wetland
- Freshwater Forested/Shrub Wetland
- Freshwater Pond
- Lake
- Riverine
- Estuarine/Marine categories where present
- no_NWI_wetland_500m.

Rare levels are not merged after readback; they receive zero interaction if below the estimability gate.

## Mechanism model

M0 = existing principal comparator:
- cross-fitted species rainfall response;
- strictly-prior species × SiteID propensity;
- dry-state persistence a=0.75;
- pair-level total wet-incidence matching.

M_NWI adds a **species-specific rainfall × NWI wetland-type interaction**.

Training uses only the opposite deterministic route fold.

For each species and wetland-type level, estimate the additional dryness/rain response relative to the reference habitat while controlling for State, RunNumber, mean air temperature and annual sine/cosine.

Estimability gate for a species × habitat interaction:
- >=20 positive stop-cells in that habitat;
- >=5 positive routes containing that habitat.

Non-estimable interactions are zero.

For a focal pair, the common rain contrast is multiplied by each stop's cross-fitted species × wetland-type interaction, then the unchanged pair-level common shift matches observed total wet incidence.

Thus NWI is tested on **where** activation occurs, not how much total activation occurs.

## Coverage gate

Before frog endpoint readback require:
- NWI query success for >=90% of focal physical SiteIDs in the strict-coordinate principal universe;
- >=1,500 focal pairs with all ten stops assigned either an NWI wetland type or the explicit `no_NWI_wetland_500m` class;
- >=300 routes;
- >=15 states.

HTTP/query failures are missing and are not converted to `no_NWI_wetland_500m`.

## Primary diagnostic

On the identical NWI-complete sample compare M0 and M_NWI using the existing conditional concentration statistic, 1,000 simulations, and unchanged residualization.

Report residual removed:
`(residual_M0 - residual_M_NWI) / residual_M0`.

NWI habitat filtering is sufficient only if the M_NWI residual no longer exceeds its simulated upper 95% bound.

## Interpretation boundary

Support would mean that landscape wetland type filters the spatial expression of a rainfall pulse.

It would not show that NWI type itself changes through time, nor establish water depth, water temperature, demographic success, or unique causal mediation.

## Anti-tuning

After NWI values are joined to frog outcomes, do not change:
- 500-m search radius;
- nearest-polygon rule;
- WETLAND_TYPE as the primary grouping;
- interaction estimability thresholds;
- route folds;
- a=0.75 anchor;
- concentration endpoint;
- pair-level total-incidence conditioning.
