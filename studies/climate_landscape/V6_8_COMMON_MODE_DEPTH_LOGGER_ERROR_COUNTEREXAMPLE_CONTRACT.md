# v6.8 — frozen COMMON-MODE logger error counterexample: four sensors may still leave false frog-history gain

**2026-10-11 JST.** Committed BEFORE the first v6.8 synthetic data readback. Independent draft PR #135 only. This is a post-v6.7 exploratory **source-free algorithmic stress test**, not an empirical frog result, proof of common instrument error in Murrumbidgee, or preregistration of historical observations. JAE RC6/main stays frozen.

## Specific question

v6.7 showed that, in an invented world with **exact ZERO direct previous-call influence**, noisy or missing depth measurements could leave a positive held-out predictive gain for previous calling; averaging four independent error signals attenuated that false gain.

What if four loggers **share a substantial common error** due to datum/calibration/site wetness processes? Averaging many correlated sensors is not equivalent to independent replicate environmental measurements. A correct source-level logger count alone is therefore insufficient.

## Frozen truth and error-generating mechanism

- Reuse **without modification** the v6.6 `generate(seed, direct_acoustic=0.0)` function and the same 180 synthetic wetlands × 24 synthetic episodes.
- Five deterministic seeds exactly **20261011–20261015**.
- Same fixed sensor error SD **1.10 invented water-depth units** as v6.7; **no source-calibrated error estimate** is implied.
- Construct **four simultaneous synthetic sensor errors per wetland and episode** as

  `e_i = 1.10 * (sqrt(rho) * common_z + sqrt(1-rho) * independent_z_i)`,

  with all `z` from pre-fixed independent standard-normal random streams, and source-free scenarios `rho = 0.00` (fully independent), `rho = 0.75` (mostly common-mode), and `rho = 1.00` (fully shared). Each sensor retains marginal SD 1.10 by construction. All four devices measure the same artificial latent site depth and are averaged.
- One noisy sensor comparator uses sensor 1 of the `rho=0` generated array; its source-free marginal SD is 1.10.
- Oracle exact true synthetic depth comparator uses zero sensor error.

No missing-depth model here, as v6.7 separately tested 25% synthetic gaps. Do not modify coefficients, seeds or correlation cases after first readback.

## Frozen model and pass/fail logic

For every condition use the same invented frog outcomes, same identical held-out **episode 23**, earlier training episodes **1–22**, same baseline features and L2 logistic regularization as v6.7:
- observed current depth, observed depth-change phase, recursively derived EMA water history, synthetic diel term and training-only wetland propensity, plus explicit zero-valued missingness/gap-age covariates;
- compare paired `B` against `B+correct_completed_previous_episode_call`, and against `B+wrong_wetland_shuffled_previous_call`;
- report median and all five signed improvements in **held-out negative log loss** for every regime. No per-clip P-value or significance claim.

**Necessary software invariants**: oracle observations equal the true generator water, one-sensor/four-sensor source arrays are deterministic, per-sensor generated error variance is equal across `rho` in population, all history used is previous completed training episode, full shared `rho=1` produces four identical sensor values. No original frog or environmental source is queried. If a test fails, report and repair the software error without outcome-driven changing of the frozen model.

**No preselected sign threshold**: median gains can be positive, negative or inconsistent; those are outcomes of the synthetic test, not grounds to tune `rho` or acoustic truth. Report whether common-mode error *attenuates less* than independent error, but do not claim it must.

## Scientific boundary

- Demonstrating a spurious lag prediction under common-mode error would strengthen a **counterexample**, not evidence that genuine frog populations possess a memory mechanism.
- A real logger network might have shared or independent errors, and a single depth sensor may not measure pond microhabitat inundation. Obtain source sensor model/precision/calibration, datums, paired logger deployment dates, time-gap distributions and independent site IDs before treating local hydrological history as adjusted.
- A wrong-wetland acoustic history placebo may be negative in all these cases even if the true same-site lag is predictive only because of local hydrology.
- Required original acoustic classifier calibration, valid negative listening opportunities and rights are not yet obtained. The single CEWH custodian inventory request remains **UNSENT**, source API 403 is not circumvented, and JAE RC6 remains unchanged.
