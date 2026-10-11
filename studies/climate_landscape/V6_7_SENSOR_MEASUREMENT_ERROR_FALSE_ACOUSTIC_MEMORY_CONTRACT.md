# v6.7 — frozen sensor-error counterexample: nominal logger control may not remove false acoustic memory

**2026-10-11 JST.** Independent draft PR #135; this contract is committed before v6.7 artificial outcome readback. The study is exploratory at project level; this is a **synthetic stress test only**, not a newly preregistered ecological hypothesis, a type-I error calibration, or a source-backed frog result. Submitted JAE RC6/main remains untouched.

## Decision advanced beyond v6.6

v6.6 proves an **unmeasured cumulative local water state** can make prior calls predict future calling when there is no direct biological acoustic-history mechanism, and that including *oracle true synthetic slow water* removes the median spurious gain.

But real depth loggers do not provide the true ecologically relevant state without error. Even one valid instrument may have finite resolution, sensor drift, uncalibrated datum, missed readings, or fail to capture microhabitat moisture. **The presence of a logged depth covariate is not the same as adequate hydrological-history adjustment.**

### Frozen artificial data-generating truth and error scenarios

Reuse the EXACT v6.6 source-free truth generator, `generate(seed, direct_acoustic=0.0)`, with **180 invented wetlands × 24 invented chronological episodes × seeds (20261011–20261015)**, including site propensities, depth AR, true cumulative slow-water dependence, and **exact zero direct prior-call effect**. No code/parameters in the original v6.6 generator are modified.

Before looking at results, fix four *observation* regimes for the **same** artificial call outcomes:

1. **ORACLE_UNOBSERVABLE**: exact true synthetic water depth, derived phase and EMA slow state (upper reference; not a real sensor).
2. **ONE_NOISY_LOGGER**: measured depth = true depth + independent zero-mean Gaussian error with standard deviation **1.10 artificial depth units**. Derived phase and EMA computed only from these noisy readings.
3. **FOUR_LOGGERS_MEAN**: four independent errors per instant per wetland, all with standard deviation **1.10**, averaged to create a synthetic multi-sensor depth estimate. No assumption four real sensors actually exist in Murrumbidgee.
4. **ONE_NOISY_LOGGER_WITH_GAPS**: same single noisy instrument with **25%** of scheduled depth observations missing completely at random; use backward-only last measured depth as a ***deliberate demonstration of a risky imputation***, retain missingness and time-since-valid-reading features, and never use a future reading. This is not an endorsed real source-processing rule (the actual feasibility protocol must instead obey source-approved maximum gaps).

The synthetic EMA parameter **0.84 previous + 0.16 current** is the known data-generating hydrology filter; the test gives every competing hydrological model this deliberately generous correct functional form applied to its own observations. Even with the right filter, **measurement error may leave residual confounding**.

### Identical model fitting and target comparison

Train on artificial episodes 1–22; evaluate only episode 23. Lag predictors use only episode 22 (complete training observation), never episode-23 call labels. Include training-estimated synthetic wetland fixed propensities, current **observed** depth, measured depth-change phase, observed-water-derived slow state, synthetic diel and (for gap scenarios) missingness/age-since-valid-reading. The **same measured hydrological predictors and same held-out outcomes** are used in each paired comparison:

- **B**: full available hydrology + wetland propensity, **without** prior acoustic calls.
- **B+lag**: same B plus true *completed prior episode* call. There is **ZERO true direct lag by construction** in every regime.
- **B+shuffled lag**: control with prior episode calls permuted across invented wetlands.

Score **mean held-out negative log loss** on the identical synthetic last-episode 180 outcomes, report each seed and five-seed median; higher `B+lag-B` is better as **prediction**, but may be entirely confounded. Report `B+shuffled-B` alongside to show that even a successful wrong-wetland placebo does not identify memory.

### Frozen expectations, not post-hoc acceptance thresholds

- ORACLE: genuine lag should not **consistently** improve, consistent with v6.6's oracle model.
- ONE_NOISY_LOGGER: spurious lag could become positive because historical acoustic labels proxy the same unobserved slow water. Negative/noisy results are also scientifically reportable as limits of this chosen synthetic regime.
- FOUR_LOGGERS_MEAN: reducing *independent* measurement error may attenuate spurious lag versus ONE_NOISY; no required numerical magnitude and no sensor benefit should be claimed without readout.
- ONE_NOISY_LOGGER_WITH_GAPS: arbitrary backward imputation can amplify uncertainty; its sign is not predetermined.

**DO NOT change the stated noise levels, proportions, seeds, model features or regularization after inspecting the first readout to force this narrative.** An inconclusive demonstration must remain inconclusive.

## Identifiability and source-stop consequence

- If even the appropriately specified noisy-logger baseline yields spurious historical-call gains, the real inference needs **source-level instrument accuracy, calibration, depth-gap patterns and measured-versus-latent hydroperiod sensitivity**; an original `depth` column alone is insufficient.
- A standard deviation of 1.10 is purely invented relative to artificial water units, **not an observed logger error** or prevalence in any real wetland.
- A priori source QA must still authenticate independent wetland×recorder×local logger/time/valid silence/quality/classifier and rights, with hydrological uncertainty and environmental confounding. The *only* CEWH metadata request is still **UNSENT**; no outcome-driven real-data retuning is allowed.
- A real historical-call gain is **predictive**, not proof of individual memory, social facilitation, hydrological causality, reproductive success or adaptive payoff. JAE RC6 remains frozen.

No source animal, site, geometry, audio or hydrology observational records accessed by v6.7.
