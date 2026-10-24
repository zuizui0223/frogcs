# The site-history paradox: exact-k identifiability and observed water-change support
**2026-10-24 — NEW mechanism/measurement audit.** No NAAMP `Counts.csv` was opened, no actual amphibian outcome coefficients were fitted/re-fitted. This is a separate research branch; JAE RC6 and `main` are unchanged.

## Formal result: persistent habitat and persistent site states are structurally aliased
For ten monitored acoustic stations, let the strong-calling indicator vector `Y_t` contain exactly `k` ones and
`P(Y_t=y | ΣY_t=k) = exp(Σ_i y_i η_{i,t}) / Σ_{a:Σa=k} exp(Σ_i a_i η_{i,t})`.

Suppose `η_{i,t}=β E_i + U_i + δ_t`, where `E_i` is time-invariant mapped habitat and `U_i` is a completely unrestricted persistent unmeasured site state. For ANY real number `c`, change parameters to `β'=β+c` and `U_i'=U_i-c E_i`. Then `η'_{i,t}=η_{i,t}` **for all observations**. Any route-night common `δ_t` also cancels from the *conditional* allocation likelihood because `Σ y_i=k` is fixed.

**The acoustic allocation alone therefore cannot tell stable habitat filtering from persistent unmeasured site propensity under these assumptions, even with unlimited repeat surveys.** An arbitrary common rain-triggered activity shift may change total chorus intensity `k`; this statement is restricted to its *spatial placement conditional on k*. Constraints on the distribution/independence of `U_i`, direct dynamic habitat observation, manipulations, or spatial transport to novel sites can add identification.

### Numeric verification using real habitat vectors and NO frog outcomes
- SHA256-verified full **USGS Annual NLCD Collection 1.2** 2001–2015 panel: `137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a`.
- Survey-year mean habitat for each physical RouteNumber × SiteID; select first **333** SHA256-ordered routes with exactly ten sites from **1,052** eligible routes. Selection does **not** use acoustic records.
- Set `η_i=2.0 wetland_i + 0.8 openwater_i + U_i`; equivalently `η_i=U_i'` with `U_i'=U_i+2.0 wetland_i+0.8 openwater_i`.
- Enumerate all **45, 120 and 252** possible ten-site configurations at fixed `k=2,3,5` respectively. Maximum observed difference in conditional configuration probability between the two mechanisms was **0** at floating-point precision; adding a uniform weather offset changes probability by at most `2.8×10^-16`.
- These are mathematical identity checks, not ecological evidence that either mechanism is biologically correct.

## How to break the confounding
If `η_{it}=βE_i+γW_{it}+U_i+δ_t`, the dynamic effect `γ` requires water differences that change **differently among sites over time**, rather than simply a spatially constant habitat map or common route-wide shift. A necessary *environmental rank* diagnostic on repeated site/year data is the variation of
`ΔW_i - mean_j(ΔW_j)`, where `ΔW_i=W_{i,t_2}-W_{i,t_1}` is computed at common physical sites during the **same previous calendar month** in two years.

### Empirical JRC data, 2001–2015, strictly environment-only
Full 500-m previous-month JRC MonthlyHistory VER5-0 panel SHA256 `bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b`; **136,194** rows have at least 50% satellite-observed pixels. A zero JRC value is unobserved, **not dry**.

- **3,967** route×month groups with source-observed records; **10,602** adjacent-observed-survey-year comparisons attempted.
- **9,420** pairs from **964 routes** retained at least six identical physical stations with usable imagery at both dates; 1,182 pair comparisons excluded for insufficient common observed stations.
- In 9,420 valid pairs, within-route among-station variation of water *change* exceeded **5 percentage points in 16.13%**, **10 points in 7.14%**; median within-route range of water change only **0.874 percentage points**.
- Retaining only the **first valid adjacent-year pair per route×same calendar month**, n=**2,793**, produced **15.47%** with >=5pp site-specific change.
- Assigning equal weight to each of the **964 routes** gave **14.99%** with >=5pp site-specific change; physical-route cluster bootstrap 95% interval **13.29–16.69%** (1000 resamples; seed 2840223).
- Uniform route-common water shifts are not the relevant identifying contrast for fixed-k placement: a pure constant `ΔW_i=c` has spatially centred variation exactly zero even when water increases.

