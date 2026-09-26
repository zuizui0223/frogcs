# Rainfall-associated expansion of frog active communities adds sites and species without detectable beta-diversity change

## Abstract

1. **Short environmental pulses can reorganize observed animal communities without demographic turnover, but richness alone does not show where those changes enter a spatial community.** Rainfall effects on frog calling are well known; we asked whether recent-rain conditions expand the active spatial footprint, deepen local assemblages, increase landscape richness or alter spatial differentiation.

2. **We analysed 15 years of standardized North American Amphibian Monitoring Program surveys.** We compared 4,236 wetter–drier survey pairs from the same route and seasonal sampling window. Ten aligned stops per route allowed us to quantify active-site number, local alpha richness, route gamma richness, beta diversity and exact species × stop incidence changes.

3. **Rainfall contrast was associated with expansion at both spatial and taxonomic scales.** Greater contrast predicted more active stops (β = 0.384, 95% CI 0.240–0.528), higher richness per active stop (β = 0.079, 0.023–0.136) and higher route richness (β = 0.286, 0.165–0.407). Richness also increased within the same StopNumbers active in both paired surveys. These signals persisted after adjustment for recorded hearing impairment, major-noise interruptions and wind.

4. **Expansion occurred without detectable change in measured beta diversity or material change in active-matrix fill.** Pairwise Sørensen showed no rainfall-associated shift (P = 0.937), while proportional matrix fill met a prespecified ±0.05 practical-equivalence criterion. Of the total species × stop incidence slope, 36.9% was route-new species at newly active sites, 15.2% existing species at newly active sites, 39.9% route-new species at already-active sites and 8.0% rearrangement within the existing active core.

5. **Recent-rain conditions therefore enlarge the behaviourally realized frog community along both spatial and taxonomic dimensions without detectable spatial homogenization.** The result concerns acoustic activity rather than occupancy, abundance or colonization, and secondary species-trait analyses are treated as falsification evidence rather than as the mechanism of the community response.

## Keywords

active community; alpha diversity; beta diversity; environmental pulse; incidence matrix; metacommunity; rainfall; species richness

## Introduction

Ecological communities are often observed under environmental conditions that vary much faster than demographic turnover, dispersal or long-term occupancy. Short environmental pulses can therefore change the **realized active community** on behavioural timescales even when the underlying regional pool changes little. Pulse ecology has long emphasized that brief environmental events can propagate across biological levels and that their consequences depend on the spatial and temporal scale at which organisms respond (Yang et al., 2008; Holt, 2008). Yet community responses to such pulses are commonly reduced to a single quantity such as abundance, richness or total activity. That compression can hide whether a pulse activates additional local communities, increases diversity within already-active communities, or reorganizes differences among communities across a landscape.

A metacommunity perspective is useful precisely because it separates local and landscape scales (Leibold et al., 2004). In a spatially replicated survey, a change in landscape-scale richness can arise in several ways. More sites may enter the observed active state; local richness may increase at sites that were already active; species already participating at landscape scale may spread among sites; or species not previously observed in the landscape-level active assemblage may appear. These mechanisms need not have the same consequences for beta diversity. If environmental forcing homogenizes local assemblages, local alpha diversity may rise while compositional differentiation declines. Alternatively, alpha and gamma diversity could increase while beta diversity remains approximately stable, implying an expansion of the active community without collapse of its spatial organization. Because beta metrics can depend mechanically on alpha and the number of local communities, interpreting this pattern also requires complementary dissimilarity measures and normalized partitioning (Jost, 2007).

Frogs provide a strong system for resolving these possibilities. Rainfall effects on anuran calling and chorus activity are familiar (Hsu et al., 2006; Xie et al., 2017; Brodie et al., 2025). Demonstrating once more that frogs call after rain would therefore add little. The more informative question is **where the rainfall-associated increase enters the community matrix**. A recent-rain survey could contain more active wetlands but essentially unchanged assemblages within those wetlands; alternatively, the same wetlands could contain more species; or both spatial and taxonomic boundaries could expand simultaneously. These alternatives have different implications for how short environmental variation is translated into landscape-scale biodiversity observations.

We addressed these questions using standardized North American Amphibian Monitoring Program (NAAMP) surveys. We treated each ten-stop route-run as a landscape sampling unit containing replicated local active assemblages; we use “metacommunity-scale” and “active metacommunity” as descriptions of this spatial organization, not as evidence of demographic connectivity among stops. We matched wetter and drier runs from the same route and seasonal sampling window, then quantified (i) the number of active stops, (ii) local alpha richness among active stops, (iii) route-level gamma richness, (iv) among-active-stop beta diversity, and (v) exact changes in the species × stop incidence matrix. The central question was not whether frogs call after rain, but **how a familiar rainfall association is distributed across the rows, columns and fill of a spatial community matrix**.

## Materials and Methods

### NAAMP surveys and the active-community matrix

We used the U.S. Geological Survey North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). Analyses were restricted to the unified-protocol period 2001–2015. A route contained ten standardized wetland-associated stops sampled acoustically for 5 min. CallingIndex values 1–3 were treated as positive acoustic activity.

