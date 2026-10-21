# Frog-pair acoustic network: year-strata reproducibility and PEM context modification

Frozen *before new outcome readback*, 2026-10-21. New user-directed post-hoc ecology extension. Does not change frozen JAE RC6.

## Why this test

Existing NWI-weighted fixed-margin frog acoustic pair network: CI1–3 = **43** supported signed pair links among 127 eligible fully resolved species pairs; CI2–3 = **14** among 57. Taxon-specific mapped emergent wetland associations do not uniquely determine whether those taxon units co-call or segregate. No robust nontrivial three-taxon motif excess was found.

Question A: are particular frog pair associations temporally persistent within the existing NAAMP archive, rather than driven by an early or late subset?
Question B: within surveyed ten-stop routes that have **both** mapped PEM-overlap and non-overlap sites, does an association's signed residual differ by mapped vegetation context after controlling taxon stop counts, site richness and cross-fitted species-specific NWI habitat coefficients?

## Fixed inputs and boundaries

- EXACT matched matrices from verified `naamp-nwi-route-crossfit-weighted-checkerboard-v0-1`, GitHub Actions 39516056663: 3,659 CI1–3 (primary) and 1,766 CI2–3 (secondary) runs.
- Immutable USGS NAAMP source files from existing signed/pinned loader and original survey `SurveyYear`. No membership changes: observed C-score must be reproduced exactly for every run.
- Immutable response-blind NWI 250m mapped emergent **PEM** fraction; **mapped polygon overlap >0 versus no mapped polygon overlap**. No mapped polygon does NOT prove no plants.
- Frozen opposite-route cross-fitted NWI wetland+PEM species weights: coefficients trained across the full period and reused **without refit**; current analysis is therefore a **retrospective year-stratification, NOT an independently chronological crossfit**.
- Reproduce the previous signed pair covariance residual using an independent deterministic weighted Curveball simulation with 199 draws per matrix, burn 40*n_taxa, thin 8*n_taxa, fixed seed 2840293. Preserve species-row counts and site-column richness; verify generated margins and observed matrix C-score. No changing buffers, taxa labels or sampling thresholds to rescue outcomes.
- Species complexes remain in each entire species-by-stop matrix and associated nulls; only fully resolved taxon names are tested as nodes.

## Year-stratification and formal decision

Year strata: **early = 2001–2009 inclusive**, **late = 2010–2015**. Year labels come from source Runs.csv and must match `RunID`.

Eligibility for *early* discovery: ≥30 pair-active runs, ≥12 distinct routes, ≥10 pair-active runs with variable weighted-null overlap.
Year-early discoveries: route-clustered CI excluding 0, BH q<0.05 across all eligible early pairs, same sign in geographic route folds A/B (require at least five pair-active runs per fold).

Independent response holdout *conditional on previously frozen environmental coefficients*: Late sample eligible ≥40 pair-active runs, ≥15 routes and ≥10 null-variable pair runs. Evaluate only early-discovered links, with route-clustered signed effect, its CI, fold signs, and BH q **across all eligible early-discovered links evaluated in late data**. "Temporally persistent association" requires consistent sign and nonzero late CI, late BH q<0.05 and consistent geographic A/B signs. This **cannot** be called independent model validation: the underlying first-order NWI coefficients were previously trained across early and late years.

Also report year-specific direction and 95% CIs of the **three fixed motivating pairs**, regardless of discovery eligibility:
1. *Hyla versicolor* × *Lithobates clamitans* (both previously positive PEM-associated; joint CI1–3 negative);
2. *Lithobates catesbeianus* × *Lithobates clamitans* (strongest prior CI1–3 and CI2–3 positive);
3. *Anaxyrus fowleri* × *Lithobates clamitans* (previously supported negative under CI1–3 and CI2–3).
Do not pick replacements if one fails.

## Plant context modification

For a run with at least **2 PEM-overlapping** and **2 non-overlapping** surveyed stops, and pair i,j both detected somewhere in the run, calculate

`delta_PEM = [joint positive-stop proportion of pair i,j within PEM-overlap stops] - E_NWI,null[same proportion]`

and `delta_nonPEM` likewise, using the EXACT same fixed-margin MCMC draws and observed row/column margins. Per-run moderation contrast `delta_PEM - delta_nonPEM`. This identifies whether the leftover pairwise association differs between site vegetation contexts **within a route-night**, after species first-order mapped PEM response is represented; it does not prove plants caused the pair relationship.

Plant-moderation test eligibility: ≥30 mixed-PEM pair-active run matrices, ≥12 distinct routes, ≥10 mixed matrices where the null contrast varies. Compute route-clustered mean contrast, 95% CI and two-sided p; BH q across **all** eligible resolved pairs. Call a "PEM-context candidate" only if adjusted q<0.05 and both geographic folds' moderation means share the sign. All taxon-pair results, not only 43 preidentified prior edges, enter this multiplicity family. Report the fixed three motivating pairs separately even when ineligible.

Do NOT interpret a negative moderation contrast as competition or a positive contrast as facilitation; both can arise from unmeasured water depth, predator fish, aquatic macroinvertebrates, sound masking and temporally mismatched NWI maps.

## Gates

- If primary run count !=3659 or strong !=1766, abort.
- If source survey-year values absent, duplicated or not in 2001–2015, abort.
- Synthetic QA checks: exact margins, pairwise signed covariance, deterministic reproducibility, positivity of available PEM group counts.
- If insufficient early/late or mixed-PEM tests, report low power/coverage, never an absence of a biological effect.
- Save complete pair-level and focal-pair evaluation with source hashes, workflow SHA, and interpretation limits; no user-approved field action is performed.
