# E3 final remote-abiotic test: Landsat vegetation moisture — v0.1

**Frozen 2026-10-08 before any E3 focal Landsat moisture values are read or combined with frog outcomes.**

## Why this test is authorized and why it is last

The archived environmental-priority ledger:
`revision/ENVIRONMENTAL_MECHANISM_PRIORITY_AFTER_HYDROLOGY_2026-10-07.md`
authorized E3 if the official NWI rainfall-by-water-regime mechanism (E1) was unsupported and local nighttime thermal filtering (E2) was unsupported or coverage-inconclusive.

Actual E1: on 2,028 pairs / 300 routes / 20 states, the NWI regime interaction did not reduce the conditional concentration residual.

Actual E2: MOD11A1 nighttime LST failed its response-blind coverage gate (rule A 83 pairs / 62 routes; rule B 427 pairs / 184 routes; required >=1,500 / >=300). This is **inconclusive**, not evidence of no thermal effects.

E3 is the FINAL public remote-abiotic test. No alternative index, radius, sensor, temporal window, or taxon subset may replace its result.

## Biological question

> Can transient local vegetation-moisture differences among sites explain the higher-order taxon-by-place concentration left after rainfall response, strictly-prior species x SiteID propensity, dry-state persistence, and total activation magnitude are represented?

This is a configuration-mechanism question, not a new search for calling-intensity correlations.

## Remote-sensing product and band definition

Source: USGS **Landsat Collection 2 Level-2 Surface Reflectance**:
- Landsat 5 TM and Landsat 7 ETM+ for early years;
- Landsat 8 OLI for 2013–2015;
- 30-m scene data.

Single primary indicator: **NDMI = (NIR - SWIR1) / (NIR + SWIR1)**.

Bands:
- TM/ETM+: NIR SR_B4, SWIR1 SR_B5;
- OLI: NIR SR_B5, SWIR1 SR_B6.

Convert Collection 2 Level-2 SR digital values with:
`reflectance = DN * 0.0000275 - 0.2`.

Retain only physically valid scaled reflectance (0 < NIR <= 1; 0 < SWIR1 <= 1; finite denominator). Use QA_PIXEL to exclude fill, dilated cloud, cloud, cloud shadow, snow, and QA-flagged water pixels, and QA_RADSAT to exclude saturated pixels. The cirrus flag is additionally masked where meaningful for the sensor.

**NDMI measures vegetation water content / spectral wetness, not directly water depth, soil moisture, or pond temperature.** A null result therefore cannot exclude those local states.

## Spatial support

- Strict response-blind NAAMP coordinate route gate already frozen (1,106 / 1,183 coordinate-table routes eligible).
- Main circle: 500 m radius around each physical SiteID.
- Summarize the **median valid-pixel NDMI** within the circle.
- Require >=70% of nominal 30-m pixel centers in the circle to pass sensor QA and validity.
- No manual coordinate repair, pixel value interpolation, or change of radius.
- No sensitivity search after readback.

## Temporal correspondence

For every survey RunID, choose the most recent eligible acquisition on or before its survey date, within **32 calendar days**.

**All ten stops of a RunID must use one same acquisition date and product**, chosen on the basis of QA/coverage only. If multiple products have the same eligible date, select the lexicographically smallest product ID among those satisfying the entire route.

Do not use scenes acquired after a survey.

If a chosen scene spans the 10-stop route but fails the 70% QA threshold at even one stop, test the next most recent eligible pre-survey acquisition, still within the 32-day window. If none covers all ten sites, that RunID is missing.

This selection must happen without reading frog calling outcomes or concentration residuals.

## Availability and access gate

Phase A is a **response-blind source-access test** using only arbitrary non-NAAMP points and three historical periods (2002, 2008, 2014):
- confirm STAC collections and scene metadata are reachable;
- identify NIR, SWIR1 and QA_PIXEL URLs without constructing or guessing asset URLs;
- confirm both spectral assets and QA are actually accessible without private authentication;
- verify CRS / raster transform and QA bit behavior on a small test window.

If Phase A cannot retrieve these products from authorized public sources, stop as `E3_public_asset_access_inconclusive`. Do not substitute a different sensor or index.

Phase B is response-blind coverage estimation on the NAAMP focal 2,916 strictly-prior-history pairs using survey dates and physical SiteIDs only. Gate:
- >=1,500 pairs with all ten stops valid in both surveys;
- >=300 routes;
- >=15 states.

If the gate fails: `E3_remote_moisture_coverage_inconclusive`. Do not change temporal window, valid-pixel threshold, or source.

## Frozen biological model — only if gate passes

M0 = existing principal configuration generator:
- opposite-route-fold species rainfall response;
- strictly-prior species x SiteID propensity;
- dry-state anchor a = 0.75;
- pair-level conditioning on observed total wet-state incidence.

M_E3 adds a cross-fitted species-specific NDMI response using only opposite-route-fold training cells. Before fitting, NDMI is centered first by physical SiteID over training observations and then by RunID, targeting local temporal moisture deviations rather than static site/route traits.

Training response: binary calling CI>=1 per species x RunID x SiteID.
Controls: log1p(DaysSinceRain), route mean air temperature, sin/cos DOY, State, RunNumber.
Estimability: >=20 positive training cells and >=5 positive training routes.
Binomial GLM; fixed ridge fallback alpha=0.01; unstable/nonestimable beta forced to zero.

For each focal physical SiteID, apply the species coefficient to NDMI(wetter survey) - NDMI(drier survey), then use the unchanged pair-level common shift to match total activation.

Use 1,000 simulations. Report on the **identical E3-complete sample**:
- observed concentration;
- M0 and M_E3 predicted concentration;
- both conditional residuals;
- null 95% residual intervals and upper-tail P values;
- residual fraction removed.

Sufficiency requires the observed M_E3 residual to lie inside its predeclared null 95% interval, not merely be a smaller number.

## Interpretation

Support implicates local vegetation/spectral moisture as a candidate environmental filter but does not establish causal mediation or breeding success.

Non-support weakens this last measurable public remote-abiotic route, while leaving true fine-scale water depth, temperature, substrate moisture, demographic availability, and social/chorus state unresolved.

No result authorizes a new ad hoc remote-sensing candidate.

**RC6/JAE remains unchanged during this E3 work.**