For the community analyses we retained complete ten-stop runs with at least eight valid stop temperatures, mean converted temperature between -10 and 45 °C, a parseable survey date, and numeric DaysSinceRain within the publisher-documented 0–180 day range. This yielded 7,848 eligible runs. At each run we represented the observations as a binary species × stop incidence matrix. A stop was **active** if at least one species was detected calling. Local richness was the number of calling species at a stop. Route-level active richness was the number of distinct calling species detected across all ten stops.

These quantities describe the behaviourally realized acoustic community during the survey. They do not measure abundance, occupancy, colonization, extinction or reproductive success.

### Matched wetter–drier comparisons

Runs were stratified by State × RouteNumber × RunNumber, where RunNumber represents the programme’s seasonal sampling window. Within each stratum, eligible runs were ordered by survey year and paired across adjacent observed years. Pairs with equal DaysSinceRain were excluded. In each remaining pair, the run with the smaller DaysSinceRain was labelled wetter and the other drier.

The primary matched dataset contained 4,236 comparisons from 585 routes in 21 states. Of these, 2,693 pairs were exact consecutive years and formed a prespecified sensitivity subset. Rainfall contrast was

`ΔR = log(1 + D_dry) - log(1 + D_wet)`,

which is positive by construction and increases with the difference in rainfall recency. Unless noted otherwise, matched-pair models used

`response ~ rain_contrast + temperature_difference + day_of_year_difference + year_gap + State + RunNumber`

with cluster-robust covariance by State × RouteNumber. The same specifications were repeated in exact consecutive-year pairs.

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

Several prespecified or frozen alternatives were not supported and are reported in full in Supporting Information. Early response-sign diversity did not buffer later route-richness sensitivity to rainfall contrast (interaction β = -0.954, 95% CI -3.267–1.359, P = 0.419). The rain-recency analysis supports an association beyond the calendar day of rain, but the exact consecutive-year 4–7-day contrast was imprecise, so no week-long endpoint is used. Primary between-year turnover was also imprecise (P = 0.104). Coarse hydroperiod, breeding-season breadth, recurrence, seasonal concentration, historical route dryness and the prespecified spatial-specialist hypothesis did not provide an authorized mechanism. These failures narrow rather than replace the main inference: the robust result is the geometry of active-community expansion and its repeatable species-specific activation modes.

## Discussion

Our results resolve a familiar rainfall–calling association into a substantially more specific community-ecological pattern. Recent rain was associated with **more active sites, more species within active sites and more species across the route**, but not with detectable loss or gain of compositional differentiation among active sites. In other words, the behaviourally realized community expanded at both local and landscape scales while no detectable change occurred in the measured beta metrics. This differs from a simple “chorus intensification” interpretation and from a homogenization scenario in which the same rain-favoured assemblage spreads across all sites.

The species × stop decomposition shows why. Approximately 92% of the rainfall-associated incidence slope involved crossing at least one boundary of the observed matrix. New route-level participants occurred at both newly active and previously active stops, while species already present at route scale also expanded into newly active stops. Only about 8% of the slope was attributable to rearrangement of existing route species among sites that were already active. The response is therefore best described as **two-dimensional expansion**: spatial dilation of the active footprint together with taxonomic deepening of the local and landscape active assemblage.

The species-level activation geometry is the lower-level counterpart of this same matrix accounting. For each species, wetter-run gains can be placed at sites that were inactive or already active in the paired drier survey, after correcting for how many sites of each type were available. Summing those gain incidences across species yields the positive-entry sides of the community decomposition: gains at previously inactive stops contribute to corner expansion or spatial spread, whereas gains at already-active stops contribute to taxonomic deepening or within-core gain. The symmetric community analysis additionally subtracts dry-loss incidences, so species geometry alone does not reconstruct the net community coefficients. It instead identifies which taxa disproportionately load onto the spatial-edge versus local-deepening pathways whose aggregate balance produces the observed expansion.

The alpha–beta–gamma result adds an important constraint. Increasing alpha and gamma do not by themselves imply any particular change in spatial organization. Here multiple beta metrics, including a form normalized for alpha and active-site number, remained close to zero across the rainfall contrast. In addition, proportional fill of the active species × site matrix passed a prespecified practical-equivalence test: its 90% interval lay well inside ±0.05 connectance units per unit rainfall contrast in both the primary and exact-year samples. Because matrix fill is mathematically linked to alpha/gamma, this is not an independent fourth diversity component; instead, it makes the geometry of the expansion explicit. Rows and columns of the active matrix increased while average fill remained materially stable within the frozen margin. The additional local richness therefore did not measurably collapse site-to-site differences into a common wet-weather assemblage.

Species-level analyses did not identify a unique rainfall-specific trait mechanism. In particular, the proposed activation geometry was highly repeatable across time and route subsets but failed its frozen placebo gate because reverse-direction gains, low-rain-contrast pairs and baseline solitude tendency reproduced the same species ranking (Supporting Information). We therefore interpret that repeatability as evidence of a stable species co-occurrence/gain-placement property, not as evidence that rainfall induces a distinct species response geometry. This falsification strengthens the narrower community-level conclusion by preventing a persistent species property from being promoted as the causal or mechanistic explanation for matrix expansion.

