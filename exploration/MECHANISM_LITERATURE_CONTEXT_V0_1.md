# Literature context for mechanism exploration v0.1

**Status:** literature interpretation for the exploratory mechanism programme. This is not submission authority and does not modify RC11.

## What prior work already establishes

The broad ecological premise is not new: anuran calling and reproductive activity are often weather- and hydrology-dependent.

- Brinley Buckley et al. (2021, *Ecological Indicators*, DOI **10.1016/j.ecolind.2020.107171**) paired passive acoustics with imagery in boreal chorus frogs. Hydropattern, vegetation and precipitation contributed to calling phenology. This directly supports the biological plausibility of a hydrologic state variable but is a single-species/local-system study.
- Sadinski et al. (2018, *PLOS ONE*, DOI **10.1371/journal.pone.0201951**) combined multi-year wetland water-level sensors and acoustic monitoring. Their St. Croix case study showed that spring-peeper calling tracked seasonal water availability and that calling ceased when wetlands dried early. This is especially relevant because it measures water depth directly rather than treating rainfall as the ecological state.
- Recent automated-acoustic work on *Pseudophryne covacevichae* reports different rainfall windows and even opposite rainfall responses among Australian regions, implying that local hydrology can gate reproductive activity differently among populations (Ecological Entomology / current 2026 publication indexed at PMID 42609249).
- Environmental-driver studies in tropical frogs likewise show that temperature, humidity and accumulated rainfall can jointly predict calling rather than a single universal weather cue (e.g. *Agalychnis lemur*, PMID 40501132).
- Calling/breeding-site fidelity is biologically plausible at the individual level. Multi-night territorial/site fidelity has been documented in red-eyed treefrogs, where chorus attendance predicts mating success (Dougherty et al. 2022, *Ethology*, DOI **10.1111/eth.13321**). Other anurans show breeding-site fidelity or homing, but these studies concern particular species and individuals rather than multispecies acoustic-community state matrices.

## What these papers do not already establish

The literature located so far does **not** provide the complete chain recovered by the frogcs exploration:

1. **Community-scale threshold recruitment.** The NAAMP signal is not merely a rainfall–calling correlation in one species. Rain-associated CallingIndex change is dominated by dry-zero → wet-positive recruitment, mostly CI2/3, and even CI3 full choruses increase.
2. **Recurrent species × physical-site template.** Strictly prior own-species strong-chorus history at the same SiteID predicts where a route-new species later forms a strong chorus, beyond generic site productivity and sampling opportunity.
3. **Hydric state beyond rainfall amount.** Among tested environmental variables, wet-minus-dry ERA5 soil-water change is more predictive of strong chorus recruitment and spatial depth than 72-hour rainfall amount, instantaneous VPD/RH, barometric pressure or current light rain.
4. **Activation depth as the matrix mechanism.** The unusual allocation appears chiefly after the second stop: third-plus and fourth-plus stop participation are excessive, and almost all of that third-plus coefficient is carried by CI2/3 activity. Once species identity and realized wet-side stop count are fixed, special stop geometry is unnecessary.
5. **Two-axis structure.** Historical template breadth and soil-water change independently predict third-plus spatial depth. The full-sample template × soil interaction is not supported, so the safest model is two largely additive axes rather than a single multiplicative gate.
6. **Large-scale robustness.** These patterns are tested across thousands of matched comparisons, hundreds of routes and 21 states, with same-observer, same-physical-stop, route-split, temporal-split and leave-one-state-out checks.

## Where the novelty actually lies

The novelty should **not** be written as “frogs call after rain” or even “hydrology influences frog calling.” Both are established.

The stronger gap is:

> Existing studies usually ask **whether and when a species calls under particular environmental conditions**. The frogcs exploration asks **how a hydric pulse changes the realized multispecies spatial acoustic state**, and finds that it chiefly re-expresses historically used species × site chorus states and increases the spatial depth of already-activated taxa.

A second, related gap is the distinction between a weather event and ecological state:

> Rainfall amount and recency are imperfect proxies for the state experienced by the system. The NAAMP exploration finds that **relative soil-water change carries stronger, more transportable information than recent rainfall amount**, while direct St. Croix work independently shows why such a distinction is biologically sensible: rainfall does not always translate one-for-one into wetland water-level change.

## Generality boundary

The mechanism is currently general only in a qualified sense.

- **Within NAAMP:** strong pooled generality. Soil-water effects transport across deterministic route halves, early/late periods, same-observer + same-site route halves and all 21 leave-one-state-out analyses. Own-species local-template effects are positive across nearly all estimable species and robust geographically.
- **Among NAAMP states:** heterogeneous. State-specific effect sizes vary substantially; a pooled mechanism does not imply identical local response.
- **Across continents:** not established. Existing external public datasets do not yet reproduce the complete effort-controlled species × site matrix estimand. AnuraSet tests did not satisfy the prefixed threshold-dominance rule.
- **Across species:** the taxonomic signal is diffuse in NAAMP, but no universal physiological trait has been identified.

## Most useful independent evidence next

The highest-value external evidence is not another rainfall correlation. It is a dataset with an **independent measure of hydrologic state**.

The USGS St. Croix system (Sadinski et al. 2018; data DOI **10.5066/F7CR5SBH**, water-depth DOI **10.5066/P145DVG8**) contains daily spring-peeper calling intensity and pressure-logger water depth over multiple years at SC4DAI2. If its raw tables can be joined without outcome-dependent choices, it can test whether direct water depth explains daily calling activity after accounting for seasonal progression. This would be a single-species/single-site hydrology replication, not a replication of NAAMP community geometry.

## Wording ceiling

A literature-aware mechanistic interpretation can now be:

> **Rain-associated chorus expansion is consistent with hydric release of a recurrent local acoustic network: environmental wetting predicts entry into substantial chorus activity and spatial activation depth, while species-specific historical site use predicts where that activity is re-expressed.**

Do not replace “consistent with” by “caused by” or “mediated by.” Direct water level, frog hydration and individual identity are not observed in NAAMP.

