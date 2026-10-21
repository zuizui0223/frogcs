# PEM-specific frog pair moderation: retrospective falsification receipt — 2026-10-21

## Authority and priority
New exploratory sensitivity, frozen before reading the subset-specific outcomes. Direct continuation of the two already reported **post-hoc** PEM-moderated frog pair candidates. No change to JAE RC6, main manuscript, SI or frozen submission evidence.

## Data and immutable model
- Original source: pinned USGS NAAMP calling counts, dates, ten-stop survey matrices (2001–2015).
- Mapped plant proxy: USFWS NWI 250-m **PEM polygon overlap**, from source-blind validated NWI artifact, Actions **39450277196**. No mapped PEM **does not mean absence of aquatic vegetation**.
- Reference candidate screen: Actions **39592028334**, two BH q<0.05 CI1–3 moderation candidates among 121; 45 eligible mixed PEM runs /20 routes for `Gastrophryne carolinensis || Hyla chrysoscelis`; 34/15 for `Hyla gratiosa || Lithobates sphenocephalus`. Neither confirmed for strong chorus CI2–3.
- Frozen original NWI-weighted fixed-fixed curveball null and opposite route-fold taxon-specific wetland+PEM coefficients: Actions **39516056663**. No re-fitting or reselection of NWI coefficients, source runs, species, radius, threshold or alternative hypotheses.
- All taxa (including complexes) remain in each fixed-margin frog community matrix; the focal association calculations involve two fully resolved species names. The two candidate pairs were chosen from an already *full-period-tested* family. Therefore year-strata analysis is **post-selection descriptive stability**, not an independent chronological validation.

## Core question
Is the reported difference in **residual joint calling** at NWI-PEM-mapped versus other route stops persistent in 2001–2009 and 2010–2015, and is it an artefact of a few states, highly unbalanced 2-vs-8 stop partitions, or survey-run recording intensity?

## Identical estimand and simulation
- Primary response: CallingIndex ≥1 in the original 3,659 matrices, same species/stop row-column margins, only pairs positive somewhere on the route and **at least 2 PEM mapped stops and 2 non-mapped stops**. Never select based on observed joint overlap.
- For each valid run, PEM and nonPEM joint fraction of ten stop observations for each candidate pair; subtract each's expected fraction under NWI species weights + fixed-row/column Curveball. Per-run effect `[(PEM observed – PEM null) − (nonPEM observed – nonPEM null)]`. This is **moderation of signed pair co-calling** on the NWI mapping category, not a causal effect.
- 199 MCMC samples/matrix, 40*n_taxa burn-in, 8*n_taxa thinning, deterministic seed **2840297**. On every matrix verify original observed C-score and exact null-preservation of original species row sums and stop richness. Verify at least 2 distinct simulated pair-moderation values in ≥10 complete matched matrices; report zero-variation cases, acceptance fraction and null distribution.
- Reproduce previous candidate sign and similar magnitude (tolerance ±0.05 raw fraction) on full samples as a **QA check**, not a requirement for discovery. The new seed may change minor Monte Carlo noise.
- Fit route-clustered intercept estimates for full, **2001–2009 early** and **2010–2015 late** periods; report n_runs, n_routes, mean signed moderation, 95% CI, P. Report whether both split means have the original sign and whether each split's 95% route CI excludes 0; do **not** call either a confirmatory replication.
- Within each epoch, report deterministic original geographically disjoint SHA256 route folds A/B signs and coverage.
- Additional predeclared buffer category sensitivity **without changing radius**: restrict original mixed-PEM runs to **≥3 mapped PEM and ≥3 nonPEM stops**; compare the same per-run effect and report CI. This tests sensitivity to highly unequal denominators without selecting the ratio with best P.
- Geographic concentration diagnostic: leave each State out one at a time on the exact eligible mixed-PEM runs. Report coefficient range, how many leave-state-outs retain the direction, and how many retain a CI excluding 0. No selected-state analysis for the headline.
- If either epoch has <12 informative mixed-PEM pair runs / <6 routes, label insufficient for temporal claim. If balanced sample has <20 runs / <10 routes, report insufficient for denominator robustness.
- Strong CI2–3 **pre-existing secondary**: report comparable effect/coverage, never promote to a primary outcome if CI1–3 fails.

## Decision
Classify candidate `stable_noncausal_PEM_context_association` only if:
1. both early/late estimates have the same original sign;
2. both route-stratified 95% CIs exclude 0 in that sign;
3. ≥80% of available leave-one-State-out point estimates preserve sign, **and**
4. balanced sensitivity preserves sign with route-cluster CI excluding 0.

If any requirement is not met: `fragile_posthoc_PEM_candidate` (or `underpowered` when gates fail); do **not** rescue via additional covariates, alternative cutoff or data subset searches.

## Inference boundaries
NWI is static/heterogeneous imagery, not a contemporaneous species-identified aquatic plant census in 2001–2015. Sequential NAAMP listening stops are not repeated simultaneous co-signaling data. Pair overlap is not proof of competition, acoustic attraction, a fish/odonate-predator mediation chain or higher-order network causation. The old NWI filter used data from all years to learn habitat coefficients; apparent epoch persistence cannot be called independent temporal replication. No RC6 paper/claim change.
