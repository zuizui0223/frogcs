# Frog active-community response to rainfall — JAE RC9 reproducibility package

Current Journal of Animal Ecology candidate:

**Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization**

## Current scientific authority

The canonical submission state is aligned across:

- `main`
- `release/jae-v1-rc9`
- `submission/jae-v1`

Current article surfaces:

- manuscript: `MANUSCRIPT_JAE_V1_1.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC9_V0_1.md`
- cover letter: `submission/COVER_LETTER_JAE_V0_12.md`
- novelty audit: `submission/NOVELTY_AUDIT_V0_9.md`
- reviewer attack matrix: `submission/REVIEWER_ATTACK_MATRIX_V0_9.md`
- submission handoff: `submission/SUBMISSION_HANDOFF_RC9.md`
- story freeze: `submission/RC9_STORY_FREEZE_V0_1.json`
- current JAE compliance audit: `submission/JAE_INITIAL_SUBMISSION_AUDIT_RC9_2026_09_28.md`
- post-freeze compliance receipt: `submission/RC8_POSTFREEZE_JAE_INITIAL_SUBMISSION_COMPLIANCE_RECEIPT_V0_1.json`
- post-freeze hypothesis-spine receipt: `submission/RC8_POSTFREEZE_HYPOTHESIS_SPINE_RECEIPT_V0_1.json`
- main figures: `figures_ecology_v1_0/`

**Canonical SI:** `SUPPORTING_INFORMATION_JAE_RC9_V0_1.md`.

`SUPPORTING_INFORMATION_JAE_RC6_V0_1.md`, `SUPPORTING_INFORMATION_JAE_RC7_V0_1.md` and `SUPPORTING_INFORMATION_JAE_RC8_V0_1.md` remain repository audit history only and are not current submission authority.

RC1–RC8 release branches are intentionally retained as immutable audit/fallback history.

## Question spine

RC9 is organized around three linked questions:

1. **Q1 — expansion and external consistency:** do recent-rain conditions expand the behaviourally realized community, and is taxonomic deepening within already-active units directionally consistent in independent North American and Australian systems?
2. **Q2 — structure:** is the resulting species × site allocation distinguishable from a magnitude-matched uniform activation process? This is the central structural test.
3. **Q3 — differentiation:** does expansion materially erode local pairwise-Sørensen differentiation?

The general distinction is **community amplification versus community recruitment**: environmental pulses can recruit previously inactive spatial and taxonomic participation beyond what uniform amplification predicts while retaining local differentiation.


## Cross-continental active-unit taxonomic deepening

RC9 adds a frozen external validation of the most transportable response component: **species richness beyond the first species within an acoustic unit that is already active**.

North America:
- NAAMP active-stop richness rainfall-contrast β = **+0.0794**;
- 95% CI = **+0.0231 to +0.1357**.

Australia:
- **40,754** expert-validated FrogID recordings;
- excess richness = species richness − 1;
- β per 1 SD increasing log dry-spell exposure = **−0.0818**;
- 95% CI = **−0.0982 to −0.0654**;
- recorder-clustered and within-ERA5-cell sensitivities are also fully negative.

Secondary Australian depth endpoints agree:
- ≥3-species recording OR = **0.846** per 1 SD increasing dry-spell exposure;
- excess richness beyond two species β = **−0.0483**.

Frozen decision: **STRONG PASS**.

Authorized interpretation:

> **Rainfall-associated taxonomic deepening within already-active acoustic units is directionally consistent across independent North American and Australian monitoring systems.**

This does **not** authorize worldwide universality, pooled effect sizes, identical mechanisms across continents or replication of the fixed ten-stop NAAMP matrix geometry in FrogID.

Authoritative files:
- `submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json`
- `CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json`
- `submission/RC8_CROSSCONTINENTAL_DEPTH_DECISION_TREE_V0_1.json`
- `CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json`
- `scripts/run_crosscontinental_active_depth.py`

## Main ecological result

Across 4,236 matched wetter–drier route × seasonal-window comparisons from 585 routes in 21 states:

- active spatial footprint increases with rainfall contrast;
- local alpha richness among active stops increases;
- route gamma richness increases;
- richness also increases at the same numbered stops that are acoustically active in both paired surveys.

Headline coefficients:

- active stops: **β = +0.384**;
- local alpha: **β = +0.0794 species per active stop**;
- route gamma: **β = +0.2859 species**.

