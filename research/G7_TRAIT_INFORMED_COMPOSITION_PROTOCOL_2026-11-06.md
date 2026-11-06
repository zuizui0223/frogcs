# G7: pre-specified species-group moderation of the vegetation–calling association

**6 November 2026. Fixed before fitting or inspecting any new trait-group–calling association.**

This is a new, prospectively specified comparison in the already examined R1/G1–G6 cohort. It is not an independent sample, an external registry preregistration, or an outcome-blind study as a whole. The exact new grouping, model and decisions below are frozen in a separate Git commit before real G7 fitting. Existing positive and uncertain R1–R4, P1 and G4–G6 results remain unchanged.

## 1. Biological qualification before outcomes

The proposed test asked whether vegetation is more positively associated with strong calling where salamanders with longer aquatic development are suitable. A literature-only audit does **not** support a universal long-versus-short assignment for the five original pond caudates. Typical larval durations overlap: western tiger salamanders usually develop in 3–4 months, eastern tiger populations in New York/Michigan/Indiana in 2–3.5 months, spotted salamanders in 2–4 months and blue-spotted salamanders in 3–4 months. Overwintering is possible in both tiger and spotted salamanders. Eastern newts have aquatic adults, with subspecies-dependent direct aquatic development or paedomorphosis. Regional timing is not measured at the acoustic sites.

Therefore G7 tests a **trait-motivated species-group suitability contrast**, not a measured larval-duration gradient. The primary comparison keeps the aquatic newt separate. The user-proposed tiger-versus-all-other comparison is a single fixed secondary sensitivity, never a replacement if the primary is uncertain. No other group, taxon, duration threshold, synthetic rate, or background will be selected after results.

