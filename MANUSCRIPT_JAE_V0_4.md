# Recent rainfall predicts broader frog acoustic participation without stronger residual co-calling associations

## Abstract

1. **Environmental pulses can make more species appear together by independently activating more species or by changing residual temporal association.** Multispecies detections alone do not distinguish broader community participation from synchrony.

2. **We separated these possibilities using two continental frog-monitoring systems.** In NAAMP, we tested rainfall recency against the proportion of standardized 5-min stops containing at least two calling species. We tested the same directional event-level pattern in Australian FrogID recordings linked to ERA5 precipitation, then decomposed the NAAMP signal into acoustic activation, active species-pool richness and residual co-calling.

3. **Recent rainfall predicted more multispecies calling in both systems.** Across 9,399 NAAMP runs and 93,383 stops, the primary odds ratio was 0.969 per 1 SD increase in log-transformed days since rain (95% CI 0.941–0.998). After temperature and nonlinear day-of-year adjustment, the NAAMP rain association remained (OR 0.946, 95% CI 0.917–0.976). In 40,754 FrogID recordings, antecedent dry-spell duration likewise reduced the odds of multiple calling species after timezone-aware event-time repair (OR 0.853, 95% CI 0.827–0.879).

4. **NAAMP decomposition showed an activation-dominated rainfall signal.** Increasing dryness reduced the odds that any species was calling (OR 0.904, P = 4.63 × 10^-8) and was associated with lower active species richness (β = -0.0187, P = 1.92 × 10^-4). Rain did not change multispecies calling conditional on acoustic activity (OR 0.988, P = 0.402), pairwise network density (P = 0.724), independence-residual co-calling (P = 0.389) or mean pairwise excess covariance (P = 0.205).

5. **Shared environmental activation can therefore increase multispecies calling without detectable restructuring of residual species associations.** Short-window multispecies observations should not by themselves be interpreted as temporal-niche compression, facilitation or pairwise synchrony. The observational design identifies replicated weather associations, not causal rainfall effects.

## Keywords

acoustic community; activation; anurans; ecoacoustics; environmental cue; rainfall; synchrony; weather

## Introduction

Animal communities are organized not only in space and resource use but also in time. Environmental pulses can alter the number of species active at a given moment, and multispecies observations are therefore often interpreted as changes in community synchrony or temporal niche overlap. Yet the same observation can arise without any change in interspecific association. If several species respond independently to the same environmental cue, the probability of observing two or more species in the same short window increases mechanically as their marginal activity probabilities increase.

Frog acoustic communities provide a strong system in which to separate these possibilities. Rainfall and temperature are established drivers of frog calling probability, intensity and breeding phenology. Hsu, Kam and Fellers (2006) found that nightly calling-species richness and maximum calling intensity covaried with rainfall and temperature in a Taiwanese subtropical forest, and Xie et al. (2017) linked community calling activity and richness to recent rainfall. Brodie, Allen-Ankins and Schwarzkopf (2025) further showed that major rainfall events can trigger chorus onset in a tropical savanna assemblage. The question is therefore not whether rain can make more frogs call.

A different mechanistic question is whether a rainfall-associated increase in multispecies calling reflects **broader community activation** or **stronger residual association among species once marginal activity is accounted for**. These alternatives have different ecological meanings. The first implies that a shared cue expands the set of species participating in acoustic activity. The second would imply that co-calling increases beyond that expected from changes in species-specific participation alone. Raw calling-species richness or a binary “one versus multiple species” response cannot distinguish them.

We used two independent monitoring systems to establish the event-level phenomenon and a standardized North American system to decompose it. NAAMP provides repeated 5-min acoustic stops on fixed routes. FrogID provides expert-validated Australian smartphone recordings and an independent weather linkage. We first asked whether recent rainfall predicted a greater probability of observing multiple calling species in each system. We then used NAAMP to ask whether rain increased any-calling activity, expanded the run-level active species pool, changed multispecies calling conditional on at least one species already calling, or changed residual co-calling beyond that expected under within-run marginal independence.

