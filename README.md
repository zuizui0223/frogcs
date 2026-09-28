# Frog active-community response to rainfall — JAE RC11 reproducibility package

Current Journal of Animal Ecology candidate:

**Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts**

## Current scientific authority

The canonical submission state is aligned across:

- `main`
- `release/jae-v1-rc11`
- `submission/jae-v1`

Current article surfaces:

- manuscript: `MANUSCRIPT_JAE_V1_3.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md`
- cover letter: `submission/COVER_LETTER_JAE_V0_13.md`
- novelty audit: `submission/NOVELTY_AUDIT_V0_11.md`
- reviewer attack matrix: `submission/REVIEWER_ATTACK_MATRIX_V0_11.md`
- submission handoff: `submission/SUBMISSION_HANDOFF_RC11.md`
- story freeze: `submission/RC11_STORY_FREEZE_V0_1.json`
- pre-submission review disposition: `submission/RC10_PRE_SUBMISSION_REVIEW_DISPOSITION_V0_1.md`
- current JAE compliance audit: `submission/JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md`
- post-freeze compliance receipt: `submission/RC8_POSTFREEZE_JAE_INITIAL_SUBMISSION_COMPLIANCE_RECEIPT_V0_1.json`
- post-freeze hypothesis-spine receipt: `submission/RC8_POSTFREEZE_HYPOTHESIS_SPINE_RECEIPT_V0_1.json`
- main figures: `figures_ecology_v1_0/`
- title-page template: `JAE_TITLE_PAGE_V0_8.template.md`
- metadata template: `submission/SUBMISSION_METADATA_TEMPLATE_V0_7.yml`
- citation template: `submission/CITATION_V0_5.cff.template`
- human-finalization guide: `submission/HUMAN_FINALIZATION_RC11.md`

**Canonical SI:** `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md`.

## Repository layout

The default branch is intentionally split into current authority, reproducibility code and archived submission history.

- repository root: current manuscript/SI/title-page surfaces plus scientific contracts, receipts and summaries used by active analyses;
- `scripts/`: current analysis and reproducibility scripts only;
- `.github/workflows/`: current submission QA plus analysis workflows that remain useful for reproducibility;
- `submission/`: current submission surfaces and provenance files still referenced by the present paper;
- `figures_ecology_v1_0/` and `figures_ecology_v1_2/`: current figures;
- `archive/`: superseded manuscripts, SI, title pages, submission documents, workflows, QA/build scripts and old figure directories.

Files under `archive/` are audit history, not current authority. Exact historical states also remain available on release branches.


Superseded manuscripts, Supporting Information, title-page templates and submission-facing documents are retained under `archive/` and on immutable historical release branches.

RC1–RC10 release branches are intentionally retained as immutable audit/fallback history.

## Question spine

RC11 retains the RC10 three-question scientific spine:

1. **Q1 — expansion:** do recent-rain conditions expand spatial and taxonomic participation?
2. **Q2 — allocation:** is the species × site allocation more boundary-biased than uniform activation predicts, including under strong dry-state persistence?
3. **Q3 — consistency/context:** does active-unit taxonomic depth point in the same recent-rain direction in NAAMP and FrogID, and what happens to pairwise composition?

The general distinction is **community amplification versus community recruitment**: environmental pulses can recruit previously inactive spatial and taxonomic participation beyond what uniform amplification predicts while retaining local differentiation.


## Cross-dataset active-unit taxonomic deepening

RC11 retains the RC10 estimand-aligned cross-dataset comparison of the most transportable response component: **species richness beyond the first species within an acoustic unit that is already active**.

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

> **Active-unit taxonomic deepening has the same recent-rain direction in the aligned NAAMP and FrogID analyses.**

This is cross-dataset consistency, not independent validation. It does **not** authorize worldwide universality, pooled effect sizes, identical mechanisms or replication of the fixed ten-stop NAAMP matrix geometry in FrogID.

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

RC11 does not treat 92% alone as surprising. A high boundary-crossing fraction is expected whenever overall activation increases. The paper therefore compares the observed decomposition with a frozen magnitude-matched **uniform-activation null**.

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

## Persistence-preserving null: the allocation result survives strong dry-state anchoring

RC11 retains the RC10 reviewer-facing persistence stress test that removes hierarchical species-level shrinkage and directly anchors each pair to its observed dry species × stop state before applying the common activation shift.

Primary a = 0.75:
- boundary null mean: **77.9%**
- 95% null interval: **73.4–82.8%**
- observed boundary crossing: **92.0%**
- expected within-core: **22.1%** vs **8.0% observed**
- four-component omnibus **P = .000999**

The same omnibus result holds at a = 0.50 and 0.90 (**P = .000999** each). At a = 0.90, the upper 95% boundary-crossing null bound is **82.3%**.

Therefore the observed allocation is not explained by a null model that makes stable species × stop identities too exchangeable.

Authoritative files:
- `submission/RC10_SCOPE_UNFREEZE_V0_1.json`
- `NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json`
- `NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json`
- `submission/RC10_STORY_DECISION_TREE_V0_1.json`

## Secondary Sørensen context

Pairwise Sørensen differentiation is tested with a fixed post hoc practical-equivalence margin of **±0.025 rainfall-slope units**.

