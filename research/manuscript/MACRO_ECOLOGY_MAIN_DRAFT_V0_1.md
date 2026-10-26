# Where frogs call: three-guild niche associations across wetland vegetation and antecedent surface water

**Active frogcs macroecology manuscript v0.1, 2026-10-26 — WORKING / NOT SUBMISSION READY.** [Macro-first editorial authority](../MACRO_FIRST_EDITORIAL_DECISION_2026-10-26.md). This manuscript is an exploratory analysis of **species occurrences, modeled community niches, adult acoustic use, landscape vegetation, previous-year water, and historical site use**. It supersedes the prior [stage-structure-led working draft](INTEGRATED_FROG_ECOLOGY_DRAFT_V0_1.md) as the intended current paper, but does not rewrite that source or the completed RC6 candidate.

## Single research question

**Do landscape-scale associations between strong frog calling and odonate niche suitability differ with pond-breeding caudate suitability, and how do flooded vegetation, antecedent surface water, and recurrent site use contextualize those associations?**

The guilds are **Anura, Odonata and Caudata**; niche values are estimated from species occurrences, **not** direct predator counts. The underlying calling observations are **roadside listening locations**, which may be near more than one breeding pool. Thus this is a macroecological study of environmental and multispecies associations, **not** a demonstration of local competition, predation or refuge.

## Abstract — the macro results lead

Species distribution and wetland habitat can structure where seasonal animal activity is recorded, but correlations among potential community niches and reproductive behavior may depend on other guilds and environmental context. We combined North American frog acoustic surveys with ecologically screened GBIF species records, two-background presence–background models of frogs, odonates and caudates, landscape flooded vegetation, preceding-year remotely sensed surface water, and historical acoustic site use. From 30 selected candidates, 28 species could be modeled (15 anurans, seven caudates, six odonates), with **4,248 repeatedly surveyed acoustic locations** in the main ecological analysis. Strong frog calling frequency had a weak negative whole-region Spearman correlation with modeled odonate suitability (**ρ = −0.095** under uniform background, **−0.086** under a target-group background), which weakened within monitoring routes. The negative association depended on pond-breeding caudate suitability: the **high minus low** caudate stratum difference in odonate–calling correlations was **−0.385** (95% route-bootstrap interval **−0.509 to −0.240**) under uniform background and **−0.179** (**−0.328 to −0.029**) under the target-group background. Landscape flooded vegetation modified the whole-region associations, although a positive three-way odonate×caudate×vegetation coefficient was clearly separated from zero only under uniform background (**+0.037**, interval **+0.008 to +0.068**) and attenuated in within-route comparisons. In **4,040** predefined within-run strong-calling versus silent-location comparisons, preceding-year conditional surface-water detection frequency within 3 km was **1.481 percentage points lower** on the strong-calling side (interval **−2.601 to −0.294**, **3,907** eligible pairs), whereas water-detected **area fraction** did not show a comparable difference. Strictly prior strong calling at those locations was **27.68 percentage points more frequent** on the currently strong-calling side (interval **+25.07 to +30.17**) under resampling of 388 physically connected route components. These source- and scale-dependent associations reveal a community and wetland landscape context to frog chorusing without establishing the direction of trophic effects, the identity of individual frogs, or the hydroperiod of a particular breeding pond.

**Keywords:** macroecology; amphibian chorusing; Odonata; Caudata; species distribution models; wetland vegetation; satellite surface water; site history; community assembly.

## 1. Introduction

Patterns of seasonal reproductive activity are shaped not only by immediate climatic conditions but also by the spatial distributions of potentially interacting taxa and their environments. Wetlands provide changing water availability and structural habitat; different members of a community may respond to these conditions independently or through unobserved interactions. A useful macroecological question is therefore **where species activity and community-niche opportunities covary**, and whether that relationship is spatially uniform.

### Motivating observation: from RC6 to a separate macro question

An **earlier analysis of the same NAAMP acoustic programme** investigated how rain-associated activation is allocated among species and sequential monitoring stops. Its excess within-taxon multi-site concentration relative to first-order acoustic generators motivated a broader question: **what kinds of community niches and wetland landscapes occur around repeatedly used calling locations?** The RC6 result is an **origin of the hypothesis**, not an independent replication, an endpoint fitted in this paper or a figure deserving the main results section. Its historical full-methods scientific package is retained unchanged as a separate [archived candidate](../../paper/manuscript.md). Because the present site analyses also use NAAMP source data, the two cannot be counted as independent datasets.

### Competing ecological explanations

