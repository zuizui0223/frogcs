# Recent rainfall predicts broader frog acoustic participation without stronger residual co-calling associations

## Abstract

1. **Environmental pulses can increase multispecies detections by broadening participation across sampling units or by changing species multiplicity and residual association within active units.** These mechanisms are not equivalent, and multispecies detections alone cannot distinguish them.

2. **We separated these components in standardized North American frog surveys and used Australian FrogID recordings as an external, differently conditioned contrast.** The NAAMP primary response included all sampled 5-min stops, whereas every FrogID recording already contained at least one calling species and therefore estimates a one-versus-multiple-species contrast conditional on acoustic activity.

3. **Rainfall associations depended on that conditioning.** In 9,399 NAAMP runs, increasing time since rain reduced overall multispecies calling (OR = 0.969, 95% CI 0.941–0.998), and the association remained after temperature and nonlinear day-of-year adjustment (OR = 0.946, 95% CI 0.917–0.976). Among 40,754 already-active FrogID recordings, increasing antecedent dry-spell duration strongly reduced the odds of multiple callers (OR = 0.853, 95% CI 0.827–0.879). By contrast, the analogous NAAMP activity-conditioned effect was null (OR = 0.988, 95% CI 0.959–1.017).

4. **Within NAAMP, the rainfall signal was concentrated in participation breadth.** Increasing dryness reduced the odds that a stop contained any caller (OR = 0.904) and reduced run-level active species richness (β = -0.0187), but did not detectably change residual co-calling under plug-in independence, a fixed-marginal shuffle null, pairwise excess covariance or network density.

5. **Thus, standardized monitoring showed more active sampling units and a broader active species pool after recent rain without evidence for stronger within-active-unit association.** The contrasting FrogID conditional effect shows that activity-conditioned multiplicity can differ among systems or observation processes. Multispecies detections should therefore not be interpreted as synchrony or temporal-niche reorganization without separating participation from association.

## Keywords

acoustic community; activation; anurans; ecoacoustics; environmental cue; participation; rainfall; weather

## Introduction

Environmental pulses can change community observations through several distinct pathways. A pulse may increase the number of sampling units in which any species is active, expand the set of species participating across a survey, increase the number of species within already-active units, or alter residual association among species after their marginal activity is accounted for. All of these can increase raw multispecies detections, but they imply different ecological processes.

Frog acoustic communities provide a useful system in which to make this distinction. Rainfall and temperature are established drivers of frog calling probability, intensity and breeding phenology. Hsu, Kam and Fellers (2006) found that nightly calling-species richness and maximum calling intensity covaried with rainfall and temperature in a Taiwanese subtropical forest, Xie et al. (2017) linked community calling activity and richness to recent rainfall, and Brodie, Allen-Ankins and Schwarzkopf (2025) showed rainfall-triggered chorus onset in a tropical savanna assemblage. The question is therefore not whether rain can increase frog acoustic activity.

The unresolved community-level question is **where an increase in multispecies detections enters the observation process**. In a standardized route survey, recent rain could make more stops acoustically active and thereby expose a broader run-level species pool, even if the number of species within an already-active stop and residual cross-species alignment do not change. Alternatively, rain could increase multiplicity within active sampling units or strengthen co-calling beyond marginal activity frequencies. This distinction parallels broader work separating shared environmental responses from residual multispecies association or synchrony (Royan et al., 2016; Swallow et al., 2016).

We used two monitoring systems with importantly different conditioning. NAAMP provides repeated standardized 5-min stops on fixed North American routes and therefore observes both inactive and active sampling units. FrogID provides expert-validated Australian smartphone recordings that are present by construction only when at least one frog species was recorded. Consequently, the FrogID one-versus-multiple-species response is closer to the **activity-conditioned** NAAMP component than to the unconditional NAAMP primary endpoint. We used NAAMP to decompose rainfall associations into stop-level acoustic participation, run-level active species-pool breadth, species multiplicity within active stops and residual co-calling. We used FrogID as an external contrast asking whether the activity-conditioned component has the same direction in a distinct biological and observation system.