Primary:
- β = **-0.000492**;
- 90% CI = **-0.0107 to +0.00968**;
- practical-equivalence PASS.

Exact consecutive-year:
- β = **+0.00215**;
- 90% CI = **-0.00973 to +0.0140**;
- practical-equivalence PASS.

The 90% interval lies within the post hoc ±0.025 bound, but this is secondary context rather than a headline discovery because the bound was selected after the conventional coefficient was known and the observed slope is ordinary under the uniform-activation null.

Active-matrix fill separately remains within its previously frozen ±0.05 practical-equivalence margin, but fill is mathematically linked to alpha/gamma and is not treated as an independent diversity axis.

## Important separation

The uniform-activation null is rejected because of **incidence allocation**, not because Sørensen beta diversity behaves unusually.

Under the primary uniform null:
- Sørensen slope null mean = **-0.00615**;
- 95% null interval = **-0.0130 to +0.00178**;
- observed = **-0.00049**.

The observed Sørensen slope lies within that null distribution.

Thus RC11 separates two claims:

1. **where additional incidences enter the matrix differs strongly from uniform activation**;
2. **pairwise Sørensen differentiation remains practically stable within a fixed margin**.

## Same-observer robustness

RC11 adds a prefrozen reviewer-defense analysis using the public NAAMP `ObserverTrackingID`. Restricting the matched design to the same observer in both wetter and drier surveys retained **3,152 of 4,236 pairs (74.4%)**, spanning **500 routes and 542 observer identifiers**.

All three headline coefficients remained 95%-CI positive: active stops **0.352 [0.179, 0.525]**, active-stop alpha **0.098 [0.028, 0.169]**, and route gamma **0.319 [0.171, 0.466]**. Observed boundary crossing remained **92.0%**. The same-observer primary uniform null expected **80.3% [73.0, 87.1%]** and the primary persistence-preserving null expected **79.1% [73.3, 84.9%]**; both four-component omnibus tests gave **P=.001**.

This shows that between-observer turnover is not required for the headline pattern in the large same-observer subset. It does not prove observer equivalence or eliminate all detectability bias.

Authoritative files:
- `NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json`
- `NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json`
- `scripts/run_naamp_same_observer_robustness.py`

## Explicit remaining null boundary

Both tested null families impose a common activation shift. RC11 explicitly states that a null allowing **species-specific rainfall-response shifts** remains untested. The present analysis therefore does not distinguish species-level response heterogeneity from site-level activation as the unique source of excess boundary allocation. This analysis is reserved for editor/reviewer request rather than searched pre-submission.

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

RC11 does **not** claim:

- rainfall causality;
- occupancy or abundance change;
- colonization or extinction;
- demographic connectivity among route stops;
- uniform response across states;
- exact beta-diversity invariance;
- equivalence of every beta metric;
- a validated rainfall-specific species trait;
- a unique mechanism from uniform-null rejection;
- exclusion of species-specific rainfall-response heterogeneity;
- hydration or inundation mediation;
- a week-long response endpoint;
- a physiological rainfall-response half-life.

## Submission QA

The RC11 submission package checks:

- the v1.3 scientific package;
- uniform-null decision and all three smoothing sensitivities;
- Sørensen practical-equivalence bounds;
- title and inferential-boundary consistency;
- current Figure 1/2 content;
- same-observer reviewer robustness and explicit species-specific-null boundary;
- anonymous v1.3 main-manuscript DOCX;
- anonymous RC11 Supporting Information DOCX.

## Repository history and branch policy

Release branches `release/jae-v1-rc1` through `release/jae-v1-rc11` are retained as versioned audit history.

The repository also contains historical `revision/*`, `fix/*`, `chore/*` and `cleanup/*` branches created during the analysis/falsification path. They are **not current scientific authority**. Current authority is defined only by the branches and files listed at the top of this README.

Historical manuscripts, SI versions, workflows and failed/falsified analyses are preserved deliberately for auditability and should not be used as current submission surfaces.

## Data sources

- NAAMP: DOI **10.5066/F7G44NG0**
- FrogID dataset: DOI **10.3897/zookeys.912.38253**
- AmphiBIO v1: article DOI **10.1038/sdata.2017.123**; data DOI **10.6084/m9.figshare.4644424.v5**

Raw third-party source datasets are not redistributed.

## Development policy

The RC11 story is frozen around:

1. multiscale active-community expansion in standardized NAAMP routes;
2. four-component incidence allocation that strongly rejects the original uniform-activation null;
3. the same allocation departure under a persistence-preserving null with 50–90% pair-specific dry-state anchoring;
4. directional cross-dataset consistency of active-unit taxonomic deepening in NAAMP and FrogID;
5. pairwise Sørensen retained only as secondary bounded context;
6. geographic, protocol-window, recorded-detection and same-observer robustness;
7. explicit acknowledgement that species-specific activation shifts remain untested;
8. no independent-validation, worldwide-universality, pooled-effect-size, species-level-mechanism or causal-rainfall claim.

No additional endpoint search, new continent, replacement null model, Sørensen-margin retuning, residualized activation-geometry rescue or replacement post-opening species trait is authorized for this submission without an explicit versioned unfreeze justified by an editor/reviewer request or documented defect.
