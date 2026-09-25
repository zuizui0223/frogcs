# Rainfall pulses increase frog active-community richness through species-selective reassembly

## Abstract

1. **Short environmental pulses can change not only how strongly animal communities are active, but which species constitute the active assemblage.** Rainfall effects on frog calling are well known, yet it remains unclear whether wetter conditions simply amplify a stable community or transiently reorganize community membership.

2. **We tested this using 15 years of standardized North American Amphibian Monitoring Program surveys.** We compared 4,236 wetter–drier pairs drawn from the same route and the same seasonal sampling window across adjacent observed years (585 routes, 21 states). We quantified active-species richness, turnover versus nestedness, species-specific wet recruitment, and trait correlates of recruitment.

3. **Greater rainfall contrast predicted higher active-community richness.** Wetter runs contained more acoustically active species, and wet-minus-dry richness increased with rainfall contrast (β = 0.286 species per unit log-rain contrast, 95% CI 0.165–0.407, P = 3.81 × 10^-6). The effect persisted in exact consecutive-year pairs (β = 0.301, P = 1.60 × 10^-4).

4. **The richer wet assemblage was not a simple nested extension of the dry assemblage.** Nestedness did not increase with rainfall contrast, whereas turnover increased in the consecutive-year sensitivity (β = 0.0184, 95% CI 0.00470–0.0321, P = 0.00850). Species responses were strongly heterogeneous (adjusted Q = 144.0, df = 28, P = 1.46 × 10^-17), with wet-associated and dry-associated taxa remaining after temperature, survey-date, rain-contrast and year-gap adjustment. A secondary trait analysis showed that smaller-bodied species had more positive wet-recruitment responses (β = -0.367 on log body size, 95% CI -0.515 to -0.219, P = 1.23 × 10^-6).

5. **Rainfall was therefore associated with transient, species-selective reassembly of the acoustically active frog community rather than a uniform rise in activity by an unchanged assemblage.** The body-size gradient is consistent with stronger hydric constraint in smaller anurans, suggesting that short rainfall pulses may act as community filters by differentially releasing water-balance constraints.

## Keywords

active community; anurans; body size; community assembly; environmental filtering; rainfall; temporal beta diversity; water balance

## Introduction

Environmental variation can reorganize ecological communities on timescales far shorter than changes in regional species pools or local occupancy. Short pulses of rain, temperature, food or disturbance may temporarily alter which species are active, visible or reproductively engaged. Yet community responses to such pulses are often summarized as changes in total activity, richness or co-occurrence, leaving unresolved whether the same assemblage simply becomes more active or whether the composition of the active community itself changes.

Frogs are an especially useful system for separating these alternatives because rainfall is a major cue for acoustic and reproductive activity. Numerous studies have shown that rainfall covaries with calling intensity, calling-species richness and chorus onset (Hsu, Kam, & Fellers, 2006; Xie et al., 2017; Brodie, Allen-Ankins, & Schwarzkopf, 2025). Consequently, demonstrating that “frogs call after rain” is neither surprising nor sufficient as a community-ecology result. The less resolved question is whether rainfall acts uniformly across species or functions as a short-term ecological filter that changes which species participate in the acoustically active assemblage.

These alternatives make different predictions. Under **uniform activation**, wetter conditions should increase community activity while preserving relative species membership: a wet assemblage should largely resemble a more active version of the dry assemblage. Under **nested recruitment**, wetter conditions should retain a dry-weather core while adding additional species. Under **species-selective reassembly**, however, wet conditions should simultaneously increase active richness and alter species membership, producing species-specific gains and losses rather than simple nested expansion.

A species-selective response is plausible because anurans differ substantially in hydric physiology and life history. Water balance is a central constraint on amphibian activity, and smaller anurans generally experience higher mass-specific evaporative water loss because of their greater surface-area-to-volume ratios. Comparative studies have linked anuran body size to water economy, climatic water deficit and precipitation, with larger body size potentially conferring greater resistance to dehydration (Amado, Bidau, & Olalla-Tárraga, 2019). A short rainfall pulse could therefore release hydric constraints disproportionately for smaller-bodied species, creating transient trait filtering in the active community.

