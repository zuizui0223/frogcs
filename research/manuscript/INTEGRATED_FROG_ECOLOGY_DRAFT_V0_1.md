# Rainfall-linked chorus configuration and developmental-stage observations in amphibian wetland communities

**frogcs integrated working manuscript — v0.1, 2026-10-26.**  
**Status:** Draft assembled from existing measured and independently auditable results, **not submission-ready**. Original Journal of Animal Ecology RC6 article remains fixed, with its **stand-alone submission deferred** by the later dated editorial decision. The current scientific programme targets a **single integrated paper** but does not yet identify a unifying predator-stage mechanism. See [editorial authority](../INTEGRATED_PAPER_DECISION_2026-10-26.md), [integration contract](../ONTOGENETIC_LEGACY_INTEGRATION_MASTER_V1.md), and [source inventory](../PART2_POND_STAGE_SOURCE_INVENTORY_2026-10-26.md).

## Candidate title and central question

**Working title:** *From rainfall-associated chorus organization to aquatic life-stage records: testing the limits of a unified amphibian wetland response model.*

**Central question:** When environmental conditions allow amphibians to become reproductively active, how much of the observed species-selective distribution of adult calling and subsequent aquatic life-stage records can be explained by recurring location-specific use, observation processes, local water state, and the developmental composition of interacting species?

**Hypothesis status:** Past predator-stage legacies may alter future prey reproduction and survival, but that pathway remains **unmeasured in the same wetlands** in the presently eligible source data. The acoustic-site-to-larval-stage bridge is an empirically testable *transition in records*, not a validated trophic mechanism.

## Working abstract (measured findings and explicit ceiling)

Rainfall-associated changes in amphibian calling may include more than the total amount of acoustic activity: the spatial arrangement of responses could retain species- and location-specific structure. We examined adult calling in the North American Amphibian Monitoring Program (NAAMP) and evaluated whether independent temporal calling histories and same-site developmental-stage records offer an empirical bridge toward a wetland community mechanism. In 4,236 matched NAAMP wetter–drier comparisons, conditions with recent rain were associated with switching into stronger chorus states. Among 2,916 comparisons with strictly preceding site histories, observed within-taxon multi-stop concentration was 1.6503, compared with 1.3535 from a matched model accounting for taxon-specific rainfall response, earlier site use, dry-state persistence, and total wet-state activity (residual +0.2969; simulated P = 0.000999). Independently monitored NPS recorders showed recurring species-specific strong acoustic use of fixed locations, but an exploratory previous-year green-frog to next-year wood-frog suppression prediction was unsupported (adjusted coefficient +0.0143; approximate 95% interval −0.0691 to +0.0977). Two Flemish INBO sampling-event datasets shared 96 original site identifiers. For *Hyla arborea*, 245 source-site-year pairs linked a previously observed adult chorus with a later explicitly surveyed larval stage. Adding the earlier acoustic observation improved site-held-out Brier loss from 0.2582 to 0.2427, but worsened a 2024–2025 temporal evaluation from 0.2784 to 0.3479. Because the matched records do not measure predator-stage abundance, prey cohort survival, or local water permanence, we cannot attribute NAAMP spatial structure to aquatic predation or infer general acoustic-to-larval transfer. Together, the results delineate observable spatial and cross-stage patterns while identifying the site-resolved developmental and hydrological observations required for a mechanistic explanation.

**Abstract release gate:** The above is a truthful working synthesis, **not** an acceptable causal-mechanism headline, and does not constitute an independent pooled effect-size analysis.

## 1. Introduction

Seasonal rainfall and water availability can release constraints on amphibian reproductive activity, but a change in recorded chorus magnitude does not by itself describe **where** individuals call, **which taxa** activate, or what becomes of the resulting eggs and larvae. In wetlands, aquatic cohorts may persist across seasons; when new eggs and early larvae enter a water body, resident large larvae, fishes, odonate nymphs, and salamanders may act as consumers, competitors, or sources of behavioral cues. Species and life stages can thus occupy different positions in a food web over the course of a year.

