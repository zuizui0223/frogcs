# Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without detectable homogenization

## Abstract

1. **Short environmental pulses can reorganize observed animal communities without demographic turnover, but richness alone does not show where those changes enter a spatial community.** Rainfall effects on frog calling are well known; we asked whether recent-rain conditions expand the active spatial footprint, deepen local assemblages, increase landscape richness or alter spatial differentiation.

2. **We analysed 15 years of standardized North American Amphibian Monitoring Program surveys.** We compared 4,236 wetter–drier survey pairs from the same route and seasonal sampling window. Ten aligned stops per route allowed us to quantify active-site number, local alpha richness, route gamma richness, beta diversity and exact species × stop incidence changes.

3. **Rainfall contrast was associated with expansion at both spatial and taxonomic scales.** Greater contrast predicted more active stops (β = 0.384, 95% CI 0.240–0.528), higher richness per active stop (β = 0.079, 0.023–0.136) and higher route richness (β = 0.286, 0.165–0.407). Richness also increased within the same StopNumbers active in both paired surveys. These signals persisted after adjustment for recorded hearing impairment, major-noise interruptions and wind, and all three coefficients retained positive 95% confidence intervals when any one of the 21 states was omitted.

4. **Expansion occurred without detectable change in measured beta diversity or material change in active-matrix fill.** Pairwise Sørensen showed no rainfall-associated shift (P = 0.937), while proportional matrix fill met a prespecified ±0.05 practical-equivalence criterion. Of the total species × stop incidence slope, **92.0% crossed at least one spatial or taxonomic matrix boundary**: 36.9% was route-new species at newly active sites, 15.2% existing species at newly active sites and 39.9% route-new species at already-active sites; only 8.0% was rearrangement within the existing active core.

5. **Recent-rain conditions were associated with a larger active community, not a detectably more homogeneous one.** Expansion occurred by adding active sites and taxonomic depth while most additional incidences crossed a spatial and/or taxonomic matrix boundary. The result concerns acoustic activity rather than occupancy, abundance or colonization; species-level mechanism remains unresolved.

## Keywords

active community; alpha diversity; beta diversity; environmental pulse; incidence matrix; metacommunity; rainfall; species richness

## Introduction

Short environmental pulses can change which species are active and where they are detected long before demographic turnover, dispersal or occupancy patterns change. Community responses on these behavioural timescales are often summarized by a single quantity such as richness or total activity, but the same increase in landscape-scale diversity can arise from very different spatial processes: more local communities may become active, diversity may deepen within already-active sites, or composition may converge among sites. Distinguishing these alternatives requires separating local alpha diversity, landscape gamma diversity and among-site beta diversity, and then locating change directly within the species × site incidence matrix (Leibold et al., 2004; Jost, 2007).

Frogs provide a useful test because rainfall effects on calling and chorus activity are already well established (Hsu et al., 2006; Xie et al., 2017; Brodie et al., 2025). Short-term changes in the composition and beta diversity of calling assemblages have also been quantified (Sugai et al., 2021), and wetland inundation can increase frog richness while altering community composition (Sarker et al., 2022). Demonstrating again that frogs call after rain, or that wetting changes richness, would therefore add little. The unresolved question is **where a short rainfall-associated increase enters the spatial community matrix within the same standardized landscape sampling unit**. Recent-rain conditions could activate additional wetlands without changing assemblages inside them, increase taxonomic depth within sites that were already active, or expand both spatial and taxonomic boundaries while leaving relative differentiation among sites intact. These outcomes represent different community responses even when total richness changes by the same amount.

We tested these alternatives with standardized North American Amphibian Monitoring Program (NAAMP) surveys. Calling surveys are behaviour-sensitive observations rather than direct censuses of abundance, and NAAMP methodology has explicitly treated imperfect detection and weather-sensitive calling behaviour as part of the observation process (Royle & Link, 2005). We therefore make the behaviourally realized acoustic community—not latent abundance or occupancy—the object of inference. Each ten-stop route-run was treated as a landscape sampling unit containing replicated local acoustic assemblages; “metacommunity-scale” and “active metacommunity” describe that spatial organization rather than demographic connectivity. We matched wetter and drier runs from the same route and seasonal sampling window and quantified (i) active-stop number, (ii) local alpha richness among active stops, (iii) route gamma richness, (iv) among-active-stop beta diversity and (v) exact changes in the species × stop incidence matrix. The central question was therefore not whether rain increases frog activity, but **how rainfall-associated expansion is partitioned across sites, species and matrix fill**.

## Materials and Methods

### NAAMP surveys and the active-community matrix

