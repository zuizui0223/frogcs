# G8: 27-rate paired vegetation-function generality test (design freeze, 2026-11-07)

**Status: design fixed BEFORE running any G8 27-rate biological results.** This is a prospective *additional model experiment* motivated by earlier R2/R3/P1 results, **not** an externally registered field hypothesis. Previous R1–R4/P1/G4–G7 evidence and decisions remain immutable.

## Exact scientific question
Do the two vegetation functions (frog refuge from salamanders, and support for odonate feeding on frogs) increase idealized four-sign compatibility across a broad rate grid **when held-out structural and nuisance backgrounds are kept identical between all four interventions**, and does this correlate with better or worse frog-cohort abundance? A model-generated signature is NOT a demonstrated natural continental association.

## Fixed source and complete design
* Original 3,600 legal model catalog and biological 80-year seasonal/annual kernel from commit \`5e2f0a87c639df373fa2700b29403d2ab417a1cc\`. No source kernel modifications.
* Recreate the same 256 legal baseline backgrounds using original \`confirmatory_2x2_vegetation_predator_switch.original_draws()\`, seed \`20261123\`, chosen before G8.
* Same 256 baseline model IDs; per-source strength, refuge order and size-gate code held fixed **within and across** rate cells. No successful-only selection.
* **Exactly 27** rates: attack \`[0.5,1.5,3.0]\` × local recruitment \`[0.25,0.5,0.75]\` × conversion \`[2.0,4.0,8.0]\`, lexicographic order. Source original variable conversion is replaced by each grid value; the old context-matched value provides a reproducibility check only.
* For every source, rate, and each original developmental context 0/1/2, cross all four **legal catalog** plant states \`00,10,01,11\` by toggling only \`cover_SF\` and \`support_DF\`.
* Thus **256 × 27 × 3 × 4 = 82,944 genuine 80-year scenarios** and **663,552 eight-corner responses**. Three original developmental contexts, 8 corners V/S/D per scenario, years=80, window=20, dt=0.5, eps=1e-6. This is not a stochastic finite-N experiment and does not directly vary P1's separated duration/arrival factorial.

## Fixed endpoints and comparisons
* For each source × rate × context × arm calculate four sign compatibility \`OS<0 OV<0 SV>0 OSV>0\` on log model aquatic frog cohort. Preserve failures as well as successes.
* Paired primary contrast per rate: **mean(accepted_11 - accepted_00)** across all 256 backgrounds, with three contexts equally weighted. Also show 2x2 nonadditivity \`accepted_11-accepted_10-accepted_01+accepted_00\`; report all 27 rows, not just favourable rates.
* Secondary: same paired 11–00 contrast for mean log aquatic frog cohort; separately all three contexts; source-level cross-rate concordance between pattern compatibility and cohort benefit.
* Viability sensitivity: for each arm, report \`accepted AND min_F>=0.05 AND min_S>=0.05\` on the **full original denominator**, plus paired 11–00 difference. The 5% artificial floor is NOT an observed persistence threshold. Do not condition the sample on surviving plants or observed success.
* For each of the 27 rate cells and pooled equally across rates: 10,000 paired **source-background** bootstrap resamples (same source IDs in every timing, arm and rate comparison; seed 20261107) yield descriptive, pointwise 95% intervals. The 27 rates and 3 contexts are model treatments, NOT 27 independent natural populations.
* Preserve signed vs nonzero-compatible counts, non-additive effects, viability, mean log F, and denominators. Verify all 00/10/01/11 outputs are identical under V=0 (numerical negative control). Original PR161 rate-matched per-source outputs (attack=.5,rho=.75, each original conversion) must reproduce.

## Staged execution gate
1. Complete protocol + tested code are committed before any G8 27-rate outcomes.
2. Run a 4-year **method-only** check against original \`abc_pom_main3600.run_subset()\` for multiple rate cells. Four-year tests are **not scientific answers**.
3. Execute the complete 80-year design in 64 shards of four unselected source backgrounds (all IDs 0–255). A missing/failing shard is **no result**, never an exclusion. Save all shard receipts; aggregate only when all 64 pass.
4. Independent audit must reconstruct all 82,944 rows and 27 × 3 × 4 cells, paired source IDs, source parameter invariants, original matched replay, and the no-vegetation control before showing rates or scientific conclusions. No threshold retuning, rebinning, rate choice, or exclusion after results.

## Decision interpretation
* **Robust within-model rate generality** requires paired compatibility increases across a substantial predeclared fraction of rate cells, with the full table and artificial viability sensitivity given equal attention; do not relabel cells post hoc.
* The divergence between compatibility and frog welfare is assessed independently using paired cohort contrasts; a lower cohort does not mean a natural population declined.
* Prior G5/G7 held-out acoustic tests failed their fixed support gates. G8 cannot turn those null predictions into field confirmation. The unresolved adult-acoustic-to-larval-demographic link must remain explicit.
