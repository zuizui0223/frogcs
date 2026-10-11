# v6.8 — independent local numerical reconstruction of shared logger error counterexample

> **Final v6.8 CI status update, 2026-10-11 JST:** The previously queued [GitHub Actions run 38108980247](https://github.com/zuizui0223/frogcs/actions/runs/38108980247) subsequently completed **SUCCESS**; its actual workflow logs reproduce **every five-seed local number below** (oracle, one logger, four independent, rho 0.75, rho 1 and wrong-wetland placebos). The historical statement further below that CI was "QUEUED" is preserved as the state *when that local comparison was first written*, not as current status. Both are entirely synthetic source-free results; no biological effect is established.


**2026-10-11 JST — source-free SYNTHETIC calculation.** This is a preliminary **local re-execution of the same frozen formulas and logistic-model specification**, not an official completed GitHub Actions run, not biological data and not a field-instrument accuracy estimate. Independent draft PR #135 only. JAE RC6/main unaffected.

## Authority and execution distinction

- Frozen before numerical readback: [v6.8 common-mode sensor contract](V6_8_COMMON_MODE_DEPTH_LOGGER_ERROR_COUNTEREXAMPLE_CONTRACT.md).
- Committed implementation: [`scripts/test_correlated_depth_loggers_false_chorus_history_v68.py`](scripts/test_correlated_depth_loggers_false_chorus_history_v68.py), importing the already-frozen v6.6 artificial true ecology and v6.7 prediction matrix.
- GitHub Actions workflow: [38108980247](https://github.com/zuizui0223/frogcs/actions/runs/38108980247). **Status at this recording: QUEUED; not yet a CI PASS.** Do not silently describe the local result as this run's output.
- Separately, the formula and model fitting operations in the committed Python files were reproduced locally with Python, NumPy **2.3.5** and scikit-learn **1.8.0**, single-threaded BLAS. This reproduced the earlier v6.6/v6.7 known *oracle* sequence exactly: `[-0.001526, +0.003547, -0.001700, -0.003388, -0.003092]`. The v6.8 random instrument stream uses its own frozen seed offset and therefore its one-noisy condition is not numerically identical to v6.7's separate random instrument stream.

**Every simulated call label was generated with the direct past-acoustic causal coefficient fixed to exactly ZERO.** Five seeds; 180 invented wetlands; 24 invented episodes; only the last episode per wetland tested; history feature contains the completed training episode immediately before the test. Wetland propensity fitted only in historical training data.

## Actual LOCAL reconstructed numeric output

Signed paired held-out **negative-log-loss** improvements when adding previous call to a baseline already containing *observed* present depth, observed phase, observed EMA water history, diel proxy and training-only wetland propensity. Positive numbers mean a prediction improvement despite zero direct biological carryover **by construction**.

| Artificial measurement regime | Median apparent lag gain (5 seeds) | Gains by seed | Median WRONG-wetland lag placebo gain |
| --- | ---: | --- | ---: |
| ORACLE true water | **−0.001700** | −0.001526, +0.003547, −0.001700, −0.003388, −0.003092 | −0.001454 |
| ONE independent noisy sensor (invented error SD 1.10) | **+0.010257** | +0.003691, −0.003306, +0.010257, +0.017378, +0.011322 | −0.000519 |
| FOUR independent errors, averaged (rho=0) | **+0.000644** | +0.000798, +0.000309, +0.000644, +0.001263, −0.001301 | −0.000767 |
| FOUR errors with shared component, rho=0.75 | **+0.006490** | +0.007106, −0.001826, +0.007746, +0.006490, +0.003443 | −0.000281 |
| FOUR fully common errors, rho=1.00 | **+0.008675** | +0.009780, −0.000735, +0.008848, +0.008675, +0.004917 | −0.000916 |

All units, noise SD, wetland histories, observation years, and logger counts are **invented**. Error correlation rho=0.75 is an experimental assumption, **not estimated** from Flow-MER. Correlated instruments are not independent replicated measurements merely because the device count is four. The one-sensor results in this v6.8 synthetic experiment are based on a different noise stream from v6.7 and should not be numerically equated across independent seed setups.

## What changes scientifically

1. **A negative spatial-history placebo is insufficient to rule out source-local latent environmental confounding.** Prior calls of the SAME site can proxy water history left unmeasured by noisy local instruments, while a different-site history predictor remains uninformative.
2. **Adding devices alone is insufficient** when their errors share a calibration datum, physical placement issue or a wetland-scale unmeasured environment. With all four measurement errors perfectly shared, averaging cannot remove that error.
3. Accurate contemporaneous depth measurement alone is not the full environmental state; antecedent depth trajectories, real inundation continuity, dry-interval duration, thermal/soil/microhabitat conditions and detection noise also matter.
4. An observational lagged-call score gain is **predictive information**, not an identified causal acoustic memory, adaptation, reproductive payoff, individual fidelity or cross-wetland relay mechanism.
5. **This is one source-free counterexample, not a theorem or Type I error/power estimate for real data**; it neither implies typical sensor correlations nor that frogs in Murrumbidgee exhibit the simulated pattern.

## Source evidence decision: stop adding artificial worlds

The v6.5–v6.8 suite has now shown:
- correctly specified toy models distinguish known null, water-only and injected lag regimes (v6.5);
- omitted true slow-water state can induce a false lag gain (v6.6);
- noisy or incomplete depth measurement can leave the false gain with a logged-water covariate (v6.7);
- shared logger error can defeat independent-sensor averaging (v6.8 local reproduction, **CI still queued at recording**).

**No further unprompted synthetic mechanism family should be used to lengthen the current frog paper or imply accumulating biological evidence.** The only evidential upgrade is an authorised original Flow-MER independent physical wetland ↔ recorder ↔ water logger ↔ time/quality source manifest, actual logger calibration and missingness metadata, validated acoustic detections, and rights.

The existing metadata-only custodian enquiry is **UNSENT**. Revise *only its source dictionary request* to ask for instrument precision, reference datum, calibration/maintenance and cross-logger common error assumptions; do not request animal values at this first contact. No JAE RC6 main changes or PR merge.
