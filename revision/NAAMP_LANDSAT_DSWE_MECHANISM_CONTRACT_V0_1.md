# NAAMP Landsat DSWE local-inundation mechanism contract v0.1 — 2026-10-07

**Status:** frozen after the JRC MonthlyHistory current-open-water test was negative and before any DSWE value was extracted at a focal NAAMP SiteID or joined to frog outcomes.

## Scientific role

The existing concentration endpoint remains unchanged.

JRC 250-m monthly visible open-water change did not explain the focal concentration on its coverage-qualified sample. DSWE is therefore a change in hydrological measurement, not a retuned version of the JRC open-water endpoint.

The question is:

> Does acquisition-scale partial/local inundation, including potential wetland signal, explain the within-taxon concentration that coarse monthly open-water extent did not?

## Source

USGS Landsat Collection 2 Level-3 Dynamic Surface Water Extent (DSWE), STAC collection `landsat-c2l3-dswe`.

Use the Interpreted Layer with All Masks Applied (INWAM), because it incorporates cloud and cloud-shadow masking.

Official DSWE interpreted classes:
- 0 = not water
- 1 = high-confidence water
- 2 = moderate-confidence water
- 3 = potential wetland / mixed vegetation-water signal
- 4 = low-confidence water or wetland
- 9 and fill/masked values are not valid land/water observations for the focal fraction.

## Spatial support

Primary buffer: 250 m around the same strict-coordinate-gate physical SiteID.

Named sensitivities: 100 m and 500 m only.

## Temporal rule

For each focal survey date and SiteID:

1. Search DSWE acquisitions with acquisition time on or before the survey date and no more than 16 calendar days earlier.
2. At the 250-m buffer, calculate the fraction of valid INWAM pixels for each candidate acquisition.
3. A candidate acquisition is usable only if >=50% of buffer pixels are valid DSWE classes 0–4.
4. Choose the usable acquisition closest in time to the survey date.
5. If two acquisitions are equally close, choose the lexicographically smallest STAC item ID.

No post-survey imagery is used in the primary analysis.

Named temporal sensitivity: same rule with a 32-day lookback. It cannot replace the 16-day primary based on outcome direction.

## Primary DSWE exposure

For the selected acquisition:

`DSWE_123 = n(INWAM class in {1,2,3}) / n(valid class in {0,1,2,3,4})`

This deliberately includes class 3 potential wetland so that the test is not merely a second open-water analysis.

For each matched wetter–drier NAAMP pair at the same physical SiteID:

`delta_DSWE_123 = DSWE_123_wetterSurvey - DSWE_123_drierSurvey`

## Fixed class sensitivity

`DSWE_1234 = n(class in {1,2,3,4}) / n(valid class in {0,1,2,3,4})`

This includes the low-confidence class 4 and is secondary only. It cannot replace DSWE_123.

## Coverage gate before frog outcome readback

Primary 16-day DSWE mechanism proceeds only if all ten physical SiteIDs have valid selected acquisitions in both focal runs for at least:
- 1,500 principal pairs
- 300 routes
- 15 states

If this fails, classify the 16-day DSWE mechanism as coverage-inconclusive. Do not widen the primary window after outcome readback.

The 32-day sensitivity has its own reported coverage and remains sensitivity-only.

## Mechanism model

Use the same M0 principal comparator and simulation machinery as the JRC current-water test.

DSWE coefficients are:
- species-specific
- trained only on the opposite deterministic route fold
- estimated from species × RunID × SiteID cells
- controlled for log(1+DaysSinceRain), mean air temperature, annual sine/cosine, State and RunNumber
- zero for species below the existing 20-positive-cell / 5-positive-route estimability gate
- binomial GLM with the already frozen ridge fallback alpha=0.01

Before fitting, DSWE_123 is centered by physical SiteID and then by RunID, so the coefficient targets time-varying, locally non-uniform inundation rather than static wetland identity or route-wide wetness.

For focal-pair generation, apply the cross-fitted coefficient to same-SiteID wet-minus-dry delta_DSWE_123, then use the unchanged pair-level common shift to match total wet incidence.

## Primary diagnostic

On the identical DSWE-complete sample compare:
- M0 conditional concentration residual
- M_DSWE conditional concentration residual
- fraction residual removed = (M0 - M_DSWE) / M0
- simulated residual 95% interval and plus-one upper-tail P.

DSWE is sufficient only if the residual no longer exceeds its simulated upper 95% bound.

## Interpretation

A positive result would support local partial/inundated wetland state as a generator of chorus configuration after broad rainfall response and persistent SiteID propensity are represented.

A negative result would directly weaken remotely sensed surface inundation at both monthly-open-water and acquisition-level partial-water scales, increasing the priority of water depth, water temperature, soil/substrate moisture, dense-vegetation hydrology, demographic readiness, or social state.

CallingIndex remains reproductive acoustic activity, not reproductive success.

## Anti-tuning

After focal DSWE values are extracted, do not change:
- INWAM as the primary layer
- classes 1–3 as the primary positive set
- 250-m radius
- on-or-before 16-day primary window
- >=50% valid-buffer rule
- nearest-valid acquisition rule
- coordinate gate
- route folds
- coefficient estimability rule
- concentration endpoint
- total-incidence conditioning.
