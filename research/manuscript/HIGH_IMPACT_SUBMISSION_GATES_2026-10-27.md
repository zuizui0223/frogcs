> 最新更新：[2026-10-29追加検証とゲート判定](NEE_FOLLOWUP_AND_GATE_UPDATE_2026-10-29.md)、[統合作業稿](working_20261029/MANUSCRIPT_JA.md)。以下の方針・履歴を保持し、到達点は最新更新で判断する。

# High-impact single-paper strategy: frogcs macroecology × stage-structured mechanism

**Decision date: 2026-10-27 (JST). Editorial roadmap only; no empirical result added, no manuscript submitted.** Current source of truth: `main` at source commit `a817d41425902b1778f4c3c26059eebb112146f2`. Current paper: [two-part working manuscript](TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md) and [final conditional mechanism comparison](FINAL_MECHANISM_COMPARISON_2026-10-27.md). RC6 remains a historical motivating acoustic analysis, not the headline result, separate publication, or supposed independent replication.

## Objective and target ladder

Aim to develop **one** manuscript connecting observed macroecological context and quantitative process theory, without splitting the simulation into a second paper.

**Stretch target 1 — Nature Ecology & Evolution (Article)**: journal officially covers macroecology, community ecology and ecological theory. Article: 3,500 main-text words excluding Methods, abstract 200 words, ≤6 main display items. The paper needs a field-impacting **generalizable discovery**, not one large survey association plus a flexible illustrative model.

**Competitive high-tier target 2 — Ecology Letters (Letter)**: stated preference for novel ecology that tests precise hypotheses; purely descriptive results discouraged. Limit 5,000 main-text words and six display items. Needs a concise and discriminating observation-to-theory advance, ideally replicated or strongly falsifiable.

**Alternative upper-tier — PNAS or Nature Communications**, if a principle and an independent data test are demonstrated; PNAS requires broad scientific significance, Nature Communications a strong advance of significance to ecological specialists. Do not presume a relative acceptance likelihood. Nature/Science would require a still broader, independently supported conceptual shift than current source evidence.

Official scope/format:
- NEE: https://www.nature.com/natecolevol/aims and https://www.nature.com/natecolevol/content
- Ecology Letters: https://onlinelibrary.wiley.com/page/journal/14610248/homepage/ForAuthors.html
- Nature Communications: https://www.nature.com/ncomms/aims
- PNAS: https://www.pnas.org/ or https://doi.org/10.1073/pnas

## General principle worth trying to demonstrate

**Testable central question:** When one guild appears negatively associated with breeding activity, **which parts of the association remain after conditioning on a third guild and vegetation, and under what validated demographic and observational conditions could that contextual dependence emerge?**

A hypothetical broad statement (NOT a current finding): **"The apparent sign or strength of an ecological two-guild association is context dependent because a third guild and habitat can redistribute direct and indirect mortality effects."** Related ecology has already been studied (see [primary novelty audit](NOVELTY_MECHANISM_PRIMARY_AUDIT_2026-10-26.md)); new originality would require **identifying a general quantitative boundary or diagnostic prediction**, not merely illustrating a third predator or a regression interaction.

Keep macro result in front: 4,248 acoustic sites, site strong-call fraction, model-derived Odonata suitability. Whole-region rho −0.095 (uniform) and −0.086 (target-group). High-versus-low pond-breeding Caudata strata change Odonata–calling rho by −0.385 (95% CI −0.509,−0.240; uniform) and −0.179 (−0.328,−0.029; target-group). Vegetation at 3 km has two-way sign differences; observed macro three-way uniform +0.037 (+0.008,+0.068), but target-group interval crosses zero and within-route attenuates. Preceding-year satellite *water detection*, not pond hydroperiod, −1.481 percentage points (−2.601,−0.294) for water-positive 3 km pixels in 3,907 fixed pairs. Past recorded acoustic use +27.68 percentage points in 4,040 fixed pairs.

**Crucial current negative fact:** fixed finite model catalogue of 3,600 stage-network structures; 20 candidates ×24 common nuisance blocks; selected candidate 1479 only jointly matched three directions in **one block**. Reduced model 1455 also works only there. More critically, the modeled macro-style **three-way term was negative** (~−0.0482 at coarse 3-level grid; −0.0104 at 21 levels) while the main uniform macro estimate is **positive** (+0.037). The macro variables are Odonata/Caudata environmental suitability + landscape vegetation + adult calling detection; simulated variables are synthetic supply densities, predator hazard, juvenile survival/recruitment and plant refuge multiplier. These are NOT identical observation scales. The current model is not a field-identified explanation.

## Three decisive upgrading tasks, fixed to avoid post-result tuning

### G1. Make the empirical association a **discriminating source-verified ecological pattern**

