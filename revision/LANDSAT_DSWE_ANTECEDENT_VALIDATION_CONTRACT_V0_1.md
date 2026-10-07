# Landsat DSWE antecedent validation contract v0.1 — 2026-10-07

**Frozen before the JRC M0–M3 mechanism result is read.**

## Role

This is a temporal-direction validation of the dynamic-hydrology mechanism, not a replacement primary analysis.

JRC MonthlyHistory can summarize the survey calendar month but does not guarantee that classified water observations occurred before the exact NAAMP survey date.

DSWE therefore tests the same biological idea using only Landsat surface-water observations on or before the survey date.

## Product

Use USGS Landsat Collection 2 Dynamic Surface Water Extent (DSWE) Science Product where available for Landsat 5, 7 and 8.

Use only observations whose acquisition date is <= the NAAMP survey date.

## Spatial support

Primary radius: 250 m around the same strict-coordinate physical SiteID.

No single-pixel analysis.

## Temporal matching

Primary antecedent scene:
- nearest valid DSWE acquisition on or before the survey date;
- maximum lag 16 days.

Named sensitivity:
- maximum lag 32 days.

No post-survey acquisition may be used in the primary antecedent test.

## Water metric

For the selected scene, compute fraction of valid 250-m buffer pixels classified as open water / water by the DSWE product.

Require >=50% valid classified pixels in the buffer.

For each matched focal pair at the same SiteID:

delta_DSWE = antecedent water fraction for the wetter survey - antecedent water fraction for the drier survey.

## Mechanism test

Use the same concentration endpoint and principal comparator.

Add cross-fitted, within-SiteID and within-route-run residualized species response to DSWE water state using the same coefficient estimability rules as the JRC M1 model.

Retain pair-level total-incidence matching.

## Coverage gate

Interpret only if the primary 16-day matching yields:
- >= 1,000 complete focal pairs
- >= 250 routes
- >= 12 states
- all ten focal SiteIDs valid in both focal runs

If this gate fails, classify the DSWE temporal validation as inconclusive.

The 32-day sensitivity cannot replace a failed 16-day primary gate.

## Interpretation

If JRC M1/M2/M3 and antecedent DSWE agree:
> local surface-water dynamics have temporally ordered support as a generator of the chorus configuration.

If JRC supports but DSWE does not:
> monthly water state is associated with the configuration, but an antecedent short-window hydrological mechanism is not independently supported.

If DSWE supports while JRC does not:
> sub-monthly event timing may matter more than monthly water state.

## Boundaries

DSWE remains observational and does not prove causal mediation.

Calling activity is a reproductive acoustic state, not reproductive success.
