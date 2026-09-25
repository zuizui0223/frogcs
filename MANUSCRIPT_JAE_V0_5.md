# Rainfall-associated richness gains accompany species-selective reassembly of active frog communities

## Abstract

1. **Rainfall effects on frog calling are familiar, but whether short rainfall pulses merely amplify the same assemblage or reorganize which species are active is much less clear.** We tested whether rainfall changes the composition of the acoustically active community, not simply its total activity.

2. **We used 15 years of standardized North American Amphibian Monitoring Program surveys and compared 4,236 wetter–drier pairs from the same route and the same seasonal sampling window across adjacent observed years** (585 routes, 21 states). We quantified active-species richness, turnover versus nestedness, and species-specific wet-versus-dry responses.

3. **Greater rainfall contrast predicted higher active-community richness.** Wet-minus-dry richness increased by 0.286 species per unit log-rain contrast (95% CI 0.165–0.407, P = 3.81 × 10^-6), with a similar effect in exact consecutive-year pairs (β = 0.301, P = 1.60 × 10^-4).

4. **The richer wet assemblage was not a simple nested extension of the dry assemblage.** Nestedness did not increase with rainfall contrast, whereas turnover increased in the consecutive-year sensitivity (β = 0.0184, 95% CI 0.00470–0.0321, P = 0.00850). Species wet-versus-dry responses were strongly heterogeneous after environmental adjustment (Q = 144.0, df = 28, P = 1.46 × 10^-17), and 52.1% of heterogeneity among family-matched species remained within families (P = 8.28 × 10^-8).

5. **Rainfall was therefore associated with transient, species-selective reassembly of the acoustically active frog community rather than a uniform increase in activity by an unchanged assemblage.** A secondary body-size correlation was strong across species but did not survive family-stratified permutation, indicating that the species selectivity is biologically structured but its trait mechanism remains unresolved.

## Keywords

active community; anurans; community assembly; environmental pulse; rainfall; species reassembly; temporal beta diversity; turnover

## Introduction

Environmental variation can reorganize ecological communities on timescales far shorter than changes in regional species pools or local occupancy. Short pulses of rain, temperature, food or disturbance may temporarily alter which species are active or reproductively engaged. Yet pulse responses are often summarized only as changes in total activity or richness, leaving unresolved whether the same assemblage simply becomes more active or whether the identity of active species changes.

Frogs provide a strong test case because rainfall effects on calling are already well established. Rainfall has been linked to calling activity, calling-species richness and chorus onset (Hsu, Kam, & Fellers, 2006; Xie et al., 2017; Brodie, Allen-Ankins, & Schwarzkopf, 2025). Demonstrating that frogs call more after rain is therefore neither surprising nor sufficient as a community-ecology result. The ecological question is instead whether rainfall acts uniformly across species or rapidly reorganizes the composition of the active assemblage.

Three alternatives are distinguishable. Under **uniform activation**, wetter conditions increase activity while preserving relative community membership. Under **nested recruitment**, wetter conditions retain a dry-weather core and add species, so temporal beta diversity is increasingly nested. Under **species-selective reassembly**, wetter conditions increase active richness while simultaneously changing membership, producing turnover and contrasting species-specific responses. This distinction is relevant because temporal frog assemblages can sometimes vary mainly through nestedness rather than turnover; for example, a three-year Brazilian frog-community study reported relatively stable composition and temporal beta diversity dominated by nestedness (Severgnini et al., 2024). A rainfall-associated increase in turnover within the same sites and seasonal windows would therefore represent a different mode of short-term community change.

We tested these alternatives using standardized North American Amphibian Monitoring Program (NAAMP) surveys. Rather than comparing different locations, we matched surveys from the **same route and the same seasonal sampling window** across adjacent observed years and oriented each pair by rainfall recency. We first asked whether greater wet–dry rainfall contrast predicted higher active-species richness. We then partitioned compositional dissimilarity into turnover and nestedness, and tested whether species differed systematically in their wet-versus-dry responses. We finally explored a finite external trait family after species effects had been opened; body size emerged as a strong pooled correlate, but a family-stratified permutation test was used to determine whether that relationship represented a within-family gradient or broader clade structure.

