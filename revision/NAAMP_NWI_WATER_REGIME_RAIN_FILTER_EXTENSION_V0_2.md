# NAAMP NWI water-regime rain-filter extension v0.2 — 2026-10-07

**Status:** supersedes v0.1 for the primary NWI grouping before any NWI value from a focal NAAMP SiteID has been read.

## Reason for the change

The original v0.1 contract used the broad NWI `WETLAND_TYPE` field as the primary rainfall-effect modifier.

Before the NWI coverage workflow began, the official NWI REST service was found to expose a companion table `NWI_Wetland_Codes` (MapServer table 1) keyed by `ATTRIBUTE`. The table contains explicit fields:
- `WATER_REGIME`
- `WATER_REGIME_NAME`
- `WATER_REGIME_SUBGROUP`
- plus system/class definitions.

Official examples verified before NAAMP readback include:
- PEM1C -> C -> Seasonally Flooded;
- PUBHh -> H -> Permanently Flooded;
- R5UBH -> H -> Permanently Flooded.

Because the ecological question is whether hydrological regime filters conversion of a rain pulse into reproductive activity, the official water-regime field is more mechanistically aligned than broad wetland form.

## Primary NWI grouping

Primary grouping = official `WATER_REGIME_NAME` joined from `NWI_Wetland_Codes` by exact `ATTRIBUTE`.

For stops with no NWI polygon within the frozen 500-m rule, use the explicit level:
`no_NWI_wetland_500m`.

If a selected wetland polygon has an ATTRIBUTE that cannot be joined to the official code table or has no WATER_REGIME_NAME, that SiteID is missing for the primary analysis. Do not parse the code heuristically.

## Secondary grouping

`WETLAND_TYPE` is retained as a frozen secondary landscape grouping on the same primary-complete sample.

It cannot replace or rescue a failed water-regime primary analysis.

## Geometry and selection unchanged

- strict NAAMP coordinate gate;
- 500-m scientific search radius;
- NWI polygons from official Wetlands MapServer layer 0;
- distance/area geometry in EPSG:5070;
- nearest polygon, then largest area in the 500-m circle, then lexicographically smallest ATTRIBUTE tie-break;
- no-wetland is an explicit class only after a successful NWI query.

## Primary biological model

M0 remains the existing principal comparator.

M_REGIME adds species-specific rainfall redistribution by official WATER_REGIME_NAME.

All water-regime interactions are estimated jointly within the opposite deterministic route fold. Before fitting interaction slopes, log(1+DaysSinceRain) is centered within physical SiteID across the available training runs. The fitting model also controls for water-regime main effects, State, RunNumber, mean air temperature and annual sine/cosine.

Thus the interaction is learned from temporal changes in rainfall proximity at the same physical location, rather than from cross-site geographic differences in climatology.

Habitat-specific dryness slopes are fit in one design matrix. Regime levels meeting the existing interaction gate (>=20 positive stop-cells and >=5 positive routes for that species) are centered by their training-cell-weighted mean; the sign-reversed centered deviations are added to the M0 species wet-response slope.

Non-estimable regime interactions are zero and regime levels are never merged after readback.

Pair-level total wet incidence remains exactly matched, so the test concerns where activation is allocated rather than total activation amount.

## Frozen primary-interpretation sensitivity

M_REGIME_WETLAND_ONLY uses the same fitted WATER_REGIME_NAME interaction coefficients as M_REGIME, but sets the interaction deviation for the explicit `no_NWI_wetland_500m` level to zero at focal prediction.

All mapped NWI water-regime interactions remain unchanged and the same focal-pair sample is retained.

This sensitivity is not a separate fitted model and cannot replace M_REGIME. Its role is diagnostic:

- if M_REGIME and M_REGIME_WETLAND_ONLY both reduce the residual similarly, support is attributable to differences among mapped hydroperiod regimes;
- if only M_REGIME improves strongly, the effect is primarily mapped-wetland versus no-mapped-wetland contrast rather than water-regime structure.

## Frozen secondary biological model

M_TYPE repeats the same joint interaction procedure using official `WETLAND_TYPE` on the identical primary-complete focal-pair sample.

M_TYPE is reported regardless of direction but cannot supersede M_REGIME.

## Coverage gate

Before frog endpoint readback require:
- successful NWI polygon/no-wetland assignment plus official water-regime join for >=90% of focal physical SiteIDs;
- >=1,500 focal pairs with all ten SiteIDs primary-complete;
- >=300 routes;
- >=15 states.

HTTP/query failures and code-table join failures are missing.

## Diagnostics

For M0, M_REGIME, M_REGIME_WETLAND_ONLY and M_TYPE report:
- observed concentration beta;
- predicted concentration beta;
- conditional residual;
- simulated residual 95% interval;
- plus-one upper-tail P.

Primary residual fraction removed:
`(residual_M0 - residual_M_REGIME) / residual_M0`.

M_REGIME is sufficient only if its residual does not exceed its simulated upper 95% bound.

Secondary M_TYPE is interpreted only as supporting context.

## Temporal-map interpretation boundary

The NWI layer is a static/current mapping product, not a historical annual reconstruction of each wetland during the 2001–2015 NAAMP surveys.

Therefore WATER_REGIME_NAME is treated as a proxy for persistent hydrogeomorphic setting. The analysis asks whether that mapped persistent setting predicts differential response to historical rainfall pulses.

It does not assume that polygon boundaries, management, water regime, or wetland existence were unchanged at every site throughout 2001–2015.

## Interpretation

Primary support would show that mapped persistent hydroperiod regime predicts which local breeding sites are activated by a common rainfall pulse, even after persistent SiteID use and total activation magnitude are represented.

This would not mean the NWI regime itself changed between surveys, nor prove that the current NWI classification was identical during every historical survey.

## Anti-tuning

After focal NWI values are read, do not change:
- official WATER_REGIME_NAME primary grouping;
- the fixed no-NWI-zero regime-only sensitivity;
- WETLAND_TYPE secondary status;
- 500-m nearest-polygon rule;
- EPSG:5070 geometry;
- interaction gates;
- within-SiteID centering of log(1+DaysSinceRain);
- joint within-fold fitting;
- weighted-centering rule;
- route folds;
- a=0.75 anchor;
- concentration endpoint;
- pair-level total-incidence conditioning.
