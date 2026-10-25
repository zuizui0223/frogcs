# INBO frogcs Stage G1 — same-original-site cross-stage forward association (outcome-blind contract)

Locked 2026-10-26, **after source-blind G0 (96 exact cross-protocol locations; 247 location-years) and G0.1 (Hyla arborea: 245 species×location×year opportunities, 93 sites; Pelobates fuscus: only 2 opportunities across 2 sites)**, **before reading any chorus/larva present/absent value or count**. Observed results from this secondary newly discovered source will be **exploratory and independent of NAAMP**. Original dataset URLs and SHA256 are locked in `research/scripts/inbo_stage_taxon_g0.py`.

### 1. Primary analysis taxon (frozen by coverage, not by effect direction)

- **One analyzable focal taxon: `Hyla arborea`.** `Pelobates fuscus` with only two eligible site-years is **mandatory non-estimable**, even if those two happen to be positive. All other species excluded from this contrast.
- Target = **recorded larval occurrenceStatus `present` vs `absent` at the FIRST subsequent explicitly labeled `larva` census** of Hyla arborea at source-exact `locationID × breeding year`.
- Exposure = **any `Hyla arborea` adult chorus occurrenceStatus `present` at one or more adult choir surveys strictly BEFORE the first eligible larval census**; `absent` only if at least one source Hyla adult choir row explicitly scored `absent`. Unmonitored/blank/ambiguous/unknown statuses are NA, never zero.
- Do **not** treat an unannotated taxon at an event, missing larval stages, unknown count or lack of date as absence. `individualCount` is a source QC consistency check only, not a survival denominator. Exclude same-day events because within-day ordering is not verified.
- Validate cross-dataset `locationID` AND independently compare site `locality` string with a one-to-one mapping; fail closed if ambiguous sites are involved, withhold raw IDs in result.
- Required sample: at least 25 independent exact-site-year complete pairs, 15 distinct original sites, and >=10 recorded `present` and >=10 recorded `absent` larval outcomes. Also exposure prior call has both levels and >=10 `0` and >=10 `1` when aggregating complete pair opportunities. If not, **non-estimable with no alternate species, threshold or year search**.

### 2. Two model comparison families, matching the same site×year rows

- M0 habitat/time/detection baseline: year and census day-of-year (numeric), delay from previous adult survey to first larval census, number of adult choir target surveys prior to first larval survey, and **only actually recorded** concurrent `permanent water column` class at the larval event if measurement coverage is reliable. `hydroperiod` is a coarse covariate, not verified dryout/re-wetting; if coverage or coding is inconsistent, omit the entire field from M0 and document why **before inspecting outcome**. No site ID dummy in site-held-out forecast, because new physical sites were not trained; use location grouping in validation instead.
- M1 = precisely M0 + the **one binary prior adult chorus recorded occurrence signal**. No post-census adult calling records, no egg-count proxy, no predator identity.
- Primary validation: deterministic 5-fold `GroupKFold` on all original locationIDs (all years from each site in one fold), `LogisticRegression(C=1.0, max_iter=1000)` on standardized numeric features; preserve folds and eligible rows across M0/M1. Secondary validation: train on years <=2023; evaluate 2024–2025 complete pairs only if both classes and enough sites, otherwise non-estimable temporal generality.
- Scores: Brier loss and log loss (negative gain means M1 worsens). Report coverage, both exposure/outcome prevalences, held-out predicted probabilities (not raw IDs), site-bootstrap (2,000 draws on site-level out-of-fold loss differences) as uncertainty **conditional on training fits**; no p-hacking if gain fails.
- **Do not interpret positive M1 score improvement as stage-specific predation**: independent fish, size, tadpole cohort survival, true wet/dry reset, dispersal and prey mortality data absent in these records. A within-year acoustic-to-larva link is about reproductive stage reporting and detection.

### 3. Release decision

- If no true surveyed-zero records for larva `lifeStage`, or fewer than 10 zeros/positives, mark primary ***not estimable*** rather than constructing false absences from another stage.
- If site-block held-out M1 improves: **support for conditional same-species acoustic-to-larval reporting**, not H1B prey egg-survival or why NAAMP has C residual.
- If M1 is equal or worse: negative finding on that proxy transfer; preserves RC6 acoustic spatial evidence and leads to habitat/stage data acquisition.
- No claim of causal rainfall, individual reproductive output, cohort survival, predator attack, or frog resource-driven niche trade-off. Report complete result and both adverse/positive effects.
