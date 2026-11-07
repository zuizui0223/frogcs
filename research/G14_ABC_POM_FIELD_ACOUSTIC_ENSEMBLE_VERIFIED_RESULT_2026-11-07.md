# G14 — ABC-selected original model interaction templates versus geographically heldout adult frog calling

**Completed, source-verified 7 November 2026.** The original 80-year model R2 proposals (20,000 source 8 shards) and the original NAAMP adult acoustic cohort (4,248 sites, 63,180 visits) were input without biological rerun or field response-based source selection. The original numerical model and field source SHA256s, 5 geographic folds, 56 spatial blocks, two SDM backgrounds and all 50,976 heldout site×background×candidate prediction rows passed independent source and numerical audit. [G14 pre-outcome fixed protocol](G14_ABC_POM_FIELD_ACOUSTIC_ENSEMBLE_PROTOCOL_2026-11-07.md); [successful run and independent direct-NLL audit #42376332598](https://github.com/zuizui0223/frogcs/actions/runs/42376332598); [G14 archived source receipt](results/g14_abc_pom_field_ensemble_20261107/G14_source_holds_and_claim_limits.json).

## Main empirical prediction result: one background improves, dual-background gate is unmet

The ABC-style model-native screening had previously accepted **794/20,000** synthetic model proposals generating four log aquatic frog cohort signs OS−,OV−,SV+,OSV+ at epsilon 1e-6; this set contained **647 canonical structure IDs**. The unweighted mean four-factor *interaction* coefficients of those original 794 accepted proposals was set **without examining new G14 acoustic outcomes**. All 20,000 original proposals, including failures, contributed to fixed comparison source templates. A single positively constrained acoustic source slope and the flexible original environmental coefficients were fitted *only on training geographic folds*. No actual predator abundance, reproduction probability, field trophic relationship, or natural-rate prior was fitted.

### Geographically heldout binomial NLL, baseline minus model (positive means improvement)

| Comparison per original completed acoustic visit | Uniform SDM background [56-block 95%] | Target-group background [56-block 95%] |
|---|---:|---:|
| **Flexible environmental additive baseline minus \`ABC_accepted\`** | **+0.001155 [+0.000253,+0.002427]** | **+0.000163 [−0.000548,+0.000931]** |
| Flexible additive minus \`ABC_accepted_viable\` (426 source proposals) | +0.000995 [+0.000059,+0.002274] | +0.000203 [−0.000525,+0.000988] |
| Flexible additive minus **all 20,000 original priors** | −0.0000010 [−0.0000018,−0.00000016] | −0.0000592 [−0.000593,+0.000534] |
| Flexible additive minus **19,206 rejected source proposals** | −0.00000002 [−0.00000089,+0.00000094] | −0.0000362 [−0.000322,+0.000266] |
| **Unrestricted four-interaction environmental model minus \`ABC_accepted\`** | **−0.000021 [−0.001681,+0.001273]** | **+0.000816 [−0.000971,+0.002508]** |

The model hypothesis' **primary 2-background heldout gate FAILED** because the target-group background's 95% resampling interval included zero. Its stronger gate, improving over the unrestricted O/S/V 4-interaction statistical model in both backgrounds, **also FAILED**. Recomputing all NLLs from each saved site-level predicted Bernoulli probability and original strong-call counts agreed with archived scores within <1e−12. Reweighting to a more favorable background *after* the result would be post-selection and is not done.

**Positive but bounded finding:** The source-accepted ensemble gained geographically heldout predictive value over a flexible additive baseline **in the uniform SDM background only**, and the 426-accepted-with-artificial-survival template was also positive in that same background. The two fixed synthetic prior/unaccepted templates did not show comparable robust improvement. The ABC-selected source template had a nonnegative fitted slope in all five folds in both backgrounds, while original all-proposal and rejected templates had zero slopes in all five uniform-background folds. This *within-source conditional pattern* is consistent with some predictive structure, but the original four-sign target was drawn from the same overall acoustic-association question; it is not a new independent observational mechanism discovery.

### Absolute heldout prediction NLL per visit (smaller is better)

| Model | Uniform | Target-group |
|---|---:|---:|
| Flexible additive environmental baseline | 0.673687 | 0.675933 |
| **ABC accepted-template + flexible environment** | **0.672532** | **0.675770** |
| ABC accepted+synthetic-floor template | 0.672692 | 0.675729 |
| All-original-prior template | 0.673688 | 0.675992 |
| All-original-rejected template | 0.673687 | 0.675969 |
| Unrestricted four original O/S/V interactions + flexible environment | **0.672511** | 0.676586 |

All entries were obtained from exactly **4,248 unique sites × 2 backgrounds × 6 fixed candidates = 50,976 heldout site rows**, each strong adult-call outcome scored only by the corresponding out-of-56-block fold prediction. The original 56 blocks partitioned into five geographically heldout folds by the existing R1/G5 protocol; two SDM backgrounds are alternative predictor backgrounds on the **same** sites, not independent datasets. NLL is the binomial deviance component per completed survey; group-cluster bootstrap uses exactly 999 56-block resamples with seed20261106.

## Why this does not establish an empirical ABC posterior or wild mechanism

The source templates were generated from the *original 794 accepted model-native four-sign patterns*, not posterior samples fitted to NAAMP adult frog-call likelihood. Given four saved original contrasts (OS,OV,SV,OSV) of the log aquatic frog cohort in the 2×2×2 plant×salamander×odonate source design, the model-derived field proxy is exactly

\[
\phi(O,S,V) =
  (OS-\tfrac12 OSV)\,O S
  +(OV-\tfrac12 OSV)\,O V
  +(SV-\tfrac12 OSV)\,S V
  +OSV\,O S V,
\]

using **site-rank transformed habitat suitability** (O and S) and a **3-km flooded-vegetation proxy**, not measured local predator abundance or submerged refuge. Its field predictor is **algebraically contained in the original unrestricted empirical four-interaction O/S/V statistical basis** (maximum numerical span residual <1e−8). Therefore a positive one-dimensional regularized field improvement cannot be interpreted as discovery of a new ecological covariate or empirical proof of the source trophic process.

The adult strong-calling probability is not the simulated larval cohort population. A positive constrained source slope is an uncalibrated statistical association; the study has not independently established the larval-to-adult-calling observation model, natural predation rates or causal vegetation effects. In the original G5, a separate pooled-source ensemble did not beat environmental alternatives robustly; G7 likewise failed its pre-fixed independent species-composition predictive gates. The new G14's positive uniform-only result **does not overturn** those decisions. More importantly, background sensitivity prevents a dual-background field predictive conclusion.

## Retained scope, reproducibility and source results

- [G14 complete source-hash and field-gate receipt](results/g14_abc_pom_field_ensemble_20261107/G14_source_holds_and_claim_limits.json).
- [All 4 original source templates and original N=794/426/20,000/19,206](results/g14_abc_pom_field_ensemble_20261107/G14_original_ABC_source_templates.csv).
- [All 16 paired dual-background comparisons and 56-block pointwise intervals](results/g14_abc_pom_field_ensemble_20261107/G14_block_paired_all_source_template_competitions.csv).
- [All site/background/model heldout predictions with original strong-call outcomes](results/g14_abc_pom_field_ensemble_20261107/G14_all_4248_heldout_site_predictions.csv.gz).
- [All 12 heldout scores](results/g14_abc_pom_field_ensemble_20261107/G14_original_acoustic_NLL_scores.csv) and [all five-fold source-slope records](results/g14_abc_pom_field_ensemble_20261107/G14_5fold_source_slope_fits.csv).
- [Original-source G14 analysis](scripts/g14_abc_ensemble_geographic_acoustic_holdout.py); [balanced eight-corner factorial-algebra unit tests](scripts/test_g14_abc_ensemble_geographic_acoustic_holdout.py); [successful G14 original field SHA/score audit](https://github.com/zuizui0223/frogcs/actions/runs/42376332598).

**Scientific decision:** Original model-native ABC acceptance contains a synthetic source interaction shape that gave a modest positive heldout acoustic contribution under one SDM background, but **failed** the preread fixed two-background gate and cannot outperform an unrestricted interaction model robustly. Its field mechanism remains unvalidated. G13's conditional-null selection, G8/G11's model-family structural replication and P1's developmental inversion remain valid *model-side* positives, not newly confirmed natural trophic causes.
