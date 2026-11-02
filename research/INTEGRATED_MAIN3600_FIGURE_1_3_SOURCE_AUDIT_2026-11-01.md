# frogcs: Figure 1 and 3 source-backed scientific audit and reusable captions

2026-11-01. **RESULT: All four Figure 1/3 panels GENERATED and independently source-audited in [GitHub Actions #41317178174](https://github.com/zuizui0223/frogcs/actions/runs/41317178174).** PNGs and source SHA256 receipts are in artifact `frogcs-PR160-figure1-figure3-real-field-and-model-verified`. All original biology, geographic observational CSVs and earlier figures remain unchanged.

## Figure 1: actual geographic association (NOT simulated predation)

**Original immutable main SHA:** `5e2f0a87c639df373fa2700b29403d2ab417a1cc`. Data used by [Figure1 reproducible renderer](scripts/plot_integrated_234_macro_fig1.py):

- `research/results/naamp_odonata_caudata_associations_20261026/stratified_correlations.csv` (24 complete source rows; pond breeding Caudata, three suitability tertiles and two SDM backgrounds, whole-region vs within-route).
- `research/results/naamp_odonata_caudata_associations_20261026/high_low_contrasts.csv` (8 original source rows; both backgrounds, all Caudata / pond-breeding subgroups and spatial settings).
- `research/results/naamp_remote_vegetation_20261026/network_rank_coefficients.csv` (112 original 3-km landscape vegetation rank-model coefficient rows; selected term×pond breeding subgroup×2 backgrounds×within-route factors are audited as exactly 16 values).

**Figure 1A caption.** Observed site-level Spearman associations of Odonata mean *environmental suitability* with strong adult frog-calling frequency in low, middle and high pond-breeding Caudata-suitability tertiles (n=4,248 same NAAMP acoustic listening locations under each SDM-background specification). Points and whiskers represent observed within-stratum estimates and **95% route-bootstrap intervals**. Right panel shows high-minus-low contrasts: uniform −0.38475 [−0.50912,−0.24038], target-group −0.17869 [−0.32797,−0.02917]. The positive low-tertile uniform point estimate has an interval spanning zero; it is not proof of sign reversal. Both SDM-backgrounds reuse the same sites and are not independent replication. Odonata suitability does not measure odonate larval predation.

**Figure 1B caption.** Four rank-standardized model interaction coefficients (O×S, O×V, S×V, O×S×V), separately for whole region and within-route comparisons under two originally retained SDM-backgrounds. **95% route-bootstrap intervals** are conditional on the original fitted SDM scores; V is the source 3-km EarthEnv flooded-vegetation context (approximately 1-km input pixels), **not measured aquatic refuge complexity**. A whole-region positive O×S×V point estimate does not robustly replicate at the within-route scale. Effects are conditional associations, not observed prey survival responses.

## Figure 3: genuine original model outputs, distinct from the actual-site adequacy test

[Figure3 source-locked renderer](scripts/plot_integrated_234_population_fig3.py) joins the following *different* evidence sources only at the presentation layer:

1. [PR160 genuine 80-year source Actions #41262102436](https://github.com/zuizui0223/frogcs/actions/runs/41262102436), all four artifacts `integrated-234-finite-0..3` (`finite_predictions_shard_00..03.csv.gz`; **1,536 original model arms, 96 selected M×T×θ IDs, 2 stochastic seeds, q3/q12, S→F ON/OFF, movement ON/OFF**). Original accepted-context weights are (317,265,212)/794 across 32 IDs per original context. The original `draw_bootstrap_predictive_interval.csv` and `summary.json` come from artifact `integrated-234-final-scientific-receipts`.
2. [PR158 separate same-source/field-proxy audit #41215171866](https://github.com/zuizui0223/frogcs/actions/runs/41215171866), `all_original_same_theta_4248_site_POM_and_80year_outcomes.csv.gz` with 1,536 background×candidate rows and `real_site_six_pattern_model_adequacy_by_background.csv`. **768 candidate source structures/rate/q/movement cases per observed SDM-background**, 523 nondegenerate four-seed ensembles/background. No site observation transfer is empirically calibrated.
3. The Figure3 renderer recomputes all source-ID paired/weighted occupancy means from the **individual original 1,536 simulation arms** and validates against the frozen outcome table. It verifies 0/768 uniform and 7/768 target-group six-statistic marginal interval coverage by reaggregating the **individual 1,536 same-source observed-site models**, checking their model IDs and confirming no common candidate passes both backgrounds.

**Figure 3A caption.** Mean number of F-occupied artificial ring patches in model year 80 (0–8) under S→F predation ON or OFF and annual movement ON or OFF, conditioned on the 96 source-compatible original model/rate proposals. Two fixed hypothetical finite-count scales `q=3` and `q=12` are displayed separately. Points and whiskers are source-stratified synthetic Monte Carlo estimates (96 matched source IDs, 2 stochastic seeds each; 6,000 source-ID bootstrap repeats). **These are not natural pond numbers, real movement rates, or field population confidence intervals**. Original model source includes **external immigration ON**; the near-full q12 eight-patch limit makes occupancy differences less informative.

**Figure 3B caption.** Source-conditional moderation of the movement-associated model occupancy effect by S→F predation (difference of matched differences, F occupied patches). q3 −0.0092 [−0.2643,+0.2404]; q12 −0.0115 [−0.0694,+0.0411] from the original PR160 accepted-source bootstrap. Intervals straddle zero, so no robust overall predation-specific movement benefit has been established for this synthetic model.

**Figure 3C caption.** Adequacy of **a separate uncalibrated site-emission proxy** for matching six observed acoustic-site statistics, compared for the same 768 candidate source models against two SDM-backgrounds at 4,248 real monitoring sites. **0/768 uniform and 7/768 target-group** matched all six *individual marginal 95% observed intervals* (none matched both backgrounds); 523/768 source predictions/background were nondegenerate across all four finite-N seeds. These six marginal bands are **not a calibrated joint 95% criterion**, and seven target-group band coverages are not seven validated trophic causal mechanisms. This panel is not an extension of PR160's four-sign acceptance numerator (794/20,000).

## Publication claim gates

The verified Figure 1 result is a **geographical third-guild-conditional association**. Figure 2 provides **within-model recipient-specific vegetation effects on F abundance and four-sign pattern compatibility**; the original 96 accepted source samples and the exploratory 50 survival-floor subset must be shown separately. Figure 3 displays **model-only demographic outcomes and an empirical adequacy failure**, not identification of the food web underlying Figure 1. The appropriate integrated biological statement is:

> The demographic benefit of vegetation refuge depends on which trophic partner it protects and cannot be inferred directly from a geographically conditional interaction signature.

Neither the observation bridge nor native pond larval mortality has been calibrated; the connected outputs therefore **do not establish realized predation as the cause** of the adult-calling field association.

## Reproducibility and status

- [Figure1 and Figure3 complete source-gated CI](https://github.com/zuizui0223/frogcs/actions/runs/41317178174): **SUCCESS**, exactly four PNG panels plus two SHA256 receipts and eight-arm source F occupancy table; four original source paths checked, all 4 finite-N shards and both site backgrounds checked.
- [Figure 2 complete source-gated CI](https://github.com/zuizui0223/frogcs/actions/runs/41298704170): **SUCCESS**, 96 original M×θ accepted sources plus 50 selected-source original viability filtering.
- Full figure code is held on PR #160 with original main and PR #158/159 results unchanged.
- No manuscript submission, external field predation, observation calibration or coauthor approval is implied.
