# Freeze-before-readback: global vegetation-stratified frog pair-identity network, corrected for acoustic richness

**Date 2026-10-23.** This analysis is motivated by source-verified previous 6,236 NAAMP × NWI surveys showing more calling taxa at emergent-wetland sites, more species per matched equal-effort taxon pool, and a positive extra-taxa component. It is **a new post-hoc observational analysis**, not independent confirmation or preregistration. No prediction/forecast, no new literature retrieval, no expansion to fictitious fish or insect records. Frozen JAE RC6 and main remain untouched.

## Distinct biological macro question

The previously robust mapped PEM–frog **alpha and gamma** richness association could increase taxon co-detection mechanically: more taxa at a stop means more detected pairs. Does **the identity of the pairs of frog taxa co-detected together** differ between PEM+ and PEM0 stations *within the same mapped wetland route-night* more than expected from a null model that preserves every taxon's observed 10-stop attendance, every stop's total number of detected taxa, and held-out taxon-specific NWI site affinities?

This is a global network-structure question **beyond richness**, not a rerun of individual pair BH screens that found only two fragile candidates (neither passed time/geography robustness). Primary is any-call CI≥1, strong CI≥2 is secondary. We never claim paired acoustic detection equals direct species interaction, synchronized chorusing, competition, facilitation, or biological higher-order interaction.

## Source identity and environmental gates