The original analysis programme contained four hypotheses: greater multispecies calling after recent rain (H1), greater multispecies calling at warmer temperatures (H2), stronger rain effects at seasonal sampling shoulders (H3), and rainfall-driven pairwise co-calling network densification (H4). Original primary, validation and prespecified secondary endpoints were governed by versioned analysis contracts committed before their corresponding effect readbacks. During pre-submission review, we identified a hierarchy defect in the H3 formula and a logical limitation in treating different observation-conditioning schemes as direct replications. We therefore added explicitly labelled post-opening diagnostics for active-pool richness, marginal-independence residuals and a fixed-marginal shuffle null; these diagnostics were separately frozen before their own fits and do not replace the original primary decisions.

## Materials and Methods

## Materials and Methods

### NAAMP data and standardized acoustic response

We used the USGS North American Amphibian Monitoring Program data release for the eastern and central United States (Foreman, Grant, & Weir, 2017; DOI 10.5066/F7G44NG0). Analyses were restricted to the unified-protocol period 2001–2015. NAAMP routes comprised repeated wetland-associated stops surveyed acoustically for 5 min. Publisher metadata define CallingIndex values 1–3 as positive calling states.

The primary replication unit was a route-run rather than an individual stop. For each eligible run, we counted sampled non-skipped stops and the subset at which at least two distinct species had positive calling indices. The run-level binomial response avoided treating the approximately 10 stops within a route-run as independent biological replicates.

Publisher metadata define DaysSinceRain as the number of days since the last rain event, with a documented numeric range of 0–180 days and a null code. A pre-submission outcome-blind value audit found 9,401 numeric unified-protocol values and 10,648 null-coded values. Numeric values spanned 0–180 days, none lay outside the documented range, the median was 1 day, the 95th percentile was 7 days and only 11 numeric records exceeded 30 days. Existing primary scripts already excluded non-numeric null codes by numeric parsing; no value recoding was introduced.

### NAAMP primary rain model and weather robustness

The frozen primary predictor was z[log(1 + DaysSinceRain)]. We modelled multispecies-calling stops out of sampled stops using a binomial-logit model with State, RunNumber, RouteType and standardized SurveyYear as fixed adjustments. Standard errors were cluster-robust by State × RouteNumber. The directional prediction was β_rain < 0 because larger DaysSinceRain represents less recent rainfall. Two prespecified sensitivities used complete 10-stop runs and runs with at least eight sampled stops.

Temperature was a prespecified secondary predictor. After source-scale conversion and a predictor-only plausibility filter retaining run mean temperatures from -10 to 45 °C, we fitted a joint rain-plus-temperature model and a robustness model additionally containing a five-degree-of-freedom spline for day of year. These models report both rain and temperature coefficients rather than using temperature only as a separate secondary endpoint.

### FrogID activity-conditioned cross-system contrast

FrogID is an Australian citizen-science programme in which smartphone recordings of calling frogs are reviewed by expert validators (Rowley et al., 2019; Rowley & Callaghan, 2020). The analysed source was a SHA-256-pinned Atlas of Living Australia Darwin Core archive (`dr14760.zip`; SHA-256 `f5dd70ed07956e3e37de4fb04692b83a9d726eae2312767c9eda2dcbf61f759d`) spanning 10 November 2017 to 9 November 2024 and containing 1,183,011 occurrence rows. Its temporal scope matches the Australian Museum’s seven-year FrogID Dataset 7.0 release (Australian Museum, 2026). The GBIF resource DOI is 10.15468/wazqft.

A deterministic outcome-independent 1/16 eventID sample was frozen before external rainfall values were opened. The final analysis contained 40,754 recordings, including 18,174 with at least two calling species, from 13,148 recorders and 1,623 0.25° ERA5 cells. The binary response was whether a recording contained one versus multiple expert-validated calling species.

Every analysed FrogID event already contained at least one caller because FrogID is a presence-only acoustic-submission system. Its estimand is therefore explicitly **conditional on acoustic activity**. Conceptually, this is closer to the NAAMP probability of multiple callers among active stops than to the NAAMP primary probability of multispecies calling across all surveyed stops. The observation units, sampling processes and rainfall metrics still differ, so the corresponding coefficients are compared qualitatively rather than treated as estimates of one common parameter.

### ERA5 rainfall linkage

We linked FrogID events to ERA5 hourly total precipitation (Hersbach et al., 2020). Hourly precipitation was assigned to complete local calendar days using the coordinate-derived time zone and interval midpoints. The frozen exposure was the number of consecutive complete local calendar days immediately before the recording date with <1 mm precipitation, capped at 30 days and transformed as z[log(1 + dry days)]. The recording day itself was deliberately excluded, so rainfall earlier on the recording day is not represented in this exposure.