The study concerns the **behaviourally realized acoustic community**. It does not infer occupancy, abundance, colonization, extinction, dispersal or reproductive success.

## North American matrix geometry: uniform activation is not enough

The exact species × stop decomposition contains four components:

- corner expansion — route-new species at newly active stops;
- spatial spread — route-existing species at newly active stops;
- taxonomic deepening — route-new species at already-active stops;
- within-core rearrangement — route-existing species at already-active stops.

Observed coefficient shares are:

- corner expansion: **36.9%**;
- spatial spread: **15.2%**;
- taxonomic deepening: **39.9%**;
- within-core rearrangement: **8.0%**.

Thus **92.0%** of the rainfall-associated incidence slope crosses at least one spatial or taxonomic boundary.

RC9 does not treat 92% alone as surprising. A high boundary-crossing fraction is expected whenever overall activation increases. The paper therefore compares the observed decomposition with a frozen magnitude-matched **uniform-activation null**.

The null:

- preserves observed dry matrices;
- estimates dry-side species × StopNumber acoustic propensities from unique drier-member runs;
- applies one common additive log-odds activation shift to all candidate cells;
- calibrates that shift for each pair so expected wet incidence count equals the observed wet incidence count;
- recomputes all four components in 1,000 simulations.

Primary κ = 2 result:

- null mean boundary crossing: **80.9%**;
- 95% null interval: **74.2–87.4%**;
- observed: **92.0%**;
- four-component omnibus Monte Carlo **P = .000999**.

The same omnibus decision holds under the frozen κ = 1 and κ = 5 smoothing sensitivities (**P = .000999** each).

The departure is structured:

- corner expansion: **36.9% observed vs 27.4% null mean**;
- spatial spread: **15.2% vs 22.9%**;
- taxonomic deepening: **39.9% vs 30.5%**;
- within-core rearrangement: **8.0% vs 19.1%**.

The authorized interpretation is therefore:

> **Rainfall-associated acoustic-community growth is more taxonomically recruiting and less core-rearranging than a magnitude-matched uniform increase in baseline species × site activation predicts.**

Rejecting the null does **not** identify a unique biological mechanism.

Authoritative null files:

- `NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json`
- `NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json`
- `NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_2.json`
- `NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_3.json`
- `NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`
- `scripts/run_naamp_uniform_activation_null.py`

## Practical non-homogenization

Pairwise Sørensen differentiation is tested with a fixed post hoc practical-equivalence margin of **±0.025 rainfall-slope units**.

Primary:
- β = **-0.000492**;
- 90% CI = **-0.0107 to +0.00968**;
- practical-equivalence PASS.

Exact consecutive-year:
- β = **+0.00215**;
- 90% CI = **-0.00973 to +0.0140**;
- practical-equivalence PASS.

This supports **practical stability of the pairwise Sørensen slope within the fixed margin**. It does not establish exact invariance or equivalence of every beta-diversity metric.

Active-matrix fill separately remains within its previously frozen ±0.05 practical-equivalence margin, but fill is mathematically linked to alpha/gamma and is not treated as an independent diversity axis.

## Important separation

The uniform-activation null is rejected because of **incidence allocation**, not because Sørensen beta diversity behaves unusually.

Under the primary uniform null:
- Sørensen slope null mean = **-0.00615**;
- 95% null interval = **-0.0130 to +0.00178**;
- observed = **-0.00049**.

The observed Sørensen slope lies within that null distribution.

Thus RC9 separates two claims:

1. **where additional incidences enter the matrix differs strongly from uniform activation**;
2. **pairwise Sørensen differentiation remains practically stable within a fixed margin**.

## Geographic and design robustness

### Geographic generality

Every one of 21 leave-one-state-out refits retains positive, 95%-CI-supported coefficients for:

- active spatial footprint;
- local alpha;
- route gamma.

This establishes robustness to omission of any single sampled state, not a uniformly positive response in every state. State-specific slopes remain heterogeneous.

### NAAMP rain-targeting protocol

The national NAAMP protocol targeted surveys within three days of rain in some regions. DaysSinceRain is therefore partly conditioned by programme scheduling and is not a randomized exposure.

A frozen sensitivity requiring the **drier survey to occur at least four days after rain** retained:

- 1,769 pairs;
- 425 routes;
- 20 states.

All three headline coefficients remained 95%-CI positive:

