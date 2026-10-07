# NAAMP dynamic-hydrology mechanism extension v0.4 — 2026-10-07

**Status:** supersedes v0.3 for the primary hydrology exposure before any hydrology-augmented frog concentration result was calculated.

## Why v0.4 is necessary

A response-blind product-behaviour audit found that JRC MonthlyHistory and MonthlyRecurrence have different useful supports for this question.

After correcting the JRC tile filename row/column order:
- MonthlyHistory returned class 1 (observed non-water) at inland U.S. test points and class 2 at a Lake Michigan point.
- MonthlyRecurrence returned 0 with has_observations=0 at inland dry-land test points, but recurrence=100 with has_observations=1 at the Lake Michigan point.

Thus MonthlyRecurrence is not suitable as the denominator-valid seasonal baseline for an entire 250-m wetland buffer containing terrestrial/non-water pixels.

This decision uses only arbitrary non-NAAMP test coordinates and product metadata. No frog endpoint and no focal NAAMP hydrology effect was read.

## Primary dynamic-hydrology exposure

Use JRC GSW v1.0 MonthlyHistory only.

For each focal physical SiteID and each focal survey month:

W = number of class-2 water pixels / number of valid class-1-or-class-2 pixels

within the fixed 250-m buffer.

A site-month is valid only if >=50% of candidate buffer pixels are class 1 or 2.

For each matched wetter-drier focal pair at the same physical SiteID:

delta_W = W_wetter-survey-month - W_drier-survey-month

This is the primary M1 dynamic-hydrology exposure.

Because the comparison is within the same physical SiteID and the existing comparator already contains strictly-prior species × SiteID propensity, persistent static site quality is not the target of delta_W.

## MonthlyRecurrence role

MonthlyRecurrence is demoted from the primary mechanism.

It may be used only as descriptive/static hydroperiod context for pixels where recurrence is defined. It cannot determine focal-pair eligibility and cannot replace delta_W.

## Environmental-variability sequence retained

M0: existing principal comparator.

M1: M0 + cross-fitted species-specific response to current monthly water fraction W, applied as the focal stop difference delta_W.

M2: M1 + recent_wetness_3m difference.

M3: M2 + hydro_sd_12m difference.

Definitions from v0.3 remain:
- recent_wetness_3m = mean W for survey month and previous two months, all three valid;
- hydro_sd_12m = sample SD of W over the 12 months ending in survey month, requiring >=9 valid months;
- hydro_range_12m remains secondary only.

## Primary biological decomposition

M0 -> M1 asks:
Does event-specific change in local surface water explain where reproductive acoustic activity is allocated?

M1 -> M2 asks:
Does sustained wetness add information beyond focal-month water state?

M2 -> M3 asks:
Does hydroperiod variability add information beyond current and sustained wetness?

The concentration endpoint, route folds, a=0.75 anchor, total-incidence conditioning and simulation framework remain unchanged.

## Coverage gates

Primary M1:
- >=1,500 pairs
- >=300 routes
- >=15 states
- all ten focal SiteIDs valid in both focal survey months

M3:
- same thresholds
- all ten focal SiteIDs have current W, recent_wetness_3m and hydro_sd_12m in both focal runs

No missing hydrology value is imputed.

## Spatial support

Primary: 250 m.

100 m and 500 m remain named sensitivities only and cannot replace 250 m based on results.

## Tile-axis correction

All JRC GeoTIFF access must use the verified filename convention:

<ROW_OFFSET>-<COLUMN_OFFSET>

where:
- row offset is derived from global raster row measured southward from 80 N;
- column offset is derived from global raster column measured eastward from 180 W.

The earlier column-row implementation and its coverage receipts are invalidated for scientific use.

## Interpretation boundary

Support concerns reproductive acoustic activity and spatial expression of breeding activity, not reproductive success, recruitment or fitness.
