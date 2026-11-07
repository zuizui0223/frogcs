# G15 — Does the ABC-selected acoustic signal exceed generic sign and rate/context-conditioned null sources?

**Original-source field predictive specificity completed and independently audited, 2026-11-07.** Scientific type: *post-hoc predictive diagnostic within the existing NAAMP acoustic data*, **not** a field-fitted Bayesian ABC posterior or independently identified natural predator pathway. All [G14](G14_ABC_POM_FIELD_ACOUSTIC_ENSEMBLE_VERIFIED_RESULT_2026-11-07.md) positive uniform-only and negative dual-background gates, [G13](G13_ABC_POM_CONDITIONAL_STRUCTURE_NULL_VERIFIED_RESULT_2026-11-07.md) source-catalogue structure selectivity, G8/G11 model structural replication, and G5/G7 field non-support remain intact.

## 1. Controlling source, preread specification and successful run

G15 fixed the [full protocol](G15_ABC_ACOUSTIC_SELECTION_SPECIFICITY_PROTOCOL_2026-11-07.md) **before computing new G15 null/field outcomes** (commit \`f3e1865\`), after G14 outcomes had already been seen. Original 20,000 genuine R2 80-year source proposals (eight SHA-verified gzip shards), 794 strict-four-log-sign accepted, and all original 81 exact attack×recruitment×conversion×developmental-context accepted counts are preserved.

Without using adult acoustic outcomes to select source cases, G15 constructed:
1. **ABC_794**: exact original G14 794-accepted source four-interaction vector.
2. **SIGN_ONLY**: a fixed **unit synthetic log-contrast** vector [OS,OV,SV,OSV] = [−1,−1,+1,+1]; converted to empirical interaction coefficients [−1.5,−1.5,+0.5,+1.0]. This tests whether specifying the **four signs alone** generates the same predictive shape.
3. **STRAT_NULL_000..198**: 199 new fixed source-label draws, seed **20261108**, each selecting exactly the original 794 accepted counts in the same 81 rate×context strata, but with the selected *model structures* exchangeable. Every null is a different synthetic source template, not a separately observed natural pond dataset.

The exact G14 geographic acoustic 5-fold recipe was applied to every template, with 4,248 distinct sites, 63,180 completed visits, 36,554 strong call events, 432 routes, 56 original geographic blocks and **both** uniform/target-group SDM backgrounds. Each template adds one nonnegative observation slope to the original flexible additive environmental model, ridge10. **201 fixed source templates × 2 background settings × 4,248 original sites = 1,707,696 complete heldout site predictions**, evaluated without target selection after seeing the results.

The source/time/field/ridge tests and four original geographic field-shard jobs all passed; independent aggregation recalculated each recorded site's binomial NLL from its predicted probability and observed k/n to **<1e−11** and verified every 56-block score. [G15 complete Actions run #42379659618](https://github.com/zuizui0223/frogcs/actions/runs/42379659618) SUCCESS. A previously too-strict optimizer numerical replay gate was transparently repaired; identical G14 original source coefficients and site/call/block source inputs were required, with per-site probability difference <1e−4 and mean NLL numerical difference <1e−6. Final G14 replay differences were **2.02×10⁻⁷ uniform**, **9.14×10⁻⁸ target-group**, negligible compared with the fixed G14 effects. No scientific outcome threshold or source null was changed.

## 2. Source-randomization comparison yields opposite ranking by SDM background

**Table G15a.** Geographically heldout binomial negative log likelihood **per completed acoustic visit** (smaller is better). Conditional-null empirical p = (1 + #null with NLL≤ABC NLL)/200, so p is a **source-selection permutation metric**, not a p-value for natural predation.

| Pre-frozen model/diagnostic | Uniform SDM | Target-group SDM |
|---|---:|---:|
| **Original ABC_794 template** | **0.67253269** | 0.67576987 |
| **SIGN_ONLY** generic sign template | 0.67266202 | 0.67618235 |
| **199 matched rate×context source nulls: mean** | 0.67296347 | **0.67559274** |
| 199 matched nulls: median | 0.67295129 | 0.67559316 |
| 199 matched nulls: 95% model-source range | 0.67281551–0.67315958 | 0.67553508–0.67563448 |
| **ABC-specific gain versus SIGN_ONLY** (NLL sign-only − ABC, positive = ABC wins) | **+0.00012934** | **+0.00041248** |
| **Rate/context nulls with lower or equal NLL than ABC** | **0/199** | **199/199** |
| Conditional-source upper-tail p (ABC best) | **0.005** | **1.000** |

**The core scientific finding:** the original 794-model ABC source ensemble's *empirical acoustic ranking relative to rate/context-matched artificial null ensembles reverses completely* across two commonly used SDM background models for **the same** NAAMP acoustic observations. Under uniform SDMs, ABC won against all 199 null source templates; under target-group SDMs, **all 199 nulls predicted the heldout calls better**. The fixed **both-background source-specificity gate FAILS**. No source-enriched causal natural predator hypothesis is validated.

G15 ABC_794 does outperform the arbitrarily scaled SIGN_ONLY template in both backgrounds. This shows the specific source shape is not observationally equivalent to the **particular declared unit-contrast sign-only** predictor. It does **not** prove that ABC is better than every other sign-compatible shape, and it does not overturn the matched-source null failure in target-group. SIGN_ONLY has no field or synthetic biological likelihood behind its arbitrary unit contrasts.

## 3. G14 predictive improvement is real within one background, not a general field mechanism result

Within the same fixed G15 scoring pipeline, ABC_794 predicts better than the original flexible environmental additive baseline by **+0.00115476 per visit** under uniform and **+0.00016295** under target-group. These replay G14's values (+0.00115496 and +0.00016286) to within 2.03×10⁻⁷ per visit. G14's 56-block bootstrap 95% interval excluded zero in uniform but **included zero under target-group**; G14 also failed to outperform unrestricted four O/S/V interactions robustly. The G15 source permutation p=0.005 for uniform is a *different conditional synthetic-source reference*, not a replacement for G14's original geographic-block bootstrap.

All source templates remain algebraically inside the original **unrestricted four O/S/V interaction feature span**. Stronger prediction over an additive null can arise through a one-dimensional regularization even if the source does not represent a natural predator process. The four-sign target was inspired by the original R1 association on the same NAAMP population, so geographic folds do not create a fully independent selection/validation population. Crucially, model larvae and adult frog calls remain different outcomes; environmental suitability is not field odonate/caudate density and 3-km vegetation is not submerged refuge.

## 4. What is now supportable and what is not

**Supported within the synthetic-to-acoustic comparison:** ABC-selected source shapes encode more than the arbitrary SIGN_ONLY comparison and can improve heldout adult acoustic NLL over additive shared-environment models under uniform background settings. This is not invariant to equally legitimate target-group SDM backgrounds; the specific accepted template can be *worse than all 199 rate/context-matched null models* in that alternative representation.

**Not supported:** a robust ABC-specific field predictor, a natural pond trophic mechanism's posterior identification, a calibration of attack/larval survival or adult calling from synthetic demographic output, or a claim that G14's modest improvement independently confirms G13's familywise structural-selection findings.

**Still supported:** R1 observed geographical association, G13 model-catalogue selection after rate/context conditioning, G8 and G11 independent-structure *synthetic* pattern/demography mismatch, P1 modelled developmental reversal. G5/G7 and G14 robust field predictive-gate failures remain.

## 5. Complete source outputs

- [G15 frozen design](G15_ABC_ACOUSTIC_SELECTION_SPECIFICITY_PROTOCOL_2026-11-07.md), original source selection \`199 null ×81 source strata\`, seed20261108.
- [Complete 199-null dual-background acoustic scores](results/g15_abc_acoustic_specificity_20261107/audited/G15_199_rate_context_null_template_field_scores.csv) and [ABC vs sign-only / all nulls summary](results/g15_abc_acoustic_specificity_20261107/audited/G15_G14_signonly_vs_ABC_null_comparison.csv).
- [All null/source 56-block loss summaries](results/g15_abc_acoustic_specificity_20261107/audited/G15_all_null_56block_losses.csv) and [all training-only five-fold source slopes](results/g15_abc_acoustic_specificity_20261107/audited/G15_all_null_fold_source_slopes.csv).
- [Frozen source coefficient catalog](results/g15_abc_acoustic_specificity_20261107/audited/G15_frozen_source_templates.csv) and [G15 SHA/source/field audited final receipt](results/g15_abc_acoustic_specificity_20261107/audited/G15_full_source_audit_receipt.json).
- [Source-code reproducer](scripts/g15_abc_selection_specificity_holdout.py) and [source-factorial sign control unit tests](scripts/test_g15_abc_selection_specificity_holdout.py); [G15 complete full-source G14 replay and field run](https://github.com/zuizui0223/frogcs/actions/runs/42379659618).
- Full **1,707,696 individual** original site-source predictions were audited on the GitHub Actions run from four original field shards. The branch retains aggregated per-source/per-block data and reproducible original code and source files; the detailed per-site G15 null predictions remain in the run's individual source-shard artifacts rather than bloating the Git branch.

**Decision: fixed G15 dual-SDM-background specificity gate = FAIL**, with meaningful opposite rankings across SDM backgrounds; **separate positive uniform-only source ranking is retained without calling it natural field mechanism identification**.
