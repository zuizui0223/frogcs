# Recent rainfall predicts week-long richness elevation and species-selective reassembly in active frog communities

## Abstract

1. **Rainfall effects on frog calling are familiar, but the duration and community consequences of a rainfall pulse are less clear.** We asked whether recent rain merely produces an immediate increase in acoustic activity or shifts the richness and composition of the active assemblage over several days.

2. **We analysed 15 years of standardized North American Amphibian Monitoring Program surveys.** We compared 4,236 wetter–drier pairs from the same route and seasonal sampling window across adjacent observed years, and independently mapped active-community richness across five prespecified rain-recency classes within fixed route × seasonal-window strata.

3. **Active-community richness remained elevated for up to one week after reported rain.** Relative to surveys ≥8 days since rain, adjusted richness was higher on day 0 (+0.654 species, 95% CI 0.448–0.860), day 1 (+0.544), days 2–3 (+0.411), and days 4–7 (+0.381, 95% CI 0.202–0.561). In matched wet–dry pairs, richness gain also increased with rainfall contrast (β = 0.286, 95% CI 0.165–0.407).

4. **The richer wet assemblage was not a simple nested extension of the dry assemblage.** Turnover increased in exact consecutive-year pairs (β = 0.0184, P = 0.00850), species wet-versus-dry responses were strongly heterogeneous after environmental adjustment (Q = 144.0, P = 1.46 × 10^-17), and 52.1% of heterogeneity among family-matched species remained within families (P = 8.28 × 10^-8).

5. **Rainfall was therefore associated with a multi-day expansion and species-selective reassembly of the acoustically active frog community, not only an immediate calling response by an unchanged assemblage.** The trait basis of species selectivity remains unresolved, and the acoustic response should not be interpreted as occupancy change or rainfall causality.

## Keywords

active community; anurans; community assembly; environmental pulse; rainfall; species reassembly; temporal beta diversity; turnover

## Introduction

Environmental pulses can reorganize ecological communities on timescales far shorter than changes in regional species pools or local occupancy. A pulse may produce an immediate behavioural response, but its ecological signature can persist if different species enter and leave the realized active community over subsequent days. Distinguishing a momentary activity spike from a multi-day community state is therefore important for understanding how short environmental events propagate through animal assemblages.

Frogs provide a strong test case because rainfall effects on calling are already well established. Rainfall has been linked to calling activity, calling-species richness and chorus onset (Hsu, Kam, & Fellers, 2006; Xie et al., 2017; Brodie, Allen-Ankins, & Schwarzkopf, 2025). Demonstrating that frogs call more on a rainy night is therefore neither surprising nor sufficient as a community-ecology result. Two questions remain more consequential: **how long the active-community response persists after rain, and whether the responding assemblage is compositionally the same community or a different set of species.**

Three compositional alternatives are distinguishable. Under **uniform activation**, wetter conditions increase activity while preserving relative community membership. Under **nested recruitment**, wetter conditions retain a dry-weather core and add species. Under **species-selective reassembly**, wetter conditions increase active richness while simultaneously changing membership, producing turnover and contrasting species-specific responses. A second, temporal dimension concerns the duration of that state: an immediate pulse should decay by the next few days, whereas a multi-day community response should remain detectable after the initial rainfall event has passed.

We tested these alternatives using standardized North American Amphibian Monitoring Program (NAAMP) surveys. First, we matched surveys from the **same route and the same seasonal sampling window** across adjacent observed years and oriented each pair by rainfall recency. We quantified wet–dry richness differences, partitioned compositional dissimilarity into turnover and nestedness, and estimated species-specific wet-versus-dry responses. Second, in a separately frozen timescale analysis, we classified complete runs as day 0, day 1, days 2–3, days 4–7, or ≥8 days since rain and estimated richness contrasts within fixed State × RouteNumber × RunNumber strata. This design asked whether the richness signal was confined to the immediate rain event or persisted across the following week.

We expected a purely immediate calling response to decline rapidly after day 0–1. By contrast, a multi-day ecological pulse would remain visible in active-community richness several days after rain. If rainfall also reassembled the active community rather than uniformly amplifying it, wet–dry richness gains should be accompanied by species replacement and heterogeneous species responses.

