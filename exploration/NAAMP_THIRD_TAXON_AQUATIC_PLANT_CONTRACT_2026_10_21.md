# Third-taxon acoustic organization and aquatic plants — frozen exploratory v0.1
2026-10-21; new user-directed question, **separate from closed JAE RC6**.

## Question
Beyond taxon-specific associations with mapped emergent wetland habitat, does the *identity of triples of calling frogs* show non-random placement not reproduced by the already cross-fitted vegetation-conditioned fixed-margin generator? Is that excess concentrated near mapped emergent vegetation or in identifiable taxon "hub" roles?

## Crucial distinction
The previously demonstrated `within-taxon multi-stop higher order` is **not** the same as **three-taxon** co-calling. We test third-order *co-occurrence geometry*, not a causally irreducible higher-order interaction. Pairwise frog–frog interactions, unmeasured environment, observation/detection coupling and species' individual habitat responses can all create centered third-order moments. Do not name a network edge as competition or facilitation without intervention.

## Frozen inputs and sample
- USGS NAAMP Runs/Stops/Counts with existing pinned hashes. Primary CallingIndex≥1, secondary CallingIndex≥2.
- Existing site geometry and USFWS NWI 250m fraction (static PEM emergent and total mapped wetland), source-only 12-shard NWI crosswalk, [Actions 39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Prior species-specific **route-held-out wetland + PEM** fixed-k coefficients and original per-run baseline fixed-fixed C-score, *unchanged*, [Actions 39516056663](https://github.com/zuizui0223/frogcs/actions/runs/39516056663). Import frozen `any_train_coefficients.json`/`strong_train_coefficients.json` and `any_heldout_run_diagnostics.csv`/`strong_heldout_run_diagnostics.csv` plus the 399-draw baseline reference from [Actions 39436588431](https://github.com/zuizui0223/frogcs/actions/runs/39436588431).
- Same complete route-run set: at least three positive taxa, at least two with two or more detected stops, at least three active stops, exchangeable fixed row/column margins. Any change to run membership or observed C-score = abort.
- Test all previous matched NWI-covered route runs, no selecting significant species or observed high triad scores. Do not refit habitat coefficients.

## Statistic and invariance
For each detected taxon i and sampled stop s, \(X_{is}\in\{0,1\}\). Fix taxon-specific detected-stop mean \(p_i\).

Primary third-order identity-sensitive statistic:
\[
 T_3=\operatorname{mean}_{i<j<k}\left[\frac1{10}\sum_{s=1}^{10}(X_{is}-p_i)(X_{js}-p_j)(X_{ks}-p_k)\right]^2.
\]
This is a squared *centered third co-calling moment* averaged over unordered taxon triples; it is not simply `choose(stop richness,3)`, which would be **exactly invariant** if stop richness is fixed. The third centered moment removes the direct product of first means and pairwise lower-order terms algebraically, but a nonzero excess **does not** establish a causal three-body interaction or exclusion of pairwise-only generators.

Two frozen companions:
1. Pairwise benchmark \(T_2=\operatorname{mean}_{i<j}[\overline{(X_i-p_i)(X_j-p_j)}]^2\).
2. PEM-localized triplet score \(T_{3,E}=\operatorname{mean}_{i<j<k}[\overline{(E_s-\bar E)(X_i-p_i)(X_j-p_j)(X_k-p_k)}]^2\), where \(E_s\) is NWI 250m emergent **fraction**, not a species-level aquatic macrophyte census.

To test which taxa are unusually represented in residual three-taxon configurations, compute for taxon i the average squared moment of triples containing i, and compare to its own weighted-null expectation on **identical route-runs**. Only test taxon units with ≥80 qualifying runs, ≥25 independent routes and ≥20 runs with nonzero simulated T3 variance. Benjamini–Hochberg q across all taxa eligible by those counts; no name or taxon is preselected based on existing PEM BH results. Require an excess whose route-clustered CI excludes zero, **both route folds positive**, and BH q<0.05 before calling a *candidate* network hub.

## Fixed null and inference
- NWI wetland+PEM weighted Curveball proposal with exact fixed row AND column sums, already route-cross-fit trained coefficients frozen prior to this new test.
- 199 MCMC draws per complete survey-run matrix, burn-in 40×detected taxa, thinning 8×detected taxa, new deterministic seed 2840279.
- Compute observed and null T2, T3, T3,E per identical matrix; global mean observed-minus-weighted-null and route-clustered 95% CIs; global plus-one directional MC upper-tail P (minimum 0.005), both folds separately.
- At least 100 matrices and 30 routes (per primary). At least 100 matrices with variable T3 under the null; fewer means *coverage-inconclusive* for higher-order geometry even when simulation technically passes.
- Verify original observed C-score and baseline matrix membership. Verify every generated row/column margin at randomly selected draws. Compare T2/T3 together; if both depart, do NOT claim genuine higher-order interaction beyond pairwise edges.
- If ≥20% of originally exchangeable/informative matrices cannot explore T3 and fewer than 100 vary, mark insufficient identifiability; report deterministic T3 cases separately.
- Species roles are post-hoc exploratory **signals for follow-up**, not real-time causal ecological network links.

## Boundaries and future experiments
Observational NAAMP listening stops were visited sequentially; co-detection at one stop on the same survey night is **not simultaneous acoustic signaling**. The time-mismatched NWI polygons, unmeasured predator fish/insects, water depth and actual plants, detection bias and site history remain unresolved. Without insect/fish survey, trophic paths like plant → insect predator → frog are a literature-backed hypothesis, not tested in the NAAMP dataset.

No RC6 files modified; all results stay on an independent exploration branch.
