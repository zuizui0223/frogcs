# Frog acoustic community assembly through seasons: mapped emergent wetland enrichment and temporal complementarity

**2026-10-23 — completed real-data macroecology, no predictions or literature review.** Original USGS NAAMP 2001–2015 species calling-index records joined to USFWS NWI 250-m mapped wetland categories, preserving the original response-blind source and physical monitoring-station identities. This is **exploratory reanalysis on the same previously examined source**, not preregistered independent replication, a plant manipulation or an estimate of frog demographic occupancy. The manuscript JAE RC6, Supporting Information, release and `main` remain untouched.

## Main supported ecological result

**Within the same calendar year and across precisely the same physical monitoring stops, frog acoustic taxon pools at NWI-mapped emergent PEM wetland stations contain more source taxa from combining two distinct survey rounds than comparably sized pools of other already-mapped wetland stations.** Importantly, this is not solely a cross-sectional richness difference: the **absolute additional temporal complementarity component**, calculated by holding monitoring-station sampling effort and *two* observation rounds identical, is also positive.

This is an observation about **temporally complementary acoustic detections of taxon units** at mapped wetland habitat classes. It does not demonstrate living emergent plants cause breeding habitat selection, true species colonization, increased relative taxon turnover, animal facilitation, or any direct multi-taxon ecological interactions.

### Exact matched source and expectation, with hierarchy preserved

