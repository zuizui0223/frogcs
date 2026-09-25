# Species-specific rainfall sensitivity predicts short-term reassembly of active frog communities

## Abstract

1. **Rainfall effects on frog calling are familiar, but community reassembly after rain should be predictable only if species differ consistently in their sensitivity to the pulse.** We tested whether species-specific rainfall responses persist across years strongly enough to forecast later changes in the acoustically active community.

2. **We used 15 years of standardized North American Amphibian Monitoring Program surveys.** We first compared 4,236 wetter–drier pairs from the same route and seasonal sampling window to quantify richness gain, turnover and species-specific reassembly. We then separated the time series: 2001–2007 estimated each species’ within-route sensitivity to rain recency, whereas 2008–2015 independently estimated wet-versus-dry recruitment.

3. **Wetter matched runs contained richer active communities and the gain included compositional replacement.** Richness gain increased with rainfall contrast (β = 0.286 species per unit log-rain contrast, 95% CI 0.165–0.407, P = 3.81 × 10^-6), while exact consecutive-year turnover increased with rainfall contrast (β = 0.0184, P = 0.00850). Species wet-versus-dry responses were strongly heterogeneous after environmental adjustment (Q = 144.0, df = 28, P = 1.46 × 10^-17).

4. **Species-specific rain sensitivity measured years earlier predicted later reassembly.** Among 27 species estimable in both periods, a 1-SD increase in 2001–2007 rain-pulse sensitivity predicted a 0.284 increase in 2008–2015 wet-recruitment log odds (95% CI 0.141–0.428, P = 1.05 × 10^-4; Spearman ρ = 0.458, P = 0.016). The relationship remained positive when rain sensitivities were permuted only within taxonomic families (positive-tail P = 0.0156).

5. **Short rainfall pulses therefore reorganize the behaviourally realized frog community in a predictable, species-specific manner.** The reassembly is not simply a uniform rise in activity: species differ persistently in their response to recent rain, and those differences forecast which taxa later enter wetter active assemblages.

## Keywords

active community; anurans; community assembly; environmental pulse; rainfall; response heterogeneity; species reassembly; temporal beta diversity

## Introduction

Environmental pulses can reorganize ecological communities on timescales far shorter than changes in regional species pools or local occupancy. Rain, temperature, food pulses and disturbance may temporarily alter which species are active or reproductively engaged. Yet short-term community responses are often summarized only as changes in total activity or richness, leaving two ecological questions unresolved: whether the same assemblage simply becomes more active, and whether any species differences in pulse response are persistent enough to make community reassembly predictable.

Frogs provide a strong test case because rainfall effects on calling are already well established. Rainfall has been linked to calling activity, calling-species richness and chorus onset (Hsu, Kam, & Fellers, 2006; Xie et al., 2017; Brodie, Allen-Ankins, & Schwarzkopf, 2025). Demonstrating that frogs call more after rain is therefore neither surprising nor sufficient as a community-ecology result. The more informative question is whether rainfall acts uniformly across species or whether species occupy different **rain-response strategies** that repeatedly determine which taxa enter the acoustically active assemblage.

Three community responses are distinguishable. Under **uniform activation**, wetter conditions increase activity while preserving relative community membership. Under **nested recruitment**, wetter conditions retain a dry-weather core and add species. Under **species-selective reassembly**, wetter conditions change membership because taxa differ in their response to the environmental pulse. A further prediction follows from the third model: if species differences represent persistent ecological response strategies rather than year-specific noise, sensitivity to recent rain estimated in one period should predict wet-versus-dry recruitment in a later, non-overlapping period.

We tested these ideas using standardized North American Amphibian Monitoring Program (NAAMP) surveys. First, we matched surveys from the same route and seasonal sampling window across adjacent observed years, asking whether rainfall contrast predicted active-species richness, turnover versus nestedness, and species-specific wet-versus-dry responses. Second, we performed a temporally disjoint test of mechanism. Using 2001–2007 only, we estimated each species’ within-route change in acoustic presence with increasing time since rain while controlling temperature, season and year. Using 2008–2015 only, we independently estimated each species’ tendency to occur on the wetter side of matched community transitions. We then asked whether the early-period rain-sensitivity ranking predicted later reassembly.

Our central prediction was therefore stronger than “rainfall matters.” If short rainfall pulses reorganize active communities through persistent species-specific responses, then (1) wetter surveys should contain richer and compositionally different assemblages, (2) species should differ strongly in wet-versus-dry recruitment, and (3) species that were most rain-sensitive in 2001–2007 should be preferentially recruited to wetter assemblages in 2008–2015.

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

### Temporally disjoint species rainfall sensitivity

To test whether species-specific rainfall responses were persistent rather than an artefact of the same matched pairs used to identify reassembly, we separated the 15-year series into non-overlapping training and validation periods.

