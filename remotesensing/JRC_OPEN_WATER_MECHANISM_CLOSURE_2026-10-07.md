# JRC MonthlyHistory open-water mechanism closure — 2026-10-07

## Scope

This record closes the JRC GSW v1.0 MonthlyHistory **visible open-water** mechanism line after the response-blind tile-axis correction and the predeclared 100/250/500 m analyses.

It does not close all hydrology. Landsat DSWE partial-inundation work is a separately frozen next measurement under `revision/NAAMP_LANDSAT_DSWE_MECHANISM_CONTRACT_V0_1.md`.

## Primary 250 m result

Final rank-checked workflow: 37609691508.

Coverage:
- 1,881 pairs
- 366 routes
- 20 states
- M1 coverage gate passed.

Same-sample concentration:
- observed beta = 1.466552
- M0 predicted = 1.292062
- M0 residual = 0.174490; null 95% [-0.150908, 0.166734]; P = 0.01898
- M1 predicted = 1.284302
- M1 residual = 0.182250; null 95% [-0.161133, 0.147236]; P = 0.01399
- fraction residual removed by current monthly water = **-4.45%**.

Classification: **current_hydrology_not_supported_M3_inconclusive**.

Thus 250-m monthly visible surface-water extent does not explain the within-taxon concentration residual.

## 500 m named sensitivity

Coverage:
- 2,016 pairs
- 371 routes
- 20 states.

Same-sample residual:
- M0 = 0.245403
- M1 = 0.245572
- fraction removed = **-0.07%**
- both M0 and M1 remain outside their simulated upper 95% residual bounds (P ~= 0.001).

Classification: **not supported**.

## 100 m named sensitivity

Coverage:
- 1,640 pairs
- 349 routes
- 20 states.

Same-sample residual:
- M0 = 0.085022; null 95% [-0.171810, 0.171627]; P = 0.1828
- M1 = 0.082538; null 95% [-0.151168, 0.165910]; P = 0.1638
- fraction removed = +2.92%.

The 100-m subset is **mechanism-uninformative**, not evidence that 100-m hydrology is sufficient, because the same-sample M0 concentration residual is already inside its null interval before hydrology is added.

The primary 250-m result is not replaced by this subset.

## Strong-chorus biological bridge

Frozen secondary workflow: 37609815039.

Coverage:
- 1,000 informative pair x taxon clusters
- 252 routes
- 45 taxa.

Within pair x taxon, the mean current-water increase at wet-survey CI>=2 stops minus other stops was:
- observed = +0.000160
- permutation 95% [-0.000798, +0.000831]
- upper-tail P = 0.3596.

Classification: **strong_chorus_hydrology_alignment_not_supported**.

Thus visible monthly open-water change is not preferentially aligned with the established silence -> strong-chorus spatial transition.

## Hydroperiod variability

The predeclared 12-month JRC variability sequence is **coverage-inconclusive**:
- only 166 complete pairs
- 88 routes
- 14 states.

Do not relax the 9-of-12-month rule or the all-ten-stop pair requirement after seeing this missingness.

## Interpretation

Do not say hydrology is irrelevant.

The tested variable is 30-m Landsat-derived JRC monthly **visible surface-water extent** aggregated around the stop. It can miss or poorly represent:
- shallow water under emergent or dense vegetation;
- small ephemeral pools below pixel/support resolution;
- soil and substrate wetness;
- water depth;
- water temperature;
- within-month wet-dry transitions.

The negative JRC result therefore narrows the leading environmental explanation from generic local surface-water extent to finer or partially inundated wetland state.

## Next authorized measurement

Landsat Collection 2 Level-3 DSWE is frozen prospectively as the next test because it distinguishes moderate-confidence and potential-wetland/partial-inundation classes at acquisition scale.

No JRC radius, validity threshold, or temporal aggregation will be further searched for a favorable result.
