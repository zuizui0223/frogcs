# JAE submission handoff — RC3 activation-decomposition revision

## Article

**Title:** Recent rainfall predicts broader frog acoustic participation without stronger residual co-calling associations

**Target:** Journal of Animal Ecology — Research Article

## Core empirical story

1. A raw short-window multispecies rainfall association replicates across NAAMP and FrogID.
2. The NAAMP rain coefficient persists after temperature and nonlinear day-of-year adjustment.
3. NAAMP decomposition shows a rain association with any acoustic activity and active species-pool richness.
4. Rain does not detectably strengthen conditional multispecies calling, independence-residual co-calling, mean pairwise excess covariance, or pairwise network density.
5. The ecological interpretation is therefore **broader acoustic participation without detectable strengthening of residual association**, not temporal-niche compression.

## Key pre-submission repairs closed

- temperature-adjusted NAAMP rain coefficient recovered and reported;
- original H3 model-hierarchy defect repaired; H3 remains unsupported;
- FrogID source described as the exact SHA-pinned ALA snapshot matching Dataset 7.0 temporal scope;
- FrogID output serialization bug fixed without changing the pinned weather digest construction;
- FrogID eventTime explicit-offset semantics audited;
- timezone-aware event date/hour repair completed; effect change negligible;
- NAAMP DaysSinceRain publisher range and observed values audited;
- provenance ledger documents contract commits before original effect readbacks;
- NAAMP spatial/temporal confounding of the 5-min stop is stated as a limitation;
- small NAAMP primary effect and complete-10-stop P=.058 are retained explicitly.

## Scientific provenance

Original effect families are separated from reviewer-motivated diagnostics in:
- `ANALYSIS_PROVENANCE_V0_1.md`
- `CLAIM_BOUNDARY_V2_0.json`

The post-opening diagnostics cannot replace or retroactively redefine the original primary endpoints.

## Submission files

- `MANUSCRIPT_JAE_V0_4.md`
- `figures/FIGURE_1_DESIGN_V0_1.svg`
- `figures/FIGURE_2_EFFECTS_V0_1.svg`
- `figures/FIGURE_3_DECOMPOSITION_V0_1.svg`
- `submission/COVER_LETTER_JAE_V0_2.md`
- `submission/NOVELTY_AUDIT_V0_3.md`
- `submission/REVIEWER_ATTACK_MATRIX_V0_3.md`
- `submission/JAE_SCIENTIFIC_ADAPTATION_V0_2.md`
- generated anonymized DOCX from revision manuscript QA

## Remaining human-only blockers

- final author set/order;
- affiliations and corresponding-author contact details;
- CRediT roles;
- funding / acknowledgements;
- conflict-of-interest statement;
- statement on inclusion;
- all-author approval / authorship completeness / no simultaneous submission.

An archive DOI is **not required for initial double-anonymized submission**; the manuscript currently states the intended persistent archiving plan. Public DOI finalization is deferred to the archive/finalization stage.

## No further ecological outcome search

No additional endpoint hunting is authorized for RC3. Any further analysis must be a response to a concrete reviewer/editor request or a documented data/implementation defect.
