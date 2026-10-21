# Same-route-run partner-dependent frog acoustic site allocation — exploration contract
Frozen 2026-10-21, separate from JAE RC6.

## Scientific question

Does the strong positive joint acoustic overlap of `Lithobates clamitans` with `L. catesbeianus` and its negative overlap with other taxa persist **within the very same 10-stop NAAMP route-run**, when all three taxa were heard somewhere on that route-run? The earlier pair edges used distinct geographic/survey samples and could reflect nonoverlapping community contexts. This test conditions on the SAME night, route, season, species set, NWI 250m wetland+emergent cover and species/site activity margins.

Focal unordered triples fixed by previously identified network, before inspecting triple-eligible outcomes:
- C = `Lithobates clamitans`, positive partner P = `Lithobates catesbeianus`, negative partner N1 = `Hyla versicolor`.
- C = `Lithobates clamitans`, positive partner P = `Lithobates catesbeianus`, negative partner N2 = `Anaxyrus fowleri`.

**This compares two pairwise relations in a common survey, not an irreducible three-body interaction.** A third taxon's presence merely defines an identical ecological context for both pair tests.

## Frozen input and gates

- Full source-blind NWI overlay, USFWS mapped emergent `PEM`, Actions `39450277196`.
- Original **same** 3659 CI1–3 primary / 1766 CI2–3 secondary survey matrices, previously validated by observed run-specific C-score, Actions `39516056663`.
- Original species-specific wetland + PEM conditional-logistic coefficients, trained on **opposite geographic route fold**, frozen in `naamp-nwi-route-crossfit-weighted-checkerboard-v0-1` artifact. The model was trained over BOTH year periods; this is NOT independent early-trained/late-tested confirmation.
- Include run if all C, P, N have >=1 positive calling stop (for each calling threshold) and all ten plant data are present. This *eligibility is determined by single-taxon positive row totals*, never by pairwise spatial overlap.
- Preserve every detected taxon's positive-stop count and every listening stop's frog species richness exactly, including nonfocal species and complexes. Verify the already frozen original observed C-score for all selected runs.
- Do not relax the triad definition, calling threshold, NWI buffer, source period, or model after seeing results.

## Per-run statistics

Let `c(C,P)` and `c(C,N)` be the centered site co-call covariance `mean_s[(X_C-p_C)(X_partner-p_partner)]`. Both share exactly the same ten stops (a single route-run).

Use the cross-fitted NWI-weighted fixed-row/column Curveball null to estimate
`e(C,P)=c_obs(C,P)-mean_null c(C,P)` and similarly `e(C,N)`.
The paired signed **partner-switch contrast** is
`D=e(C,P)-e(C,N)`.
Record `e(C,P)`, `e(C,N)`, `D` *per route-run* and its weighted-null variability; C-score under prior baseline must match identically. `D>0` only demonstrates different residual pair allocations in the same survey context; it cannot identify attraction/competition and can still be influenced by a time-varying species-specific habitat factor.

## Frozen inference

- Fixed NWI-weighted Curveball, 199 post-burn draws per qualifying matrix, burn 40×taxon count, thin 8×taxon count, deterministic seed `2840301`, no species coefficient re-fitting.
- Primary CI1–3: each focal trio needs >=60 qualifying route-runs, >=25 distinct routes and >=20 qualifying runs with nonzero null variance for D to be statistically interpretable; else `insufficient_sample`. Secondary CI2–3 same *descriptive* thresholds, never replaces primary.
- Route-clustered OLS intercept estimates, 95% CI and two-sided p for e(C,P), e(C,N), D. BH q across **two** fixed primary trio contrasts, including all statistically estimable trios. Require q<.05, lower CI(D)>0, e(C,P) lower CI>0, e(C,N) upper CI<0, and positive D in both geographic route folds to call a `supported_within_run_partner_contrast_candidate`.
- Pre-specified retrospective 2001–2009 and 2010–2015 splits; report means, clustered 95% CI only when >=20 runs and >=10 routes in a split. If either split underpowered, temporal persistence `unresolved`. Full-year first-order coefficients contain both eras.
- Leave-one-State-out D direction audit whenever ≥3 observed States, with no cherry-picking. Report number of State removals preserving D>0 and signed CI; classify `geographically_fragile` when <80% preserve positive sign.
- For each focal trio, report within-run PEM mapped exposure variance and sample extent. A three-taxon joint observation is **not a direct simultaneous call interaction** because NAAMP ten stops are sampled sequentially.
- 199 null draws imply Monte Carlo variability; inferential CIs are route-clustered for the per-run paired contrasts. A significant D is not biological causation.

## Expected interpretations

- If D>0, both residual edges have opposite signed CIs and this holds across route folds, evidence for **partner-specific spatial organization** beyond first-order NWI habitat sorting survives identical night/route comparisons. Does **not** show true higher-order interspecific effects.
- If positive D but either edge fails signed CI: relative differences alone, do not assert contemporaneous simultaneous coexistence/exclusion.
- If no identifiable same-run sample: prior separate-pair edges remain descriptive but cannot establish within-community partner switching.
- If D fails: geographic/seasonal composition may underlie the seemingly opposite network edges.

Do not edit `paper/`, `submission/`, SI, or RC6 freeze.
