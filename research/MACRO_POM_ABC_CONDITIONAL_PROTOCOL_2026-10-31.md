# Macro pattern-oriented comparison + conditional ABC pilot, 2026-10-31

## Goal and methodological distinction

Select which **hypothetical stage-structured scenario(s) best reproduce multiple observed NAAMP macro patterns**, not prove that the trophic mechanism occurs in nature. The earlier PR #145/#146 held-out call-prediction competition against environmental models addresses an **additional, stricter predictive/identifiability question**; it is not a necessary threshold for *descriptive pattern-oriented modeling* (POM). Do not erase those negative results, and do not confuse pattern matching with field causation.

This section is declared **after** examining the NAAMP coefficients and previous case-084 results. It is therefore exploratory, not independent confirmation or pre-data model selection.

### Existing data, fixed mechanism candidates

- Exactly 4,248 NAAMP sites / 63,180 completed adult-call surveys; predictor distributions at **these same 4,248 real sites**, not on equal-weight synthetic grids.
- 24 existing, frozen 80-year stage-network candidate surfaces from `literature_extension_20261029`, 3 timing contexts × 2 feeding budgets × 2 behavioral refuge states × frog-postmetamorph→emerging-dragonfly edge on/off. Nine S×nine D density cells × two model vegetation levels; `F_B` is the **synthetic year-start aquatic frog cohort**.
- Site O and S are SDM **relative suitabilities**, not field densities. Site V is 3-km EarthEnv flooded-vegetation composite **positive vs zero**, not measured pond shelter.
- Use identical rank-to-grid transport for all candidates; both `uniform` and `target_group` backgrounds reported **separately**. They are two SDM constructions on the same 4,248 observations, not independent replicate data.

### Why rank-statistics, not a fitted arbitrary calling link

The primary model-derived response is `rank(F_B)`, compared with `rank(observed site strong-call fraction)`, using **the same pooled, unadjusted rank regression** on O, S, V, OS, OV, SV, OSV, with intercept and fixed predictor ranking. This is invariant to a common *strictly increasing* observation transformation. It **does not assert a calibrated larva→male→calling mapping**; absolute acoustic probabilities, prevalence and detection are not simulated. It also avoids each scenario choosing the favorable sign of its own acoustic slope. A fixed positive monotone link may be explored but is not treated as a biological calibration.

**Fitted pattern components** (six dimensions):
1. OS, OV, SV, OSV from the above fixed rank regressions.
2. O–response rank correlation **within lower vs upper halves of the observed S suitability distribution**. Both obs and sim use the same fixed site masks and globally ranked O and response.
Do not force uncertain SV/OSV to be positive, or fix signs to earlier formulations. Weight using observed **56-spatial-block covariance** (999 spatial-block bootstrap draws) with shrinkage regularization; publish raw pattern differences alongside the distance. High correlation across summary components is not counted as six independent biological discoveries.

**Held-out pattern components**, not used to rank cases: O–response correlations on V>0 and V=0 sites; pooled vs within-route coefficient fingerprint, both SDM backgrounds. Report any inability to estimate a pattern due to rank deficiency; never silently substitute another metric or favorable case.

### What is ABC and what is not (phase gate)

- **Phase A** (run now): all 24 *frozen-parameter* surfaces × exact site distribution, observed covariance-whitened pattern distances, paired reverse-on/off ambiguity and pseudo-observation identifiability check under specified synthetic rank-noise assumptions. Label any numerical pseudo-posterior **conditional toy-reference posterior** only, never full biological-model posterior. A strict nearest-pattern ranking is valid even if no model fits adequately.
- **Phase B** (separately): draw *actual biological rates* (predation, growth, maturation, recruitment) from externally justified, source-defined prior distributions and rerun the **true seasonal demographic simulator** for each draw. A prior on rank-transfer, arbitrary outcome noise or grid-interpolation is NOT a prior on predation rates. Do not claim genuine biological ABC model posterior probabilities until Phase B has an actual prior-predictive library, simulation-based recovery tests, and posterior predictive checks.
- During Phase A, allow a modest explicitly labelled **transport-nuisance** prior (monotone O/S proxy-to-grid warp) and stochastic rank-observation noise for **identifiability simulation only**. The point-distance main comparison uses the fixed literal mapping, so priors cannot manufacture a favorable scenario. Pseudo-observation recovery must use independent random replicates and report confusion among *empirically indistinguishable mechanisms*. Exact duplicate `F_B` arrays must be grouped before any scenario ranking probability is interpreted.
- Model selection is **not valid simply by taking the lowest distance**: provide best distance, observed uncertainty, per-pattern mismatches, held-out pattern failure, simulated identification accuracy and explicit `NO_ADEQUATE_SCENARIO` if none passes the absolute posterior predictive check. Do not assert the **probability** that a specific field mechanism is true.
- Predation edge on/off for some cases is numerically identical in prior audits; cannot be called uniquely identified merely because a tie-breaker chose one.

### Numerical and integrity gates

1. Reproduce the existing source-data `macro_common_estimators.csv` for the subset `vegetation=binary, x_transform=rank, y_transform=rank, adjustment=none, mode=pooled` to 1e-8 on OS/OV/SV/OSV, including full sample and correct low/high vegetation rank levels.
2. For each frozen scenario, report exact real-site regression coefficients, O–response correlations within S-low/high, and V-zero/positive holdout correlations. No grid-uniform pseudo-site weighting.
3. Generate 999 clustered bootstrap draws **once** from the observed field response to estimate summary covariance; not independent bootstrap samples for model outcomes. Include fail-closed support and regularization of near-singular covariance.
4. Forward-simulation identifiability: simulate new synthetic response vectors conditional on each frozen source surface under **explicit arbitrary rank-noise levels**; infer nearest mechanism using the common pattern distance. Report raw confusion and group-level recovery; this is a power/identifiability diagnostic **under the stated simulation noise**, not validation on field data.
5. Run in GitHub Actions and commit compact exact score tables, duplicates, rank/correlation diagnostics and receipts with SHA256. Leave original candidate code and full-scale observational records immutable.

**Paper-ready claim ceiling**: “Among the tested fixed-parameter scenarios, X had the smallest distance to a prespecified suite of observed patterns, but several mechanisms were observationally equivalent / absolute discrepancies remained.” The independent meth-eDNA stage and field predation study remains a separate experimental test.
