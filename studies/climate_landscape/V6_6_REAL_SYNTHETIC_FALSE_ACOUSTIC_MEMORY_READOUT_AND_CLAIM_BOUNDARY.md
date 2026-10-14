# v6.6 REAL CI execution — omitted slow hydrology creates FALSE apparent acoustic-history information

**Date: 2026-10-11 JST.** This is an **executed SYNTHETIC counterexample**, **NOT a biological result from frog observations**. Independent draft PR #135 only; JAE RC6/main not changed.

## Execution provenance

- [Pre-read synthetic mechanism and interpretation contract](V6_6_OMITTED_SLOW_HYDROLOGY_SPURIOUS_ACOUSTIC_MEMORY_CONTRACT.md) committed **before** first model outcome.
- [Artificial source generator and four-model test](scripts/test_omitted_slow_hydrology_acoustic_lag_v66.py).
- [**Actual GitHub Actions run 38107962770 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38107962770). The workflow completed and printed the actual numerical contrasts; unlike API source checks returning 403, this is a true execution of an entirely simulated calculation.
- 5 fixed deterministic seeds (20261011–20261015); 180 **invented wetlands**; 24 **invented chronological wetting episodes**; 1 terminal episode per invented wetland withheld from training; synthetic original calling labels created from a known generative process.
- Site propensity was learned only on synthetic training episodes; pseudo site fixed-effect columns and identical held-out samples were used in every comparator. The lagged call feature uses only an immediately prior completed artificial episode. No evaluation labels enter fitting.

## Results — actual printed synthetic paired held-out NEGATIVE log-loss gains

| Artificial generating truth | Apparent calling-history gain with SHORT hydrology | Calling-history gain after TRUE slow hydrology is modeled | Gain from adding true slow water vs short hydrology | Wrong-wetland lag placebo gain (full hydrology) |
| --- | ---: | ---: | ---: | ---: |
| **H0: true direct acoustic-history effect = exactly ZERO** | **+0.013938** | **−0.001700** | **+0.075807** | **−0.001454** |
| **H1: genuinely nonzero direct acoustic-history effect injected** | **+0.114296** | **+0.030201** | **+0.127557** | **+0.000116** |

The entries are **medians across five seeds** of paired per-source-sample negative-log-loss differences; **not ecological effect sizes**, P values, confidence intervals or estimated incidence rates.

More importantly the H0 naive positive gains by seed were:
`+0.017373, +0.001524, +0.011720, +0.025122, +0.013938` (all 5 positive).

After controlling the *actual known artificial slow water* in H0, the lag gains were:
`−0.001526, +0.003547, −0.001700, −0.003388, −0.003092` (4/5 negative).

In H1, where a direct lag was truly programmed into the data, **all 5** adjusted gains remained positive:
`+0.028909, +0.028985, +0.030201, +0.033841, +0.035162`.

## Ecological interpretation, with the correct epistemic boundary

**Synthetic falsification result:** the generative H0 contains no real acoustic-state-to-acoustic-state effect, but a model with incomplete water history gives previous calling an **apparent positive predictive gain on future held-out data**. Prior calling proxies cumulative wetland wetness. This gain disappears on the median after the *known data-generating slow water state* is included, while the truly injected H1 acoustic carryover remains detectable.

Therefore:

1. **An out-of-year M2 positive log-score gain is insufficient to identify biological acoustic memory or even an independent ecological acoustic state.** It could be an omitted local hydrological history proxy.
2. Including a short rising/falling phase is **not automatically enough**. Need direct same-wetland local depth history, realistic hydroperiod, previous dry interval and uncertainty/missingness represented adequately, ideally with strong independent hydrological validation.
3. Site fixed effects and strict chronological train/test blocks protect against some confounding and prediction leakage; they do **not** by themselves remove time-varying omitted environmental states.
4. The wrong-wetland history placebo is useful but **not sufficient alone**: the H0 genuine previous-site call can predict slow water even while a shuffled previous-site call fails. The spatial specificity of predictive lag is not a proof of memory.
5. The v6.4 model comparison must use an **adequately specified, pre-outcome water-history baseline** in M1 before treating M2 as extra predictive ecological information. If historical water records or independent logger data are unavailable, classify `LOCAL_HYDROLOGY_HISTORY_UNMEASURED; ACOUSTIC_HISTORY_CAUSE_NOT_IDENTIFIABLE`.
6. Do not turn this artificial counterexample into an assertion about actual Murrumbidgee frog physiology, wetland memory, spawning success or JAE NAAMP mechanism.

## Direct future-study consequence

The only meaningful source next step is still an **authorized, original recorder × water-depth logger × independent wetland × date/time history and valid acoustic opportunity manifest**, plus source calibration, permissions and year-version data. Annual CEW inundation frequency or representative river-gauge discharge cannot substitute for exact local historical wetness. The single CEWH metadata inquiry remains UNSENT.

**QC outcome:** `PASS_SYNTHETIC_CONFOUNDING_COUNTEREXAMPLE`, **biology status** `NO_REAL_FROG_ANALYSIS; MECHANISM_NOT_IDENTIFIED`. Frozen JAE RC6/main unchanged.
