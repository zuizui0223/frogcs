# Frog-first breeding creates recurring stage-specific opportunities for interactions with spotted salamanders in vernal pools

**Research Note — exploratory manuscript draft, 25 October 2026. Not submitted.**
This study reports stage-specific co-detection, not verified predation or reproductive success. It is independent of the NAAMP observations underlying `frogcs` RC6.

## Abstract

**Background.** The timing of reproduction can determine whether an organism encounters another species as an egg, larva, or adult. Laboratory work has established that wood-frog (`Lithobates sylvaticus`) tadpoles can consume spotted-salamander (`Ambystoma maculatum`) egg masses, but the frequency with which these stages overlap in repeatedly monitored natural breeding pools remains less clearly quantified.

**Methods.** We re-analysed occurrence-stage records from 11 Mohonk Preserve vernal pools during 2016–2021 (59 pool-years, 240 sampling dates). For each pool-year, we calculated the first *recorded positive* egg detection for wood frogs and spotted salamanders and asked whether wood-frog tadpoles and spotted-salamander eggs were detected in the same pool on the same survey date. We retained explicit zero observations and did not treat unreported stages as absent.

**Results.** Both species' eggs were detected in 44 pool-years. Wood-frog eggs were recorded first in 29, the two species were first detected on the same date in 14, and spotted-salamander eggs were recorded first in one. Among the 30 cases with distinguishable first-detection dates, wood-frog eggs preceded spotted-salamander eggs in 29 (96.7%). The median observed first-detection gap was six days. Wood-frog tadpoles and spotted-salamander eggs were co-detected on 31 survey dates distributed across 29 of 59 pool-years. The predominance of wood-frog-first records remained when restricting attention to more frequently surveyed pool-years, although monitoring timing limited precision.

**Conclusions.** The data document a recurring *phenological opportunity* for a trophic interaction previously established experimentally. They do not establish that egg predation occurred at Mohonk or that reproductive success was altered. The ecological consequence of reproduction timing must be tested using observations of feeding, egg development and survival, including habitat-dependent costs and benefits of egg-jelly defense.

**Keywords:** amphibian breeding phenology; cross-stage encounters; vernal pools; wood frog; spotted salamander; trophic opportunity; life-history timing

## Introduction

The identity of a potential predator or competitor is not static across the life cycle. In temporary-water communities, breeding order affects whether vulnerable embryonic stages encounter heterospecific larvae, and whether the size of a potential predator changes before prey become available. A census of species composition therefore need not capture the temporal structure of ecological interactions.

Previous work has already documented phenological tracking between adult calling and larval occurrence in a nine-species amphibian assemblage across eight ponds (Carroll, Saenz & Rudolf, 2023). Furthermore, direct experiments demonstrate a wood-frog-tadpole–spotted-salamander-egg interaction whose effect may not be simply negative: the protective jelly layer can impose oxygen-diffusion costs, and predator-induced thinning can under particular conditions improve hatching of intact egg masses (Takahashi & Ruszala, 2023). These findings make the *frequency of actual stage encounter opportunities in natural pools* a worthwhile observational question. Yet first observations of egg masses must be distinguished from actual laying and hatching dates, and stage co-detection must be distinguished from predation.

We used an independent long-term vernal-pool monitoring archive to ask: (1) how often are wood-frog eggs first detected before spotted-salamander eggs in the same pool-year, and (2) how frequently are wood-frog tadpoles recorded while spotted-salamander eggs remain detectable in the same pool? We use these results to delimit opportunities for an established predator–egg interaction, not to estimate its realized rate.

## Methods

### Data and design

We used the original publicly archived Mohonk Preserve vernal-pool amphibian monitoring Darwin Core Archive (GBIF-US IPT, version 1.1; DOI 10.15468/dypfbs), downloaded as the original publisher ZIP. The archive contains 13,862 records spanning much of 1931–2021. We restricted comparisons to **2016–2021**, during which species-by-life-stage records more consistently include explicit zero counts. Earlier positive-event-heavy reporting could not support the same assessment of non-detection.

The main analytical units were (i) pool × calendar year and (ii) pool × sampling date. We identified 11 pools using the dataset's generalized coordinates, yielding 59 pool-years and 240 pool-date surveys. Coordinates were used only to distinguish recorded pools, not to infer microhabitat proximity of egg masses and tadpoles.

We extracted records for `Lithobates sylvaticus` egg and tadpole stages and `Ambystoma maculatum` egg and tadpole stages. For a stage on a sampling date, a reported individual count above zero constituted a positive detection. A reported zero was an assessed non-detection; absence of a species-stage record was *unassessed*, not zero. Duplicate stage/date cells, if any, were reduced to an any-positive indicator without summing potentially redundant counts.

### Phenological order and possible encounter windows