The central empirical obstacle is **observation at different life stages**. Calling indices are male adult acoustic activity, not counts of eggs, metamorphs, or predator larvae. The absence of calling does not prove species absence, nor does a detection at a listening stop uniquely identify a pond. Temporal asymmetry in acoustic associations is likewise compatible with persistent habitat differences, survey timing, and species-specific phenology, without any interspecific feeding effect.

This study integrates results at three **non-equivalent evidence levels** rather than pooling incomparable effect estimates. We first use the frozen NAAMP analysis to identify conditional acoustic spatial structure. We then test whether separate NPS acoustic histories show the particular asymmetric suppression expected under a simple overwintering-predator proxy. Finally, we evaluate source-linked adult and later larval monitoring in a second independent geography, asking whether an earlier chorus supplies incremental **out-of-site and out-of-time** information about a later larval report.

### Predictions, specified versus observed

1. **P1: Adult acoustic configuration is not a uniform route-wide activation.** The taxon-specific allocation of strong chorusing retains excess multi-stop concentration after the pre-established acoustic history, rain-response, dry persistence and activity-magnitude comparator. **Observed in locked RC6**; it is a spatial acoustic claim only.
2. **P2: A putative overwinterer’s prior calling suppresses the following year's smaller spring-breeder chorus.** Specifically green frog → wood frog, with the reverse compared separately. **Not supported in exploratory NPS data.** This negative test does not falsify measured egg consumption in other experimental studies.
3. **P3: An earlier adult chorus adds held-out information about later same-species larval detection at the identical source-monitoring location.** **Mixed in the eligible INBO *Hyla arborea* data**: modest improvement at unseen stations, deterioration on later years. Not an identified recruitment or survival relation.
4. **P4: Directly observed resident predator-stage biomass/size modifies subsequent prey egg–larval fate, especially across independently documented drying and refilling.** **Not tested** because no qualified same-pond exposure–outcome–water-state panel has passed the gate. This is a future discriminating study, not a result section.

## 2. Methods

### 2.1 Study units and evidence separation

**NAAMP (Part I, frozen).** The original [RC6 paper](../../paper/manuscript.md), [supporting information](../../paper/supporting_information.md), and [machine-readable results](../../provenance/CURRENT_RESULTS.json) are the source of truth. The full NAAMP material comprises 21,934 run rows, 219,340 stop records, and 337,848 positive call records, with filters specified in the original analyses. The matched set includes 4,236 wetter–drier route/night comparisons, 585 routes and 53 taxon labels. The focal prior-history-eligible comparisons number 2,916. The original simulation estimator and all observation restrictions remain unchanged. The sampling units are **sequential roadside acoustic listening stops**, not synchronized individual ponds.