Our ecological prediction was that if rainfall merely amplifies a stable assemblage, wet–dry richness differences should not be accompanied by systematic species replacement. Conversely, if rainfall produces **species-selective short-term reassembly**, greater rainfall contrast should increase active richness while species membership changes non-uniformly across taxa.

## Materials and Methods

### NAAMP surveys and active-community definition

We used the U.S. Geological Survey North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). Analyses were restricted to the unified-protocol period 2001–2015. NAAMP routes contain approximately 10 standardized wetland-associated stops surveyed acoustically for 5 min. CallingIndex values 1–3 were treated as positive acoustic activity.

For the ecological community analyses, an **active species** was a species with a positive calling index at at least one sampled stop in a route-run. Active-community richness was the number of distinct positively calling species across a complete 10-stop run. This quantity represents acoustic participation during the survey, not occupancy, abundance or successful reproduction.

We retained runs with exactly 10 non-skipped sampled stops, at least eight valid stop temperatures, a mean converted temperature between -10 and 45 °C, a parseable survey date, and a numeric DaysSinceRain value within the publisher-documented 0–180 day range. The resulting ecological-extension dataset contained 7,848 eligible runs.

### Matched wet–dry route pairs

To compare communities under different rainfall conditions while holding geography and seasonal survey structure constant, we stratified runs by **State × RouteNumber × RunNumber**. Within each stratum, eligible runs were ordered by survey year and paired between adjacent observed years. A run could therefore contribute to at most two adjacent-year comparisons.

For pairs with unequal DaysSinceRain, the member with the lower DaysSinceRain was defined as the wetter run and the other as the drier run. Equal-rain pairs were excluded. The primary dataset contained 4,236 matched wet–dry pairs from 585 routes in 21 states. The median year gap was one year; 63.6% of pairs were exact consecutive years. We therefore repeated all principal community metrics in the 2,693 exact consecutive-year pairs.

Rain contrast was

`ΔR = log(1 + D_dry) - log(1 + D_wet)`

which is positive by construction and increases as the two paired runs differ more strongly in rainfall recency. Models also included the wet-minus-dry difference in mean temperature, day of year, and the year gap.

### Richness response

For each pair, richness gain was

`ΔS = S_wet - S_dry`.

We fitted (Delta S) against rain contrast, temperature difference, day-of-year difference and year gap, with State and RunNumber fixed effects. Standard errors were cluster-robust by State × RouteNumber. The prespecified ecological prediction was that greater rainfall contrast would produce positive richness gain.

### Turnover and nestedness

For each matched pair, species were partitioned into those shared between runs (`a`), present only in the wetter run (`b`), and present only in the drier run (`c`). Sørensen dissimilarity was

`β_sor = (b + c) / (2a + b + c)`.

The Simpson turnover component was

`β_sim = min(b, c) / (a + min(b, c))`,

and the nestedness-resultant component was

`β_sne = β_sor - β_sim`.

We modelled wet-minus-dry richness gain, `β_sim`, and `β_sne` separately against rain contrast, paired temperature difference, day-of-year difference and year gap, with State and RunNumber fixed effects and cluster-robust standard errors by State × RouteNumber. The same metrics were recalculated in the exact consecutive-year sensitivity.

### Species-specific wet-versus-dry responses

We next asked whether rainfall-associated community change was uniform across taxa. For every matched pair and every species present in exactly one member of that pair, we scored a discordant species event as 1 when the species occurred only in the wetter run and 0 when it occurred only in the drier run. Species entered the frozen response family when they had at least 40 discordant matched pairs spanning at least 10 routes; eligibility depended only on coverage, not response direction.

