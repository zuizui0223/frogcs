# Ecology/Oikos: acoustic observation bridge and mechanism competition (2026-10-31)

## Question and fixed boundaries

Can mechanisms of stage-structured frog (F), caudate (S), and odonate (D) dynamics explain **held-out site-level strong-call frequency** better than a shared-environment baseline, after both are passed through the same acoustic observation operator? This PR is stacked on `research/nee-evidence-gates-20261029` (PR #144). It does not amend the frozen macro source, kernel, or previous results.

The main empirical signal remains the vegetation-by-odonate suitability association (OV). The other pairwise interactions (OS, SV) and the three-way term (OSV) are not forced to predetermined signs. A viable mechanism should improve independent **predictive** comparison, not merely reproduce signs on simulated survival hazards. An honest negative predictive result is a deliverable.

## Pre-specified minimum comparison

1. Source observations: 4,248 NAAMP sites, site visits from `naamp_completed_site_surveys.csv.gz`; count strong-call surveys and valid completed surveys. Each route belongs to exactly one geographic block and one outer fold.
2. Competing mechanistic source surfaces: the five **existing** handling factorial arms (0000, 1000, 0100, 1100, 1111) in `handling_factorial_20261029/dense21_cells.csv.gz`. They were generated before this bridge. No retuning of trophic model parameters on acoustic outcomes.
3. Shared **assumed**, not biologically calibrated, transport: map O/S **suitability rank** to S/D source-grid rank, flooded 3 km vegetation to the synthetic 0/1 structure. Extract F_B from a model-arm grid. No assertion that suitability is density or that 3 km vegetation is pond refuge.
4. Statistical acoustic observation operator: a regularized binomial logistic regression from site environmental covariates and the candidate model's log F_B to visit-level strong-call probability. The log F_B slope, intercept and environmental terms are fitted on **training spatial blocks only**. The observation operator is a predictive bridge, not an independently validated maturation, breeding-participation, vocalization, or detection model.
5. Identical spatial folds, training procedure and scoring across background specifications and all candidates; include an environment-only null. Store held-out per-site predicted probabilities, counts, log scores, observed/predicted interaction summaries, and computation receipts. Never use held-out outcomes for parameter or scenario selection.

## Decision rules

- Primary: out-of-block **per-survey binomial negative log score** relative to the environment-only null in the **same SDM background**, with counts and total visits reported.
- Secondary: squared error on strong-call frequency (survey-weighted), discrimination of the observed OV contrast, and OS/SV/OSV with uncertainty separated from a model selection score.
- Require improvement in both background specifications and non-trivial held-out vegetation support to call a candidate robust. Differences without uncertainty or a mechanistically independent observation calibration remain **conditional predictive ranking**, not a field cause.
- Report whether a model improves the environment-only null, and report all failures; do not choose an observation link or a background after seeing scores. An additional independent field/meth-eDNA experiment is a separate follow-up.

## Scope of this PR

This is a **minimal executable proof of comparison**. It does not claim independent biological calibration, field causal identification, species-specific call prediction, or a completed Ecology/Oikos submission. Any code smoke tests on synthetic inputs must be labeled as such; repository-wide data execution and its numerical outcome must be separately verified before the manuscript is revised.