## Materials and Methods

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

### Rainfall-pulse timescale

To estimate how long the active-community richness signal remained detectable, we used the same 7,848 complete, temperature-qualified runs and assigned each run to one of five rain-recency classes fixed before timescale outcome readback: day 0, day 1, days 2–3, days 4–7, or ≥8 days since reported rain. The ≥8-day class served as the dry reference.

We modelled run-level active-species richness using within-stratum variation in **State × RouteNumber × RunNumber**, thereby comparing surveys from the same route and seasonal sampling window. Predictors were indicators for day 0, day 1, days 2–3 and days 4–7, together with mean temperature, SurveyYear and a five-degree-of-freedom spline for day of year. Standard errors were cluster-robust by State × RouteNumber. The prespecified richness-pulse endpoint was the latest recent-rain bin whose 95% confidence interval remained entirely above zero relative to the ≥8-day reference, provided all earlier bins had non-negative point estimates.

As a stricter sensitivity, we reused adjacent observed-year matched pairs in which one run occurred <8 days after rain and the other ≥8 days after rain. We estimated recent-minus-dry richness separately for day 0, day 1, days 2–3 and days 4–7 while adjusting for paired temperature difference, day-of-year difference, year gap, State and RunNumber. We repeated this contrast in exact consecutive-year pairs. Because there were too few independent dry–dry pairs to estimate background compositional turnover with adequate precision, we do **not** use the timescale analysis to claim persistence of compositional reassembly itself beyond the matched-pair results.

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

### Active-community richness remains elevated for up to one week after rain

The prespecified run-level timescale analysis included all 7,848 eligible runs from 807 routes and 2,212 route × seasonal-window strata. Relative to surveys conducted ≥8 days after reported rain, adjusted active-species richness was higher in every recent-rain class: day 0, +0.654 species (95% CI 0.448–0.860, P = 5.08 × 10^-10); day 1, +0.544 (95% CI 0.350–0.739, P = 3.86 × 10^-8); days 2–3, +0.411 (95% CI 0.227–0.596, P = 1.26 × 10^-5); and days 4–7, +0.381 (95% CI 0.202–0.561, P = 3.11 × 10^-5). The prespecified richness-pulse endpoint was therefore **days 4–7**.

The stricter matched dry-anchor sensitivity gave the same temporal ordering but wider intervals. In exact consecutive-year pairs, recent-minus-dry richness was +0.866 species on day 0 (95% CI 0.108–1.624), +0.450 on day 1 (0.109–0.790), +0.416 on days 2–3 (0.091–0.741), and +0.257 on days 4–7 (-0.197–0.710). Thus the matched sensitivity clearly supported the richness signal through days 2–3 and remained directionally positive but imprecise at days 4–7.

The week-scale result should not be read as a precise physiological recovery time: DaysSinceRain records recency rather than rainfall amount, and surveys were not repeated daily after individual storms. It nevertheless shows that the community-richness association is not confined to the calendar day of rain.

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

The ecological signal was not confined to the familiar observation that frogs call during or immediately after rain. Within fixed routes and seasonal sampling windows, active-community richness remained elevated across every prespecified rain-recency class through **4–7 days** relative to surveys ≥8 days since rain. The effect was largest on day 0 and declined over subsequent days, but the run-level confidence interval remained entirely positive one week after the reported rain event. A stricter exact-consecutive-year matched analysis clearly supported the signal through days 2–3 and was directionally consistent, though imprecise, at days 4–7. The data therefore support a **multi-day active-community pulse**, not merely an instantaneous chorus response.

That pulse was also compositionally structured. Wetter matched surveys contained more active species, but the wet assemblage was not simply the dry assemblage plus extra species. Nestedness did not increase with rainfall contrast, turnover increased in the exact consecutive-year sensitivity, and species differed sharply in whether they appeared preferentially in wetter or drier matched surveys. Adjusted species effects remained extremely heterogeneous after accounting for temperature differences, survey timing, rainfall-contrast magnitude and year gap (Q = 144.0, P = 1.46 × 10^-17), with raw and adjusted species rankings nearly identical (ρ = 0.997). More than half of heterogeneity among family-matched species remained within families, including significant internal heterogeneity in both Hylidae and Ranidae. The response is therefore organized more finely than a simple broad-clade contrast.

