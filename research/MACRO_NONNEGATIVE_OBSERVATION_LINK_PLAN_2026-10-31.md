# Follow-up sensitivity: a nonnegative statistical cohort-to-calling coefficient

**Status:** post-result assumption test, declared after the 24-candidate nested selection and after observing **8/10 negative log(F_B) slopes**. This does **not** establish that `F_B` (aquatic cohorts) is monotonically linked to adult calling. The test asks whether the already chosen candidates still contain independent predictive information if negative log(F_B) slopes are prohibited.

- Hold **exactly the previously selected scenarios in each of 5 outer blocks**; do not pick a different model using the outer heldout outcomes.
- Keep the original source/cohort, both SDM backgrounds, suitability-rank mapping, vegetation proxy, site controls, ridge penalty 10, all outer folds and unmodified environment-only baselines.
- Change only the learned coefficient of the final mechanism input `log(F_B)`: constrain standardized logistic coefficient **beta_F >= 0**, with all other parameters reoptimized on the *outer-training blocks only* by bounded L-BFGS-B. A boundary slope zero is permitted and should numerically reproduce the environmental **additive** model, since adding a zero mechanism signal is equivalent to omitting it.
- Score outer fold strong-call count/visits by paired held-out log score, against the original unconstrained model and both fixed environment benchmarks; stratify V-positive vs V-zero.
- If a negative unconstrained slope is set to zero, report **nonidentifiability under this hypothesis** rather than evidence that the ecological mechanism is false. If the constraint improves scores, it still is not independent biological calibration; if it worsens them, the prior descriptive fit depended on a sign assumption that is not externally verified.
- This is *not* new scenario selection or a formal confirmatory holdout because the NAAMP cohort has been examined repeatedly. ABM/PDE methods are unrelated to this issue.

Code tests must verify that a boundary coefficient is exactly or numerically equivalent to the additive environmental null, preserve the previous unconstrained probabilities bitwise or to 1e-12, and prevent heldout outcome leakage.