- Original source census: 7,848 standardized ten-stop survey runs, 6,236 NWI/temperature/noise complete source route-nights and 5,147 original mapped SiteIDs on 499 physical routes /20 US States; geographically source-only audited in [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Strictly same route, same calendar year, **same ten ordered physical SiteIDs**, ≥2 actual monitoring rounds and ≥2 NWI-mapped PEM and ≥2 nonPEM *within mapped wetland* stops. Directly reused source cohort from previously verified seasonal study [#39904251155](https://github.com/zuizui0223/frogcs/actions/runs/39904251155): **2,869 visits, 1,115 route×calendar-year metacommunities, 274 independent physical routes, 20 States**.
- Enumerate *every* unordered pair of sampled protocol rounds in a route-year: **2,475** two-round comparisons (668 round1–2, 647 round1–3, 725 round2–3, and 435 across combinations with sparse round4). Data from 2-,3-,4-round route-years yield 1,3,6 pair combinations, respectively. Those multiple pair combinations are averaged **first within route-year**, and route-years are then averaged within each **physical route**; the ultimate independent inference unit is the 274 routes.
- A site is **one of the same exact physical stations across both round visits**, and m=min(#mapped PEM stations,#other mapped wetland stations), m=2..5, is used in both vegetation categories. Analytic no-replacement rarefaction **chooses the same m physical monitoring stations in both acoustic rounds**, rather than letting each round independently select different physical stations. Preserve all NAAMP taxon labels including source complexes, acoustic zeros, original CI≥1 and CI≥2 thresholds.

For a taxon label t within mapped habitat h: k_early sites heard in round A, k_late in round B, k_union sites heard in **at least one** of those rounds at the same physical station. `P0_x=C(n−k_x,m)/C(n,m)` with 0 when `n−k_x<m`. Then the exact `G_early=Σ(1−P0_early)`, `G_late`, `G_two=Σ(1−P0_union)`, and temporal complementarity bonus `B_h=G_two−(G_early+G_late)/2`. Algebraically this is `(E later-only acoustic labels + E early-only acoustic labels)/2`. Entire measurement validated against all possible matched m-site subsets of source-free synthetic communities.

## Four pre-fixed empirical results: two-round cumulative acoustic gamma and the temporal bonus

All numbers below are equal-physical-route averages over the original **1,115** route-years, using four predeclared route cluster Student-t tests with **4-test BH correction**, 4,999 whole-route sign flips, State-equal/State-cluster intervals and 20 leave-one-State-out estimates.

| Source ecological outcome: PEM minus other wetland | CI≥1 any calls | CI≥2 strong calls |
|---|---:|---:|
| **Two-round cumulative rarefied gamma ΔGtwo** | **+0.43791 taxon units** | **+0.33082** |
| ΔGtwo 95% route CI | +0.32220 to +0.55362 | +0.23679 to +0.42485 |
| ΔGtwo 4-test BH q | **4.91×10⁻¹²** | **6.18×10⁻¹¹** |
| **Temporal bonus ΔB beyond average one-round gamma** | **+0.12780 taxon units** | **+0.12826** |
| ΔB 95% route CI | +0.07680 to +0.17879 | +0.08470 to +0.17182 |
| ΔB 4-test BH q | **1.41×10⁻⁶** | **2.48×10⁻⁸** |
| ΔB whole-route signflip P (4,999 draws) | **0.0002** | **0.0002** |
| ΔB 20-State 95% CI | +0.05177 to +0.20607 | +0.06143 to +0.17038 |
| ΔB State means positive | 16 of 20 | 18 of 20 |
| ΔB mean remains positive when one State omitted | 20/20 omissions | 20/20 |

All four routes/states/FDR/signflip predefined endpoint gates passed; the pre-readback primary classification is **`exploratory_positive_PEM_temporal_acoustic_complementarity`**. The same source is being reused, so this does **not** provide independently collected biological validation. Statistical association of **absolute** temporal bonus may reflect larger available species pools or different acoustic detection probabilities, rather than a truly increased proportional ecological replacement rate.

Original Actions [#39905766189 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39905766189); [original complete result artifact #12480583178](https://github.com/zuizui0223/frogcs/actions/runs/39905766189/artifacts/12480583178).

### Decompose the two-round pool surplus

| Equal-site-and-round acoustic taxon pool (CI≥1) | PEM mapped wetland | Other mapped wetland | PEM additional |
|---|---:|---:|---:|
| Average single-round gamma | 2.67496 | 2.36486 | **+0.31011** |
| Two-round union gamma | **4.41397** | **3.97606** | **+0.43791** |
| Bonus above average single-round pool | **1.73900** | **1.61121** | **+0.12780** |
| "Only later-round detected" acoustic taxon labels | 1.97879 | 1.79682 | **+0.18197** |
| "Only earlier-round detected" labels | 1.49922 | 1.42560 | **+0.07362** |
| Descriptive mean `B/G_two` among nonempty pools | ~38.49% | ~39.83% | Not same per-route-year paired denominator |

The identity is exact: `+0.43791 = +0.31011 + +0.12780` and `+0.12780 = (+0.18197 + +0.07362)/2`. "Later-only" and "earlier-only" mean acoustic detection windows; they are NOT colonization/competitive displacement or local extinction.

The robust absolute difference **does not imply a larger *relative* seasonal turnover rate at PEM**. In the explicit post-readback, exactly paired route-year-round-pool descriptive comparison, only compare ratios when both habitats' two-round gamma is nonzero. **2,443/2,475 CI≥1 round pairs valid**, spanning 1,104 route-years and 272 routes. The equal-route PEM-minus-nonPEM `B/G_two` difference is **−0.01354** (−1.35 percentage points); State-equal mean −0.01634, State mean sign negative in **15/20**. Strong CI≥2 matching uses 2,345 valid pairs, ∆ ratio −0.01034, 14/20 State means negative. No additional normalized-ratio hypothesis test was conducted, because that check was specified as descriptive/postreadback.

**Meaning:** vegetation-associated mapped PEM sites contribute a bigger absolute mosaic of temporally detected frog taxon labels because they contain bigger acoustic species pools; there is **no evidence yet that they have a higher proportional within-year turnover rate**.

## Taxonomic composition: temporal bonus is multi-taxon yet strongly genus-structured

An **after-positive-result** exact taxon-label decomposition was frozen separately, explicitly as accounting rather than any new tests. For each of all 2,475 original two-round pairs, the exact `d_t = b_t,PEM − b_t,otherwetland` is summed/averaged first within each route-year and then independent physical route. Every absent taxon contributes zero at the same source observation denominator. **Σtaxa d_t = +0.12779625975522307** CI≥1 and **+0.12826328471249396** CI≥2, the original full-community positive effects to 1e−10.

- **Any-call CI≥1:** 48 source taxon labels, **35 positive, 13 negative** signed mean bonus contributions. Positives sum +0.14180 and negatives −0.01400, net +0.12780. Largest one is 18.18% of sum of positive components; top five 54.26%. Omitting only the largest (*Lithobates clamitans*, +0.02578) leaves a descriptive **+0.10201** additional temporal bonus. This is mathematical influence, **not an adjusted statistical test after dropping this species**.
- Highest positive taxon labels: *Lithobates clamitans* +0.02578, *L. catesbeianus* +0.02069, *L. sylvaticus* +0.01385, *L. palustris* +0.00908, *L. pipiens* +0.00755. Negative examples include *Pseudacris crucifer* −0.00622. These individual labels are **not independently significant source discoveries**.
- Genus-prefix accounting reveals **`Lithobates` +0.08763 of the +0.12780 net** (about 68.6%); *Hyla* +0.02300 and *Acris* +0.01176 also contribute. Therefore the acoustic bonus occurs across multiple monitored taxa **but is distinctly taxonomically concentrated** in one prefix. Original taxon complexes and genus prefix groupings are NOT a phylogenetic comparative analysis, independent evolutionary replicates or mechanistic pollinator-like niche partitioning.
- **Strong-call CI≥2:** 48 labels, 36 positive and 12 negative; largest contributor again *L. clamitans* +0.02313. Largest-one positive fraction 17.00%, top-five 47.26%, original bonus excluding largest descriptor +0.10514. Absolute species-level sums and linked source round-pair cells verified to 1e−10.

New taxon-sum and paired proportional check [Actions #39906468671 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39906468671), [full result artifact #12480244019](https://github.com/zuizui0223/frogcs/actions/runs/39906468671/artifacts/12480244019). These are source-linked numerical decompositions, **not independent new ecology hypotheses tested after positive results**.

## Integrate, rather than overwrite, previous macro vegetation results

The previous same-source observational hierarchy (all originally audited and retained):
1. **Local acoustic alpha:** PEM +0.2715 monitoring taxon units/stop matched within ten-stop night (388 routes); +0.2378 after adjusting other mapped habitat classes, overall wetland fractional area, source stop temperature/noise and within-night FE (499 routes).
2. **One-round equal-effort gamma:** within mapped wetlands PEM +0.2984 taxon units per identical number of source stations (281 routes), after exact rarefaction; broad positive taxon contributions across 39/48 labels but genus concentration.
3. **Spatial covariance hierarchy:** positive PEM×frog acoustic richness covariance at within-night physical stops (+0.04082) but negative among State means (−0.01257), a descriptive ecological scale reversal.
4. **Dyadic animal-call network:** 199-draw original fixed-margin NWI site co-detection pair identity network with 120 CI>=1 eligible pairs /269 routes found NO robust PEM-driven global partner identity excess after route-vector sign flips (route P=.3276 vs run-independent nominal P=.005).
5. **Interannual same-physical-site calling identity:** exact 2,403 repeated-year source pairs/273 routes had positive acoustic site recurrence beyond random rematching of other within-vegetation-class physical stations in both PEM and other wetland habitats, but PEM-specific advantage absent; a subsequent within route×round adjusted elapsed-year memory decline was not supported.
6. **Survey-round seasonal alpha and gamma modulation:** same physical 1,115 route-years/274 routes, nominal CI>=1 third-round PEM alpha increment +0.170, but categorical 4-test BH q=.0653 and geographic 20-State P=.126, so seasonal *PEM vs nonPEM strength modulation* not confirmed.
7. **NEW across-round temporal gamma complementarity (this analysis):** absolute NWI PEM acoustic taxon-pool enrichment accumulates when two monitored rounds are combined, and **the absolute additional taxon complementarity above average one-round diversity remains positive under route, State and four-test BH gates**. Relative complementarity `B/G_two` is instead slightly lower at PEM by descriptive paired comparison, so increased proportional species turnover is not supported.

**Ecological insight:** vegetation-linked wetland landscapes can have an acoustically richer **seasonal species pool**, detectable as taxon additions between scheduled frog calling surveys, without establishing stronger phenological species turnover **rates**, increased site occupancy/persistence, a measurable shift in which pair of taxa co-call, or any direct vegetation–animal causal pathway. Biological levels of organization (local alpha, spatial gamma, seasonal gamma/complementarity, physical site re-detection, identity-specific pair network) carry distinct information and must be analysed at their correct observational grains.

Static mapped NWI wetland polygon classes are not contemporaneous or taxonomically measured macrophytes; NAAMP calls depend on species breeding phenology, weather and detection; multi-source monitoring taxon labels are not verified independent evolutionary units; signs do not prove species-level tests; fish/insect predators are not co-measured; no direct frog competition/facilitation or any three-species trophic interaction is identified.

## Reproducibility and frozen authority

- Locked-before-new-outcome original protocol: `exploration/NAAMP_WETLAND_WITHINYEAR_TEMPORAL_COMPLEMENTARITY_SPEC_2026_10_23.md`.
- Locked **postreadback taxon audit protocol**: `exploration/NAAMP_PEM_SEASONAL_TAXON_CONTRIBUTION_POSTREADBACK_SPEC_2026_10_23.md`.
- Executables `exploration/run_naamp_wetland_seasonal_complementarity_v0_1.py` and `exploration/run_naamp_wetland_seasonal_taxon_contributions_v0_1.py`. Both workflows verified exact matched physical m-site hypergeometric source identities, route/year/pair integrity and scientific no-causality claim gates.
- Primary and four fixed tests verified [Actions #39905766189](https://github.com/zuizui0223/frogcs/actions/runs/39905766189) **SUCCESS**.
- Taxonomic decomposition and paired proportional bonus source-verified [Actions #39906468671](https://github.com/zuizui0223/frogcs/actions/runs/39906468671) **SUCCESS**.
- Permanent original primary numerics `exploration/NAAMP_PEM_WETLAND_TWO_ROUND_TEMPORAL_COMPLEMENTARITY_AGGREGATE_2026_10_23.json`.
- Permanent postreadback numeric components `exploration/NAAMP_PEM_SEASONAL_TAXON_CONTRIBUTION_AGGREGATE_2026_10_23.json`.
- No raw third-party NAAMP/NWI records committed; all analytical code, science interpretation and aggregates on isolated `exploration/naamp-wetland-seasonal-complementarity-2026-10-23` branch. Original JAE RC6 scientific authority in `main` left unchanged.
