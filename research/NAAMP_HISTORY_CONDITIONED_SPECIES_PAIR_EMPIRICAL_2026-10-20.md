# Actual NAAMP results: historical species×site preferences explain a limited part of taxon-pair segregation (2026-10-20)

**Status:** SOURCE-VERIFIED EMPIRICAL EXPLORATORY COMPARISON COMPLETE. **Original JAE `main` frozen and untouched**; this is **not** preregistered, independent replication, competitive-interaction evidence, proof of learning, or causal separation of historical habitat quality and competition.

## Central biological question

> **How much of the nonrandom allocation of frog species pairs among acoustic sites can be reproduced by each taxon's *strictly prior* recurring physical-site use, after holding each species' current number of calling sites and each site's current number of calling species fixed?**

This addresses **cross-taxon site segregation** (checkerboard C-score) and **is NOT the submitted JAE within-taxon multi-site concentration endpoint**. Multiple calling species detected in the same sequential stop survey are not necessarily calling simultaneously.

Original prespecified protocol: [PAIR_HISTORY_CONDITIONED_NULL_CONTRACT_2026-10-20.md](PAIR_HISTORY_CONDITIONED_NULL_CONTRACT_2026-10-20.md). The earlier [PAIR_HISTORY_WEIGHTED_IMPLEMENTATION_QA_2026-10-20.md](PAIR_HISTORY_WEIGHTED_IMPLEMENTATION_QA_2026-10-20.md) documents the **before-source** stage; this report supersedes its "empirical analysis not run" status.

## Real authoritative data and sample gate