For pool-years in which egg stages of both species were observed, we computed the interval (in days) from the first positive wood-frog egg record to the first positive spotted-salamander egg record. We classified strictly earlier wood-frog detections, same-day first detections and strictly earlier spotted-salamander detections.

A stage-specific *potential encounter* required both (a) wood-frog tadpoles and (b) spotted-salamander eggs to have positive records on the **same pool-date**. Such co-detection establishes neither physical contact at the egg-mass scale nor a feeding event. We separately tabulated Jeff­erson-salamander (`Ambystoma jeffersonianum`) eggs as a distinct pair with no directly verified predation claim.

We tabulated a descriptive pool-cluster bootstrap for wood-first frequency conditional on *distinguishable first-positive survey dates* (2,000 cluster resamples; seed 2840223). Pool is the resampling cluster because repeated years and sampling dates within a pool are not independent. Robustness descriptors included pool-years with at least three survey dates and pool-years in which both first-positive egg detections occurred *after* the initial survey date, reducing left-censoring. All analyses are exploratory.

### Data provenance

Original archive SHA256:
`0309abd9afa4a224287d6853d79ae1f7111a3a7bb19b0d2337f05c280ef12b34`.

Original `occurrence.txt` SHA256:
`d52b288608a40c3b721f3561a57ace34728975522892a4fdc1d0b4f6ffb3610e`.

Reproducible scripts and result receipts are retained in the independent `research/ontogenetic-interaction-phenology-2026-10` branch. This dataset and script do not read NAAMP `Counts.csv`.

## Results

### Egg detections were predominantly wood-frog-first

Both egg stages were positively recorded in **44 pool-years**. Wood-frog eggs were first detected earlier in **29**, both species' eggs were first detected on the same date in **14**, and spotted-salamander eggs were recorded earlier in **one** pool-year (Table 1). Among **30 strictly ordered cases**, **29 (96.7%)** placed the wood-frog egg detection first (descriptive pool-cluster bootstrap 95% interval **0.889–1.000**). The median spotted-minus-wood first-positive survey-date interval across all 44 pool-years was **6 days**.

The ordering did not depend solely on very poorly sampled pool-years. For **34 pool-years with at least three visits**, the corresponding counts were **26 wood-first, seven ties and one salamander-first**. In **20 pool-years** where each species' first egg detection occurred after the initial visit, they were **14 wood-first, five ties and one salamander-first**. Because visits were intermittent, neither these differences nor the bootstrap interval is a precise estimate of actual laying order.

### Wood-frog tadpoles and spotted-salamander eggs repeatedly occurred together

Across **235 pool-dates on which both focal stage categories were assessed**, tadpoles and spotted-salamander eggs were simultaneously recorded as present on **31** survey dates. These events were distributed over **29 of 59 pool-years**. This is direct evidence that a stage pair with a documented experimental trophic interaction repeatedly shared a pond within the same survey date, but **not** evidence of an attack or its consequences. A further **nine** pool-dates co-detected wood-frog tadpoles and Jefferson-salamander eggs; their specific trophic relationship is not established by these records.

The stage-order pattern varied across years: many first detections were tied in 2016–2017, whereas strict wood-first detections were common in 2019–2020 (Table 1). Pool-specific surveying effort also varied by year, precluding attribution of this pattern to rainfall, temperature or phenological climate shifts.

### Table 1. Recorded first-positive egg chronology by year

| Year | Pool-years with both egg stages | Wood frog first | Same first-positive date | Spotted salamander first | Tadpole + spotted egg co-detection dates |
|---|---:|---:|---:|---:|---:|
| 2016 | 8 | 2 | 6 | 0 | 5 |
| 2017 | 4 | 1 | 3 | 0 | 4 |
| 2018 | 6 | 3 | 2 | 1 | 1 |
| 2019 | 8 | 8 | 0 | 0 | 2 |
| 2020 | 9 | 9 | 0 | 0 | 10 |
| 2021 | 9 | 6 | 3 | 0 | 9 |
| **Total** | **44** | **29** | **14** | **1** | **31** |

The final column uses pool-date counts irrespective of whether both species' egg stages were recorded in that pool-year. Dates are assessment events, not independent biological replicates.

## Discussion

### A repeated reproductive sequence creates potential trophic encounters

The conspicuous result is not simply that two amphibians breed in the same pond. When each species' egg stage was recorded, wood-frog eggs almost always appeared no later than spotted-salamander eggs on the sampling schedule, and wood-frog tadpoles were repeatedly recorded while spotted-salamander eggs were still present. This temporal structure is consistent with a recurring opportunity for the already-documented wood-frog-tadpole–spotted-salamander-egg interaction.