Several limits are important. First, the entire study concerns **acoustic activity**. The core spatial, alpha and gamma coefficients remained positive after adjustment for NAAMP-recorded hearing impairment, major-noise interruptions, wind and, in a large subset, traffic counts; they also persisted when the Massachusetts noise index was used directly. This makes the recorded survey hearing conditions an unlikely explanation for the main pattern, but it does not eliminate unmeasured acoustic detectability or species-specific masking. A stop becoming acoustically active can reflect calling phenology, breeding engagement, local movement, detectability or combinations of these processes; it does not establish occupancy gain. Likewise, a route-new species is new only to the paired active assemblage and need not have colonized the route. Second, the ten-stop route is a convenient multiscale sampling system, but we do not demonstrate dispersal links among stops and therefore avoid a demographic metacommunity claim. Third, rainfall was observational, and unmeasured time-varying conditions may contribute despite matched geography, seasonal window, temperature and date adjustment. Fourth, the functional panel is deliberately finite. Traits such as developmental rate, fine-scale breeding hydroperiod, call energetics or physiological water balance may better encode rainfall response but are not adequately represented in the current frozen trait source. The null trait–response alignment applies only to the tested life-history space.

An earlier repository version emphasized a null rain effect on the **probability of multiple species conditional on a stop already being active** (OR = 0.988, P = 0.402). The current matched-pair alpha decomposition uses a different estimand: wet-minus-dry changes in each run's mean richness and fraction of active stops with ≥2 species, with route-season pairing and pair-level weighting. The small ≥2-species component is positive in that matched analysis, but about 71% of the alpha slope comes from multiplicity **beyond the second species**. The two results therefore need not agree numerically and do not represent a silent reversal of the same model; Supporting Information gives the explicit estimand and weighting comparison.

The analysis hierarchy also deserves explicit treatment. The original programme-level rainfall endpoint was specified before readback, whereas the community-scale decompositions arose during subsequent interpretation. We controlled this iterative development by freezing each new decomposition before reading its own endpoints, preserving deterministic source hashes, exact algebraic identities and an exact-consecutive-year sensitivity. These safeguards do not turn post-opening questions into preregistered ones. Supporting Information preserves the failed and non-headline mechanism tests so that the evidence hierarchy is auditable. The strongest contribution is therefore the convergence of independently specified decompositions on the same structural result rather than the nominal significance of any single exploratory extension.

The rain-recency analysis is treated only as secondary context: the association is not confined to the day of rain, but its exact duration is not identified cleanly (Supporting Information S2). The main spatial and taxonomic conclusions do not depend on assigning a pulse duration.

More generally, short environmental pulses may reorganize observed communities without either demographic turnover or wholesale replacement of their spatial structure. In this frog system, recent rainfall was associated with an expansion of the **active community matrix**: additional localities became active, existing species spread among localities, new active participants entered both new and already-active sites, and local multispecies depth increased. Yet measured beta diversity showed no detectable shift and active-matrix fill remained within the prespecified practical-equivalence margin. This combination—taxonomic and spatial expansion without detectable change in compositional differentiation—would be missed by analyses focused only on total chorus activity or route richness.

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

Oliveira, B. F., São-Pedro, V. A., Santos-Barrera, G., Penone, C., & Costa, G. C. (2017). AmphiBIO, a global database for amphibian ecological traits. *Scientific Data*, 4, 170123. https://doi.org/10.1038/sdata.2017.123

Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017). An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators*, 82, 13–22. https://doi.org/10.1016/j.ecolind.2017.06.015

Yang, L. H., Bastow, J. L., Spence, K. O., & Wright, A. N. (2008). What can we learn from resource pulses? *Ecology*, 89, 621–634. https://doi.org/10.1890/07-0175.1

## Figure concepts

**Figure 1. Recent-rain conditions expand the active community at local and landscape scales without detectable beta-diversity change.** Panel A shows rain-contrast coefficients for active-stop count, local alpha and route gamma. Panel B shows near-zero pairwise Sørensen and normalized Whittaker beta effects. Panel C compares the core coefficients before and after recorded hearing/noise/wind adjustment. Panel D summarizes the matched design and exact-year sensitivity.

**Figure 2. Rainfall-associated expansion occurs at the boundaries of the species × stop matrix.** Panel A shows the 2 × 2 matrix defined by route-new versus route-existing species and previously inactive versus already-active stops. Panel B presents the exact four-way coefficient shares: 36.9% corner expansion, 15.2% spatial spread, 39.9% taxonomic deepening and 8.0% within-core rearrangement. Panel C decomposes local alpha increase into the ≥2-species threshold component and multiplicity beyond the second species.

Rain-recency, turnover/nestedness, functional-trait analyses, response-diversity tests, activation-geometry repeatability and its placebo falsification are reported in Supporting Information.
