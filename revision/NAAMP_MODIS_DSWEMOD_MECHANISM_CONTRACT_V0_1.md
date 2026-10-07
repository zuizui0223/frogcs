# NAAMP MODIS DSWEmod partial-inundation mechanism contract v0.1 — 2026-10-07

**Status:** frozen after the negative JRC MonthlyHistory open-water result and before any DSWEmod raster value is extracted at a focal NAAMP SiteID or joined to frog outcomes.

## Scientific role

The endpoint remains the existing within-taxon multi-site concentration.

JRC monthly visible open-water change did not explain the focal concentration. Landsat Collection 2 Level-3 DSWE metadata coverage is adequate but its STAC raster assets require EarthExplorer authentication in the current execution environment.

DSWEmod is therefore evaluated as a distinct public hydrological measurement, not as a substitute relabelled as Landsat DSWE.

Question:

> Does monthly partial/potential wetland state from the MODIS-adapted DSWE algorithm explain the chorus concentration that monthly visible open-water extent did not?

## Source

USGS data release DOI 10.5066/P9UMFBDE:
National Surface Water Maps using Daily MODIS Satellite Data for the Conterminous United States, 2003–2019.

Use annual DSWEmod GeoTIFFs for 2003–2015 only.

Official classes:
- 0 = not water
- 1 = high-confidence water
- 2 = moderate-confidence water
- 3 = potential wetland
- 4 = low-confidence water/wetland
- 9 = no data

Each annual raster has 12 bands corresponding to January–December.

## Temporal population

Because DSWEmod begins in 2003, only existing principal-comparator pairs for which both focal surveys occur in 2003–2015 are eligible.

This temporal restriction is determined by product availability before raster values are read.

## Coordinate gate

Use only routes passing the existing strict response-blind remote-sensing geometry gate.

## Spatial support

Native DSWEmod resolution is 250 m.

Primary support: **500 m radius** around each physical SiteID.

Rationale: a 250-m-radius buffer contains only about three native 250-m pixels and is too sensitive to official-coordinate error and pixel phase. A 500-m buffer samples roughly an order of magnitude more native pixels while remaining local relative to >=0.8-km NAAMP stop spacing.

Named sensitivity: 250 m radius.

The 500-m primary cannot be replaced by 250 m based on outcome direction.

## Primary exposure

For each SiteID x focal survey month, among valid class 0–4 pixels:

DSWEmod_123 = fraction of pixels in classes {1,2,3}.

This includes potential wetland class 3 and excludes only low-confidence class 4 from the numerator.

For each matched wetter–drier focal pair at the same SiteID:

delta_DSWEmod_123 = DSWEmod_123_wetterSurvey - DSWEmod_123_drierSurvey.

## Fixed class sensitivity

DSWEmod_1234 = fraction of valid class 0–4 pixels in classes {1,2,3,4}.

This is secondary only.

## Validity

A SiteID-month is valid when >=50% of candidate buffer pixels are valid DSWEmod classes 0–4.

No-data class 9 is excluded from both numerator and denominator.

No spatial or temporal interpolation.

## Coverage gate

Before frog endpoint readback require all ten focal SiteIDs valid in both focal surveys for at least:
- 1,500 pairs
- 300 routes
- 15 states

If the gate fails, classify DSWEmod as coverage-inconclusive. Do not change radius, class set, or valid-pixel rule.

## Mechanism model

Use the same M0 principal comparator and concentration simulation machinery as the JRC mechanism test.

DSWEmod coefficients are:
- species-specific
- trained on the opposite deterministic route fold only
- estimated from species × RunID × SiteID cells
- controlled for log(1+DaysSinceRain), mean air temperature, annual sine/cosine, State and RunNumber
- zero below the existing 20-positive-cell / 5-positive-route estimability gate
- binomial GLM with ridge fallback alpha=0.01

Before fitting, DSWEmod_123 is centered first by SiteID and then by RunID, so the coefficient targets local temporal inundation variation rather than static wetland identity or route-wide hydrological state.

For focal-pair generation, apply the cross-fitted coefficient to same-SiteID delta_DSWEmod_123, then retain unchanged pair-level total-incidence matching.

## Primary diagnostic

On the identical DSWEmod-complete sample compare:
- M0 conditional concentration residual
- M_DSWEmod conditional concentration residual
- fraction residual removed
- null residual 95% interval
- plus-one upper-tail P

DSWEmod is sufficient only if the residual no longer exceeds the simulated upper 95% bound.

## Strong-chorus secondary

Only after the concentration result is frozen, test whether delta_DSWEmod_123 is larger at wet-survey CI>=2 sites than at other focal sites within pair × taxon.

This cannot rescue a failed concentration mechanism.

## Interpretation boundary

A positive result supports partial/potential wetland state as a generator of reproductive acoustic configuration.

A negative result weakens monthly remotely sensed surface-inundation explanations at both 30-m visible-open-water and 250-m DSWE-class scales. It does not test water depth, water temperature, soil moisture, dense-canopy water, demographic readiness, or social facilitation.

CallingIndex is reproductive acoustic activity, not reproductive success.
