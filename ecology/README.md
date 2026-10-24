# Frog chorus as a temporal gateway into stage-structured interaction networks

## Independent ecological result — Mohonk vernal pools (25 October 2026)

A NEW empirical observation series has now been analysed independently of NAAMP: **11 ponds, 59 pond-years, 240 sampling dates (2016–2021)** from the original [Mohonk Preserve GBIF-US archive](https://doi.org/10.15468/dypfbs). Of **44 pond-years** where both wood-frog and spotted-salamander eggs were seen, first positive wood-frog egg detection preceded spotted-salamander egg detection in **29**, tied in **14**, and followed in **1**. Across **31 pond-date visits**, wood-frog tadpoles and spotted-salamander eggs were **co-detected**; these occurred in **29 of 59 pond-years**. No direct attacks or offspring survival were recorded.

This is a **recurring cross-stage trophic opportunity**, not proof of predation or predator-driven fitness change. It complements, but does NOT replicate, the published experimental tadpole–egg interaction in Takahashi & Ruszala (2023), DOI 10.1002/ece3.10427. Nor is cross-life-stage seasonal overlap entirely new: Carroll, Saenz & Rudolf (2023), *Oikos*, DOI 10.1111/oik.09773 already measured adult-calling/larval overlap across nine amphibian species. The ecological step still lacking is an **actual interaction outcome** (direct predation/hatching survival) linked to the temporal stage overlap and real wetland conditions.

- [Source-verified result and caveats](mohonk/MOHONK_WOODFROG_SALAMANDER_STAGE_PRIORITY_RESULT_2026-10-25.md)
- [Ecology-first research note manuscript draft](mohonk/DRAFT_STAGE_ORDER_AND_TROPHIC_OPPORTUNITY_RESEARCH_NOTE_2026-10-25.md)
- [Original-stage analysis script](data/mohonk/analyze_egg_stage_priority.py) and [4 synthetic quality tests](data/mohonk/test_stage_priority.py); [GitHub Actions SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/40112620306).
- Mohonk data are independent of NAAMP; frozen JAE `main` is unchanged.

Ecology-first research concept — 2026-10-24. **Ideas are hypotheses, not a new empirically demonstrated frogcs result.**

## The ecological paper, not a measurement-method paper
**Candidate title:** *Breeding phenology rewires frog–predator interaction networks across aquatic and terrestrial life stages.*

**Core idea:** A frog chorus advertises a reproductive opportunity, but breeding success also depends on the **relative timing** of eggs, tadpoles, salamander larvae, dragonfly nymphs and dragonfly emergence. An apparent predator or competitor at one stage can become prey or facilitator at another. Hydroperiod, canopy, emergent vegetation and fish can change these stage encounters. A pond's list of species alone cannot tell the direction of their interactions.

### Three predictions of ecological interest
**P1 — Time-order hypothesis:** Frog breeding/hatching earlier or later than antagonists shifts predation opportunities across **egg and larval stages**. Test `frog hatching date − salamander hatching date`, predator size distribution and *measured* egg/tadpole survival rather than raw co-occurrence. In some systems frogs may consume salamander eggs; in others salamander larvae consume frog tadpoles. Such contrasting cases need not represent a single same-species-pair reversal.

**P2 — Metamorphic predator-prey reversal:** The expected predation direction between a frog and an odonate depends on the overlap between early tadpoles and odonate aquatic nymphs versus predatory-size postmetamorphic frogs and vulnerable emerging odonates. Beranek et al. (2023) already reported an actual `Litoria aurea–Anax papuensis` reversal: the new question is **which pond phenologies and vegetated structures make it common/rare** and whether that alters offspring recruitment or odonate emergence, rather than simply observing one more event.

**P3 — Indirect and multi-layer effects:** Fish can harm tadpoles directly while sometimes reducing odonate nymph predation, changing the NET effect. Vegetation can simultaneously shelter some prey and house larval predators and provide emergence substrate. Adult chorus calls may attract frog-biting midges and bats, introducing **a different enemy guild during the signalling stage**; offspring predators arrive in later developmental stages. The novel hypothesis is a context-dependent change of net enemy risk with reproductive timing, not one universally positive or negative ecological interaction.

### Published work that already occupies nearby gaps
- Beranek et al. (2023), *Ecology*, DOI 10.1002/ecy.4108 — same frog–odonate pair with actual aquatic-to-terrestrial reversal.
- Benard & Greenwald (2023), *Diversity*, DOI 10.3390/d15020253 — seven-year, six-wetland salamander/frog breeding migration phenology; inferred changing predation risk under climate variation. Thus “relative timing may alter predator-prey interactions” is already a known hypothesis.
- Takahashi et al. (2023), *Ecology and Evolution*, DOI 10.1002/ece3.10427 — wood frog tadpoles consume spotted salamander embryos; egg jelly defense/oxygen/hatching effects can be nonmonotonic.
- Kishida et al. (2014), *Journal of Animal Ecology*, DOI 10.1111/1365-2656.12186 — Japanese frog–salamander aquatic-stage predation and phenotypic response.
- Adams et al. (2003), *Ecology Letters*, DOI 10.1046/j.1461-0248.2003.00435.x — sunfish suppression of odonate nymphs indirectly helps non-native bullfrog tadpoles; an experimental trophic cascade.
- Bernal et al. (2007), *American Naturalist*, DOI 10.1086/510729, and Cutajar et al. (2026), DOI 10.1002/ece3.74381 — calling-male eavesdropping by bats and blood-feeding midges, with acoustic selectivity.
- Watanabe et al. (2020), *Entomological Science*, DOI 10.1111/ens.12395 — water strider predation on frog eggs in Japan, with phenological overlap.
- Japanese Odonata aquatic-plant survey (2025), DOI 10.7211/jjsrt.51.103 — dragonfly larvae linked to particular aquatic plants, rather than a simple “more plants = more refuge” rule.

### Precise gap without overclaiming novelty
Existing work demonstrates separate **pairwise edges**, some within-stage priority effects, and at least one confirmed cross-stage reversal. The opportunity is to ask **whether a whole set of stage-specific antagonisms changes sign or strength as a function of measured temporal overlap and wetland environment across several wetlands and years**, using chorus-derived breeding timing only after independent egg/hatching calibration. The literature search is a bounded primary-source audit, not proof that no prior integrated paper exists; a full systematic review is required before claiming global originality.

### Link to frogcs RC6, without inventing an effect
The validated frogcs manuscript finds **(i) rainfall-associated silence→strong chorus, (ii) a deeper-than-expected same-taxon multi-stop tail, and (iii) recurrence at previous physical strong-chorus sites**. All three describe **breeding-associated ACOUSTIC EXPRESSION**, not eggs laid or larvae surviving. The time/stage trophic hypothesis gives a plausible biological CONSEQUENCE worth testing, but is currently unmeasured and **must not be presented as the causal explanation** for the existing manuscript's configuration residual.

**Paper strategy:** retain frozen RC6 as one empirically supported frog acoustic-spatial-ecology paper. Reserve the cross-stage predator-prey/reproduction timing claim for a genuinely new ecology paper with field-stage timing, predator presence and recruitment data. Do not split the same NAAMP observations into a nominally independent interaction paper.

## First ecological data assembly — no outcome claim yet
Aim for pond × year × dated-stage observations with:
- frog male chorus onset/peak and **observed** egg date, tadpole hatching, larval body-size distribution and metamorphosis;
- salamander egg date, hatch date, larval stage/size and actual tadpole/egg predation;
- odonate nymph instar & overwinter presence, vulnerable emergence/teneral window, actual feeding observation;
- fish and aquatic-insect predators, actual flooded duration, microhabitat aquatic-plant structure, canopy, water temperature;
- survival from egg to metamorph; distinguish apparent presence from direct trophic interactions.

**Data accessibility warning:** iNaturalist has an Odonata *Nymph* life-stage annotation but frog tadpoles are not equivalently covered by a generic animal *Larva* annotation. Public adult occurrence records and emergence-date photos alone cannot reconstruct historical same-pond larval predator exposure or demonstrate trophic interactions. An annotated observation is opportunity data, not a sampling-effort-controlled non-detection.

A falsifiable new finding would be a measured **stage-order × predator life stage × local hydroperiod/vegetation interaction** predicting real egg/tadpole survival or observed predation while holding pond and observation effort constant; a null interaction is informative too. That is the ecological quantity this branch is organized around.
