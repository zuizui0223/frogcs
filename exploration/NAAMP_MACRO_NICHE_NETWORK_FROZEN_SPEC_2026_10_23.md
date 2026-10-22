# Frozen-v1 exploratory NAAMP continental macro-network test: vegetation niche divergence vs frog co-calling

**Created 2026-10-23 before computing the *new* cross-dataset pair-versus-niche association.** Input outcomes and single-layer analyses were already published/explored within frogcs, hence this is **post-hoc research** not a preregistration or new data. JAE RC6 main/manuscript/SI remain frozen. No literature search or species experiments.

## Scientific question
**Across all NAAMP amphibian taxon pairs, do taxa with more different mapped emergent-wetland acoustic affinities show systematically more segregation in their same-stop calling than expected from the original taxon/stop-marginal-constrained, route-heldout NWI+PEM baseline?**

## Source and independent grain (no sample invention)
Inputs on this same branch inherited from the exploration lineage:
- `exploration/NAAMP_TAXON_SPECIFIC_AQUATIC_VEGETATION_RESULT_V0_1.json` — original within-survey PEM coefficient `primary_strong.pem_beta_per_10pp`, 25 historically eligibility-gated taxa out of 49. 6,236 eligible NWI-linked ten-stop surveys before taxon filters.
- `exploration/NAAMP_PLANT_CONDITIONED_FROG_PAIR_NETWORK_RESULT_V0_1.json` — same-stop residual pair `estimate.beta` based on exactly fixed species stop counts, exactly fixed stop species-richness, and route-heldout plant/wetland weights. Primary CI2–3 `modes.strong.all_pairs` (57 historically eligible pairs); secondary CI1–3 `modes.any.all_pairs` (127 historically fitted, likely fewer after intersecting plant slope eligible taxa). Underlying route-run sample 1,766/398 routes for CI2–3 and 3,659/478 for CI1–3. Original co-calling unit is pair overlap *within sequentially visited route stops*, not individual interaction/occupancy/simultaneity.

Allowed network pair inclusion **frozen** to existing record `status="fitted"`, `estimate.status="fitted"`, both taxon names in **previously eligible** plant slopes (same >=80 active runs, >=120 positive strong sites, >=25 routes, >=30 PEM-varying runs, all pre-existing). Never pick only BH-positive taxa or BH-supported pair edges. No custom ecological trait labels from external papers.

## Endpoint and hypotheses
Primary response Y = **100 × signed observed-minus-NWI+PEM-weighted-null pair overlap** (percentage points of ten stops, averaged by route-run). Predictor `x=abs(beta_PEM_taxon_i - beta_PEM_taxon_j)/0.1`; +1 x means their slope difference is +0.10 **absolute probability change per 10pp mapped PEM area fraction**. Biological directional hypothesis **negative**: greater niche difference -> more residual acoustic segregation. This is an *additional* species-pair ecological sorting component after the pre-existing weighted null accounts for first-order wetland affinities.

**Single primary inferential statistic:** OLS partial coefficient on x in strong-call 57-pair intersection after nuisance controls:
1. `log1p(pair.n_runs)` (sampling intensity),
2. `mean_null_pair_cov` (base expected overlap),
3. `same_genus` taxonomic nonindependence proxy,
4. `abs(log(active_runs_i/active_runs_j))` (taxon relative calling frequency difference).
All controls are fixed from original sources, **not** selected using the observed new macro effect. Missing/NaN numeric covariates fail closed. Standardize nuisance predictors over included pairs for numerical conditioning; x stays in declared units. Primary coefficient must be reported with sign/effect size even if p is high.

## Non-independent edge inferential gate
A naive edge-level P would pseudoreplicate taxon identities. Instead use **9,999 deterministic taxon-label permutations** of the 25 existing slopes over all existing eligible taxa, fixing the pair residual network, pair inclusion, route, overlap, taxa coverage and nuisance controls exactly. Refit OLS for each permutation. Report *one-sided negative* empirical p=(1+# beta_perm<=beta_observed)/(10,000) and two-sided |beta| p against zero. Permutation is **exploratory and relies on approximate node exchangeability**; habitat coefficients correlate with geographic range/lineage, so p is not a causal proof or exact design-randomization inference.

Report:
- histogram-summary of permuted beta, fitted coefficient, residualized R², pair counts, taxa count, coverage.
- Leave-one-taxon-out coefficient sign/count and range to diagnose node leverage; no automatic reselection.
- Species coefficient **within genus** permuted (3,999 draws) as a stringent taxon-clade sensitivity. If no within-genus variation, mark nonidentifiable; do not artificially count identical shuffles as support.
- Covariate-adjusted weighted WLS (`weight=min(n_routes,150)`) as **sensitivity**, not a second confirmatory endpoint.
- Geographic fold A and B pair residuals (`fold_deltas`) with identical X/pair membership for directional stability, no claim of independent geo replication because original plant slope estimates combined folds.
- Secondary CI1–3 using the **same strong-condition PEM niche coefficients**: explicitly a cross-endpoint ecological predictor, not a matching CI1–3 PEM regression. Report its OLS and node-permutation two-sided p **as secondary**, not independent replication.
- Optional exclude names containing `complex`, omitting composite taxon units, and recompute strong beta.
- Diagnostics contrast `mean_null_pair_cov` and actual `mean_observed_pair_cov`, verify `observed - null` equals the original `estimate.beta` up to numeric tolerance. Never infer plant causality or literal simultaneous calling from this ecological macro association.

Scientific outcome labels:
**"supported_nodal_exploratory_macro_pattern"** only if strong-call directional p<.05, a negative beta in *both* original geographic folds, ≥75% negative LOTO, and within-genus permutation also p<.05; otherwise **"nonconfirmatory_descriptive"**. Even a pass supports only conditional **acoustic site-allocation patterns** under the selected models, not frog competition, plant-caused interactions, trophic mediation or irreducible higher-order effects.

## Reproducibility
Frozen estimator is used without tuning radius (250m), period (2001–2015) or ecological response. Raw third-party data not redistributed. Source JSON immutable and script+result isolated from frozen RC6.
