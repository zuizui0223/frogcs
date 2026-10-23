# Interannual ecological hierarchy of wetland-associated frog acoustic communities: duration is not demonstrated as the cause of site-identity loss

**Study date 2026-10-23; real USGS NAAMP 2001–2015 × geographically audited USFWS NWI 250-m mapped wetland data.** Ecology-first observational analysis of detected calling taxon units, not a predictive model, new literature review, contemporary botanical survey or experiment. The study uses the SAME source archive as previous PEM acoustic richness and taxon-pool results; all new year-gap tests are explicitly post-hoc and were specified before this particular regression readback. Frozen JAE RC6 main/manuscript/SI/submission remain unchanged.

## Ecological answer

**Physical wetland listening stops retain species-specific acoustic identities across separately monitored years beyond what would be expected from exchanging stop taxon lists within the same NWI vegetation category.** However, the difference between PEM emergent wetlands and other mapped wetlands in this identity persistence is nonsupported. And after comparing year gaps within the **same monitoring route × NAAMP annual survey round**, while accounting for calendar year, phenological day-of-year difference, temperature difference, rain and observer, **there is no supported monotonic loss of site identity as calendar gaps get longer**.

This is an important hierarchical distinction: mapped emergent-wetland association with *how many* frog taxa call, and general local micro-site anchoring of *which taxa* are re-detected, do NOT necessarily share a vegetation-specific time-decay signature. A nonsignificant gap slope is **not equivalence evidence** or a positive claim of memory remaining constant for 14 years.

## Original source and exact ecological units

Original full NAAMP standardized ten-stop surveys: **7,848**. Earlier GIS crosswalk and acoustic source quality gates: **6,236** complete 10-stop survey nights; **5,147** geographically mapped physical NWI SiteIDs /499 total source routes /20 US States; 12 outcome-blind USFWS NWI shards, original [source Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).

Validated same-physical-SiteID paired survey years: **2,403** pairs from **273 physical monitoring routes/20 States** in exactly comparable State×route×original RunNumber (coarse within-year survey round). Each physical stop and original 250m NWI habitat indicator remains identical across paired source years, and each wetland type has ≥2 physically matched sites. Exactly **1,573** adjacent observed visit pairs had 1-calendar-year gap, **830** longer gaps, maximum 14 years. The same nonmissing ObserverTrackingID appears across **1,925** matched pairs from 238 routes. Taxon complexes retained as original monitoring labels. No missing frog calls were used as a geographic inclusion criterion.

## Core metric: specific acoustic taxon recurrence beyond random rematching of other same-habitat sites

For each paired route-round-year visit and each mapped wetland habitat h (PEM vs nonPEM mapped wetland), set A_i and B_i to frog calling taxon lists from the earlier and later source year at physical stop i. Given n_h wetland stops in category h, sample m=min(n_PEM,n_otherwetland) matched sites per habitat, m≥2. The exact hypergeometric expected taxon recurrence excess over rematching the later-year entire-stop communities within their *same* vegetation class is:

`F_h(m) = (m−1)/m × {mean_i |A_i ∩ B_i| − mean_{i≠j}|A_i∩B_j|}`.

The equation was previously independently verified against **every m-subset and every entire-stop permutation** on known synthetic communities, including binary any-caller and both-empty edge cases. It is a measure of **repeat acoustic taxon identity at physical monitoring site**, not persistent individual frogs or plant-driven offspring recruitment.

Previously verified source-grounded positive context values (retained unmodified):

| Interannual site identity excess (taxon units per stop) | PEM | Other mapped wetland | PEM minus other |
|---|---:|---:|---:|
| Any calling CI≥1 | **+0.08388** | **+0.08862** | −0.00475, 95% route CI [−0.01692,+0.00743], P=.443 |
| Strong calling CI≥2 | +0.04838 | +0.04956 | −0.00119, 95% route CI [−0.01027,+0.00790], P=.798 |

