# G10 fixed post-hoc comparison: is G9's 73% loss excess explained by rate and developmental context?

**2026-11-07 JST.** This is a diagnostic on the complete archived G8/G9 synthetic experiment. Its analysis plan is committed before inspecting the rate×context-adjusted G10 estimates. G8 means and G9's 571/782 joint counts are known; this is **not preregistration**, a new biological simulation or an independent field cohort.

## Motivation and controlling denominator

G9 found lower model frog-cohort abundance for 571/782 (73.02%) source-rate-context comparisons where the 00→11 vegetation-function intervention *newly generated* all four model-native signs. Across the full 20,736 comparisons, 13,802/20,736 (66.56%) showed a negative frog-cohort response. These groups have different mixes of hypothetical rates and developmental contexts; a raw difference is not evidence that pattern generation itself predicts harm.

Read only the archived G8 paired table `research/results/g8_27rate_paired_20261107/audited/g8_all_source_rate_context_paired.csv.gz`, with its SHA256 checked against the G8 completion receipt. Preserve exactly 256 original structural backgrounds ×27 synthetic attack–recruitment–conversion cells ×3 original developmental contexts. Every original background/rate/context stays in the full joint ledger. No new 80-year biological runs, field records, model retuning or success-only background exclusion.

Definitions: `new=1` iff paired compatibility `accepted_11−accepted_00 = +1`; `loss=1` iff mean model log frog cohort `logF_11−logF_00 < 0`; exact zero is neither gain nor loss. Primary comparator `new=0` includes unchanged or lost compatibility, and sensitivity comparator `compatibility=0` includes unchanged only.

## Primary *rate×context-standardized* descriptive contrast

Define the 81 prespecified strata `h = (rate_id, original_context_id)`, with 256 original source backgrounds each. For every stratum with at least one `new` record and at least one non-new record, estimate

- `p1_h = n(loss & new, h) / n(new, h)`.
- `p0_h = n(loss & non-new, h) / n(non-new, h)`.
- `w_h = n(new,h) / sum_h n(new,h)`, **only over support-eligible strata**.

The fixed primary contrast is `D = sum_h w_h * (p1_h - p0_h)` (percentage point difference in model cohort-loss frequency). Also show the two component standardized risks and the unadjusted G9 73.02% vs full-grid 66.56% for orientation, not as a causal estimate. The analogous continuous contrast is `sum_h w_h * (mean(logF effect | new,h) - mean(logF effect | non-new,h))`. This comparison is across different background structures *within the same synthetic rate and developmental context*. It is **not** a randomized effect of sign-generation status, which is a model output.

*Support and positivity rule:* report all 81 original stratum counts. If either group is absent in a stratum, do not estimate a within-stratum difference; explicitly report number of omitted strata, number/fraction of the original 782 new cases they contain, and 81-strata coverage. Do not silently call these zeros or extrapolate. If a source-cluster bootstrap draw has a stratum with a new case but no comparator, invalidate that draw and report bootstrap validity fraction; do not silently renormalize the risk contrast. Draws with no new observations in one stratum receive zero stratum weight, as defined. A bootstrap draw with zero newly generating records overall is invalid.

## Fixed sensitivity and heterogeneity

1. Comparator restricted to unchanged (compatibility 0), with the same stratum weights and independent positivity accounting.
2. Require >=5 original new and >=5 original comparator cases in a rate×context stratum. Report coverage and new-case fraction; recalculate standardized contrast within that subset. This is a support sensitivity, not a new primary.
3. Separate descriptive contrasts for each original developmental context 0/1/2 and each attack level 0.5/1.5/3.0; list the exact source and stratum denominators, and do not apply a multiple-testing claim.
4. Complete joint outcomes: 3 compatibility states (new, unchanged, lost) × 3 frog-cohort states (positive, negative, exact zero); preserve G9's original 571/782 source counts and G8's pooled means.

**Uncertainty:** 10,000 shared-source-cluster (256 backgrounds, all 27 rates and 3 contexts kept paired) bootstrap draws, seed `20261107`. Estimate the same standardized contrasts per resample using the complete source-level numerator/denominator matrices. Report pointwise 95% intervals and valid-replicate fraction. Do not resample the 20,736 source–rate records as independent ponds. An observed interval excluding zero is conditional on the synthetic structural sample and rates, not wild ecological evidence. No new confirmatory p-values.

## Decision rule and biological claim boundary

If the adjusted standardized difference is near zero or changes sign, **keep the 571/782 descriptive G9 finding but remove any implication that newly sign-generating configurations are disproportionately harmful beyond their underlying rate/developmental mix**. If positive and robust under the two comparator/support sensitivities, a limited model-conditional association may be added, without causal wording or field identification.

This result cannot prove that a natural continental association was generated by the food web. Retain the R1 observational correlation, all positive R2/P1/R4 findings, the G8 full-grid mean effect and G5/G7 non-support; explain that odonate/caudate SDM suitability and adult frog calling do not directly measure larval predation or cohort survival.