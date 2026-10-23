# NAAMP × NWI: seasonal frog acoustic community assembly in wetland vegetation — absolute enrichment with relatively less replacement

**2026-10-23 — completed real-data macroecological analysis; two successful independent numerical recomputations.** No prediction, added literature reanalysis, new field collection or plant manipulation. This is an **exploratory analysis of the SAME previously examined 2001–2015 USGS NAAMP monitoring database** joined to the original USFWS NWI **250-m mapped wetland polygon overlay**, not a separate source validation or preregistered inference. JAE RC6 original submission, manuscript, SI and `main` remain completely frozen.

## Ecological claim: scale matters, and temporal taxon-pool gain is not replacement rate

**Mapped PEM-emergent wetland stations contain a larger frog acoustic taxon pool when distinct calling rounds are combined, but in the subset where both vegetation classes have calls in both rounds, their taxon identities are *less* replaced between rounds than in other mapped wetland stations.**

This is a non-obvious distinction between **absolute seasonal taxon accumulation**, **relative seasonal taxon replacement**, and **nestedness-related richness imbalance**. Acoustic calling records are taxon-level detection events, not demographic species turnover, persistent individual frogs, reproductive success or experimentally tested causal vegetation ecology. The relative replacement finding is conditional on both acoustic assemblages having detectable calls.

### Source, correct hierarchy and source-independent effort

Original underlying data before new acoustic outcome conditions:

- 7,848 standardized NAAMP ten-stop survey visits (2001–2015), of which 6,236 ten-stop visits have the original **12-shard outcome-blind 5,147-SiteID NWI 250-m crosswalk**, temperature and acoustic masking information; original source [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Geographically and temporally matched subgroup: **2,869 visits in 1,115 original physical route×calendar-year groups**, from **274 physical monitoring routes /20 US States**; same exact original 10 physical `SiteID` stations across 2–4 source `RunNumber` acoustic survey rounds and same original mapped wetland classes. Previous source study [Actions #39904251155](https://github.com/zuizui0223/frogcs/actions/runs/39904251155).
- Use all **2,475 unordered pairs of source rounds**, but round comparisons were averaged *within each route-year first* and then *within each physical route*. Each `SiteID`, route-year, selected station pair and amphibian monitoring taxon label is NOT treated as an independent geographic replicate.
- Compare **PEM+ emergent** mapped wetland stops to **other already NWI-mapped wetlands with PEM=0**, using the **same number of exactly 2 physical listening stations sampled without replacement** in both wetland strata. Two selected observation rounds are identical between habitat groups. Source taxon labels including complexes retained.
- Maps classify NWI polygon overlap within a 250-m buffer, **NOT vegetation species identities, measured 2001–2015 plant biomass, living macrophyte cover or experimental treatments**. The observer encounters listening stations sequentially.

## New six-test composition analysis and exact ecological definitions

Using exact without-replacement site probabilities, compute `g_e` acoustic taxon gamma on the earlier round, `g_l` on the later, and `g_U` on their union at the same physical stations. The original source-verified hypergeometric function `exact_two_round_pool(...,m=2)` was reused unchanged.

Expected counts for a taxon-labelled pair of source rounds (expectations over m-site subsets): `a=g_e+g_l−g_U` shared-across-round taxa; `b=g_U−g_l` earlier-only; `c=g_U−g_e` later-only. Then calculate **ratios of expected component counts**, explicitly **NOT the mean of per-subsample dissimilarity ratios**:

- Sørensen `β_sor=(b+c)/(2a+b+c)` (total acoustic temporal composition dissimilarity);
- Simpson turnover `β_sim=min(b,c)/(a+min(b,c))` (relative taxon identity replacement component);
- Nestedness-resultant `β_sne=β_sor−β_sim` (nonreplacement richness-imbalance component).

Exact `β_sor=β_sim+β_sne` was verified at source-run, physical-route and aggregate levels. Source-free synthetic QA enumerated **all two-site subsets** for perfect species replacement, true taxon-pool nesting, stable pools, entirely silent and only one round calling.

**Critical denominator choice, frozen before this new data readback:** every inferential round-pair must have **detected calling taxa in both actual rounds in BOTH vegetation categories**, and valid Simpson denominators. Do **not** impute fully or partially silent pools as zero-turnover or zero-nestedness. Exclusions are explicitly biological-outcome-conditioned, so conclusions only apply to acoustically active two-round assemblages:

| Calling threshold | Original matched round-pair opportunities | Both habitats × both rounds active | Excluded for silent/undefined compositional contrast | Eligible physical routes / States |
|---|---:|---:|---:|---:|
| CI>=1 all calls | 2,475 | **2,180** | **295 (11.9%)** | **267 /20** |
| CI>=2 strong calls | 2,475 | **1,621** | **854 (34.5%)** | **241 /20** |

## Primary empirical result: lower **relative temporal replacement** in PEM despite higher absolute taxa

| Within-year temporal beta, equal physical-route mean | PEM mapped wetland | Other mapped wetland | PEM − other |
|---|---:|---:|---:|
| **Simpson turnover β_sim**, CI>=1 | **0.57143** | 0.60355 | **−0.03212** |
| Sørensen β_sor, CI>=1 | 0.67259 | 0.70289 | **−0.03030** |
| Nestedness-resultant β_sne, CI>=1 | 0.10116 | 0.09934 | +0.00183 |
| Simpson turnover β_sim, CI>=2 | 0.62058 | 0.63604 | −0.01546 |
| Sørensen β_sor, CI>=2 | 0.70608 | 0.72141 | −0.01533 |
| Nestedness-resultant β_sne, CI>=2 | 0.08549 | 0.08537 | +0.00013 |

Full pre-fixed **six two-sided** route-clustered ecological endpoints, 4,999 physical-route sign flips and BH six-test correction:

| Contrast, PEM minus other wetland | Route effect | 95% route CI | BH q | 4,999-route signflip P | 20-State CI | Result |
|---|---:|---|---:|---:|---|---|
| **β_sim CI>=1 PRIMARY** | **−0.03212** | **−0.05364 to −0.01061** | **0.01071** | **0.0026** | **−0.09638 to −0.00361** | **Supported, exploratory** |
| **β_sor CI>=1** | **−0.03030** | **−0.04633 to −0.01427** | **0.00145** | **0.0002** | **−0.07428 to −0.01376** | **Supported, exploratory** |
| β_sne CI>=1 | +0.00183 | −0.01120 to +0.01485 | 0.93920 | 0.7814 | −0.01952 to +0.03146 | Not supported |
| β_sim CI>=2 | −0.01546 | −0.03858 to +0.00767 | 0.28381 | 0.1872 | −0.07066 to +0.10006 | Not supported |
| β_sor CI>=2 | −0.01533 | −0.03381 to +0.00315 | 0.20721 | 0.1044 | −0.07105 to +0.09338 | Not supported |
| β_sne CI>=2 | +0.00013 | −0.01145 to +0.01171 | 0.98266 | 0.9858 | −0.01614 to +0.00908 | Not supported |

For the CI>=1 primary Simpson result, mean effects were negative in **15/20 States**, and **all 20 leave-one-State-out route-average contrasts remained negative** (−0.03596 to −0.02793). Its corresponding 20-State CI excludes zero, so the originally frozen joint inference rule passes, yielding `exploratory_PEM_specific_temporal_acoustic_replacement`. This label means a **negative mapped-vegetation context contrast in acoustic Simpson replacement**, NOT increased biological replacement or causation. The **CI>=2 strong-call** study does not establish the effect; importantly, its source excluded 34.5% of otherwise geographically valid round pairs due to silent or undefined β assemblages.

The nestedness-resultant index difference was approximately zero. **Thus the supported CI>=1 reduction in overall normalized temporal dissimilarity is attributable primarily to the replacement component, not a stronger difference in the richness-imbalance component.** This is complementary to, not the same as, the earlier descriptive ~59% nestedness-resultant contribution of **spatial PEM-versus-nonPEM pooled assemblage dissimilarity**; earlier spatial β and the new **temporal β** compare entirely different axes. Do not falsely combine those percentages.

## Why an absolutely richer seasonal taxon pool can have lower relative replacement

On the CI>=1 **both-rounds-active conditional sample only**, equal-route mean two-round gamma union is:

- **PEM: 4.06018** acoustic monitoring taxon units across two visits;
- **Other mapped wetland: 3.59780** units;
- PEM advantage **+0.46237** units (descriptive conditional-sample contrast, not a newly separately tested endpoint).
- The temporal acoustic taxon bonus above mean early/later gamma is PEM **+1.61976** versus other **+1.47003** (difference +0.14973 acoustic taxon units, a conditional descriptive quantity).

At the same time, PEM **β_sim=0.571** vs other **0.604**. These can coexist: a larger absolute species-detection pool yields **more absolute additional labels** across visits, while a *smaller fraction of community dissimilarity is due to relative replacement*. This is a key macroscopic acoustic assembly finding, not evidence of animal demographic stability.

Interpretation must distinguish three observational hierarchies:

1. **Local acoustic alpha / spatial gamma:** Mapped PEM has a broad positive association with how many frog taxon units are heard, including +0.23777 local units/stop after prior landscape/environment adjustment and +0.29837 expected taxa in equal-effort, **within-mapped-wetland** pooled surveys, both on source monitoring data.
2. **Seasonal acoustic gamma / absolute bonus:** combining two original seasonal survey rounds increases PEM observed taxon pools more than other mapped wetland types, previous within-year result +0.12780 units beyond a single-round average in a matched two-to-five-site full-cohort comparison; separate strictly 1→2 round at same physical site gave +0.16193 taxon units relative PEM seasonal gain (274 routes, 20 States; six-test BH-supported secondary endpoint). These are **absolute** source acoustic taxon-incidence gains.
3. **NEW relative temporal β:** in source round pairs where both habitats are acoustically active in both rounds, **Simpson identity replacement and total Sørensen temporal dissimilarity are smaller in PEM**. The nestedness-resultant difference is nonsupported. Therefore **an ecosystem can contain more observable taxa across an acoustic season without showing greater proportional replacement between its calling windows**.

Further hierarchy layers from prior source experiments remain distinct: NWI PEM acoustic richness covariance positive **within** single route-night stop networks but negative among the 20 State means (observational scale reversal); previous fixed-margin conditional NWI frog taxon-pair co-detection network did not establish a route-robust PEM-specific partner rewiring effect; earlier same-physical-site interannual re-detection persisted in both PEM/nonPEM and adjusted elapsed-year decay was nonsupported. **No** plant→fish/insect→frog trophic mediation, irreducible three-species interaction, population stability, true animal movements or direct interspecific behavior has been measured.

### Caveats material to the conclusion

- **Activity-selected target population:** both taxonomic groups must have acoustic activity in both survey rounds. This preferentially selects more detectable communities and could itself alter apparent relative dissimilarity; only 2,180 of 2,475 CI>=1 and 1,621 of 2,475 CI>=2 round pairs remain. A result on active groups **does not estimate** relative turnover for absent/silent communities.
- **Ratios of expectations:** `β_sim` and `β_sor` are ratios of expected exact equal-two-site gamma overlap components, not an expectation/mean of individual hypergeometric subsample beta indices. They are valid defined observational metrics but interpretations should preserve the definition.
- **Post-hoc and multiple exploratory branches:** BH protects only the six tests in this specific locked-before-readback family, not an analysis-wide family spanning earlier repeated studies on the same NAAMP archive.
- **GIS static exposure:** NWI habitat polygons/PEM class are **not field-measured 2001–2015 vegetation**. Actual water permanence/hydroperiod, wetland structure and detection environment, phenology, fish/predatory insects, survey dates and monitor biases could explain these observational effects.
- **Ecological units:** NAAMP calling records are acoustic taxon detections, including taxon complexes, not established populations or direct species interactions; phylogenetic independence of species is not guaranteed. Route-level inferential clustering addresses repeated visits but does not yield causal attribution.

## Execution, repeatability, repo outputs

- Original new outcome contract (frozen before this calculation): `exploration/NAAMP_PEM_TEMPORAL_BETA_TURNOVER_NESTEDNESS_SPEC_2026_10_23.md`.
- Full reproducible script: `exploration/run_naamp_pem_temporal_beta_turnover_v0_1.py`.
- Same source historical GIS crosswalk [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- First complete independent GitHub Actions study [#39917395651](https://github.com/zuizui0223/frogcs/actions/runs/39917395651) **SUCCESS**, source numeric [artifact #12484994661](https://github.com/zuizui0223/frogcs/actions/runs/39917395651/artifacts/12484994661).
- Second complete GitHub Actions reexecution [#39916111616](https://github.com/zuizui0223/frogcs/actions/runs/39916111616) **SUCCESS on attempt 3**, after overcoming an intermittent NWI artifact Blob download fault; source numeric [artifact #12488836114](https://github.com/zuizui0223/frogcs/actions/runs/39916111616/artifacts/12488836114). These two runs are **numerical reproducibility of the same source, not independent biological replication**. Whole six-test metrics agree to at most 1×10⁻¹⁵ numerical absolute tolerance and source cohort/exclusion counts match exactly.
- Permanent full aggregate numerical receipt `exploration/NAAMP_PEM_TEMPORAL_BETA_TURNOVER_NESTEDNESS_AGGREGATE_2026_10_23.json`.
- Permanent two-run source tolerance audit `exploration/NAAMP_PEM_TEMPORAL_BETA_DOUBLE_EXECUTION_NUMERICAL_QA_2026_10_23.json`.

All source code, aggregate outcomes, exact mathematical QA and ecological interpretation are restricted to the `exploration/naamp-vegetation-temporal-beta-partition-2026-10-23` branch. Original `main`, frozen JAE RC6 manuscript, Supporting Information, submission and release authority remain unchanged. No raw third-party NAAMP/NWI records are committed.