Both within-habitat F estimates were positive at route-cluster level (explicit earlier post-readback testing), including same-observer sensitivity; **no PEM advantage** beyond other wetlands.

## NEW: lag-gradient analysis, not a prediction experiment

The new inferential endpoint is whether F declines as **elapsed calendar years double**: x=log2(year_gap), 1-unit = double years. Estimate four predetermined observational gradients:

1. **Primary** mean of PEM and other-wetland F, CI≥1.
2. **Secondary** corresponding mean F, CI≥2.
3. **Secondary** PEM minus nonPEM gap-slope difference, CI≥1.
4. **Secondary** PEM minus nonPEM slope difference, CI≥2.

For all 2,403 source year-pairs, apply **exact monitoring physical-route × NAAMP RunNumber fixed effects** (727 groups), with 6 pre-fixed regressors: log2(year gap), absolute DOY gap per 30 days, absolute source mean air-temperature difference per 5°C, difference in log1p(DaysSinceRain), same-observer flag and starting survey year per five years. Weight each physical route equally. Route-clustered Student t(df=272) CIs and P, route-vector FWL nuisance-residualized sign-flips (4,999 draws), 20-State cluster CIs, four-test BH correction and leave-one-State-out coefficient signs. Duration variation is actually estimable in **404 route-round groups within 179 of 273 physical routes** — unlike naively pretending that all 2,403 pairs independently determine the elapsed-year coefficient.

| x=log2(year-gap) adjusted slope (taxon units per stop / gap doubling) | Beta | 95% route CI | Route P | 4-test BH q | 4,999-route-score-flip P |
|---|---:|---|---:|---:|---:|
| Mean site recurrence, CI≥1 **primary** | **−0.00218** | −0.01376 to +0.00940 | .7111 | **.8674** | .6868 |
| Mean site recurrence, CI≥2 | −0.00340 | −0.01092 to +0.00411 | .3735 | .7469 | .2902 |
| Differential PEM−other slope, CI≥1 | +0.00137 | −0.01473 to +0.01746 | .8674 | .8674 | .8528 |
| Differential PEM−other slope, CI≥2 | −0.01024 | −0.02202 to +0.00154 | .0881 | .3524 | .0384 |

**Inference: no supported adjusted interannual memory decay.** The strongest directional slope for PEM-vs-nonPEM on strong calling is still **unconfirmed**, because its route Student interval includes zero, BH q=.3524, and State cluster interval [−0.02393,+0.00344] includes zero. A single route score-flip nominal P=.0384 is not sufficient to overturn the predeclared multicomparison and cluster robustness gates; avoid p-value cherry-picking.

**Same ObserverTrackingID sensitivity:** among 1,925 matched years/238 physical routes, mean acoustic F CI≥1 slope −0.00230 (95% route CI −0.01448 to +0.00989), and strong CI≥2 −0.00443 (CI −0.01320 to +0.00433); both again nonsupport. The same-observer indicator is omitted from this stratum model because constant 1; all other covariates, route×round FE and route-cluster uncertainty are preserved.

### Why a simple comparison of 1-year versus multi-year pairs is insufficient

Earlier raw data showed larger site F for 1-year paired visits than for pooled >1-year gaps in both wetland groups; but those groups represent different routes/years/observers/phenological intervals.

The new unadjusted route-balanced mean **pooled F_any**, stratified with the identical fixed source duration bins, is:

| Year gap | Original paired nights | Route-balanced F_any |
|---|---:|---:|
| 1 year | 1,573 | **+0.09865** |
| 2 years | 402 | +0.07574 |
| 3 years | 182 | +0.08393 |
| 4–14 years | 246 | +0.06586 |

Those are **not** matched route-round-year comparisons with the same covariates. After the fixed-effects / nuisance adjustments, the monotone duration trend was not supported. The 3-year bin being higher than the 2-year bin is a further reason not to promote this raw sequence as an ecological exponential decay law. Data cover 1–14-year gaps but sparse long lags are not sufficient to conclude no decline at any specific year.

