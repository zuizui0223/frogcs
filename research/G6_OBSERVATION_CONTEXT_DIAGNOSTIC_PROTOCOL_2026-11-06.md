# G6: locate field–model agreement in the original observation contexts

2026-11-06. Diagnostic specification fixed before calculating the new context-specific outputs. This is a retrospective diagnostic of the completed G5 experiment, not a newly independent confirmatory test.

## One question

Does the modest G5 predictive agreement occur in the observed vegetation and third-guild contexts motivating the biological model, and which parts of the original R1 conditional association are reproduced by the archived predictions?

G5 has already finished. Its two-background primary prediction criterion was not met. G6 will not refit a model, alter a penalty or fold, select a developmental context or synthetic rate, or reclassify the G4 15/16 coverage result as a success.

## Fixed original sources

- Repository starting point: `e963b2bf8f8522117f7ac1cf6c10389f1766fbb2` (PR166).
- Original field files remain those at main `5e2f0a87c639df373fa2700b29403d2ab417a1cc`.
- [G5 run 42173456057](https://github.com/zuizui0223/frogcs/actions/runs/42173456057), artifact `13481904130`: all 50,976 held-out site × background × candidate predictions, original 12 scores and source receipt. ZIP SHA256 `784b7b89bbd82b9da6d31ff756f8a312dfada81fef417933127fd057f13ac108`.
- [G4 run 42173236906](https://github.com/zuizui0223/frogcs/actions/runs/42173236906), artifact `13481963468`: all 8,496 site × background predictor classifications, 16 corner support rows and source receipt. ZIP SHA256 `acc45c72a14490f2fefe9a648856fcd29fe48ab83298290d11771bcd40d12f90`.
- Fixed denominators: 4,248 sites; 63,180 completed surveys; 36,554 strong-call events; 432 route components; 56 geographic blocks; 506 sites with flooded vegetation recorded in the original 3 km landscape proxy.
- Retain both original SDM specifications and all six G5 candidates: `env_add`, `env_all`, `flex_add`, `flex_all`, `flex_prior_00`, `flex_prior_11`.

## 1. Context-specific prediction and calibration

The primary partition is original binary vegetation V0/V1. The secondary partition is V × original pond-Caudata suitability tertiles (six groups). Retain all 18 V × S-tertile × O-tertile cells as a descriptive appendix, including sparse and empty cells. Copy G4 classifications and check them against the original predictor-only quantile rule; do not change boundaries after inspecting calls.

For every candidate and group, report sites, routes, blocks and completed visits, observed strong-call frequency `sum(k)/sum(n)`, visit-weighted predicted frequency `sum(n*p)/sum(n)`, their difference, NLL/visit and Brier/visit. These are comparisons within the observed covariate distribution, not standardized vegetation interventions.

For `flex_prior_11`, retain four comparisons against `flex_add`, `flex_prior_00`, `flex_all` and `env_add`. Report both:

1. Within-group improvement = group sum of (comparator loss − 11 loss) / group completed visits.
2. Contribution to the whole-cohort improvement = the same numerator / all 63,180 completed visits.

Require the contributions of every complete partition to sum to the original whole-cohort gain. Independently reproduce all 12 G5 scores from saved probabilities. In particular, a benefit relative to nonlinear `flex_add` does not establish a benefit relative to the simpler `env_add`.

Reuse paired whole-geographic-block resampling (999 draws, seed 20261106) with the same block multiplicities for every group and comparator. Report the paired V1-minus-V0 difference in within-group improvement. Record the number of undefined replicates instead of replacing missing denominators by zero. The G4 pragmatic thresholds (20 sites, 5 routes, 3 blocks, 200 visits) mark group support; unsupported groups retain point summaries but no interval-based interpretation. These are pointwise descriptive intervals, conditional on the saved fitted predictions; they do not incorporate refitting, SDM or biological-source uncertainty, and are not adjusted for multiple comparisons.

## 2. The original R1 statistic on observed and predicted responses

Apply the same descriptive operator to observed site strong-call fractions and each candidate's saved held-out probability: Spearman(O, response) in the original high-S tertile minus that in the original low-S tertile. Report all sites as primary, with V0/V1 as context diagnostics. Retain the original O predictor as continuous; do not require the sparse G4 high-O/high-S/V1 corner or calculate a new full eight-corner four-sign decision.

Check the original all-site observed contrasts against the archived R1 point estimates (approximately −0.38475 uniform and −0.17869 target-group). Use shared 56-block draws for the predicted-minus-observed discrepancy and report support and undefined draws. This changes uncertainty clustering from R1's original route bootstrap; it does not replace the original published R1 intervals.

The Spearman correlation of a smooth fitted probability and that of a noisy observed visit fraction need not be equal even under a useful probability model. This is a response-shape diagnostic, not a complete posterior predictive test or a pass/fail criterion. No field mechanism is selected from whichever candidate happens to be closest.

## Interpretation and stopping rule

- Preserve G5's positive point directions and failed robust-prediction criterion together.
- A concentration of performance in V1 can locate predictive agreement in a relevant context; it is not a vegetation treatment effect. V0 predictions may also differ because G5 fitted separate observation and environmental coefficients for 11 and 00.
- G5's retained interaction polynomial is not statistically orthogonal to the environmental main effects. Its positive fitted coefficient is not an isolated estimate of a vegetation pathway or a biological larval-to-adult calibration.
- A simpler environmental candidate reproducing R1 is retained as an alternative explanation, not treated as a reason to delete the empirical association.
- Save the complete tables, source hashes, diagnostic figure, code and tests. Finish this diagnostic after replay and consistency checks; do not launch further fits to obtain a preferred direction.

No original biological kernel, source field records or G1–G5 results will be changed. This work remains a reviewable research branch.