We used the U.S. Geological Survey North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). Analyses were restricted to the unified-protocol period 2001–2015. A route contained ten standardized wetland-associated stops sampled acoustically for 5 min. CallingIndex values 1–3 were treated as positive acoustic activity.

For the community analyses we retained complete ten-stop runs with at least eight valid stop temperatures, mean converted temperature between -10 and 45 °C, a parseable survey date, and numeric DaysSinceRain within the publisher-documented 0–180 day range. This yielded 7,848 eligible runs. At each run we represented the observations as a binary species × stop incidence matrix. A stop was **active** if at least one species was detected calling. Local richness was the number of calling species at a stop. Route-level active richness was the number of distinct calling species detected across all ten stops.

These quantities describe the behaviourally realized acoustic community during the survey. They do not measure abundance, occupancy, colonization, extinction or reproductive success.

### Matched wetter–drier comparisons

Runs were stratified by State × RouteNumber × RunNumber, where RunNumber represents the programme’s seasonal sampling window. Within each stratum, eligible runs were ordered by survey year and paired across adjacent observed years. Pairs with equal DaysSinceRain were excluded. In each remaining pair, the run with the smaller DaysSinceRain was labelled wetter and the other drier.

The primary matched dataset contained 4,236 comparisons from 585 routes in 21 states. Of these, 2,693 pairs were exact consecutive years and formed a prespecified sensitivity subset. NAAMP sampling was not exposure-randomized: under the national protocol, Gulf Coast and Great Plains programmes documented the last rainfall event because routes in those regions were intended to be surveyed within three days of rain, reflecting known regional calling behaviour (U.S. Geological Survey, 2016). This protocol feature can restrict the observed support of rainfall recency in some regions and is one reason we interpret all rainfall results as associations rather than causal effects. Because wetter–drier contrasts were matched within State × RouteNumber × RunNumber, comparisons remained within the same regional programme and seasonal sampling structure.

Rainfall contrast was

`ΔR = log(1 + D_dry) - log(1 + D_wet)`,

which is positive by construction and increases with the difference in rainfall recency. Unless noted otherwise, matched-pair models used

`response ~ rain_contrast + temperature_difference + day_of_year_difference + year_gap + State + RunNumber`

with cluster-robust covariance by State × RouteNumber. The same specifications were repeated in exact consecutive-year pairs.

### Geographic generality audit

After the RC6 scientific story had been frozen, we conducted an explicitly versioned pre-submission audit of geographic generality because broad spatial coverage does not by itself establish that a pooled effect is independent of one influential region. The audit contract and an estimability repair were committed before endpoint readback. The three already-authorized headline responses—active-stop number, local alpha richness and route gamma richness—were refit 21 times, each time omitting one state while retaining the original covariates, State and RunNumber fixed effects for the remaining observations, and route-clustered covariance. The prespecified PASS criterion required all leave-one-state-out rainfall-contrast coefficients to remain positive for all three responses; strong PASS required every corresponding 95% confidence interval to remain above zero.

We also estimated state-specific slopes using the same covariates except the State term. These slopes were descriptive and were not used for the PASS decision; states for which route-clustered inference was not estimable were explicitly flagged. A secondary State random-intercept/random-slope model quantified heterogeneity where it converged. No state-specific significance threshold was used as a criterion for generality.

### Metacommunity-scale alpha, beta and gamma decomposition

For each run we quantified four spatial scales of the active community.

**Active spatial footprint** was the number of the ten stops containing at least one calling species.

**Local alpha richness** was mean species richness across active stops. Inactive stops were excluded from this conditional alpha quantity because the number of inactive stops was modelled separately as the spatial-footprint component.

**Gamma richness** was total active-species richness across the route-run.

**Beta diversity** was quantified among active stops using complementary metrics. We calculated mean pairwise Sørensen dissimilarity, decomposed pairwise Sørensen into Simpson turnover and nestedness-resultant components, and calculated a normalized Whittaker measure,

`((gamma / alpha_active) - 1) / (n_active - 1)`,

for runs with at least two active stops. We modelled wet-minus-dry differences in these metrics against rainfall contrast with the matched-pair specification above.

This operational “active metacommunity” is a set of spatially replicated local acoustic assemblages within a route. The analysis does not assume or demonstrate that all stops form a demographic metacommunity linked by contemporary dispersal.

### Spatial and taxonomic expansion

We next resolved how route-level richness change was related to the active spatial footprint. For every species present somewhere in both runs of a pair, we calculated its wet-minus-dry difference in number of occupied stops. Positive values indicate spatial expansion of an already-participating route species.