The **training period** comprised eligible runs from 2001–2007. For each of the existing 29 coverage-qualified species, we defined an opportunity set as routes on which that species was detected at least once during the training period; no validation-period data were used to define these routes. Species entered the training model when they had at least eight opportunity routes, 40 eligible runs, 10 positive runs and 10 negative runs. Across all eligible training runs, log(1 + DaysSinceRain), mean temperature and survey year were standardized once and the same scaling was used for every species.

For each species we fitted a linear-probability model of run-level acoustic presence against standardized rain recency, temperature, a five-degree-of-freedom spline of day of year, RunNumber and year, with route fixed effects and route-clustered standard errors. Route fixed effects were implemented by within-route demeaning of the response and model matrix. We defined

`rain-pulse sensitivity = -β_dryness`,

so larger positive values indicate a stronger decline in acoustic activity as time since rain increases. Species were retained regardless of the individual significance of this coefficient.

The **validation period** comprised 2008–2015 only. We rebuilt the same State × RouteNumber × RunNumber adjacent-year wet–dry pairs within this period. For each fixed-family species with at least 20 discordant events across at least five routes, we fitted a binomial-logit model of wet-only versus dry-only occurrence against within-species centred rain contrast, temperature difference, day-of-year difference and year gap, with route-clustered standard errors. The intercept estimates that species’ adjusted wet-versus-dry log odds during the validation period.

The primary cross-species test included species estimable in both periods. Early rain-pulse sensitivity was standardized across these species, and validation-period wet-recruitment log odds were regressed on this predictor using inverse-variance weighted least squares with HC3 covariance. We also calculated an unweighted Spearman correlation. As a robustness test for broad taxonomic structure, we permuted early rain-pulse sensitivities among species **within families** 100,000 times while holding validation responses and inverse-variance weights fixed. This temporally disjoint analysis was the final prespecified mechanism slot in the post-opening mechanism programme; no additional mechanism family was opened after its result.

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

### Early-period rain sensitivity predicts later species recruitment

The temporal split produced 2,888 eligible training-period runs (2001–2007) and 4,960 validation-period runs (2008–2015), from which 2,459 late-period matched wet–dry pairs were constructed. Twenty-seven of the fixed 29 species met coverage requirements in the training period, all 29 were estimable in the validation period, and 27 therefore entered the cross-period prediction.

Species that were more strongly associated with recent rain in 2001–2007 were more strongly recruited to wetter assemblages in 2008–2015. A 1-SD increase in early-period rain-pulse sensitivity predicted a **0.284** increase in later adjusted wet-recruitment log odds (95% CI 0.141–0.428, P = 1.05 × 10^-4). The unweighted species ranking showed the same pattern (Spearman ρ = 0.458, P = 0.0162).

The relationship was not explained solely by differences among major taxonomic families. Among 24 species with unambiguous family assignments, the weighted within-family slope was 0.193. Permuting early rain sensitivities only among species within the same family yielded a positive-tail P = 0.0156 (two-sided P = 0.0344; 100,000 permutations).

Several species illustrate the temporal persistence of the response. *Gastrophryne carolinensis*, *Hyla femoralis* and *H. squirella* showed strong positive rain-pulse sensitivity during 2001–2007 and subsequently strong wet-side recruitment in 2008–2015. Conversely, *Lithobates catesbeianus* and *L. palustris* showed weak or negative early rain-pulse sensitivity and later dry-side recruitment. Individual exceptions occurred, as expected, but the cross-species relationship was positive across the temporally independent periods.

### A pooled body-size correlation does not survive family-stratified testing

The secondary AmphiBIO screen matched 26 of the 29 species. Across species, wet-recruitment log odds declined strongly with log body size in both the raw response analysis (β = -0.3353, 95% CI -0.4662 to -0.2044, P = 5.17 × 10^-7) and the pair-covariate-adjusted response analysis (β = -0.3670, 95% CI -0.5153 to -0.2187, P = 1.23 × 10^-6). The unweighted rank association was also negative (Spearman ρ = -0.517, P = 0.00687).

However, the family-stratified permutation did not support a general within-family body-size gradient. The observed weighted within-family slope was -0.1889, compared with a permutation distribution centred near zero (two-sided P = 0.314; negative-tail P = 0.151). Descriptive family-specific slopes were -0.447 for Hylidae (14 species) and -0.063 for Ranidae (7 species), while the remaining families contained too few species for informative within-family slopes.

We therefore treat body size as a **secondary cross-species correlate that is partly confounded with taxonomic structure**, not as the mechanism responsible for rainfall-associated reassembly.

### Community activity changes more than residual co-calling structure

Supporting decomposition analyses showed that recent rain increased the probability that sampled stops contained any caller and expanded the run-level active species pool. By contrast, the analogous rain effect on multispecies calling conditional on acoustic activity was near zero (OR = 0.988, 95% CI 0.959–1.017), and multiple residual co-calling metrics were null.

These findings place the compositional result at the level of **active-community membership and participation**, rather than stronger residual pairwise association among species already active at the same stop.

## Discussion

