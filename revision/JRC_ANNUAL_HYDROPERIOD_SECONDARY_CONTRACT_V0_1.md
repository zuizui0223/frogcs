# JRC annual hydroperiod secondary contract v0.1 — 2026-10-07

**Frozen before the monthly JRC M0–M3 frog mechanism result is read.**

## Role

This is a separate secondary test of interannual hydrological regime, motivated by response-blind missingness in MonthlyHistory.

It does not replace the fixed monthly M1–M3 analysis and cannot rescue a failed monthly mechanism result.

## Product

Use JRC Global Surface Water YearlyClassification / YearlyHistory for the NAAMP survey years 2001–2015.

At 30-m resolution, waterClass is:
- 0 = no data
- 1 = not water
- 2 = seasonal water
- 3 = permanent water

## Spatial support

Primary radius: 250 m around strict-coordinate physical SiteIDs.

Use only valid classes 1–3 in the denominator.

Require >=50% valid pixels in a site-year buffer.

## Annual hydrology metrics

For each SiteID × survey year calculate:

annual_water_fraction = fraction of valid pixels with class 2 or 3

seasonal_water_fraction = fraction of valid pixels with class 2

permanent_water_fraction = fraction of valid pixels with class 3

seasonal_share_of_water = seasonal / (seasonal + permanent), defined only when annual water fraction > 0.

## Primary annual dynamic exposure

For each wetter–drier matched pair at the same SiteID:

delta_annual_water = annual_water_fraction_wet-year - annual_water_fraction_dry-year

This tests whether the focal survey closer to rain occurred in a year when the same wetland had a broader annual water footprint.

## Environmental-variability exposure

Primary variability descriptor:

delta_seasonal_fraction = seasonal_water_fraction_wet-year - seasonal_water_fraction_dry-year

This tests whether interannual shifts toward seasonal/ephemeral surface water are associated with the spatial allocation of reproductive acoustic activity.

## Mechanism test

Use the same concentration endpoint, strict geometry gate, route folds, a=0.75 anchor and pair-level total-incidence matching.

Fit species-specific annual hydrology coefficients out of route fold with the same estimability and regularization rules as monthly hydrology.

Hydrology covariates are double-centered by SiteID and route-run before coefficient fitting.

## Coverage gate

Require:
- >=1,500 complete focal pairs
- >=300 routes
- >=15 states
- all ten SiteIDs valid in both focal years

## Interpretation

If annual water extent explains residual concentration:
> year-to-year hydroperiod state contributes to where breeding activity is expressed.

If seasonal-water change adds information:
> interannual shifts in temporary/seasonal wetland availability contribute to the spatial organization of reproductive acoustic activity.

This is an effect on acoustic breeding activity, not demonstrated reproductive success.

## Anti-tuning

Do not change class definitions, 250-m radius, coverage gate or annual metrics after frog outcome readback.

The annual analysis remains secondary regardless of whether it is stronger than the monthly result.