Official USGS ScienceBase item `583dc314e4b0d1899f9dea8d` (Foreman et al., DOI `10.5066/F7G44NG0`), retrieved in real [GitHub Actions run 39383185451](https://github.com/zuizui0223/frogcs/actions/runs/39383185451), [verified original files artifact 12246202420](https://github.com/zuizui0223/frogcs/actions/runs/39383185451/artifacts/12246202420). SHA256 against archived model pins: original `Runs.csv` 2,194,381 bytes, `ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730`; `Stops.csv` 14,070,232 bytes, `28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f`; `Counts.csv` 17,214,148 bytes, `60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086`. **All 3 verified byte-for-byte.** Original citation: https://www.sciencebase.gov/catalog/item/583dc314e4b0d1899f9dea8d

After reconstructing the original 7,848 eligible runs / 4,236 paired comparisons and verifying all 6,074 previously archived paired-run C-score inputs against the **original taxon×10-stop detections**, retained 1,440 original informative pair comparisons. Exclusions for new historical-template requirement: 19 physical-site mismatches/incomplete support and 737 comparisons without ≥2 strictly earlier eligible complete same-route, same seasonal round, same SiteID surveys.

**Final analysis: 684 matched comparisons, 221 routes, 20 states**, involving 1,090 unique RunIDs and 45 operational taxon labels (511 observed taxon-pair combinations). Median eligible earlier same-physical-site history = **3 completed surveys** (range 2–15). The prespecified 200-comparisons/80-routes gate **PASSED**. These 684 comparisons are only ~16% of the original 4,236, so selection/representation is material.

## Two comparable distributions and prior data-only weighting

- **A: Uniform fixed-fixed Curveball null** retains observed taxon row incidence breadth and site column calling-richness totals.
- **B: Historical site-weighted, fixed-fixed null** retains the same margins while giving matrix probability proportional to `exp(sum(Y_sj × logit((prior_sj+0.5)/(prior_n+1))))`, using only physically matched same-season surveys with year strictly **less** than the earlier of the two focal survey years. A taxon unseen in prior surveys receives constant site weight, preventing artificial preference.
- Both use the same 684 focal comparison pairs, two independently seeded chains × 256 retained draws per run/history context; initial 100×max(3,n_taxa) and between-draw 20×max(3,n_taxa) trades. Null samples preserve all row and column totals. No pairwise interaction parameter enters distribution B.
- (E) is observed taxon-pair checkerboard C-score minus that model's expected C-score. Primary comparison is A's remaining (E) minus B's remaining (E), equivalently B expected C minus A expected C, **route-equal** across 221 routes. Cluster-bootstrap 95% intervals (2,000 resamples), conditional on estimated historic weights and finite null simulations.

## Empirical primary results

| Identical 684 pairs and 221 routes | Route-equal segregation excess or change | Route-bootstrap 95% interval |
|---|---:|---|
| **A uniform fixed margins: observed minus expected C** | **+0.077103** | **[+0.054695,+0.100958]** |
| **B historical taxon×site fixed margins: observed minus expected C** | **+0.065780** | **[+0.044621,+0.088578]** |
| **B-minus-A expected C / reduction in residual** | **+0.011323** | **[+0.003778,+0.019416]** |

**Observed segregation exceeds both fixed-margin nulls. Species-specific historical SiteID use increases expected segregation relative to the uniform null and therefore accounts for a limited, supported part of the observed excess.** The residual decline is descriptively **14.7%** of the uniform-excess point estimate, not a causal explained fraction or mediation estimate. A substantial **+0.0658** residual remains with its full route-bootstrap interval positive, so stable historical site preference is **insufficient** as a sole statistical generator of observed species-pair placement.

### Pre-specified sensitivity results

- **Same observer**, 537 comparisons / 188 routes: expected C change **+0.011637**, 95% CI **[+0.003466,+0.019887]**.
- **Earliest focal-pair context per RunID**, 1,090 unique-run contexts across 221 routes: **+0.010616**, 95% CI **[+0.003024,+0.018934]**. This is a *run-context* sensitivity, not 1,090 independent paired survey comparisons.
- **Two independent source-specified MCMC chains** (same pair support): +0.011282 and +0.011363; neither chain difference suggests a sign reversal. This **does not prove complete MCMC mixing**.
- **Rain closer vs farther**: uniform-null segregation-residual difference +0.02459, 95% CI [−0.01852,+0.06816]; historical-null difference +0.02005, CI [−0.02060,+0.06391]. **No supported rain-related difference** in segregation strength in this restricted historical subset. Rain labels reflect cross-year rain recency, not controlled pre–post rainfall changes.

Independent validation on the exact saved files: separate script recomputed every pair identity, route-level weighting, taxon-pair weighted-contribution sums, and 5,000-bootstrap intervals with a distinct random seed. A's recomputed CI [+0.05433,+0.10132], B's [+0.04431,+0.08919], change [+0.00393,+0.01908], agreeing with the original 2,000-bootstrap inference. All original result-file SHA256 hashes passed. Exact enumeration of all 90 synthetic 4×4 fixed-margin arrangements independently verified the weighted MH sampler and detailed balance; **synthetic values are not frog effect estimates**. All 28 shipped unit tests PASS.

## Which species pairs contribute? Descriptive only

Signed contributions sum to the **route-equal** B residual. A large positive value means a pair contributes to the segregation surplus **after historical site-use adjustment**, while a negative value means relative co-occurrence. Opposing contributions can cancel. These are **post hoc, unadjusted, not significant competitive interactions**.

| Operational species pair | Contribution to B residual | Routes / unique runs with focal pair |
|---|---:|---|
| *Hyla versicolor* – *Lithobates catesbeianus* | +0.03527 | 95 / 246 |
| *Hyla versicolor* – *Lithobates clamitans* | +0.02494 | 103 / 280 |
| *Hyla chrysoscelis* – *Lithobates catesbeianus* | +0.01823 | 104 / 308 |
| *Lithobates catesbeianus* – *Lithobates clamitans* | **−0.06810** | 182 / 613 |
| *Lithobates clamitans* – *Pseudacris crucifer* | −0.01156 | 143 / 334 |

**Never interpret the positive pairs as antagonistic species competition or the negative pair as facilitation without site-level habitat/detection and direct biological tests.** Relative C-score contributions depend on conditional margins and which other species are in the matrix.

## What this adds to community ecology, and what it does not

**New limited empirical insight:** prior recurrent species-specific choice of physical locations predicts part, but only a minority, of an assemblage's degree-conditioned checkerboard segregation. Thus an acoustic community's pattern cannot be reduced to marginal species activity or site richness **and** is not fully predicted by its stable historical species×site preferences.

This is relevant to ecological assembly, historical contingency and niche partitioning, but the observational mechanism remains unresolved: spatially varying microhabitat, stable local populations, species-specific calling detectability, seasonal breeding differences and biotic interactions could all contribute to the persistent residual. The previous ERA5/MODIS study found rain/soil moisture linked to overall chorus magnitude but not supported to change the segregation contrast. Those data have mostly route-scale soil/water context and do not supply site×taxon microhabitat controls for this model.

It does **not** prove competitive exclusion, acoustic temporal niche partitioning, learning, fertilization/oviposition, demographic coexistence, a universal assembly law, or independent cross-programme replication. Route clustering does not model spatial dependence across routes. Interval uncertainty conditions on historical propensity estimates and finite randomization (does not propagate their full uncertainty). Historical sample eligibility heavily favors well-monitored, repeatable physical-site routes. Species complexes are operational labels, not necessarily genetically separated species.

## Reproducibility and deliverables

Source analysis package `NAAMP_history_weighted_null_ready_2026-10-20.zip` (source SHA256SUMS 19 members), official pinned original 3CSV ZIP, and all results plus independent QA are made available as a combined downloadable local handoff ZIP in the conversation. The original program enforces the 7,848/4,236/6,074/1,440 exact-match gates, stops on SHA mismatch, preserves historic-only time boundaries, produces 684 route-equal comparisons, all pair contributions, and two-chain sensitivity values.

[Original official retrieval workflow](https://github.com/zuizui0223/frogcs/actions/runs/39383185451). The initial missing-numpy retrieval CI failed; installing the reader dependencies repaired the workflow and the succeeding execution confirmed original file checksums. **The NAAMP mechanism analysis itself ran in the current working environment, not a separately passed GitHub Actions job.** Keep historical analysis separate from submission-ready `main`.