## Position within frogcs vegetation and community hierarchy

1. **Static wetland vegetation structural mosaic (mapped NWI), local alpha:** PEM+ sites co-occur with about +0.238 additional calling taxon units per stop after conditioning on mapped wetland area, other mapped types, air temperature, noise, stop number and same-night route (CI≥1; original 499-route acoustic richness model).
2. **Multi-stop equal-area gamma:** among only mapped-wetland sites, 2–5-stop exactly rarefied PEM pools have about **+0.298** more detected taxa than nonPEM pools, 281 source routes, with positive contributions distributed across 39/48 monitoring taxon labels (these labels are not independent genus-level hypothesis tests).
3. **Geographic hierarchy:** PEM×frog acoustic richness signed covariance is positive within route-night stops (+0.04082) and negative between state means (−0.01257), a descriptive cross-scale sign reversal.
4. **Specific pair co-detection:** source-verified 199-draw fixed-margins taxon-pair identity network had **no route-robust vegetation-driven global network reorganization** (any-call route vector signflip P=.3276; strong P=.3844).
5. **Interannual physical-site anchoring:** F_h>0 within both PEM/nonPEM habitat classes, showing actual site-level acoustic taxon identity structure unaccounted for by static habitat class, but **PEM-specific advantage absent**.
6. **Within-route temporal elapsed-year slope (this analysis):** no adjusted duration relationship passed route, four-test BH and FWL score-null gates. This does not remove the positive same-site re-detection result; it says the source's **elapsed-year gradient is too weak/confounded to identify a monotone decline**.

**Ecological takeaway:** the empirical PEM enrichment is a **local and pooled community-size phenomenon**, not established vegetation-driven partner-network rewiring or longer-term stability of specific physical-site taxon identity. Broader interannual site recurrence appears in both wetland classes and may reflect unmeasured persistent microhabitat (hydroperiod, shoreline, water depth, acoustic transmission), but no evidence attributes it causally to plants.

Do not collapse source survey call data into true demographic occupancy, successful recruitment, residence of specific frogs, direct interspecific interaction or a true ≥3-taxon trophic web. Static current NWI geometry is not a field inventory of 2001–2015 live wetland vegetation.

## Immutable source, audit and repository outputs

- New locked ecological question before new result: `exploration/NAAMP_VEGETATION_TEMPORAL_ANCHORING_DECAY_SPEC_2026_10_23.md`.
- New executable: `exploration/run_naamp_vegetation_temporal_anchoring_decay_v0_1.py`.
- Completed source scientific computation: [GitHub Actions #39902559322](https://github.com/zuizui0223/frogcs/actions/runs/39902559322), [original complete result artifact #12479102856](https://github.com/zuizui0223/frogcs/actions/runs/39902559322/artifacts/12479102856).
- That full original run is UI-marked FAILURE because the last validation step asked for nonexistent top-level key `original_source`; the actual source key is `original_temporal_source`. A previous partial attempt similarly failed on interpreting 0/1 observer code as Boolean mask; this was fixed without changing source cohort or scientific model definition. The expensive real scientific step itself succeeded.
- Original workflow QA corrected; full rerun available on manual dispatch or scientific script changes. Source aggregate safely persisted: `exploration/NAAMP_WETLAND_INTERANNUAL_ACOUSTIC_MEMORY_DECAY_AGGREGATE_2026_10_23.json`.
- **Independent and successful immutable artifact readback**: [GitHub Actions #39902993685](https://github.com/zuizui0223/frogcs/actions/runs/39902993685), which fetched the original complete numerical artifact, verified source 2,403/273/20, all four full estimates, interval bounds, FDR family, 4,999 route null tests, same-observer covariates and exact match to permanent aggregate. This is output QA, **not** independent ecological replication.
- The same NWI 5,147-site and original NAAMP 6,236-run source and JAE RC6 main/Supporting Information/manuscript remain untouched.

No literature search or prediction result is represented as positive biology in this work.
