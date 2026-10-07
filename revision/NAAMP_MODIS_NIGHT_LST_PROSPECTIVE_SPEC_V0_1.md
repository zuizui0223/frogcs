# MODIS nighttime LST feasibility and prospective mechanism boundary — 2026-10-07

## Status

Response-blind preparation only.

Do not calculate a frog concentration endpoint with MODIS LST unless the preceding NWI water-regime mechanism is unsupported or coverage-inconclusive, as specified in:
`revision/ENVIRONMENTAL_MECHANISM_PRIORITY_AFTER_HYDROLOGY_2026-10-07.md`.

## Scientific role

The existing analyses already represent route-level air temperature and rainfall.

This candidate asks a distinct question:

> Does local nocturnal surface thermal state among stops within the same route event help determine where a species expresses reproductive acoustic activity?

The target is local thermal heterogeneity, not regional weather magnitude.

## Source

Primary product:
NASA MODIS/Terra MOD11A1 Collection 6.1 daily Land Surface Temperature / Emissivity, 1-km sinusoidal grid.

Required layers:
- LST_Night_1km;
- QC_Night;
- Night_view_time.

The product spans the full 2001–2015 focal NAAMP period.

Temperature scaling:
`LST_K = DN * 0.02`.

## Why nighttime MODIS is preferred to Landsat ST for the primary thermal test

Landsat Collection 2 surface temperature has finer spatial resolution but is a daytime scene product.

The NAAMP response is nocturnal calling.

MOD11A1 directly provides nighttime LST and observation time, so temporal correspondence with the behavioral endpoint is better even though spatial resolution is coarser.

Landsat ST may remain a later spatial-resolution sensitivity only if the primary MODIS thermal line is informative.

## Response-blind temporal coverage preflight

MOD11A1 file/item dates are **UTC data days**, while `Night_view_time` is local solar time. The MOD11 C6.1 user guide explicitly notes that the UTC data day and a grid cell's local-solar data day can differ by one calendar day.

Therefore temporal matching is defined on the reconstructed **local-solar observation date**, not directly on the STAC item/file date.

For a pixel with longitude `lon` (degrees east, negative in the conterminous U.S.) and scaled local solar observation hour `h_local`:

`h_utc_unwrapped = h_local - lon / 15`

`day_shift = floor(h_utc_unwrapped / 24)`

`local_solar_date = UTC_data_date - day_shift days`.

Require `Night_view_time` to be within its documented non-fill range 0–24.0 h before using it for date reconstruction.

Before any frog endpoint is calculated, report coverage under both:

A. a valid Terra nighttime observation whose reconstructed `local_solar_date` equals the nominal NAAMP survey date at all ten focal SiteIDs;

B. the nearest **common local-solar route date** on or before the survey date within 2 calendar days for which all ten focal SiteIDs have valid Terra nighttime LST under the frozen QC rule. The same target local-solar date is used for all ten stops of that RunID.

For each target local-solar date, search the adjacent UTC data days needed to recover it (target date −1, target date, target date +1) and retain only pixel observations whose reconstructed local-solar date equals the target.

The decision rule is fixed:
- use A if it passes the primary coverage gate;
- otherwise use B if B passes;
- otherwise classify local-nighttime-LST coverage-inconclusive.

No local-solar observation after the survey date is used.

This selection is based only on data availability/QC, not frog outcomes.

Do not choose a different local-solar date for different stops within the same RunID; route-relative thermal contrasts must come from one common satellite night.

## QC rule

A pixel is valid when:
- LST_Night_1km is non-fill;
- QC_Night mandatory QA bits 0–1 = 0 (LST produced, good quality);
- QC_Night LST-error bits 6–7 = 0 (estimated average LST error <=1 K).

Do not relax QC after outcome readback.

Night_view_time is retained and reported for audit.

## Spatial rule

For each strict-coordinate-gate physical SiteID:
- sample the MOD11A1 native 1-km pixel containing the SiteID;
- no buffer-radius search;
- no spatial interpolation in the primary analysis.

If two focal stops map to the same MODIS pixel, keep the identical value for both rather than perturbing coordinates.

If a SiteID lies on a MODIS tile boundary and more than one same-date Terra item contains the point, choose the lexicographically smallest item ID after verifying the point is within the raster bounds. Do not choose by LST or QC value.

Report the number of unique MODIS pixels represented among the ten focal stops for each RunID as a resolution diagnostic; do not use that diagnostic to select a subset after outcome readback.

## Dynamic local thermal variable

For each valid RunID × SiteID observation:

1. obtain nighttime LST;
2. center within physical SiteID across the training-fold observations to remove persistent site thermal identity;
3. center again within RunID across the focal route stops to remove route-wide nighttime thermal state.

The fitted coefficient therefore targets local temporal thermal deviation that is spatially non-uniform within the route-night.

At focal-pair prediction, apply the cross-fitted species coefficient to the corresponding wet-minus-dry local thermal difference; the pair-level common incidence-matching shift remains unchanged.

## Model

M0:
existing principal comparator.

M_LST:
M0 + cross-fitted species-specific local nighttime LST response.

Training:
- opposite deterministic route fold only;
- binary species calling by RunID × SiteID;
- controls for log(1+DaysSinceRain), route mean air temperature, annual sine/cosine, State and RunNumber;
- minimum >=20 positive cells and >=5 positive routes;
- binomial GLM;
- existing ridge fallback alpha=0.01;
- zero coefficient when non-estimable/unstable.

## Coverage gate

Before frog endpoint readback require:
- >=1,500 complete focal pairs;
- >=300 routes;
- >=15 states;
- all ten focal SiteIDs have valid nighttime LST in both focal runs.

If neither temporal rule A nor B reaches the gate, stop as coverage-inconclusive.

## Primary diagnostic

Use the unchanged conditional concentration statistic and 1,000 simulations.

Report:
- same-sample M0 residual;
- M_LST residual;
- residual fraction removed;
- simulated residual 95% interval;
- plus-one upper-tail P.

Sufficiency requires the M_LST residual to no longer exceed its own simulated upper 95% bound.

## Biological secondary

Only after the concentration result is frozen, local nighttime LST may be tested against the existing route-new CI>=2 strong-chorus placement endpoint using a separately frozen permutation specification.

## Interpretation boundary

Support would implicate local nocturnal thermal heterogeneity as a spatial filter on reproductive acoustic activity.

It would not measure water temperature directly and would not establish reproductive success, abundance or fitness.

A negative result would not exclude sub-kilometre water-temperature microclimates that a 1-km land-surface product cannot resolve.

## Anti-tuning

After focal LST values are joined to frog outcomes, do not change:
- Terra MOD11A1 as primary product;
- nighttime rather than daytime LST;
- QC rule;
- A/B temporal decision rule;
- native-pixel extraction;
- route/site centering;
- coverage gate;
- route folds;
- concentration endpoint;
- pair-level total-incidence conditioning.
