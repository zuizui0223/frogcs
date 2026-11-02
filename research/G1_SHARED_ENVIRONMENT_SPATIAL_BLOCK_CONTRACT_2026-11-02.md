# G1 fixed contract: evaluate third-guild conditioning against environmental-only alternative, 2026-11-02

## Status and provenance

New prospective **source-frozen, within-cohort** prediction test for Draft PR #160. Does not discard prior positive 4,248-site macro association, the main 3,600 mechanism comparison, the PR #160 synthetic source outcome or the negative PR #145 original acoustic-bridge assessment. No new field predator observations. This G1 test is a **statistical shared-environment and spatial-confounding stress**, not a causal interaction experiment.

### Frozen real data and external matching

- Input observational source: exact main SHA `5e2f0a87c639df373fa2700b29403d2ab417a1cc`, `research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz` (4,248 distinct acoustic sites) and `research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz` (63,180 completed NAAMP surveys at these 4,248 source sites).
- Source field processing: exact source PR #145 head SHA `a5ddc281ba17017a52b404a5725327f6e829824f`, the original code `research/scripts/acoustic_mechanism_cv.py`. Reuse its `prepare_sites`, `assign_spatial_folds`, `base_matrix`, `zrank`, `train_predict` and `log_score` without modifying their source meaning.
- Eligibility: same original 28 SDM-modelled potential guild taxa, 15 frog + 7 caudate + 6 odonate, two (non-independent) distribution-model backgrounds `uniform`, `target_group`. O=Odonata mean potential niche suitability, S=pond-breeding Caudata mean potential niche suitability, V=EarthEnv 3-km flooded vegetation>0. Predictor location is not measured pond predator abundance or larval habitat structure.
- Response: actual strong adult frog calling events (`strong=1`, survey visit CallingIndex≥2 for at least one frog species) among completed surveys, aggregated into original site `k/n` counts. Not larval survival, reproduction or movement.
- Frozen spatial partition: PR #145's five outcome-blind folds composed of whole route-centroid **2-degree** spatial blocks (~56 blocks), no route split across training/test. Ridge penalty **10** (fixed, no tuning) and binomial site-count likelihood, scored as negative log loss **per completed survey**. No random survey-level splitting or matching on the outcome.

### Predeclared, common-source nested comparisons

For each background, **same folds and biological predictor ranks**, fit candidate statistical observation models on training blocks only:

| code | Predictor additions beyond nuisance survey, weather, climate, geography and additive O,S,V | Role |
|---|---|---|
| `env_add` | none | additive shared-environment/guild baseline |
| `env_OS` | O×S | tests third-guild interaction |
| `env_plant2` | O×V, S×V | plant-context baseline without O×S |
| `env_all` | O×S, O×V, S×V, O×S×V | complete empirical interaction model (PR #145 source comparable) |
| `flex_add` | all `env_add` predictors plus *a priori* all six measured environmental variables' squares and 15 pairwise products | flexible non-linear common-environment baseline |
| `flex_OS` | `flex_add` + O×S | essential conditional test beyond flexible shared environment |
| `flex_plant2` | `flex_add` + O×V,S×V | plant-only two-way alternative |
| `flex_all` | `flex_add` + all four interactions | extended context interactions |

The six environment predictors are exactly the original `ENV` tuple `(bio1,bio4,bio12,bio15,water_3000m_mean,herbaceous_3000m_mean)`. The flexible set has 6 squares + 15 unique cross-products = **21 predeclared terms**; base already has geographical rank-centroid quadratic terms and survey diagnostics. No response-informed variable selection, no multiple penalty searches. Environmental effects may absorb O/S interactions because the guild SDMs were built from climate/land cover, so *loss of incremental predictive gain is not absence of real biology*.

### Endpoint and source-unit uncertainty

Primary extra predictive information: `flex_add` minus `flex_OS` **held-out binomial per-survey NLL** (positive = OS helps) in EACH SDM background, with the original 56 spatial blocks paired. Secondary: `env_add`→`env_OS`, `flex_plant2`→`flex_all`, `flex_add`→`flex_all`, `env_add`→`env_all`. Save per-site heldout predictions, block×model losses, fold support, paired block-bootstrap 95% intervals **999** draws with source-fixed seed 20261102; bootstrap does not re-fit the models.

Require model score reconciliation with existing PR #145 source for `env_add` and `env_all` under both backgrounds (same fold, same PR #145 core). Fail closed if original source population, n surveys, group IDs, geometry, seed, fold boundaries, original baseline NLL, or duplicate source site observations have changed. Include the frozen within-route observational high-minus-low contrast as a **different estimand**, not a predictive-success claim: uniform −0.12185 [−0.19870,−0.03423] vs target-group −0.07250 [−0.18303,+0.02286]; neither is a pond-scale predation effect.

### Precommitted interpretation

- A robust positive *incremental* O×S prediction requires improvement and a 95% conditional block interval excluding zero under **both** SDM backgrounds for the primary `flex_add`→`flex_OS` contrast. This is still within the original NAAMP cohort and cannot establish ecological causality.
- A partial/one-background improvement is a source/background-specific association, not a general stage-dependent food-web selection.
- A nonpositive/uncertain effect leaves the observed wide-area 4,248-site caudate-conditioned Spearman contrast intact as a **descriptive** field result, but cannot support a claims that third-guild ecology adds independent information beyond flexible shared environment.
- No parameter fitting to the original PR #160 synthetic model's four-sign targets, nor reusing its 20,000 candidate sources as an independent field fit. PR #145's mechanism-versus-full-environment negative CV result is retained.
- Keep PR #160 Draft, main untouched, no submitted paper or wild 80-year forecast.

### Required successful outcome gate

1. Exact original PR #145 block and additive/full-interaction held-out score replay;
2. All 4,248 original sites present in all 8 candidates ×2 backgrounds, no route/block leakage;
3. Individual held-out loss sums, 56-block matched uncertainty and complete no-selection comparison grid;
4. Independent complete source artifact, code and editorial evidence ledger; don't report sign or numerical gain before this succeeds.
