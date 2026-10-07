# DSWEmod classes 1–3 mechanism closure — 2026-10-07

## Scope

This closes the predeclared primary MODIS DSWEmod classes {1,2,3} mechanism line after the source-availability repair that excluded broken public year 2004 before frog readback.

Primary support: 500 m around physical SiteID.

## Coverage

Source-available years: 2003 and 2005–2015.

M1 current-state sample:
- 2,249 pairs
- 372 routes
- 19 states
- gate passed.

M3 common sample:
- 1,649 pairs
- 324 routes
- 19 states
- gate passed.

Thus persistence/variability inference is not coverage-inconclusive.

## M0–M3 result on the 1,649-pair common sample

Observed concentration beta = 2.558784.

M0 principal comparator:
- predicted = 2.056628
- residual = 0.502156
- null 95% [-0.197230, 0.224164]
- upper-tail P = 0.000999.

M1 + current DSWEmod_123:
- predicted = 2.041947
- residual = 0.516837
- fraction removed relative to M0 = -2.92%
- P = 0.000999.

M2 + 3-month persistence:
- predicted = 2.052223
- residual = 0.506561
- increment relative to M1 = +2.05% of M0 residual
- but M2 remains worse than M0 overall
- P = 0.000999.

M3 + 12-month hydroperiod variability:
- predicted = 2.028566
- residual = 0.530218
- variability increment = -4.71% of M0 residual
- total fraction removed M0 -> M3 = -5.59%
- P = 0.000999.

Classification: **dswemod_dynamic_hydrology_not_supported**.

## 250-m named sensitivity

Current DSWEmod_123 reduced the residual by only +2.25%. M1 was not sufficient. This sensitivity cannot replace the negative 500-m primary.

## Scientific conclusion

Neither monthly visible open water (JRC) nor monthly MODIS DSWEmod partial/potential wetland state (classes 1–3), recent persistence, or 12-month hydroperiod variability explains the within-taxon concentration excess.

This directly weakens the leading remotely sensed surface-inundation explanation at the tested 30-m and 250-m products/scales.

It does not test water depth, water temperature, soil/substrate moisture, dense-canopy hydrology, very small pools below remote-sensing support, demographic readiness, or social facilitation.

## Authorized remaining secondaries

Only the already predeclared DSWEmod class sensitivity {1,2,3,4} and the DSWEmod strong-chorus biological bridge may still be evaluated. Neither may replace or redefine the negative classes 1–3 primary mechanism result.
