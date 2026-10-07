# NAAMP MODIS DSWEmod mechanism extension v0.2 — 2026-10-07

**Status:** supersedes v0.1 by adding a nested hydroperiod-persistence/variability sequence before any focal DSWEmod value has been read. The initial 13-year extraction workflow was still queued when this extension was frozen.

## Scientific target unchanged

The response remains the existing within-taxon concentration endpoint.

DSWEmod is tested because JRC monthly visible-open-water change failed to explain the residual, while DSWEmod includes moderate-confidence and potential-wetland classes derived from daily MODIS imagery.

## Product and primary spatial/class definitions unchanged

- USGS DSWEmod monthly MODIS product, 2003–2015.
- Native resolution 250 m.
- Primary radius 500 m.
- Named radius sensitivity 250 m.
- Primary positive classes {1,2,3}.
- Valid denominator classes {0,1,2,3,4}.
- Class 9 and nodata are invalid.
- >=50% valid candidate pixels required.

## Temporal hydrology variables

For each SiteID and calendar month define:

D_t = DSWEmod_123 fraction in the primary 500-m buffer.

### D1. Current partial-inundation state

current_D = D_t.

Focal pair exposure: delta_current_D = D_wetterSurveyMonth - D_drierSurveyMonth at the same SiteID.

### D2. Recent persistence

recent_D_3m = mean(D_t, D_t-1, D_t-2).

All three months must be valid.

### D3. Hydroperiod variability

DSWE_sd_12m = sample SD of monthly D over the 12 months ending in the survey month.

Require >=9 valid months out of 12. No temporal interpolation.

Named descriptive secondary: DSWE_range_12m = max(D)-min(D) over the same valid months.

## Nested mechanism sequence

M0 = existing principal comparator.

M1 = M0 + species-specific current_D effect.

M2 = M1 + species-specific recent_D_3m effect.

M3 = M2 + species-specific DSWE_sd_12m effect.

All hydrology coefficients use the same predeclared structure:
- opposite deterministic route-fold training;
- binary species calling at RunID × SiteID cells;
- controls for log(1+DaysSinceRain), run mean air temperature, annual sine/cosine, State and RunNumber;
- >=20 positive cells and >=5 positive routes to estimate;
- binomial GLM with ridge fallback alpha=0.01;
- zero hydrology coefficient if non-estimable or unstable;
- each hydrology covariate centered by SiteID and then by RunID before coefficient fitting.

At focal prediction, apply the raw same-SiteID wet-minus-dry covariate differences and retain the unchanged pair-level total-incidence matching.

## Coverage gates

M1 current-state gate:
- >=1,500 pairs
- >=300 routes
- >=15 states
- all ten focal SiteIDs valid in both focal survey months.

M3 variability gate:
- same thresholds;
- all ten focal SiteIDs have current_D, recent_D_3m and DSWE_sd_12m in both focal runs.

If M3 gate fails but M1 passes, evaluate M0 vs M1 and classify variability as coverage-inconclusive.

## Mechanism decomposition

On an M3-complete common sample report:

- fraction_removed_current = (residual_M0 - residual_M1) / residual_M0
- increment_recent = (residual_M1 - residual_M2) / residual_M0
- increment_variability = (residual_M2 - residual_M3) / residual_M0
- fraction_removed_total = (residual_M0 - residual_M3) / residual_M0

Report negative increments unchanged.

Each model is sufficient only if its residual no longer exceeds its own simulated upper 95% residual bound.

## 250-m radius sensitivity

The 250-m radius evaluates M0 vs current-state M1 only.

It cannot replace the 500-m primary or promote an M2/M3 result not supported at the primary 500-m radius.

## Strong-chorus secondary

After the concentration result is frozen, the primary 500-m current_D exposure may be tested against the existing silence-to-CI>=2 spatial transition.

## Interpretation boundary

M3 support would show that hydroperiod variability contains information about the spatial expression of reproductive acoustic activity beyond current and sustained partial-wetland state.

It would not show an effect on reproductive success, larval survival, recruitment or fitness.