For route-level richness, wet-only and dry-only species were partitioned according to whether their detections were structurally dependent on a change in active-stop footprint. A wet-only species was classified as footprint-dependent if all of its wetter-run detections occurred at stops that were inactive in the drier run; dry-only species were treated symmetrically. This generated an exact pairwise identity:

`richness gain = footprint-dependent net species + within-footprint net species`.

Because this is an algebraic decomposition of observed incidence patterns, “footprint-dependent” does not mean that activation of a site causally mediated the appearance of a species.

### Within-active-site taxonomic depth

An increase in mean richness per active stop can itself arise at different multiplicity depths. For a run with active-stop species counts (K),

`mean(K | K >= 1) = 1 + P(K >= 2 | active) + E[(K - 2)+ | active]`.

We therefore decomposed the matched wet-minus-dry alpha change into the fraction of active stops crossing from one to at least two species and the mean excess number of species beyond the second. We further split the latter into the fraction reaching at least three species and excess multiplicity beyond the third species.

To hold site identity and active status constant, we also calculated mean wet-minus-dry richness only across StopNumbers active in both members of each matched pair.

### Exact species × stop incidence decomposition

We classified every wet-gain incidence—species present at a stop in the wetter run but not at that same stop in the drier run—along two axes: whether the species was already detected elsewhere in the drier route and whether the stop was already active in the drier run. Dry-loss incidences were classified symmetrically. Net wet-minus-dry changes therefore fell into four mutually exclusive components:

1. **corner expansion:** route-new species × newly active stops;
2. **spatial spread:** route-existing species × newly active stops;
3. **taxonomic deepening:** route-new species × already-active stops;
4. **within-core rearrangement:** route-existing species × already-active stops.

For every matched pair,

`delta species-stop incidences = corner + spatial spread + taxonomic deepening + within-core rearrangement`

exactly. Identical covariates across the four component regressions ensure that the rainfall-contrast coefficients also sum exactly to the coefficient for total species-stop incidence change.

### Active-matrix fill and practical-equivalence test

We quantified the proportional fill of each observed active species × active-stop incidence matrix as

`connectance = incidences / (gamma × n_active) = alpha_active / gamma`.

This quantity is the mean fraction of the active species pool represented at an active site and, equivalently, the mean fraction of active sites occupied by an active species; in binary species × site matrices it is directly related to multiplicative Whittaker beta diversity (Arita et al., 2012). Because fill is undefined when a run contains no active species or active stops, this analysis structurally excluded matched pairs in which either member was completely acoustically inactive.

To distinguish practical invariance from a non-significant difference, we froze an equivalence margin before endpoint readback. We modelled wet-minus-dry connectance with the same matched-pair covariates and route-clustered covariance as the other community metrics. The smallest change considered large enough to contradict structure-preserving expansion was an absolute rainfall-contrast slope of ±0.05 connectance units, approximately 10% of the typical active-matrix fill near 0.5. Practical equivalence required the complete 90% confidence interval for the rainfall-contrast coefficient to lie within [-0.05, +0.05], equivalent to two one-sided tests at α = 0.05. The same margin and model were prespecified for exact consecutive-year pairs. This test concerns observed acoustic matrix fill and does not imply exact invariance.

### Recorded detection-condition robustness

Because acoustic community metrics can be affected by hearing conditions, we prespecified a reviewer-robustness analysis using survey-quality fields recorded by NAAMP. Regional programmes recorded ambient hearing impairment either as a yes/no `Noise` field or with the Massachusetts noise index. We standardized a stop as hearing-impaired when `Noise = 1` or, when the Massachusetts index was available, when `MassNoiseIndex >= 2`; indices 0–1 were treated as not materially impairing sampling. We also used `TimeOut`, which records major noise interruptions during which the listening period was paused, and the mean of valid start- and end-of-run Beaufort wind codes.

For each eligible run we calculated the fraction of sampled stops with recorded hearing impairment, the timeout fraction and mean wind. Primary robustness models added wet-minus-dry differences in these three quantities to the matched-pair models for active-stop count, local alpha richness and route gamma richness. The primary detection-quality sample required at least eight valid stop-level noise and timeout records per run and valid start/end wind in both members of the pair. Prespecified sensitivities additionally adjusted for mean stop-level car counts where at least eight values were available and, in programmes using it, replaced the binary impairment fraction with mean Massachusetts noise index. These analyses constrain measured acoustic detection conditions as an explanation but do not constitute a complete detection model.

### Analysis provenance and inferential boundaries

