# Frozen before new result readback — NAAMP continental acoustic-community turnover at mapped emergent-wetland boundaries

**2026-10-23** — Exploratory *new pooled macroecological test* of existing publicly studied USGS NAAMP 2001–2015 and geometrically validated USFWS NWI 250-m crosswalk. This is NOT prospective preregistration: the source datasets and prior single-taxon/pair/landscape results have already been inspected in frogcs. There is **no literature expansion**. JAE RC6 main and its paper, SI and submission are out of scope.

## Core ecological question

Do **two stops on the same ten-stop NAAMP route-night** have a more dissimilar acoustically detected frog community when exactly one stop intersects a mapped NWI PEM *emergent wetland polygon* than when both stops share the same mapped PEM category, **after matching the time, route-run, survey protocol and controlling pairwise differences in landscape wetland cover, acoustic species richness and listening-stop separation?**

Here `PEM > 0` represents **a mapped 250-m polygon-overlap flag**, not contemporary 2001–2015 plant identity, biomass, real emergent cover, or causal plant exposure. The route-night 10 stations were visited sequentially; calling is not abundance, demographic occupancy or simultaneous vocalization.

## Dataset and outcome, fixed without new selection

Reuse `exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py` exactly as a validated original NAAMP loader/crosswalk, reproducing the existing 7,848 standardized survey nights and 6,236 NWI + air temperature/sound-complete 10-stop nights. NWI response-blind source run **39450277196**, geometry must have 12 successful shards and 5,147 physical site records. Do not silently reclassify 53 failed route queries as vegetation absence.

One *biological* data unit is the **complete survey route/night** nested within the route, not 45 independent stop pairs. Candidate routes have 10 unique physical SiteID points, and must include **at least 2 mapped PEM-positive and 2 PEM-nonoverlap stops** (environment-only inclusion); require >1 distinct observed acoustic taxon across route for meaningful composition. Describe all exclusions.

For each ten-stop night, construct **45 unordered stop pairs**, with taxon name retained (including explicitly labelled historical taxon complexes). Standard acoustic detection `CallingIndex>=1` is **primary**, CI>=2 **secondary**. If both compared sites have zero detected frog taxa, Sørensen is **undefined** (exclude, never impute 0 or 1). If only one has detections, Sørensen =1. Otherwise:
- `a=|S_i ∩ S_j|`, `b=|S_i\S_j|`, `c=|S_j\S_i|`.
- **Sørensen dissimilarity:** `Y=(b+c)/(2a+b+c)`, in 0..1. Report coefficient `100*β` **percentage points of Sørensen dissimilarity**.
- **Simpson turnover** `min(b,c)/(a+min(b,c))` is a separate *secondary* outcome **only if both stops have detections and denominator>0**; do not use Simpson = 0 for all-empty or nested 0/0 cases.
- `B=1` if `(PEM_i>0) XOR (PEM_j>0)`; B=0 for shared mapped PEM status.
- Context: difference in total wetland 250m coverage (absolute), difference in temperature (absolute °C), difference in acoustic masking/sound index (absolute), difference in acoustic taxon richness (absolute), mean acoustic richness, and 8 dummies for **physical route stop separation** `|stop_i-stop_j|=2..9` (distance 1 baseline). These nuisance variables are fixed *before result readback*, regardless of sign/significance; do not add other covariates after readback.

## Estimation and inference

1. Regress `Y` on B and those 13 fixed nuisance variables with **exact within-survey-night fixed-effects demeaning**. This conditions on shared species availability, season and unmeasured run-level wet/dry weather for a same-night route.
2. Weight observations so each **physical route contributes equally**, even if surveyed many nights or has different numbers of valid stop pairs. Route groups, not stops/nights, define independent clusters. Use cluster sandwich 95% intervals (Student t, df=#routes−1), with finite-cluster factor `G/(G-1) × (N−1)/(N−K)`. Clearly label this exploratory associational interval, not a randomization CI.
3. As a **pre-fixed, non-spatially-exact** independent-route uncertainty check: 4,999 Rademacher route-sign flips of nuisance-residualized primary score contributions, conditioning on B and nuisance design; compare signed score to a two-sided wild score reference (Monte Carlo plus-one). This tests a statistical coefficient null under approximately independent symmetric route scores, not randomized plant labels or a causal hypothesis.
4. Provide secondary **equal-observation** OLS route-cluster estimate (checks uneven route effort influence), Simpson turnover among both-active site pairs, and CI2–3 Sørensen (same mapped PEM rules). No new significance hunting.
5. Falsification: compute sample means in same-PEM vs mixed-PEM stop pairs; if B is nearly constant/collinear with controls or <50 independent routes, fail closed. Count route/run eligibility, unique paired survey routes, taxon richness, and the fraction of pair opportunities missing because both stops are silent. Confirm numerical 0..1 metrics.
6. Report outcome counts and 95% CIs. Decision rule: **exploratory residual boundary association** if primary route-cluster CI excludes zero, sign stable between equal-route and equal-observation estimates, and 4,999-wild-score two-sided p<0.05. Otherwise **not supported**. Not a biological interaction or plant causality even if the rule passes.

## Scientific interpretation limits

An apparent PEM boundary effect could reflect changing shoreline geometry, hydroperiod, predator presence, actual wetland size, mapping year, detectability, sound transmission, or colonization history. Conversely null result doesn't prove uniform communities or no plant effect. This is a **community turnover pattern** test, not fish/insect trophic mediation, taxon competition, or irreducible higher-order interactions. This new test is distinct from earlier species-pair 57/110-node permutation failures; those are retained as history, not overwritten. Raw NAAMP and NWI site source files are downloaded only during GitHub Actions, never committed.

Code `exploration/run_naamp_macro_pem_boundary_turnover_v0_1.py`, GitHub Actions `.github/workflows/naamp_macro_pem_boundary_turnover.yml`, numerical result as immutable run artifact. No updates to RC6 authority files.