Rainfall did more than increase the amount of frog calling. Within the same standardized routes and seasonal survey windows, wetter conditions contained more acoustically active species, the richer wet assemblage included compositional replacement, and species differed sharply in whether they occurred on the wet or dry side of matched community transitions. Most importantly, those species differences were **predictable across time**: rain sensitivity measured during 2001–2007 forecast wet-versus-dry recruitment during an independent 2008–2015 period.

This temporal prediction changes the ecological interpretation of the reassembly result. Species-selective turnover is not merely an idiosyncratic consequence of particular wet and dry years. Instead, species appear to differ in a persistent **rain-response strategy**. A one-standard-deviation increase in early-period rain-pulse sensitivity predicted a 0.284 increase in later wet-recruitment log odds, and the association remained positive when sensitivities were shuffled only within taxonomic families. Short environmental pulses can therefore reorganize a behaviourally realized community through repeatable differences in how constituent species respond to the same environmental cue.

The matched-community analyses show how that response is expressed at the assemblage level. Rainfall contrast increased active-species richness, but the wet assemblage was not simply the dry assemblage plus extra taxa. Nestedness did not increase, whereas exact consecutive-year comparisons showed increasing turnover. Adjusted wet-versus-dry responses were extremely heterogeneous among species, and more than half of the heterogeneity among family-matched taxa remained within families. Together with the temporally disjoint prediction, this indicates that community reassembly is structured at a finer level than broad clade membership.

The result is more specific than the familiar observation that frogs call after rain. Calling activity can rise uniformly without changing community composition. Here, however, species differed in both their early-period rain-recency responses and their later membership in wet versus dry assemblages, and those two quantities were linked across non-overlapping years. The community consequence of rainfall therefore depends on **who is sensitive to the pulse**, not only on whether total activity increases.

The time-split analysis provides a mechanistic explanation at the behavioural level, but it does not identify the physiological or life-history traits that generate rain sensitivity. A finite post-opening trait programme tested several obvious candidates. Pooled body size correlated strongly with wet response, but the relationship did not survive a family-stratified permutation. Coarse ATraiU hydroperiod flags contained no useful variation among matched species, breeding-season breadth was unrelated to wet response, and route-local core–satellite prevalence did not distinguish wet gains from dry losses. These negative results are informative: the persistent rain-response axis is real, but it is not captured by these coarse ecological proxies. Direct measurements of evaporative water loss, dehydration tolerance, breeding hydroperiod, reproductive mode or microhabitat may be required to identify its physiological basis.

Previously completed activity-decomposition analyses provide additional context. Recent rain increased the number of standardized stops containing callers and expanded run-level active richness, whereas multispecies calling conditional on an already-active stop and several residual co-calling metrics changed little. The matched-community and temporal-split results therefore place the main response at the level of **which species enter the active assemblage**, rather than stronger residual association among species already calling at the same stop.

Several limitations define the scope of inference. Acoustic presence is not occupancy: a species absent from a run may remain locally present but silent. “Wet recruitment” therefore means acoustic participation in the wetter survey, not colonization, and “dry loss” does not mean extinction. Rainfall was not experimentally manipulated, so time-varying covariates may contribute despite matched routes, seasonal-window controls and temperature/date adjustment. The training–validation split prevents the same years from defining both species rain sensitivity and later recruitment, but the fixed 29-species family was selected previously on coverage across the ecological programme. Early rain sensitivity is itself an estimated behavioural response and contains measurement error that is not modelled in the cross-species regression. Finally, the ecological extension and mechanism analyses were developed after the original rainfall endpoint had opened; each was separately frozen before its own readback and should not be represented as an original preregistered hypothesis.

Despite these boundaries, the conclusion is now mechanistically specific. **Short rainfall pulses reorganize the active frog community in a predictable species-specific manner.** Species that were more rain-sensitive during the first seven years of monitoring were more likely to appear on the wetter side of community transitions during the following eight years. Behaviourally realized communities can therefore be reorganized over short environmental contrasts by persistent differences in species response to the same pulse, long before any change in the regional species pool or local occupancy is required.

The remaining biological question is the trait basis of this persistent rain-response strategy. The present study establishes the community pattern and its temporal predictability; resolving the underlying physiological or reproductive mechanism requires traits measured at finer resolution than currently available comparative databases.

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

**Figure 2. Early species rain sensitivity predicts later community recruitment.** Species-specific rain-pulse sensitivity estimated from 2001–2007 on the x-axis and independently estimated 2008–2015 adjusted wet-recruitment log odds on the y-axis, with the inverse-variance weighted cross-species relationship and the disjoint time periods shown explicitly.

**Figure 3. Rainfall-associated richness gain includes compositional replacement.** Rain-contrast effects on nestedness and Simpson turnover for the primary matched pairs and exact consecutive-year sensitivity, accompanied by the magnitude of species-response heterogeneity.

The full species wet/dry forest plot, body-size analyses and earlier co-calling decomposition are treated as supplementary supporting analyses.