The original rainfall endpoint in the broader analysis programme was frozen before effect readback. The metacommunity, incidence-matrix, functional and response-diversity analyses reported here were developed after that endpoint had been opened. Each extension was nevertheless committed as a finite versioned contract before its own endpoints were read, with exact-consecutive-year sensitivities and deterministic identity checks where applicable. We describe these analyses transparently as post-opening mechanistic/community extensions rather than original preregistered hypotheses.

All rainfall results are observational associations. Terms such as “new species,” “lost species,” “newly active site” and “active metacommunity” refer to differences in acoustic detections between paired surveys, not colonization, extinction, site creation or demographic connectivity.

## Results

### Recent rain expands both the active spatial footprint and taxonomic richness

The 4,236 matched wetter–drier comparisons represented 585 routes. Wetter surveys contained slightly more active stops on average, and the difference increased strongly with rainfall contrast. Each unit increase in log-rainfall contrast predicted a wet-minus-dry increase of 0.384 active stops (95% CI 0.240–0.528, P = 1.80 × 10^-7). The exact consecutive-year sensitivity remained positive (β = 0.292, P = 5.77 × 10^-4).

Taxonomic richness increased at both local and route scales. Mean richness among active stops increased with rainfall contrast (β = 0.0794 species per active stop, 95% CI 0.0231–0.1357, P = 0.00569), while route-level gamma richness increased by 0.2859 species per unit contrast (95% CI 0.1646–0.4072, P = 3.81 × 10^-6). Both results persisted in exact consecutive-year pairs.

The local increase was not an artefact of newly active stops entering the active-stop average. Restricting each pair to identical StopNumbers that contained callers in both surveys, wet-minus-dry richness still increased with rainfall contrast (β = 0.0953 species per stop, 95% CI 0.0347–0.1559, P = 0.00204; exact-year β = 0.0938, P = 0.0245). Species that occurred somewhere in both route-runs also occupied more stops in wetter surveys (mean shared-species stop-use contrast β = 0.1533, P = 0.0130).

### Recorded hearing conditions do not explain the multiscale expansion signal

The spatial, local-alpha and route-gamma associations persisted after adjustment for recorded hearing impairment, major-noise timeouts and wind differences. In 4,024 matched pairs from 576 routes, the adjusted rainfall-contrast coefficient was +0.377 active stops (95% CI 0.227–0.527, P = 8.52 × 10^-7), +0.0838 species per active stop (95% CI 0.0254–0.1422, P = 0.00494), and +0.2968 route-level species (95% CI 0.1710–0.4227, P = 3.79 × 10^-6). All three confidence intervals also remained positive in the exact consecutive-year subset.

Two prespecified detection sensitivities gave the same qualitative result. Adding mean traffic counts retained positive rainfall coefficients for active stops (+0.448), local alpha (+0.0845) and route gamma (+0.307) across 2,968 matched pairs. In the Massachusetts noise-index subset (1,444 pairs), coefficients were +0.248, +0.158 and +0.428, respectively, with all 95% confidence intervals above zero. Recorded hearing conditions therefore do not account for the observed multiscale expansion, although unmeasured detectability differences remain possible.

### The multiscale expansion signal is not driven by any single state

The frozen geographic-generality audit passed its strongest prespecified criterion. Across all 21 leave-one-state-out refits, rainfall-contrast coefficients remained positive and their 95% confidence intervals remained above zero for active-stop number, local alpha richness and route gamma richness. The active-stop coefficient ranged from 0.346 to 0.433 across state omissions, local alpha from 0.0496 to 0.0955, and route gamma from 0.218 to 0.329. Even the smallest lower 95% confidence limit across the 21 refits was positive for each response (+0.196 active stops, +0.0101 species per active stop and +0.118 route-level species, respectively). Thus no single sampled state controlled any of the three headline associations.

This robustness to state omission did not imply uniform state-level responses. Of 19 states with estimable route-clustered state-specific models, the rainfall slope was positive in 16 for active-stop number and in 13 for both local alpha and route gamma. Florida and Texas did not support the prespecified state-specific clustered model. Opposite-direction state-specific confidence intervals occurred for active-stop number in Vermont and for local alpha in Massachusetts, whereas no state had a wholly negative confidence interval for route gamma. We therefore interpret the result as broad geographic robustness of the pooled expansion signal with genuine local heterogeneity, not as evidence that every state responds identically.

### Alpha and gamma expansion occurs without detectable change in among-site beta diversity

Despite increases in active-stop number, local alpha richness and route gamma richness, compositional differentiation among active stops changed little with rainfall contrast. The coefficient for wet-minus-dry mean pairwise Sørensen dissimilarity was -0.00049 (95% CI -0.0126–0.0116, P = 0.937). The normalized Whittaker beta coefficient was -0.00482 (95% CI -0.0147–0.00507, P = 0.339).

