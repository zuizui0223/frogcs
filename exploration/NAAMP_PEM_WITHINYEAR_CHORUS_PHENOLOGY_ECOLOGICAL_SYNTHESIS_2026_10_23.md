# Mapped emergent-wetland vegetation × frog acoustic-community seasonal hierarchy — NAAMP real macroecology

**2026-10-23: actual analysis complete, GitHub Actions SUCCESS.** Nonpredictive exploratory ecological analysis of USGS NAAMP 2001–2015 calling taxon lists crossed with the same original outcome-blind, 5,147-physical-SiteID USFWS NWI 250m mapped wetland polygons. Source survey archive had been repeatedly explored in earlier positive PEM acoustic alpha/gamma studies: this question is **post-hoc** (though its exact 4-endpoint analysis, source gates and significance rules were frozen before these new outcomes). Not a literature reanalysis, independent biological replication, experiment or live macrophyte phenological measurement. Frozen JAE RC6 main/manuscript/SI unchanged.

## Ecological focus: does vegetation-linked frog richness change through the breeding-season survey series?

Earlier real macro studies established that within the same 10-stop night, mapped NWI PEM emergent wetland stations had more calling frog taxon units than other stations (+0.27150 units/stop route-equal), and within *mapped wetlands only* +0.29837 units in exactly equal-size 2–5-stop rarefied taxon pools. The gain was distributed across many monitoring taxon labels. Subsequent fixed-margin PEM species-pair identity network and PEM advantage in **interannual** physical site recurrence were not route-robust.

The new question was whether **survey-round number (NAAMP RunNumber 1, 2, 3, 4)**—a broad within-year acoustic phenology proxy—systematically changes the *difference in frog acoustic richness between mapped PEM and other mapped wetland stations in the same physical route-year*. Survey rounds are not contemporaneous measured plant phenology, not equal calendar days or exact seasonal light/temperature across 20 States.

### Verified original source and same-physical-site controls

