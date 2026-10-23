# Wetland habitat architecture versus frog acoustic metacommunity hierarchy — executed macroecology

**Date 2026-10-23.** New ecology-first observational analysis of original publicly monitored USGS NAAMP 2001–2015 calling records and original geometrically checked USFWS NWI 250-m wetland polygons. Not a prediction exercise, new literature search, experimental manipulation or independent external validation. Both new questions were **post-hoc**, frozen before their respective result readbacks. Frozen JAE RC6 submission/main untouched.

## Main biological findings

**(A) Additive/saturating plant-habitat structure, not demonstrated synergy.** When restricting analysis to stops already geographically mapped as wetland, PEM-associated local calling richness remains positive **with or without** a woody/shrub wetland polygon in the same 250m station buffer. The specific PEM×woody factorial interaction is small and not statistically distinguishable from zero across **499 physical routes** and **20 States**.

**(B) The PEM-associated acoustic richness surplus has two different ecological layers: an increased probability of any call at a stop, and more additional taxon units heard at already activated stops.** For all calling (CI≥1) the additional-taxon count component makes up **63–68%** of the linear coefficient; for strong calls (CI≥2), the probability of at least one strongly calling taxon is the larger component (~57–66%). These are **exact statistical accounting identities**, not proof of social frog-frog facilitation or causal environmental effects.

**(C) No supported structure×structure nonadditivity implies the larger gamma diversity previously documented in PEM cannot be attributed to a demonstrated nonlinear effect of overlapping PEM+woody NWI categories.** The earlier 2–5-stop exact rarefaction plus within-wetland taxon pool finding remains a strong exploratory *descriptive* pattern, not a mechanistic inference.

## Source, population and habitat 2×2

Same original complete source **7,848 standardized NAAMP route-run nights**, **6,236** nights fully NWI-matched with ten stops, **62,360** site×night observations, 5,147 mapped NWI physical SiteIDs and 499 routes across 20 US States. Primary analysis restricts to **57,821 mapped-wetland site×night observations**; 6,236 nights /499 routes /20 States remain (0 source nights lost for having fewer than two mapped wetland stops).

NWI PEM-emergent category P and woody/shrub wetland category W intersect within a 250m stop buffer. All four wetland categories were represented across the original full source:

| Map class at stop | Site×night records in analysis | Distinct wetland physical SiteIDs | Independent routes |
|---|---:|---:|---:|
| Neither PEM nor woody | 18,503 | 1,611 | 394 |
| Woody but no PEM | 23,477 | 1,833 | 424 |
| PEM but no woody | 5,169 | 439 | 211 |
| Both PEM and woody | 10,672 | 839 | 323 |

These are overlap classes, **not distinct living macrophyte species or physical habitat intervention treatments**.

## Spatially adjusted nonadditivity tests

Original before-outcome-fixed **16-predictor within-survey-night fixed-effects count-mean** model:
PEM map overlap (binary), woody map overlap (binary), **PEM×woody**, aquatic-bed overlap, mapped total wetland fraction (per +10pp), local air temperature, sound masking, and nine stop-position dummies. Whole routes are equally weighted; route- and 20-State-cluster sandwich Student intervals. Two interaction tests (CI≥1 and CI≥2) adjusted by BH.

| Calling outcome | PEM effect with woody absent (95% route CI) | PEM effect with woody present (95% route CI) | **PEM×woody interaction (95% route CI)** | BH q |
|---|---|---|---|---:|
| CI≥1: any call | **+0.20460** (+0.13911 to +0.27009) | **+0.23351** (+0.18305 to +0.28398) | **+0.02891** (−0.04951 to +0.10734) | **0.50019** |
| CI≥2: strong calling | **+0.12737** (+0.07917 to +0.17557) | **+0.14717** (+0.11099 to +0.18334) | **+0.01980** (−0.03785 to +0.07745) | **0.50019** |

None of the two interaction confidence intervals excludes zero under either route **or 20-State** clustering. Even when restricting to the **1,256 route-run nights /89 routes /19 States where all four mapped classes occurred on the exact same ten-stop visit**, the raw full-four-cell difference-in-differences was −0.08445 (CI≥1, route CI −0.25913 to +0.09023, P=.339) and −0.06946 (CI≥2, CI −0.19366 to +0.05475, P=.269), both unsupported. These raw results differ in sign from the adjusted models; do not claim a positive architecture interaction.

The positive PEM main conditional effect remains positive in both woody strata and its 20-State sandwich CI excludes zero in both calling thresholds; however, the class variables are partially overlapping and possible unmeasured water depth, shoreline complexity, hydrology and acoustic detectability persist.

## Exact decomposition: habitat association at site activation versus multi-taxon calling

For each outcome, fit the **same 57,821 wetland-site source rows, same 16 covariates, same nights, same weights** to three responses satisfying an identity at every stop:

  # calling taxa Y = 1{Y≥1} + max(Y−1,0).

Every habitat coefficient and every PEM conditional effect must therefore satisfy the same additivity identity, verified numerically (absolute error under 10⁻⁹) in original real-data GitHub Actions.