An outcome-blind timing audit found explicit UTC offsets on all 655,502 events in the fixed source snapshot. In the deterministic analysis sample, 40,603/40,754 supplied offsets matched the coordinate-derived time-zone offset exactly; 151 event hours and six local dates changed after coordinate-time-zone conversion. We therefore froze a timing repair before recomputing the FrogID effect: the offset-bearing event timestamp was converted to the coordinate-derived time zone, and the resulting local date and clock hour were used for the rainfall exposure and cyclic-hour adjustment. The FrogID primary model adjusted for state-by-month, calendar year and these repaired cyclic local-hour terms. Standard errors were clustered by ERA5 weather cell; recorder clustering was a prespecified sensitivity. Because NAAMP DaysSinceRain and FrogID ERA5 dry-spell duration are different exposure metrics on different observation designs, their odds ratios were treated as directional replication and were not pooled.

### Within-space diagnostics

After the cross-system rain effects were opened, we froze diagnostics targeted at time-invariant spatial confounding. For NAAMP, run-level multispecies-stop proportion, rainfall exposure, year and sampling-window indicators were demeaned within repeatedly surveyed routes and fitted as a weighted linear-probability model. For FrogID, the one-versus-multiple-species outcome, dry-spell exposure, month indicators, calendar year and event-time cyclic terms were demeaned within 0.25° ERA5 cells. These diagnostics use temporal variation within fixed spatial units; they do not remove time-varying local confounding.

### NAAMP activation decomposition

A mechanism contract was frozen after the original rain endpoint had been opened but before the decomposition was fitted. Using the plausible-temperature subset and the day-of-year-adjusted weather model, we estimated two complementary binomial responses: (1) the number of sampled stops containing at least one positively calling species out of all sampled stops, and (2) the number of stops containing at least two calling species out of stops containing at least one calling species. The first estimates general acoustic activation, whereas the second asks whether rain predicts multispecies calling beyond simply making sampled stops acoustically active.

H4 independently tested whether rainfall changed pairwise co-calling network density among the species available in complete 10-stop runs. The pair universe was defined before the weather effect was opened, and no individual edge effects were selected.

### Pre-submission reviewer-motivated diagnostics

Two additional mechanistic diagnostics were frozen before their own fitting after pre-submission review exposed the distinction between participation breadth and residual association.

First, for complete 10-stop runs with at least eight valid temperature stops, plausible mean temperature and a parseable survey date, we defined **active-pool richness** as the number of distinct positively calling species across the run. We modelled log(1 + active-pool richness) against rain, temperature, a nonlinear day-of-year spline, State, RunNumber, RouteType and SurveyYear with route-clustered standard errors. This measures acoustic participation across a route-run; it is not local occupancy richness.

Second, for complete runs containing at least two active species, we calculated the observed fraction of stops containing at least two calling species. For each species in the run pool, its within-run marginal calling probability was its fraction of the 10 stops at which that species called. Under independence, the plug-in expected probability of at least two callers was

P(≥2) = 1 − ∏(1 − p_i) − Σ_i p_i ∏_{j≠i}(1 − p_j).

The primary residual diagnostic was observed P(≥2) minus this expectation. A second metric averaged, across all species pairs in a run, the observed pairwise co-calling frequency minus p_i p_j. Both residual metrics were regressed against the same rain, temperature, day-of-year and design adjustments.

As a finite-sample sensitivity, we also used a **fixed-marginal shuffle null**. Within each eligible 10-stop run, each species’ binary stop-presence vector was independently permuted across stop labels 1,024 times using a deterministic RunID-based seed. This preserved exactly the number of positive stops for every species, the 10-stop run size and the active species pool while destroying cross-species alignment to particular stops. For each run we subtracted the mean shuffled probability of ≥2 callers from the observed probability and regressed that residual against the same weather and design terms.

These are reviewer-motivated post-opening diagnostics, not members of the original confirmatory family. The plug-in expectation estimates marginals from the same 10 stops, while the shuffle null destroys shared stop identity; persistent stop-level habitat or detectability heterogeneity can therefore contribute to observed shuffle excess.

### Seasonal-shoulder specification repair