**Shared habitat filtering** predicts guild niches, acoustic detections and wetland vegetation may covary because the same macroclimate and geography are favorable. **Guild-dependent sorting** predicts a different odonate–calling association where pond-breeding caudates are more environmentally suitable. **Wetland structural context** predicts vegetation can modify these associations, but static remotely sensed plants cannot identify actual protective shelter, oviposition or emergence substrate. **Historical conditions** predict that prior site use and antecedent water occurrence can be informative without requiring a direct biological interaction. These explanations are not mutually exclusive.

## 2. Methods

### 2.1 Species occurrences and guild niche construction

[Source-eligibility and modeling report](../NAAMP_INTERACTION_SSDM_REPORT_2026-10-26.md): candidate selection compared regional GBIF keys with independent taxonomic/checklist evidence and categorized GloBI relationship types. GloBI source terms include eats/preysOn but also coOccursWith/interactsWith and do **not** all represent predation. Thirty candidate species (17 Anura, seven Caudata, six Odonata) supplied **36,627 retrieved GBIF records**; **28 species** (15 Anura, seven Caudata, six Odonata) met the frozen modeling-coverage rule. Two inadequately recorded taxa were left unmodeled, not set to biological zeros.

Presence–background models used regional thinned species records, WorldClim climatic variables and EarthEnv flooded vegetation/open-water covariates. We retained **uniform** and **target-group** background constructions and geographically blocked evaluations. Models predicted relative environmental suitability for **11,947 NAAMP coordinate records**; **only 4,248 sufficiently repeated physical source listening sites** entered the primary descriptive association analysis. Site-level potential richness is the count exceeding species-specific fitted thresholds **within these 28 modeled species**, not a census of all possible regional taxa or realized pond assemblages. Odonate suitability includes broad original species occurrences, not measured aquatic nymph densities.

### 2.2 Macro acoustic responses and correlation scale

The [site-use audit](../NAAMP_SITE_USE_ASSOCIATION_REPORT_2026-10-26.md) retained 4,248 locations with ≥6 qualifying survey visits spanning ≥3 years (2001–2015; 432 route-linked components). The leading response is the **fraction of acoustic visits on which any frog species attained CallingIndex ≥ 2**; a separate response uses years with strong calls. This is not frog density or reproductive success, and it differs from RC6's taxon-specific multi-stop allocation statistic.

We examined whole-region **Spearman correlations**, original-route-centered rank correlations, fixed original guild suitability tertiles, and continuous **Odonata × pond-breeding-Caudata** rank interactions. Uncertainty was quantified by **1,000 route-level resamples**, conditional on fitted SDM values. All background, grouping and spatial-scale comparisons remain visible. Exploratory feature screening has not received a familywise multiplicity correction, and SDM/remote-sensing uncertainty is not fully propagated.

### 2.3 Flooded-vegetation landscape context

[Observed vegetation report](../REMOTE_VEGETATION_NETWORK_REPORT_2026-10-26.md): original hash-checked EarthEnv static flooded-vegetation, herbaceous vegetation and open-water raster values were sampled with source-consistent no-data treatment. Site-centered 1-km and **3-km** neighborhoods were area-weighted. Sites with some 3-km flooded vegetation increased from **46 pixel-center positive** to **506 of 4,248 landscape neighborhoods**, reflecting broader coverage, not 506 confirmed vegetated breeding ponds. Within both SDM backgrounds, vegetation and guild suitability ranks were entered with **all lower-order terms** before estimating odonate×caudate×vegetation products. Whole-region and within-route analyses were separate. The input vegetation mean versus spatial standard-deviation rank correlation was **0.99984**, so these are not independent vegetation structural traits.

### 2.4 Antecedent water and matched calling sites

[Fixed-pair source](../NETWORK_FIXED_PAIR_REPORT_2026-10-26.md) supplied **4,040 within-run strong versus silent listening-stop pairs** formed under common recorded meteorological/vegetation/noise constraints; no re-pairing was performed for the present results. There were **389 route labels**, combined into **388 connected physical-site components** for clustered bootstrap uncertainty (2,000 draws). Both members of each pair had sufficient observations from prior years; a strict calendar-year exclusion removed current and future information from historical strong-call fractions.

We acquired **72 preceding-year GLAD annual surface-water tile-years for 2001–2014**, recording original source hashes and building covariates for 6,293 site-years. For both members of each original pair, source-neighborhood 3-km and 1-km indices were calculated: (a) mean water classification frequency across valid satellite pixels; (b) fraction of pixels ever detected as water; (c) **water frequency conditional on pixels with at least one water detection**. Criterion (c) is undefined without such pixels; those pairs are **excluded rather than imputed zero** (3 km n = 3,907, 1 km n = 2,204). The GLAD annual measure is satellite **observation frequency**, not physical pond flooding days or actual hydroperiod.

### 2.5 Comparative unit safeguards

