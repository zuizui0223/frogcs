# PR146 — model-native 2×2×2 directional POM and actual demographic ABC-RF

Frozen **before** the new model-native factorial simulations are run, 2026-10-31. This is a **post-NAAMP exploratory model comparison**: the same OS−, OV−, SV+, OSV+ target signs have been repeatedly examined. This analysis compares the *ability to generate these directions*, not field cause.

## Target and experimental unit

**Only the four environment-unadjusted broad-scale empirical *signs*** specified by the user: `(OS,OV,SV,OSV)=(-,-,+,+)`. No original site suitability, SDM background, rank correlations, 3-km vegetation sampling, R² match or adult-calling noise is transported to the simulator. No "low-S ≈0" category.

Every hypothetical structural mechanism is run in **its own complete 8-cell full factorial** on the untouched 120-day stage network plus 80-year demographic recurrence, with `V=0/1`, `S_source=.25/2.0`, `D_source=.25/2.0`, initial frog cohort F=1. `F_B` is mean preseason F aquatic cohort over years 61–80. The input S/D are model supply densities, **not observed NAAMP SDM suitability**.

Define `f[v,s,d]=log(F_B[v,s,d])` (primary ecological *log-density* scale). Let `D(v,s)=f[v,s,1]-f[v,s,0]`, `S(v,d)=f[v,1,d]-f[v,0,d]`. The balanced orthogonal interaction contrasts are

- `OS=1/2 * sum_v (D(v,1)-D(v,0))`;
- `OV=1/2 * sum_s (D(1,s)-D(0,s))`;
- `SV=1/2 * sum_d (S(1,d)-S(0,d))`;
- `OSV=(D(1,1)-D(1,0)) - (D(0,1)-D(0,0))`.

The same four are also computed on untransformed `F_B` as a **pre-declared sensitivity**; higher-order signs may differ by response scale. Sign precision tolerance `1e-9` applies to each finite contrast; contrasts within tolerance receive sign=0 and **are not accepted** as matching positive/negative biological direction. Include a sensitivity for signs at `1e-11` and `1e-7` without reselecting a favorable threshold. No extra noise: model-native differences are not rank correlations, so the previous rank saturation does not apply.

## Structural hypotheses, same priors for all

**12 primary structural classes** = 3 stage arrival/size contexts (`original`, `D_first_S_overtakes`, `S_first_D_overtakes`) ×2 handling families (`baseline`, `shared_both`) ×2 behavioral-refuge switches. Exactly **12 model classes**, not the entire earlier 3,600 exploratory designs or a claim that all 132 cases are equivalent.

The frog postmetamorphic→emerging dragonfly reversal is a **latent Bernoulli(0.5) structural nuisance** within each class. Every draw is evaluated with BOTH edges ON/OFF and averaged with equal prior weight, eliminating Monte Carlo imbalance between the two nuisance states. It is **not** presumed always indistinguishable: store paired outcomes and compare sign vectors at exactly matching rate vectors. If it changes signs, report this as nuisance sensitivity, not verified equivalence.

Before inspecting outcomes, draw **N=256 rate vectors per class**, each evaluated under both latent reversal states (**512 actual full 80-y simulator runs per class**, with an optional earlier tiny CLI smoke test), using identical Latin-hypercube draws shared among the 12 classes to reduce Monte Carlo imbalance. Fixed hypothetical ranges copied from the *previously documented* process-prior stress test:
- global attack multiplier `logUniform(.25,1)`;
- relative S growth and D growth `Uniform(.75,1.25)` each;
- local return/mixing `rho Uniform(.55,.90)`;
- synthetic annual conversion `Uniform(2,6)`;
- frog juvenile survival `Uniform(.6,.9)`;
- frog annual survival `Uniform(.25,.6)`;
- maturity delay discrete 2/3 years, 1:1;
- reverse D emergence edge on/off, 1:1 within each demographic class.
- seasonal dates, F aquatic duration, S/D other maturity/survival, vegetation refuge kernel and the type-III/II litter switch are frozen to the original research source.