Pre-submission code review identified that the original H3 formula contained rain × shoulder without the lower-order shoulder term. We therefore re-estimated H3 using the hierarchy-corrected model `rain_z * shoulder` together with the original State, RunNumber, RouteType and year adjustments. A four-window-state sensitivity retained the original sampling-window fixed effects, which span the shoulder baseline contrast in that subset. This repair cannot retroactively convert H3 into a preregistered positive result; it tests whether the original “not supported” conclusion changes under a hierarchy-correct specification.

### Ethics and inference boundaries

This study is a secondary analysis of publicly released acoustic-monitoring and citizen-science records. We conducted no new animal capture, handling or field sampling. All estimates are observational associations. Multispecies calling does not identify causal rainfall effects, interspecific facilitation, reproductive success, demographic consequences or fine-scale phase synchronization.

## Results

### Rainfall associations under different observation conditioning

The NAAMP primary analysis included 9,399 route-runs from 900 routes and 93,383 sampled stops; 41,020 stops contained at least two calling species. Greater time since rain was associated with a small decline in multispecies calling across all surveyed stops (β = -0.0312, cluster-robust SE = 0.0151), equivalent to an odds ratio of 0.969 per 1 SD increase in log-transformed DaysSinceRain (95% CI 0.941–0.998, P = 0.0388). The ≥8-stop sensitivity retained the original support rule (P = 0.0431), whereas the complete-10-stop sensitivity was directionally similar but crossed zero narrowly (P = 0.0580).

On the 8,200-run plausible-temperature subset, the NAAMP rain association remained after temperature adjustment (OR = 0.942, 95% CI 0.913–0.972, P = 1.71 × 10^-4). Adding nonlinear day of year gave OR = 0.946 (95% CI 0.917–0.976, P = 5.44 × 10^-4). Temperature remained positively associated with multispecies calling in the same model (OR = 1.492, 95% CI 1.414–1.574, P = 1.21 × 10^-48).

FrogID estimated a different, activity-conditioned response. After timezone-aware event-time repair, greater antecedent dry-spell duration was associated with a lower probability that an already-active recording contained multiple calling species (β = -0.1591, OR = 0.8529, 95% CI 0.8274–0.8793, P = 1.19 × 10^-24); recorder-clustered inference gave the same conclusion (P = 6.88 × 10^-33).

The closest NAAMP analogue to this FrogID estimand was the probability of multiple callers among stops already containing at least one caller. That NAAMP coefficient was near zero (OR = 0.988, 95% CI 0.959–1.017, P = 0.402). The two systems therefore do **not** replicate one another for the activity-conditioned component. Instead, they show that a rain association with multiplicity among already-active observations can depend on biological system, exposure definition, detectability or observation process.

### Within-space robustness

Within each system’s own estimand, the rain direction persisted when static spatial differences were removed. For NAAMP’s all-stop multispecies response, within 797 repeatedly surveyed routes (9,256 runs), greater time since rain remained negatively associated with multispecies-stop probability (β = -0.01367 on the probability scale, 95% CI -0.01998 to -0.00737, P = 2.15 × 10^-5). For FrogID’s activity-conditioned one-versus-multiple-species response, within 1,071 informative ERA5 cells (40,020 recordings), the timezone-repaired coefficient was β = -0.04262 (95% CI -0.05170 to -0.03354, P = 3.57 × 10^-20).

These results show that static geographic differences alone are insufficient to explain either system-specific association. They do not make the NAAMP and FrogID estimands equivalent, and time-varying confounding remains possible.

### NAAMP rainfall signal reflects broader participation across stops

The NAAMP decomposition localized the rainfall signal to participation breadth. Increasing dryness reduced the odds that a sampled stop contained **any** calling species (OR = 0.904, 95% CI 0.872–0.937, P = 4.63 × 10^-8). Across 7,848 complete, temperature-qualified runs, increasing dryness was also associated with lower run-level active species richness after temperature and nonlinear seasonal adjustment (β = -0.01872 on the log1p richness scale, 95% CI -0.02857 to -0.00888, P = 1.92 × 10^-4). Thus recent rain was associated with acoustic activity occurring across more standardized route-stops and with a broader set of species participating somewhere in the run.

By contrast, species multiplicity **within already-active stops** did not detectably change with rain (OR = 0.988, 95% CI 0.959–1.017, P = 0.402; active-stops ≥5 sensitivity OR = 0.995, P = 0.758). For scale context, the adjusted all-stop rain effect on the same dryness scale was OR = 0.946; that value lies outside the activity-conditioned 95% CI. This comparison is descriptive rather than a formal additive decomposition because the denominators differ, but it shows that the conditional analysis had precision to exclude an activity-conditioned odds-ratio effect as large as the adjusted all-stop effect.