The two components of pairwise Sørensen were likewise stable: turnover β = -0.00097 (P = 0.885) and nestedness-resultant dissimilarity β = +0.00048 (P = 0.877). Exact consecutive-year sensitivities were also near zero for all beta metrics. Thus the observed active community expanded in spatial footprint, alpha richness and gamma richness without detectable homogenization or differentiation among already-active local assemblages.

### Active-matrix fill is practically equivalent across rainfall contrast

Of the 4,236 matched comparisons, 116 contained a completely inactive run and therefore had undefined active-matrix fill, leaving 4,120 pairs from 582 routes. Mean matrix fill was 0.5552 in drier surveys and 0.5534 in wetter surveys. The rainfall-contrast coefficient was -0.00936 connectance units (95% CI -0.0214–0.00263).

More importantly, the prespecified 90% equivalence interval was -0.0194 to 0.00070, entirely inside the frozen practical-equivalence margin of ±0.05. The exact consecutive-year subset gave the same conclusion (β = -0.00739; 90% equivalence interval -0.0191–0.00436). Thus, within the prespecified margin, the active incidence matrix added species and sites without a material change in its average proportional fill. Because matrix fill equals local alpha divided by route gamma, this is a direct matrix-geometric restatement of their joint scaling rather than an independent diversity axis.

### The species × stop matrix expands mainly at spatial and taxonomic boundaries

Rainfall contrast predicted an increase of 1.365 species × stop incidences in the wetter survey (95% CI 0.757–1.974, P = 1.10 × 10^-5). Exact algebraic decomposition showed that almost all of this increase involved opening at least one boundary of the observed matrix.

**Corner expansion**—route-new species appearing at newly active stops—contributed β = 0.5040, or 36.9% of the total incidence slope (P = 5.07 × 10^-7). **Spatial spread**—route-existing species appearing at newly active stops—contributed β = 0.2080, or 15.2% (P = 0.00623). **Taxonomic deepening**—route-new species entering stops that were already active in the drier survey—contributed β = 0.5444, or 39.9% (P = 0.00159). By contrast, **within-core rearrangement** of route-existing species among already-active stops contributed only β = 0.1090, or 8.0%, and was not distinguishable from zero (P = 0.252).

Exact consecutive-year pairs gave a similar partition: 33.3% corner expansion, 11.2% spatial spread, 46.9% taxonomic deepening and 8.6% within-core rearrangement. The main pattern was therefore not reshuffling of a fixed set of species among a fixed set of active sites, but simultaneous expansion of spatial and taxonomic participation.

### Local deepening is concentrated beyond the second species

The increase in mean species richness per active stop also had a structured multiplicity profile. Of the total rainfall-contrast coefficient for active-stop mean richness (0.0794), 0.0230 (28.9%) was attributable to the increase in the fraction of active stops containing at least two species (P = 0.0142). The remaining 0.0565 (71.1%) was attributable to additional multiplicity beyond the second species (P = 0.0147).

Consistent with this result, the fraction of active stops containing at least three species increased with rainfall contrast (β = 0.0226, P = 0.00670), and excess multiplicity beyond the third species was also positive (β = 0.0338, P = 0.0399). Thus “taxonomic deepening” was not merely conversion of single-species detections into two-species detections; richer multispecies active assemblages became more prominent.

### Species-level mechanism remains unresolved after placebo tests

Post-opening species-level analyses did not yield an authorized rainfall-specific mechanism. An opportunity-corrected “activation geometry” was repeatable across non-overlapping years and disjoint route sets, but a separately frozen falsification gate showed that the same species ordering was reproduced by reverse-direction dry gains (ρ = 0.929), low-rain-contrast pairs (ρ = 0.953) and baseline acoustic solitude tendency (ρ = 0.782); the raw singleton-calling fraction was also strongly correlated with the proposed geometry (ρ = 0.876). The prespecified headline gate therefore failed, and activation geometry is not interpreted as a rainfall-specific response trait. Functional and other static-trait analyses likewise did not provide a robust replacement mechanism (Supporting Information).

### Secondary falsification analyses do not alter the matrix interpretation