The original analysis programme contained four hypotheses: greater multispecies calling after recent rain (H1), greater multispecies calling at warmer temperatures (H2), stronger rain effects at seasonal sampling shoulders (H3), and rainfall-driven pairwise co-calling network densification (H4). Primary, validation and prespecified secondary endpoints were governed by versioned analysis contracts frozen before their corresponding effect readbacks in the development history. During pre-submission review, we identified a hierarchy defect in the H3 formula and a logical limitation in interpreting conditional multispecies detections. We therefore added explicitly labelled post-opening diagnostics for active-pool richness and marginal-independence residuals; these diagnostics were separately frozen before they were fitted and do not replace the original primary decisions.

## Materials and Methods

### NAAMP data and standardized acoustic response

We used the USGS North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). Analyses were restricted to the unified-protocol period 2001–2015. NAAMP routes comprised repeated wetland-associated stops surveyed acoustically for 5 min. Publisher metadata define CallingIndex values 1–3 as positive calling states.

The primary replication unit was a route-run rather than an individual stop. For each eligible run, we counted sampled non-skipped stops and the subset at which at least two distinct species had positive calling indices. The run-level binomial response avoided treating the approximately 10 stops within a route-run as independent biological replicates.

Publisher metadata define DaysSinceRain as the number of days since the last rain event, with a documented numeric range of 0–180 days and a null code. A pre-submission outcome-blind value audit found 9,401 numeric unified-protocol values and 10,648 null-coded values. Numeric values spanned 0–180 days, none lay outside the documented range, the median was 1 day, the 95th percentile was 7 days and only 11 numeric records exceeded 30 days. Existing primary scripts already excluded non-numeric null codes by numeric parsing; no value recoding was introduced.

### NAAMP primary rain model and weather robustness

The frozen primary predictor was z[log(1 + DaysSinceRain)]. We modelled multispecies-calling stops out of sampled stops using a binomial-logit model with State, RunNumber, RouteType and standardized SurveyYear as fixed adjustments. Standard errors were cluster-robust by State × RouteNumber. The directional prediction was β_rain < 0 because larger DaysSinceRain represents less recent rainfall. Two prespecified sensitivities used complete 10-stop runs and runs with at least eight sampled stops.

Temperature was a prespecified secondary predictor. After source-scale conversion and a predictor-only plausibility filter retaining run mean temperatures from -10 to 45 °C, we fitted a joint rain-plus-temperature model and a robustness model additionally containing a five-degree-of-freedom spline for day of year. These models report both rain and temperature coefficients rather than using temperature only as a separate secondary endpoint.

### FrogID independent event-level validation

FrogID is an Australian citizen-science programme in which smartphone recordings of calling frogs are reviewed by expert validators (Rowley et al., 2019; Rowley & Callaghan, 2020). The analysed source was a SHA-256-pinned Atlas of Living Australia Darwin Core archive (`dr14760.zip`; SHA-256 `f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d`) spanning 10 November 2017 to 9 November 2024 and containing 1,183,011 occurrence rows. Its temporal scope matches the Australian Museum’s seven-year FrogID Dataset 7.0 release (Australian Museum, 2026). The GBIF resource DOI is 10.15468/wazqft.

A deterministic outcome-independent 1/16 eventID sample was frozen before external rainfall values were opened. The final validation contained 40,754 recordings, including 18,174 with at least two calling species, from 13,148 recorders and 1,623 0.25° ERA5 cells. The binary response was whether a recording contained one versus multiple expert-validated calling species. Because FrogID records are presence-only acoustic submissions, every analysed recording already contained at least one calling species. This conditioning controls the trivial “no acoustic activity versus some activity” contrast, but it does **not** rule out the possibility that several species independently increase their marginal calling probabilities after rain.

### ERA5 rainfall linkage

We linked FrogID events to ERA5 hourly total precipitation (Hersbach et al., 2020). Hourly precipitation was assigned to complete local calendar days using the coordinate-derived time zone and interval midpoints. The frozen exposure was the number of consecutive complete local calendar days immediately before the recording date with <1 mm precipitation, capped at 30 days and transformed as z[log(1 + dry days)]. The recording day itself was deliberately excluded, so rainfall earlier on the recording day is not represented in this exposure.

