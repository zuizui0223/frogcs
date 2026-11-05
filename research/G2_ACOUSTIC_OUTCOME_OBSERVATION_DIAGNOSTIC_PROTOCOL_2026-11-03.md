# G2 acoustic-outcome measurement decomposition: source-frozen observational check

2026-11-03. **Frozen before viewing the new acoustic decomposition result.** This is a *measurement and response-definition diagnostic* for the already observed R1 third-guild correlation. It cannot estimate the demographic link from larval frog F_B to adult male calling or identify larval predators.

## Original verified sources, no new measurements

- Source `main` immutable commit `5e2f0a87c639df373fa2700b29403d2ab417a1cc`:
  - `research/results/naamp_site_use_associations_20261026/primary_site_characteristics.csv.gz` (4,248 source acoustic monitoring sites; prefiltered at ≥6 repeated surveys, ≥3 years; site-level strong and any calling fractions).
  - `research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz` (original completed-survey strong/any visit indicators; use only original source sites and `timeout==0`).
  - `research/results/naamp_odonata_caudata_associations_20261026/high_low_contrasts.csv` (the exact R1 frozen strong-calling high-minus-low caudate suitability contrast and route-cluster bootstrap intervals).
  - Original unchanged `research/scripts/naamp_site_use_associations.rank_association` and `research/scripts/naamp_odonata_caudata_associations.tertiles`; no new SDM fitting or spatial site selection.
- Same original 4,248 sites, 28 modelled potential biotic guild taxa, two original SDM-background methods `uniform` and `target_group`, and the original `pond_breeding_Caudata` grouping. O=mean odonate environmental suitability, S=mean pond-breeding-cauda environmental suitability. These are NOT measured predator densities.
- Exact R1 source original geographic tertiles: predictor-only full-cohort S suitability quantiles at 1/3 and 2/3, with original `searchsorted(side='left')`. No re-stratification on outcomes or observed calling.

## Predeclared observed outcomes

For each original physical acoustic site and all completed surveys, confirm exact strong/any counts (strong ≤ any and both binary), no duplicate site/run, and that rebuilt site-level strong/any survey ratios match the original source frozen values.

1. **Strong activity on all completed visits**: `P(strong)=N_strong/N_completed` — exactly the preexisting R1 response. Fail closed unless both full-cohort high-minus-low association points and **original 1,000-route-bootstrap intervals** match immutable R1 source to numerical tolerance across both SDM backgrounds and both whole-area/within-route scopes.
2. **Any recorded calling on all completed visits**: `P(any)=N_any/N_completed` — ordinary acoustic detection/calling, not true site occupancy.
3. **Strong conditional on any recorded calling**: `P(strong|any)=N_strong/N_any` for original sites with `N_any>0`; explicitly report changed site and route denominator by original S suitability tertile. Sites without recorded calling are excluded *only* for this conditional diagnostic. Conditioning on detections changes the estimand and can introduce selection/collider effects. It does not estimate conditional frog population abundance.

For each of these three *observable acoustic definitions*, use the **same original rank-association method**, whole area and within route, high/middle/low S-suitability classes, and 1,000 original route-cluster bootstrap draws (`seed=20261027`) from the same original route-block index. Do **not** treat the SDM backgrounds as independent study replications.

**Paired descriptive contrast** (main new comparison): the difference between R1 high-minus-low `strong` contrast and the corresponding `any` contrast on the same 4,248 sites, resampling exactly the *same* original route indices on every bootstrap. Also report the distinct conditional-strong contrast, but do not assume a linear identity among Spearman correlations or an additive biological decomposition of R1.

## Interpretation gate

- The descriptive R1 negative contrast in strong calling remains positive evidence about **adult acoustic behavior at the observed monitoring sites**, whether or not the `any` or `strong|any` patterns look similar.
- If the conditional-strong acoustic contrast differs from the any-call contrast, describe it as **outcome-definition/recording sensitivity**, not larval survival or realized frog breeding success.
- Do not relabel `any` detection as true population occupancy; the original NAAMP observational source does not contain a calibrated repeated-detection model, larval S/D predator densities, F larval abundance, measured pond-level vegetation refuge, reproductive output or a field-calibrated F_B→adult call observation function.
- The older [PR #145 negative out-of-block mechanism-acoustic bridge](https://github.com/zuizui0223/frogcs/pull/145) and the newer [PR #160 G1 no background-robust incremental O×S prediction](https://github.com/zuizui0223/frogcs/pull/160) are independently retained. This additional diagnostic cannot reverse them simply by choosing an acoustically favorable response type.
- This is a **same original 4,248-site observational cohort**, not independently collected out-of-sample data. The 1,000 route-bootstrap ranges are conditional on fixed original SDM suitability, do not include SDM model fitting uncertainty, and do not correct multiple comparisons.

## Required reproducible deliverables

- Original-source strong/any visit-account audit with original SHA and exact original R1 strong statistic replay.
- Complete 2 backgrounds × 2 geographic scopes × 3 outcomes × 3 S tertiles = **36 correlation rows** and **12 high-minus-low contrasts**, plus **4 paired strong-minus-any contrast rows** and source site/route denominators.
- One figure juxtaposing strong vs any vs conditional strong under two original SDM backgrounds, with original route-cluster uncertainty.
- Manuscript/SI updates: scientific strongest statements from actual observed results and explicit remaining larval-to-adult observation-link non-identifiability. `main` and PR #160/161/162 biological source results untouched; no journal submission.

