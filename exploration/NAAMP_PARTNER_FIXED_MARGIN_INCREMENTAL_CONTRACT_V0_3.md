# Partner identity attribution within a previously supported fixed-margin frog model (v0.3)

Frozen 2026-10-22, **post hoc after reading v0.2**. Separately labelled from the predeclared primary M0→M1 test. Does not reopen the RC6 paper.

## Motivation and exact predeclared follow-up

Under fully **nested** A/B geographic route training, the existing M0→M1 joint partner model improved heldout fixed-margin pseudolikelihood in both focal comparisons. Both partner coefficients had expected signs for the `Anaxyrus fowleri` contrast, but the negative `Hyla versicolor` coefficient reversed sign between the training folds. Therefore the joint model's positive score gain does NOT establish that the negative partner contributes independent predictive information.

To isolate this, fit exactly the **same** route-run source, historical SiteID scores, NWI coefficients, fixed C↔j swapping events, nuisance generic-other-frog richness and training/test folds as in contract v0.2, with one **additional nested intermediate model**:

- M0: NWI + strictly earlier-year physical SiteID fixed offsets, plus estimated generic other-taxon richness coefficient;
- **M_P**: M0 + `X_P` (positive partner `Lithobates catesbeianus` at stop);
- M1: M_P + `X_N` (`Anaxyrus fowleri` or `Hyla versicolor` at stop).

All three use the same ridge `3·sum(beta²)/2`, same ±3 coefficient bounds and exactly enumerated fixed-row/column candidates. No refitting of first-order NWI coefficients and no change of the predeclared triple identities. For each training fold F, original NWI first-order coefficients trained on F must be used in **both first- and second-stage fit for fold F**, then evaluated only on the complementary geographic fold. Strictly prior-year SiteID histories are allowed as survey-time information, not heldout outcomes.

## Reporting and fixed decision

At the per-survey-run level, decompose heldout conditional pseudolikelihood gain `M1-M0 = (M_P-M0) + (M1-M_P)` exactly, averaged over the exact same allowed C↔j choices. Check per-run additivity before storing an outcome.

For each fixed trio report:
- `ΔP` = `M_P-M0`: incremental positive partner value;
- `ΔN|P` = `M1-M_P`: **incremental negative partner value** after already knowing P;
- `Δjoint` = M1-M0, the original v0.2 endpoint as a reproducibility comparison.

For all three use route-clustered intercept 95% CI, **2,000 route-block bootstraps**, and the signed mean within each original A/B heldout fold.

Because this additional analysis is explicitly selected after examining v0.2 coefficients, classify `negative_partner_increment_exploratory_supported` only if all conditions hold:
1. Mean `ΔN|P` >0 with bootstrap 95% CI lower bound >0;
2. both geographically heldout fold gains in `ΔN|P` >0;
3. the fitted beta_N <0 in both training folds;
4. two-sided route-cluster P remains BH q<0.05 over the **two** fixed primary CI1–3 partner trios.

Otherwise `negative_partner_increment_not_established`. This is **exploratory transferable predictive information, not independently confirmed causal negative frog-frog interaction**. Even a failed ΔN|P does not negate the descriptive negative pair residual from same-run NWI+history fixed-margin comparisons.

Primary inference is CI1–3. CI2–3 is separately reported, but may be insufficient. Early→late remains descriptive only because the original NWI coefficients were trained over the full archive. If either model fails rank/optimizer gates, report fail-closed rather than fallback/refit.

**No subsequent search** over alternate taxa, moderators, spatial buffers, regularization or species thresholds if this diagnostic fails.
