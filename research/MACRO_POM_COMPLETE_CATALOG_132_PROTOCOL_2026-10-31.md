# Expanded complete-existing-catalog POM and conditional ABC (2026-10-31)

This is a follow-up declared after completing the initial **24-case** POM pilot, which found no fully adequate matching scenario. The earlier 24 comparisons, rank estimands and toy-ABC limits remain unchanged. This second pass includes **every** already-computed 2026-10-29 literature-extension case (132 cases), rather than selecting only promising cases from past results.

## Why expansion matters

The initial subset omitted `shared_S`, `shared_D`, reciprocal edge ablations (`no_DS`, `no_SD`), frozen size gates and `shared_both_sensitivity`. These are real structural competitors: omission could bias nearest-case ranking. Keep all 132 cases from the archived `design.csv`, not only scenarios with favorable empirical coefficient signs.

## Exact previously computed sources

- Four full, archived `research/results/literature_extension_20261029/primary_{risk}_{size_mode}_cells.csv.gz` files, risk 0/1 and size-mode dynamic/frozen.
- Archived case inventory `research/results/literature_extension_20261029/design.csv`, all 132 case IDs, each with 2 model vegetation levels × 9 S source levels × 9 D source levels, **21,384** total cells. Verify every case is one-to-one with design.csv, no duplicate grids, finite positive F_B.
- Same untouched 4,248 NAAMP site covariate/value distribution, same rank-to-grid mapping, same binary landscape vegetation and strong-call fraction ranks as the pilot.
- Same 6 fitted POM patterns (OS, OV, SV, OSV, O associations conditional on low/high S) and 4 heldout pattern components (two V strata O associations, two within-route coefficients), same bootstrap uncertainty and covariance shrink.
- Both uniform and target-group SDM backgrounds separately.

## Inference status and gates

**Primary:** all 132 deterministic fixed-rate models' Mahalanobis distances, per-component observed-SE differences, six-component 95% overlap and heldout discrepancies. Select and report all ties and exact-identical surfaces. This is a descriptive **best reproducing** candidate, NOT one true causal mechanism.

**Conditional toy rejection ABC:** identical source-proxy warp prior `Uniform(.8,1.2)` and rank-noise prior `Uniform(.2,.8)` as the initial pilot; use 32 synthetic reference draws per case and 6 independently generated pseudo-observations per case for a computationally bounded first full-catalog test. Group exact source-equivalent cases and normalize prior at the **group** level; acceptance fraction 2%. These choices are illustrative measurement-uncertainty assumptions, *not ecological priors on predation, development or recruitment*. Toy mass and confusion **must not be described as biological-model posterior probability**. Population-level ABC for real rate variation requires actual multi-year re-simulation at rate draws and independent constraints before publication.

**No shifting goalposts:** a globally smallest distance in the expanded catalog is permitted to be called "best among tested scenarios", but cannot be called an adequate reproduction if most fitted/heldout observed patterns fail. Label expansion exploratory; earlier data use invalidates pretending an untouched confirmatory holdout.

## Evidence reporting

Report the 132-case full ranking per background, 16+ exact equivalence groups, group/condition metadata, per-pattern discrepancies and heldout components. Report distribution of toy group masses, pseudo recovery confusion matrix and source hashes. Store full synthetic data as GitHub Actions artifacts; commit compact reproducible summaries and all failures in PR #146. ABM/PDE remain secondary and untouched.
