# G2B: Two-part observed frog calling audit — prospective source-locked prediction protocol

2026-11-05. **Frozen before looking at the two-part prediction results.** Continues the one-paper R1→R4 work without modifying R2/R3/R4 biological sources, R1 original observed associations, PR145's negative acoustic bridge, or G1's shared-environment control.

## Scientific question

Original G2 verified that the within-route odonate–calling association conditional on pond-Caudata suitability differed between *any recorded calling* and *strong calling* only under the uniform SDM background. This is a descriptive signal from the same cohort. Can an odonate × pond-caudate environmental-suitability interaction improve **spatially held-out predictions of (A) whether a call was recorded and (B) whether a recorded call was strong**, after survey, geography and nonlinear shared-environment controls?

The two outcomes are observed acoustic behavior/recording states, **not** occupancy detection probability or mechanistically calibrated frog larval survival. Splitting a strong-call probability into `P(any call) × P(strong | any call)` is a statistical identity under the original binary events, not a maturation or causal predator-detection model.

## Immutable input and observational denominators

- `main` frozen source SHA `5e2f0a87c639df373fa2700b29403d2ab417a1cc`: `primary_site_landscape_context.csv.gz` (4,248 original source sites); `naamp_completed_site_surveys.csv.gz` (63,180 completed visits among those sites), and `high_low_contrasts.csv` (original R1 geographic source).
- Original unchanged PR145 acoustic functions SHA `a5ddc281ba17017a52b404a5725327f6e829824f` for `prepare_sites`, `assign_spatial_folds`, `train_predict`, `log_score`. Reuse [verified G1](G1_SHARED_ENVIRONMENT_SPATIAL_BLOCK_VERIFIED_RESULT_2026-11-02.md) predictor matrices `design_matrices`.
- Source visit truths: any-call `47912/63180`, strong-call `36554/63180`, all `strong<=any`; exactly **66 sites with any-call zero**, leaving 4,182 with conditional strong records.
- Same 432 route components and 56 whole 2-degree geographical blocks, in the pre-fixed original **5 folds** with no route/block split; both original SDM backgrounds reuse source sites and are **not independent geographical replicates**.

## Frozen models, predictors, scoring and tests

Use the original 4 predefined statistical designs from G1, no outcome-informed feature selection:
- `env_add`: climate, water, plant, geographic and survey effort controls, additive O/S/V.
- `env_OS`: original `env_add` + O×S.
- `flex_add`: `env_add` + predeclared 21 nonlinear climate/water/vegetation terms.
- `flex_OS`: original `flex_add` + O×S.

Use PR145's fixed ridge penalty **10** on training blocks; no tuning on held-out visits. Fit three original binomial site-count likelihoods per background/fold/design:
1. `any_all`: recorded any-call count / completed visit count at all sites.
2. `strong_given_any`: strong-call count / any-call visit count *only where any>0*. The 66 zero-any sites cannot contribute to conditional stage likelihood; nevertheless predict conditional probability at all held-out sites for the factored probability.
3. `strong_all_direct`: direct strong-call count / completed visit count, as original G1 reference.

Construct `strong_all_factored = predicted(any_all) × predicted(strong_given_any)` in each test site without any held-out outcome information and score against all completed strong-call visits. Check `0<=p_factored<=p_any<=1` and source count identities; do not fit an extra outcome model.

- Primary contrast: `flex_add → flex_OS` *held-out conditional strong-given-any* NLL **per recorded any-call visit**, positive gain if O×S adds information; **must be positive with source-block-bootstrap 95% interval excluding zero in both backgrounds** before interpreting as independent background-robust predictive information. This would still not be an observed predation mechanism.
- Secondary: same incremental O×S added to `any_all`, `strong_all_direct` and `strong_all_factored`, across both flex/environment additive families; compare `strong_all_factored` to `strong_all_direct` under identical feature families. Negative results retained. Distinguish a conditional probability evaluated on 47,912 recorded any-call visits from strong-call NLL evaluated on all 63,180 completed visits.
- Original source strong-call `env_add` and `env_OS` held-out NLL must match published G1 values within **3e-5** for both backgrounds; original 5-fold, route/block and visit count must all agree. Site-level predictions archived once per background and design.
- Pair 56 **source spatial blocks**, not individual visits or sites as independent resampling units; **999 fixed block-bootstrap replicates, seed 20261105** on held-out predictions, without re-fitting. Both backgrounds/response definitions are tested on identical blocks and records; report all twenty-four planned contrasts and group denominators, not favorable outcome cherry-picking.

## Gate and publication interpretation

A robust conditional strong-call predictive result might localize the descriptive R1 signature to one *adult acoustic measurement stage*, not to frog larval abundance or direct/indirect predator effects. A non-improvement or change by SDM background leaves the original G2 observed geographic contrast intact while weakening interpretation as reproducible extra ecological information. Statistical factored/conditional output is **not true occupancy, independently calibrated survey detection, nor recruitment/age-class coupling**.

Preserve G1 negative/background-specific results, PR145 negative fixed full-environment acoustic bridge, and PR158 site six-statistic adequacy failure. No field trophic posterior, no model-generated 80-year wild forecast, no unblinded rate fitting. Save source rows, complete model scores, paired block intervals, exact source SHA and one diagnostic figure. Keep PR162 Draft, `main` untouched, no submission.