We tested these ideas using standardized North American Amphibian Monitoring Program (NAAMP) surveys. Rather than comparing different sites, we matched surveys from the **same route and the same seasonal survey window** across adjacent observed years and oriented each pair by rainfall recency. We first asked whether greater wet–dry rainfall contrast predicted higher active-species richness. We then partitioned compositional change into turnover and nestedness and tested whether species differed systematically in wet recruitment. Finally, after opening species-specific responses, we used an independently compiled amphibian trait database to test a finite set of ecological traits, with body size emerging as the principal secondary correlate. We also use previously completed community-activity decomposition analyses as supporting evidence to distinguish community reassembly from stronger pairwise co-calling within already-active sampling units.

Our ecological hypothesis is that rainfall functions as a **short-term community filter**: wetter conditions should increase the richness of the active assemblage, but the added richness should arise through species-selective reassembly rather than a uniform rise in activity across an unchanged species set.

## Materials and Methods

### NAAMP surveys and active-community definition

We used the U.S. Geological Survey North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). Analyses were restricted to the unified-protocol period 2001–2015. NAAMP routes contain approximately 10 standardized wetland-associated stops surveyed acoustically for 5 min. CallingIndex values 1–3 were treated as positive acoustic activity.

For the ecological community analyses, an **active species** was a species with a positive calling index at at least one sampled stop in a route-run. Active-community richness was the number of distinct positively calling species across a complete 10-stop run. This quantity represents acoustic participation during the survey, not occupancy, abundance or successful reproduction.

We retained runs with exactly 10 non-skipped sampled stops, at least eight valid stop temperatures, a mean converted temperature between -10 and 45 °C, a parseable survey date, and a numeric DaysSinceRain value within the publisher-documented 0–180 day range. The resulting ecological-extension dataset contained 7,848 eligible runs.

### Matched wet–dry route pairs

To compare communities under different rainfall conditions while holding geography and seasonal survey structure constant, we stratified runs by **State × RouteNumber × RunNumber**. Within each stratum, eligible runs were ordered by survey year and paired between adjacent observed years. A run could therefore contribute to at most two adjacent-year comparisons.

For pairs with unequal DaysSinceRain, the member with the lower DaysSinceRain was defined as the wetter run and the other as the drier run. Equal-rain pairs were excluded. The primary dataset contained 4,236 matched wet–dry pairs from 585 routes in 21 states. The median year gap was one year; 63.6% of pairs were exact consecutive years. We therefore repeated all principal community metrics in the 2,693 exact consecutive-year pairs.

Rain contrast was

[
Delta R = log(1 + D_{dry}) - log(1 + D_{wet}),
]

which is positive by construction and increases as the two paired runs differ more strongly in rainfall recency. Models also included the wet-minus-dry difference in mean temperature, day of year, and the year gap.

### Richness response

For each pair, richness gain was

[
Delta S = S_{wet} - S_{dry}.
]

We fitted (Delta S) against rain contrast, temperature difference, day-of-year difference and year gap, with State and RunNumber fixed effects. Standard errors were cluster-robust by State × RouteNumber. The prespecified ecological prediction was that greater rainfall contrast would produce positive richness gain.

### Turnover and nestedness

For each matched pair, species were partitioned into those shared between runs ((a)), present only in the wetter run ((b)), and present only in the drier run ((c)). Sørensen dissimilarity was

[
eta_{sor} = rac{b+c}{2a+b+c}.
]

The Simpson turnover component was

[
eta_{sim} = rac{min(b,c)}{a+min(b,c)},
]

and the nestedness-resultant component was (eta_{sne} = eta_{sor} - eta_{sim}).

We modelled turnover and nestedness against the same rain contrast and pair-level covariates used for richness gain. A simple nested-recruitment hypothesis predicted increasing nestedness with rain contrast and little change in turnover.

### Species-specific wet recruitment

After the community-level extension was specified, we froze a separate species-response analysis before species-specific effects were opened. For each species and matched pair in which that species occurred in exactly one member, we scored a **wet gain** if it occurred only in the wetter run and a **dry loss** if it occurred only in the drier run.

Species were eligible if they contributed at least 40 discordant pairs across at least 10 routes. Twenty-nine species passed this outcome-independent structural gate. Initial wet-gain versus dry-loss asymmetry was assessed with exact binomial tests and Benjamini–Hochberg FDR.

Because wet–dry pairs also differed in temperature, survey date, rain-contrast magnitude and year gap, we subsequently froze a robustness analysis before opening adjusted species effects. For each species, we fitted a binomial-logit model to its discordant events:

[
P(wet gain) sim Delta R + Delta Temp + Delta DOY + YearGap,
]

