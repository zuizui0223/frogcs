# Stage-structured timing of frog–salamander encounters in vernal pools: field co-detection and context-dependent consequences of egg predation

**Ecology-first integrative research note — revised 25 October 2026. NOT SUBMITTED.**
**Evidence hierarchy:** NEW reanalysis of long-term pond-stage records + REANALYSIS OF AN ALREADY PUBLISHED experiment. Not a new manipulation, not independent confirmation of egg-predation outcomes, and not the NAAMP adult chorus study.

## Abstract

**Context.** Interactions in temporary wetlands depend on which *life stages* coincide. Wood-frog tadpoles can consume spotted-salamander egg masses in experiments, but a trophic interaction requires the two stages to overlap in natural ponds. Such timing also matters because predator exposure can have opposing consequences for eggs with and without gelatinous protection.

**Methods.** We quantified first positive egg records and dated tadpole–egg co-detections in the original Mohonk Preserve amphibian monitoring archive (11 northeastern U.S. vernal pools, 2016–2021, 59 pool-years and 240 pool-date visits). We compared the 235 pool-dates assessing both focal stages with an exact within-pool-year fixed-marginal survey-date permutation benchmark and a circular-shift sensitivity. Separately, we verified and re-tabulated the published Takahashi and Ruszala factorial laboratory dataset (32 spotted-salamander egg masses, n=4 per jelly-layer × wood-frog-tadpole-density treatment).

**Results.** In 44 pool-years when both egg stages were detected, wood-frog eggs were first recorded before spotted-salamander eggs in 29, on the same survey date in 14 and after in one. Wood-frog tadpoles and spotted-salamander eggs were co-detected on 31 pool-dates, compared with 23.87 expected from each pool-year's observed stage-positive date frequencies (ratio 1.30; exact conditional benchmark upper-tail 0.0051; circular-shift 0.0053). This excess was heterogeneous across years: omitting 2020 reduced the ratio to 1.17 and benchmark tail to 0.118. Tadpole co-detection with Jefferson-salamander eggs was 9 versus 8.1 expected (ratio 1.11), without comparable excess. The independent, **previously published** laboratory experiment showed that moving from no tadpoles to high tadpole density increased mean hatching by 18.9 percentage points for intact salamander egg masses but decreased it by 90.7 points for eggs stripped of jelly, a 109.5-point factorial contrast. Egg mass, not embryo, was the experimental replicate.

**Inference.** The field record supports a repeatable, albeit year-dependent, **temporal opportunity** for an independently demonstrated predator–egg interaction. The laboratory record establishes context-dependent consequences *under experimental conditions*. Neither dataset links naturally occurring field attacks to embryo survival. Reproduction timing, enemy-stage phenology, protective egg architecture and pond water/oxygen conditions motivate a testable multilevel food-web hypothesis rather than a demonstrated ecological causal chain.

**Keywords:** breeding chronology; amphibian community; *Lithobates sylvaticus*; *Ambystoma maculatum*; vernal pools; phenological overlap; developmental stage; indirect interactions; egg jelly; tadpole predation.

## Introduction

The ecological role of an organism changes profoundly across development. A calling adult frog advertises mating activity but is not equivalent to an egg-laying female, its tadpoles, or a predator capable of feeding on a heterospecific egg mass. In temporary ponds, the temporal gap between reproductive events can shift which developmental stages are present together, potentially changing the direction and strength of trophic edges without changes in the adult species assemblage.

Phenological overlap across amphibian calling and larval life stages is *already well studied*: Carroll, Saenz and Rudolf (2023) analysed nine amphibian species at eight ponds over six years. Nor is the predator–egg link novel: Takahashi and Ruszala (2023) experimentally demonstrated that wood-frog tadpoles interact with spotted-salamander egg masses and that jelly-layer costs and benefits vary with predator exposure. The missing step addressed here is narrower: **in actual repeatedly monitored vernal pools, how often does the precise, trophically plausible tadpole–egg stage pair coincide on the same survey date beyond its marginal occurrence frequency?** We then distinguish that natural opportunity from the conditional consequences demonstrated in the separately published egg-mass experiment.

We predicted *exploratorily* that the documented early-wood-frog egg chronology would create repeated windows with tadpoles coincident with spotted-salamander egg masses. We make no advance claim that natural attacks occur or benefit prey.

## Data and analysis

### Mohonk Preserve: dated life-stage monitoring

