# Macro test 2 frozen protocol: within-night frog community beta-diversity across mapped emergent-wetland boundaries

**Created 2026-10-23 before looking at outcomes of this new station-pair turnover contrast.** Independent exploratory endpoint following a **negative** cross-taxon niche-divergence macro test; hence **sequentially generated hypothesis, not independent preregistration**. No literature survey. No changes to JAE RC6 main, SI or manuscript.

## Database and population
Use the **full** original USGS NAAMP standardized ten-stop run data (7,848 source runs) joined to the **previously response-blind, official 12-shard USFWS NWI** crosswalk from Actions run **39450277196**, 5,147 physical sites, no geometry recomputation. Existing source module `exploration/run_naamp_nwi_conditional_checkerboard_v0_1.py::load_run_context()` yields **6,236** complete ten-stop survey-runs with NWI and acoustic-condition QA from ~499 routes. Observe all named NAAMP taxon units, not only the 25 with estimated plant slopes. Original route-stop call records are source observations, not simulated outcomes.

## New biological question
**Within the very same route and sampling night, do locations differing in mapped emergent-wetland (PEM) class carry more different frog calling assemblages than two locations of the same PEM class?**

The test is about **community turnover at mapped vegetation boundaries**, not spatial synchrony, literal frog competition, food-web mediation or plant *causation*. NWI is a static proxy not measured on the historical 2001–2015 night.

## Analysis choices frozen before empirical comparison
- Focus on a complete 10-stop survey where `nwi_emergent_cover_250m > 0` at **≥2 sites** and equals **0 at ≥2 sites**; never treat NWI zero as verified absence of living plants.
- Compute the binary taxon strong/any acoustic call set per stop (same thresholds as original NAAMP). **Primary: any calls, CallingIndex 1–3. Secondary: strong 2–3**.
- For each of 45 possible i<j station pairs with **at least one calling taxon at both stations**, compute Sørensen *dissimilarity* `D=1-2*|A∩B|/(|A|+|B|)`. Pairs with zero taxa at either site are excluded as noncomparability of composition, *not* turned into 0 or 1; this deliberately changes the estimand from all-station calling activity. Record dropped counts.
- Exposure `X=1` for one PEM-overlap, one no-mapped-PEM stop, else `0`. This is a categorical distinction in **mapped emergent polygon overlap**, not species-level macrophyte identity or measured area percent.
- On individual station pairs control (a) absolute stop-order difference (a proxy for geographic distance, imperfect), (b) absolute difference in **total** mapped NWI wetland fraction (scaled to original `v`), (c) acoustic detected-taxon richness difference and (d) mean acoustic richness.
- Demean all predictors and response **within each survey-run** (run fixed effect removes shared date/weather/route-mean). For identifiable runs require ≥10 both-active pairs, ≥2 cross-PEM pairs and ≥2 same-PEM pairs; report excluded runs by reason.
- Fit one shared within-run linear model. Estimate uncertainty by **entire-route clustered sandwich with t(df=unique routes−1)**. All 45 station pairs and repeated site visits on one route are **NOT independent trials**. Report sample counts: source runs, vegetation-contrast runs, valid runs, routes, States, site pairs, species pool and effect on 0–1 Sørensen dissimilarity scale.
- Independent geographic A/B route-fold effect signs are predeclared sensitivity, not fresh causal replication.
- State leave-one-out sign stability (all states with valid runs) and route-equal weighted analysis are sensitivity, not selection of best states.
- **Strict richness-matched sensitivity:** station pairs with `|rich_i−rich_j|≤1`, same full model; can be underpowered without promotion.
- No changing NWI buffer (fixed **250 m**) or turning two silent stations into similarity evidence after looking at results.

## Decision gate (observational)
Call an **"exploratory_macro_boundary_association"** only when the primary route-clustered 95% CI for the cross-PEM dissimilarity coefficient is >0, route-fold A and B coefficients are >0, at least 80% of leave-one-State-out coefficients stay >0 and richness-matched sensitivity retains positive sign. Otherwise **"nonconfirmatory"**. Do not regard this as causal or general plant-mediated frog interactions. No post-hoc latitude trend search if failed.

## QA
- Provenance (runs and station counts) matches original 6,236 run complete-case eligibility.
- No numeric transformation creates 45 new independent replicates from one route-night.
- Binarization checks positive but tiny PEM fraction, not NWI absence.
- Run-fixed within-run predictor/response demeaning correct, tested with synthetic known boundary effect and within-run shifting.
- Original raw USGS and NWI crosswalk not redistributed.