with all continuous covariates centered within species and cluster-robust standard errors by route. The intercept therefore estimates each species' adjusted wet-versus-dry tendency at its mean pair conditions. Residual heterogeneity among species intercepts was tested using inverse-variance Cochran's Q, and raw-versus-adjusted rank concordance was assessed with Spearman correlation.

### Trait analysis

Species-specific responses suggested that rainfall filtering was not uniform. We therefore froze a finite trait screen before opening external trait values. Species traits came from AmphiBIO v1, an independently compiled global amphibian trait database (Oliveira et al., 2017). Twenty-six of the 29 response-eligible NAAMP species matched unambiguously to body-size data.

The original climatic-seasonality trait hypothesis was not estimable because of missing values. Among the finite secondary trait family, body size was the only estimable variable showing a strong association with wet recruitment. We therefore treated body size as a **secondary ecological mechanism**, not as an original confirmatory hypothesis.

For each matched species, we modelled wet-recruitment log odds against log-transformed AmphiBIO body size using inverse-variance weighted least squares and HC3 covariance. We then repeated the analysis using pair-covariate-adjusted species wet-versus-dry intercepts. Spearman rank correlation and leave-one-family-out analyses were used as sensitivities. A family-stratified permutation analysis was separately specified to test whether the body-size gradient persisted within taxonomic families.

The body-size analysis is interpreted as a proxy for hydric and life-history differences. It does not directly measure evaporative water loss, dehydration tolerance or breeding-water hydroperiod.

### Supporting activity decomposition

Previously completed NAAMP analyses provide mechanistic context but are not the ecological endpoint of the present paper. Recent rain increased the probability that a standardized stop contained any caller and increased run-level active species richness. In contrast, rain did not detectably increase multispecies calling conditional on an already-active stop, co-calling above a plug-in marginal-independence expectation, a fixed-marginal shuffle residual, mean pairwise excess covariance, or pairwise network density.

These analyses support the interpretation that rainfall alters **participation in the active assemblage** more strongly than it alters pairwise co-calling structure within active sampling units.

### Inference boundaries

All analyses are observational. “Wet recruitment” refers to acoustic presence in the wetter member of a matched pair, not colonization. “Dry loss” does not imply local extinction. Changes in active-community composition may reflect calling phenology, reproductive engagement, local movement or detectability in addition to physiological constraint. We therefore interpret the results as rainfall-associated reassembly of the **acoustically active** community, not changes in underlying occupancy.

## Results

### Wetter matched runs contain richer active communities

The primary matched dataset comprised 4,236 wet–dry comparisons from 585 routes across 21 states. Wetter runs contained an average of 3.752 acoustically active species, compared with 3.650 in their drier counterparts, for a mean wet-minus-dry richness difference of 0.102 species.

Richness gain increased strongly with rainfall contrast after adjustment for paired temperature difference, survey-date difference, year gap, State and seasonal RunNumber (β = 0.2859 species per unit log-rain contrast, 95% CI 0.1646–0.4072, P = 3.81 × 10^-6).

The pattern persisted when restricted to exact consecutive-year pairs (2,693 pairs): β = 0.3009 (95% CI 0.1447–0.4572, P = 1.60 × 10^-4).

### Rainfall-associated richness gain includes compositional replacement

The wetter assemblage was not simply a nested extension of the drier assemblage. Across all pairs, the average Sørensen dissimilarity was 0.295, with mean turnover 0.130 and mean nestedness-resultant dissimilarity 0.165. Wetter runs retained a median 75% of species found in the drier run.

Rain contrast did not predict stronger nestedness in the primary matched analysis (β = 0.00650, 95% CI -0.00526–0.01827, P = 0.279) or in exact consecutive-year pairs (P = 0.711).

The primary turnover coefficient was positive but imprecise (β = 0.01264, P = 0.104). In exact consecutive-year pairs, however, turnover increased with rainfall contrast (β = 0.01840, 95% CI 0.00470–0.03211, P = 0.00850). Thus the rainfall-associated richness gain was not attributable to simple species addition around an unchanged dry-weather core.

### Species differ sharply in wet-versus-dry recruitment

Across 29 eligible species, raw wet-gain versus dry-loss responses were strongly heterogeneous (χ² = 165.45, df = 28, P = 1.91 × 10^-21). Nine species were significantly biased toward wetter runs and three toward drier runs at FDR 5%.

