# Frozen exploratory ecological macroanalysis: within-year temporal β-diversity turnover versus nestedness in mapped PEM wetlands

Date 2026-10-23. Frozen before running this *new* NAAMP acoustic temporal composition endpoint. The user requested ecology and vegetation hierarchy rather than prediction or literature surveys. This analysis is observational and **post-hoc on the already multiply analyzed USGS NAAMP × NWI archive**; the new six-test family is fixed before its result, but it is NOT an independently preregistered confirmation. Frozen JAE RC6 scientific paper, SI, main and submission untouched.

## Scientific question

At identical physical wetland stations repeatedly acoustically surveyed within the same calendar year, does **taxon replacement between calling windows**, as distinct from **differences in the number of detected taxa**, depend on mapped 250m USFWS NWI PEM/emergent wetland class? Prior robust empirical results established (a) positive PEM-local taxon richness, (b) higher absolute two-round acoustic gamma taxon complementarity, and (c) larger added gamma from another round rather than another station, but neither a robust PEM pair-identity acoustic network nor a differential spatial×temporal gamma cross term. A higher absolute acoustic bonus could arise simply because the underlying PEM taxon pool is larger. Here the primary endpoints are **compositional dissimilarity normalized to taxon pool size**, partitioned into turnover and nestedness-resultant components.

## Immutable source and hierarchy

- Use exactly the already verified 7,848 standardized USGS NAAMP 2001–2015 surveys, 6,236 complete NWI/air/sound ten-stop nights, original 5,147 physical USFWS NWI SiteIDs from 12 response-blind GIS shards, 499 geographic routes/20 States.
- Reuse unchanged `source()` and `build_rounds()` of `exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py`: the previously audited **2,869 survey visits from 1,115 distinct physical route×year groups on 274 routes/20 States**, exact same ordered SiteIDs across visits, no duplicate annual rounds, at least 2 PEM stations and 2 nonPEM stations inside mapped total wetland footprint. Retain original CI≥1 and CI≥2 taxon labels (including complexes) and acoustic zeros. No selection by observed frog richness.
- For every route-year, enumerate all **2,475 unordered round pairs** across R=2..4 original within-year `RunNumber` values, then average **within route-year first** and **within physical route second**. Taxon group PEM+ versus other wetland PEM0 is static mapped polygon overlap, not actual 2001–15 measured live plant cover.
- **Matched sampling:** exactly m=2 of the same physical wetland stations chosen uniformly without replacement in each plant class, and the same two monitoring rounds for both classes. nPEM and nOther may differ; analytic expectation over every possible pair of physical sites, **no stochastic Monte Carlo resampling of taxa, source stations or target years**.

## Exact incidence-based temporal dissimilarity

For each two-round site pool within habitat h, call the expected acoustic taxon count at early survey `g_e`, later survey `g_l`, and union across BOTH surveys `g_U`, computed using the previously verified exact hypergeometric same-site two-round function `exact_two_round_pool(...,m=2)`. Taxon-labelled expected overlap components under uniform m=2 physical stations are:

- `a=g_e+g_l−g_U`: expected acoustic taxon labels heard in both rounds' **pooled m-site sets**;
- `b=g_U−g_l`: expected labels heard only in the earlier round;
- `c=g_U−g_e`: expected labels heard only in the later round.

All nonnegative up to floating-point tolerance; direct `g_U=g_e+g_l−a` and `B=(b+c)/2` must agree with the previous exact acoustic temporal bonus. These are **expected counts**, not actual local species colonization/extinction.

Define source-stable **ratios of expected component counts**, explicitly NOT the expected value of individual sub-sample Sørensen/Simpson indices:

- `β_sor=(b+c)/(2a+b+c)`;
- `β_sim=min(b,c)/(a+min(b,c))` (turnover/replacement component);
- `β_sne=β_sor−β_sim` (nestedness-resultant component due to unbalanced numbers of taxa heard);
- `J=(b+c)/(a+b+c)` Jaccard as an optional descriptive normalization and `B/g_U=J/2` exact check when gU>0.