The five original taxa, keys, source URLs and classification reasons are fixed in [the trait evidence table](g7_trait_evidence_20261106.csv). Primary empirical evidence for newt life-cycle variation is Takahashi & Parris (2008), DOI [10.1007/s00442-008-1125-8](https://doi.org/10.1007/s00442-008-1125-8). COSEWIC and the species-account providers are synthesis sources for natural-history ranges, not measurements from NAAMP sites. P1 independently manipulated early arrival and prolonged aquatic duration; **neither a positive nor a null G7 result validates or falsifies that joint field mechanism**.

## 2. Immutable data and predictor construction

Reuse original main `5e2f0a87c639df373fa2700b29403d2ab417a1cc`, without retraining SDMs:

| File | SHA256 |
|---|---|
| `research/results/interaction_species_sdm_20261026/naamp_species_suitability.csv.gz` | `a2a7018e747349ff94b0b98c36fed0958458f652bfa658568c3a498141bdb637` |
| `research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz` | `cbb389264f8bf167f53b5dfd38c5e1a17aec6243cc6ce30cbb7ae3b5417f75ff` |
| `research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz` | `74d28435ce6e1a842e003eaa6754c6db373e026728cfbf457784814c47cd997c` |

Retain all 4,248 primary listening sites, 432 canonical routes, 63,180 completed visits, 56 original two-degree route-centroid blocks, and the original five folds. Vegetation is `flooded_3000m_mean > 0`: 506 positive sites and 3,742 zero sites. Do not substitute the older single-cell vegetation measure. The response is original strong-call count `k` among completed visits `n`; it is not tadpole abundance or recruitment. `suitability_percentile` is an environmental score percentile, not an occurrence probability or observed animal density.

Within each original `uniform` and `target_group` background define raw indices:

```
T = mean(s_mavortium, s_tigrinum)
B = mean(s_maculatum, s_laterale)
N = s_viridescens
A = (T + B) / 2
C = T - B
```

For coefficient interpretation, centre and scale raw A, C and N by their outcome-blind full-cohort means and population SDs, separately for each SDM background. Preserve raw indices and transformation parameters. O is the original rank-standardized odonate score; V remains 0/1. Do not rank C, use a T/(T+B) ratio, or weight species using acoustic results. The original five-species mean is exactly `0.8*A_raw + 0.2*N_raw`; omit original S from the new design to avoid redundant total-suitability predictors. Verify that this mean reproduces the original S to 1e-12.

The fixed secondary two-group comparison uses `R=(2*B+N)/3`, `A5=(2*T+3*R)/5` and `C5=T-R`, with the same outcome-blind standardization. It deliberately pools the different newt life history and remains a sensitivity on group definition.

## 3. One primary conditional association

Model site counts as binomial with the original fixed ridge penalty 10. The primary design has an intercept and:

```
O, A, C, N, V,
O*A, O*C, O*N, O*V, V*A, V*N, O*V*A, O*V*N,
original eight survey controls,
original six environmental controls,
original five geographical controls,
G1's fixed 21 nonlinear environmental terms,
V*C.
```

Survey: `n_visits,n_years,mean_air,mean_noise,season_2,season_3,season_4,mean_doy`.
Environment: `bio1,bio4,bio12,bio15,water_3000m_mean,herbaceous_3000m_mean`.
Geography: ranked/standardized latitude and longitude, their squares and product. The 21 nonlinear terms are six squared and 15 unordered pairwise products of rank-standardized environmental variables. OVA and OVN are nuisance context controls. No OVC term or outcome-selected nonlinear moderator is added.

The single target is **theta**, the coefficient on V*C: change in the vegetation log-odds association per SD increase in tiger-minus-other-Ambystoma suitability, at fixed total Ambystoma suitability and newt suitability. It is an average moderator under the specified absence of OVC. **Fit theta without any sign constraint.** The proposed positive direction is a trait-motivated hypothesis, not guaranteed by P1 without observed arrival order. A positive-constrained fit would not test that direction.

For the secondary grouping, replace the focal base by `O,A5,C5,V,OA5,OC5,OV,VA5,OVA5` and append `V*C5`; retain identical survey/environment/geographical controls. N is not additionally included in this deliberately pooled sensitivity.

## 4. Frozen uncertainty, support and prediction decisions

1. **Coverage before fitting:** require unique complete 5-species × 2-background predictions at all 4,248 sites, finite scores, unchanged source hashes and reproduced group means. Integrity failure stops analysis. Record C's within-block and between-block variance. Inspect no C–calling association during this stage.
2. **Support qualification:** use predictor-only full-cohort C tertiles with fixed cutpoints and unsplit ties. In each background each V=0/1 × C-low/high cell must have at least 20 sites, five routes, three blocks and 200 completed visits, following G4's pragmatic reference. For the primary full cohort and each training fold, the residual sum of squares of VC after projection on the intercept/nuisance base must be at least 1% of its centred total sum of squares. These checks qualify support; a failure does not justify redefining the groups. Continuous estimates may still be displayed descriptively, explicitly ineligible for the primary support claim.
3. **Primary coefficient intervals:** draw 999 paired whole-block bootstrap multiplicity vectors over the same 56 geographical blocks, seed `20261107`, and refit each primary and sensitivity model. Keep predictor transformations and full-sample numerical scaling fixed within coefficient resamples, and retain complete sites/visits in selected blocks. Report every failed fit; require at least 990 valid draws per comparison. Use two-sided percentile 95% intervals. These are conditional on fixed SDMs, selected covariates, ridge and species groups; SDM fitting/trait uncertainty is not propagated. They are penalized-model descriptive intervals, not bias-corrected causal confidence intervals.
4. **Primary claim:** only if both backgrounds pass support/identifiability/convergence and both theta intervals have lower endpoints above zero, describe a positive conditional group-composition association robust to the two SDM specifications. Both backgrounds reuse the same observations and are not independent replication. Preserve negative, opposite-direction and uncertain results. Secondary sensitivity cannot rescue the primary.
5. **Separate predictive check:** use original five spatial folds. Fit the frozen full design and identical null omitting only VC; fit numerical scaling only on training rows. Compare held-out NLL per completed visit, positive meaning null loss minus full loss. Use 999 paired 56-block score bootstraps, seed `20261107`, conditional on these saved predictions. Both background intervals must be positive to claim predictive improvement. Report each training theta without selecting folds. Association and prediction decisions are separate. Compare absolute NLL with the saved original additive-environment prediction if available, without refitting or selecting a new baseline.

No additional subgroup, alternative penalty, duration coding or further search is authorized by a favorable or unfavorable result. Main P1 and R1–R4 numerical results are retained. Geographic clustering does not remove habitat or geographical confounding; only four Ambystoma taxa contribute to the primary contrast.

## 5. Reproducibility and paper integration

Archive source hashes, fixed trait table, protocol SHA, group/site manifest, support and residual-information diagnostics, fitted coefficients, all bootstrap theta draws, saved held-out predictions, score tables and an execution receipt. The implementation uses the original acoustic helper from `a5ddc281ba17017a52b404a5725327f6e829824f`; any source transport/newline discrepancy must be documented before declaring byte identity. Test signed synthetic effects, site identity, missing taxa, count denominators, block resampling and fold separation before the real run.

Report G7 in the Supplement and a short main-text statement regardless of its result. Replace opaque Abstract wording with plain English describing the small vegetation-context improvements, their uncertainty and the stronger simple environmental model. Keep G4/G5's unmet gates and G6's retrospective label. The remaining submission tasks are factual author/data/licensing and journal production decisions, not an open-ended search for positive analyses.