This heterogeneity persisted after species-specific adjustment for rain-contrast magnitude, temperature difference, survey-date difference and year gap. All 29 species remained estimable, and adjusted responses were still highly heterogeneous (Q = 144.01, df = 28, P = 1.46 × 10^-17). Species rankings were almost unchanged by adjustment (raw versus adjusted Spearman ρ = 0.997, P = 1.24 × 10^-31).

At FDR 5%, adjusted wet-associated taxa included *Gastrophryne carolinensis*, *Hyla squirella*, *Hyla chrysoscelis*, *Pseudacris crucifer* and *Pseudacris maculata*. Adjusted dry-associated taxa included *Hyla cinerea*, *Lithobates catesbeianus* and *Lithobates palustris*.

The strongest adjusted wet association was *G. carolinensis*, with an estimated wet probability of 0.774 among discordant matched pairs. By contrast, *H. cinerea*, *L. catesbeianus* and *L. palustris* each had adjusted wet probabilities below 0.43.

### Smaller-bodied species are more strongly associated with wet recruitment

A secondary AmphiBIO trait analysis matched 26 of the 29 species. In the raw species-response analysis, wet-recruitment log odds declined strongly with log body size (β = -0.3353, 95% CI -0.4662 to -0.2044, P = 5.17 × 10^-7).

The relationship strengthened slightly when species responses were first adjusted for matched-pair covariates (β = -0.3670, 95% CI -0.5153 to -0.2187, P = 1.23 × 10^-6). The unweighted rank relationship was also negative (Spearman ρ = -0.517, P = 0.00687).

Leave-one-family-out slopes were negative wherever the reduced dataset remained estimable, including analyses excluding Bufonidae and Ranidae. A conventional family-fixed-effect HC3 model was numerically unstable because of the small number and imbalance of species among families; the separately frozen family-stratified permutation test provides a more appropriate robustness check.

### Community activity changes more than residual co-calling structure

Supporting decomposition analyses showed that recent rain increased the probability that sampled stops contained any caller and expanded the run-level active species pool. By contrast, the analogous rain effect on multispecies calling conditional on acoustic activity was near zero (OR = 0.988, 95% CI 0.959–1.017), and multiple residual co-calling metrics were null.

These findings place the compositional result at the level of **active-community membership and participation**, rather than stronger residual pairwise association among species already active at the same stop.

## Discussion

Rainfall was associated with more than a simple increase in frog calling. Within the same standardized routes and the same seasonal survey windows, wetter conditions were associated with higher active-species richness, and the magnitude of richness gain increased with the contrast in rainfall recency. Yet the wetter assemblage was not merely the drier assemblage plus additional species: turnover increased in the strict consecutive-year comparison, and species differed dramatically in whether they appeared preferentially on the wet or dry side of matched pairs.

These results support a view of rainfall as a **short-term ecological filter on active-community composition**. The relevant ecological response is not only the amount of activity but the identity of species participating in the active assemblage. Such filtering can generate rapid community reassembly without requiring colonization, extinction or any change in the regional species pool. It is therefore distinct from the slower spatial processes usually emphasized in community assembly.

The species-level result is particularly important because it rejects a simple uniform-activation interpretation. If rainfall merely raised calling probability similarly across species, wet-versus-dry asymmetry should have been comparatively homogeneous. Instead, species responses remained extremely heterogeneous even after adjustment for temperature, survey timing, rain-contrast magnitude and year gap. Several species were consistently associated with wetter runs, whereas others were preferentially retained on the drier side.

Body size provides a plausible ecological axis for this filtering. Smaller-bodied species showed substantially more positive wet-recruitment responses, both before and after pair-level adjustment. This pattern is consistent with the hydric biology of amphibians. Smaller anurans have larger surface-area-to-volume ratios and can experience greater mass-specific evaporative water loss, whereas larger body size can reduce relative dehydration risk. Comparative work across anurans has linked body size to water balance and water availability (Amado et al., 2019). Under this interpretation, rainfall transiently relaxes hydric constraints more strongly for smaller species, allowing them to enter the acoustically active assemblage disproportionately after wet conditions.

This mechanism remains a hypothesis rather than a direct physiological demonstration. Body size covaries with many ecological traits, including life history, habitat use and breeding strategy, and our current trait analysis does not directly measure dehydration tolerance or pond hydroperiod. Nevertheless, the size gradient is difficult to dismiss as a simple artefact of the matched-pair design: it remains strong when species wet–dry responses are adjusted for temperature, survey date and temporal separation, and species-response rankings are almost unchanged by adjustment.