An outcome-blind timing audit found explicit UTC offsets on all 655,502 events in the fixed source snapshot. In the deterministic analysis sample, 40,603/40,754 supplied offsets matched the coordinate-derived time-zone offset exactly; 151 event hours and six local dates changed after coordinate-time-zone conversion. We therefore froze a timing repair before recomputing the FrogID effect: the offset-bearing event timestamp was converted to the coordinate-derived time zone, and the resulting local date and clock hour were used for the rainfall exposure and cyclic-hour adjustment. The FrogID primary model adjusted for state-by-month, calendar year and these repaired cyclic local-hour terms. Standard errors were clustered by ERA5 weather cell; recorder clustering was a prespecified sensitivity. Because NAAMP DaysSinceRain and FrogID ERA5 dry-spell duration are different exposure metrics on different observation designs, their odds ratios were treated as directional replication and were not pooled.

### Within-space diagnostics

After the cross-system rain effects were opened, we froze diagnostics targeted at time-invariant spatial confounding. For NAAMP, run-level multispecies-stop proportion, rainfall exposure, year and sampling-window indicators were demeaned within repeatedly surveyed routes and fitted as a weighted linear-probability model. For FrogID, the one-versus-multiple-species outcome, dry-spell exposure, month indicators, calendar year and event-time cyclic terms were demeaned within 0.25° ERA5 cells. These diagnostics use temporal variation within fixed spatial units; they do not remove time-varying local confounding.

### NAAMP activation decomposition

A mechanism contract was frozen after the original rain endpoint had been opened but before the decomposition was fitted. Using the plausible-temperature subset and the day-of-year-adjusted weather model, we estimated two complementary binomial responses: (1) the number of sampled stops containing at least one positively calling species out of all sampled stops, and (2) the number of stops containing at least two calling species out of stops containing at least one calling species. The first estimates general acoustic activation, whereas the second asks whether rain predicts multispecies calling beyond simply making sampled stops acoustically active.

H4 independently tested whether rainfall changed pairwise co-calling network density among the species available in complete 10-stop runs. The pair universe was defined before the weather effect was opened, and no individual edge effects were selected.

### Pre-submission reviewer-motivated diagnostics

Two additional mechanistic diagnostics were frozen before their own fitting after pre-submission review exposed the distinction between marginal activation and residual association.

First, for complete 10-stop runs with at least eight valid temperature stops, plausible mean temperature and a parseable survey date, we defined **active-pool richness** as the number of distinct positively calling species across the run. We modelled log(1 + active-pool richness) against rain, temperature, a nonlinear day-of-year spline, State, RunNumber, RouteType and SurveyYear with route-clustered standard errors.

Second, for complete runs containing at least two active species, we calculated the observed fraction of stops containing at least two calling species. For each species in the run pool, its within-run marginal calling probability was its fraction of the 10 stops occupied acoustically. Under independence, the expected probability of at least two callers was

P(≥2) = 1 − ∏(1 − p_i) − Σ_i p_i ∏_{j≠i}(1 − p_j).

The primary diagnostic was observed P(≥2) minus this independence expectation. A sensitivity metric averaged, across all species pairs in a run, the observed pairwise co-calling frequency minus p_i p_j. Both residual metrics were regressed against the same rain, temperature, day-of-year and design adjustments. These are reviewer-motivated post-opening diagnostics, not members of the original confirmatory family; the plug-in marginal probabilities are estimated from the same 10 stops and are interpreted accordingly.

### Seasonal-shoulder specification repair

Pre-submission code review identified that the original H3 formula contained rain × shoulder without the lower-order shoulder term. We therefore re-estimated H3 using the hierarchy-corrected model `rain_z * shoulder` together with the original State, RunNumber, RouteType and year adjustments. A four-window-state sensitivity retained the original sampling-window fixed effects, which span the shoulder baseline contrast in that subset. This repair cannot retroactively convert H3 into a preregistered positive result; it tests whether the original “not supported” conclusion changes under a hierarchy-correct specification.

### Ethics and inference boundaries

This study is a secondary analysis of publicly released acoustic-monitoring and citizen-science records. We conducted no new animal capture, handling or field sampling. All estimates are observational associations. Multispecies calling does not identify causal rainfall effects, interspecific facilitation, reproductive success, demographic consequences or fine-scale phase synchronization.

## Results

### Replicated multispecies-calling association

