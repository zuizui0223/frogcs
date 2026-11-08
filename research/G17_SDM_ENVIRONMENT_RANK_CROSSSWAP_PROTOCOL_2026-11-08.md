# G17 — Fully crossed environmental main effects × source-predictor SDM ranks in the original G15 field test

**Post-hoc 2×2 model-specification isolation protocol, fixed on 2026-11-08 JST before running any G17 crossed predictions.** G15/G16's same-original-NAAMP-source full scores and background reversal are already known. G17 does NOT provide an independent natural-pond sample, true predator density, direct larval survival, a field-conditioned ABC posterior, or proof of a trophic mechanism. No new original 80-year biology, NAAMP field records, SDMs, ABC source selection or after-result choice of predictors.

## 1. Explicit two components to exchange

Original G14/G15 \`flex_add\` contains environmental nuisance and original O/S SDM-suitability **main effects** from one occurrence-model background, \`env_bg∈{uniform,target_group}\`. The source-template interaction scalar \`phi\` contains **only** original O×S, O×V, S×V, O×S×V interaction terms, computed from the predictor-only rank01 transforms of O/S suitability under \`rank_bg∈{uniform,target_group}\`. In the original diagonal G15 both are the same source: \`(env_bg,rank_bg)=(uniform,uniform)\` and \`(target_group,target_group)\`. Therefore G15/G16 cannot independently assign the background reversal to which group of columns changed.

Create exactly the complete 2×2 grid:
- (U,U): original G15 diagonal, internal exact-source replay anchor.
- (U,T): original flexible environment from U, source-interaction O/S ranks from T.
- (T,U): original flexible environment from T, source-interaction O/S ranks from U.
- (T,T): original G15 diagonal, independent source replay anchor.

Keep the original V indicator at each of the 4,248 original sites in every cell; do not change the 3-km landscape flooded vegetation proxy. Source rank01 is the **same full-dataset predictor-only rank transform as G14** (transductive in covariates but no heldout outcome leakage). The original environment includes main effects of its own SDM O/S ranks, so crossing rank-source covariates is a *statistical model-specification counterfactual*. Off-diagonal source interaction directions are no longer necessarily in the original env_bg unrestricted four-interaction span; this does not constitute newly measured ecological data.

## 2. Fixed source and observation link

Use only the original G15 frozen \`G15_frozen_source_templates.csv\` validated by G15 SHA/source receipt, with **201 exact source shapes**: accepted 794 model source, one arbitrary SIGN_ONLY comparator, and 199 original 81-rate/context conditioned source-null templates (seed20261108), no source reweighting, no field-ranked model selection. Original G14/G15 **4,248 NAAMP sites, 63,180 completed visits, 36,554 strong adult calls, 432 routes, 56 disjoint geographic blocks, predictor-balanced five original folds**, original G14 source-locked site and visit hashes. Retain original \`flex_add\` environmental column set (including the main effect O,S,V), original ridge=10, original nonnegative single source-slope optimizer and original training/test fold membership for all cells. No environmental or source slope is trained on a heldout site's strong-call outcome.

For all 201 source templates ×4 crossed cells ×4,248 original sites compute **3,415,392 geographically heldout original site predictions** (and original 5-fold slope diagnostics). Source interaction templates and the original 199-null identities are fixed independently of all crossed test outcomes. Each prediction's binomial NLL is computed from original n completed visits/k strong calls. Retain every fit (including zero constrained source slopes); fail closed on nonfinite predictions or optimizer failure. Split four source-template shards by \`null_id mod 4\`; the ABC and SIGN_ONLY controls are in shard0.

## 3. Required original diagonal replication and fixed numerical tolerance

Before interpreting off-diagonal cells, replay the original G15 diagonal (U,U and T,T): for every one of the 201 source templates, require full **4,248 source-aligned site IDs**, original per-site original k/n, folds and geographic blocks. Compare original G15 archived **201×2×56 block NLLs** (not just the ABC overall mean) to G17 diagonal source re-fit scores. Original source numerical fit differences may arise from L-BFGS-B stopping. A priori diagnostic tolerance is per-original-site predicted p max difference < 1e-4 for ABC (G14 original ABC template), per-site old G15 source p < 1e-4 across all if original full shard source is available, overall per-visit absolute NLL difference < 1e-6 per template and background, and original 56 block NLL discrepancy per block < 0.02. If these fail, **stop before declaring any cross-swap scientific results**. Document actual replay maxima.

These are tolerances on reproducibility of an unchanged data/model numerical algorithm; they are not scientific significance gates and do not permit re-selection, retuning of regularization or alterations to response definition.

## 4. Four-cell source-mean and empirical-null metrics

For each \`(env_bg,rank_bg)\` cell:
- Compute the original 63,180-visit binomial NLL of ABC_794 and SIGN_ONLY; also the NLL distribution of all 199 rate/context null source templates.
- Define **D(e,r) = mean_199(NLL_null(e,r)) − NLL_ABC794(e,r)** (positive = ABC better), with one-source-randomization upper-tail p \`(1+#{NLL_null≤NLL_ABC})/200\`. Retain all source nulls and their counts. The 199 comparisons are model-template randomization, not independent observed ponds.
- Define the rank-swap effect at fixed environment \(R_e=D(e,U)-D(e,T)\), and environment-swap effect at fixed source ranks \(E_r=D(U,r)-D(T,r)\).
- Exact balanced **2×2 additive factorial decomposition** of the original diagonal contrast:
  \[
  \Delta_{\mathrm{diag}}=D(U,U)-D(T,T)=\frac{[D(U,U)-D(T,U)]+[D(U,T)-D(T,T)]}{2}
    + \frac{[D(U,U)-D(U,T)]+[D(T,U)-D(T,T)]}{2}
    =E_{\mathrm{avg}}+R_{\mathrm{avg}} .
  \]
  Also report nonadditivity \(I=D(U,U)-D(U,T)-D(T,U)+D(T,T)\).
- Exactly **9,999 paired 56-geographic-block bootstrap resamples** (same sampled original block IDs for all 4 cells, seed20261108), recompute the four D values, E_avg, R_avg, Δ_diag and I, report descriptive pointwise 95% block ranges. The 56 block sample is not an independent fresh cohort and these intervals are not independent mechanism-validation p-values.
- Report source null ranks for both crossed cells; do not select a more favorable off-diagonal arrangement as the revised paper's primary.
- Repeat the complete 2×2 calculation for the generic SIGN_ONLY baseline comparison as a diagnostic, not an additional field mechanism result.

## 5. Interpretation and stopping
G16's prior finding that **95.61%** of the G15 original background gain discrepancy originated in mapped V=0 sites remains a complete bookkeeping statement. G17's crossed refits can tell whether the **environmental main-effect model representation** or the **source O/S rank-interaction representation** has the larger *model-specification* influence. The components are not biological causal effects and, because the ridge-regularized nuisance refits interact nonlinearly with source rank geometry, the decomposition may have nonadditivity.

No matter which cell or effect is strongest, **G14 and G15's original precommitted two-background and unrestricted-interaction field validation gates still FAIL**. Retain G5/G7 non-support, the G13 conditional synthetic ABC structural selection, G8/G11 independent-structure **model-family** replication and P1 controlled developmental effect. If the diagonal replay fails at locked numerical tolerance, G17 is **unverified**, and no new manuscript conclusion should be made. Any subsequent original NAAMP post hoc selection cannot create a previously absent natural trophic identification. G17 is intended as the final diagnostic of G15's background sensitivity, not a basis for indefinite outcome-selected parameter tuning.