The turnover result further argues against a simple “wet weather activates everyone” model. If wet communities were merely nested supersets of dry communities, increasing rainfall contrast should have increased nestedness. It did not. Instead, exact consecutive-year comparisons showed increasing turnover. The biological picture is therefore one of simultaneous richness gain and compositional replacement: rainfall appears to open an activity window for some species while others contribute less consistently to the wetter assemblage.

This interpretation also clarifies earlier co-calling results. Rain increased the number of active stops and the run-level active species pool, but did not detectably strengthen pairwise or residual co-calling within already-active stops. The ecological signal therefore lies primarily in **which species and sampling units enter the active community**, rather than in stronger association among species once activity has begun.

Several limitations define the scope of inference. First, acoustic presence is not occupancy. Species that are absent from a run may still occur locally but remain silent. The response is therefore active-community composition, not the full ecological community. Second, rainfall was not experimentally manipulated; unmeasured conditions correlated with rainfall may contribute to the patterns. Third, body size is an explanatory correlate rather than a measured physiological mechanism. A stronger test would combine species-specific recruitment responses with direct traits of evaporative water loss, dehydration tolerance, breeding hydroperiod or reproductive mode. Fourth, the ecological-extension and trait analyses were developed after the original rainfall endpoint had been opened; each extension was separately frozen before its own effect readback, but they should not be represented as original preregistered hypotheses.

Despite these boundaries, the ecological result differs fundamentally from the familiar observation that frogs call after rain. **Rainfall-associated activity is species-selective and compositionally structured.** Wetter conditions increase the richness of the active frog assemblage, but they also alter which species are represented, and smaller-bodied species are disproportionately associated with the wet side of this reassembly.

More generally, short environmental pulses can act as transient community filters. Community assembly is often framed in terms of persistent habitat differences or long-term environmental gradients, but behavioural communities may be repeatedly reassembled on much shorter timescales. In frogs, rainfall may temporarily redraw the realized active community by releasing hydric constraints unequally among species.

## Data Availability

NAAMP source data are publicly available from the U.S. Geological Survey data release (Foreman et al., 2017; DOI 10.5066/F7G44NG0). Trait analyses use AmphiBIO v1 (Oliveira et al., 2017), distributed under CC BY 4.0. The standalone analysis repository preserves versioned contracts, source digests, result receipts and analysis scripts. Raw third-party source datasets are not redistributed. A persistent archive will be created at manuscript finalization.

## References

Amado, T. F., Bidau, C. J., & Olalla-Tárraga, M. Á. (2019). Geographic variation of body size in New World anurans: energy and water in a balance. *Ecography*, 42, 456–466. https://doi.org/10.1111/ecog.03889

Brodie, S., Allen-Ankins, S., & Schwarzkopf, L. (2025). Environmental influences on chorusing patterns in an Australian tropical savanna frog community. *Ecosphere*, 16, e70153. https://doi.org/10.1002/ecs2.70153

Foreman, T., Grant, E. H., & Weir, L. A. (2017). *North American Amphibian Monitoring Program (NAAMP) anuran detection data from the eastern and central United States (1994–2015)* [Data release]. U.S. Geological Survey. https://doi.org/10.5066/F7G44NG0

Hsu, M.-Y., Kam, Y.-C., & Fellers, G. M. (2006). Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology*, 269, 331–339. https://doi.org/10.1111/j.1469-7998.2006.00044.x

Oliveira, B. F., São-Pedro, V. A., Santos-Barrera, G., Penone, C., & Costa, G. C. (2017). AmphiBIO, a global database for amphibian ecological traits. *Scientific Data*, 4, 170123. https://doi.org/10.1038/sdata.2017.123

Xie, G. Y., et al. (2017). [Rainfall and frog community acoustic activity study; full citation retained from prior manuscript bibliography.]

## Figure concepts

**Figure 1. Matched-route design and rainfall-associated richness gain.** Same-route, same-seasonal-window wet–dry pairs, with richness gain plotted against log rainfall contrast and the exact consecutive-year sensitivity.

**Figure 2. Species-selective community reassembly.** Adjusted species wet-versus-dry probabilities or log odds with 95% CIs, highlighting FDR-supported wet-associated and dry-associated taxa.

**Figure 3. Body-size gradient in rainfall filtering.** Adjusted species wet-recruitment response against log body size, with families indicated and family-stratified robustness summarized.

**Figure 4. Ecological synthesis.** Rainfall pulse → broader active-stop coverage → higher active-community richness + species-selective replacement; residual pairwise co-calling remains comparatively stable.
