# 80-year endogenous 4-sign ABC: biological rate-prior sensitivity, 2026-10-31

**One targeted question.** Does the prior result (original timing × baseline handling dominating `OS− OV− SV+ OSV+` among twelve stage-network classes) persist under plausible *alternative mathematical distributions on the exact same declared parameter support*? The 6,144 **real** 80-year simulated trajectories are reused; no re-fitting of the field response, no noise process, and no additional ABC-RF ballots are generated. Main `log(F_B)`, secondary `raw(F_B)`, all 4 signs only.

**Scientific boundary.** The process-rate ranges (attack .25–1, frog survival .25–.60, juvenile survival .60–.90, maturity delay 2 or 3) were **synthetic stress-test priors, not measurements from frogcs sites or independently established species priors**. The following changed densities are also hypothetical. Therefore even a robust ranking means only *conditional sign-generating capacity* of the candidate networks; never a calibrated field mechanism posterior. Reweighting an existing reference library does not count as 6,144 new model simulations or replace new simulations when a changed prior has support outside the original range.

## Frozen before the new sensitivity outputs

The analysis uses the **exact prior-rate draws and paired ON/OFF source outcomes** from successful [Genuine 80-year ABC Actions #41178134567](https://github.com/zuizui0223/frogcs/actions/runs/41178134567), three original source `*_prior_predictive_reference.csv.gz` files and their verified receipts, paired `*_parameter_draws.csv`. The current [source-verified class rates](results/model_native_abc_rf_20261031/abc_rejection_model_acceptance.csv) and [256-ID paired intervals](results/model_native_abc_rf_20261031/paired_prior_class_intervals.csv) must be rederived at baseline, tolerance 1e-12.

Equal prior weight on all **12** structural classes, equal latent reversal ON/OFF weight **within every common rate draw**. Source category target and interaction signs never change: log `F_B` 2×2×2 `(-,-,+,+)`; raw F_B is separate. The source-effective independent draw is the **shared rate draw ID (n=256)**, not the two reversal treatments counted twice. All classes use the same 256 rate vectors, so bootstrap resamples **the same draw IDs across all 12 classes**.

## Exactly eight prior variants (plus original)

1. **original**: the original log-uniform attack and uniform other continuous rate priors; 2/3-year maturation 50:50. Every draw weight exactly 1.
2. **attack_uniform**: replace the attack's log-uniform density with Uniform(0.25,1). Relative weight `a ln(1/.25)/(.75)`.
3. **attack_favors_weak**: triangular density declining linearly from .25 to 1 on attack. Importance weight `2×(1-a)/(.75²) × a×ln4`.
4. **attack_favors_strong**: triangular density increasing from .25 to 1; `2×(a-.25)/(.75²) × a×ln4`.
5. **frog_juvenile_favors_high**: triangular density increasing across juvenile survival [.60,.90]. Relative weight `2×(j-.60)/(.30)`.
6. **frog_juvenile_favors_low**: opposite survival triangle `2×(.90-j)/(.30)`.
7. **maturity_favors_2y**: two-year maturation probability .75 and three-year .25, vs source .50/.50; per-draw weights 1.5 or .5.
8. **maturity_favors_3y**: two-year probability .25, three-year .75; weights .5 or 1.5.
9. **joint_weak_attack_high_juvenile**: product of (3) and (5), intentionally a low-ESS stress case; report effective prior-draw sample size rather than inventing an accurate conditional posterior when weights concentrate.

These are explicit post-result prior sensitivity specifications, **not ecological calibrations**. Each density has support wholly inside the source prior support and is nonnegative. All weights are identical for each class at the same `draw`; the prior on structure and reversal is unchanged. Do not reweight `family` or `risk` to manufacture a winner.

For each scale and variant calculate a per-class `P(target sign vector | class, specified process prior)` as the **weighted average** of the two reversal acceptance indicators over unique independent `draw` IDs. Equal model priors give normalized conditional class shares `p_g/Σ_h p_h`; undefined when all p_g=0. Save model-class and marginal (ontogenetic timing / handling / refuge) shares and the effective prior ESS `(Σ w)^2 / Σw²`. Separate accepted-draw effective sample size and prevent interpreting sparse <20-effective-draw cells as well-characterized parameter regimes.

For uncertainty: 999 paired draw-ID bootstrap samples (replace IDs, preserve the same 12-class paired outcomes and source importance weights); report within-variant conditional 95% Monte Carlo share intervals, maximin and original-vs-stress share shifts. Do not compute p-values from the fair-sign 1/16 reference.

## Fail-closed

- Must load and independently validate all three real 80-year source artifacts using existing `model_native_abc_rf.load_actual_refs`; no synthetic surrogate data.
- The original variant must reproduce `abc_rejection_model_acceptance.csv` per-class log/raw acceptance rates and equal-prior shares at tolerance ≤1e-12.
- Every process draw must appear twice as ON/OFF for each of 12 structures; 12×256 unique class-draw aggregates, no dropped/null sign categories.
- Check importance-weight normalization and ESS for all variants; the input rate table must match all three original source contexts.
- On/off nuisance equality in *acceptance* is verified but never generalized to complete numerical identity.
- Do not add field observation likelihood, SDM-site mapping, rank-noise calibration, or unrelated studies to this targeted task.

## Publishable interpretation

If original timing/base handling remains high under all declared distributions with adequate ESS, report **structural robustness within the tested synthetic rate support**, not probability of the true trophic mechanism. If a variant weakens or reverses the class ranking, report the particular prior dependency transparently. The four signs from main are **pre-environmentally-adjusted statistical associations**, not direct measured larval interactions; POM's model-native contrasts are a cross-level *directional hypothesis comparison*, not a shared likelihood. Earlier rainfall/multisite/recurrent-place positive observational findings remain distinct and are not falsely claimed explained by a trophic network.

Keep this work on **Draft PR #146**, do not modify `main`, PR #144/#145 or prior frozen model/ABC output.