Several prespecified or frozen alternatives were not supported and are reported in full in Supporting Information. Early response-sign diversity did not buffer later route-richness sensitivity to rainfall contrast (interaction β = -0.954, 95% CI -3.267–1.359, P = 0.419). The rain-recency analysis supports an association beyond the calendar day of rain, but the exact consecutive-year 4–7-day contrast was imprecise, so no week-long endpoint is used. Primary between-year turnover was also imprecise (P = 0.104). Coarse hydroperiod, breeding-season breadth, recurrence, seasonal concentration, historical route dryness and the prespecified spatial-specialist hypothesis did not provide an authorized mechanism. These failures narrow rather than replace the main inference: the robust result is the two-dimensional expansion of the active community and the way that expansion is partitioned across the observed species × stop matrix.

## Discussion

Recent-rain conditions were associated with a larger behaviourally realized frog community at both local and landscape scales: more stops were acoustically active, active stops contained more species, and route-level active richness increased. Yet the measured beta-diversity metrics showed no detectable rainfall-associated shift. This pooled pattern was also geographically robust in the specific sense tested here: omitting any one of the 21 sampled states left positive, confidence-interval-supported effects for active footprint, local alpha and route gamma. State-specific slopes nevertheless varied, so broad robustness should not be confused with a spatially uniform response. This contrasts with prior anuran work in which short-term calling composition varies through time and wetland inundation is associated with altered community composition (Sugai et al., 2021; Sarker et al., 2022). The main result is therefore not simply “more calling after rain,” but **two-dimensional active-community expansion** across both spatial and taxonomic dimensions without detectable spatial homogenization.

The species × stop decomposition makes that expansion explicit. Approximately 92% of the rainfall-associated incidence slope crossed at least one boundary of the observed matrix: new route-level participants appeared at newly active or already-active stops, and route-existing species also spread into newly active stops. Only about 8% was attributable to rearrangement of existing route species among sites that were already active. The accounting identity guarantees that the four components sum to total incidence change; it does **not** determine how the rainfall-associated slope is distributed among them. The empirical result is therefore the strong concentration of that slope on boundary-crossing components rather than within-core rearrangement. Consistent with that pattern, proportional fill of the active species × site matrix passed the prespecified practical-equivalence test in both the primary and exact-year samples. Matrix fill is mathematically linked to alpha/gamma and is not an independent diversity component, but the equivalence result sharpens the geometric interpretation: the active matrix expanded in rows and columns without a material change in average fill within the frozen ±0.05 margin.

Species-level analyses did not yield a rainfall-specific mechanism. A proposed activation geometry was highly repeatable across time and disjoint route sets, but reverse-direction gains, low-rain-contrast pairs and baseline solitude tendency reproduced the same species ranking. The prespecified placebo gate therefore failed, and **activation geometry is not interpreted as a rainfall-specific response trait**. Its repeatability is more parsimoniously treated as a stable acoustic co-occurrence or gain-placement property. This falsification is useful because it prevents a persistent species property from being promoted as the explanation for rainfall-associated matrix expansion.

The absence of an identified species-level mechanism does not leave the community pattern biologically uninterpretable. Independent anuran studies show that sympatric species respond to different combinations of rainfall, temperature, humidity and other weather variables (Oseen & Wassersug, 2002), and that temperate assemblages contain multiple breeding strategies ranging from seasonally predictable calling to rainfall- or flood-dependent opportunistic breeding (Saenz et al., 2006). Continuous acoustic monitoring further shows that explosive breeders may begin chorusing on the night of, or immediately after, large rain events, whereas prolonged breeders respond to different rainfall windows and other cues (Brodie et al., 2025). Wetland inundation can increase frog richness while eliciting contrasting chorusing responses among species and sites (Sarker et al., 2022). A proximal hydric route is also biologically plausible: field hydration state varies with seasonal water availability and habitat use, and anurans possess physiological control over cutaneous water uptake (Tracy et al., 2014; Lemenager et al., 2022). Together with the geographic heterogeneity observed here, this literature supports a **plausible activation-threshold interpretation**: recent rain and associated moisture or breeding-site conditions may move different species and sites across different behavioural activation thresholds, recruiting previously acoustically inactive participants into the realized community. Such heterogeneous recruitment could enlarge spatial footprint and taxonomic depth without forcing local assemblages to converge. Hydration is one candidate proximal route within this interpretation, not a mediator identified by the present analysis.

