# Current paper overview

## Paper

**Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts**

Current submission authority is synchronized across `main`, `release/jae-v1-rc11`, and `submission/jae-v1`.

Journal-facing sources:

- `MANUSCRIPT_JAE_V1_3.md`
- `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md`
- `JAE_TITLE_PAGE_V0_8.template.md`
- `submission/COVER_LETTER_JAE_V0_13.md`

## Scientific spine

Across 4,236 matched wetter–drier NAAMP comparisons, recent-rain conditions are associated with expansion in:

- number of acoustically active stops;
- richness per active stop;
- route-level richness.

The main structural result is the location of added species × stop incidences. **92.0%** of the rainfall-associated incidence slope crosses a spatial or taxonomic boundary.

A magnitude-matched uniform-activation null expects **80.9%** boundary crossing; the observed four-component allocation rejects that null. A persistence-preserving null that strongly anchors each pair to its dry matrix also fails to reproduce the observed allocation (**77.9%** expected boundary crossing under the primary anchor).

The large same-observer sensitivity retains **3,152 pairs (74.4%)** and again gives **92.0%** boundary crossing, so observer turnover is not required for the headline pattern.

FrogID provides **cross-dataset directional consistency** for active-unit taxonomic depth. It is not treated as independent validation or a pooled cross-continent effect-size analysis.

## Current evidence anchors

### Community expansion

- `contracts/NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1.json`
- `contracts/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1.json`
- `summaries/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json`

### Species × stop allocation

- `contracts/NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_CONTRACT_V0_1.json`
- `contracts/NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json`
- `repairs/NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json`
- `summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`

### Persistence stress test

- `submission/RC10_SCOPE_UNFREEZE_V0_1.json`
- `submission/RC10_STORY_DECISION_TREE_V0_1.json`
- `contracts/NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json`
- `summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json`

### Same-observer robustness

- `contracts/NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json`
- `summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json`

### Pairwise Sørensen context

- `contracts/NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1.json`
- `summaries/NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json`

### Cross-dataset active-unit depth

- `submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json`
- `contracts/CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json`
- `summaries/CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json`

### Design / detectability robustness

- `contracts/NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1.json`
- `contracts/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1.json`
- `contracts/NAAMP_DETECTION_QUALITY_ROBUSTNESS_CONTRACT_V0_1.json`
- `contracts/NAAMP_WITHIN_ACTIVE_DEPTH_CONTRACT_V0_1.json`
- `contracts/FROGID_TIMEZONE_REPAIR_CONTRACT_V0_1.json`

## Remaining inferential boundary

The tested activation comparators impose a common activation shift. A null allowing **species-specific rainfall-response shifts** has not been tested. The paper therefore does not uniquely separate species-level response heterogeneity from site-level activation as the source of excess boundary allocation.

The study concerns behaviourally realized acoustic communities. It does not claim rainfall causality, occupancy or abundance change, colonization/extinction, demographic connectivity, a unique mechanism, worldwide universality, or identical cross-continent effect sizes.

## Submission provenance

- `submission/RC11_STORY_FREEZE_V0_1.json`
- `submission_docs/JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md`
- `submission_docs/NOVELTY_AUDIT_V0_11.md`
- `submission_docs/REVIEWER_ATTACK_MATRIX_V0_11.md`
- `submission_docs/SUBMISSION_HANDOFF_RC11.md`

Paths in this overview are relative to `provenance/`.

## Historical material

The current branch intentionally omits superseded analyses and submission versions. Full history remains in:

- `history/pre-deep-cleanup-2026-09-28`;
- `release/jae-v1-rc1` through `release/jae-v1-rc11`;
- ordinary Git history.
