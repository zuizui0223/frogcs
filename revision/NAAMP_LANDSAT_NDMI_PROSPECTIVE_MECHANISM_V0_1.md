# Landsat NDMI substrate/vegetation-moisture prospective mechanism v0.1 — 2026-10-08

**Status:** response-blind preparation only. Execute only if the frozen MOD11A1 nighttime-LST mechanism is unsupported or coverage-inconclusive.

## Scientific role

This is E3, the final authorized abiotic remote-sensing mechanism test in the frozen environmental-priority ledger.

Question:
> Does local vegetated/substrate moisture, not captured by open-water products, help determine where a common rainfall pulse is spatially expressed as frog reproductive acoustic activity?

The existing within-taxon multi-site concentration remains the response endpoint.

## Source

Primary product:
- Landsat Collection 2 Level-2 Surface Reflectance;
- Landsat 5 TM, Landsat 7 ETM+, and Landsat 8 OLI over 2001–2015.

Primary moisture index:
- NDMI = (NIR - SWIR1) / (NIR + SWIR1).

Sensor bands:
- Landsat 4–7: NIR band 4, SWIR1 band 5;
- Landsat 8: NIR band 5, SWIR1 band 6.

Collection 2 surface-reflectance scaling must be applied before calculating NDMI:
- reflectance = DN * 0.0000275 - 0.2.

## Pixel QA

Use QA_PIXEL to exclude:
- fill;
- dilated cloud;
- cloud;
- cloud shadow;
- snow.

For Landsat 8, also exclude high-confidence cirrus.

Exclude QA_RADSAT-saturated pixels.

Do not use the QA clear bit as the sole validity rule.

## Temporal rule

For each focal RunID search Landsat scenes on or before the NAAMP survey date.

Primary temporal window:
- 0 to 16 calendar days before the survey date;
- no future scene allowed.

Select the nearest acquisition date for which all ten focal SiteIDs have valid NDMI coverage under the frozen spatial rule.

The same Landsat acquisition date is used for all ten stops of a RunID.

If multiple sensors/scenes cover the route on that date, use all geometrically covering scenes and choose, for each stop, the lexicographically smallest item ID among valid items containing that stop. Do not select by NDMI value.

Do not widen the 16-day window after outcome readback.

## Spatial rule

Primary support:
- 250-m radius around each physical SiteID.

For each SiteID/acquisition:
- calculate the mean NDMI across valid 30-m pixels whose centers lie within 250 m;
- require >=50% of candidate 30-m pixel centers to be valid after QA;
- no spatial interpolation.

Named descriptive diagnostic:
- valid-pixel fraction.

No alternate radius is authorized for the primary mechanism.

## Dynamic local moisture variable

Training coefficients target local temporal variation, not static habitat identity.

Within each deterministic training route fold:
1. calculate SiteID mean NDMI across available focal RunIDs;
2. center NDMI within SiteID;
3. center again within RunID across the ten focal stops.

Fit species-specific local-moisture responses from these double-centered values.

At focal-pair prediction, apply the cross-fitted species coefficient to the same-SiteID wet-minus-dry raw NDMI difference; unchanged pair-level incidence matching removes common activation magnitude.

## Model

M0 = existing principal comparator.

M_NDMI = M0 + cross-fitted species-specific local NDMI response.

Training controls:
- log1p(DaysSinceRain);
- route mean air temperature;
- annual sine/cosine;
- State;
- RunNumber.

Estimability:
- >=20 positive stop-cells;
- >=5 positive routes;
- binomial GLM;
- ridge fallback alpha=0.01;
- zero coefficient when non-estimable or unstable.

## Coverage gate

Before frog endpoint readback require:
- >=1,500 complete focal pairs;
- >=300 routes;
- >=15 states;
- all ten focal SiteIDs valid in both focal runs.

If coverage fails, classify E3 as NDMI-coverage-inconclusive. Do not widen temporal or spatial rules.

## Primary diagnostic

Use the unchanged conditional concentration statistic and 1,000 simulations.

Report:
- same-sample M0 residual;
- M_NDMI residual;
- fraction residual removed;
- simulated residual 95% interval;
- plus-one upper-tail P.

Sufficiency requires the M_NDMI residual to no longer exceed its simulated upper 95% bound.

## Interpretation boundary

Support would implicate local vegetation/substrate moisture as a spatial filter on reproductive acoustic activity.

NDMI is not direct soil-moisture, water-depth, or water-temperature measurement.

Non-support closes the predeclared E1–E3 remote abiotic search.

## Stop rule

If E3 is unsupported or coverage-inconclusive after E1 and E2 have also failed, do not continue testing additional radii, moisture indices, land-cover variables, or rainfall windows on the same endpoint.

Priority then shifts to latent/biological mechanisms:
- local demographic availability;
- species × route-night reproductive readiness;
- social/chorus-state dependence.

## Anti-tuning

After focal NDMI values are read, do not change:
- NDMI as the index;
- surface-reflectance scaling;
- QA rule;
- 16-day lookback;
- common route acquisition date;
- 250-m radius;
- >=50% valid-pixel rule;
- double centering;
- species estimability;
- route folds;
- concentration endpoint;
- total-incidence conditioning.