We used the GBIF-US IPT original Mohonk Preserve vernal-pool amphibian archive (DOI 10.15468/dypfbs, original archive v1.1, SHA256 `0309abd9afa4a224287d6853d79ae1f7111a3a7bb19b0d2337f05c280ef12b34`; original occurrence text SHA256 `d52b288608a40c3b721f3561a57ace34728975522892a4fdc1d0b4f6ffb3610e`). We restricted the primary analyses to 2016–2021, when monitoring more regularly contained explicit assessed zero counts for species × life-stage cells. The full archive contains 13,862 records covering a longer and heterogeneous reporting period; these earlier records cannot support equivalent absence inference.

Eleven generalized coordinate-based pond identities produced 59 pond-years and 240 pool-date sampling visits. A stage-positive day had an explicitly recorded count greater than zero; an explicitly reported zero was an assessed nondetection; an absent stage record was **not assessed**, never zero. A pool-year's first positive egg date was the minimum *observed* date, **not an exact laying date**. A prospective tadpole–egg encounter required positive wood-frog `lifeStage=tadpole` and spotted-salamander `lifeStage=egg` records on the same pool-date. We did not infer attack events or nest-scale adjacency from generalized pond coordinates.

For the new **exploratory** opportunity benchmark, we retained the 235 pond-dates where both target stages were explicitly assessed. For each pool-year `p`, the calendar had `n_p` sampled days, `a_p` tadpole-positive days, and `b_p` salamander-egg-positive days. Under a date-shuffling benchmark conditional on those stage-day totals, `X_p ~ Hypergeometric(n_p,a_p,b_p)`. We convolved its exact discrete distributions across pool-years and reported observed `ΣX_p`, expected `Σ(a_p b_p/n_p)`, exact conditional upper tail and null central 95% interval. A second benchmark cyclically rotated one stage sequence through every possible offset within each pool-year to retain within-season clustering while changing alignment. This wraps the study-season boundaries and is not an ecologically exact phenology null. The calculations were **not preregistered before the original 31 co-detections had already been observed**; tail values are exploratory reference measures, not independent-pond-year frequentist significance levels. We separately tabulated Jeffrey/Jefferson salamander egg-stage events as a different species pair, not a negative-control for predation.

Year and leave-one-pond/year analyses described heterogeneity; repeated years at a single pond are not independent ecological replicates. We did not search across many lag windows, study dates or predators to optimise a result.

### Independent published egg-mass experiment

We obtained the original public `Hatch_w.csv` from Takahashi & Ruszala (2023), archived on Dryad (DOI 10.5061/dryad.bnzs7h4gn, version 4; file SHA256 `8bf8166185fb1607710bd3bfd9a81d9f82ea34c1d8ae8874f562d5bee70076db`). The experiment randomised 32 spotted-salamander egg masses into eight combinations of **outer jelly intact/removed × no/low/medium/high wood-frog-tadpole density**, four masses per treatment. We preserved each original recorded hatching proportion and the authors' correction of one value exceeding the estimated clutch denominator to one. Missing incubation `Days='na'` where no embryos hatched was not treated as zero days.

We re-tabulated cell means and the high-versus-absent-predator contrast within each jelly-layer condition. A mean-scale difference-in-differences describes the interaction. A **20,000-replicate, seed 2840223, egg-mass-stratified percentile bootstrap** quantifies its sample sensitivity; because only four egg masses per cell, this interval is not an external ecological sampling uncertainty interval. These are measurements and treatment results **previously published**; the original study already established the interaction.

## Results

### Wood-frog egg detection generally preceded spotted-salamander egg detection

In the primary 2016–2021 series, eggs of both species were recorded in 44 pond-years. Wood-frog eggs were detected first in 29, both types on the same date in 14, and spotted-salamander eggs first in one. Among 30 strictly ordered first-survey detections, 29 were wood-frog-first. The median observed date gap was six days (spotted minus wood-frog first-positive detection). Restricting to at least three pool-year visits retained 26 wood-first, seven ties and one spotted-first; restricting to both egg detections after the first visit retained 14, five and one, respectively.

An **exploratory historical-positive-only check** used older Mohonk records separately. Between 1931 and 2015, 129 pond-years across 27 recorded years contained at least one positive egg-stage report for both species, but the chronology was tied on the sampling date in 98. Strictly distinguishable dates favoured wood-frog first in 26 versus spotted first in five; among the older pond-years with at least three recorded visits, the corresponding counts were 22 wood-first, 21 ties and four spotted-first (47 pond-years). These early years lack comparable explicit zero-stage reporting and vary greatly in survey effort: they do **not** substantiate long-term climate trends or exact oviposition dates.

### Stage co-detection exceeded its within-pond-year sampled-day benchmark