Several limits define the inference. The study concerns **acoustic activity**, not occupancy, abundance, colonization or reproductive success. Positive spatial, alpha and gamma coefficients persisted after adjustment for recorded hearing impairment, major-noise interruptions and wind, and in sensitivities using traffic counts and the Massachusetts noise index, but unmeasured masking and species-specific detectability remain possible. The ten-stop route provides replicated local assemblages, but the analysis **does not assume or demonstrate that all stops form a demographic metacommunity**. Rainfall was observational, and the regional NAAMP protocol sometimes deliberately targeted surveys soon after rain; DaysSinceRain therefore reflects both weather history and programme scheduling. Matching within route and seasonal window, State and RunNumber adjustment, exact-consecutive-year replication, detection-condition sensitivities and the leave-one-state-out audit constrain several alternatives, but they do not remove time-varying confounding or protocol-based selection. An earlier repository version emphasized a null rain effect on the probability of multiple species conditional on a stop already being active (OR = 0.988, P = 0.402). The current matched-pair alpha decomposition uses a different estimand—wet-minus-dry changes in run-level richness and the fraction of active stops with ≥2 species—and about 71% of the alpha slope lies beyond the two-species threshold. The two results therefore address different weighting and response constructions rather than silently reversing the same model; Supporting Information gives the explicit reconciliation.

The evidential hierarchy is also important. **The original rainfall endpoint in the broader analysis programme was frozen before effect readback.** The alpha–beta–gamma, matrix and trait extensions arose during subsequent interpretation and were frozen before their own endpoint readback. That procedure limits within-analysis flexibility but does not make post-opening questions preregistered. Supporting Information retains failed and non-headline mechanism tests—including rain-recency, turnover, response-diversity, trait and activation-geometry analyses—so the development path remains auditable. The rain-recency analysis supports an association beyond the day of rain but does not identify a clean pulse duration; the main spatial and taxonomic conclusions do not depend on one.

More generally, short environmental pulses need not reorganize an observed community in the same way that they enlarge it. This distinction matters especially for acoustic monitoring, where the observed community is a weather-sensitive behavioural realization of a latent biological assemblage rather than a direct census of that assemblage (Royle & Link, 2005). In this system, recent-rain conditions were associated with a community matrix that expanded across sites and species while measured among-site compositional differentiation showed no detectable shift and matrix fill remained within a prespecified practical-equivalence range. The ecological contrast is therefore **expansion without detectable homogenization**: the active community became larger chiefly by opening matrix boundaries rather than by reshuffling an unchanged core.

## Data Availability

NAAMP source data are publicly available from the U.S. Geological Survey data release (Foreman et al., 2017; DOI 10.5066/F7G44NG0). Functional traits are from AmphiBIO v1 (Oliveira et al., 2017; DOI 10.1038/sdata.2017.123; data DOI 10.6084/m9.figshare.4644424.v5). The analysis repository preserves source digests, versioned contracts, deterministic scripts, workflow receipts and derived summaries. Raw third-party source datasets are not redistributed. A persistent archive identifier will be added at finalization.

## References

Arita, H. T., Christen, A., Rodríguez, P., & Soberón, J. (2012). The presence–absence matrix reloaded: the use and interpretation of range–diversity plots. *Global Ecology and Biogeography*, 21, 282–292. https://doi.org/10.1111/j.1466-8238.2011.00662.x

Brodie, S., Allen-Ankins, S., & Schwarzkopf, L. (2025). Environmental influences on chorusing patterns in an Australian tropical savanna frog community. *Ecosphere*, 16, e70153. https://doi.org/10.1002/ecs2.70153

Foreman, T., Grant, E. H., & Weir, L. A. (2017). *North American Amphibian Monitoring Program (NAAMP) anuran detection data from the eastern and central United States (1994–2015)* [Data release]. U.S. Geological Survey. https://doi.org/10.5066/F7G44NG0

Holt, R. D. (2008). Theoretical perspectives on resource pulses. *Ecology*, 89, 671–681. https://doi.org/10.1890/07-0348.1

Hsieh, C.-h., Pan, R.-Y., Chang, C.-W., Anneville, O., et al. (2026). Quantifying the effects of response diversity dynamics on ecosystem stability. *Nature Communications*, 17, 4090. https://doi.org/10.1038/s41467-026-70192-x

Hsu, M.-Y., Kam, Y.-C., & Fellers, G. M. (2006). Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology*, 269, 331–339. https://doi.org/10.1111/j.1469-7998.2006.00044.x

Jost, L. (2007). Partitioning diversity into independent alpha and beta components. *Ecology*, 88, 2427–2439. https://doi.org/10.1890/06-1736.1

Kraft, N. J. B., Adler, P. B., Godoy, O., James, E. C., Fuller, S., & Levine, J. M. (2015). Community assembly, coexistence and the environmental filtering metaphor. *Functional Ecology*, 29, 592–599. https://doi.org/10.1111/1365-2435.12345

Kunze, C., et al. (2026). Species interactions determine the importance of response diversity for community stability to pulse disturbances. *Ecology Letters*. https://doi.org/10.1111/ele.70299

