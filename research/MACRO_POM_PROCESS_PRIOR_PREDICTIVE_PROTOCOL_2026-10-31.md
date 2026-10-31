# Prior-predictive simulation of biological model-rate uncertainty (2026-10-31)

## Purpose

**Primary goal remains pattern reproduction:** compare mechanisms that generate the observed multi-site NAAMP O–S–vegetation (OS, OV, SV, OSV) signatures and conditional O association at low/high S. This is the next step after the frozen 132-case POM audit, not an independent untouched validation.

Unlike the earlier conditional toy ABC, **every parameter draw actually reruns the unchanged 120-day trophic kernel and 80-year delayed-recruitment model**; no perturbation of precomputed F_B surfaces masquerades as demographic variation.

## What the cited evidence actually licenses

- Beranek et al. (2023), *Ecology*, DOI [10.1002/ecy.4108](https://doi.org/10.1002/ecy.4108), documents a frog–dragonfly reversed predation **event and stage**, not site-wide prey consumption per adult per day or an attack-rate distribution.
- Kishida et al. (2009), *Ecology*, DOI [10.1890/08-0238.1](https://doi.org/10.1890/08-0238.1), documents a three-guild risk-mediated response and modified offense, not transportable wetland-scale hazard coefficients.
- A study of *Rana temporaria* (2002), DOI [10.1078/1617-1381-00011](https://doi.org/10.1078/1617-1381-00011), documents links of metamorph production to recruitment **two or three years later**; this motivates the discrete F maturity-lag sensitivity.
- Evidence in the local research files is qualitative for the remaining predation and life-stage effects. The studies are **species-, region- and setting-specific**; extrapolation to an assemblage of North American frog species and SDM proxies cannot be called calibrated.

Thus the following are **explicit exploratory process-parameter uncertainty ranges**, **not literature-estimated probability distributions**. We use one deterministic Latin hypercube over continuous intervals and a separately balanced discrete lag. This is prior-predictive hypothesis stress testing; the resulting ABC-like acceptance fractions are conditional on these declared ranges and do not estimate the probability that a field mechanism is true.

## Exact model ensemble, fixed before inspection

Use 3 stage/size cross-over contexts (`original`, `D_first_S_overtakes`, `S_first_D_overtakes`) × 2 handling budgets (`baseline`, `shared_both`) × 2 behavioral risk-refuge settings × 2 F postmetamorph→D emergence edge settings = **24 structural hypotheses**. A small, computationally bounded pilot uses **8 matched process-parameter draws** shared by all 24 structures; full 2×9×9 model source grids, 80 years, annual last-20-year mean, seasonal dt=0.25 days. Same original F/S/D source densities and model equations; no parameter is optimized on field patterns.

| Drawn parameter | Range | Interpretation / limit |
|---|---|---|
| `attack_scale` | log-uniform 0.25–1.0 | dimensionless **global** scaling of existing simulated attack hazards; literature does **not** give these numeric bounds |
| `s_growth` multiplier | uniform 0.75–1.25 | relative to the context's synthetic S size growth |
| `d_growth` multiplier | uniform 0.75–1.25 | relative to the context's synthetic D size growth |
| `rho` | uniform 0.55–0.90 | synthetic local return/migration mixing, **not measured** dispersal |
| `conversion` | uniform 2–6 | synthetic density-dependent reproductive scaling, **not eggs/female** |
| `juvenile F survival` | uniform 0.60–0.90 | undetermined effective immature carryover in the annual equation |
| `adult F survival` | uniform 0.25–0.60 | undetermined yearly survival in the annual equation |
| `F maturity delay` | equal 2 or 3 model-years | stage-age sensitivity motivated by *Rana temporaria*, **not established across NAAMP frog taxa** |

All S and D demographic constants, 120-day kernel, fixed vegetation refuge functional response, source densities and initial cohorts retain their original default values. **No derived inference about stage reversal rates** is possible from the one global attack multiplier; reversal OFF/ON is structural.

## Checks and analysis outputs

1. **Baseline source replay gate:** rerun the original 24 structural cases with published 2026-10-29 baseline parameter values (attack .5, `rho=.75`, unchanged growth, conversion 4, F juvenile=.8, survival=.4, delay=2) and reject the entire run if the new complete F_B grid fails 1e-9 comparison to the archived two `primary_{0,1}_dynamic_cells.csv.gz` sources. Test both reversal ON/OFF rather than assuming the sensitivity model matches the original.
2. **Actual model draw:** each of 8 prior rows is passed to the real `stage_network_extension_20261029.simulate` via `extension_annual_summary_20261029.summarize_years`, propagating all annual cohort states. Batch by risk; keep the full 24×8×162 source cells and source receipts as an Actions artifact. No ABM/PDE.
3. **Identical POM estimands:** 4,248 real locations and same six rank-based observed patterns, fixed observed 56-block covariance and all 4 additional unused-in-selection patterns, both SDM backgrounds. Report per-pattern residuals, minimum distance and 6/6 matches by structural family.
4. **Scenario selection diagnostic:** for each draw and hypothesis, score distance to observed patterns. Report best-of-tested configuration, class×parameter uncertainty and whether full 6-pattern interval coverage is reached. A low distance alone is **not** adequate fit.
5. **Leave-one-parameter-draw-out pseudo-recovery:** each artificial target is a simulator-generated response at one parameter draw. Competing candidates may only use the *other* 7 draws. Report 24-class (and reversal-collapsed 12-class) confusion. This is not posterior predictive verification against real frogs.
6. **Conditional ABC-like acceptance:** top 10% of observed-to-prior-simulated distances with equal matched draws per class; report **acceptance share under declared exploratory ranges**, **never** biologically calibrated scenario posterior.
7. **Stopping rule:** if the source baseline fails, no real-world coefficient comparisons are reported. If no draw fits all patterns, `NO_ADEQUATE_PRIOR_PREDICTIVE_SCENARIO_IN_TESTED_HYPOTHESIS_RANGES`; do not widen intervals after looking merely to force success.

Prior predictive sample size (8) is a computation feasibility *pilot*, not a converged ABC posterior. Later rate-prior refinement requires independent attack-rate, maturation and pond-stage observations plus more draws and explicit convergence; a favorable pilot draw cannot be promoted to a species-wide ecological conclusion.
