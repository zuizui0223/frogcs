# JAE submission handoff v2.0 — activation-decomposition revision

## Article

**Title:** Recent rainfall predicts broader frog acoustic participation without stronger residual co-calling associations

**Target:** Journal of Animal Ecology — Research Article

**Submission authority:** `CLAIM_BOUNDARY_V2_0.json`

## Current scientific claim

Across independent North American and Australian acoustic monitoring systems, more recent rainfall is associated with a greater probability of multispecies frog calling in a short observation unit.

In standardized NAAMP data, the rainfall-associated multispecies signal is activation-dominated:
- recent rain is associated with a greater probability that a stop contains any calling frog;
- recent rain is associated with a larger acoustically active species pool;
- rain does not detectably strengthen multispecies calling conditional on activity;
- rain does not detectably change observed-minus-independence residual co-calling;
- rain does not detectably change mean pairwise excess covariance;
- rain does not detectably change pairwise network density.

The paper therefore does **not** claim temporal-niche compression, interspecific facilitation or rainfall-driven pairwise synchrony.

## Key submission values

### NAAMP raw pattern
- 9,399 runs / 900 routes / 93,383 sampled stops.
- OR per 1 SD increasing dryness = 0.969.
- 95% CI 0.941–0.998; P = 0.0388.
- complete-10-stop sensitivity P = 0.058.

### NAAMP adjusted rain robustness
- plausible-temperature subset: 8,200 runs / 814 routes.
- rain + temperature model: rain OR = 0.942; P = 1.71e-4.
- + nonlinear day-of-year: rain OR = 0.946; 95% CI 0.917–0.976; P = 5.44e-4.

### NAAMP decomposition
- P(any calling): rain OR = 0.904; P = 4.63e-8.
- P(>=2 | >=1): rain OR = 0.988; P = 0.402.
- active-pool richness: beta = -0.01872; P = 1.92e-4.
- independence residual: beta = 0.000876; P = 0.389.
- mean pairwise excess covariance: beta = 0.000617; P = 0.205.
- network density: P = 0.724.

### FrogID timezone-repaired validation
- 40,754 recordings / 13,148 recorders / 1,623 ERA5 cells.
- OR per 1 SD increasing dry-spell exposure = 0.852945.
- 95% CI 0.827392–0.879287; P = 1.19e-24.
- recorder-cluster P = 6.88e-33.
- within-cell beta = -0.042616; 95% CI -0.051695 to -0.033538; P = 3.57e-20.
- timezone repair altered 151 event hours and six local dates; effect change was negligible.

### H3 hierarchy repair
- hierarchy-corrected beta = -0.0480; P = 0.0698.
- four-window-state sensitivity P = 0.628.
- H3 remains unsupported.

## Evidence hierarchy

See `ANALYSIS_PROVENANCE_V0_1.md`.

Original primary, validation and secondary contracts have externally timestamped Git commits preceding their corresponding effect readbacks. The NAAMP activation-versus-conditional-overlap decomposition was also frozen before its own fit.

Active-pool richness, independence residual, pairwise covariance, H3 hierarchy repair, DaysSinceRain audit and FrogID timing repairs are explicitly labelled reviewer-motivated post-opening diagnostics/specification repairs.

## Technical QA

Passing revised manuscript QA:
- run `36113948458`
- review artifact `10854350433`
- artifact digest `sha256:b946c971874556b9f3b8049913439d2731a58d6ab6f92117621ba7055fafa947`
- 295-word numbered abstract
- 4,115 guarded words at that passing snapshot
- eight keywords
- anonymous DOCX
- Figures 1–3

Figure hashes are frozen in `REVISION_FIGURE_HASHES_V0_1.json` and must reproduce exactly.

## Source / implementation repairs

- NAAMP DaysSinceRain documented range audited: no numeric values outside 0–180.
- FrogID exact analyzed source: SHA-pinned ALA `dr14760.zip`, Dataset 7.0 temporal scope.
- FrogID literal-backslash JSON serialization bug repaired; weather digest semantics intentionally unchanged.
- FrogID eventTime offsets audited; timezone-aware local date/hour repair adopted.
- Static spatial robustness retained in both systems.

## Remaining initial-submission blocker

Human metadata only:
- authors and order;
- affiliations;
- corresponding-author details;
- CRediT roles;
- funding / acknowledgements;
- Conflict of Interest;
- Statement on Inclusion;
- all-author approval / authorship completeness / no concurrent submission.

Archive DOI is intentionally deferred from the double-anonymized initial main manuscript.

## Superseded material

Old RC1/RC2 and manuscript v0.3 remain audit history only. They must not be submitted.