- 7,848 original standardized ten-stop NAAMP survey runs; 6,236 source NWI+temperature+sound-complete nights, 62,360 eligible stop×night measurements; original **5,147 physical mapped SiteIDs**, 499 source routes, 20 States and 12 geography shards from [source #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- From 2,678 route×year strata, drop duplicate route×year×round records (294 ambiguous cells; 660 run records) independently of frog outcomes. Require ≥2 distinct rounds, **exactly unchanged SiteIDs in all ten ordered stops** and mapped wetland class within each route-year, plus ≥2 PEM and ≥2 other NWI-mapped wetland stops. Result: **2,869 route-night observations / 1,115 fixed physical route-years / 274 independent routes / 20 States**. Survey round 4 has only **195 nights, 55 routes and 6 States**: geographic coverage is noticeably thinner than rounds 1–3 (844/924/906 nights).
- Each of the 1,115 retained route-years had ≥2 repeated rounds: 558 with 2 rounds, 475 with 3 rounds and 82 with all four. Dates of year progressed monotonically with source round order in all retained physical route-year groups. The DOY medians are round1 93, round2 128, round3 169, round4 188.
- Compare PEM-positive to PEM-unmapped within **already mapped NWI wetlands**, not all dry upland points. Use zero-inclusive taxon counts and exact no-replacement matched m-site rarefaction for taxon pool gamma. Preserve all monitoring taxon labels including complexes; counting detected frog taxa is **not abundance, reproduction or true occupancy**.

## Statistical hierarchy and why it is not a predictive model

For each same-route/year monitoring visit, compute a **within-night PEM minus other wetland acoustic difference** in (1) mean count of CI≥1 calling taxa, (2) CI≥2, (3) exactly m-site rarefied gamma CI≥1, (4) CI≥2. Model these four acoustic contrasts by **within-route×year fixed effects** and the three protocol-round indicator contrasts **round2−round1, round3−round1, round4−round1**, while controlling instantaneous stop-group temperature difference and acoustic noise difference. Every physical route contributes equal total observation weight; physical **routes**, not 2,869 monitoring nights or 28,690 stops, provide independent inferential clusters. Report:
- three-degree-of-freedom route-sandwich Wald F test and 20-State-sandwich F as geographic sensitivity;
- 4,999 physical-route 3-vector FWL-nuisance-score sign flips for another route-level observational null;
- Benjamini–Hochberg over all **four** originally declared omnibus endpoints;
- no testing chosen after the outcome of the nominal round3 contrast.

The actual sampled source met all pre-fixed identifiability gates: e.g. same physical route-year records jointly containing round1/2 occur on **224** routes, round1/3 on **235** routes, and round1/4 on **45** routes. Round4's 6-State composition still limits extrapolation.

### Result A: descriptive seasonal acoustic richness surplus

| Protocol round | Survey-night records | States | Median DOY | Raw route-balanced PEM−other wetland CI≥1 alpha | Raw route-balanced equal-m gamma CI≥1 |
|---|---:|---:|---:|---:|---:|
| 1 | 844 | 19 | 93 | **+0.18778** | **+0.21315** |
| 2 | 924 | 20 | 128 | +0.27974 | +0.30924 |
| 3 | 906 | 20 | 169 | **+0.34761** | **+0.40066** |
| 4 | 195 | 6 | 188 | +0.22329 | +0.28878 |

**All four raw round-specific sample means are positive**, consistent with PEM enrichment in the same source archive. These means are **not** balanced over the identical set of routes across four rounds and must NOT be interpreted as a causal increase/decrease in live vegetation or independent statistical evidence for each round. Especially round4 is geographically restricted.

### Result B: full adjusted seasonal variation is not confirmed

| Frozen omnibus endpoint | Adjusted round2−round1 | Adjusted round3−round1 (95% route CI) | Adjusted round4−round1 | 3-df route F P | 4-test BH q | 20-State F P | Route-score-flip P |
|---|---:|---|---:|---:|---:|---:|---:|
| **CI≥1 alpha (primary)** | +0.08667 | **+0.17010** ( +0.05565 to +0.28454 ) | −0.06767 | **.01632** | **.06527** | **.12607** | .0008 |
| CI≥2 alpha | −0.01799 | −0.00446 (−0.08748 to +0.07856) | −0.11449 | .36991 | .49321 | .30504 | .1864 |
| CI≥1 rarefied gamma | +0.07147 | +0.19305 (+0.00649 to +0.37960) | +0.05610 | .23594 | .47188 | .43880 | .0732 |
| CI≥2 rarefied gamma | −0.01039 | +0.01585 (−0.13258 to +0.16429) | −0.01076 | .97907 | .97907 | .94422 | .9582 |

**Classification: `not_supported_by_joint_withinyear_multilevel_gates`.** The source has a potentially meaningful early-to-middle-round CI≥1 acoustic-alpha PEM surplus increment, but the **four-outcome FDR q=.0653** and the **20-State F P=.126** do not pass the frozen joint inference rule, and these results were built on the same archive used to suggest this line of analysis. The individual nominal round3 interval alone does not justify a publication-ready general seasonal effect. The observed **within-route-year categorical shape may be non-monotone** (round4 nominal declines, with sparse coverage); a simple positive linear seasonal slope is not supported: CI≥1 alpha +0.05291 per round, route CI −0.00044 to +0.10625; CI≥1 gamma +0.07477, CI −0.01314 to +0.16268.

#### Components of the exploratory round3 alpha difference

The within-night difference in taxon units satisfies at *each actual stop*:

`# acoustic taxa = 1{≥1 calling taxon} + max(# acoustic taxa−1,0)`.

Exactly the same source/time/space model gives at nominal round3 vs round1:
- CI≥1 adjusted PEM surplus difference **+0.17010** = **+0.03033** in probability of >=1 recorded taxon + **+0.13976** in additional detected taxon units beyond the first.
- Thus ~82.2% of this particular *post-readback numerical round3 coefficient* is in the **additional-taxon component**, not the first call-activation component.
- All five fixed predictor coefficients obeyed the exact additive identity to floating-point precision. This is an *algebraic component decomposition of a globally nonsupported seasonal omnibus*, not a separately supported species-interaction mechanism. The CI≥2 round3 alpha contrast was effectively zero.

Original same-observer (nonmissing ObserverTrackingID) sensitivity preserved **2,812 rounds /1,098 route-years/271 physical routes**. CI≥1 categorical omnibus remained nominally P=.029 with **State P=.211**; the adjusted round3–round1 beta was +0.15683. This neither provides independent confirmation nor overcomes the predeclared State/BH gates.

## Connect to the verified vegetation ecological hierarchy

The result refines, but does **not erase**, previous positive macro findings on this monitoring network:

1. **Local habitat & alpha richness:** mapped NWI emergent wetland class is positively associated with acoustically detected frog taxon counts, including after adjusting other mapped wetland types, within-night route conditions and source stop temperatures/noise (PEM +0.23777 taxonomy units/stop, 499 routes).
2. **Area-matched taxon pool gamma:** within any NWI-mapped wetland class, emergent PEM sites have **+0.29837 expected taxa** compared with non-PEM wetland sites for equal-size m-site samples, 281 routes. Gains are distributed across many monitored taxon labels.
3. **Spatial hierarchy:** mapped PEM × acoustic richness covariance concentrates within stops of one route-night; it is positive locally but the **State-mean component is negative** (descriptive cross-scale reversal).
4. **Specific acoustic pair identity:** after fixing complete taxon and stop-richness margins, no route-robust *global PEM-dependent taxon-pair rewiring* signal survives.
5. **Interannual physical-site identity:** exactly the same frogs are **not** individually identifiable; calling taxon identities at physical wetland stops recur beyond within-category site swaps in PEM and nonPEM alike. But the PEM−other difference and adjusted gap-duration slope are not confirmed.
6. **Within-year survey rounds (NEW):** raw PEM acoustic enrichment occurs at each represented round and appears greatest around the third protocol round on this source cohort. With whole-route, multiple-endpoint and State uncertainty, **no geographically robust vegetation×round seasonal modulation is yet established**.

### Ecological interpretation and limits

The positive, repeated source-level PEM acoustic enrichment is an ecological pattern of habitat-associated local and pooled acoustic taxon assembly, not a hypothetical prediction score. However, taxon detection varies strongly with protocol survey round and geography, especially in round4. A tentative round3 extra-taxon hump is **not enough** to claim that macrophytes facilitate multi-frog interactions, extend the breeding season, or increase long-term population persistence.

NWI buffer polygons do not identify actual 2001–2015 live emergent vegetation composition or phenophases. NAAMP survey round does not record a plant lifecycle stage. Hydroperiod, geography, local habitat quality, acoustic detectability, fish/insect predators and frog abundance remain unmeasured covariates. Several earlier analyses are based on the **same** source archive and must not be called independent replications; no evidence of direct causal frog–frog, plant–frog or true third-order interactions.

## Verified execution and permanent outputs

- Protocol `exploration/NAAMP_VEGETATION_WITHINYEAR_ROUND_HIERARCHY_SPEC_2026_10_23.md` created **before new results**.
- Reproducible script `exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py`.
- Both source-free mathematical QA and full empirical source+result QA succeeded: [GitHub Actions #39904251155](https://github.com/zuizui0223/frogcs/actions/runs/39904251155) **SUCCESS**.
- [Verified numerical result artifact #12479644916](https://github.com/zuizui0223/frogcs/actions/runs/39904251155/artifacts/12479644916). Only scientific aggregate JSON and documentation committed; original USGS NAAMP/NWI raw data were not redistributed.
- Durable numerical receipt `exploration/NAAMP_PEM_WITHINYEAR_ROUND_HIERARCHY_AGGREGATE_2026_10_23.json`.
- All additions on exploration/naamp-vegetation-withinyear-phenology-hierarchy-2026-10-23. Original `main`, JAE RC6 paper, supporting information, existing submission artifacts and frozen source analyses unchanged.

## Next scientific direction

Rather than select round3 or exclude sparse round4 *after* seeing P values, use an **independent phenology/plant-architecture dataset** to test whether the positive PEM multi-taxon acoustic enrichment follows time-matched emergent vegetation/hydroperiod trajectories. Under this source, no additional radius/taxon/season retuning is justified as confirmatory evidence.
