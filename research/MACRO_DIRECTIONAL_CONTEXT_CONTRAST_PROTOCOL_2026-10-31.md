# Direct signed-context-modulation POM: S-high versus S-low and V-present versus V-zero (2026-10-31)

**Aim:** advance the existing *direction-only* PR #146 without creating new trophic edges or forcing ABC posterior probabilities. The earlier ternary "low S ≈0" threshold was derived from the observed bootstrap interval and may be broad; this audit tests the sign of the **difference between conditional associations**, a biologically interpretable, threshold-free directional feature. This is post-hoc relative to the repeatedly inspected NAAMP dataset and cannot serve as a pristine independent confirmation.

## Pre-specified definitions (before inspecting these outcomes)

For every one of the same **4,248 sites**, **63,180 surveys**, both SDM backgrounds and identical globally ranked site predictors / strong-call fractions:

- `OS`: signed coefficient of O×S in the same pooled unadjusted 8-term rank OLS.
- `OV`: signed coefficient of O×V in the same OLS.
- `ΔS = corr(rank(O),rank(Y) | S high) − corr(rank(O),rank(Y) | S low)`, split on the median **SDM suitability** of pond-breeding Caudata (not observed salamander numbers).
- `ΔV = corr(rank(O),rank(Y) | flooded landscape V >0) − corr(rank(O),rank(Y) | V=0)`. Landscape V is a **3 km composite proxy**, not measured pond vegetation.
  
All rank calculations use **global ranks before stratification**, preserving the original PR #146 estimator. No alternative rank definitions chosen after seeing scenario results. ΔS and ΔV both express *more negative O–calling association in the higher-S or vegetation-present context*. A negative slope is association, not evidence of site-level trophic damage.

## Directly shared observed uncertainty

Build **one joint 999-replicate whole spatial-block bootstrap** for the 4-element vector `(OS, OV, ΔS, ΔV)`, instead of independently bootstrapping component signs. Each draw uses the same integer block multiplicities for coefficients and all four subgroup correlations. Record point value, 95% bootstrap interval and frequencies of negative/positive signs for every background.

Primary directional constraints are only those with `max(negative_fraction,positive_fraction) >= 0.90` under the actual bootstrap. Keep uncertain components visible but do not force their signs. Score sign agreement using **joint** observed/bootstrap and joint candidate sign vectors (penalty 0.25 per mismatch) rather than treating the four correlated metrics as independent likelihood contributions. Exact complete-sign match frequency is a separate diagnostic; no posterior probabilities or p-values.

## Competing simulations and identifiability

1. **Primary 132 fixed-rate catalog**: all four saved `literature_extension_20261029` source files. Feed every candidate through the **real NAAMP site O/S/V distribution**. Group byte-identical F_B surfaces before model/noise simulation (historically 104 exact-source groups). Reuse matched random site/block error and matched predictor-rank warps for *all* candidates (48 explicit hypothetical observation perturbations per source group, **not empirically calibrated acoustic noise**). Preserve all 132 cases, per-component model signs, grouped signatures and ranked joint directional score.
2. **Identifiability test**: independent 8 pseudo-observation noise draws per *source group* after fixing the model reference. Predict its 4-pattern direction-signature group using the reference joint categorical response. Store the full normalized confusion matrix and accuracy. Deterministically identical response surfaces must never be counted as independently identified cases.
3. **Secondary true-demography sensitivity**: reuse successful 80-year simulation artifact #41163370575 (8 matched process-rate draws ×24 original structures); do not fabricate extra biological draws. Compare the **same** 4-pattern directions for all 192 process-case/draw combinations ×2 SDM backgrounds; aggregate by original stage-structure group and report sign coherence over 8 draws. Draws have exploratory, *uncalibrated* predation/growth/recruitment/maturation ranges; do not call a rank "biological ABC posterior".
4. **Chance reference**: report both the simple independent fair-sign `2^(-K)` for K eligible constraints **as a pedagogical, not statistical null**, and the empirically enumerable fraction of exactly distinct source groups whose *deterministic* signs match all eligible field directions. The latter is a *candidate-catalog reference frequency* (not a permutation p-value). Model labels are not independent.
5. **Cross-background consistency**: the same scenario group must meet the eligible directions in **both** SDM backgrounds to claim cross-construction compatibility. Both backgrounds use the same NAAMP calls; they are sensitivity choices, not two independent tests.

## Decision

If at least one scenario has all robust observed directions, label it **direction-compatible conditional on the fixed proxy→source mapping** and show every tie/ambiguous response-surface group; do not demand magnitude or environmental-null predictive improvement. If none matches, label **NO_COMPLETE_SIGNED_CONTEXT_COMPATIBILITY**. In either case, show ΔS and ΔV disagreements explicitly, and preserve the earlier stronger low-S ternary test, which answers *whether low S is near zero* rather than just *whether high S is more negative*.

Do not search new predator amplification parameters, change the observation link sign, or require ABM/PDE. Keep full source SHA256 and GitHub Actions outputs on Draft PR #146; no `main`, PR #144/145 or original biological kernel edits.
