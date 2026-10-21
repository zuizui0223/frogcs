# A surprisingly indirect interaction hierarchy: wetland plants → aquatic predator context → frogs → acoustic community

**Status: mechanistic hypotheses and literature-backed contrasts, not a direct multi-trophic inference from NAAMP.**
Date: 2026-10-21. User asked whether apparently unrelated species could create a hierarchy of interspecific interactions related to emergent aquatic plants.

## Current NAAMP evidence (observed, not causal)

The source experiment is USGS NAAMP 2001–2015 recorded calling, matched to present-day mapped NWI emergent-wetland polygon fractions:

1. Five of 25 tested frog taxon units have positive associations between NWI mapped PEM fraction and same-route-night location of CI≥2 calls (BH q<0.05). Four survive a separate post-hoc binary mapped-PEM-overlap sensitivity.
2. Strong chorus at previously used physical SiteIDs remains more frequent after mapped plant cover and observation covariates (β≈+0.1444 in 10,166 cell records).
3. Between-frog-taxon checkerboard remains excessive relative to exact fixed row/stop margins after conditioning on route-cross-fitted species-specific NWI wetland + PEM preferences: CI1–3 residual ~+0.0523 in 3,659 run matrices; CI2–3 residual ~+0.0584 in 1,766 matrices.
4. NWI PEM × survey-month-inclusive three-month MODIS wetness does not improve held-out strong-call placement (route-fold log-score increment −0.000810, 95% bootstrap CI −0.003351 to +0.001744; later-year increment −0.000841, CI −0.004379 to +0.002123). Checkerboard residual persists.
5. These are **recorded acoustic detections**, not larvae, mating, spawning or individual movements. NWI classes are mapped plant-community proxies and not time-matched aquatic macrophyte abundance at exact listening points.

## Ecological hierarchy worth testing

A plausible multiplex system has **two principal forks, plus a parasite-mediated third layer**, rather than one plant→frog food chain:

**Aquatic predator/refuge cascade:** fish assemblage/stocking and wetland hydroperiod → fish and aquatic insect predator exposure + submerged macrophyte state → locations of tadpoles and insect larvae within open-water vs emergent littoral cover → local recruitment/survival and potential later adult breeding-site availability. The initial ecological hierarchy can therefore prioritize fish over aquatic insects, followed by vegetation cover and slope, and can even reverse the naive notion that denser emergent plants are always safer. Fish can cause **tadpoles and insect predators to congregate in the same emergent vegetation**, potentially exposing tadpoles to more insect predation. Transferring a tadpole result to current calling adult distribution is **not automatic** and requires matching life stages and time lags.

**Acoustic signaling and interference:** plant architecture → availability/height/geometry of calling perches and sound propagation/detection → conspecific and heterospecific acoustic interference or calling position → observed species-by-stop call sharing/avoidance. Competition over calling sites has been demonstrated experimentally for some treefrog pairs **outside this NAAMP dataset**; calls may also be altered by receiver/detection physics. A nonrandom co-calling network alone does not show behaviourally direct exclusion.

Potential additional (lower-confidence) layers: aquatic insect emergence/food resources affecting adult frog foraging; waterfowl/large aquatic herbivores that restructure macrophytes; wetland engineers that affect hydroperiod and habitat. **No member of these external guilds was measured concurrently in NAAMP, so no effect can be claimed here.**

## Direct studies establishing biological plausibility

