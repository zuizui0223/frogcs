# G11 — disjoint original-structure holdout reproduces the pattern–population mismatch

**Audited scientific result, 7 November 2026.** Original first-run model execution [#42366300373](https://github.com/zuizui0223/frogcs/actions/runs/42366300373) completed all 64 biological shards successfully; it failed **only at the audit's secondary developmental-context aggregation**, where it erroneously attempted to read nonexistent `pooled_27/context=0,1,2` cells from the original G8 654-row summary. No biological simulations were changed or selected. The corrected audit instead computes those aggregates directly from the full G8 and G11 paired source-rate-context records. Reusing the **immutable original 64 80-year biological artifacts** without recomputation, independent re-audit [#42368396463](https://github.com/zuizui0223/frogcs/actions/runs/42368396463) **SUCCEEDED**. The complete independent receipt and SHA256 evidence are in [g11_final_independent_validation_receipt.json](results/g11_disjoint_holdout_20261107/audited/g11_final_independent_validation_receipt.json). G11 remains a **model-family structural holdout**, not an externally preregistered field test.

## Design and source audit

The original 3,600 canonical food-web catalogue contains **720 counterfactual-legal backgrounds** with `cover_SF=0`, `support_DF=0` and non-`risk_refuge` behavior, in which all four vegetation 00/10/01/11 variants map to original canonical IDs. The original G8 selected 256 unique such baseline structures. G11 excluded those **exact 256 IDs**, leaving **464 unused**, and selected a further **256 distinct, disjoint structures** with source seed 20261107, before observing heldout 80-year outcomes. The remaining 208 legal structures were not simulated. The 720 candidates form a restricted, encoded model family, **not** a representative sample of natural food webs or even all canonical catalogue structures.

Original biological kernel SHA `5e2f0a87c639df373fa2700b29403d2ab417a1cc`, 80 annual years, final 20-year response, half-day seasonal integration, original three developmental contexts, original 00/10/01/11 vegetation functions, all 27 full-factorial attack (0.5/1.5/3) × recruitment (0.25/0.5/0.75) × conversion (2/4/8) rates, with new nuisance draws from the previously fixed discrete priors. Exactly **82,944 original source scenarios**, **663,552 eight-corner environmental states**, **20,736 paired source×rate×context contrasts**, all **64/64 true-80-year shards**, original V=0 invariance control, within-source quartet and source SHA/selection checks passed. Independently reconstructed original four-sign contrasts agreed to max absolute discrepancy **1.34×10⁻¹⁵**. The response-blind source selection digest is `75a885adf1aff4c33819cc27869d2d49c57328537f970295538f24518182e718`.

## Both primary directional structural-replication gates passed

Equal-weight source, rate and context estimates; 10,000 source-cluster bootstraps with all rates/contexts paired, seed 20261107. The pointwise intervals summarize variation across synthetic source structures, *not* field or model-class uncertainty.

| Predetermined G11 11 minus 00 model contrast | Earlier G8, 256 backgrounds | Disjoint G11, new 256 backgrounds | Locked G11 direction |
|---|---:|---:|---|
| Four-sign compatibility, percentage points | **+2.705** [2.021, 3.410] | **+2.754** [2.083, 3.434] | **PASS** (95% lower >0) |
| Mean aquatic frog log cohort | **−0.04030** [−0.04918, −0.03109] | **−0.04125** [−0.05018, −0.03202] | **PASS** (95% upper <0) |

The old G8 and new G11 point estimates are close: compatibility difference **+0.0482 percentage points** and log-cohort difference **−0.000950**. These are descriptive comparisons of independent, artificial within-model source sets, not proof of equality or evidence that any natural wetland follows the same biology. The combined pre-fixed decision `joint_compatibility_population_mismatch` is **true**.

The auxiliary artificial-5%-survival-gated compatibility contrast also remains positive, **+2.831 percentage points [2.305, 3.385]** (G8 +2.619); pooled factorial (two-function nonadditivity) is **−0.608 points [−1.210,−0.019]** versus G8 −0.709 [−1.461,+0.010]. The historical fixed-rate positive synergy therefore must not be generalized to all 27 hypothetical rates.

## Original developmental contexts reproduce the demographic reversal

These are original *composite developmental settings*, not isolations of salamander arrival alone. We recalculated **27-rate pooled** effects separately for G8 and G11 from the complete 20,736 matched records per sample; the existing 654-row G8/G11 rate summary never contained pooled-rate, context-specific cells.

| Original context | G8 log-cohort effect [95%] | G11 disjoint log-cohort effect [95%] | G11 compatibility gain, percentage points [95%] |
|---|---:|---:|---:|
| 0 | −0.07227 [−0.08327,−0.06103] | **−0.07350 [−0.08444,−0.06239]** | **+4.181** [3.226,5.150] |
| 1 | −0.07384 [−0.08525,−0.06217] | **−0.07648 [−0.08784,−0.06485]** | **+4.181** [3.284,5.122] |
| 2 | +0.02521 [+0.01507,+0.03543] | **+0.02624 [+0.01526,+0.03726]** | −0.101 [−0.796,+0.550] |

Thus both independent structural source sets preserve **two negative and one positive developmental mean abundance effects**. The all-rate positive compatibility contrast is driven by contexts 0/1, not uniformly by context 2. G10's exploratory sign–loss standardization still applies to the original G8 background sample only; this test does not recalculate that adjusted comparison in G11.

## New four-sign generators and abundance: full denominator retained

G8's **571/782 (73.02%)** new-sign generation cases lost frog log-cohort abundance (original 20,736 matched pairs). In G11, adding both plant functions *newly* generated the four idealized signs in **835/20,736** paired cases; **612/835 (73.29%)** nevertheless lost frogs, and **223/835 (26.71%)** did not lose them. Source-bootstrap descriptive 95% for the 73.29% loss fraction: **[66.43%,79.69%]**, 10,000/10,000 valid bootstrap draws. Importantly, these are conditional frequencies among new-sign cases; neither old nor new percentages alone establish *excess* losses relative to alternative model structures at comparable synthetic rates and developmental contexts. G10 originally found overall standardized excess loss uncertain (−4.93 pp [−11.28,+0.83]); do not overwrite that negative finding with the raw G11 loss percentage.

## Exact 27-rate-cell sensitivity — all cells (no success filter)

Compatibility in **11/27** cells was positive, **11/27** negative and **5/27** zero; only **10** cells had a pointwise bootstrap interval fully positive, and **3** fully negative. Mean frog log-cohort change was negative in **27/27** rate cells; **26/27** pointwise intervals lay wholly below zero (one included zero). Aggregate of the nine rate cells within each hypothetical attack value: at attack 0.5 compatibility **+8.796 points** and log-cohort **−0.05563**; attack 1.5 compatibility **+0.130 points** and log-cohort **−0.03723**; attack 3 compatibility **−0.666 points** and log-cohort **−0.03088**. These are descriptive subgroups; the heldout confirmatory inference is the **pooled two-gate decision**, not 27 independent significance tests.

Each row below is a **modelled** rate cell pooled equally across 256 new structures and three original contexts; source-bootstrap 95% intervals are pointwise, unadjusted for the 27 comparisons.

| Attack | Recruitment | Conversion | 11−00 compatibility, percentage points [95%] | 11−00 frog log cohort [95%] |
|---:|---:|---:|---:|---:|
| 0.5 | 0.25 | 2.0 | 0.13 [0.00, 0.39] | -0.0109 [-0.0120, -0.0099] |
| 0.5 | 0.25 | 4.0 | 4.82 [2.86, 6.90] | -0.0215 [-0.0239, -0.0191] |
| 0.5 | 0.25 | 8.0 | 10.42 [7.55, 13.41] | -0.0422 [-0.0485, -0.0359] |
| 0.5 | 0.50 | 2.0 | 7.68 [5.34, 10.29] | -0.0188 [-0.0214, -0.0163] |
| 0.5 | 0.50 | 4.0 | 16.02 [12.63, 19.53] | -0.0356 [-0.0428, -0.0284] |
| 0.5 | 0.50 | 8.0 | 8.20 [5.60, 10.94] | -0.1040 [-0.1262, -0.0824] |
| 0.5 | 0.75 | 2.0 | 17.71 [14.19, 21.35] | -0.0093 [-0.0145, -0.0041] |
| 0.5 | 0.75 | 4.0 | 9.38 [6.51, 12.24] | -0.0374 [-0.0555, -0.0198] |
| 0.5 | 0.75 | 8.0 | 4.82 [2.21, 7.68] | -0.2208 [-0.2708, -0.1701] |
| 1.5 | 0.25 | 2.0 | 0.00 [0.00, 0.00] | -0.0119 [-0.0131, -0.0107] |
| 1.5 | 0.25 | 4.0 | 0.00 [0.00, 0.00] | -0.0195 [-0.0222, -0.0167] |
| 1.5 | 0.25 | 8.0 | 0.78 [0.13, 1.56] | -0.0375 [-0.0454, -0.0294] |
| 1.5 | 0.50 | 2.0 | 0.00 [0.00, 0.00] | -0.0206 [-0.0241, -0.0170] |
| 1.5 | 0.50 | 4.0 | -0.65 [-1.69, 0.26] | -0.0388 [-0.0494, -0.0279] |
| 1.5 | 0.50 | 8.0 | -0.78 [-2.60, 1.04] | -0.0622 [-0.0842, -0.0398] |
| 1.5 | 0.75 | 2.0 | 0.00 [-1.30, 1.30] | -0.0103 [-0.0209, 0.0005] |
| 1.5 | 0.75 | 4.0 | 2.21 [0.13, 4.43] | -0.0674 [-0.0965, -0.0369] |
| 1.5 | 0.75 | 8.0 | -0.39 [-2.60, 1.82] | -0.0668 [-0.1018, -0.0316] |
| 3.0 | 0.25 | 2.0 | 0.00 [0.00, 0.00] | -0.0082 [-0.0094, -0.0071] |
| 3.0 | 0.25 | 4.0 | -0.39 [-1.04, 0.13] | -0.0143 [-0.0172, -0.0115] |
| 3.0 | 0.25 | 8.0 | -0.52 [-1.04, -0.13] | -0.0312 [-0.0379, -0.0243] |
| 3.0 | 0.50 | 2.0 | -1.43 [-2.47, -0.52] | -0.0144 [-0.0180, -0.0107] |
| 3.0 | 0.50 | 4.0 | -0.91 [-1.82, -0.13] | -0.0378 [-0.0469, -0.0284] |
| 3.0 | 0.50 | 8.0 | -0.52 [-1.43, 0.39] | -0.0412 [-0.0529, -0.0301] |
| 3.0 | 0.75 | 2.0 | -0.65 [-1.82, 0.52] | -0.0190 [-0.0298, -0.0079] |
| 3.0 | 0.75 | 4.0 | -1.17 [-3.78, 1.43] | -0.0592 [-0.0778, -0.0411] |
| 3.0 | 0.75 | 8.0 | -0.39 [-1.43, 0.65] | -0.0524 [-0.0661, -0.0395] |

The [full 27-cell machine-readable table](results/g11_disjoint_holdout_20261107/audited/g11_all_27_rate_paired_effects.csv), [654 all-rate/context/source-bootstrap estimates](results/g11_disjoint_holdout_20261107/audited/g11_all_27_rate_source_bootstrap_estimates.csv), [G8/G11 original-context comparisons](results/g11_disjoint_holdout_20261107/audited/g11_developmental_context_vs_g8.csv), [all 82,944 original source outcomes](results/g11_disjoint_holdout_20261107/audited/g11_disjoint_full_82944_source_scenarios.csv.gz), [all 20,736 paired contrasts](results/g11_disjoint_holdout_20261107/audited/g11_disjoint_20736_matched_source_rate_context.csv.gz), [frozen source structures](results/g11_disjoint_holdout_20261107/audited/g11_frozen_structure_selection.json) and [full SHA/corner audit](results/g11_disjoint_holdout_20261107/audited/g11_final_independent_validation_receipt.json) are versioned in this stacked Draft PR.

## Interpretation, preserved constraints and publication scope

**Positive:** G8's model-family result transfers to **unseen structures from the same legal original food-web catalogue**: adding both vegetation functions modestly increases generation of idealized four-sign conditional associations **while reducing average frog-cohort abundance**, despite a developmental regime in which cohorts benefit. The pattern-generation/demography decoupling and three-context sign reversal recur without sharing old baseline structural IDs or reselecting rates.

**Negative/limits:** the gain is **not** present in every rate or developmental context; full-grid factorial synergy is not robustly positive, and the G11 pooled negative cohort mean does **not** mean every developmental setting or individual structure loses frogs. The 73% of newly sign-generating cases that lose abundance is not a proven relative excess harm. The field mechanism is **not identified**: observed R1 data concern adult acoustic calling and O/S suitability instead of natural larval predator abundance, attack rates, frog recruitment or habitat-mediated trophic pathways. G5/G7 original heldout field-prediction limitations remain. G11 is not evidence of wild model parameter values or spatial/temporal transfer across ponds. An ecological experiment measuring trophic attack, recruitment and the larval-to-calling bridge would be needed for causal inference.

**Provenance:** response-blind protocol [G11_DISJOINT_STRUCTURE_HOLDOUT_PROTOCOL_2026-11-07.md](G11_DISJOINT_STRUCTURE_HOLDOUT_PROTOCOL_2026-11-07.md), unchanged biological generation [run_g11_disjoint_structure_27rate.py](scripts/run_g11_disjoint_structure_27rate.py), independent corrected 64-shard biological/corner audit [audit_g11_disjoint_structure_27rate.py](scripts/audit_g11_disjoint_structure_27rate.py). First run failed the **reporting-only context aggregation** after all 64 biological shards passed; successful immutable-shard audit [#42368396463](https://github.com/zuizui0223/frogcs/actions/runs/42368396463) closes that failure. No field observations, source kernels, rate definitions, old G8 outputs or natural trophic claims were altered.