These environmental observations expose *low rank/support* for testing rapid, **within-site** hydrology × spatial allocation in much of the current JRC series. They do **not** prove hydrology is stable at actual breeding pools: monthly 30-m open-water pixels miss shallow, ephemeral, vegetated and forest-shaded inundation and have seasonally patterned missingness. Even nonzero water spatial change does not by itself remove time-varying detection or latent-state confounding.

## Known-truth instrument experiment — assumptions, NOT real sensor accuracy
Using the same **333 original ten-site habitat layouts** and a *synthetically imposed* event-dated local-water effect `γ=1.5`, generate `W~Bernoulli(expit(-0.5+1.5 wetland+1.0 openwater))` at two synthetic occasions and calculate the full exact-k probability distribution, not sampled calling outcomes. **80 RNG replicates** (seed 2840223); a route-month is completely observed with prechosen probability 0.79 except near-direct regime 0.95.

Simulated classification sensitivities are NOT derived from actual JRC pixels. They are illustrative assumptions. The proxy predictor uses the **posterior-mean plug-in** \`eta_proxy=eta_base+gamma E[W|classified Z]\` (where synthetic Z=0 means *classified non-water*, NOT JRC unobserved-code 0). Because exact-k probabilities are nonlinear, this plug-in is **not the fully Bayes-integrated optimum** \`E[P(Y|W)|Z]\`; the percentages are NOT universal attainable-information ceilings. Comparing the *expected* log-probability improvement of this specified plug-in over a static predictor to a true-water oracle:

| Assumed hypothetical measurement regime | k=3 oracle nats | k=3 proxy nats | Information captured | k=5 captured |
|---|---:|---:|---:|---:|
| Poor under-canopy water detection: sensitivities open water .90, vegetation wetland **.12**, other .55; specificity .98 | +0.516 | +0.165 | **31.99%** | 33.56% |
| Improved all cover types: sensitivity .90, specificity .98 | +0.516 | +0.400 | **77.38%** | 78.38% |
| Near-direct local water: sensitivity .99, specificity .99, 95% complete-route availability | +0.516 | +0.495 | **95.81%** | 95.76% |

The assumption-dependent Monte-Carlo 5th–95th quantiles of captured information for `k=3` were **29.02–35.06%, 74.76–80.22%, and 94.59–97.17%**, respectively. These are NOT confidence intervals for frogs and do NOT calibrate true JRC detection sensitivity. They instead prove a conditional **possibility**: under this known-truth generator, a severe proxy blind spot can hide most of a real dynamic-water contribution even when the water effect is substantial; better event-specific measurement can reveal it.

## Science and decision
1. **Directly proven:** static environment and unrestricted persistent site process are nonidentifiable from conditional acoustic site placement alone.
2. **Measured (environment only):** JRC previous-month water supports >=5pp *site-relative interannual* contrasts in ~15% of equal-route-weighted route/month comparisons. Distinct station water-change contrasts exist, but are sparse and selectively observable.
3. **Shown only in simulation:** artificially limiting water observation sensitivity can reduce recoverable known-truth event-water information from ~96% to ~32% in one controlled parameter setting.
4. **NOT established:** actual water causality, actual JRC sensitivity/specificity, true frog habitat preference, individual site memory/philopatry, social recruitment, simultaneous calling, or independent replication.

**Priority for future field/independent monitoring:** repeat event-dated, *same-site* pond depth/extent under vegetation, record actual water presence and acoustic CI/detection covariates at all ten sites, with repeated near-rain and dry comparisons across different weather episodes; preserve route/time blocked evaluation. A route-wide rainfall change with spatially uniform pond response alone cannot identify a driver of **placement conditional on k**, though it may affect the overall chorus magnitude.

## Execution & reproducibility
- Synthetic proof/test: 333 real environmental route layouts, k=2/3/5 numeric equality; original verified environmental source only.
- Rank analysis/test: original JRC source SHA256, physical-site intersection and same-calendar-month adjacent-year comparisons, >=6 common sites, route-cluster bootstrap.
- Simulation/report/test source and complete replicate-level CSV and 9,420 matched environmental comparisons are distributed in the accompanying **reproducibility ZIP** generated in the conversation. Do not commit large original 26 MB water panel or amphibian source outcomes to the repository.
