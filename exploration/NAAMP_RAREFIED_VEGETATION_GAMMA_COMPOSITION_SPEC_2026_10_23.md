# Locked exploratory macroecology: does mapped vegetation enrich frog community taxon pools, or replace them?

Date: 2026-10-23. Locked **before the new rarefied-gamma outcome is computed**, after prior NAAMP/NWI alpha-richness and covariance results had already been examined. Thus retrospective *exploratory* research, NOT preregistration or new independent data. No prediction, forecast, simulation-as-data, literature research, or JAE RC6 edits.

## Biological question

In the same physical route and listening-night, mapped emergent-wetland sites have more acoustically detected frog taxon units per stop. Does that positive local **alpha** pattern extend to the number of **distinct taxa across multiple stops (gamma)** when exactly equal numbers of vegetation-positive and vegetation-negative stops are surveyed? Is the distinction mainly asymmetric richness of the two sampled taxon sets (nestedness component) or a turnover/replacement difference?

This is distinct from the already completed *richness-adjusted between-individual-stop Sørensen boundary effect* (+0.087 pp, P=.714), because it compares **equal-area sampled taxon pools**, not pairwise adjacent or arbitrarily distant individual stops, and the taxon-pool richness difference is the primary endpoint. No changing buffer radius, species exclusions or spatial windows after results.

## Unmodified source, all source taxa
Use original 2001–2015 NAAMP CI≥1 and CI≥2 taxon/stop calling records, all taxon names including labelled complexes, and original geometrically audited 250-m 12-shard USFWS NWI habitat polygon fractions from source run 39450277196. Reproduce exactly 7,848 standardized nights; 6,236 environmental-complete 10-stop nights; 62,360 valid stop-by-night records; 5,147 unique source NWI physical sites. No sound/temperature-based re-selection beyond previously frozen complete-10-stop source gate. Independent geographic unit: physical route, not species, taxa, stop pairs, rarefaction replicates or repeated nights.

Four overlapping mapped habitat binary contrasts, in this order: PEM emergent, aquatic bed, woody/shrub, total NWI wetland fraction; positive iff corresponding mapped NWI 250-m polygon fraction>0; negative iff zero polygon overlap. **These are not contemporaneous field observations of live plants** and overlapping class indicators do not distinguish intrinsic effects.

For each route-night with 1–9 positive and 1–9 negative sites, let n+ and n− be the number of stops with/without mapped class, and m=min(n+,n−). The **fixed primary gamma analysis requires m≥2 stops per group** to distinguish multi-site taxon pool from single-stop alpha. Separately report m≥1 as a direct continuity/coverage sensitivity (will include primary and one-site comparisons). If a class has fewer than 30 independent routes or 5 States at m≥2, it is **underpowered**, not an ecological negative result; keep all eight pre-fixed class × calling-threshold tests in the FDR family with P=1 for ineligible.

### Exact rarefaction, without Monte Carlo selection of favorable subsamples

Let a taxon s be heard at k_s out of n stops in one habitat category. Under uniformly choosing m unique stops without replacement, its exact probability of appearing in the pooled taxon list is
p_s=1−C(n−k_s,m)/C(n,m), where C(a,b)=0 for b>a.
Therefore expected gamma = Σ_s p_s. Calculate E[gamma+] and E[gamma−] at the same m, and **delta gamma** = E[gamma+]−E[gamma−].

For sampled pools drawn independently across non-overlapping positive/negative stop groups on the same route-night, calculate *expected shared taxon count* E[shared]=Σ_s p+_s p−_s, and expected unique positive = Σ_s p+_s(1−p−_s), expected unique negative analogously. Verify the **identity E[gamma+]−E[gamma−] = E[unique+]−E[unique−]** to within numeric precision. This is a statement about the sampled taxon pools, not direct transitions, invasions or competitive exclusion.

Route-level estimand: first average route-night delta gamma **within each independently sampled physical route**, then give every route equal weight; report mean in **distinct acoustic taxon units per m-stop pool**, 95% Student-t CI(df=routes−1), two-sided P, and 4,999 sign flips of complete route estimates, with BH across eight primary m≥2 tests. Geographic sensitivity: equal-State average; fraction of States with positive mean; leave-one-State-out signs; retrospective 2001–09 vs 2010–15 route means, clearly not independent temporal validation. Also report m distribution, including count m=1 excluded from primary. Two calling thresholds: CI≥1 (primary) and CI≥2 (secondary).

### PEM composition partition (secondary descriptive, fixed before readback)

For **PEM only** m≥2 nights, and CI≥1/CI≥2 separately, take 199 deterministic independent paired subsamples of m distinct positive sites and m distinct negative sites for each night, using a hash of route-night identity and threshold. Compute pooled taxon sets A and B, and Baselga incidence dissimilarity components when BOTH pooled sets have ≥1 taxon:
- Sørensen β_sor=(b+c)/(2a+b+c), with a shared taxa, b PEM-only, c non-PEM-only.
- turnover β_sim=min(b,c)/(a+min(b,c)).
- nestedness-resultant β_sne=β_sor−β_sim.

Only use those comparisons if denominators valid; do not coerce all-empty/one-empty assemblages into fabricated Simpson values. Report draw count, fraction excluded, **route-balanced** β_sor/β_sim/β_sne means, and ratio of sum nestedness component to sum Sørensen (a descriptive composition metric, not the fraction of causal plant effect). Sampling draws are measurement approximations within each night, **never independent experimental replicates**. If >50% draws invalid or <30 routes, classify descriptive insufficient. The expected unique positive/negative taxa use **exact analytic probabilities**, not Monte Carlo.

## Scientific inference gates

- Supported *observational taxon-pool enrichment*: primary route-level CI excludes 0 and eight-test BH q<0.05, with ≥30 routes and ≥5 States. A Stage-2 State-equal result with sign reversal is explicitly marked geographically fragile.
- A positive gamma contrast plus large β_sne does **not** mean real species additions replaced no species or that those plants cause population persistence. Species pools are calling detections on sequentially surveyed stops. Nestedness/turnover are descriptive dissimilarity metrics, not temporally observed transitions.
- The original 2026-10-23 matched-alpha result, covariance sign reversal among State means vs local stops and non-support of richness-conditioned Sørensen are all retained. Different estimands may yield different conclusions; do not overwrite.
- There are no contemporaneous measurements of plant identity/architecture, hydroperiod, fish, aquatic predatory insects, competition, recruitment or animal movement. Direct species interaction and irreducible triadic causality not identifiable.

Output one source-audited code script and run artifact, plus compact claim ledger. **main**, JAE RC6 manuscript, SI and submission left untouched.
