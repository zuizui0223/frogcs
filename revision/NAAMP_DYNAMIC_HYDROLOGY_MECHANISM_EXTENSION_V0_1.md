# NAAMP dynamic-hydrology mechanism extension v0.1

**Status:** post-RC6 mechanistic extension of the existing within-taxon concentration result.  
**Scope:** this is not a new ecological endpoint and does not reopen or redefine the RC6 concentration statistic.

## Mechanistic question

The existing focal result is:

- observed within-taxon concentration beta = 1.6503;
- principal comparator prediction = 1.3535;
- conditional residual = 0.2969.

The comparator already represents:
1. route-cross-fitted taxon-specific rainfall response;
2. strictly-prior taxon x physical-SiteID propensity;
3. dry-state persistence;
4. pair-level matching of total wet-state incidence.

This extension asks one mechanistic question:

> **Is the remaining concentration caused, wholly or partly, by dynamic local wetland state that varies among stops and survey events?**

The intended mechanism is:
> broad favourable conditions set the taxon-night opportunity for reproductive calling, while local hydrological state filters where that activity is expressed.

This is an observational mechanism test. Even complete residual removal would support hydrological mediation/filtering, not prove unique causality.

## Endpoint lock

The biological endpoint remains exactly the frozen RC6 higher-order within-taxon concentration statistic.

No new concentration metric, depth threshold, compactness statistic, distance metric, landscape fragmentation metric or alternative outcome may replace it.

The principal quantity to report is:

> **fraction of the same-sample principal concentration residual removed by adding dynamic local hydrology.**

A hydrology model is called *sufficient for the concentration pattern* only if the hydrology-augmented residual no longer exceeds its own simulated upper 95% null bound.

Partial explanation is reported continuously as the fraction of residual removed; no post-readback threshold will be invented for “partial support.”

## Stage 0 — coordinate authority, before remote-sensing extraction

Coordinate source is frozen to the official physical-SiteID table already used in frogcs:

- SHA256: `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`
- columns: `RouteNumber, SiteID, lat, lon`
- expected rows: 12,064
- expected route identifiers: 1,183.

No coordinate is manually repaired from frog outcomes or remote-sensing values.

A route is **coordinate-unsafe** and excluded from this extension if any of the following holds using geometry alone:

1. any coordinate is non-finite;
2. any coordinate falls outside the broad CONUS bounds 24 <= latitude <= 50 or -125 <= longitude <= -66;
3. the maximum great-circle span among physical SiteIDs assigned to that route exceeds 100 km.

The 100-km rule is deliberately conservative and is intended only to remove gross transcription failures already known to exist. Routes below this bound are not claimed to have perfectly accurate coordinates.

A focal pair is remote-sensing eligible only if every physical SiteID required for its ten-stop wet and dry matrices has an accepted coordinate. No coordinate imputation is allowed.

## Primary remote-sensing source

**JRC Global Surface Water Monthly History**, Landsat-derived, 30 m.

Primary extraction uses the monthly water classification:
- 0 = no data;
- 1 = not water;
- 2 = water.

The preferred historical asset is the version ending in 2015 (`JRC/GSW1_0/MonthlyHistory`) because it exactly spans the NAAMP study endpoint. If that legacy asset is technically unavailable, `JRC/GSW1_4/MonthlyHistory` may be used only as a technical replacement and the switch must be recorded before frog outcomes are joined.

## Primary local-hydrology variable

Spatial support is fixed at a **250-m radius** around each physical SiteID.

For each site and survey month:

`water_fraction = water pixels / (water + non-water pixels)`

No-data pixels are excluded from the denominator.

A site-month is valid only if >=50% of the 250-m buffer area has valid water/non-water classification.

### Pre-study monthly hydrological baseline

For each physical SiteID and calendar month, compute the mean water fraction from **1984-2000 only**.

At least 5 valid pre-study years are required for that calendar month.

Define:

`hydrology_anomaly = current survey-month water_fraction - 1984-2000 same-month mean water_fraction`

For every wetter-drier matched pair and stop define:

`delta_hydrology = wet-survey hydrology_anomaly - dry-survey hydrology_anomaly`.

This is the primary dynamic-hydrology exposure.

The pre-2001 baseline is fixed so that permanent/static wetness is separated from event/year-specific deviation and no post-2001 state is used to define the climatological reference.

## Named spatial sensitivities

Only two spatial sensitivities are allowed:
- 100-m radius;
- 500-m radius.

They are sensitivity analyses only. The 250-m result remains primary regardless of direction.

No radius may be chosen after outcome readback.

## Secondary temporal refinement

Landsat Collection 2 Level-3 Dynamic Surface Water Extent (DSWE), 30 m, may be used as a secondary temporal refinement.

The fixed exposure is the most recent cloud/shadow/snow-valid DSWE acquisition on or before the survey date within 16 days.

If unavailable, that site-event is missing. A 32-day window is a named sensitivity only.

DSWE is not allowed to replace the JRC monthly primary based on its result.

## Static wetland context

USFWS National Wetlands Inventory may be used only to characterize:
- mapped wetland/open-water presence around each SiteID;
- coarse wetland class.

NWI is not a primary mechanism variable because the existing prior species x SiteID propensity already absorbs persistent local suitability. Static NWI classes cannot be used to rescue an unsupported dynamic-hydrology result.

## Remote-sensing coverage gate — before frog outcome join

After coordinates and JRC values are extracted, but before joining any calling outcome:

Report:
- accepted/excluded routes;
- accepted physical SiteIDs;
- valid site-month fraction;
- number of the frozen 2,916 principal pairs for which all required primary hydrology values exist;
- corresponding route and state counts.

The dynamic-hydrology mechanism analysis proceeds only if the hydrology-complete intersection contains at least:
- 1,500 focal pairs; and
- 300 routes.

Otherwise classify the primary mechanism test as **hydrology_coverage_inconclusive**.

No coverage threshold may be relaxed after frog outcomes are joined.

## Model sequence to be frozen after response-blind coverage preflight

The final hydrology-generator parameterization will be frozen **after remote-sensing coverage is known but before hydrology is joined to frog outcomes**.

It must preserve the existing principal ingredients and pair-level incidence matching.

The sequence must contain:
- M0: same-sample frozen principal comparator;
- M1: M0 + dynamic local hydrology;
- optional M2: a predeclared taxon-specific hydrology-response extension if estimability is sufficient.

No landscape/topology endpoint is authorized.

## Decisive interpretation

If hydrology makes the concentration residual compatible with its null:
> dynamic local wetland state is sufficient to reproduce the previously unexplained concentration on the analysed sample.

If hydrology removes a substantial continuous fraction but residual dependence remains:
> dynamic local wetland state is a partial mechanism, but not the full generator.

If hydrology has little held-out predictive contribution and leaves the residual essentially unchanged:
> remotely sensed surface-water state, at the tested resolution, does not explain the concentration; finer hydrology, water temperature, vegetation, social state or demographic availability remain candidates.

## Anti-tuning rule

After frog outcomes are joined, do not change:
- coordinate source or coordinate exclusions;
- JRC product version except a previously documented technical fallback;
- 250-m primary radius;
- 1984-2000 baseline;
- monthly anomaly definition;
- valid-pixel threshold;
- coverage gate;
- endpoint;
- primary residual-removal estimand;
- named sensitivity radii/windows.

Any later alternative is a separate analysis and cannot replace this one.