Wood-frog tadpoles and spotted-salamander eggs were co-detected on **31** of the **235** pool-dates that explicitly assessed both target stages, distributed across 29 of 59 pond-years. Holding fixed each pond-year's number of assessments, tadpole-positive survey dates and spotted-salamander-egg-positive survey dates, the expected joint count was **23.869**. The observed/expected ratio was **1.299**, and the exact conditional date-shuffling reference 95% range was 19–29 co-positive dates (upper-tail **0.00507**). A within-year circular-shift benchmark, preserving each binary stage-series pattern but wrapping seasonal endpoints, gave upper-tail **0.00526**.

The pattern was **not consistent across all years**: yearly observed/conditional-expected paired-date counts were 5/4.00 (2016), 4/2.45 (2017), 1/2.15 (2018), 2/2.73 (2019), 10/5.97 (2020) and 9/6.57 (2021). Omitting 2020 left 21 observed versus 17.90 expected (upper-tail **0.118**). The result is thus sensitive to the 2020 contribution even though no single pond was indispensable in a leave-one-pond-out diagnostic. The co-detection association cannot establish that tadpoles consumed eggs or that the same spring date would be detected given a different sampling schedule.

With Jefferson-salamander (`Ambystoma jeffersonianum`) eggs as a second stage-pair comparison, there were **nine** observed co-detections against **8.1** expected (upper-tail **0.398**). This is a taxon-specific descriptive contrast, not proof of preference or an interaction absent in the Jefferson species.

### Published experimental consequences depend strongly on jelly defense

All eight treatment cells of the independently published experiment contained four original egg masses. The verified mean hatching success percentages were:

| Wood-frog tadpole treatment | Jelly intact (n=4 masses) | Jelly removed (n=4 masses) |
|---|---:|---:|
| No tadpoles | 72.26% | 90.69% |
| Low tadpole density | 63.29% | 32.76% |
| Medium tadpole density | 77.19% | 0% |
| High tadpole density | 91.11% | 0% |

Relative to absence of tadpoles, high density increased mean hatching success **18.85 percentage points** for intact egg masses but decreased it **90.69 percentage points** when jelly was removed. Their descriptive factorial difference-in-differences was **109.55 percentage points** (egg-mass-stratified bootstrap 95% interval **90.58–125.56 pp**, a small-n sensitivity, not a newly discovered effect). Under medium and high tadpole density, no jelly-removed clutches hatched, so mean incubation time is **missing by outcome**, not zero. The original article had already reported strong jelly × predation interaction.

Crucially, this experiment did not manipulate natural Mohonk field date offsets, pond oxygen or field predation; no *cross-dataset* experimental effect estimate is possible.

## Discussion

### A directional developmental encounter window, not just shared adult habitat

The field pattern goes beyond adults of two species occupying the same pond. Wood-frog egg detection commonly preceded spotted-salamander egg detection, and the particular **tadpole–egg stage combination** was documented repeatedly on the same survey date. When constrained by the observed within-pond-year frequency of each stage, actual co-detection was about 30% above the random sampled-day alignment benchmark. This is a novel **exploratory field-level description of encounter opportunity**, not proof of realised feeding. The strength of the association varies by year and is plausibly sensitive to rainfall, ponds' spring drying trajectories and observation timing, none of which can be isolated here.

### Enemy identity is stage-specific; the sign of the interaction can depend on defense

The independently published experiment supplies a mechanistic reason that a stage-overlap window can matter: a wood-frog tadpole is capable of damaging spotted-salamander eggs, yet intact outer egg jelly changes the effect of the tadpoles' exposure. The earlier authors proposed that predators may remove some jelly and improve oxygen diffusion even as they pose direct predation risk. **Oxygen diffusion and actual egg-jelly erosion are not measured columns in the available five-variable original experimental table**, so that proposed pathway is mechanistic interpretation, not identified mediation. Importantly, high densities can destroy eggs under other conditions; positive outcomes are neither general nor guaranteed.

The encounter-opportunity field series and egg-mass experiment occupy *different ponds, years and protocols*. Their synthesis yields a clear ecological prediction: reproductive priority can alter the duration of exposure to a stage-specific enemy, while the egg's defensive architecture and pond microenvironment govern the sign/magnitude of its reproductive consequence. **It does not establish that any Mohonk embryo benefited or suffered from predators.**

### Relation to life-stage networks and earlier literature

The general idea of temporal interaction networks across amphibian life stages was demonstrated previously (Carroll, Saenz & Rudolf, 2023, *Oikos*). Here the narrower ecological advancement is a **source-verified, stage-specific opportunity benchmark for a predator–egg pair**, and a transparent quantification of an already documented defense-dependent reproductive effect. Neither alone demonstrates trophic-network rewiring. Dragonfly larvae, fish and adult frog-call eavesdroppers were **not monitored together** in the Mohonk source, so the proposed broader three-guild network remains a separate hypothesis.

