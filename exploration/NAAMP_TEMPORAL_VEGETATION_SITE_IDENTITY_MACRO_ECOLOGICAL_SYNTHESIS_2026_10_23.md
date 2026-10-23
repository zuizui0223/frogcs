# Temporal hierarchy of wetland vegetation and frog acoustic metacommunities — executed NAAMP macrostudy

**2026-10-23.** Actual, reproducible observational macroecology on the **USGS NAAMP 2001–2015 × USFWS NWI 250m** original source archive. Not a forecast, simulation-only biological evidence, new review of other papers, contemporaneous macrophyte field measurement or independent biological replication. The 2026-10-23 positive habitat-richness and non-route-robust pair-network findings were already observed before this temporal question. The original RC6 JAE manuscript, SI, main and submission remain frozen.

## Main discovery: physical site identity persists, but is not uniquely stronger in PEM

**Frog acoustic taxon identity at a physical wetland listening stop is more repeatable across monitored years than a within-the-same-wetland-category swap of whole stop communities would predict**. This spatial identity signal occurs in **both** PEM emergent wetland and other mapped wetlands. The direct PEM–other-wetland difference in this excess, however, is **not supported**, even using the same observer.

The real result separates **richness/community size hierarchy** (PEM is enriched) from **interannual site identity hierarchy** (specific sites show acoustic taxon recurrence broadly, without a verified PEM advantage). Neither requires direct frog-frog attraction or vegetation-caused site fidelity.

## Source & source geography