The NAAMP primary analysis included 9,399 route-runs from 900 routes and 93,383 sampled stops; 41,020 stops contained at least two calling species. Greater time since rain was associated with a small decline in multispecies co-calling (β = -0.0312, cluster-robust SE = 0.0151), equivalent to an odds ratio of 0.969 per 1 SD increase in log-transformed DaysSinceRain (95% CI 0.941–0.998, P = 0.0388). The ≥8-stop sensitivity retained the original support rule (P = 0.0431), whereas the complete-10-stop sensitivity was directionally similar but crossed zero narrowly (P = 0.0580).

On the 8,200-run plausible-temperature subset, the rain association strengthened rather than disappearing after temperature adjustment (OR = 0.942, 95% CI 0.913–0.972, P = 1.71 × 10^-4). Adding nonlinear day of year gave OR = 0.946 (95% CI 0.917–0.976, P = 5.44 × 10^-4). Temperature remained positively associated with multispecies calling in the same model (OR = 1.492, 95% CI 1.414–1.574, P = 1.21 × 10^-48).

FrogID independently reproduced the event-level rain direction. After converting each offset-bearing event timestamp into the coordinate-derived time zone, greater antecedent dry-spell duration was associated with a lower probability that an acoustically active recording contained multiple calling species (β = -0.1591, OR = 0.8529, 95% CI 0.8274–0.8793, P = 1.19 × 10^-24). Recorder-clustered inference gave the same conclusion (P = 6.88 × 10^-33). This result establishes independent replication of the multispecies-recording pattern, but the conditional FrogID design alone does not distinguish residual interspecific association from independent increases in species-specific activity.

### Within-space robustness

The rain direction persisted when estimates used temporal variation within fixed spatial units. Within 797 repeatedly surveyed NAAMP routes (9,256 runs), greater time since rain remained negatively associated with multispecies-stop probability (β = -0.01367 on the probability scale, 95% CI -0.01998 to -0.00737, P = 2.15 × 10^-5). Within 1,071 informative FrogID ERA5 cells (40,020 recordings), the analogous timezone-repaired coefficient was β = -0.04262 (95% CI -0.05170 to -0.03354, P = 3.57 × 10^-20). Static geographic differences in species pools are therefore insufficient to explain the replicated direction, although time-varying confounding remains possible.

### Rainfall signal decomposes into activation rather than conditional overlap

The NAAMP decomposition separated general acoustic activation from multispecies calling conditional on activity. Increasing dryness reduced the odds that a sampled stop contained any calling species (OR = 0.904, 95% CI 0.872–0.937, P = 4.63 × 10^-8). By contrast, rain recency had little association with the odds of multiple species conditional on at least one species already calling (OR = 0.988, 95% CI 0.959–1.017, P = 0.402). Restricting to runs with at least five active stops gave the same null rain result (OR = 0.995, P = 0.758).

The post-opening active-pool diagnostic pointed in the same direction. Across 7,848 complete, temperature-qualified runs, more recent rainfall was associated with greater run-level active species richness after temperature and nonlinear seasonal adjustment (β_rain = -0.01872 on the log1p richness scale, 95% CI -0.02857 to -0.00888, P = 1.92 × 10^-4).

Residual association metrics did not increase after recent rain. Across 7,176 runs with at least two active species, the mean observed multispecies-stop probability was 0.4758 and the independence expectation derived from within-run marginal species frequencies was 0.4766. Rain recency did not predict their difference (β = 0.000876, 95% CI -0.00112 to 0.00287, P = 0.389). The mean pairwise excess-covariance sensitivity was likewise null (β = 0.000617, 95% CI -0.000337 to 0.00157, P = 0.205).

Consistent with these continuous diagnostics, the prespecified H4 analysis found no detectable rainfall effect on pairwise co-calling network density conditional on the available species pool (OR = 0.994, P = 0.724; repeated-edge sensitivity P = 0.790). Individual edge effects were not opened.

### Seasonal shoulder remains unsupported

Correcting the lower-order hierarchy in H3 did not change its substantive conclusion. The hierarchy-corrected rain × shoulder interaction was β = -0.0480 (95% CI -0.0999 to 0.00388, OR = 0.953, P = 0.0698). In states with four sampling windows, the interaction was β = 0.0236 (95% CI -0.0719 to 0.119, P = 0.628). Seasonal-shoulder amplification therefore remains unsupported.