- active stops: **0.374 [0.198, 0.551]**;
- local alpha: **0.0839 [0.0140, 0.154]**;
- route gamma: **0.289 [0.133, 0.446]**.

This shows the headline is not confined to comparisons entirely within the 0–3 day target window. It does not establish rainfall causality or eliminate protocol selection.

### Recorded detection conditions

Footprint, alpha and gamma effects remain positive after adjustment for recorded hearing impairment, major-noise timeouts and wind; traffic and Massachusetts noise-index sensitivities agree.

Unmeasured species-specific detectability and masking remain possible.

## Species-level mechanism: falsified rather than rescued

A proposed post-opening “activation geometry” was highly repeatable across non-overlapping years and disjoint route sets but failed a separately frozen rain-specificity placebo gate.

Wet-gain geometry was strongly reproduced by:

- reverse-direction dry gains: ρ = **0.929**;
- low-rain-contrast gains: ρ = **0.953**;
- opportunity-corrected baseline solitude tendency: ρ = **0.782**;
- raw singleton-calling fraction: ρ = **0.876**.

Activation geometry is therefore **not** treated as a rainfall-specific response trait.

The North American uniform-null rejection does not rescue this failed trait.

Independent anuran literature supports heterogeneous activation thresholds, breeding/inundation cues and hydric physiology as plausible discussion-level pathways. None is identified as the causal mediator of the NAAMP result.

## Historical v0.4 reconciliation

An earlier manuscript version reported a null pooled active-stop conditional-multispecies effect:

- OR = **0.988**;
- 95% CI = **0.959–1.017**;
- P = **.402**.

The current matched analysis estimates wet-minus-dry changes in run-level active-stop depth under a different weighting, exposure scale and matched design. The ≥2-species threshold component is positive but contributes only ~28.9% of the local-alpha slope; ~71.1% lies beyond the second species.

The explicit reconciliation remains in current Supporting Information. The earlier result is retained rather than hidden.

## Inferential boundaries

RC9 does **not** claim:

- rainfall causality;
- occupancy or abundance change;
- colonization or extinction;
- demographic connectivity among route stops;
- uniform response across states;
- exact beta-diversity invariance;
- equivalence of every beta metric;
- a validated rainfall-specific species trait;
- a unique mechanism from uniform-null rejection;
- hydration or inundation mediation;
- a week-long response endpoint;
- a physiological rainfall-response half-life.

## Submission QA

The RC9 submission package checks:

- the v1.1 scientific package;
- uniform-null decision and all three smoothing sensitivities;
- Sørensen practical-equivalence bounds;
- title and inferential-boundary consistency;
- current Figure 1/2 content;
- anonymous v1.1 main-manuscript DOCX;
- anonymous RC9 Supporting Information DOCX.

## Repository history and branch policy

Release branches `release/jae-v1-rc1` through `release/jae-v1-rc9` are retained as versioned audit history.

The repository also contains historical `revision/*`, `fix/*`, `chore/*` and `cleanup/*` branches created during the analysis/falsification path. They are **not current scientific authority**. Current authority is defined only by the branches and files listed at the top of this README.

Historical manuscripts, SI versions, workflows and failed/falsified analyses are preserved deliberately for auditability and should not be used as current submission surfaces.

## Data sources

- NAAMP: DOI **10.5066/F7G44NG0**
- FrogID dataset: DOI **10.3897/zookeys.912.38253**
- AmphiBIO v1: article DOI **10.1038/sdata.2017.123**; data DOI **10.6084/m9.figshare.4644424.v5**

Raw third-party source datasets are not redistributed.

## Development policy

The RC9 story is frozen around:

1. cross-continentally consistent taxonomic deepening within already-active acoustic units across North America and Australia;
2. multiscale active-community expansion in standardized NAAMP routes;
3. four-component North American incidence allocation that strongly rejects the frozen uniform-activation null;
4. excess route-new taxonomic participation relative to that null;
5. pairwise Sørensen practical stability within the fixed ±0.025 slope margin;
6. geographic, protocol-window and recorded-detection robustness;
7. no worldwide-universality, pooled-effect-size, species-level-mechanism or causal-rainfall claim.

No additional endpoint search, new continent, replacement null model, Sørensen-margin retuning, residualized activation-geometry rescue or replacement post-opening species trait is authorized for this submission without an explicit versioned unfreeze justified by an editor/reviewer request or documented defect.
