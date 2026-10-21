# Plant-conditioned frog acoustic pair network — exploratory contract (2026-10-21)

## Ecological question

The user asks whether apparently unrelated organisms form a hierarchy of biotic interactions: mapped emergent vegetation ↔ macroinvertebrates/fish ↔ frogs ↔ acoustic community. External literature supports possible cross-trophic mediation, but **NAAMP did not measure fish, aquatic insects, water depth or predator occurrence at these exact frog observation nights**. No trophic edge can be empirically established from the current NAAMP+NWI crosswalk.

**Testable intermediate layer:** after species' plant-related acoustic site preferences and all row/column calling margins are represented, do particular pairs of frog taxon units *still* preferentially overlap or avoid one another in ten-stop acoustic survey matrices?

This is a new hypothesis and outcome readback under a distinct exploratory branch. It does not reopen or update the JAE RC6 manuscript.

## Frozen data and generator

- Original pinned USGS NAAMP standardized 10-stop monitoring runs.
- Full geometrically vetted 12-shard USFWS NWI 250-m polygon fractions (501 successfully mapped routes; source artifact from workflow 39450277196).
- Model weights taken **without refitting** from the previously completed, route-cross-fitted species-specific **NWI total-wetland + PEM** fixed-k conditional model (workflow 39516056663; `strong_train_coefficients.json`). Opposite route fold only, same predetermined fold hash.
- Primary calling endpoint: CI≥2; use exactly the subset of previous strong-calling fixed-margin matrices with all ten fully linked NWI/stop conditions (expected 1,766 matrices, 398 routes). No selecting frog taxa by BH significance.
- Both **taxon-by-run positive stop totals** and **observed total taxa per listening stop** remain identical under every null matrix.
- Curveball weighted symmetric proposals, Metropolis acceptance. 199 draws per matrix, fixed burn-in 40×n_taxa and thinning 8×n_taxa, seed 2840279, deterministic run ordering. Cross-fitted coefficients unmodified. Verify preservation of both margins and identical observed run C-score against existing strong-run frozen reference.

## Predeclared pair statistic and eligibility

For every jointly recorded taxon pair (a,b) within the same route-run, let \(S_{ab}=\) the number of the same ten stops where CI≥2 is heard for both; compute \(E_{PEM}(S_{ab})\) under the NWI weighted fixed-fixed null and \(E_W(S_{ab})\) under a wetland-amount-only fixed-fixed null.

- Primary network edge weight is the mean (across all matched route-runs in which both taxa were detected) of \(S_{ab}-E_{PEM}(S_{ab})\). Positive means excess acoustic sharing; negative means relative segregation. This is a *conditional acoustic spatial association*, not actual ecological facilitation/competition.
- To test any pair, require **at least 30 jointly detected route-runs, at least 15 independent State:RouteNumber routes, and at least 10 matrices with nonzero overlap-simulation variance**. Eligibility is predeclared and cannot change in light of coefficient signs or nominal p.
- Exclude a pair if a monitoring species-complex label explicitly contains the other individual species label (e.g. `Hyla versicolor` and `Hyla chrysoscelis/versicolor complex`), because classification aliases could induce artificial interactions. Retain other taxon complexes, but label them as taxon units rather than independent biological species.
- Fit intercept-only route-clustered robust models for eligible pair residuals and for plant increment \(E_{PEM}(S)-E_W(S)\), with 95% CI.
- Correct the **primary residual** two-sided p-values across every eligible pair with Benjamini–Hochberg FDR 0.05. Plant increments are descriptive and do not define a second list of discoveries.
- All eligible pairs must be reported including null/negative results; include cumulative counts, which taxa have supported positive/negative network edges and their route/sample coverage. If no eligible pair or no FDR-supported pairs, report that as the result.

## Diagnostics and interpretation

- Before any outcome readback, synthetic 2×2 weighted Metropolis test and exact row/column-marginal conservation must pass (reuse original immutable test, verify deterministic pair overlap calculation).
- Reject a claim if >20% of matrices whose fixed-margin null C-score was informative have <2 distinct simulated C-score values or if any margin changes.
- Report simulation acceptance rate and original frozen C-score equality.
- The pair network is **not a trophic network**: links represent conditional similarity of *detected strong calling across NAAMP listening stops*, with no measured dragonfly, fish, mosquito, bird or plant species co-occurrence. Even a negative edge cannot establish competition, since route-order, small wetlands, microhydrology, imperfect detection, phenology and conspecific recruitment may create residual patterns.
- Species complexes/phylogenetic nonindependence and within-night sequential rather than simultaneous ten-stop surveys are explicit limitations.
- A multi-trophic explanation requires co-sampled habitat structural traits, predator fish presence, odonate larvae, tadpole or egg survival, exact acoustic location/perch and water depth **at the same microhabitat and date**. Public EPA NWCA 2011 supplies plant/hydro/chemistry measures but not a response-aligned NAAMP fish-odonate-amphibian census; do not join arbitrary distant sites as if co-observed.

## Output
- Complete per-pair count and effect ledger, all eligible and FDR results;
- Run-level conditioned observed/null shared-stop ledger;
- JSON scientific synthesis separate from RC6;
- Reproducible GitHub Actions execution, source artifact IDs and QA.
