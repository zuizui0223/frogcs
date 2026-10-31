# PR #146 — observed-sign and zero-state pattern-oriented comparison (2026-10-31)

This **post-result** directional audit responds to the user's request to choose a scenario reproducing the *direction* of broad NAAMP patterns, not to force a perfect quantitative effect-size match or to claim causal field evidence. It is separate from the previously completed 132-case quantitative POM and 8-draw demographic sensitivity; neither result will be overwritten.

## Fixed input and shared estimand

4,248 NAAMP sites, 63,180 complete acoustic surveys, predictor-only real-site mapping of Odonata suitability, pond-breeding Caudata suitability and remote 3 km flooded vegetation. The frozen 132 original 80-year model surfaces come from **all four** `literature_extension_20261029` source files; their biological rates are not re-tuned.

For both SDM backgrounds, the six *joint observed* rank patterns are

`OS, OV, SV, OSV, O_with_S_low, O_with_S_high`.

Use the identical 4,248-site rank estimand already audited by `pattern_oriented_abc_pilot.py`. The observation is **strong adult calling**, while the simulation is an **aquatic F_B cohort**. Only compare directional/categorical patterns under a common positive monotone response assumption; never treat the rank link as a measured adult acoustic calibration.

## Observation uncertainty and what is allowed to count

Obtain **999 whole-spatial-block bootstrap replicates** of the entire *joint six-dimensional* observed vector (same block draw for every component). Record each pattern's negative-resampling fraction `p_negative`, positive-resampling fraction `p_positive`, 95% intervals and source point sign. These are **bootstrap resampling frequencies**, not posterior probabilities that the signs are biologically true.

Binary sign patterns are eligible as *primary* directional constraints **only** if `max(p_negative,p_positive) >= 0.90` in that SDM background. Other uncertain patterns remain in the audit but cannot reject a scenario simply for one unfavorable sign. No strength or sign is imported from the earlier 49/49 sensitivity count, which is not this bootstrap probability.

The low-S O–calling correlation is **always explicitly ternary**: negative / practically near zero / positive. Define the near-zero threshold **before seeing the candidate outcomes** from the observed bootstrapped 95% interval:

`delta_zero = max(0.05, (quantile_97.5 - quantile_2.5)/2)`

in rank-correlation units. Bootstrap mass below `-delta_zero`, inside `[-delta_zero,+delta_zero]`, above `+delta_zero` gives `p_lowS_{negative,zero,positive}`. **A non-zero category is not "proven equivalent to zero" by this threshold**. An ambiguous observed three-way vector must be disclosed as such.

## Uncertainty propagated to simulated sign scenarios

For each **distinct F_B response surface** (collapse 132 exact duplicates first), at the exact 4,248 field sites generate 64 **paired** hypothetical replicates with the same sampled rank-to-grid monotone warp and the same block/site noise realization across model groups:
- O/S rank transport exponents each uniform in `[0.8,1.2]`.
- rank-observation noise scale uniform in `[0.2,0.8]`, with fixed site + 0.25 shared spatial-block Gaussian components.
- Same random-noise/warp draws for all scenarios to prevent finite-Monte-Carlo ranking differences between exactly identical source surfaces.

These are *illustrative observation uncertainty ranges*, **not calibrated field error or a prior on biological capture rates**. Report both strict deterministic source signs and the noisy simulated sign probabilities `q`. All 132 labels map onto groups, so duplicate cases do not receive duplicate prior weight.

## Comparison and chance controls

- **Primary directional compatibility:** `mean_{obs_block_boot,sim_noise_draw}[exp(-log(4) × number_of_category_mismatches)]` over the high-confidence binary patterns and the one low-S ternary state. This is a **joint categorical similarity score** retaining observed/simulated correlations among patterns, *not a probability the ecological scenario is true*. A strict complete-match frequency is also reported.
- **Secondary marginal composite agreement**: product of `Σ_s p_{k,s}q_{k,s}` for the selected patterns; since summaries are correlated, do **not** call it a likelihood or posterior without a validated joint generative observation model.
- Report the **equal-category combinatorial chance reference** `1/(2^K × 3)` for K selected binary constraints plus the ternary low-S component, explicitly as an independence benchmark, **not a calibrated ecological null or p-value**.
- Group models by their **deterministic directional signature** (much coarser than exact response-surface identity). Report how many distinct directional signatures occur and the size of the broadest indistinguishable group.
- To verify recoverability, generate 8 independent synthetic label replicates per distinct surface (same hypothetical rank noise family, held out from scoring reference draws); assign each by **nearest categorical mismatch to candidate q distributions**. Report exact-source-group and direction-signature-group recovery separately. Low recovery = directional data cannot uniquely identify a biological mechanism. Never give exact-case recovery credit to a duplicate response surface.
- Primary constraints and grouping are chosen from **observed bootstrap only** and are fixed before examining the synthetic model scores. Do not select a favorable background: show both independently.

### Heldout pattern audit

For the top **observational-direction-compatible group(s)**, inspect O–calling correlation in V=0 and V-positive subsets and within-route OS/OV. The four patterns have independent observed-only block-bootstrap 95% intervals from the prior POM audit but are *different summaries of the same original NAAMP sites*, not external field validation. Report matches and failures in all four; do not use them to revise the winning direction group.

## Biological-rate ensemble

The earlier **actual** 8-draw × 24-structure × 80-year re-simulation is a separate genuine process-parameter sensitivity, with **unverified illustrative numeric parameter ranges**. If its output artifact is available, perform the *same* direction-state audit over its actual `process_prior_predictive_patterns.csv`; the eight parameter draws are not calibrated posterior draws. Do not manufacture additional replicates or call a normalized acceptance share a biological ABC posterior.

## Extra “risk amplification” alternative

The user's proposed **danger amplification** is distinct from the existing `behavioral_refuge=True` suppression mechanism. Its exact extra pathway, life stage and mathematical rate have **not** been specified or field-calibrated in this project. Before any scientific inference, define a new optional model edge such as D-induced amplification of S-on-F encounter risk (versus documented D-induced suppression) and test it as a **separately labelled hypothetical structural mechanism**, with the original source kernel and frozen prior results immutable. Do **not** mislabel the existing risk-refuge scenario as danger amplification. That new mechanism is *not among the 132 previously run cases* and cannot be counted as having been numerically tested by this audit.

## Outcome limits

A scenario may reproduce only pattern *directions*, even when the six continuous observed effect sizes are badly mismatched. The correct result is “directionally compatible within chosen observational uncertainty and model assumptions”, not “best proven ecological mechanism”. Avoid any `x%` **posterior probability** until stage-appropriate parameter priors and adult-calling observation model are independently grounded and checked.

Freeze complete scores, all failures, grouping, pseudo-confusion, chance benchmark, 999 bootstrap receipts and source hashes into the Draft PR; leave `main`, PR #144/#145 and source-model kernels unchanged.
