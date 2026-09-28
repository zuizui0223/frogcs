# Current paper provenance overview

This document is the compact provenance map for the current Journal of Animal Ecology submission.

## Current scientific claim

**Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts.**

Across 4,236 matched NAAMP wetter–drier comparisons, recent-rain conditions are associated with expansion in active spatial footprint, richness per active stop and route richness. The incidence allocation is more boundary-biased than a magnitude-matched uniform-activation comparator predicts, including under strong dry-state persistence. The same pattern survives restriction to 3,152 same-observer pairs.

FrogID supplies directional cross-dataset consistency for active-unit taxonomic depth. It is not treated as independent validation of the NAAMP matrix geometry.

A null allowing species-specific activation shifts remains untested and is reserved for revision if requested.

## Core current provenance

### Primary NAAMP expansion
- `provenance/contracts/NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1.json`
- `provenance/receipts/NAAMP_ECOLOGICAL_PULSE_RECEIPT_V0_1.json`
- `scripts/naamp/run_naamp_ecological_pulse.py`

### Multiscale community responses
- `provenance/contracts/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1.json`
- `provenance/summaries/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json`
- `scripts/naamp/run_naamp_metacommunity_alpha_beta_gamma.py`

### Species × stop allocation
- `provenance/contracts/NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_CONTRACT_V0_1.json`
- `scripts/naamp/run_naamp_spatial_taxonomic_activation_decomposition.py`

### Uniform-activation comparator
- `provenance/contracts/NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json`
- `provenance/repairs/NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json`
- `provenance/summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`
- `scripts/naamp/run_naamp_uniform_activation_null.py`

### Persistence-preserving comparator
- `provenance/contracts/NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json`
- `provenance/submission/RC10_SCOPE_UNFREEZE_V0_1.json`
- `provenance/submission/RC10_STORY_DECISION_TREE_V0_1.json`
- `provenance/summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json`
- `scripts/naamp/run_naamp_persistence_preserving_null.py`

### Same-observer robustness
- `provenance/contracts/NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json`
- `provenance/summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json`
- `scripts/naamp/run_naamp_same_observer_robustness.py`

### Protocol and detection robustness
- `provenance/contracts/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1.json`
- `provenance/contracts/NAAMP_DETECTION_QUALITY_ROBUSTNESS_CONTRACT_V0_1.json`
- `provenance/contracts/NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1.json`

### Sørensen context
- `provenance/contracts/NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1.json`
- `provenance/summaries/NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json`

### Cross-dataset depth
- `provenance/contracts/CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json`
- `provenance/contracts/FROGID_TIMEZONE_REPAIR_CONTRACT_V0_1.json`
- `provenance/submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json`
- `provenance/summaries/CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json`
- `scripts/frogid/run_crosscontinental_active_depth.py`

### Current submission freeze and reviewer defense
- `provenance/submission/RC11_STORY_FREEZE_V0_1.json`
- `provenance/submission_docs/JAE_INITIAL_SUBMISSION_AUDIT_RC11_2026_09_28.md`
- `provenance/submission_docs/NOVELTY_AUDIT_V0_11.md`
- `provenance/submission_docs/REVIEWER_ATTACK_MATRIX_V0_11.md`
- `provenance/submission_docs/SUBMISSION_HANDOFF_RC11.md`

## Historical material

Exploratory analyses, superseded contracts, failed mechanisms and earlier submission states are not duplicated on the current branch. They remain available from:

- `history/pre-deep-cleanup-2026-09-28`;
- `release/jae-v1-rc1` through `release/jae-v1-rc11`;
- ordinary Git history.

The current branch is deliberately restricted to provenance required by the current paper and its active reproducibility workflows.