**These intervals are not independently estimated ecological priors.** The ABC posterior and RF estimated selected-class support, if computed, are **conditional on these hypothetical prior ranges, deterministic simulator, model set and four observed signs**, *not real-world model probabilities*. Do not fabricate literature calibration or model adequacy.

## Real simulator validation

The code uses the original `stage_network_extension_20261029.simulate` (unmodified) on a vectorized ensemble of 8-cell treatment blocks, and implements the annual recruitment recurrence **identically** to the unmodified `extension_annual_summary_20261029.summarize_years`, with per-row variable demographic parameters. Before reporting any inference, rerun all 24 original baseline source cases' **8 corner cells** and match the archived `primary_0_dynamic_cells.csv.gz`, `primary_1_dynamic_cells.csv.gz` preseason F_B and F_fraction to absolute tolerance `1e-8`. Any failure blocks analysis. Test annual offspring maturation timing (F delay2/3, S2, D1), positivity, propensity to recompute identical result with same seed, 8-vertex complete shape, high-order contrast scale sensitivity, and exact on/off identity controls.

**Computational batching** is permitted to share one kernel call across parameter draws and classes, but it must not replace the actual 80-year model with interpolated outcomes or a single-season proxy. Store every **12×256×2 =6144** actual parameter×class×reversal full-model run, eight source cells each (49,152 vertices), plus source hashes. The paired reversal ON/OFF must be compared at exactly matched rate draws (not assumed identical) and then marginalized at 1/2 each for each model class.

## POM and ABC model choice

For each structural class, report (i) all 16 possible four-bit sign counts, (ii) fraction exactly matching `(-,-,+,+)` on log and raw scale, (iii) counts of numerically zero contrasts, (iv) joint rejection-ABC acceptance rate with Wilson intervals, and (v) the selected-parameter conditional distributions vs input priors. For equal 1/12 model priors, normalized exact-match acceptance fractions give a **discrete summary-statistic posterior under the stated *hypothetical* parameter priors**; zero matches everywhere means **undefined**, not equal posterior. The 1/16 fair independent-sign rate is only a mathematical reference, *not* a calibrated null test; the four contrast signs are correlated.

**ABC-RF model choice** (Pudlo et al., *Bioinformatics* 2016, DOI https://doi.org/10.1093/bioinformatics/btv684): classifier on four signed summary bits (log primary; raw and a fixed 50:50 log/raw response-scale prior as sensitivities); balanced class priors; out-of-bag **prior error rate**, 20% wholly held-out Latin-hypercube draw IDs shared across all classes, 12×12 confusion matrix. **Model vote fraction is not a posterior probability**; train an independent second regression forest on OOB misclassification indicators to estimate `1−P(error | observed four bits)` for **the RF-selected class only**. Report cases where observed bits occur rarely/never in the reference library and refuse to overinterpret the classifier's output. Optional RF reference learning cannot exceed the 16 unique four-sign patterns: class identifiability must be scored before posterior rhetoric.

POM/ABC-RF cannot rescue an unrepresentable target or a high-error classifier. If classification accuracy is near the equal-prior 1/12 chance level or the four signs are noninformative about the 12 class labels, conclude **MODEL_CLASSES_NOT_IDENTIFIABLE_FROM_FOUR_SIGNS**, not a uniquely selected biological network. If the exact-match target occurs but for many classes, describe all compatible structural families and what prior parameter regions produce the pattern. Do not make background/scale/noise arbitrations a primary result.

## Reproducible output contract

One separate GitHub workflow with a deterministic pilot and unit tests; create source-backed `parameter_draws.csv`, `prior_predictive_reference.csv.gz`, `factorial_corner_baseline_replay.csv`, `signed_pattern_acceptance.csv`, `rf_class_confusion.csv`, `rf_selected_class_summary.csv`, `posterior_parameter_summary.csv`, per-sign-pattern counts, and SHA256 receipts. All original source kernels, main branch, PR #144 and #145 remain unchanged. Remain Draft until simulation results/accuracy audited; no commit of incomplete data as a positive result.
