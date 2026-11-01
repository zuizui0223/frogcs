# PR160: original-source survival-floor and predator-edge sensitivity of vegetation refuge

2026-11-01. **PASS: [Targeted source-audit Actions #41298326487](https://github.com/zuizui0223/frogcs/actions/runs/41298326487).** Same unmodified 96 selected food-web M×stage×θ draws used in [the authoritative integrated model](INTEGRATED_234_MAIN3600_80Y_VERIFIED_RESULT_2026-11-01.md) (source run #41262102436). No new seasonal simulations, wild predation observations, ad hoc change to a sign criterion, or replacement of earlier positive results.

## Decision and meaning

**The ecology within this model is most clearly that the trophic recipient of vegetation shelter, not just the presence of vegetation, determines demographic outcomes.** F-from-S refuge increases the mean log aquatic frog cohort in all three original contexts. By contrast, vegetation sheltering S from D can lower F cohorts while allowing more structures to generate the predefined four-sign OS−/OV−/SV+/OSV+ signature. These are not empirical effects of natural wetland vegetation.

**A stronger claim that F-from-S refuge switches from improving to worsening the four-sign pattern with developmental timing is NOT robust.** The original 96-source data give +7.29/+8.12/−3.76 percentage-point passage effects in contexts 0/1/2, but all three 95% source Monte Carlo intervals include zero. When the post hoc original-selection survival criterion is imposed, all three passage contrasts are positive. This does not erase PR146's separate 64-source deterministic stage×plant finding: its stage scenarios, synthetic prior, handling/risk states and estimand are different.

## Exact provenance and checked design

- True original model source: PR #160 [80-year source run #41262102436](https://github.com/zuizui0223/frogcs/actions/runs/41262102436), **794/20,000 model-native 4-sign accepted**.
- Fixed selected subset: 96 accepted M×T×θ source IDs, **32 drawn from each original developmental context** before post-intervention analysis, original weighted mass 317/794, 265/794, 212/794. For each ID, 3 counterfactual contexts × F shelter from S ON/OFF or S shelter from D ON/OFF = 576 matched source responses. Primary conditional bootstrap resamples original *source draw IDs* within their original stage-selection strata, not 576 nominal intervention rows as independent field sites.
- Inputs: `posterior_paired_plant_stage.csv` original SHA256 `878bdcbb909598bc02459c1be178a9e91eddd7700e7dcc4a8c15325ba547f905`; `selected_draws.csv` original SHA256 `739ac81c0e781451537d5485a362bb1be27d9807fda03842c82ca2a0f0e82934`. The audit fails if original source bytes, IDs, 6 responses per source, weights, original 32×3 sampling or source group flags differ.
- **Survival-floor eligibility:** 50/96 selected draws met **both F and S minimum 5% survival in their own ORIGINAL source context**, not necessarily in every one of the three intervention contexts. Their source-stratum counts are 21, 24 and **5** out of 32. Thus the selected floor sample is imbalanced and small for originally early-S cases. This is an **exploratory selection sensitivity**, not independent confirmation or a field-calibrated viability requirement.
- Actual D→S predator edge ON in 77/96 sources; the 19 edge-OFF sources have **exact zero response** to `cover_DS` ON−OFF in all three counterfactual contexts. Original survival-floor and active edge both hold in 37/96 draws (strata 12,21,4).
- 20,000 fixed source-stratified bootstrap replicates, seed 20261101, for each subset. **Intervals measure Monte Carlo variability among synthetic accepted source draws conditional on the model and filter, not real ecological confidence intervals.**
- [Complete CI/CSV artifact](https://github.com/zuizui0223/frogcs/actions/runs/41298326487): original 96-source independent 24-row contrast/interval table, **108-row** conditional floor/active-edge/combined sensitivity, exact provenance receipts. Independent local Python recomputation matched the full 108-row floor subset key measures within numerical precision, and the original prior 36-row analysis within `1e-15`.

## 1. The main 96-source analysis

Same source IDs, weighted within original accepted-context frequencies, model-native vegetation mechanism ON−OFF.

| Pathway / main developmental context | Δmean log(F_B) [95% source MC] | Δfour-sign passage (percentage points) [95% source MC] |
|---|---|---|
| F sheltered from S, 0 | **+0.04120** [+0.02696,+0.05805] | +7.29 [−4.37,+18.76] |
| F sheltered from S, 1 | **+0.04017** [+0.02537,+0.05805] | +8.12 [−1.05,+17.50] |
| F sheltered from S, 2 | **+0.10712** [+0.07727,+0.14025] | −3.76 [−11.89,+4.59] |
| S sheltered from D, 0 | **−0.00637** [−0.01093,−0.00235] | +1.04 [−7.08,+9.17] |
| S sheltered from D, 1 | −0.00315 [−0.00681,+0.00006] | **+8.96** [+1.87,+16.46] |
| S sheltered from D, 2 | **−0.01391** [−0.01842,−0.00985] | **+7.72** [+1.67,+13.98] |

These 96 source models were already selected for the original four-sign gate, so the conditional passage change is **not** an unconditional frequency of how often a refuge works over the full 3,600-catalogue prior.

## 2. Original-source 5% survival-floor sensitivity (50 draws)

| Pathway / counterfactual context | Δmean log(F_B) [95% source MC] | Δfour-sign passage, pp [95% source MC] |
|---|---|---|
| **F sheltered from S, 0** | **+0.03483** [+0.02033,+0.05159] | **+22.18** [+5.28,+39.08] |
| **F sheltered from S, 1** | **+0.03477** [+0.02011,+0.05135] | **+21.44** [+7.90,+35.72] |
| **F sheltered from S, 2** | **+0.12156** [+0.08816,+0.15914] | **+7.91** [+1.13,+15.06] |
| **S sheltered from D, 0** | **−0.00569** [−0.00892,−0.00291] | −0.37 [−9.01,+8.27] |
| **S sheltered from D, 1** | **−0.00379** [−0.00606,−0.00170] | **+15.05** [+6.02,+25.19] |
| **S sheltered from D, 2** | **−0.01266** [−0.01763,−0.00831] | +5.65 [−1.13,+13.18] |

In particular, **context 1** retains opposite signs for simulated frog abundance (negative) and four-sign passage probability (positive) under the floor sensitivity. Context 2's passage gain is *uncertain* after this filter; retain the original full96 positive point estimate as a conditional result, but do not describe its floor sensitivity as confirming the passage gain.

The target-model OV log coefficient under S-from-D shelter in context 1 decreases by −0.00763 [−0.01238,−0.00319] in this 50-source sensitivity, consistent with one geometrical contributor to the desired OV− direction. This is not an independently isolated pathway decomposition of all four coefficients and should not be promoted to an inferred wild trophic mechanism.

## 3. Directed predator edge activity and genuine structural null

- Active D→S only (77 sources): for S-from-D shelter, context 1 `Δlog(F_B)=−0.00397` [−0.00849,+0.00007], **Δfour-sign passage +11.29 pp** [+2.35,+20.74]; context 2 `Δlog(F_B)=−0.01752` [−0.02295,−0.01269], **Δfour-sign passage +9.73 pp** [+2.12,+17.34].
- Both floor and active D→S (37 sources): context 1 S-from-D shelter **Δlog(F_B)=−0.00522** [−0.00809,−0.00252], **Δfour-sign passage +20.73 pp** [+9.33,+34.20]; context 2 `Δlog(F_B)=−0.01744` [−0.02343,−0.01206], passage +7.78 pp [−1.56,+18.16] (interval includes zero).

The `edge_DS=0` zero effect in all 19 three-context pairs is an **exact source-verified mechanical negative control**, preventing a nominal plant role being double-counted when its target predator edge is absent.

## 4. How this relates to main, PR146 and PR159

- The original `main` comparison #1479/#1455 conditionally succeeded with a combination of F-from-S vegetation refuge, D→S feeding and `litter` attack response. #1455 does not require S→D predation. PR160's 272 successful 80y four-sign structures without S→D reinforce that **this one edge is not universally required in the tested prior**, not that it is absent in actual wetlands.
- PR146 generated strong plant×ontogeny modulation in its *own* deterministic 64-rate design. None of those positive model-native outputs was retracted. PR160 uses different three developmental source contexts, a subset selected on original four-sign success, and a different prior mixture; its source-floor result demonstrates why its own context-dependent sign claims must remain qualified.
- PR159's 4-rate, no-external-immigration, finite-N q3/q12 results are **directionally consistent** with the recipient-specific F versus S refuge distinction, but cannot be numerically pooled with PR160's originally retained external immigration and main seasonal model.

## 5. Publication decision and next gate

The credible mechanistic headline **is not "vegetation universally reverses predation by developmental order."** The supported model-native observation is that **protecting an intermediate predator can improve a selected interaction signature while reducing the model's focal prey abundance**; protecting the focal prey instead increases model frog abundance without necessarily increasing four-sign compatibility. Survival-floor selection changes some passage-direction outcomes, so report both source samples and the 19 exact null interventions.

The actual 4,248-location NAAMP acoustic model identifies *geographic conditional associations*, not local larval predator densities. PR158's unfitted site-proxy comparison found no common six-statistic-adequate model under both SDM backgrounds (uniform 0/768; target-group 7/768). No model-native accepted fraction or Monte Carlo interval is a field predation estimate or validated 80-year forecast.

**Durable reproducibility:** [Audit script for the original 96-source experiment](scripts/audit_integrated_234_stage_uncertainty.py) and [fail-closed survivor/edge sensitivity](scripts/audit_integrated_234_viability_sensitivity.py) both passed in [Actions #41298326487](https://github.com/zuizui0223/frogcs/actions/runs/41298326487). Manuscript updates are on the same PR160 research Draft; main and earlier results remain untouched.