The source-authenticated [species-occurrence-first](../results/species_occurrence_first/REPORT_2026-10-26.md) layer retains **464,941 source-native survey×species records** from NAAMP, NPS, INBO and Hungary, preserving independent taxonomic assessments and different meanings of surveyed zero. It does not join source recording stations to verified ponds. Other-source co-detections are supplementary exploratory context, not a pooled independent confirmation of the main niche association.

A further **route-held-out fixed-pair predictive** comparison was also retained as a negative check, but **predictive improvement is not the criterion** for reporting the observed whole-region macro correlations. Statistical estimands (Spearman rho, standardized rank coefficients, pairwise percentage-point contrasts, temporal water occurrence) are compared by interpretation, **not pooled as commensurate coefficients**.

## 3. Results

### 3.1 Whole-region odonate suitability has a weak negative association with acoustic site use

Among **4,248** sites, the correlation between mean modeled odonate suitability and strong-calling visit fraction was **ρ = −0.095** (95% interval **−0.154 to −0.035**) for uniform background and **−0.086** (**−0.149 to −0.018**) for target-group background. The corresponding within-route correlations were **−0.027** (**−0.061 to +0.007**) and **−0.019** (**−0.059 to +0.022**). Thus the sign of broad spatial covariation does not justify inferring local nymph-driven frog avoidance.

### 3.2 Pond-breeding caudate suitability changes the pattern

| SDM background | Low pond-Caudata suitability | High pond-Caudata suitability | High minus low association |
|---|---|---|---|
| Uniform | **ρ +0.101** (−0.008 to +0.202; 1,417 sites) | **ρ −0.284** (−0.368 to −0.201; 1,412 sites) | **−0.385** (−0.509 to −0.240) |
| Target-group | **ρ −0.004** (−0.112 to +0.100; 1,420 sites) | **ρ −0.183** (−0.298 to −0.077; 1,416 sites) | **−0.179** (−0.328 to −0.029) |

These are [the core empirical macro correlations](../ODONATA_CAUDATA_VEGETATION_PATTERN_REPORT_2026-10-26.md). The low-Caudata uniform positive point estimate **is not independently distinguishable from zero**. A continuous standardized rank interaction was **−0.115** (−0.169 to −0.059) under uniform and **−0.057** (−0.117 to +0.001) under target-group background. Within-route associations became smaller, exposing geographic and environmental confounding and sampling-scale dependence.

### 3.3 Landscape vegetation modifies some guild correlations but does not identify a refuge

For 3-km vegetation neighborhoods and whole-region pond-Caudata niche association models:

| Context term | Uniform background, beta (95% interval) | Target-group background, beta (95% interval) |
|---|---|---|
| Odonata × vegetation | **−0.087** (−0.124 to −0.048) | **−0.064** (−0.115 to −0.014) |
| Caudata × vegetation | **+0.058** (+0.015 to +0.101) | **+0.046** (−0.022 to +0.109) |
| Odonata × Caudata × vegetation | **+0.037** (+0.008 to +0.068) | **+0.027** (−0.024 to +0.073) |

The three-guild coefficient was not comparably supported with target-group background or within-route models (uniform within-route approximately **−0.001**, interval −0.035 to +0.032); it also attenuated with 1-km neighborhoods. Source vegetation represents **landscape cover**, not larval hiding, egg substrates or plant sprouting dates. The main observation is **a context- and scale-dependent moderation of guild niche association**.

### 3.4 A previously wet landscape is not the same as a water-persistent breeding pond

Across **3,907** fixed pairs with valid prior-year, 3-km **ever-water pixels**, the difference in their water-detection frequency was **−1.481 percentage points** (−2.601 to −0.294): current strong-call side **46.734%**, silent side **48.215%**. At 1 km, the difference was **−1.017** (−2.862 to +0.783; **2,204** pairs). In contrast, the 3-km **water-detected area fraction** differed by only **−0.088 points** (−0.395 to +0.213, **4,040** pairs). These are [water classification results](../PRIOR_WATER_NETWORK_REPORT_2026-10-26.md), not measured local pond hydroperiod or frog preference for drying.

### 3.5 Strong calling remains associated with the strict preceding acoustic history

In all **4,040** fixed pairs, the site that strongly called had **+0.27684** greater fraction of **strictly earlier** strong-call survey visits (95% interval **+0.25071 to +0.30175**, 388 route-linked components) than the silent site. Expressed as conventional percentages this is **+27.68 points** (+25.07 to +30.17). Across low/medium/high previous-water-frequency strata, historical advantages were **+29.59**, **+28.12**, **+29.60** points. Historical use is not individual philopatry or a measured pond return.

### 3.6 Predictive null and scale distinction