The initial species-level screen compared wet gains with dry losses using a two-sided exact binomial test under `P(wet gain) = 0.5`, with Benjamini–Hochberg FDR across eligible species. To test whether species differences persisted after paired environmental and temporal differences were accounted for, we then fitted a separate binomial-logit model for each eligible species:

`wet_only ~ rain_contrast + temperature_difference + day_of_year_difference + year_gap`.

All four continuous predictors were centered within species, and standard errors were cluster-robust by State × RouteNumber. The model intercept therefore estimates each species' adjusted wet-versus-dry log odds at that species' mean pair conditions. We applied Benjamini–Hochberg FDR across adjusted species intercept tests, quantified residual heterogeneity with inverse-variance Cochran's Q, and measured raw-versus-adjusted rank concordance with Spearman correlation.

### Secondary trait analysis

Species-specific responses were highly heterogeneous, motivating a separately frozen finite trait screen using AmphiBIO v1 (Oliveira et al., 2017). This trait analysis was conducted after the community and species-response results had been opened and is therefore secondary.

Twenty-six of the 29 response-eligible NAAMP species matched unambiguously to AmphiBIO body-size data. The originally specified climatic-seasonality trait was not estimable because only one response-eligible species had complete wet/dry seasonality fields. Among the finite secondary trait family, log-transformed body size was the only estimable trait showing a strong association with wet-versus-dry response.

We first related Haldane-corrected species wet-versus-dry log odds to log body size with inverse-variance weighted least squares and HC3 covariance. We then repeated this analysis using pair-covariate-adjusted species response intercepts. Because species are not phylogenetically independent, we did not treat the pooled body-size regression as a mechanistic result. We froze an additional family-stratified permutation analysis before opening that robustness result. For each family with at least two matched species, log body sizes were permuted among species within that family 100,000 times while adjusted species responses and inverse-variance weights were held fixed. The test statistic was the weighted slope after subtracting weighted family means from body size and response.

The trait analysis therefore asks only whether an obvious cross-species ecological correlate helps describe species selectivity. It does not establish a causal physiological mechanism, and a pooled relationship that fails the within-family permutation cannot support a headline body-size filtering claim.

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

The heterogeneity was not reducible to broad family differences. Among 26 species with unambiguous AmphiBIO family assignments, 52.1% of the inverse-variance heterogeneity remained **within families** (Q_within = 73.88, df = 21, P = 8.28 × 10^-8), while between-family heterogeneity was also strong (Q_between = 67.80, df = 4, P = 6.62 × 10^-14). Hylidae alone remained highly heterogeneous (Q = 44.97, df = 13, P = 2.12 × 10^-5), as did Ranidae (Q = 23.81, df = 6, P = 5.65 × 10^-4). Taxonomic family therefore captures part, but not most, of the species-selective response structure.

At FDR 5%, adjusted wet-associated taxa included *Gastrophryne carolinensis*, *Hyla squirella*, *Hyla chrysoscelis*, *Pseudacris crucifer* and *Pseudacris maculata*. Adjusted dry-associated taxa included *Hyla cinerea*, *Lithobates catesbeianus* and *Lithobates palustris*.

The strongest adjusted wet association was *G. carolinensis*, with an estimated wet probability of 0.774 among discordant matched pairs. By contrast, *H. cinerea*, *L. catesbeianus* and *L. palustris* each had adjusted wet probabilities below 0.43.

### A pooled body-size correlation does not survive family-stratified testing

The secondary AmphiBIO screen matched 26 of the 29 species. Across species, wet-recruitment log odds declined strongly with log body size in both the raw response analysis (β = -0.3353, 95% CI -0.4662 to -0.2044, P = 5.17 × 10^-7) and the pair-covariate-adjusted response analysis (β = -0.3670, 95% CI -0.5153 to -0.2187, P = 1.23 × 10^-6). The unweighted rank association was also negative (Spearman ρ = -0.517, P = 0.00687).

However, the family-stratified permutation did not support a general within-family body-size gradient. The observed weighted within-family slope was -0.1889, compared with a permutation distribution centred near zero (two-sided P = 0.314; negative-tail P = 0.151). Descriptive family-specific slopes were -0.447 for Hylidae (14 species) and -0.063 for Ranidae (7 species), while the remaining families contained too few species for informative within-family slopes.

