# Frog acoustic metacommunity assembly in wetland vegetation mosaics: a nested ecological hierarchy

**2026-10-23 — complete empirical follow-up.** No literature search and no predictive model. Real NAAMP 2001–2015 ten-stop frog acoustic records crossed with the same geographically validated USFWS NWI 250-m mapped polygon fractions used in the prior ecological macroanalysis. Published-study reanalysis/retrospective inference, **not preregistration, time-matched vegetation measurement, species experiments or independent replication**.

## Main result: PEM-enriched acoustic metacommunities, not just more sampling

When sampling **exactly the same number of 2–5 stops on each side of the mapped PEM category**, the expected size of the frog acoustic taxon pool is higher on mapped PEM sites.

| Paired, same-night equal-size sampled pools | Any calling (CI≥1) | Strong calling (CI≥2) |
|---|---:|---:|
| All geographically matched PEM+ vs PEM- stops | **+0.33184 taxon units** | **+0.23652** |
| 95% route CI | +0.26724 to +0.39644 | +0.18639 to +0.28665 |
| 6,236 complete NWI-linked source route-nights; eligible comparison subset | 3,717 nights / 286 physical routes | 3,717 nights / 286 routes |
| 20-State directional evidence | 19/20 State means positive | 18/20 |
| Eight-test BH q (4 overlapping NWI classes ×2 call thresholds) | **7.79×10⁻²⁰** | **1.68×10⁻¹⁷** |
| Sign after omitting each State in turn | 20/20 positive | 20/20 |

