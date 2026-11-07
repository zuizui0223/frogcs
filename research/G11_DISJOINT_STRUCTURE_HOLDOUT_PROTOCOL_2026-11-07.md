# G11 disjoint structural holdout for G8–G10: response-blind experiment specification (2026-11-07)

**Frozen before running any new heldout G11 biological simulation or reading heldout model outcomes.** This is a follow-on model experiment after G8–G10 have been observed, NOT external preregistration, independent field validation, or a random sample of natural wetlands.

## Core concern and universe

G8/G9/G10 reuse one set of 256 original food-web structural backgrounds. Therefore their structural uncertainty intervals do not prove transfer to unseen structures. The unchanged 3,600-model canonical original biological catalogue contains **720 legal baseline structures** with both focal vegetation flags off (\`cover_SF=0\`, \`support_DF=0\`) and \`behavior != risk_refuge\`; each baseline's same background features can map to all four legal 00,10,01,11 model IDs. This is the **eligible counterfactual subset**, not the entire 3,600-model prior and not the wild food-web distribution.

The original PR161/G8 set was fixed at seed 20261123 and selected 256 distinct baseline model IDs. **Exclude all 256 old baseline model IDs**, leaving 464 eligible unseen baseline structures. Using a distinct response-blind random draw \`np.random.default_rng(20261107).choice(sorted(unused_ids), size=256, replace=False)\`, select 256 of those 464. No old structural baseline may occur in the G11 holdout. The leftover 208 structures remain unused. Store selected IDs, source seed, and cryptographic hash before or with source simulation evidence. The original biological kernel is pinned to \`5e2f0a87c639df373fa2700b29403d2ab417a1cc\`.

For the 256 newly selected G11 source IDs \`0..255\`, independently draw nuisance variables with the **same synthetic discrete supports** as G8 (strength 0.5/1; refuge order S/equal/D; size gate 0/0.5), using the same holdout RNG stream after selection, before any biological outcomes. This is a *new independent nuisance draw*, not a clone of original G8 parameters.

## Complete crossed heldout experiment

Freeze *exactly the same* rates as G8: attack [0.5,1.5,3], recruitment [0.25,0.5,0.75] and maturation conversion [2,4,8] (27 full-factorial cells). Use original developmental contexts 0/1/2, original legal plant switches 00/10/01/11, the genuine original 80-year deterministic seasonal/annual kernel, window=20, dt=0.5, 8 source V/S/D corners, frozen four-sign rule OS− OV− SV+ OSV+ with threshold 1e−6. The intended total is **256×27×3×4 = 82,944 new true80 scenarios and 663,552 source corners**. Preserve all failures, nonfinite errors (fail closed), counts and zero effects. No successful-only model selection, no changed rates, and no retuning.

Run 64 shards of four disjoint source backgrounds. Four-year source checks are *only* methods checks. Audit all 64 original 80-year shards and source SHA receipts, original canonical model IDs, legal plant quartet, source/nuisance identity, all 27 rate cells, the V=0 negative control and all 8 original corners. Do not publish a scientific holdout conclusion unless complete 64/64 and source-audit PASS.

## Fixed predictions and comparisons

G11 holds out structural backgrounds from the preceding experiments. The **primary two *separate* transfer checks** are calculated over all 256 new source IDs equally, all 27 rates equally and all 3 original contexts equally:
1. Pooled paired 11−00 difference in four-sign model acceptance. Original G8 +2.705 percentage points [2.021,3.410]. Direction prediction: **positive**; a source-background bootstrap 95% interval fully above zero counts as model-family replication.
2. Pooled paired 11−00 mean log aquatic frog-cohort difference. Original G8 −0.04030 [−0.04918,−0.03109]. Direction prediction: **negative**; source-bootstrap 95% interval fully below zero counts as replication.

Both predictions must pass for the combined claim to be called independently *structure-replicated within this original eligible model family*. Failure of either cannot be repaired by selecting favorable attack rates or development contexts.

**Secondary, fixed but not necessary for joint pass:** independent holdout versions of original developmental context0/1/2 mean frog effects (G8 showed negative/negative/positive), 11−00 sign-acceptance and cohort effects by the 27 synthetic rate cells, four-sign-and-synthetic-5%-survival acceptance, nonadditive plant synergy, and the full G9 new-sign×frog-gain/loss joint count. G9's 571/782 (73.0%) is a descriptive value whose holdout proportion can vary; do not require replication of an arbitrary 73% point estimate or interpret it as field prevalence. G10's rate/context-standardized risk difference and context reversal are optional exploratory transfer checks only if each stratum meets the fixed positivity support; they cannot replace a failed primary result.

**Resampling and uncertainty:** 10,000 bootstraps of the newly selected 256 *source structures*, same sampled IDs held paired across all 27×3×4 contrasts, with seed 20261107. Use pointwise descriptive 95% intervals of synthetic model-source variability, not independent wild ecological confidence intervals. Compute G8 and G11 results with the same definitions; do not pool old and new structures until each sample is separately reported.

**Interpretation limits:** disjoint *structural* source sample only, still the same encoded mechanistic model class and highly artificial rate priors. Even perfect G11 replication does NOT establish the trophic pathway in any natural North American wetland; R1 adult acoustic calling and O/S environmental suitability are not larval predator densities or demographic counts. Preserve G5/G7 negative independent field prediction checks and G10's uncertain *adjusted* excess loss. No claim that 720 legal baseline models represent the entire 3,600 general model space.
