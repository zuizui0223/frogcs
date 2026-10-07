# NAAMP dynamic-hydrology mechanism contract v0.1 — 2026-10-07

## Scientific role

This is a mechanism study of the already-established within-taxon multi-site concentration, not a new search for a different spatial pattern.

Focal question:
Can dynamic local wetland hydrology explain the conditional concentration residual that remains after species rainfall response, strictly-prior species × SiteID propensity, dry-state persistence and total wet-state activation are represented?

Existing endpoint remains unchanged:
- observed within-taxon concentration beta = 1.6503
- principal-comparator prediction = 1.3535
- conditional residual = 0.2969

No new response endpoint is selected.

## Biological interpretation

CallingIndex is reproductive acoustic activity, not reproductive success.

The study may infer effects on:
- reproductive acoustic activation
- spatial expression of breeding activity
- chorus-state switching

It may not infer without additional data:
- spawning success
- egg or larval survival
- recruitment
- lifetime fitness

## Remote-sensing sources

Primary temporal water source:
JRC Global Surface Water Monthly History, Landsat-derived, 30 m, covering the full 2001–2015 NAAMP analysis period.

Static context:
U.S. National Wetlands Inventory wetland class/type where available.

Scene-level validation:
Landsat Dynamic Surface Water Extent (DSWE), used only where adequate scene coverage exists.

Sentinel-1 is reserved for a 2014–2015 high-resolution validation subset and cannot define the primary historical analysis.

## Coordinate authority

Only routes passing remotesensing/NAAMP_RS_COORDINATE_ELIGIBILITY_CONTRACT_V0_1.md may enter the remote-sensing mechanism analysis.

No coordinate is manually repaired after frog outcomes are inspected.

## Fixed spatial scale

Primary buffer: 250 m radius around each physical SiteID.

Named sensitivity: 500 m radius.

A 100-m buffer or single 30-m pixel is not authorized until independently validated coordinates are available.

## Hydrology variables

All variables are calculated before joining frog outcomes.

For each SiteID and survey month:

### H1. Current hydrological anomaly — primary mechanism variable

Let W_it be the fraction of valid JRC pixels classified as water in the 250-m buffer in the survey month.

Let C_im be the site's baseline mean water fraction for the same calendar month over 1984–2000.

Define:

current_anomaly = W_it - C_im

This isolates event-specific water-state deviation from persistent site quality already represented by prior species × SiteID propensity.

### H2. Recent hydrological persistence

recent_wetness_3m = mean of monthly water fraction for survey month and previous two months.

This asks whether breeding activity responds to sustained recent wetness rather than the survey month alone.

### H3. Environmental variability / hydroperiod volatility

Using the 12 months ending in the survey month:

hydro_sd_12m = SD of monthly water fraction

Named secondary descriptor:

wetdry_transition_12m = number of sign changes in monthly water anomaly across adjacent months.

The SD is the primary variability metric. Transition count is secondary.

This separates transiently variable/ephemeral wetland regimes from currently wet conditions.

## Mechanistic model sequence

The response endpoint and simulation machinery remain exactly the existing conditional within-taxon concentration test.

M0 — existing principal comparator
- cross-fitted species-specific rainfall response
- strictly-prior species × SiteID propensity
- dry-state persistence a = 0.75
- pair-level total wet-incidence matching

M1 — current local hydrology
M0 plus cross-fitted species-specific response to current_anomaly.

M2 — recent persistence
M1 plus cross-fitted species-specific response to recent_wetness_3m.

M3 — environmental variability
M2 plus cross-fitted species-specific response to hydro_sd_12m.

The route-fold scheme is inherited unchanged from the principal comparator.

Species-specific hydrology coefficients are learned only from the opposite deterministic route fold.

No taxon trait grouping is introduced.

## Pair-level application

For each focal wetter–drier pair and species × stop cell, calculate the cross-fitted hydrological logit shift:

delta_hydro = eta_hydro(wet run, stop) - eta_hydro(dry run, stop)

Add this stop-specific shift to the existing anchored prior logit before solving the same pair-level common shift that matches observed total wet incidence.

Thus hydrology is allowed to change where expected activation occurs while the observed amount of activation remains conditioned on.

## Primary mechanism diagnostic

For M0–M3 calculate the same observed conditional concentration residual.

Primary quantity:

fraction_residual_removed = (residual_M0 - residual_M3) / residual_M0

Predeclared interpretation:
- >= 0.75 removed and M3 residual inside its null 95% interval: dynamic local hydrology is sufficient to explain most of the concentration excess.
- 0.25–0.75 removed: dynamic hydrology is an important partial mechanism.
- < 0.25 removed and residual remains outside the null interval: dynamic hydrology is insufficient as the principal mechanism.

These are interpretation bins, not significance thresholds.

## Environmental-variability question

To isolate the effect of environmental variability on reproductive acoustic activity, compare M2 vs M3.

Primary variability quantity:

incremental_variability_fraction = (residual_M2 - residual_M3) / residual_M0

A positive reduction indicates that recent hydroperiod volatility contains spatial information about chorus placement beyond current and sustained wetness.

This does not imply that variability is beneficial or harmful to reproductive success.

## Coverage gates

Before frog outcome readback, require:
- >= 70% of the existing 2,916 principal pairs retain all required 250-m hydrology values at >=8 of 10 physical sites in both runs
- >= 300 routes
- >= 15 states
- full 2001–2015 period represented in the retained run universe
- >= 80% valid JRC pixel fraction within each retained buffer-month

If the gate fails, classify the primary mechanism test as remote-sensing-inconclusive rather than changing buffer size, baseline period or missing-data rules.

## Missingness

JRC no-data classifications are not water and are not silently coded as dry.

Monthly water fraction is computed only from valid water/non-water pixels.

A buffer-month fails if <80% of nominal pixels have valid classification.

No temporal interpolation is used in the primary analysis.

## Static wetland context

NWI wetland class is used only as descriptive context and a sensitivity allowing broad wetland class to modify hydrology response.

It cannot replace current anomaly as the primary mechanism because static habitat is already partly absorbed by prior SiteID history.

## No-retuning rule

After hydrology variables are joined to frog outcomes, do not change:
- 250-m primary buffer
- 1984–2000 climatology
- 3-month persistence window
- 12-month variability window
- hydro_sd_12m definition
- route folds
- species-specific coefficient family
- a = 0.75 anchor
- total-incidence conditioning
- residual-removal interpretation bins

## Scientific decision

Possible conclusions are:

1. hydrology sufficient — broad rain response is spatially filtered by event-specific local water state
2. hydrology partial — local water state contributes, but additional taxon-night, social or demographic processes remain
3. hydrology insufficient — the leading unmeasured environmental explanation is directly weakened, raising priority of social state, demographic availability or unmeasured fine-scale habitat conditions