| Fixed PEM habitat contrast | Count difference Y | At least one caller Δprobability | Additional callers beyond the first Δcount | Extra-taxon share of the signed count coefficient |
|---|---:|---:|---:|---:|
| CI≥1, no woody | +0.20460 | +0.07652 (95% route CI +0.05295 to +0.10008) | +0.12809 (+0.07734 to +0.17883) | **62.6%** |
| CI≥1, woody present | +0.23351 | +0.07498 (+0.05704 to +0.09292) | +0.15853 (+0.11827 to +0.19880) | **67.9%** |
| CI≥2, no woody | +0.12737 | +0.08432 (+0.05909 to +0.10954) | +0.04305 (+0.01365 to +0.07245) | **33.8%** |
| CI≥2, woody present | +0.14717 | +0.08418 (+0.06442 to +0.10394) | +0.06299 (+0.04058 to +0.08540) | **42.8%** |

CI≥1 has higher **multi-taxon acoustic incidence per actively calling wetland station** in the *expected additional-taxon component*, while CI≥2 shows more weight on *whether a strong caller occurs at all*. This is a descriptive decomposition of unobserved frog acoustic species units, NOT independent hypothesis tests for social attraction or frog habitat preference. The percentage shares are algebraic signed contributions, not causal mediated proportions, not vegetation type species interaction and not explained variance.

The PEM×woody interaction itself decomposes as CI≥1:
  +0.02891 = −0.00154 activation + +0.03045 extra taxon units;
CI≥2:
  +0.01980 = −0.000138 activation + +0.01994 extra.
Because the full interaction is nonsignificant, do not read the extra-taxon numerical sign as proof of synergy.

## How the hierarchy connects to the preceding genuine macroecological results

The prior source-backed NAAMP×NWI exploration established:
1. Same-night **local alpha richness** positive with PEM (CI≥1, route-average +0.27150 taxa per stop in 388 routes), and positive after controlling all mapped context (+0.23777 with 499 routes).
2. Same-size 2–5-stop **pooled gamma** positive PEM vs no mapped PEM (+0.33184, 286 routes). **Within mapped wetlands only**, PEM still +0.29837 (95% +0.23243 to +0.36430, 281 routes).
3. Exact taxon-label accounting of this within-wetland gamma contrast found **39 of 48** labels with positive signed mean contributions, with no single taxon responsible for most of the increased pool.
4. Pooled community **nestedness-resultant** accounts for ~59% of mean Sørensen compositional difference for the earlier PEM/nonPEM matched-pool comparison. This is not historical colonization or competitive replacement.
5. Spatial covariance hierarchy: PEM×frog richness signed covariance positive **among stops within a night (+0.04082)** but negative among State means **(−0.01257)** in State-equal population, a retrospective cross-scale sign reversal. An acoustic two-taxon fixed-margin residual and an actual three-taxon causal biological effect are not equivalent.

The new result reinforces a narrow, useful ecological spine: **mapped emergent wetland structure is associated with an acoustic metacommunity that contains more calling taxon units even inside an existing wetland; this is broadly distributed and not demonstrably dependent on a nonlinear overlap with mapped woody wetland cover.** Which component matters depends on calling threshold (first activation versus further co-detection).

No evidence in these NWI data identifies true botanical species, plant-caused fitness effects, actual hydroperiod, fish/insect predation, frog-frog cooperation/competition or an irreducible multi-species higher-order biotic effect. Taxon label complexes and acoustic detection confound species independence and occupancy. All evidence is observational and has already been explored in multiple post-readback analyses; these are NOT independent confirmations.

## Auditable actions and durable aggregate

- Pre-outcome primary category nonadditivity spec: exploration/NAAMP_PEM_WOODY_WETLAND_ARCHITECTURE_INTERACTION_SPEC_2026_10_23.md.
- Post-outcome component accounting spec: exploration/NAAMP_PEM_LOCAL_ENRICHMENT_ACTIVATION_VS_MULTITAXON_SPEC_2026_10_23.md.
- Executable: exploration/run_naamp_pem_woody_architecture_hierarchy_v0_1.py; exact identity and source gates in .github/workflows/naamp_pem_woody_architecture_hierarchy.yml.
- [Original factorial workflow #39889716491 (SUCCESS)](https://github.com/zuizui0223/frogcs/actions/runs/39889716491).
- [Final component recompute and independent QA #39890059482 (SUCCESS)](https://github.com/zuizui0223/frogcs/actions/runs/39890059482), [numerical artifact](https://github.com/zuizui0223/frogcs/actions/runs/39890059482/artifacts/12473894279).
- Persistent source-checked aggregate JSON: exploration/NAAMP_WETLAND_ARCHITECTURE_AND_ACOUSTIC_HIERARCHY_AGGREGATE_2026_10_23.json.

All analyses on exploration/naamp-wetland-architecture-interaction-2026-10-23. Frozen JAE RC6 main, manuscript, Supporting Information and submission untouched.
