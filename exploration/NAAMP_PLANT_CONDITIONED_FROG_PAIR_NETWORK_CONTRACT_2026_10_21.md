# Pair-identity acoustic network after null third-taxon test — frozen exploratory contract

Date 2026-10-21. Created after finding **global pairwise squared covariance excess but no robust global third-order excess** in the user-directed NWI-conditioned survey matrices. Hence pairwise species identity is the next fixed test, not a rescue of an unconfirmed three-way mechanism. This exploratory scan is post-hoc relative to NAAMP overall.

## Source
Re-use the exact **3659 CI1–3** and **1766 CI2–3** NWI-covered survey matrices and frozen opposite-route NWI wetland+PEM conditional-logistic coefficients from run **39516056663**, inherited in the already successful three-taxon workflow 39527248267. No training coefficient, NWI cover, route fold, null model or source inclusion change. All taxon units, including species complexes, remain in fixed row/column margins.

## Per-pair outcome
For fully identified taxon names without `/` or ` complex`, pair i,j in a route-run where both taxon units were heard somewhere, the centered co-calling overlap at the same physical stop is

\[
c_{ij}=\frac1{10}\sum_s (X_{is}-p_i)(X_{js}-p_j),
\]

where p_i is that species' observed positive-stop fraction. The deviation \(\delta_{ij}=c_{ij}^{obs}-E_{NWI+fixed-fixed}(c_{ij})\) is a taxon-pair-specific spatial **association** over and above each species' detected-stop count, each stop's total taxa, and route-cross-fit first-order NWI habitat preference. Positive = more same-stop co-calling; negative = more segregation. It is NOT direct attraction, facilitation, competition or simultaneous signaling.

## Sampling and gates
- Use all originally eligible matrices, do not choose subset based on pair outcome.
- NWI+PEM weighted fixed-fixed Curveball MCMC: 199 draws/matrix, 40×n burn-in and 8×n thinning, deterministic seed 2840287; verify every row and column total, observed C-score against frozen reference.
- Each run's taxon-pair coactivation is fixed by observed row sums; eligibility does not depend on actual observed same-stop overlap.
- Test a fully identified taxon pair only if >=60 eligible joint-positive run matrices, >=20 independent routes and >=15 run matrices showing any MCMC covariance variation.
- For each eligible pair fit route-clustered mean signed delta, confidence interval and two-sided P, then BH FDR q across ALL eligible pairs. A pair is a **crossfold-supported candidate** only if q<0.05, route 95% CI excludes zero AND the mean residual has the same sign in fold A and fold B. Do not use P before gates or cherry-pick visually interesting pairs.
- CI1–3 primary, CI2–3 secondary; secondary never replaces a primary-null result. Report both signs, number tested, species degree in supported residual pair network and degree across the five previous BH-positive plant-associated taxon names **only as descriptive overlap**.
- Report the fraction of all pair-run records with non-variable fixed margins and any mixing failures. If null inadequate report unresolved rather than positive.
- If no significant pair survives do not hunt for alternate thresholds/radii.

## Interpretation boundary
Pair-specific residual **network structure is not a trophic interaction network**; shared latent habitat, fish/invertebrate predators, landscape fragmentation, audible masking, taxonomic misclassification and sequential site sampling can explain a residual pair association. These causal layers require direct prey/predator/plant recording or manipulations.
