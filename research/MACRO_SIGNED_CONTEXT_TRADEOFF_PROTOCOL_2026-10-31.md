# Post-result sign-constraint lattice and minimal incompatibility audit (2026-10-31)

The just-completed **4,248-site directional context** evaluation found that the field supported negative **OS, OV, ΔS (high − low S O–call correlation)** and **ΔV (flooded-vegetation-positive − V=0 O–call correlation)** at a 90% whole-spatial-block bootstrap direction frequency. No frozen 132 case, and no one of the 8×24 genuine 80-y demographic-rate configurations, matched all four.

This follow-up is explicitly a **post-result diagnosis** of which *subsets* of directional constraints cannot coexist under current models. It is not a new model-selection criterion and cannot be called independent confirmation; no model, coefficient, rate range or observational sign target is modified.

## Inputs and reproducibility
- The audited full per-case directional output and source SHA receipt from successful [signed-context Actions #41166641637](https://github.com/zuizui0223/frogcs/actions/runs/41166641637).
- The full independently simulated eight-parameter ×24-structure `process_prior_predictive_patterns.csv` from successful [80-year simulator Actions #41163370575](https://github.com/zuizui0223/frogcs/actions/runs/41163370575). This already includes OS, OV, O–call correlation S-low/high, and flooded vegetation strata. Verify that its differences reproduce the signed-context diagnostic ΔS/ΔV for every candidate/background/draw, not just by case labels.
- Two SDM backgrounds; **same** NAAMP site cohort. No new pseudo-sites or outcome-dependent rank mapping.
- The previously frozen exact-source response groups (104 out of 132 labels) are counted only once when talking about independent **source outputs**, without treating groups as statistically independent biological hypotheses.

## Fixed audit
1. Enumerate all non-empty subsets of `{OS−, OV−, ΔS−, ΔV−}` (15 sets). For each background, count **a)** fixed 132 case labels, **b)** fixed distinct source response groups, **c)** genuine eight-rate ×24-case parameter configurations whose *deterministic* signs simultaneously agree. Every source row must be counted in exactly the same catalog and both backgrounds.
2. Identify **minimal incompatible subsets**: a subset with zero candidates for which *all proper non-empty subsets have at least one candidate*. A pair with zero while both singletons succeed is a sharp diagnostic of model structure, stronger than simply observing a failure of four terms.
3. Reapply the **90% and 95% observed bootstrap sign-frequency cutoff** without changing the fitted models. At 95%, uncertain target-group constraints may disappear; report which, and the cross-background count of cases satisfying each background's chosen constraints.
4. Report chance comparisons only as **catalog proportions and independent fair-sign combinatorial references**, not p-values; source response surfaces share model equations and thus are not independent random signs.
5. Keep `OV`/ `ΔS` conditionals as observed correlations in **SDM suitability** rather than local density, and `V>0` as remote landscape proxy; no causal trophic identification.

## Scientific decision

If `OV− & ΔS−` is unachievable among all existing candidates for a given background, then **the current family of stage timing, shared handling, behavioral refuge and reversed predation mechanisms does not jointly generate the observed direction of both associations** at the tested parameter range, despite other single/pair patterns potentially matching. A separate ecological mechanism would need to be framed as a falsifiable candidate with independently motivated biology and tested against **both** signs—not engineered to fit this one contrast. Actual salamander abundance, predator encounters, larval timing and colonization remain necessary to infer field cause.

All results must be committed as a compact table and referenced in Draft PR #146. No changes to `main`, PR #144/145 or frozen kernels.
