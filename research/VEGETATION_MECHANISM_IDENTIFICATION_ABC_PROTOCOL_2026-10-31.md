# Vegetation mechanism identification via staged model-native POM/ABC (2026-10-31)

## Why the completed ABC cannot answer vegetation's role

The PR #146 genuine 6,144 full 80-year simulations selected the structural axes **ontogenetic order (3) × handling budget (2) × behavioral refuge (2)** under a fixed vegetation pathway baseline: `cover_SF=1,cover_DF=0,cover_DS=0,cover_SD=0,support_DF=0,support_DS=0,emerge_survival=0,emerge_exposure=0,litter=1,edge_DS=1,edge_SD=1`. Consequently its 94.49% original-order class share is conditional on **F shelter from S and litter-dependent D-on-F attack shape being ON**. It is scientifically invalid to say those plant functions have been selected.

The **main** 2026-10-27 catalog is a different and wider conditional hypothesis space: `research/results/final_mechanism_20261027/catalog.csv`, 3,600 unique structures after 12,288 logical combinations and duplicate/canonical restrictions, with 4 vegetation-refuge paths, D/S feeding support, emergence timing and survival, D/S reciprocal predation edges, postmetamorph reversal, behavior and density-dependent functional response. `final_mechanism_common.catalog()` canonicalizes important impossible combinations (e.g. if `litter=1` it forces `cover_DF=0`, if `edge_DS=0` it forces `cover_DS=support_DS=0`). This means full main-to-ABC equivalence is **not yet claimed**.

## Biological axes, with causal scope

- `cover_SF` (frog aquatic F refuge from salamander S predation); plant protects F, potentially weakens S's direct negative contribution, distinct from S being net beneficial.
- `cover_DF` (frog F refuge from dragonfly nymph D predation); distinct direct pathway.
- `cover_DS` (S refuge from D predation); can *increase* the indirect S-on-F risk by preventing D's suppression of S.
- `cover_SD` (dragonfly D refuge from S predation; different recipient stage).
- `litter` (the synthetic switch between the original untreated D-on-F density dependence and the vegetation-dependent type-II/type-III-like functional response; main catalog disallows `litter=1` simultaneously with `cover_DF=1`).
- `support_DF,support_DS` feeding opportunity on vegetation; `survival,timing` emergence life-stage and phenology pathways.
- `edge_DS,edge_SD` directed predator links and `reverse` postmetamorph-to-emergence interaction, not plant roles, but **mediate** plant functions. `behavior` includes none/cue_SF/risk_refuge, and cues may be defined only with relevant refuge.
- These are **mechanistic assumptions** with qualitative literature analogues; site-scale vegetation proxy, actual in-pond aquatic plants, stage abundances, trophic attack rates and frog adult calling remain uncalibrated.

Source-backed main positive condition: catalog `1479` and simpler `1455` had conditional matches only in one out of 24 follow-up conditions; `1479` included `cover_SF=1,litter=1,edge_DS=1`, whereas `edge_SD` was removable. However **their three-way sign OSV remained negative, contrary to target +**; this is not proof that the plant path is necessary in the new 4-sign factorial.

## Stage 1: plant functions themselves (primary immediate executable goal)

Do not run a meaningless 3,600×256 grid without validating computational and model-inference constraints. First compare **12 explicitly legal main-catalog plant submodels**, not all 3,600, by crossing:

`cover_SF {0,1} × cover_DS {0,1} × litter {0,1} × cover_DF {0,1 only when litter=0}`.

Set `cover_SD=0,support_DF=0,support_DS=0,emerge_survival=0,emerge_exposure=0,edge_SD=1,edge_DS=1`. These are **12 legal combinations** (4 for litter=1; 8 for litter=0). The existing 2026-10-31 ABC baseline is exactly the `cover_SF=1,cover_DS=0,cover_DF=0,litter=1` candidate.

First exercise this vegetation subspace within the **original ontogenetic order × baseline handling** currently strongest by the completed 4-sign ABC; retain **risk_refuge off/on** and **postmetamorph reverse OFF/ON** as exactly paired nuisance states, equal weights. This is a **conditional staged investigation**, **not** a full 3,600-model ABC. The main model itself must remain unchanged.

64 shared *synthetic* biological rate vectors per model from the same frozen fixed support as prior 256-draw ABC are the **feasibility pilot**, with ON/OFF paired and true original **80-year seasonal+annual** simulation, 8 exact O×S×V corners per model. Use `log(F_B)` interaction signs as primary, raw `F_B` as secondary. Each of 12 vegetation mechanisms ×2 risk behavioral modes ×64 independent rate vectors ×2 reversed-edge nuisance states = **3,072 full long-horizon model instances** (24,576 treatment vertices). Time/effort support comes via four independently runnable `cover_SF×litter` job shards. Every shard is fully enumerated; no "best" winner is deleted.

The null/no-plant-role scenario `cover_SF=0,cover_DS=0,cover_DF=0,litter=0` is essential. The original frozen plant baseline must pass exact **same short recurrence, and full 80-year archive replay**, tolerances F_B and survival 1e-8; fail closed if not. Same 64 *rate vectors shared by all 12* vegetation models. The two reversal states are not independent biological rate draws.

**Primary scores**: binary four signs OS−,OV−,SV+,OSV+ with exact log(F_B) 2×2×2 contrasts and 1e−9 dead-zone; plant models with all four directions have per-model acceptance fractions, Wilson/paired-bootstrap uncertainty and conditional equal-prior shares (among only these 24 risk×vegetation types). **Never call these field posterior probabilities.** Report main effects on which signs are generated, e.g. 2×2 paired `cover_SF ON−OFF` and `litter ON−OFF` contrasts with identical rate draw and reverse state; only compare litter on/off **holding `cover_DF=0`** to respect main canonical constraints. Counts for `cover_DS` and `cover_DF` differences are similarly paired within legal ranges.

**ABC refinement gate**: This 64-draw sample is a pilot to identify missing states, computational feasibility and gross sensitivity, not a converged 256-draw posterior. Continue to 256 matched prior draws across all legal vegetation models and then test against stage/order/handling axes only after the baseline replay and complete pilot. If the new plant assumptions change 4-bit patterns significantly, the previous 12-class class shares are **not model-space-invariant**.

A real `cover_DF×litter` interaction is excluded by main canonical design, so **do not infer an independent estimate** of those two plant functions there. Emerging survival, phenology and plant feeding support still require separate controlled tiers. The old 3,600 comparison is a search catalog, not 3,600 independent prior-calibrated hypotheses. Retain the entire original POM/ABC results with model-space bounds plainly stated.

## Interpretation

Use ecological language anchored to role, not correlations: a V×S positive effect may arise if vegetation **reduces S's harmful predation** (less negative), **not** if S is beneficial. V may alter the prey D–S refuge balance and D attack functional response, potentially shifting net signs in opposite directions. The effect of habitat structure is **conditional on which life stage is exposed, whose attack is protected, and density/season context**. Do not equate positive SV with evidence of S-mediated mutualism.

This study is a **post-main search finite structural comparison**. A success under one synthetic prior or favorable edge mode establishes possible sign generation, not mechanism truth or plant vegetation causal effects in NAAMP.