Together, the duration and composition results change the ecological interpretation. A rainfall pulse does not simply “turn up the volume” on an otherwise fixed frog assemblage. It is associated with a temporary expansion of the acoustically active community that persists for several days, while the identities of participating species respond non-uniformly. This is a form of **behaviourally realized community reassembly** on a timescale much shorter than occupancy turnover or regional species-pool change.

The turnover result further distinguishes this pattern from simple nested recruitment. A recent three-year study of a tropical frog community found relatively stable composition and temporal beta diversity dominated by nestedness (Severgnini et al., 2024). Here, rainfall contrast did not increase nestedness, and exact consecutive-year comparisons instead showed increasing turnover. We therefore infer richness gain plus compositional replacement across wet–dry contrasts, while avoiding the stronger claim that compositional turnover itself remains elevated for a full week. A prespecified attempt to compare 4–7-day turnover against dry–dry background turnover failed its minimum sample-size gate before effect readback because dry–dry pairs were too sparse.

Several simple explanations for species selectivity were not supported in follow-up analyses. A pooled body-size association was strong, but it did not survive family-stratified permutation. Coarse ATraiU temporary-versus-permanent breeding-water flags had no variation among covered species, breeding-season breadth did not predict species response, early-period acoustic recurrence and seasonal concentration did not predict later wet recruitment, and a temporally held-out route-dryness context did not modify the richness response. These negative follow-ups narrow the mechanism without identifying it: species selectivity is real and persists within major families, but it is not captured by the simple trait or context axes tested here.

Previously completed activity-decomposition analyses provide supporting context. Recent rain increased the number of standardized stops containing callers and expanded run-level active richness, whereas multispecies calling conditional on an already-active stop and several residual co-calling metrics changed little. Together with the matched-community and timescale results, this places the response primarily at the level of **which sampling units and which species enter the active assemblage over the days following rain**, rather than stronger residual association among species already calling together.

Several limitations define the scope of inference. Acoustic presence is not occupancy: a species absent from a run may remain locally present but silent. “Wet recruitment” therefore means acoustic participation in the wetter survey, not colonization, and “dry loss” does not mean extinction. DaysSinceRain records rain recency, not rainfall amount or intensity, and the data do not follow individual storms daily; “up to one week” therefore describes the temporal support in the prespecified recency classes rather than a physiological half-life. Rainfall was not experimentally manipulated, so time-varying environmental covariates may contribute despite route, seasonal-window, temperature and date controls. The primary turnover coefficient was positive but imprecise (P = 0.104); the significant turnover result comes from the prespecified exact consecutive-year sensitivity. Finally, the ecological-extension, species-response, timescale and trait analyses were developed after the original rainfall endpoint was opened, although each was separately frozen before its own effect readback.

The broader implication is that **short environmental pulses can reorganize behaviourally realized animal communities over multiple days**. In this system, recent rainfall predicts a week-scale elevation in active-community richness and strongly species-selective wet–dry membership shifts. The unresolved question is no longer whether rainfall matters, but what species-level physiology, reproductive strategy or local habitat process generates those contrasting responses.

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

**Figure 1. A rainfall pulse elevates active-community richness for several days.** Panel A: matched same-route, same-seasonal-window design and richness-gain slope. Panel B: adjusted active-species richness contrasts for day 0, day 1, days 2–3 and days 4–7 relative to ≥8 days since rain, showing the prespecified richness-pulse endpoint at days 4–7.

**Figure 2. Species-selective community reassembly.** Adjusted species wet-versus-dry probabilities or log odds with 95% CIs, highlighting FDR-supported wet-associated and dry-associated taxa and noting strong within-family heterogeneity.

**Figure 3. Richness gain is not simple nested addition.** Rain-contrast effects on nestedness and Simpson turnover for the primary matched pairs and exact consecutive-year sensitivity.

Earlier co-calling decomposition, body-size and unsupported trait/context follow-ups are treated as supplementary analyses rather than main figures.