Stage order is a *necessary temporal condition* for some types of predator–egg contact but does not imply its occurrence. Actual interactions depend on wood-frog hatch date, tadpole size and density, egg-mass microhabitat, jelly-layer traits, water depth, temperature, oxygen, and alternative foods. We did not measure any of these together with predation outcomes at Mohonk.

### The sign of the interaction is not necessarily simple

Independent experimental work has shown that spotted-salamander egg jelly protects against tadpole attacks but may constrain oxygen diffusion. Under particular high-predator treatments, attacks that thin the jelly layer can increase hatching success of intact egg masses. Thus the presence of a potential egg predator can, in principle, have context-dependent rather than uniformly negative consequences. **This effect was demonstrated in that earlier experiment; it was not measured in the Mohonk series.**

Our field observation provides the ecological temporal context in which such experiments could matter in nature. The genuinely untested biological question is whether **the timing of predator–egg overlap × egg-mass defense × actual water/oxygen conditions** predicts net embryo survival across years and ponds. Without observed feeding and hatching outcomes, the present dataset cannot distinguish a harmful, neutral or potentially beneficial net interaction.

### What this does and does not add beyond prior phenology research

Carroll et al. (2023) documented seasonal overlap tracking between adult calling and larval occurrence among nine amphibian species. The present analysis focuses instead on a **directional, heterospecific predator-stage / prey-egg-stage opportunity** in a separate, repeatedly surveyed pool system. It remains a natural-history-based quantitative research note, not a demonstration of interaction-network rewiring. Existing species-pair feeding experiments provide biological plausibility, but the independent observational co-detection data cannot establish realized trophic edges or causality.

In particular, the `frogcs` NAAMP result on rain-associated chorus-state switching is a different study of adult acoustic activity. It should *not* be spliced into these observations as though egg laying, tadpole predation, or salamander recruitment followed from the calling signal. Any link between chorus shifts and offspring enemy exposure requires recording the relevant temporal lags within the same pool and year.

### Study limitations

First detections are interval- and left-censored by survey timing. Fourteen ties may represent unobserved differences in true laying order. The 2016–2021 sample has only 11 spatial pond clusters, and repeated pond-years are correlated. Monitoring emphasizes early spring: **no positive spotted-salamander larval-stage record** occurred in the later study window, which does not establish absence of larvae. The GBIF occurrence export excludes direct predation, embryo oxygen, hydroperiod, canopy, dragonflies and actual offspring survival, so none was tested. Sampling intensity may influence both first-detection gaps and probability of stage co-detection. These observations therefore cannot identify direction or sign of actual interactions or explain stage-order variation with environment.

## Conclusion

Across 11 monitored vernal pools over six spring seasons, recorded wood-frog egg stages usually preceded spotted-salamander egg stages when the order could be distinguished, and wood-frog tadpoles repeatedly shared a pool and survey date with spotted-salamander eggs. This quantifies an ecologically plausible, recurring **stage-specific encounter window** for a known interaction, but cannot demonstrate that predation occurred or predict the net effect on hatching. The next ecological advance requires matching verified attacks and embryo fate to relative breeding/hatching timing and local wetland conditions, rather than adding further indirect environmental proxies.

## References and data availability

Carroll, C., Saenz, D. & Rudolf, V. H. W. (2023). *Tracking phenological distributions and interaction potential across life stages*. **Oikos**, DOI: [10.1111/oik.09773](https://doi.org/10.1111/oik.09773). Associated Dryad source: [10.25338/B8G92P](https://doi.org/10.25338/B8G92P).

Takahashi, M. & Ruszala, E. (2023). *Egg predators improve the hatching success of salamander eggs*. **Ecology and Evolution**, DOI: [10.1002/ece3.10427](https://doi.org/10.1002/ece3.10427). Associated Dryad source: [10.5061/dryad.bnzs7h4gn](https://doi.org/10.5061/dryad.bnzs7h4gn).

Mohonk Preserve. *Vernal Pool Amphibian Breeding Ecology Monitoring*, GBIF-US IPT source, DOI: [10.15468/dypfbs](https://doi.org/10.15468/dypfbs), original archive v1.1.

Analysis source: `ecology/data/mohonk/analyze_egg_stage_priority.py` and `ecology/data/mohonk/test_stage_priority.py`. Derived results: `ecology/mohonk/MOHONK_WOODFROG_SALAMANDER_STAGE_PRIORITY_RESULT_2026-10-25.md`. These are independent of `frogcs` RC6; the submitted paper on `main` has not been edited.

---

**Editorial status:** An evidence-based ecology research note **draft**, not a verified novelty/causality claim or a manuscript ready for immediate submission to a mechanistic ecology journal. The core new descriptive finding needs stronger mechanistic endpoints (predation and hatching success) to warrant a separate high-impact interaction-network paper.