In a separate route-held-out allocation test, adding potential modeled richness to a strict prior-use baseline produced a predictive log-score change of **−0.00019** nat/pair (interval −0.00301 to +0.00254), while adding the 28-species composition produced **−0.00760** (−0.01864 to +0.00318). In contrast, historical-use-only prediction had a gain of **+0.17059** (0.14208 to 0.19722) against a 0.5 classifier. These outcomes **do not cancel out the whole-region associations**; the predictive and correlation metrics represent different scales and scientific questions.

## 4. Discussion

**Ecological interpretation.** The most distinctive pattern is **stronger negative Odonata suitability–frog chorusing correlation in landscapes modeled as suitable for pond-breeding Caudata**. This is incompatible with asserting a universal two-guild correlation, but compatible with more than one biological explanation. Shared geography, climate and wetland class can structure all three potential niches. Genuine competition, size-dependent predation or effects of a third guild remain untested as interactions between actual animals at the same identified pond.

**Environmental moderation.** In the source landscape, static flooded-vegetation summaries show some signed modification of guild correlations, but neither the sign of a single three-way coefficient nor a coarse 3-km neighborhood identifies effective refuge, stem structure or new plant emergence. Similarly, an annual frequency of satellite water detection must not be equated with uninterrupted hydroperiod. Strong acoustic use and lower previous-year conditional open-water classification can co-occur without identifying deliberate pond selection.

**History and geographic heterogeneity.** The larger and consistent historical-use difference within fixed strong/silent pairs deserves its own interpretation. An acoustic site may be persistently suitable or easier to detect. No individuals were tracked and the multi-guild niche surfaces are not observed densities. Within-route effects are much smaller than regionwide effects; do not combine them into one single causal slope.

**Limitation and future study.** These are **source-backed exploratory associations**, with sensitivity to species background, radius, fitted guild composition and reused NAAMP source sites. SDM uncertainty is held fixed during route bootstrap and multiple-comparison effects are not fully addressed. A prospective pond-scale design would need verified actual frog calling sources, repeated pond hydroperiod and water-level monitoring, emergent plant structure/use, predator stage, prey survival, and a true exposure comparison. The globally harmonized source-native species-occurrence layer can inform what taxa/seasonal contrasts to sample, but is not already a joint same-pond census.

## 5. Conclusion

At macroecological scale, the relationship between frog strong-calling site use and odonate niche suitability **depends on pond-breeding caudate niche context** and displays additional background/scale dependence involving wetland vegetation, preceding surface-water occurrence and strong historical acoustic-site use. These correlations are valuable in their own right, independent of whether a future mechanism or cross-source forecast succeeds. The next field study can distinguish shared habitat filtering from stage-specific trophic or refuge effects; **none has yet been identified causally** in the present data.

## Main paper figure and data plan

- **Fig. 1:** source selection of 30 candidate/28 modeled species, 11,947 spatial covariate predictions, 4,248 recurrent main sites and 4,040 fixed acoustic pairs. Show physical recording stops, NOT invented breeding ponds.
- **Fig. 2 (centerpiece):** odonate–calling association by pond-Caudata tertile, two background schemes, site sample sizes, region/route intervals.
- **Fig. 3:** vegetation × guild association coefficients, with all lower-order terms, 1/3-km and geographic scale contrasts.
- **Fig. 4:** fixed-pair historical-use difference, preceding-year water-detection frequency versus area fraction, full missingness denominators and 388 resampling components.
- **Supplement:** nine-source occurrence/protocol compatibility, detailed GloBI/GBIF taxon audit, all predictive negative controls, and separate RC6/stage-network archives.

## Provenance and submission status

Original [macro synthesis](../FROGCS_MACRO_ANALYSIS_FINAL_REPORT_2026-10-26.md); [guild source/model](../NAAMP_INTERACTION_SSDM_REPORT_2026-10-26.md); [three-guild correlations](../ODONATA_CAUDATA_VEGETATION_PATTERN_REPORT_2026-10-26.md); [vegetation](../REMOTE_VEGETATION_NETWORK_REPORT_2026-10-26.md); [preceding-year water](../PRIOR_WATER_NETWORK_REPORT_2026-10-26.md); [fixed pair & history](../NETWORK_FIXED_PAIR_REPORT_2026-10-26.md); [complete source audit](../RESEARCH_COMPLETION_AUDIT_2026-10-26.md); [species occurrence first](../results/species_occurrence_first/REPORT_2026-10-26.md); [source snapshot and offline replay](../reproducibility/README.md). Verified [main macro snapshot CI](https://github.com/zuizui0223/frogcs/actions/runs/40302573550): **894 original files**, **58 tests**, seven result tables replayed. Reproduction of this manuscript **does not require rerunning RC6**; it also does not claim raw 2.86-GB GLAD reacquisition or GBIF refitting was repeated by that offline replay.

This is an **editorial reorganization of existing measured results**. The new macro-first text has **not** undergone formal journal submission, outside peer review or independent causal confirmation.
