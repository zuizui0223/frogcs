# Locked exploratory macroecology: elapsed years and acoustic taxon site anchoring within wetland vegetation strata

**Created 2026-10-23 before reading any new regression/decay estimates.** The prior source, basic 1-year and >1-year means, and the source's original PEM site-fidelity null are already observed: 2,403 exact physical-SiteID paired year visits, 273 routes, 20 US States; CI>=1 within-habitat recurrence F_PEM=+0.08388 and F_nonPEM=+0.08862, but PEM−nonPEM=-0.00475, P=.4434. Thus this is a **post-hoc ecological mechanism-free temporal gradient analysis** of the SAME historical USGS NAAMP 2001–2015 × validated USFWS NWI 250-m mapped wetland polygons, not an independently held-out or preregistered confirmatory test.

## Biological goal — no prediction models

At identical physical monitoring stations visited in multiple survey years, is the community's **taxon-specific acoustic site identity** less persistent over longer elapsed intervals, *relative to other physical wetland stations of the same mapped vegetation class*? And does any duration relationship differ between NWI PEM-emergent and other mapped wetlands?

Distinguish **(a) vegetation-associated larger acoustic species pools** from **(b) same-site community identity anchoring** and **(c) erosion of anchoring as observation gap lengthens**. Animal recruitment, colonization, persistence of the same individuals, species–species interactions and causal plant effects are NOT observed.

## Fully fixed source and observation definition

Reuse directly from the previous source-verified `exploration/run_naamp_vegetation_interannual_site_fidelity_v0_1.py`:
- Original 7,848 standardized source survey nights; 6,236 NWI-complete ten-stop source nights; 5,147 outcome-blind NWI 250-m mapped SiteIDs, 499 routes and 20 States.
- Exactly **2,403 chronologically adjacent observed-year matched physical-SiteID pairs**, same NAAMP RunNumber within each State×route, m=min(n_PEM+,n_nonPEM)≥2, groups restricted to stations already mapped as wetland. Route/night/stop identity and static NWI map unchanged.
- Exactly **273 physical routes / 20 States**, year gaps 1 to 14, original CI>=1 / CI>=2 acoustic taxon units; preserve zero-call stops.
- For each habitat h and survey-year pair, `F_h(m)=(m−1)/m × [mean_i |A_i∩B_i|−mean_{i≠j}|A_i∩B_j|]`, verified previously against all subsets/permutations. It is *acoustic community site anchoring beyond swapping entire later-year stop taxon sets within the SAME NWI class*, not a demographic persistence rate.
- Original PEM contrast F_PEM−F_nonPEM is kept unchanged and NOT reinterpreted as a positive effect merely from other slopes.

## Exactly four prospective-for-this-retrospective-stage slopes

Before reading the new outcomes, freeze these four endpoints and one common analysis:

1. **Primary:** F_mean_any = (F_PEM_any+F_nonPEM_any)/2.
2. **Secondary:** F_mean_strong = (F_PEM_strong+F_nonPEM_strong)/2.
3. **Secondary differential:** ΔF_any = F_PEM_any−F_nonPEM_any.
4. **Secondary differential:** ΔF_strong = F_PEM_strong−F_nonPEM_strong.

Outcome unit: excess repeatedly detected taxon labels per physical site. Predictor `log2(year_gap)` with **one-unit change = a doubling of elapsed years**; primary directional ecological hypothesis **negative** (longer gaps less acoustic site identity). Differential slopes two-sided, exploratory. BH across all four route-cluster Student two-sided tests; report actual coefficients and 95% CIs even if nonsignificant. A positive result is a temporal association, NOT causation or an estimated per-year ecological extinction hazard.

Model: **physical-route × NAAMP RunNumber survey-round fixed effects**, all covariates demeaned exactly within each group. Include ONLY source-captured nuisance predictors:
- abs earlier–later day-of-year difference /30 days;
- abs earlier–later mean air temperature difference /5°C;
- abs earlier–later `log1p(DaysSinceRain)` difference (unit log scale);
- same `ObserverTrackingID` indicator;
- calendar start year `(year_before−2001)/5` (source survey-era drift).

No taxon selection, richness conditioning, year-gap filtering, vegetation GIS radius change, and no route/State selection after results. Stop observation unit is the **matched site**; analysis unit is the **paired visits per route-season**, and inferential independent cluster is physical route. Every physical route gets equal total weight, regardless of numbers of repeated paired surveys.

Pre-analysis rank/coverage gates: ≥200 original year pairs, ≥50 independent physical routes, ≥5 States, at least 80 physical routes with **within-route×survey-round variation in log2(year gap)**. Otherwise do not interpret fitted slopes. Use route sandwich with finite sample cluster factor G/(G−1) × (N−1)/(N−K−H+1), where K=6 covariate slopes including loggap, H=# route×round groups, plus Student t df=G−1; also 20-State sandwich 95% CI (df=S−1) as sensitivity. Four sets of **4,999 independent route-sign-flips of nuisance-orthogonalized score** (FWL) as an additional approximate cluster-symmetric null, not randomization.

## Pre-fixed descriptive diagnostics, not significance-shopping

- Raw per-route mean F and ΔF within lag bins `1 year`, `2 years`, `3 years`, `4–14 years`; report route and source pair counts. These are different cohort compositions and not formal ecological duration effect estimates.
- For each endpoint, leave-one-State-out fitted gap coefficient: sign, range and count of estimable States; report poor geographic consistency explicitly.
- Exact same original `ObserverTrackingID` subset (prior n=1,925 visits across 238 routes) as predeclared sensitivity; within subgroup the same-observer indicator is constant, so OMIT only that indicator and refit otherwise identical route×round model. Require ≥500 paired visits, ≥100 physical routes, ≥50 independent routes with within-group duration variation; otherwise mark insufficient. Do not selectively switch to an unadjusted model.
- Include actual route×round group coverage and effective duration variation. Report correlation of year gap with calendar starting year; if extreme collinearity makes inference unidentified, fail closed.
- Positive/negative site-fidelity itself from the source has already passed the prior source-specific route tests and should not be p-value retested as a newly independent dataset.

## Biological conclusion gates

"exploratory_route_robust_acoustic_memory_decay" only if the **primary CI>=1 mean-F slope is negative**, the route CI excludes 0, four-test BH q<0.05, route FWL score signflip P<0.05, and at least 75% of estimable leave-one-State-out coefficients are negative, without a positive State-cluster CI. Otherwise "no_supported_elapsed_year_decay_on_adjusted_same_footprint" with all estimates shown. A differential vegetation slope cannot rescue a failed primary direction test or establish causal PEM effect.

The NWI categories were mapped at another time and are coarse buffer overlaps; local water/hydroperiod, geography, fish/odonates, individual frogs, detection quality, climate trends and exact phenology can confound elapsed-year patterns even after nuisance adjustment. Adjacent observed-year pairing creates informative gap selection; acknowledge this explicitly.

Results only on independent exploration branch, numerical aggregate and reproducible GitHub Actions; untouched original JAE RC6 paper, SI and main.
