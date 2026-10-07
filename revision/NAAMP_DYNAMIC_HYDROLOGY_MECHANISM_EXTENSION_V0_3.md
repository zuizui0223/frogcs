# NAAMP dynamic-hydrology mechanism extension v0.3 — 2026-10-07

**Status:** supersedes v0.2 only by adding a response-blind environmental-variability component and a stricter geometry-only final-analysis gate. The v0.2 current-water extraction definitions remain unchanged.

No frog concentration endpoint has been calculated with remote-sensing values when this extension is frozen.

## Scientific target

The endpoint remains the existing within-taxon multi-site concentration:
- observed beta 1.6503
- principal prediction 1.3535
- residual 0.2969

The study asks whether dynamic local hydrology explains that residual.

A second, nested question asks whether hydrological variability itself contributes after current wetland state is represented.

## Existing v0.2 hydrology definitions retained

Primary radius: 250 m.

Current water state:
- JRC GSW v1.0 MonthlyHistory
- class 1 = non-water
- class 2 = water
- current water fraction calculated among valid class 1/2 pixels

Seasonal expectation:
- JRC GSW v1.0 MonthlyRecurrence for the same calendar month

Current anomaly:
H_current = current monthly water fraction - expected monthly recurrence fraction

The v0.2 >=50% valid-buffer rule is retained and is not changed after extraction began.

## Final coordinate-analysis gate

Remote-sensing extraction may be performed for the broader v0.2 coordinate-safe set, but the final mechanism analysis uses only routes passing the stricter, outcome-blind geometry gate:

remotesensing/NAAMP_RS_COORDINATE_ELIGIBILITY_CONTRACT_V0_1.md

That audit retained 1,106 / 1,183 routes and excluded all five previously known gross-error routes.

This stricter gate was defined and evaluated using coordinates only, without frog outcomes or remote-sensing water values.

## Environmental variability variables — frozen before extraction

For each physical SiteID and survey month, obtain monthly water fraction W for the survey month and preceding 11 calendar months, using the same 250-m circular support and v0.2 valid-pixel rule.

### V1. Recent wetness persistence

recent_wetness_3m = mean of W over survey month and previous two months.

Require all three monthly W values to be valid.

### V2. Hydroperiod variability — primary variability metric

hydro_sd_12m = sample standard deviation of monthly W over the 12 months ending in the survey month.

Require at least 9 of 12 monthly W values to be valid.

No temporal interpolation is used.

### V3. Hydrological range — secondary descriptor

hydro_range_12m = max(W) - min(W) over valid months in the same 12-month window.

Require the same >=9 valid months.

V3 is descriptive/secondary and cannot replace V2.

## Why these variables are distinct

H_current measures whether the site is wetter or drier than its usual seasonal state at the focal survey.

recent_wetness_3m measures persistence of recent wet conditions.

hydro_sd_12m measures environmental variability in the breeding habitat itself.

Thus a site can be:
- currently wet but historically stable
- currently wet after a highly variable year
- currently dry despite normally persistent water
- transiently flooded relative to its usual seasonal state

These represent different ecological mechanisms.

## Nested mechanism models

All models retain:
- existing concentration endpoint
- strictly-prior species x SiteID propensity
- a = 0.75 dry-state persistence
- opposite-route-fold training
- pair-level total wet-incidence matching

M0: existing principal comparator.

M1: M0 + stop-specific cross-fitted response to H_current.

M2: M1 + stop-specific cross-fitted response to recent_wetness_3m.

M3: M2 + stop-specific cross-fitted response to hydro_sd_12m.

Species-specific coefficients may be used only under a pre-frozen estimability/shrinkage rule shared across M1-M3. If a species is non-estimable, its hydrology coefficient is zero rather than being tuned from the focal pair.

## Primary mechanism quantities

For each M0-M3 calculate the same conditional concentration residual on the identical complete-case sample.

Hydrology contribution:
fraction_removed_total = (residual_M0 - residual_M3) / residual_M0

Current-state contribution:
fraction_removed_current = (residual_M0 - residual_M1) / residual_M0

Recent-persistence increment:
increment_recent = (residual_M1 - residual_M2) / residual_M0

Environmental-variability increment:
increment_variability = (residual_M2 - residual_M3) / residual_M0

## Mechanism interpretation

Dynamic hydrology is sufficient only if M3 residual is inside its simulated 95% null interval.

If M3 reduces but does not eliminate the residual, hydrology is a partial generator.

If M3 changes the residual little, JRC-scale hydrology is insufficient.

For environmental variability specifically:

- increment_variability > 0 means recent hydroperiod variability contains spatial information about reproductive acoustic activity beyond current and sustained wetness.
- increment_variability near 0 means variability adds little beyond water state.
- increment_variability < 0 is retained as non-support; no alternate variability metric is promoted.

No post-readback threshold defines a biologically important effect.

## Reproductive interpretation boundary

Calling and chorus state are reproductive acoustic behaviour.

Support may be described as an effect of environmental state/variability on the spatial expression of reproductive activity.

Do not call it an effect on:
- reproductive success
- egg production
- larval survival
- recruitment
- fitness

without independent demographic data.

## Variability coverage gate

Before joining variability metrics to frog outcomes, require:
- >= 1,500 principal-pair equivalents with complete M3 hydrology at >=8 of 10 stops in both focal runs
- >= 300 routes
- >= 15 states

If this gate fails, V2/M3 is classified as variability-inconclusive. M1 may still proceed under its separately frozen v0.2 coverage rule.

## Anti-tuning

After variability values are extracted, do not change:
- 250-m primary radius
- 3-month persistence window
- 12-month variability window
- >=9/12 valid-month requirement
- hydro_sd_12m definition
- route geometry gate
- model order M0-M3
- residual-removal estimands

The existing 100-m and 500-m radii remain named spatial sensitivities only.
