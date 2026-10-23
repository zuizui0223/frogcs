# NAAMP wetland vegetation and interannual acoustic community site fidelity: frozen exploratory protocol

Date 2026-10-23. **New observational macroecological time hierarchy**, written before computing its outcome. Motivated after the same USGS NAAMP × NWI archive showed positive PEM acoustic alpha and rarefied gamma, but **not** a route-robust PEM-specific taxon-pair identity network signal. This is post-hoc research on a previously viewed dataset, not independent validation or prospective preregistration. No predictive modeling or external literature. JAE RC6 main, manuscript, SI and submission remain frozen.

## Biological question

Across the same physical ten listening stops in successive monitored **years**, are frog *calling-taxon identities* at NWI mapped emergent (PEM) wetlands more likely to recur at their **own exact physical site**, instead of another physical site within the **same mapped wetland class**, compared with wetland stops without PEM? This separates acoustic species-pool richness at one snapshot from temporal persistence and spatial reallocation. It does **not** measure demographic persistence, individuals, frog breeding, plant causality or actual interaction partners.

## Source and design

Use the unchanged source from Actions #39450277196: 7,848 original standardized USGS NAAMP surveys in 2001–2015, 6,236 full site-NWI-temperature/noise complete ten-stop run-nights; 5,147 NWI 250m mapped physical SiteIDs, original 499 routes and 20 States. All original recorded NAAMP monitoring taxon labels including complexes; threshold CI>=1 primary, CI>=2 secondary.

- Group eligible route-nights by **State × RouteNumber × RunNumber**. RunNumber ∈ {1,2,3,4} is the repeated within-year survey round, a partial season adjustment. Within each group/year, require **exactly one NWI-complete survey**; if multiple runs in a calendar year, drop that ambiguous year altogether without looking at calls. Pair chronologically **adjacent recorded years**, not all pair combinations. Year gap may range 1–14 and must be reported, not silently treat multi-year gaps as annual lag one.
- Require both visits to use the **exact same 10 physical SiteIDs** in the same stop-position order, and the exact same mapped 250m NWI habitat descriptors. Drop changing/repositioned stations before looking at frog outcomes. Retain both-silent stops and all taxon labels. Check State, route, and year identity.
- Restrict vegetation comparison to stations already mapped as any NWI wetland (total wetland cover fraction >0) and compare PEM-overlap positive vs PEM-no-overlap among those wetland stations. Require ≥2 physical stations in each class on this route-pair. n+ and n− may differ, so use **equal-size rarefaction** m=min(n+,n−)≥2; m fixed independently of calling.
- All dates, observer IDs and local conditions are observational covariates, not reasons to change source cutoffs based on outcomes. Exclude missing 10-stop source/metadata using original full-census prefilter only.

## One exact ecological statistic

For one vegetation stratum h within one exact same-physical-site interannual run pair, let A_i denote the set of calling taxon labels at physical stop i in the earlier year, B_i in the later year (i=1..n_h). Define:
- own-site overlap average `D_h = mean_i |A_i ∩ B_i|`;
- cross-other-site overlap average `O_h = mean_{i≠j}|A_i∩B_j|`, with earlier vs later sites matched only within *the same NWI mapped habitat stratum* (preserves coarse plant class, every year's taxon pool, and taxon richness of the actual whole-stop assemblages);
- exact m-stop rarefied **site-identity recurrence excess** `F_h(m) = ((m−1)/m) × (D_h−O_h)`.

Justification: under an equal m-of-n site subset chosen uniformly without replacement and a random reassignment of all later-year entire-stop assemblages within that subset, the expected `observed own-site taxa repeated − permuted site identity taxa repeated` is exactly F_h(m). This is a simple hypergeometric combinatorial identity, to be independently validated by enumerating all possible m-site subsets and permutations on a toy ecological matrix. It is NOT a causal NWI plant effect or a species-pair interaction.

Primary pair-night contrast `Δ=F_PEM(m)−F_nonPEM(m)`: positive means greater same-site interannual excess in PEM stations than other NWI-wetland stations in the SAME route × survey round × pair of observation years. In units of repeat-detected NAAMP taxon labels/site. The null for each class preserves that whole-class observed year1 and year2 acoustic composition, frequency, and stop richness, while severing the direct physical stop pairing. It does not control for unmapped continuous within-class habitat gradients or individual detection heterogeneity.

**Matched secondary acoustic activation** replace |`A_i∩B_j`| by `1{A_i nonempty} × 1{B_j nonempty}`, keeping the same F formula. This measures persistence of detection of any taxon at the physical stop, not specific taxon identity. Report as descriptive only, no new primary significance family. Also provide each habitat's own-site recurrence, other-site recurrence, and F, and whether overall PEM focal contrast differs from zero. Both-silent pairs contribute exactly zero.

## Geography, dependence and inferential rules

Unit of independent geographic inference = **physical route**. Compute mean Δ across all eligible paired years/run rounds per route, then mean of physical-route estimates; 95% Student t with df=#eligible independent routes−1, two-sided p; 4,999 physical-route Rademacher sign flips. BH over the **two fixed call thresholds**; require ≥30 independent routes, ≥5 States, ≥100 distinct matched route×round×year pairs. Keep State-balanced mean, number of positive State means and leave-one-State-out effect sign/range. Also report:
- valid year gap distribution and descriptive 1-year / >1-year contrasts with no new p values;
- same-observer only if ≥30 routes and ≥100 matched year-pairs, as predeclared sensitivity; observership is based on the original `ObserverTrackingID` present in USGS Runs;
- both habitat-specific F values, so negative Δ cannot be mistaken for total site-fidelity absence;
- actual interannual acoustic same-site overlapping taxon means and cross-site references;
- exact NWI source denominator and exclusions (duplicate survey years, physical SiteID drift, lack of within-wetland PEM heterogeneity).

A supported **exploratory temporal habitat-context contrast** requires positive route-level CI (for predicted direction) and two-test BH q<0.05, with no reversal under omitting a State. A null or negative result is reported without geographically re-selecting a subgroup or changing the time gap after looking at results. State-level CI and State-equal direction are sensitivity summaries, not substitutes for independent experiments.

## Critical ecological limitations

USFWS NWI polygons are **static and not ground-matched to the NAAMP 2001–2015 plant structure**, and NWI PEM=0 is not evidence that plants were absent. Calling detection is not species absence/abundance/occupied breeding habitat. The same station may have stable microclimate, fish, shoreline, depth or acoustic quality; the within-habitat site permutation removes a generic mapped-PEM preference but **cannot attribute physical-station recurrence to vegetation** or measure animal competition/facilitation. Repeated routes are clustered; simultaneous chorusing across stops is not observed; causal higher-order species interactions are not inferable. Previously observed positive PEM local alpha/gamma remains unchanged regardless of this test.

Reproducibility: isolated exploration code `exploration/run_naamp_vegetation_interannual_site_fidelity_v0_1.py`, GitHub Actions workflow `.github/workflows/naamp_vegetation_interannual_site_fidelity.yml`, aggregate result archived in Actions plus a small verified summary in git. No original raw source records committed. Frozen main JAE RC6 unaffected.