- Pinned source: original USGS NAAMP 2001–2015 and response-blind USFWS NWI **12-shard site polygon crosswalk** source [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196), 5,147 physical mapped SiteIDs; 7,848 standardized complete 10-stop survey nights, 6,236 NWI/temperature/noise-complete nights, 499 geographic routes and 20 States, no raw source committed.
- Original **route-held-out** fitted taxon environmental null from [Actions #39516056663](https://github.com/zuizui0223/frogcs/actions/runs/39516056663), fixed prior settings / file coefficients. Full fixed-margin checkerboard reference is exactly **3,659 survey matrices /478 routes** for CI≥1 and **1,766 /398 routes** for CI≥2. Do not refit source NWI coefficients based on this new result or change its sample.
- Within those source matrices, define eligible test runs as **at least 2 PEM+ stations and 2 PEM0 stations among NWI-mapped total-wetland stations**. PEM+ means NWI emergent fractional 250m polygon cover >0, PEM0 means zero PEM polygon overlap **within** NWI mapped wetland footprint (total wetland cover>0). This design excludes unmapped wetlands from the direct plant-stratified comparison. Selection is solely on environmental data and original matrix row/column counts.
- Keep ALL recorded source taxon units (including taxon complexes) in the randomized matrix and in richness margins, but global tested pair labels are limited to the **preexisting network’s independently named eligible pairs**: 127 baseline CI≥1 fitted edges and 57 CI≥2 fitted edges from `exploration/NAAMP_PLANT_CONDITIONED_FROG_PAIR_NETWORK_RESULT_V0_1.json`. This pre-existing eligibility depends on historical route coactivation/fixed-margin variability, **not** the new PEM-contrast outcomes.
- For each eligible original pair, include only mixed-PEM coactive survey matrices. Before fitting any observed contrast, gate to ≥20 mixed habitat runs, ≥10 independently sampled physical routes and ≥5 independent null-varying reference matrices. This new coverage gate is fixed here; failures remain counted, not treated as zero evidence.

## Define exactly what richness cannot explain

Per survey-run pair (a,b), let `B_{ak}` be 1 iff taxon a has positive calling index at stop k. For n+ eligible wetland PEM-positive and n− eligible wetland PEM-negative listening stations, the **within-run plant-context dyadic coincidence difference** is:

`D_ab = [Σ_{k∈PEM+} B_ak B_bk/n+] − [Σ_{k∈PEM0} B_ak B_bk/n−]`.

This can be strongly positive simply from taxon-specific habitat use or more local richness. Compare with the ORIGINAL opposite-geographic-route fold NWI (total mapped wetland+emergent PEM) taxon-dependent `θ`, using a **weighted Metropolis Curveball** sampler, with **every row and column sum exactly fixed** (the source’s original sampler). Fixed settings **199 draws, 40 burn proposals per taxon, 8 proposals per taxon between draws**, deterministic run-specific SHA256 seed; no parameter optimization based on observed results.

**Hard QA invariant:** summing co-detected pairs **over all taxa** within a habitat class is mathematically fixed by column richness `Σ_{k in class} C(r_k,2)/n_class`. Consequently, any test of the *total number of co-detected pairs* would be invalid: its null variance is exactly zero. The new statistic is intentionally **which taxon pairs**, not how many pairs.

The per-pair aggregate `d_obs_ab` is the mean of D_ab over the pre-fixed mixed and eligible source route-nights. The sample null for each draw index b aggregates one independent route-night-constrained null matrix per eligible run: `d^null_ab,b`. Its mean `mu_ab` is the original weighted fixed-margin expectation.

## One global statistic, not post-hoc pair shopping

Primary statistic:

`T_observed = mean_over_eligible_pairs [(d_obs_ab − mu_ab)^2]`.

Compare it against an empirical null on the identical **original eligible edges and route-night masks**:

`T_null,b = mean_over_edges [(d_null_ab,b − mu_minus_b,ab)^2]`,

where `mu_minus_b` is the leave-one-null-draw-out mean, preventing a test null draw from centering on itself. Numerical precision and effective replicates recorded. This is a squared magnitude averaged equally over all eligible pairs: a diffuse, potentially **positive or negative** pair-identity network rearrangement can register. One plus-one **upper-tail P = (1 + # T_null≥T_obs)/(200)**. Use **CI≥1 as the single global primary**, **CI≥2 as a secondary**. The reference null includes local PEM habitat preference at first order, row/column margins and route-held-out parameter estimation; it does NOT represent all ecological abiotic covariates/true contemporaneous wetland vegetative structure.

Report in addition without reselecting edges:
- null quantiles and T observed/null mean ratio;
- fraction of edges with positive and negative mean excess PEM-vs-PEM0 dyadic coincidence after the first-order model;
- same global squared-residual statistic computed in independent geographic route folds A/B, and sign agreement of edge residual vectors for edges with adequate numbers (≥10 mixed runs per fold). These are exploratory stability diagnostics, not independent confirmation, because the original environmental weights are trained on both years;
- three to ten strongest absolute residual edges as **illustrative, not BH-supported discoveries**; the previous fragile PEM pair moderators must **not** be revived as direct interactions because of a global result.
- if primary null rejected P≤0.05 and BOTH fold-specific observed T>null mean, label `exploratory_global_PEM_conditioned_dyadic_pattern`. Otherwise `not_supported`. Do not infer paired biological interaction or causal plant mechanism from either.

## Technical integrity boundaries

- Preserve original source 3,659/1,766 reference matrix membership and compare each original observed C-score to the prior immutable diagnostic before calculating any new contrast.
- For every null, verify ten-stop row and column margins at at least first/middle/last draws. Reject unmixing or low ESS problems; report accepted moves and mixed-PEM eligible source geography.
- Preserve entire wetland within-PEM column selector through all null draws (no invented random plant layouts).
- Route-stop visits sequential; co-calling means detected within same **stop**, not simultaneous across recorded time windows.
- Edge-level null draws have within-run MCMC autocorrelation; draw count 199 bounds the smallest p to 0.005. Describe Monte Carlo uncertainty, do not promote a surprising MC floor alone as biologically definitive.
- NWI polygons, including PEM/woody/aquatic-bed, are mapped wetland categories and temporally mismatched with 2001–2015 calls; no measured local aquatic macrophyte species, hydroperiod, fish/odonates, tadpole survival or intervention.
- Preserve original RC6 paper, analysis results, provenance and release authority untouched.

Code under `exploration/run_naamp_pem_fixedmargin_pair_network_global_v0_1.py`, workflow `.github/workflows/naamp_pem_fixedmargin_pair_network_global.yml`; numerical aggregate as workflow artifact, versioned summary only after verified execution. The previous alpha/gamma positive results remain sources, not claims made by the new network statistic.
