# JAE submission handoff — RC3 conditioning revision

## Article

**Title:** Recent rainfall predicts broader frog acoustic participation without stronger residual co-calling associations

**Target:** Journal of Animal Ecology — Research Article

## Core empirical story

1. In NAAMP, recent rain is associated with more multispecies calling across all standardized route-stops and the effect survives temperature and nonlinear day-of-year adjustment.
2. NAAMP decomposition localizes that signal to **participation breadth**: more route-stops contain any caller and the run-level active species pool is larger after recent rain.
3. NAAMP shows no detectable rain-related strengthening of species multiplicity within already-active stops, plug-in independence residuals, fixed-marginal shuffle residuals, mean pairwise excess covariance, or pairwise network density.
4. FrogID is differently conditioned: every analysed recording is already acoustically active. Its strong rain effect on one-versus-multiple species contrasts with the null NAAMP activity-conditioned effect.
5. Therefore FrogID is a **conditioning contrast**, not a direct replication of the NAAMP all-stop or conditional estimand.
6. The ecological inference is that multispecies activity should be decomposed into participation, observation conditioning and residual association before being interpreted as synchrony or temporal-niche reorganization.

## Precision / null interpretation

- NAAMP activity-conditioned OR = 0.988, 95% CI 0.959–1.017; this excludes the adjusted all-stop OR 0.946 on the same dryness scale.
- plug-in residual beta = 0.000876, 95% CI -0.00112–0.00287;
- fixed-marginal shuffle residual beta = 0.000933, 95% CI -0.00110–0.00296;
- the rain-direction residual bounds are about 8% of the within-route all-stop coefficient magnitude (-0.01367).

These are **descriptive precision comparisons, not formal equivalence tests**, because response definitions and subsets differ.

## Key repairs closed

- temperature-adjusted NAAMP rain coefficient recovered;
- H3 hierarchy defect repaired; conclusion remains unsupported;
- DaysSinceRain range/null codes audited;
- FrogID source identity reconciled to the SHA-pinned ALA snapshot;
- FrogID timezone-aware local date/hour repair completed;
- FrogID JSON serialization bug corrected;
- NAAMP stop interpreted as a joint spatial/temporal sampling unit;
- plug-in independence diagnostic supplemented with a 1,024-permutation/run fixed-marginal shuffle null;
- public provenance separates original frozen endpoints from reviewer-motivated post-opening diagnostics.

## Scientific authority

- historical RC3 claim boundary: `CLAIM_BOUNDARY_V2_0.json`
- current submission authority: `CLAIM_BOUNDARY_V2_1.json`
- provenance: `ANALYSIS_PROVENANCE_V0_1.md`

## Submission files

- `MANUSCRIPT_JAE_V0_4.md`
- `figures/FIGURE_1_DESIGN_V0_1.svg`
- `figures/FIGURE_2_EFFECTS_V0_1.svg`
- `figures/FIGURE_3_DECOMPOSITION_V0_1.svg`
- `submission/COVER_LETTER_JAE_V0_2.md`
- `submission/NOVELTY_AUDIT_V0_3.md`
- `submission/REVIEWER_ATTACK_MATRIX_V0_3.md`
- `submission/JAE_SCIENTIFIC_ADAPTATION_V0_2.md`

## Remaining human-only blockers

- final author set/order;
- affiliations and corresponding-author details;
- CRediT roles;
- funding / acknowledgements;
- conflict-of-interest statement;
- Statement on Inclusion;
- all-author approval / authorship completeness / no simultaneous submission.

An archive DOI is not required for initial double-anonymized submission.

## No further ecological outcome search

No additional endpoint hunting is authorized. Further analyses require a concrete reviewer/editor request or a documented data/implementation defect.