- Burrow et al. (2022), *How plants affect amphibian populations*, Biological Reviews, DOI [10.1111/brv.12861](https://doi.org/10.1111/brv.12861): plant structure supplies calling sites and oviposition substrates, mediates abiotic microclimate and predator/competition interactions; not every plant effect is positive.
- Kloskowski et al. (2020), [Between-habitat distributions of pond tadpoles and their insect predators in response to fish presence](https://link.springer.com/article/10.1007/s10750-020-04190-5), Hydrobiologia: 35 fish-stocked/fishless pond comparison; tadpoles and aquatic insect predators both shifted relatively toward vegetated littoral habitats with fish, highlighting possible indirect risk, not a proven increase in insect predation rate.
- Shulse et al. (2013), [Mosquitofish dominate amphibian and invertebrate community development in experimental wetlands](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2664.12126), Journal of Applied Ecology: an experimentally informed **hierarchy** of frog wetland habitat use proposed fish avoidance, then aquatic invertebrate predator avoidance, vegetation cover and within-wetland slope. Mechanism-specific context; this is not yet demonstrated across the NAAMP taxa.
- [Asymmetric competition over calling sites in two closely related treefrog species](https://www.nature.com/articles/srep32569), Scientific Reports (2016): removal of one treefrog calling species changed another species' sites in paddies, illustrating the possibility of heterospecific acoustic/calling-site effects. Neither those species nor that manipulation was observed in NAAMP.
- [Calling amplitude flexibility and acoustic spacing in Allobates femoralis](https://link.springer.com/article/10.1007/s00265-020-02857-6), Behavioral Ecology and Sociobiology (2020): call height and sound propagation alter signal geography. Demonstrates an observation/signal layer separate from larval success.

## Third, surprisingly distant layer: aquatic macrophytes ↔ snails ↔ trematodes ↔ amphibians (possibly bird hosts)

A very different biotic hierarchy is parasite ecology. Trematode parasite life cycles can involve waterbirds or mammals releasing parasite eggs, aquatic **snails as intermediate hosts**, and free-swimming infectious stages encountering tadpoles. Aquatic vegetation may modify snail food and location; dense vegetation can also *physically obstruct* host–parasite contact. These mechanisms can oppose each other and are strongly density-dependent.

- [Dense aquatic vegetation can reduce parasite transmission to amphibians](https://doi.org/10.1016/j.ijpara.2024.11.003) (2025): very dense artificial macrophytes reduced trematode infection loads in controlled tadpole exposure; ordinary density or structural complexity did not have a consistent effect. Not a result from NAAMP.
- [How temperature, pond-drying, and nutrients influence parasite infection and pathology](https://pmc.ncbi.nlm.nih.gov/articles/PMC6126996/) (2018): infected-snail densities predicted frog trematode infection; food-web, pond drying, nutrient and thermal regimes acted at different transmission stages.
- [Bottom-up and trait-mediated effects of resource quality on amphibian parasitism](https://doi.org/10.1111/1365-2656.12613) (2017): host resource quality can carry a non-obvious plant/detritus → snail → parasite → amphibian pathway.

This is an especially good demonstration of **different interaction layers that an aquatic vegetation map alone cannot identify**. Neither NAAMP amphibian calls nor NWI mapping includes snail parasite burden, periphyton, bird-host presence or life-stage-specific infection. Treat this as a priority *new system*, not an explanation already demonstrated by our NAAMP results.

## Executed intermediate network result (new, 2026-10-21)

We did the measurable first step after predeclaring the NWI-conditional frog pair network. On **1,766 strong-calling survey matrices, 398 routes**, weighted fixed-fixed matrices with exactly preserved taxon positive-stop totals and stop species richness were simulated using route-cross-fitted NWI wetland+emergent coefficients **without any refitting of the old weights**.

- 489 pair units observed at least once, **112** met the prespecified support and null-variance minimums, and **21** had BH q<0.05; **14** showed more same-stop strong-calling than the null, **7** showed less. Taxonomic complex-versus-contained-species aliases were excluded.
- Positive sharing: `Lithobates catesbeianus` × `L. clamitans`, +0.2239 shared stops per jointly active run (CI +0.1586 to +0.2892; 301 runs/146 routes, BH q≈2.1e−9).
- Negative conditional sharing: `Anaxyrus fowleri` × `L. clamitans`, −0.1665 (CI −0.2287 to −0.1044, 168 runs/82 routes, q≈8.5e−6).
- Negative conditional sharing: `L. catesbeianus` × `Pseudacris crucifer`, −0.1130 (CI −0.1834 to −0.0427, 135 runs/87 routes, BH q≈0.0114).

**Post-result** source-period and independent-route-fold stability (NOT external validation) of the 21 BH edges found **10/21** with enough early/late and A/B records and matching association direction; **4/21** had sign-stable CIs excluding zero in each split. Those four: the three pairs above plus `Hyla chrysoscelis` × `H. versicolor` (interpret with extra cryptic-species acoustic identification caution). Ten original BH edges did not have four sufficiently populated holdout subsets; failing the stability rule does not imply those edges are absent. **17/21** edge directions remained unchanged across all tested leave-one-State-out subsets.

Interpretation: the mapped plant layer by itself does not absorb some between-frog-taxon spatial association, but the results are **not** evidence of direct individual competition, trophic predation, chorus facilitation or attraction. In particular, the observed `Lithobates` vs `Pseudacris` pattern is compatible with hydrological permanence and fish/invertebrate predator filtering. It cannot distinguish these from ecological interactions with existing NAAMP variables alone.

- Primary network [Actions 39520831924](https://github.com/zuizui0223/frogcs/actions/runs/39520831924), full `exploration/NAAMP_NWI_PLANT_CONDITIONED_PAIR_NETWORK_RESULT_V0_1.json`.
- Temporal, route-fold and State-leverage sensitivity [Actions 39521559210](https://github.com/zuizui0223/frogcs/actions/runs/39521559210), `exploration/NAAMP_PLANT_CONDITIONED_PAIR_NETWORK_STABILITY_RESULT_V0_1.json`.

---

## Immediate measurable intermediate question

Ask which frog taxon pairs co-occur on the same *listening stops more or less than predicted* after:

- each taxon's **number of calling-positive stops** on that route-run is exactly conditioned on;
- each stop's **total calling taxon richness** on the run is held exactly;
- each taxon's transferred route-held-out NWI total-wetland and mapped PEM associations are incorporated into a weighted Curveball null;
- repeated observations are clustered by route, BH FDR is applied across eligible pairs, species complexes are excluded from overlap aliases.

The resulting edges must be labelled `conditional_acoustic_overlap`, **not** direct competition, mutualism, fish/insect predation or observed ecosystem trophic networks. They identify candidate biological configurations not captured by plant filters and are a defensible stopping point for the original NAAMP-only data.

## Follow-up design for a genuine multilayer/causal network

At replicated ponds, sample the **same pond, sites and dates**, not unrelated historical occurrence maps:
- contemporaneous plant species, emergent stem density, submerged cover, calling perch availability and vegetation at the *actual* chorus microphone positions;
- fish presence/biomass and aquatic predators (odonate larvae, predatory hemipterans and dytiscid beetles);
- water level, temperature, hydroperiod, dissolved oxygen, sediment/substrate water content and predation/shelter habitat;
- species-resolved frog calling locations/intensity, egg masses, tadpoles, and recruitment (not assuming acoustics = reproductive success);
- calibrated acoustic signal-detection/playback, continuous simultaneous recordings and observer/recorder controls.

Prespecify **fish presence × emergent vegetation × larval predator density** predicting frog larval microhabitat and recruitment, and a separate **plant perch architecture × heterospecific chorus** effect on adult caller site placement. Stage-to-stage/lagged path estimates are necessary to join the two ecological mechanisms.

## Why this matters

A statistically supported pairwise plant-related acoustic association **does not imply** that mapped plants explain the community checkerboard. If the new plant-conditioned residual frog pair network exists, the scientific question becomes: which unmeasured microhabitat and biotic states generate the remaining **joint** allocation? This is a different and more ambitious question from the RC6 paper's main claim. Preserve all original science and submission documents unchanged.

## Provenance

- Parent NWI/NAAMP results: `exploration/NAAMP_AQUATIC_VEGETATION_ECOLOGICAL_SYNTHESIS_2026_10_21.md`;
- Frozen plant-conditional checkerboard: `exploration/NAAMP_NWI_CONDITIONAL_CHECKERBOARD_RESULT_V0_1.json`;
- Pair network prespecified contract: `exploration/NAAMP_PLANT_CONDITIONED_SPECIES_PAIR_NETWORK_CONTRACT_2026_10_21.md`.
