# v6.7 real CI readout: noisy and incomplete depth logging can preserve false chorus-history gain

**2026-10-11 JST — executed SYNTHETIC stress test, not field evidence.** This report belongs only to independent draft PR #135. The Journal of Animal Ecology RC6 on main is unchanged.

## Source and model authority

- [Pre-outcome v6.7 frozen sensor-noise contract](V6_7_SENSOR_MEASUREMENT_ERROR_FALSE_ACOUSTIC_MEMORY_CONTRACT.md)
- [Actual v6.7 source-free test implementation](scripts/test_noisy_hydro_logger_spurious_acoustic_history_v67.py)
- [GitHub Actions run **38108587827**, completed **SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38108587827) with real script output; software execution succeeded and the source-free guard checks passed.
- The truth-generating mechanism was **unmodified v6.6 synthetic `generate(seed, direct_acoustic=0.0)`**, i.e. past acoustic state had exactly **zero direct effect** on the next episode. The same created animal labels and latent water state were reused across every sensor condition.
- 180 invented wetland identifiers, 24 chronological invented episodes, 5 fixed seeds, synthetic training 1–22 and held-out episode 23. Wetland propensities fitted on training labels only. Lag predictor from completed episode 22 only, never a held-out or future animal outcome.

## Numerical results from actual v6.7 workflow logs

Each entry is the median of five *paired held-out negative-log-loss* gain values, where higher means more accurate prediction when a **past call label** is added to a water-history/site baseline. Values are software diagnostics, not an effect size, P value, confidence interval or field-estimated instrument performance.

| Source-free water observation regime | Correct prior-call lag gain, although true direct lag = 0 | Wrong-wetland lag placebo gain | Simulated missing depth fraction |
| --- | ---: | ---: | ---: |
| ORACLE_UNOBSERVABLE — exact artificial water | **−0.001700** | −0.001454 | 0 |
| ONE_NOISY_LOGGER — one invented device, Gaussian error SD 1.10 | **+0.008036** | +0.000280 | 0 |
| FOUR_LOGGERS_MEAN — average of four INDEPENDENT noisy measurements | **+0.000793** | −0.000663 | 0 |
| ONE_NOISY_LOGGER_WITH_GAPS — noise plus invented 25% MCAR gaps, backward-only carry-forward | **+0.014437** | −0.000129 | **0.250972** |

Fixed-seed lag gains:
- ORACLE: `−0.001526, +0.003547, −0.001700, −0.003388, −0.003092` — **1/5** positive.
- ONE noisy: `+0.008036, −0.002815, +0.010085, +0.013829, +0.007570` — **4/5** positive.
- FOUR independent: `+0.000793, +0.001573, +0.001712, +0.000287, −0.001234` — **4/5** positive but small.
- ONE noisy + missing: `+0.014437, −0.000962, +0.010126, +0.020862, +0.018206` — **4/5** positive.

The artificial missing-data scenario deliberately carries the last measured depth forward and includes gap-length/missingness in the regression, not future data. **This is an intentionally risky illustrative imputation strategy**, not recommended source preprocessing. The actual Murrumbidgee logger error standard deviation, deployment gaps and number of independent concurrent sensors have **not been established**.

## Strong inference permitted, and inference forbidden

1. In this designed **zero-direct-lag** world, having a water-depth column and the right cumulative-water smoothing formula is **not sufficient** to remove a spurious lagged-call predictor when that depth is noisy or incomplete.
2. Averaging independent artificial sensors reduces the median false lag score from **+0.008036** to **+0.000793** in the specified test. This **does not establish** that four real loggers exist, are independent, or would provide a comparable improvement; common environmental/instrument calibration error could remain.
3. Even wrong-wetland label shuffling gives near-zero lag gain while the true same-wetland past label shows a false gain. Thus **spatial specificity, held-out predictive gain and a negative placebo do not jointly prove biological acoustic memory**.
4. This is not a type-I error calibration, power analysis, causal identification theorem, field sensor-noise estimate, change to the submitted JAE scientific story, or real evidence about frogs.
5. A future source-data study must establish sensor accuracy and calibration, timestamp/deployment continuity, completeness/quality of wetting history, wetland-level spatial linkage and classifier validity **before** reading the new source acoustic responses. Otherwise classify `HYDROLOGICAL_HISTORY_MEASUREMENT_UNCERTAIN; ACOUSTIC_STATE_CAUSE_NOT_IDENTIFIED`.

## Next falsification boundary

Averaging independent artificial loggers is a favorable condition. Real instruments may share **common-mode bias, datum drift, calibration error or site-level missingness**. A separate, outcome-free synthetic experiment may test shared logger errors, but its noise correlation and scenarios must be declared before reading that result, and it is not a substitute for actual instrument metadata.

**Status:** `SYNTHETIC_MEASUREMENT_ERROR_FALSE_GAIN_DEMONSTRATED`; `REAL_FROG_EFFECT_NOT_TESTED`; `SOURCE_WETLAND_RECORDER_DEPTH_MANIFEST_NOT_ACQUIRED`; `CEWH_METADATA_INQUIRY_UNSENT`; `JAE_RC6_MAIN_UNCHANGED`.