- Original normalized NAAMP ten-stop survey run-nights **7,848**; NWI geometry, sound and temperature complete **6,236**. Original source-only NWI 250-m site map **5,147** physical SiteIDs, 499 source routes/20 source States, twelve shards and frog-outcome-blind GIS provenance [#39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Construct seasonally comparable sequences by **State × RouteNumber × RunNumber** (same designated within-year round). One unique visit per survey year retained. In any State×route×round×year cell with duplicate survey IDs, **drop that year as ambiguous** before reading outcome: 294 ambiguous year groups /660 run records. Pair adjacent available distinct **survey years**, do not use every combination or select frog-positive stops.
- Source provides **4,069** chronologically adjacent eligible survey-year pairs *before* physical-site identity and mapped-PEM checks. **71** had some physical stop SiteID moved/changed and were excluded. Another **1,595** lacked ≥2 PEM-positive and ≥2 other wetland sites within the exact same physical 10-stop route. Remaining **2,403** exact same-physical-site year pairs span **273 independent physical routes and 20 States**.
- **1,573** paired visits are one calendar year apart; **830** have gap ≥2 years, up to 14. **1,925** pairs have an identical, nonmissing `ObserverTrackingID` (238 physical routes). Same RunNumber is only a **coarse seasonal match**, actual day of year, rain, weather and other site observation differences remain possible.
- All source taxon labels, including grouped taxonomic complexes, used for CI≥1 all calling and CI≥2 strong calling. Silent stop pairs included as zero overlap; no inference on animals not acoustically detected.

## Exact habitat-constrained site-identity null, not a prediction score

For each eligible route×annual-round×year-pair, choose only wetland-mapped physical stops and partition into `P=1` (NWI PEM polygon within 250-m buffer) and `P=0` (no mapped PEM polygon but **some other NWI mapped wetland**). n+≥2, n−≥2. Let `m=min(n+,n−)` and match 2–5 physical sites on both sides, always equal coverage.

At physical site i in vegetation stratum h, let `A_i` and `B_i` be two-year acoustic taxon sets. Define:
- `D_h = mean_i |A_i ∩ B_i|`: taxon units repeatedly called at the **exact same** physical stop;
- `O_h = mean_{i≠j} |A_i ∩ B_j|`: taxon overlap across **different** physical stops but **within the same vegetation class**;
- `F_h(m) = [(m−1)/m]×(D_h−O_h)`: exact expected m-site same-physical-site recurrence excess over swapping complete later-year stop communities within class, averaged over all equal-size m-site subsets.

Hypergeometric identity verified **numerically against all combinations of sampled sites and all later-year site permutations**, including a separate binary-acoustic-activation identity and all-silent cases. This reference retains *each year's* actual taxon sets and distribution across surveyed stop assemblies within each class. It cannot control finer unmeasured habitat/physical site attributes or detection heterogeneity.

Primary ecologically motivated contrast is `F_PEM(m)−F_other_wetland(m)`, route-averaged and clustered by physical monitoring route. Student-t 95% intervals with df=272, **4,999 independent-route sign flips**, two-threshold family BH. Retain positive F values in each habitat as descriptive before the next post-readback within-class tests.

## Main result: PEМ minus other wetland temporal recurrence is non-support

| Interannual landscape-scale estimand (expected repeat-calling taxon units/site) | Any CI≥1 | Strong CI≥2 |
|---|---:|---:|
| **PEM same-physical-site excess F** | **+0.08388** | +0.04838 |
| **Other mapped wetland F** | **+0.08862** | +0.04956 |
| **PEM−other wetland excess** | **−0.00475** | **−0.00119** |
| 95% route CI on between-habitat contrast | −0.01692 to +0.00743 | −0.01027 to +0.00790 |
| Two-sided Student route P | 0.4434 | 0.7975 |
| Two-endpoint BH q | **0.7975** | **0.7975** |
| Independent route sign-flip P | 0.4458 | 0.8000 |
| Same observer only, PEM−other wetland (238 routes) | −0.00489 (CI −0.01870 to +0.00891) | −0.00088 (CI −0.01065 to +0.00888) |

**No evidence PEM alone increases or decreases physical-site recurrence beyond the nonPEM-wetland baseline.** This is a nonsignificant **difference**, not a formal equivalence proof. No alternative NWI radius, habitat group, species set, season split or temporal gap was chosen after observing this null.

For the CI≥1 cohort, the actual same-stop two-year shared-calling taxon counts (not null-corrected) were **0.95891** at PEM sites and **0.75394** at other wetlands. But the corresponding different-site within-habitat overlap was also higher in PEM (**0.82704** vs **0.61404**), so those raw differences cannot be attributed to PEM-specific site memory. The **null-relative standardized equal-m difference** is negligible. This illustrates exactly why richness/taxon-pool differences must not be mistaken for persistence.

## Additional positive evidence: physical-site anchoring in *both* wetland environments

After seeing the above original results, a separate **explicitly post-readback** family of four within-habitat tests was frozen and run over the **same** 2,403 matched visit pairs. All four use route-averaged means, 273 physical-route Student t intervals, 4,999 physical-route sign flips, 4-test BH adjustment, State-mean direction and same-observer sensitivity. These are **not independent preregistered confirmations**.

| Wetland group | CI≥1 (any call) site-identity F and 95% route CI | CI≥2 strong call F and 95% route CI |
|---|---:|---:|
| **Mapped PEM** | **+0.08388** (0.07290–0.09486) | **+0.04838** (0.04076–0.05599) |
| **Other mapped wetland** | **+0.08862** (0.07988–0.09737) | **+0.04956** (0.04284–0.05628) |

All four post-readback BH q values are below **1.3×10⁻²⁸**, every independent-route sign-flip P had Monte Carlo bound **0.0002** (0/4,999 more extreme than observed), and all **20/20 leave-one-State-out** mean estimates remain positive for each habitat and call threshold. Positive State means: PEM CI≥1 19/20, other CI≥1 20/20; PEM CI≥2 18/20, other CI≥2 19/20. Same-observer matched sequences remain positive with CI excluding zero in all four cases. This is substantial **observational space-time autocorrelation of taxon-call identity**, not evidence that individual frogs returned and not proof of a specific plant-mediated effect.

Within CI≥1 PEM, gap-one-year F is **+0.09345** versus positive +0.07021 for >1-year gap; other wetlands +0.10384 vs +0.07111. Strong CI≥2 PEM +0.05892 vs +0.03526 and other wetlands +0.05779 vs +0.04240. These are *descriptive different-source-composition groups*, not a fitted temporal-decay function or significance-tested cross-gap interaction. All suggest lower taxon re-detection surplus over long intervals, which requires a separate explicitly designed year-gap study to distinguish duration from historical cohort/season effects.

## How this revises the ecological hierarchy (without changing earlier results)

1. **Mapped habitat and first-order alpha diversity:** PEM has positive local acoustic taxon richness compared with nonPEM within 10-stop NAAMP runs, with other mapped classes, mapped total wetland area, temperature and sound adjusted (PEM coefficient **+0.23777** any-call per stop; 499 physical routes; same source archive).
2. **Equal-coverage multi-stop gamma and nestedness:** after exact 2–5-stop rarefaction, mapped PEM has more taxon units than other mapped wetlands in the same run (**+0.29837** when restricted to wetland-mapped stations; 281 routes); 39/48 original monitoring taxon labels have positive *signed* route-mean contributions but are not 39 independent taxon-significance tests.
3. **Geographic scale:** direct PEM–frog richness covariance is positive among stops within the same night and negative among State averages, indicating scale-specific sign reversal (descriptive, no causal plant inference).
4. **Interannual physical-site scale — NEW:** identity of taxon acoustic calls at an exact physical site recurs more often than chance rematching within its NWI wetland class, in both PEM and other wetlands. **PEM vs nonPEM temporal site-fidelity difference is null**; positive alpha/gamma richness cannot be reinterpreted as a greater stabilizing effect of PEM on long-term call identity.
5. **Dyadic and higher-order levels:** earlier crossfitted NWI fixed-margin *pair-identity* analysis found no route-robust global PEM-dependent partner identity rewiring (199-draw naïve CI≥1 P=0.005 but 4,999 physical-route sign-flip P=0.3276; CI≥2 0.3844). This and the temporal result limit overstatements about interspecific interactions and frog-frog facilitation. No irreducible multi-animal causal effect demonstrated.

### Ecological interpretation

The new **positive** site identity memory in both wetland categories is consistent with physical microhabitat structure or environmental heterogeneity anchoring calling taxa across monitoring years, while **the additional PEM taxon-richness surplus is a distinct, not demonstrably temporally stabilizing association**. However, no measurement of the 2001–2015 actual macrophyte communities, water depth, water permanence, fish/insects, acoustic detectability or individual animals permits attributing the site identity to vegetation itself.

The simplest supported storyline is **hierarchical non-equivalence** of (i) local acoustic taxon number, (ii) multi-stop taxon pool, (iii) spatially structured recurring taxon identities, and (iv) partner-specific acoustic co-detection. These scales are related but do not share the same vegetation signature. Importantly, both site permanence and richness may respond to *unobserved* time-invariant microhabitat, so do not infer a plant cause or a negative causal effect from the PEM-no-advantage contrast.

## Reproducible records and verification

- Original response-blind NWI source: [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- New original pre-readback exact same-SiteID temporal comparison: [Actions #39900305024](https://github.com/zuizui0223/frogcs/actions/runs/39900305024) **SUCCESS**.
- Complete post-readback four-habitat sensitivity with unchanged primary P and effect: [Actions #39900755251](https://github.com/zuizui0223/frogcs/actions/runs/39900755251) **SUCCESS**, numerical original [artifact #12479086077](https://github.com/zuizui0223/frogcs/actions/runs/39900755251/artifacts/12479086077).
- Script: `exploration/run_naamp_vegetation_interannual_site_fidelity_v0_1.py`, workflow `.github/workflows/naamp_vegetation_interannual_site_fidelity.yml`.
- Original pre-result ecological spec: `exploration/NAAMP_VEGETATION_INTERANNUAL_SITE_FIDELITY_SPEC_2026_10_23.md`; transparent post-readback additional test spec: `exploration/NAAMP_TEMPORAL_SITE_ANCHORING_POSTREADBACK_SPEC_2026_10_23.md`.
- Permanent auditable aggregate JSON `exploration/NAAMP_TEMPORAL_VEGETATION_SITE_IDENTITY_MACRO_AGGREGATE_2026_10_23.json`. No raw third-party NAAMP/NWI records committed to the repository.
- Exploration branch `exploration/naamp-vegetation-site-fidelity-temporal-hierarchy-2026-10-23`; `main` and JAE RC6 scientific authority untouched.