## Discussion

Recent rainfall was repeatedly associated with a greater probability of detecting multiple calling frog species in the same short acoustic observation across North American and Australian monitoring systems. Taken alone, that pattern could be described as greater community co-calling. The NAAMP decomposition changes the biological interpretation, however: rainfall was strongly associated with whether stops were acoustically active and with the size of the active species pool, but not with multispecies calling conditional on activity, residual co-calling above marginal independence, pairwise excess covariance or pairwise network density.

This distinction matters because an increase in P(≥2 species) does not require stronger interspecific temporal association. If several species independently increase calling after the same rainfall cue, multispecies observations become more common even when their residual association structure is unchanged. Our results provide an empirical example of that arithmetic distinction at community scale. The raw co-calling signal is real and cross-system, but in the standardized NAAMP data its rainfall component is best characterized as **shared community activation** rather than detectable restructuring of pairwise co-calling.

This interpretation places the study differently relative to prior work. Earlier studies already established rainfall associations with calling-species richness and community activity (Hsu et al., 2006; Xie et al., 2017), and Brodie et al. (2025) demonstrated rainfall-triggered chorus onset. We therefore do not claim novelty for “rain makes more frog species call.” The contribution is the explicit decomposition of a seemingly synchrony-like community response into marginal activation and residual association, combined with an independent continental replication of the raw multispecies pattern. The result warns that event-level species richness or multispecies co-detection can overstate evidence for temporal-niche compression unless the marginal activity process is separated from the association process.

The within-space results further constrain the explanation. Both NAAMP and FrogID retained the rain direction when static route- or weather-cell differences were removed. Thus the replicated pattern is not simply a contrast between wetter, richer places and drier, poorer places. It remains observational, however, and may reflect unmeasured time-varying conditions correlated with recent rain.

Temperature provides an informative secondary contrast within NAAMP. Temperature was strongly associated not only with overall multispecies calling but also with multispecies calling conditional on acoustic activity in the pre-existing decomposition. Rain and temperature therefore need not act through identical community pathways. Because the temperature effect lacks an independent continental validation and was secondary to the rainfall programme, we treat this contrast as hypothesis-generating rather than as a second central conclusion.

The FrogID validation also requires a narrower interpretation than in the original manuscript. Conditioning on recordings with at least one frog calling removes the zero-versus-any-activity contrast, but it does not remove the mathematical consequence of several species independently becoming more active. FrogID therefore validates the event-level one-versus-multiple-species association under a different observation system; it does not independently establish residual synchrony. The standardized NAAMP decomposition is what identifies the activation-dominated interpretation.

Several limitations remain. First, rainfall was not randomized and causal claims are not warranted. Second, a NAAMP 5-min stop is simultaneously a temporal observation window and a spatial sampling station. Multispecies calling therefore combines local co-presence, detectability and temporal activity and is not a pure temporal-niche metric. Third, FrogID is opportunistic and presence-only; submission behaviour can covary with weather even after cell- and recorder-based robustness checks. Fourth, the ERA5 dry-spell metric intentionally excludes the recording day, so same-day rain before an evening recording is not captured. Fifth, the reviewer-motivated active-pool and independence diagnostics were added after the original endpoints had been opened, although their specifications were versioned before those new diagnostics were fitted. The plug-in independence expectation also uses marginal probabilities estimated from the same 10 NAAMP stops. Finally, the NAAMP primary effect is small and one route-completeness sensitivity crosses the conventional significance threshold narrowly; the evidence is stronger as a pattern replicated across systems and supported by within-space analyses than as a claim based on the primary P value alone.

The broader ecological implication is consequently more modest but more general than “rain compresses temporal niches.” Shared environmental cues can increase the number of species observed together without detectably strengthening residual species associations. Community studies should distinguish **participation** from **association** before interpreting multispecies activity as synchrony, facilitation or temporal-niche reorganization.

## Data Availability

NAAMP source data are publicly available from the U.S. Geological Survey data release (Foreman et al., 2017; DOI 10.5066/F7G44NG0). The FrogID analysis used the Atlas of Living Australia `dr14760` Darwin Core archive pinned at SHA-256 `f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d`; the logical FrogID resource is registered under DOI 10.15468/wazqft. The analysed snapshot spans the Dataset 7.0 temporal window described by the Australian Museum (2026). ERA5 is documented by Hersbach et al. (2020).