This is a **taxonomic gamma** contrast of two equally sampled multi-stop acoustic assemblages, not a comparison of unequal group area or independent individuals. Source: [original executed Actions #39885012263](https://github.com/zuizui0223/frogcs/actions/runs/39885012263) SUCCESS, [full run artifact](https://github.com/zuizui0223/frogcs/actions/runs/39885012263/artifacts/12472486082). Exact hypergeometric taxon inclusion probabilities match a brute-force combinatorial benchmark.

The aquatic-bed category was **underpowered for the ≥2-vs-≥2 site population** (11 routes; 198 nights across 5 States) despite its previously positive *single-stop* richness contrast; it is not a negative ecological result. Woody/shrub wetland had +0.15253 any-call gamma (313 routes), and generic all-wetland had +0.35659 (100 routes), both retrospective BH-supported but overlapping NWI habitats are not independent factors.

## Why group diversity differs: richness asymmetry and compositional replacement

For the primary all-stop-context PEM comparison (CI≥1), equal sampling gives route-balanced expectations:
- **2.6895** taxon units from the PEM group vs **2.3577** from mapped non-PEM;
- **1.8335** expected shared taxon units;
- **0.8560** expected PEM-only taxon units vs **0.5242** expected non-PEM-only;
- Difference **0.8560−0.5242 = +0.3318** exact algebraic identity.

These are *expectations over potential matched subsamples of actually observed calls* and do not mean those animal taxa were newly recruited into PEM patches.

Under **199 deterministic paired without-replacement m-site draws per 3,717 eligible route-nights**, and restricting the dissimilarity calculation to draws where both pooled assemblages contained a detected taxon:
- CI≥1 valid draw fraction **90.65%**, route-balanced `β_Sørensen = 0.26283`;
- turnover `β_Simpson = 0.10735`, nestedness-resultant `β_SNE = 0.15547`;
- **nestedness-resultant component = 59.15% of the total route-balanced Sørensen**, turnover = 40.85%.
- CI≥2 valid draw fraction **74.83%**, nestedness-resultant fraction **57.54%**.

Thus group dissimilarity has a large **relative species-richness/nestedness component**, not exclusively different species replacing one another. These are compositional index decompositions conditional on both groups yielding calls — **not an experimental mechanism, direct competitive sorting, or historical species-pool transition**. The source species IDs include taxon complexes.

## More conservative: PEM enrichment exists *within wetlands*

The previous comparison can include stations that were not mapped as any NWI wetland. A new specifically labelled **post-positive-result follow-up** restricted the comparison population to sites with mapped total-wetland NWI fraction >0, and compared PEM-positive versus PEM-negative within that wetland sample at the same m≥2 matched-stop count.

| Source-stratified wetland architecture | CI≥1 gamma excess (95% route CI) | Routes / States | 6-test BH q |
|---|---|---:|---:|
| **Any mapped wetland, PEM vs nonPEM** | **+0.29837** (+0.23243 to +0.36430) | **281 / 20** | **4.06×10⁻¹⁶** |
| Wetland with woody NWI polygon overlap | +0.32011 (+0.23255 to +0.40767) | 184 / 18 | 2.80×10⁻¹¹ |
| Wetland without woody overlap | +0.23779 (+0.10657 to +0.36900) | 68 / 13 | 0.000687 |

All three CI≥1 retrospective contrasts remain positive under route tests and geographic coverage gates; strong calling also has positive BH-supported contrasts (+0.21022, +0.22396, +0.12237 respectively), but strong CI≥2 under woody-absent only **barely passes** (q≈0.0497, route CI lower ≈+0.00015) and geographically only 7/13 States are positive. **Different significance levels between woody strata do not formally establish a PEM × woody interaction**; the two estimates must not be contrasted as a causal treatment mechanism.

Primary within-wetland PEM gamma in CI≥1 is positive across **19/20 States** and all 20 leave-one-State-out estimates, including raw survey eras 2001–09 and 2010–15 in the same direction. Geographic State remains a confounding/stratification factor, not random independent vegetation intervention.

Executed: [Actions #39885710342](https://github.com/zuizui0223/frogcs/actions/runs/39885710342) SUCCESS, [aggregate artifact](https://github.com/zuizui0223/frogcs/actions/runs/39885710342/artifacts/12472636153).

## The enrichment is a distributed taxonomic pattern, not one taxon's anomaly

A taxon-level exact decomposition of the primary **within-wetland PEM** contrast (CI≥1) shows the following signed, route-balanced contributions:

| NAAMP taxon label | Contribution to Δgamma taxon units |
|---|---:|
| *Lithobates clamitans* | **+0.04476** |
| *Anaxyrus americanus* | +0.02882 |
| *Pseudacris crucifer* | +0.02694 |
| *Lithobates catesbeianus* | +0.02668 |
| *Lithobates sylvaticus* | +0.02387 |
| *Hyla versicolor* | +0.01500 |

The full 48 recorded taxon labels contributing in this conditioned sample have **39 positive and 9 negative** mean contributions. Positive taxon components sum to **+0.30643**, negative to **−0.00806**, yielding the exact whole-community **+0.29837**. The single top contributor is **14.61% of the sum of positive contributions**, the top five account for **49.30%**. Subtracting the top `L. clamitans` contribution leaves a descriptive **+0.25361** gamma contrast. This is a mathematical influence audit, **not a new hypothesis test on 47 independently observed phylogenetic lineages**.

Genus-prefix aggregation of signed positive contributions (monitoring labels, not a fitted phylogeny) is distributed among *Lithobates* +0.14487, *Hyla* +0.05084, *Pseudacris* +0.04233, *Anaxyrus* +0.03508, *Acris* +0.02433. The sign counts and genera confirm broad taxon-label participation but cannot establish independent evolutionary replication.

In strong CI≥2, 37/48 taxon labels contribute positively and 11 negatively; largest contributor is *Pseudacris crucifer* +0.03881 of the total **+0.21022**, not the same top taxon as in the CI≥1 metric.

## Context within the preexisting ecological hierarchy

Different aspects of plant association reside at different observational/organizational levels, and should not be collapsed into one causal path:

1. **Stop (alpha diversity):** mapped PEM is associated with +0.27150 calling taxon units at a stop within same route-night (388 independent routes, 19/20 States positive). After simultaneously accounting for total mapped wetland fraction, woody and aquatic-bed indicators, temperature, noise and stop position, the PEM descriptive coefficient stays **+0.23777 CI≥1** (95% 499-route CI +0.19648 to +0.27906; 20-State CI above zero), with the original source population of 62,360 site×night measurements.
2. **Multi-stop pooled community (gamma diversity):** exact equal-effort rarefaction yields +0.33184 taxon units for PEM versus nonPEM, or +0.29837 **among mapped-wetland stops only**, with large nestedness-resultant dissimilarity share in the broader PEM composition sample.
3. **Geographic hierarchy:** static PEM within-night mapped cover varies strongly among stops (75.29% of variance), while local frog calling richness also varies among nights (~24.19%). Actual PEM–frog richness covariance is positive at stop level **+0.04082** but negative between State means **−0.01257** under State-equal weighting. This is a scale-dependent covariance sign reversal, not independent evidence for a causal sign reversal.
4. **Species and species-pair organisation:** in the prior NWI taxon-specific strong-calling screen, 5/25 monitoring taxon units had BH-positive PEM site affinity. Earlier fixed-margin route-heldout NWI acoustic pair network found 43/127 CI≥1 and 14/57 CI≥2 signed residual pair detections. They are **not measured interspecific interactions**; original global centred third-order excess was not established (P=.695 any; P=.108 strong).
5. **No plant boundary compositional segregation necessary:** the previously measured richness-adjusted single-stop PEM-boundary Sørensen contrast (+0.087 percentage points, route P=.714) was null. It does **not** refute higher **alpha and equal-sampling gamma** in PEM: assemblage size and conditional pairwise dissimilarity are distinct ecological statistics.

**Unifying positive empirical conclusion:** across this NAAMP monitoring network, vegetation-associated wetland structure co-occurs with **larger locally realized acoustic species pools**, and the taxonomic enrichment is broadly distributed across the detected frog fauna and occurs even among habitats already mapped as wetlands. A substantial portion of PEM/non-PEM pooled assemblage differentiation is **nestedness-resultant**, not species replacement alone, and the sign/scale of vegetation–richness covariation changes across State/landscape/site hierarchies.

The data **do not identify** direct plant manipulation, aquatic plant taxa or historical cover, hydroperiod, fish–odonate mediation, frog–frog competition, immigration, realized reproductive success, or irreducible higher-order biological interactions. State surveys are unbalanced, NWI geographic data are temporally mismatched, acoustic detections not true absences, and taxon complexes not phylogenetically independent species. All tests are exploratory; multiple scopes observed on the same source archive are not independent external replications.

## Reproducible source of truth and code

- Original source QA: [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Earlier vegetation taxon richness and covariance analyses: [#39879561078](https://github.com/zuizui0223/frogcs/actions/runs/39879561078), [#39880097620](https://github.com/zuizui0223/frogcs/actions/runs/39880097620), [#39880672474](https://github.com/zuizui0223/frogcs/actions/runs/39880672474).
- New full acoustic community composition: `exploration/run_naamp_rarefied_vegetation_gamma_v0_1.py` and [#39885012263](https://github.com/zuizui0223/frogcs/actions/runs/39885012263).
- New wetland-conditioned group and species contributions: `exploration/run_naamp_within_wetland_gamma_taxon_v0_1.py` and [#39885710342](https://github.com/zuizui0223/frogcs/actions/runs/39885710342).
- Compact numerical results that remain in git after Actions artifact expiry: `exploration/NAAMP_VEGETATION_GAMMA_ASSEMBLY_HIERARCHY_AGGREGATE_2026_10_23.json`.

Frozen JAE RC6 manuscript, Supporting Information, release authority and `main` unchanged. Future work should expand to genuinely measured wetland vegetative structures and species interaction data, rather than chase more p-values on the same static NWI class.