The earlier NAAMP `frogcs` study found rain-associated switches from silence to strong multi-site choruses at recurrent physical listening stations. NAAMP did not measure egg timing, tadpole predation or embryo hatching in these ponds. Its chorus-state findings can motivate studies linking acoustic phenology to offspring enemy exposure, **but cannot be treated as corroborating trophic interactions**.

### Limits, novelty and the decisive independent test

First-positive records are survey-interval- and left-censored; 2016–2021 consists of only 11 physical pond clusters. Within-pond-year random-date allocation may overstate surprise if both stages share the same spring phenology; circular shifting also creates artificial end-to-start transitions. The association was explored after the raw overlap count was initially known, and repeated pond-years are correlated. Strong contribution from 2020 restricts claims of a temporally stable effect. The experimental treatment n is only four egg masses per cell, including a corrected hatching proportion, and is already published. Thus the appropriate article category at this stage is **an integrative observational natural-history note**, not a new mechanistic experiment or a proven multi-trophic network reversal.

A genuine new ecology paper at higher mechanistic resolution should study the *same ponds* through an entire season: timestamp recorded male calls, actual oviposition and frog tadpole emergence, spotted-salamander egg mass stage/attack, water depth/oxygen, tadpole size and predator density, vegetation shade and embryo hatching/survival. Replicate **egg masses/pond-years**, not embryos/survey days, and verify whether the interaction of relative stage order with measured oxygen/jelly thickness changes the net effect of exposure. A separate fish–odonate–amphibian module could then ask about indirect predation only if the other guilds are actually observed.

## Conclusion

Reproductive order and developmental timing structure when a documented frog-tadpole–salamander-egg pair can meet in the wild. In one independent vernal-pool monitoring archive, these stages were co-detected more often than their sampled-day prevalence alone predicts, although the signal was year-dependent and did not record predation. Published egg-mass experiments demonstrate that the consequence of tadpole exposure changes sharply with gelatinous egg defense. These two evidence levels motivate, but do not yet prove, the ecological hypothesis that **phenological encounter windows and protective architecture jointly determine the net costs and benefits of an enemy**.

## Data, verification and references

Field source: Mohonk Preserve. *Vernal Pool Amphibian Breeding Ecology Monitoring*, GBIF-US IPT publisher DwC-A, DOI [10.15468/dypfbs](https://doi.org/10.15468/dypfbs), original archive v1.1. Field source SHA256 and QC are in `ecology/mohonk/MOHONK_WOODFROG_SALAMANDER_STAGE_PRIORITY_RESULT_2026-10-25.md`. Exact null code: `ecology/data/mohonk/analyze_stage_overlap_null.py`, contract `EXPLORATORY_STAGE_ALIGNMENT_NULL_CONTRACT_V0_1.md`; [passing action run 40114746815](https://github.com/zuizui0223/frogcs/actions/runs/40114746815).

Existing experimental source: Takahashi, M. K. & Ruszala, D. (2023). Egg predators improve the hatching success of salamander eggs. *Ecology and Evolution*, DOI [10.1002/ece3.10427](https://doi.org/10.1002/ece3.10427); original published Dryad [10.5061/dryad.bnzs7h4gn](https://doi.org/10.5061/dryad.bnzs7h4gn), version 4 `Hatch_w.csv` SHA256 `8bf8166185fb1607710bd3bfd9a81d9f82ea34c1d8ae8874f562d5bee70076db`. Reanalysis code `ecology/dryad_takahashi/reanalyse_original_factorial.py`; [passing action run 40115055827](https://github.com/zuizui0223/frogcs/actions/runs/40115055827). All original experimental outcomes were reported by those authors; our bootstrap describes the published data anew and is not a new experiment.

General phenology baseline: Carroll, C., Saenz, D. & Rudolf, V. H. W. (2023). Tracking phenological distributions and interaction potential across life stages. *Oikos*, DOI [10.1111/oik.09773](https://doi.org/10.1111/oik.09773); source Dryad [10.25338/B8G92P](https://doi.org/10.25338/B8G92P).

**Provenance:** All new Mohonk and old experiment analyses remain in `research/ontogenetic-interaction-phenology-2026-10`. The frozen JAE RC6 `frogcs` `main` is untouched. This draft is for ecological analysis and editorial review, not ready for submission without a stronger same-system causal endpoint.
