# G9 fixed diagnostic: does generating four signs identify demographic benefit?

**Date: 2026-11-07 JST.** Post-G8, outcome-conditional diagnostic on *existing* G8 output. Designed after observing the aggregate G8 results, therefore **post hoc, not externally preregistered and not an independent model experiment**. The joint contingency outcomes below were not read before this diagnostic definition.

## Population, definitions and estimands

Exact controlling input: audited `research/results/g8_27rate_paired_20261107/audited/g8_all_source_rate_context_paired.csv.gz` from the completed G8 27-rate original-source analysis, GitHub Actions run #42320535778. Keep all 256 original food-web backgrounds × 27 rate cells × 3 original developmental contexts = **20,736 matched source-rate-context records**, including all successes, failures, zeros and negative responses. No biological reruns, parameter selection, subgroup-based exclusions, posterior weights or invented field data.

For each matched source (s), rate (r), context (c):
- (A_{11}=1) if both vegetation functions ON generate all four model-native signs; (A_{00}=1) with both OFF.
- (C=A_{11}-A_{00}\in\{-1,0,+1\}): *newly generated*, unchanged, or lost four-sign compatibility when toggling both functions.
- (\Delta_F=\overline{\log F}_{11}-\overline{\log F}_{00}\): effect on the modelled aquatic frog cohort; (B=1[\Delta_F>0]\). Exact zero is reported separately. Neither (C) nor (B) is an observed pond outcome.
- (C_{viable}\) is the already-frozen `viable_compatibility` difference using the synthetic 5% floor; treat separately.

**Primary diagnostic**: among records with (C=+1), the fraction with (B=1), its complement (\Delta_F<0) and exact zeros; accompanying mean and median (\Delta_F). This conditions on the sign-generation result *as a descriptive diagnostic*, not as confirmatory experimental randomization or a new field posterior.

**Secondary full-enumeration comparisons**:
1. 3×2 joint counts: (C=+1,0,-1) by (B=1,0), with exact zeros separately.
2. 3 developmental contexts and attack levels 0.5/1.5/3.0, all populations retained; show counts in each cell.
3. Pr((B=1) | (A_{11}=1)) and Pr((B=1) | (A_{11}=0)) globally, plus the number of rate×context strata with **both** (A_{11}) classes represented. Any within-stratum standardized contrast must report the eligible stratum fraction, and must not silently extrapolate to absent classes.
4. Positive/negative compatibility gains under the synthetic 5% floor (C_{viable}), preserving all original denominators.
5. Model-level means (E[C]), (E[\Delta_F]), context-specific mean (E[\Delta_F]), cross-checking G8 audit and all published intervals; no replacing the G8 primary estimand.

**Uncertainty**: 10,000 paired background bootstrap draws, seed 20261107, with each of the 256 structural IDs resampled as a cluster across *all* rates and contexts; apply the *same source-index draw to numerator and denominator*, and report pointwise 95% descriptive ranges. Do not resample 20,736 records independently, interpret source-bootstrap ranges as field CIs, or produce new confirmatory p-values. In any rate/context subgroup with no compatibility creation, report zero denominator / not estimable, not zero chance of benefit.

**Validity and stopping**: reject altered raw-file SHA, missing/duplicate source-rate-context rows, incompatible previously published overall G8 means, undocumented rate/context exclusions or spurious pooled inference; report all sign/benefit quadrants, including if generating a pattern happens to predict benefit. Inference is about this synthetic model family, not the biological effect of actual dragonfly/salamander larvae or natural adult frog choruses.

**Editing gate**: change the main article's central claim only if the full enumeration materially changes the correct statement. Keep the prior R1 geographical association, the G5/G7 failed predictive gates, all R2/P1/R4 positives and G8 full-rate result unchanged.