**NPS GLKN (adult-acoustic cross-lag, exploratory).** The [public GLKN source](https://doi.org/10.57830/2320505) contains 147,913 scored species-by-recording rows from 66 stations in seven parks over 2016–2023. In the [completed fixed design](../NPS_GREEN_FROG_WOOD_FROG_ACOUSTIC_CROSSLAG_SPEC_2026-10-26.md), the leading same-station contrast was prior-year strong green frog (*Lithobates clamitans*) chorus to current strong wood frog (*L. sylvaticus*) chorus, with exactly previous-calendar-year exposure and own-species history. Fixed park×year and physical-station effects and measured prior/current recording effort were represented. Missing source species–year recordings were not filled as biological zeros. The endpoint is annual maximum Calling Index at least 2; it is **not** tadpole presence or survival. Station-cluster CR1 intervals are approximate.

**INBO Meetnetten.be (adult-to-larval recorded stage, exploratory).** The Flemish [adult chorus CC0 archive](https://doi.org/10.15468/d4bu8j) and [larvae/metamorph CC0 archive](https://doi.org/10.15468/swgure) were retrieved from their original IPT sampling-event DwC-A ZIPs and checked by SHA-256. We joined records using the publisher-generated **exact `locationID`**, source `eventID`, taxon and survey date, not geospatially generalized 1/5/10-km coordinates. Source-blind pre-outcome eligibility audits found 96 shared original location IDs and 247 source-site-year combinations with an adult chorus event preceding a larval census. Of two taxon candidates selected before opening response outcomes, *H. arborea* had 245 taxon-specific pairs over 93 sites; *Pelobates fuscus* had only two and was declared non-estimable.

For *Hyla*, the binary predictor was any explicitly recorded adult chorus presence prior to the first qualifying census of the same species’ `larva` stage at the same original location/year; the outcome was that first larval census’s published `occurrenceStatus` present versus absent. Unscored species–event combinations and missing survey cells were **not imputed as absences**. Source locality labels were compared and no conflicting shared-site labels were identified. The matched sample contained 149 recorded larval presences and 96 recorded larval absences, versus 212 prior-chorus presences and 33 explicit non-calling observations.

**INBO predictive comparisons.** M0 included year, census day of year, lag since last adult chorus survey, and number of prior adult surveys; M1 added a single prior-chorus binary indicator. Both used 245 identical rows and a 5-fold location-grouped logistic regression with pre-declared fixed regularization. Brier and logarithmic scores were calculated from held-out-source-site predictions. A secondary forward-time test trained on data through 2023 and evaluated 2024–2025 (35 rows in 34 sites). The working script's old key `M0_time_hydrology_recording` is **only an internal identifier**: the entire eligible INBO sample lacked the measured `permanente waterkolom` value, so **no local hydroperiod term was fitted**. Larval effort categories were reported only for 165/245 eligible records, without a comparable numeric larval sampling-effort denominator; this limits interpretation. Bootstrap uncertainty over sites conditions on already fitted out-of-fold predictions.

### 2.2 Planned, but not estimable, mechanism test

The substantive mechanism requires a single verified wetland-by-season panel of: independently observed hydroperiod and dry-down/refill, large/overwintering predator or competitor larvae with size and abundance, target egg/young-larval cohorts with effort-adjusted survival or recruitment, habitat refuge/vegetation, and ideally direct predation trials. Future environmental baseline M0 would compete with M1 measured stage distribution and M2 stage × hydroperiod interaction. A simple same-year acoustic association or literature edge is not a substitute for measured trophic exposure, and an egg's subsequent death cannot directly cause the earlier spring adult chorus of the same cohort.

Original source audit [results](../results/part2_g0/observed_source_eligibility.json): ESGR amphibian workbook and St Marks fish–wetland workbook were publicly listed but direct workbook downloads returned HTTP 401 in the execution environment; Mohonk EDI original paired water/species files returned HTTP 403. A Mohonk GBIF occurrence mirror was readable but lacked the original pool ID and environment/call/egg details needed for same-pool joining. No G2 effect is estimated from these files.

## 3. Results

### 3.1 Adult chorus configuration (RC6, locked)

Recent-rain comparisons were associated with a transition from low/silent to stronger chorus states. Within the 2,916 comparisons with sufficient prior physical-site history, observed concentration C was **1.650320** versus a comparator expectation of **1.353466**, leaving a conditional residual of **+0.296854** (null interval −0.131854 to +0.118708, plus-one Monte Carlo P = 0.000999). Strictly preceding same-taxon use at a site predicted its subsequent strong call allocation (β = **+0.151094**, 95% CI +0.129127 to +0.173061). The RC6 comparator included route-cross-fitted species rainfall responses, previous species × physical-stop propensities, dry-state persistence and matched aggregate wet activity. The residual therefore **does not mean no wetland habitat covariates or local biotic processes remain**, because they were not directly observed.

### 3.2 Same-species acoustic persistence and unsupported directional proxy (NPS)

In the independent NPS monitoring system, previously strong species-specific site calling predicted future strong acoustic reports even after broad water-permanence category, other taxa's historical acoustic-site use and recording effort (historical-site adjusted coefficient **+0.464188**, 95% park×taxon block-bootstrap interval +0.382566 to +0.533079). This is a distinct annual acoustic estimand from the NAAMP within-route residual.

In the separately registered exploratory previous-calendar-year comparison, the prior green frog call → current wood frog strong-call association was **+0.014321** (n=431 site-years, 66 sites, seven parks; approximate station-cluster 95% interval **−0.069083 to +0.097725**), **not supporting the predicted negative suppression**. The reverse (prior wood frog → current green frog call) was **+0.118120** (approximate interval +0.007131 to +0.229109), but the two outcomes and differing detection phenology do not establish asymmetric trophic causation. We neither revisited the RC6 estimator nor searched alternative lags after this result.

### 3.3 Verified same-site cross-stage records and predictive transport (INBO)

Original INBO event-type data provided an independent, physically publisher-keyed contrast. Among 245 eligible *Hyla* site-year observations at 93 source locations, the earlier adult chorus improved location-group held-out **Brier 0.258227 → 0.242712** (improvement +0.015515; site-balanced bootstrap 95% interval +0.001122 to +0.044649), and **log loss 0.718755 → 0.693772** (improvement +0.024983; bootstrap 95% interval −0.007941 to +0.096251). These are conditional prediction diagnostics, not offspring survival.

The independent **later-year 2024–2025 validation** went in the other direction: adding the chorus predictor **worsened** Brier **0.278392 → 0.347862** and logarithmic loss **0.750606 → 1.009153**. Thus the focal acoustic record was not a stable out-of-time improvement under this frozen model. Because the eligible INBO stage events lacked measured local water persistence and predator-stage status, this experiment does not discriminate the aquatic interaction hypothesis from habitat, timing, or sampling processes.

### 3.4 The missing mechanistic estimate

No eligible dataset yet measures the requisite **same-waterbody hydrology × overwintering predator-stage pressure × target egg/larval cohort fate** triplet at comparable times. The effect of a verified predator-induced dry-down reset, the predator-prey stage-size mismatch, and the fraction of the NAAMP multi-stop concentration attributable to these mechanisms are **not estimable**. Earlier artificial stage-network coexistence and reciprocal-feeding scenarios remain simulation demonstrations, not independent field observations.

## 4. Discussion

The combined record establishes a distinguishable **pattern of adult acoustic spatial organization** that persists beyond the first-order comparator evaluated in RC6, while placing strong limits on mechanistic explanations from other datasets. NPS's same-species acoustic history corroborates recurrence of species-specific recording locations across a different network, but the simple acoustic signature expected if resident green frog larvae systematically suppressed later wood frog calling was not observed. This negative result should constrain, not provoke a search for more favorable predictor species or windows.

The INBO observation link is a genuine advancement over unconstrained GBIF spatial co-occurrence: adult and larval data are tied to identical publisher site identifiers and ordered survey dates, and the target species and explicit absence statuses are observed rather than inferred. Yet held-out future years showed **deterioration** when a prior adult acoustic covariate was added. An interpretation in which past calling is a universally stable proxy for breeding success, juvenile survival, or a resident underwater predator layer would therefore be unsupported.

A future integrated mechanism result will require a contrast capable of distinguishing at least three causes: **persistent species-specific habitat suitability**, **time-varying physical water state**, and **directly measured developmental-stage interactions**. Informative negative evidence is equally valuable: if measured water state explains most of a new study's co-occurrence or next-stage responses without a predator-stage contribution, the ecological explanation should shift toward environmental filtering rather than retroactively reading predation into the NAAMP residual.

### Causal inference and observation caveats

- NAAMP's sequential stops may detect multiple ponds and lack egg, tadpole, fish, odonate/salamander or exact local pond-water measurements.
- NPS's annual maximum Calling Index depends on acoustic effort and species' recording season. Its β estimates cannot be pooled with NAAMP's route-scale concentration or INBO's log-loss gains.
- INBO matches source observation-location identifiers, not individually tracked mating pairs or clutches. Explicit stage-specific `absent` means not recorded under a sampling protocol, **not guaranteed demographic absence**.
- Direct predator/prey feeds, stage-specific biomass flux and contemporary egg survival were never observed in the matched INBO data. A stage-network synthesis supported only by literature or synthetic parameters is **hypothesis generation**, not a field-validated mechanism.
- The combined manuscript should avoid overstating "synchrony": the NAAMP route is visited sequentially, while INBO larval sampling occurs on subsequent dates, not at the instant of calling.

## 5. Conclusion and next evidence gate

Rain-linked amphibian adult activity contains a species-selective spatial structure, and same-site adult and aquatic-stage observations can be linked in real independent monitoring systems. But neither a previous year's other-species calling nor a limited, nontransferable within-species acoustic-to-larval classifier identifies the developmental interactions needed to explain that structure. The overarching ecological mechanism remains an **open, falsifiable question**. The final integrated paper should be evaluated for submission only after a new measured pond-stage–hydroperiod–prey-fate contrast passes the dated research gates, or after an explicit editorial decision to adopt a narrower source-supported question.

## Table 1. Evidence matrix / claim ownership

| Scientific component | Source | Source observation unit | Measured result | Permitted inference |
|---|---|---|---|---|
| Adult acoustic spatial structure | NAAMP RC6 | species × route/stops × matched run | C 1.6503 versus comparator 1.3535; residual +0.2969 | Conditional species-level multi-stop organization, not inter-pond predation |
| Fixed-site acoustic recurrence | NPS GLKN | taxon × recorder station × year | Adjusted own-history +0.4642 | Reproducible association of calls with earlier species-specific sites |
| Putative predator-history suppression | NPS GLKN | taxon × recorder station × year | Green frog→wood frog +0.0143; predicted negative not supported | Absence of that specific detectable adult-acoustic suppression signature |
| Cross-stage reporting opportunity | INBO original event archives | exact source site × species × year | 96 shared source IDs, 245 *Hyla* eligible pairs | Observed possibility of original location-keyed stage comparisons |
| Cross-stage acoustic forecast | INBO *H. arborea* | taxon × exact source location × year | Site held-out small gain; later-year deterioration | Context-dependent predictive record link, not biological survival |
| Predator-stage × water reset × prey fate | qualified data not yet available | true pond × stage × cohort × date | Not estimable | No empirical mechanistic or causal statement |
| Seasonal three-guild mechanism | frogcs synthetic stage-network scripts | artificial model world | Assumption-sensitive scenario outcomes | Model plausibility only; no field support |

## Reproducibility and references

**Original data and own analyses:** [NAAMP RC6 locked scientific results](../../provenance/CURRENT_RESULTS.json); [NPS strict historical-site readout](../results/nps_glkn_history/observed_results.json) and [cross-lag negative finding](../results/nps_stage_crosslag/REPORT.md); [INBO full G0 provenance](../results/part2_g0/observed_source_eligibility.json), [taxon eligibility](../results/part2_g0/inbo_species_time_eligibility.json), and [empirical G1 estimates](../results/part2_inbo_hyla_g1/observed_results.json); [qualifying source matrix](../PART2_POND_STAGE_SOURCE_INVENTORY_2026-10-26.md).

**External sources:** [NPS GLKN DOI:10.57830/2320505](https://doi.org/10.57830/2320505); [INBO chorus DOI:10.15468/d4bu8j](https://doi.org/10.15468/d4bu8j); [INBO larvae DOI:10.15468/swgure](https://doi.org/10.15468/swgure); [ESGR Dryad DOI:10.5061/dryad.js47k](https://doi.org/10.5061/dryad.js47k); [Mohonk source](https://doi.org/10.15468/dypfbs); [St Marks Dryad DOI:10.5061/dryad.jp34d](https://doi.org/10.5061/dryad.jp34d). Data originating at distinct physical wetlands were never silently merged into a single causal cohort panel.

**Versioned publication policy:** [one-paper editorial decision dated 2026-10-26](../INTEGRATED_PAPER_DECISION_2026-10-26.md). Submission readiness is **FALSE**; editorial checkpoint currently proposed 2027-01-31. RC6 scientific artefacts remain immutable and restorable.
