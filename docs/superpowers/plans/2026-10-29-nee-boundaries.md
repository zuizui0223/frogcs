# NEE empirical robustness and amplification boundaries implementation plan

> Execute inline with superpowers:executing-plans; research agent handles independent primary-source audit.

**Goal:** Complete the user-approved existing-data robustness and mechanistic boundary investigation; not claim NEE acceptance or field causal identification.
**Spec:** User accepted the preceding three-part proposal on 2026-10-29.
**Architecture:** Preserve existing kernels and fixed cohort. New dated scripts/results describe subgroup/support sensitivity, resampled SDM estimation, and exact decomposition of hazards. Existing results are references, never tuned targets.
**Tech stack:** Python, numpy/pandas/scipy/sklearn and existing simulation.

## Constraints and design decisions
- Same 4248-site cohort and both SDM backgrounds. Existing regional analysis is reused; no outcome-selected geography.
- Seasonal outcomes use all valid visits in season, minimum 3 visits and 2 years per site, >=200 sites/20 routes/10 blocks for inference. Predictor ranks retain full cohort references. Frog species results require source-specific call indices; never infer strong calls from source_taxa alone.
- Common habitat support: high/low thirds of S suitability, spatial cross-fitted classifier from fixed nuisance variables, retain probability .1-.9. This diagnoses support, not a causal propensity design. Report losses and balance, not just surviving coefficient.
- Taxon robustness: leave-one-predator-species-out guild averages; distinguish from observed frog-species outcomes.
- Uncertainty: refit SDMs from saved presence/background rows with common spatial-block bootstrap weights, retaining reference background percentile. Replay saved predictions first. Joint site/environment resampling explicitly distinguished from SDM-only sensitivity. Do not call limited replicate quantiles precise 95% confidence intervals.
- Model: local density-response derivative plus exact algebraic path attribution. Copy kernel only for observer instrumentation, exact replay test. Do not equate local D hazard derivative with full OS contrast.
- Current literature may make proposed boundary established rather than novel; record that outcome.

## Tasks
- [x] 1. Tests for seasonal denominators/support/group splitting and derivative/decomposition identities.
- [x] 2. Fixed-region reuse, season and taxon analyses; common-support audit with all failures recorded.
- [x] 3. Replay SDMs and spatial resampling; refit flexible nuisance models for outcome uncertainty within feasible fixed replicate count; report limits.
- [x] 4. Trace baseline/FF/FD/both/full model at low/high vegetation and both size reversal orders. Decompose D hazard changes into F,D,S-state terms and total OS into D/S hazards. Verify exact replay, sum identities, derivative finite differences and timestep sensitivity.
- [x] 5. Report generality/novelty against primary literature, update manuscript and NEE status, export deliverables, validate and update PR144.

## Review focus
No taxa-list to call-intensity conversion; no fitted-suitability to density claim; no conditional bootstrap presented as full uncertainty; no local derivative called whole-system causality; no established depletion mechanism called new theory.

## Execution rulings and verified outcomes
- The proposed direction was explicitly approved by the user; no repeated design permission was requested.
- Reused four-region original sensitivity instead of outcome-selecting new geography. RunNumber is survey round, so fixed calendar quarters were added; seasonal survey controls were recomputed after review.
- Support trimming is not environmental matching: remaining SMD reported. Frog-specific CallingIndex recovery attempted; HTTP403 recorded, source_taxa not misused.
- 49 SDM and joint draws are stability diagnostics, not precise confidence intervals. Summary now rejects incomplete runs.
- Mean annual states did not exactly replay nonlinear hazards in all stage contexts (initial difference about2.1e-5). Replaced that approximation with all20actual yearly states; replay now within1e-10.
- Added a literature-motivated independent-predator/shared-prey null and single-edge removals. Local boundary and full OS are distinguished.
- Exact cache design assertions added after review. Final reviewer found no remaining required fixes.
- 156tests pass; original894files verify. Two new figures visually checked. No field-causal identification or NEE submission-ready claim.