Residual association diagnostics were more tightly bounded on the probability scale. Across 7,176 runs with at least two active species, the mean observed multispecies-stop probability was 0.4758 and the plug-in independence expectation was 0.4766. Rain recency did not predict their difference (β = 0.000876, 95% CI -0.00112 to 0.00287, P = 0.389). The same-direction lower 95% bound (-0.00112 per SD dryness) is about 8% of the magnitude of the within-route all-stop coefficient (-0.01367); this is a descriptive precision comparison, not a formal equivalence test because the models and subsets differ. Mean pairwise excess covariance was likewise null (β = 0.000617, 95% CI -0.000337 to 0.00157, P = 0.205).

The fixed-marginal shuffle sensitivity gave nearly the same result. Observed multispecies-stop probability averaged 0.47575 versus a shuffled mean of 0.47668 after preserving every species’ exact within-run stop frequency. Rain did not predict observed-minus-shuffled co-calling (β = 0.000933, 95% CI -0.00110 to 0.00296, P = 0.368). The prespecified H4 analysis was also null for pairwise co-calling network density conditional on the available species pool (OR = 0.994, P = 0.724; repeated-edge sensitivity P = 0.790). Together, these analyses provide no detectable evidence that recent rain strengthens residual co-calling within standardized NAAMP runs.

### Seasonal shoulder remains unsupported

Correcting the lower-order hierarchy in H3 did not change its substantive conclusion. The hierarchy-corrected rain × shoulder interaction was β = -0.0480 (95% CI -0.0999 to 0.00388, OR = 0.953, P = 0.0698). In states with four sampling windows, the interaction was β = 0.0236 (95% CI -0.0719 to 0.119, P = 0.628). Seasonal-shoulder amplification therefore remains unsupported.

## Discussion

The standardized NAAMP data locate the rainfall-associated multispecies signal more precisely than a raw co-calling interpretation. Recent rain was associated with a greater probability that a 5-min stop contained any caller and with a broader run-level active species pool. In contrast, the number of species within already-active stops and multiple residual-association diagnostics changed little with rain. The most direct description is therefore **broader participation across standardized sampling units**, not rainfall-driven strengthening of within-stop species association.

This distinction matters because raw multispecies detections combine several processes. More stops can become acoustically active, different species can participate across different stops, and species can change how often they co-occur within the same active stop. NAAMP supports the first two components after recent rain but not the third. We therefore avoid describing the mechanism as species-level “independent activation” in a strict probabilistic sense: our data show broader stop-level acoustic participation and run-level pool breadth, not the latent activation probability of each species independently.

FrogID provides an informative contrast rather than a direct replication. Every FrogID recording is already conditioned on at least one calling species, and its strong rain association (OR = 0.853) therefore concerns multiplicity **within active observations**. The closest NAAMP conditional estimand was null (OR = 0.988). This discrepancy is biologically and methodologically meaningful rather than something to average away. Possible explanations include selective submission of more conspicuous multispecies choruses in FrogID, weather-dependent detectability or chorus intensity, differences between programme-reported DaysSinceRain and the ERA5 antecedent-dry-day exposure, and genuine differences in community composition or breeding strategies. The present data cannot distinguish these explanations. The central cross-system lesson is therefore not a common conditional effect, but that observation conditioning must be made explicit before multispecies responses are compared.

This revised interpretation also changes the novelty boundary. Earlier studies already established rainfall associations with calling-species richness and community activity (Hsu et al., 2006; Xie et al., 2017), and Brodie et al. (2025) demonstrated rainfall-triggered chorus onset. Our contribution is the decomposition of an apparently synchrony-like community response in standardized monitoring into participation breadth versus within-active-unit and residual association. This provides an acoustic-community example of a broader issue in multispecies ecology: shared environmental responses can make species appear together without implying strengthened residual association (Royan et al., 2016; Swallow et al., 2016).

The null residual results are also more informative than P values alone suggest, although they should not be called proofs of equivalence. The NAAMP activity-conditioned OR was 0.988 with a 95% CI of 0.959–1.017, which excludes the adjusted all-stop OR of 0.946 on the same dryness scale. On the probability scale, the independence-residual CI extended only to -0.00112 in the same direction as the within-route all-stop coefficient of -0.01367, roughly 8% of its magnitude. A fixed-marginal shuffle null produced an almost identical bound (-0.00110). Because these diagnostics use different response constructions and, for the probability-scale comparison, different subsets, the ratios are descriptive precision statements rather than formal equivalence tests. Still, they make a large residual component comparable to the observed within-route total association difficult to reconcile with the data.