Leibold, M. A., Holyoak, M., Mouquet, N., Amarasekare, P., Chase, J. M., Hoopes, M. F., Holt, R. D., Shurin, J. B., Law, R., Tilman, D., Loreau, M., & Gonzalez, A. (2004). The metacommunity concept: a framework for multi-scale community ecology. *Ecology Letters*, 7, 601–613. https://doi.org/10.1111/j.1461-0248.2004.00608.x

Mori, A. S., Furukawa, T., & Sasaki, T. (2013). Response diversity determines the resilience of ecosystems to environmental change. *Biological Reviews*, 88, 349–364. https://doi.org/10.1111/brv.12004

Ross, S. R. P.-J., Petchey, O. L., Sasaki, T., & Armitage, D. W. (2023). How to measure response diversity. *Methods in Ecology and Evolution*, 14, 1150–1167. https://doi.org/10.1111/2041-210X.14087

Royle, J. A., & Link, W. A. (2005). A general class of multinomial mixture models for anuran calling survey data. *Ecology*, 86, 2505–2512. https://doi.org/10.1890/04-1802

U.S. Geological Survey. (2016). *North American Amphibian Monitoring Program*. Eastern Ecological Science Center.



Sarker, M. A. R., McKnight, D. T., Ryder, D., Walcott, A., Ocock, J. F., Spencer, J. A., Preston, D., Brodie, S., & Bower, D. S. (2022). The effect of inundation on frog communities and chorusing behaviour. *Ecological Indicators*, 145, 109640. https://doi.org/10.1016/j.ecolind.2022.109640

Sugai, L. S. M., Silva, T. S. F., Llusia, D., & Siqueira, T. (2021). Drivers of assemblage-wide calling activity in tropical anurans and the role of temporal resolution. *Journal of Animal Ecology*, 90, 673–684. https://doi.org/10.1111/1365-2656.13399

Oliveira, B. F., São-Pedro, V. A., Santos-Barrera, G., Penone, C., & Costa, G. C. (2017). AmphiBIO, a global database for amphibian ecological traits. *Scientific Data*, 4, 170123. https://doi.org/10.1038/sdata.2017.123

Oseen, K. L., & Wassersug, R. J. (2002). Environmental factors influencing calling in sympatric anurans. *Oecologia*, 133, 616–625. https://doi.org/10.1007/s00442-002-1067-5

Saenz, D., Fitzgerald, L. A., Baum, K. A., & Conner, R. N. (2006). Abiotic correlates of anuran calling phenology: the importance of rain, temperature, and season. *Herpetological Monographs*, 20, 64–82. https://doi.org/10.1655/0733-1347(2007)20[64:ACOACP]2.0.CO;2

Tracy, C. R., Tixier, T., Le Nöene, C., & Christian, K. A. (2014). Field hydration state varies among tropical frog species with different habitat use. *Physiological and Biochemical Zoology*, 87, 197–202. https://doi.org/10.1086/674537

Lemenager, L. A., Tracy, C. R., Christian, K. A., & Tracy, C. R. (2022). Physiological control of water exchange in anurans. *Ecology and Evolution*, 12, e8597. https://doi.org/10.1002/ece3.8597

Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017). An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators*, 82, 13–22. https://doi.org/10.1016/j.ecolind.2017.06.015

Yang, L. H., Bastow, J. L., Spence, K. O., & Wright, A. N. (2008). What can we learn from resource pulses? *Ecology*, 89, 621–634. https://doi.org/10.1890/07-0175.1

## Figure concepts

**Figure 1. Recent-rain conditions enlarge the active community without detectable spatial homogenization.** Panel A shows rain-contrast coefficients for active-stop count, local alpha and route gamma. Panel B shows near-zero pairwise Sørensen and normalized Whittaker beta effects. Panel C compares the core coefficients before and after recorded hearing/noise/wind adjustment. Panel D summarizes the matched design and exact-year sensitivity.

**Figure 2. Most rainfall-associated incidence growth crosses a spatial or taxonomic matrix boundary.** Panel A shows the 2 × 2 matrix defined by route-new versus route-existing species and previously inactive versus already-active stops. Panel B presents the exact four-way coefficient shares: 36.9% corner expansion, 15.2% spatial spread, 39.9% taxonomic deepening and 8.0% within-core rearrangement. Panel C decomposes local alpha increase into the ≥2-species threshold component and multiplicity beyond the second species.

Rain-recency, turnover/nestedness, functional-trait analyses, response-diversity tests, activation-geometry repeatability and its placebo falsification are reported in Supporting Information.