We therefore treat body size as a **secondary cross-species correlate that is partly confounded with taxonomic structure**, not as the mechanism responsible for rainfall-associated reassembly.

### Community activity changes more than residual co-calling structure

Supporting decomposition analyses showed that recent rain increased the probability that sampled stops contained any caller and expanded the run-level active species pool. By contrast, the analogous rain effect on multispecies calling conditional on acoustic activity was near zero (OR = 0.988, 95% CI 0.959–1.017), and multiple residual co-calling metrics were null.

These findings place the compositional result at the level of **active-community membership and participation**, rather than stronger residual pairwise association among species already active at the same stop.

## Discussion

Rainfall was associated with more than the familiar increase in frog calling. Within the same standardized routes and the same seasonal survey windows, wetter conditions contained more acoustically active species, and richness gain increased with the magnitude of the rainfall contrast. At the same time, the wetter assemblage was not simply the drier assemblage plus extra species: nestedness did not increase, turnover increased in exact consecutive-year comparisons, and species differed sharply in whether they appeared preferentially on the wet or dry side of matched pairs.

The central ecological result is therefore **species-selective short-term reassembly of the active community**. This is distinct from a uniform activity response. If rainfall merely amplified the same species set, wet-versus-dry responses should have been comparatively homogeneous. Instead, adjusted species effects remained extremely heterogeneous after accounting for temperature differences, survey timing, rain-contrast magnitude and year gap (Q = 144.0, P = 1.46 × 10^-17), while raw and adjusted species rankings were almost identical (ρ = 0.997). Importantly, more than half of the heterogeneity among family-matched species remained within families, and both Hylidae and Ranidae retained significant internal heterogeneity. The response is therefore organized more finely than a simple broad-clade contrast and reaches the level of species identity.

The turnover result further distinguishes this pattern from simple nested recruitment. A recent three-year study of a tropical frog community found relatively stable composition and temporal beta diversity dominated by nestedness, consistent with species dropping in and out around a persistent community structure (Severgnini et al., 2024). Here, rainfall contrast did not increase nestedness, and exact consecutive-year comparisons instead showed increasing turnover. The ecological picture is one of **richness gain plus compositional replacement** over short temporal contrasts.

We use the term reassembly deliberately rather than claiming classical environmental-pulse response. Environmental-filter terminology can imply that abiotic conditions prevent establishment or persistence, a stronger process than these acoustic data identify. Our results concern which locally available species enter the **acoustically active assemblage** during standardized surveys. Rainfall-associated reassembly could arise through species differences in calling phenology, reproductive engagement, local movement, physiological constraints or other behaviours; it does not require short-term colonization or extinction.

The secondary trait analysis illustrates both the promise and the current limit of mechanistic interpretation. Smaller-bodied species had more positive wet associations in pooled analyses, a pattern consistent with comparative work linking body size and amphibian water balance. However, the negative slope did not survive permutation of body size within families (P = 0.314). We therefore do not interpret body size as an established rainfall-filtering mechanism. The pooled signal may reflect a combination of body size, clade-specific life histories, habitat use and breeding strategies. Direct traits of evaporative water loss, dehydration tolerance, breeding hydroperiod or reproductive mode would be required to identify the axis responsible for the species selectivity.

Previously completed activity-decomposition analyses provide supporting context. Recent rain increased the number of standardized stops containing callers and expanded run-level active richness, whereas multispecies calling conditional on an already-active stop and several residual co-calling metrics changed little. Together with the matched-community results, this indicates that rainfall-associated community change is expressed primarily through **which sampling units and which species enter the active assemblage**, rather than stronger residual association among species already calling at the same stop.