The standalone analysis repository preserves frozen contracts, source digests, result receipts, analysis scripts and deterministic figure-generation code. Raw third-party source datasets are not redistributed. We intend to archive the submitted reproducibility package in a persistent research repository; the archive identifier will be added at the finalization stage.

## References

Allen-Ankins, S., & Schwarzkopf, L. (2021). Spectral overlap and temporal avoidance in a tropical savannah frog community. *Animal Behaviour*, 180, 1–11. https://doi.org/10.1016/j.anbehav.2021.07.024

Allen-Ankins, S., & Schwarzkopf, L. (2022). Using citizen science to test for acoustic niche partitioning in frogs. *Scientific Reports*, 12, 2447. https://doi.org/10.1038/s41598-022-06396-0

Australian Museum. (2026). *FrogID Dataset 7.0 — Seven years of data, and over 1 million records*. Australian Museum Research Institute. https://australian.museum/blog/amri-news/frogid-dataset-7/

Australian Museum. (2025). *FrogID* [Occurrence dataset]. Global Biodiversity Information Facility. https://doi.org/10.15468/wazqft

Brodie, S., Allen-Ankins, S., & Schwarzkopf, L. (2025). Environmental influences on chorusing patterns in an Australian tropical savanna frog community. *Ecosphere*, 16, e70153. https://doi.org/10.1002/ecs2.70153

Foreman, T., Grant, E. H., & Weir, L. A. (2017). *North American Amphibian Monitoring Program (NAAMP) anuran detection data from the eastern and central United States (1994–2015)* [Data release]. U.S. Geological Survey. https://doi.org/10.5066/F7G44NG0

Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., … Thépaut, J.-N. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146, 1999–2049. https://doi.org/10.1002/qj.3803

Hsu, M.-Y., Kam, Y.-C., & Fellers, G. M. (2006). Temporal organization of an anuran acoustic community in a Taiwanese subtropical forest. *Journal of Zoology*, 269, 331–339. https://doi.org/10.1111/j.1469-7998.2006.00044.x

Rowley, J. J. L., Callaghan, C. T., Cutajar, T., Portway, C., Potter, K., Mahony, S., Trembath, D. F., Flemons, P., & Woods, A. (2019). FrogID: Citizen scientists provide validated biodiversity data on frogs of Australia. *Herpetological Conservation and Biology*, 14, 155–170.

Rowley, J. J. L., & Callaghan, C. T. (2020). The FrogID dataset: expert-validated occurrence records of Australia’s frogs collected by citizen scientists. *ZooKeys*, 912, 139–151. https://doi.org/10.3897/zookeys.912.38253

Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017). An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators*, 82, 13–22. https://doi.org/10.1016/j.ecolind.2017.06.015

## Figure legends

**Figure 1. Independent acoustic systems establish the rainfall-associated multispecies-calling pattern, and NAAMP separates participation from residual association.** NAAMP provides standardized 5-min route-stop surveys and supports decomposition into any acoustic activity, active species-pool richness, conditional multispecies calling and residual co-calling metrics. FrogID provides an independent Australian one-versus-multiple-species validation linked to ERA5 precipitation. Effect sizes are not pooled across systems.

**Figure 2. Rain-recency associations replicate across monitoring systems and persist within spatial units.** Primary logistic associations are shown separately because NAAMP uses programme-reported DaysSinceRain whereas FrogID uses ERA5 antecedent dry days. Within-route and within-ERA5-cell diagnostics use only temporal variation inside fixed spatial units. Negative coefficients indicate more multispecies calling closer to recent rainfall. These are observational associations, not causal estimates.

**Figure 3. NAAMP decomposition attributes the rainfall-associated multispecies signal to broader acoustic participation rather than stronger residual co-calling.** Recent rainfall is associated with the probability that any frog calls and with greater active species-pool richness. Rain does not detectably change multispecies calling conditional on acoustic activity, the observed-minus-independence expectation, mean pairwise excess covariance, or pairwise network density. Reviewer-motivated post-opening diagnostics are identified separately from the original confirmatory and secondary endpoints.