- Re-estimate at predeclared NAAMP geographic subsets by state/ecoregion/route (not outcome-selected), both previously fixed SDM backgrounds, same species candidate cohort and explicit survey effort/season covariates.
- Separate **between-region** and **within-route** components, since existing high/low Caudata contrasts are most prominent regionwide. Test shared climatic/wetland suitability and geographic autocorrelation baselines, include source observation/detection bias and multiplicity. The question is whether the third-guild association carries ecological information not reducible to co-suitability on broad shared environmental gradients.
- Independently screen an original dataset with *actual* frog call/occurrence, odonate and caudate surveys, wetlands plus plant/hydroperiod measurements; the source must have a real common pond/time key. Existing NPS, Hungary, INBO cannot **be assumed** to have all three guilds at identical observation units. No pseudo-absence from opportunistic GBIF.

**Go/no-go:** A higher-tier macro claim requires a credible conditional contrast with independent geographic/external transfer OR an exceptionally clear spatially stratified result with quantified shared-habitat alternatives. A strong nationwide point estimate that disappears under matched within-route/environment controls cannot be promoted into an ecological mechanism.

### G2. Build the observation-to-process bridge **before adjusting the simulator**

Use source-native observation processes as separate layers rather than silently mapping them:
- source physical pond species/stage-specific prey and predator density and hydroperiod → process simulation parameters; modeled SDM suitability **does not equal** those densities;
- model adult frog abundance/activity → acoustic survey call index/count through explicit detectability, season, weather, site and species. Larval mortality in spring cannot cause calls of the *same adult cohort* earlier that season without maturation lag.
- test **all three** observed two-way signs, the macro **positive three-way term**, and the background/within-route sensitivities, each on a matched statistical scale with uncertainty. Use held-out data for calibration and testing. A predictor outcome from synthetic 18-cell supply grids **cannot be presented as a fitted macro coefficient** merely because the design matrices share terms.

**Go/no-go:** A model that reproduces two-way signs but not the original three-way sign or realistic observation dependence is a **hypothesis generator**, not an explanation. The existing 1/24 successes, after catalogue search, cannot be interpreted as empirical support or general frequency.

### G3. Establish a new ecological principle, not a new catalogue winner

Compare a small, predeclared **minimal mechanism family** (shared-environment-only, direct trophic edges, third-guild predation and indirect effects, vegetation refuge/functional-response changes). Freeze criteria and plausible parameter ranges from measurements and independently reviewed primary sources; publish negative candidate and sign failures, do not mine increasingly elaborate synthetic combinations until the macro coefficients are matched. Demonstrate a **new falsifiable prediction** that the alternatives disagree about, for example **which predator cue/density response changes with vegetation and stage size given the same true wetland**, and verify that prediction in a genuine external experimental/pond dataset.

**Go/no-go:** only then can a general principle justify a first-shot NEE or broader PNAS/Nature Communications claim. If G1/G2 fail, a rigorously scoped empirical macroecology + mechanistic *constraints* Letter may still be suitable for Ecology Letters, but cannot claim the field mechanism is identified.

## Recommended high-tier four-figure narrative

1. **Measured macro effect and third-guild context**: multi-guild 4,248 acoustic-site survey plus confounding and between-/within-route strata; source scales stated.
2. **Habitat and environment boundaries**: vegetation background/1km–3km, water-detection frequency vs area and strict acoustic history; numerical/source heterogeneity visible.
3. **Process model in matched observation space**: explicit acoustic observation model, survival vs guild density vs suitability, same effect definitions as field; show failures and successes, not just lucky parameter cell.
4. **Independent discriminating test / general principle**: held-out geography or new pond-level source measurements, and the predicted contrast among direct predation/shared habitat/refuge. If no independent endpoint is verified, this item stays **UNACHIEVED** rather than filled by more simulations.

RC6 within-taxon spatial concentration goes in the **Introduction as historical motivation, not Results Figure 1**; its original frozen release refs and reproducibility payload remain unchanged.

## Current decision

**2026-10-29 evidence update:** [Public-data calibration and independent pond audit](PUBLIC_DATA_GAP_CLOSURE_2026-10-29.md) and [fixed-model compatibility](MODEL_MACRO_COMPATIBILITY_UPDATE_2026-10-29.md) supersede the requirement to force a positive three-way sign in a revised analysis. The original positive estimate remains recorded above. The fully adjusted estimate has an interval including zero and a small negative synthetic coefficient, so the updated target is the full uncertain coefficient vector on calibrated observation scales, not the old sign alone. This reduces one apparent contradiction but does not establish model fit; G2/G3 remain unmet. No simulator retuning was performed.

**Journal target for research design:** Nature Ecology & Evolution Article (high-risk stretch). **Next alternative:** Ecology Letters Letter, depending on actual evidence outcome. PNAS/Nature Communications remain context-dependent alternatives. **NOT currently submission-ready at any of these tiers.**

Do not edit pinned original `paper/`, `submission/`, `provenance/`, `research/reproducibility/`, `research/results/final_mechanism_20261027/` or current main 2026-10-27 empirical receipts when updating the editorial target. This note changes **research ambition and explicit evidence gates only**, not science or past commitments.