Several limitations define the scope of inference. Acoustic presence is not occupancy: a species absent from a run may remain locally present but silent. “Wet recruitment” therefore means acoustic participation in the wetter survey, not colonization, and “dry loss” does not mean extinction. Rainfall was not experimentally manipulated, so time-varying environmental covariates may contribute to the associations despite matched routes, seasonal-window controls and temperature/date adjustment. The exact consecutive-year turnover result is a prespecified sensitivity rather than the primary turnover model, whose coefficient was positive but imprecise (P = 0.104). Finally, the ecological-extension, species-response and trait analyses were developed after the original rainfall endpoint was opened; each was separately frozen before its own effect readback, but none should be represented as an original preregistered hypothesis.

Despite these boundaries, the ecological conclusion differs substantially from “frogs call after rain.” **Rainfall-associated activity is compositionally structured.** Wetter conditions increase the richness of the active assemblage, but species do not respond uniformly and the change includes replacement rather than simple addition. Short environmental pulses can therefore reorganize the realized active community on timescales far shorter than changes in occupancy or the regional species pool.

The unresolved next mechanistic question is not whether rainfall matters, but **which ecological traits generate the contrasting wet-versus-dry species responses**. The present data establish the selective reassembly pattern; identifying its trait basis requires a better-covered independent trait dataset or direct physiological and reproductive-strategy measurements.

## Data Availability

NAAMP source data are publicly available from the U.S. Geological Survey data release (Foreman et al., 2017; DOI 10.5066/F7G44NG0). Trait analyses use AmphiBIO v1 (Oliveira et al., 2017), distributed under CC BY 4.0. The standalone analysis repository preserves versioned contracts, source digests, result receipts and analysis scripts. Raw third-party source datasets are not redistributed. A persistent archive will be created at manuscript finalization.

## References

Amado, T. F., Bidau, C. J., & Olalla-Tárraga, M. Á. (2019). Geographic variation of body size in New World anurans: energy and water in a balance. *Ecography*, 42, 456–466. https://doi.org/10.1111/ecog.03889

Brodie, S., Allen-Ankins, S., & Schwarzkopf, L. (2025). Environmental influences on chorusing patterns in an Australian tropical savanna frog community. *Ecosphere*, 16, e70153. https://doi.org/10.1002/ecs2.70153

Foreman, T., Grant, E. H., & Weir, L. A. (2017). *North American Amphibian Monitoring Program (NAAMP) anuran detection data from the eastern and central United States (1994–2015)* [Data release]. U.S. Geological Survey. https://doi.org/10.5066/F7G44NG0

Hsu, M.-Y., Kam, Y.-C., & Fellers, G. M. (2006). Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology*, 269, 331–339. https://doi.org/10.1111/j.1469-7998.2006.00044.x

Oliveira, B. F., São-Pedro, V. A., Santos-Barrera, G., Penone, C., & Costa, G. C. (2017). AmphiBIO, a global database for amphibian ecological traits. *Scientific Data*, 4, 170123. https://doi.org/10.1038/sdata.2017.123

Severgnini, M. R., de Oliveira, M. M., Valério, L. M., & Provete, D. B. (2024). Temporal dynamics of species richness and composition in a peri-urban tropical frog community in Central Brazil. *Ecology and Evolution*, 14, e70628. https://doi.org/10.1002/ece3.70628

Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017). An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators*, 82, 13–22. https://doi.org/10.1016/j.ecolind.2017.06.015

## Figure concepts

**Figure 1. Matched-route design and rainfall-associated active-richness gain.** Same-route, same-seasonal-window wet–dry pairs, with the adjusted richness-gain slope and exact consecutive-year sensitivity.

**Figure 2. Species-selective community reassembly.** Adjusted species wet-versus-dry probabilities or log odds with 95% CIs, highlighting FDR-supported wet-associated and dry-associated taxa.

**Figure 3. Turnover rather than simple nested addition.** Rain-contrast effects on nestedness and Simpson turnover for the primary matched pairs and exact consecutive-year sensitivity.

The earlier co-calling decomposition and body-size analyses are treated as supplementary supporting analyses rather than main figures.