**Primary and all five formal secondary tests use the SAME two-round source pairs for which both mapped vegetation classes each have nonempty expected acoustic taxon pools in BOTH rounds, and both Simpson denominators are >0.** Never set undefined beta values to 0, 1 or NaN then hide dropped groups. Describe exclusion counts for each call threshold at round-pair and route-year/route/State grain; round 4 sampling is sparse (6 states). For comparison, report the full original geography-only opportunity denominator of 2,475 pairs and a descriptive Sørensen estimate over "any taxon in either round" when one round is silent but union nonempty, with separate both-silent counters; this latter is **not** used to select a more favorable formal endpoint.

On included habitat-comparable pairs, require `β_sor = β_sim+β_sne` to ≤1e-10. Treat source contrast `Δindex=index_PEM−index_otherwetland` per actual round pair and outcome. Average all valid pairs within the original route-year, then each route-year within physical route; do not count site subsets, stations, observation windows, taxa or route-years as independently sampled inference clusters.

## Pre-fixed six-test family and decision gates

1. **Primary:** `Δβ_sim_any` — difference in the **replacement** component of acoustic taxa between rounds.
2. Secondary `Δβ_sor_any` — total temporal acoustic community dissimilarity.
3. Secondary `Δβ_sne_any` — nestedness-resultant dissimilarity.
4. Secondary `Δβ_sim_strong`.
5. Secondary `Δβ_sor_strong`.
6. Secondary `Δβ_sne_strong`.

All are **two-sided**, with no predeclared favorable sign. For each: equal physical-route mean, Student-t(df=G−1) 95% interval, two-sided P, **4,999 whole-route Rademacher sign flips**, Benjamini–Hochberg q across all six, equal-State mean and Student State 95% interval, State sign counts and all 20 leave-one-State-out signs/range. Require at least **150 eligible route-year groups, 50 physical routes and 5 States** after the fixed both-active conditioning for BOTH thresholds, otherwise classify insufficient/underpowered rather than selecting only taxon-positive groups. Small or empty expected taxon pools may make ratios unstable: report source counts; do not tune epsilon or add one unseen taxon.

A formally supported **exploratory vegetation-conditional taxon replacement** signal needs primary two-sided route CI excluding zero, six-test BH q<.05, signflip p<.05 and State CI excluding zero in the SAME direction with ≥75% same-sign leave-one-State-out effects. Secondary significance is labeled separately and cannot rescue a failed primary. If the replacement result is unsupported, report `no_robust_PEM_specific_temporal_replacement`. An opposite-sign nestedness component is not a causal mechanism.

### Pre-specified ecological descriptive diagnostics (no additional significance tests)

- Within each vegetation habitat and call threshold: physical-route means of `a,b,c,β_sor,β_sim,β_sne,J`, and ratios of `β_sim/β_sor` where identified; no claim this is share of absolute temporal gamma bonus.
- Mean expected taxon union and early/later-only counts to tie exactly to prior positive seasonal bonus. These per-pool quantities are compared at the **same conditioned observation grain**, so not directly equated with earlier unconditional ∆bonus means.
- Round-pair-specific route-balanced components for original 1–2,1–3,2–3 and sparse round4 combinations, each with n groups/routes/States and no separate P values.
- Percentage of original matched pairs excluded for both-active composition due to silent rounds; this may differ by vegetation and is **outcome-dependent**. Even with strong result, the estimand is conditional on detectable calling on both sides in both rounds and cannot be generalized to silent routes without additional modeling.
- Arithmetic split of total temporal dissimilarity into β_sim and β_sne at each source group: no biological interpretation of actual colonization, breeding success, competitive displacement or interactions.

These are native acoustic taxon pool descriptions, not a model of prediction error or multiple independent taxa. Static NWI polygons may proxy hydroperiod, shoreline, acoustic detection, fish/odonates and other geography. Neither plant causality nor frog-frog interactions nor true three-species trophic effects are measured. All results isolated in an exploration branch, code and nonraw aggregate plus workflow audit. Frozen JAE RC6 main/manuscript/SI/submission unchanged.