The within-space analyses further constrain spatial confounding without resolving the conditioning discrepancy. NAAMP retained its all-stop rain association within fixed routes, while FrogID retained its activity-conditioned association within fixed ERA5 cells. Static differences among wetter and drier locations are therefore insufficient explanations within either design, but unmeasured time-varying conditions remain possible.

Temperature provides an additional contrast within NAAMP. Temperature was strongly associated not only with overall multispecies calling but also with multispecies calling conditional on acoustic activity in the pre-existing decomposition. Rain and temperature therefore need not operate through identical observed community components. Because temperature lacks an independent external comparison under the same design and was secondary to the rainfall programme, we treat this contrast as hypothesis-generating.

Several limitations remain. Rainfall was not randomized and causal claims are not warranted. A NAAMP 5-min stop is simultaneously a temporal window and a spatial sampling station, so the response mixes local co-presence, detectability and temporal activity. FrogID is opportunistic and presence-only, and recording or submission probability may covary with chorus conspicuousness and weather. Its ERA5 metric excludes the recording day, so same-day rain before an evening recording is not represented. The reviewer-motivated active-pool, independence-residual and shuffle diagnostics were added after original endpoints had opened, although their own specifications were versioned before fitting. The plug-in independence expectation estimates marginal probabilities from the same 10 stops; the shuffle null preserves marginal frequencies but destroys shared stop identity, so persistent stop-level habitat or detectability heterogeneity contributes to observed excess. Finally, the original NAAMP effect is small and the complete-10-stop sensitivity crosses the conventional significance threshold narrowly.

The broader ecological implication is consequently specific but generalizable: **an increase in multispecies activity can be generated by broader participation across sampling units without detectable strengthening of residual species association, and the apparent conditional component can differ among monitoring systems.** Community studies should therefore separate participation, observation conditioning and association before interpreting multispecies activity as synchrony, facilitation or temporal-niche reorganization.

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

Royan, A., Reynolds, S. J., Hannah, D. M., Prudhomme, C., Noble, D. G., & Sadler, J. P. (2016). Shared environmental responses drive co-occurrence patterns in river bird communities. *Ecography*, 39, 733–742. https://doi.org/10.1111/ecog.01703

Swallow, B., King, R., Buckland, S. T., & Toms, M. P. (2016). Identifying multispecies synchrony in response to environmental covariates. *Ecology and Evolution*, 6, 8515–8525. https://doi.org/10.1002/ece3.2518

Xie, J., Towsey, M., Zhu, M., Zhang, J., & Roe, P. (2017). An intelligent system for estimating frog community calling activity and species richness. *Ecological Indicators*, 82, 13–22. https://doi.org/10.1016/j.ecolind.2017.06.015

## Figure legends

**Figure 1. NAAMP and FrogID estimate rainfall associations under different observation conditioning, while NAAMP supports mechanistic decomposition.** NAAMP includes inactive and active standardized 5-min route stops and can separate any-stop activity, run-level active species-pool breadth, species multiplicity within active stops and residual co-calling. FrogID contains only acoustically active submitted recordings and therefore estimates a one-versus-multiple-species contrast conditional on activity. The two coefficients are not treated as estimates of one common parameter.

**Figure 2. Rain-recency associations persist within spatial units, but the system-specific estimands differ.** NAAMP shows the all-stop multispecies association and its within-route diagnostic. FrogID shows the activity-conditioned one-versus-multiple-species association and its within-ERA5-cell diagnostic. Negative coefficients indicate fewer multispecies observations with increasing dryness. These are observational associations and are not pooled across systems.

**Figure 3. NAAMP decomposition localizes the rainfall signal to participation breadth rather than stronger within-active-unit or residual co-calling.** Recent rain is associated with a greater probability that a standardized stop contains any caller and with greater run-level active species richness. Rain does not detectably change multispecies calling conditional on activity, plug-in independence residuals, a fixed-marginal shuffle residual, mean pairwise excess covariance or pairwise network density. Reviewer-motivated post-opening diagnostics are identified separately from original endpoint families.

