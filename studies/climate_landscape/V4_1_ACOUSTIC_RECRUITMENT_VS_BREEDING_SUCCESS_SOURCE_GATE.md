# v4.1 — From rain-selective chorus-site re-expression to breeding opportunity and success

**Date:** 2026-10-09 (JST). **Scope:** public-source evidence audit and a *prospective* follow-on question, not a new analysis of frog calling responses. **Locked JAE RC6 manuscript and scientific main unchanged.** No new raw frog outcome records, Iowa state-native wet/dry, water-depth logs, individual animal records or approvals retrieved. No emails or archive requests sent.

## 1. Important source discovery: a larger, repeated hydrology × frog dataset has already been analyzed

**Primary empirical reference:** Ocock, J. F., Walcott, A., Spencer, J., Karunaratne, S., Thomas, R. F., Heath, J. T. & Preston, D. (2024), *Managing flows for frogs: wetland inundation extent and duration promote wetland-dependent amphibian breeding success*, *Marine and Freshwater Research* 75, MF23181. [DOI 10.1071/MF23181](https://doi.org/10.1071/MF23181); [publisher HTML](https://connectsci.au/mf/article/75/2/MF23181/194409/Managing-flows-for-frogs-wetland-inundation-extent).

This paper analyzed repeated surveys in 2015–2020 at **29 wetland sites** (**15** Gwydir + **14** Macquarie Marshes), with **343 site surveys across 95 survey nights** and over 11,000 individual frog observations as reported by the authors. The original sampling combined brief 5-minute frog call-category surveys, visual and auditory transects, counts of adult frogs and recently metamorphosed frogs, and in the programme tadpole surveys. Survey timing included September and November each year, subject to site access; a site visit not performed is **missing opportunity**, not a biological zero.

Weather and hydrology covariates included immediate and 1-, 7- and 15-day rainfall, temperature, water depth, satellite-derived local wetland inundation and antecedent river flows (including flows over a **30-day** window), as defined in the original paper. The authors compared 22 predictors with random-forest analyses.

**Already-published biological outcome (not a frogcs result):**
- **Calling index / breeding attempt proxy:** wetland **inundation extent** was the strongest reported predictor, and timing of inundation mattered.
- **Recently metamorphosed frogs / breeding-success proxy:** **preceding-months river flow volume / duration** was especially important, implying a distinct longer exposure timescale for successful recruitment.
- The study describes a **non-monotonic water-depth relationship** for calling, with activity rising to roughly 15 cm and declining at greater depths in its fitted summaries. This is not a universal physiological threshold across species and sites.
- These are **observational predictive associations**; the random-forest variable-importance ranking does not by itself identify causal effects, mediation of rain, or individual reproductive success.

### Compared with Sarker's six-site flow-arrival study

Sarker et al. (2022), [DOI 10.1016/j.ecolind.2022.109640](https://doi.org/10.1016/j.ecolind.2022.109640), had a **six-site short pre/post acoustic component**; the published before/after flow contrast remains inseparable from time in the two-period summary (v4.0 audit). Ocock's **29-site multi-year** dataset addresses a different population-level timescale and includes a distinct recruitment endpoint. It is more suitable as source evidence for the *acoustic activity vs successful recruitment* distinction, **not** automatically a natural experiment or a direct test of the original NAAMP k≥4 site allocation.

**Do not pool or double-count reported programme observations:** the NSW DCCEEW's 2025 statewide [*Evaluation of flow-dependent frog objectives and targets*](https://www.environment.nsw.gov.au/publications/evaluation-flow-dependent-frog-objectives-and-targets), part of 2019–2024 Basin Plan reporting, evaluated Gwydir, Macquarie and Lowbidgee. It builds on monitoring programmes including the one analyzed by Ocock et al. It is **not an independent holdout** simply because it has a different title or reporting period. Its monitoring methods and site-access/selection regimes vary among programmes and years.

## 2. The new *question*, not a newly discovered result

The existing frogcs JAE RC6 result concerns **where historically recurrent strong acoustic activity is expressed** after recent rain:
- directional rain-selective prior-SiteID targeting: β=+0.02449 (95% CI 0.00700–0.04198);
- within-taxon multi-site concentration: 1.6503 observed vs 1.3535 under the principal response+history comparator;
- the held-out rain × historical local-propensity gate alone is insufficient (predicted 1.3323);
- these observations **do not measure eggs, metamorphs, successful reproduction, individual movement or site memories**.

This suggests a scientifically stronger and testable *future* follow-on:

> **Does the rain-selective re-expression of historically strong chorusing sites identify a spatial template of actual reproductive opportunity, or can a strong chorus be a phenological/sensory false positive when inundation is too brief to produce metamorphs?**

**This formulation is a hypothesis.** Ocock already demonstrated that measures relevant to *initiating* calling and *achieving* successful metamorphosis differ. Novelty, if any, would have to come from the **link to strictly prior species × physical-site chorus recurrence and cross-site spatial allocation**, not from reasserting the published difference between rainfall, inundation and breeding success.

### Rival mechanisms and falsifiers

| Proposed generator | Testable prospective signal | What would falsify the simple version? |
| --- | --- | --- |
| **Hydroperiod-encoded site template** | historically strong sites reliably have longer actual wetland hydroperiod; their rain-associated choruses predict later metamorphs better than current wetness alone | after adequately measured wetness and year/site effects, historical-site indicator has no reproducible out-of-block prediction for metamorphs |
| **Fast auditory/social trigger without lasting habitat** | verified animal calls increase acutely near rain/chorus sounds but downstream eggs/metamorphs remain low where local wetlands dry rapidly | a controlled, independent cue exposure produces no calling response with adequate detection and baseline availability |
| **Broad-night activation × local reproductive filter** | shared species-night calling state recruits across multiple sites, but subsequent recruitment is concentrated at sites with adequate inundation duration | independent full-vector calling, water and recruitment predictions are explained just as well by additive local-site and event-level factors, with residual spatial dependence absent |

No mediator can be declared causal from observational conditioning on post-rain wetness or on observed post-treatment active-site number k. Separate **randomized causal outcomes** from **conditional-k spatial generator prediction** (see v3.6).

## 3. Exact data grain needed — this is the blocker to an empirical result

The minimum independent target panel is **species × immutable physical wetland × survey event**, with *separate* linked post-event follow-up for metamorphs. It needs:

1. **Prior baseline:** historical actual animal-produced CI or comparable call categories for each taxon×physical site, built strictly before evaluation windows. Missing history = not classifiable, not historical weakness.
2. **Event/cue:** rain timing and quantity, calibrated rain-sound/flow-sound exposure if testing sensory cues, local wetland water depth and inundation onset/area, plus temperature/time-of-night.
3. **Acoustic response:** actual visit survey opportunity, a comparably coded calling index, known masked/skipped/no-observer outcomes, detection/observer calibration, and verified independent ponds or acoustic clusters.
4. **Downstream success:** eggs/tadpoles/metamorphs with follow-up dates, stage-specific detectability, and a hydroperiod measure spanning larval development. **Adult calling and a metamorph observed months later need not originate from the same breeding event without additional life-history/source assumptions**.
5. **Spatial allocation:** multiple independent wetlands on the same cue/event window, so there are both recurrent and less-recurrent *available* sites. Compare matched-k placement only as an out-of-block **predictive** quantity, not a direct causal effect.
6. **Exposure comparison:** some ponds receive water without contemporaneous local rain; some experience rain without local wetting; genuinely comparable unwatered reference sites. Rain and flow must not always be aliased with calendar progression.
7. **Independent held-out blocks:** whole future water events / wetland regions / years, not repeated samples from the same source programme treated as separate replications.

Source availability gates: original Ocock raw **site-visit table, metadata dictionary, water/inundation series, true visit opportunities and breeding-stage linkages** have not been retrieved by this audit. The public journal HTML and NSW report validate the **published study**, not full raw-data accessibility or an external pre-specified validation cohort. A separate request would require user direction; no contacts were made.

## 3B. An actual data path is named in the paper — but it is not the required joint panel

A useful source-access clarification was found in the *original Ocock et al. (2024) article*, under **Data availability**:

> Frog survey records are available through NSW BioNet; ancillary data are available on request.

These are **two distinct retrieval routes**. Current official NSW documentation confirms:

1. [NSW BioNet Species Sightings public access](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/species-sightings-data) allows unauthenticated browsing and public-exported sightings. BioNet records include taxa, observation dates and some mapped sites, subject to coordinate generalisation for sensitive fauna. The [BioNet read-only OData service](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/web-services) exposes the actual [public service document](https://data.bionet.nsw.gov.au/biosvcapp/odata), including `SpeciesSightings_CoreDataExtended` and `SpeciesSightings_AdditionalMeasurementsOrFacts`, but **not a separately named Systematic Fauna Survey entity set**. Crucially, the [February 2026 API release notes](https://www.environment.nsw.gov.au/publications/bionet-web-service-release-notes-february-2026) explain that `CoreDataExtended` is the **first release for integrating systematic flora and fauna survey records in the Species Sightings service**. Thus absence of a standalone fauna entity name is **not evidence that no fauna survey observations are exposed**; exact survey-event opportunity/completeness, call categories and hydrology linkage remain unverified.
2. [NSW BioNet Systematic Fauna Survey data](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/systematic-fauna-survey-data) requires **login access for analysis/export**. Even if original sightings were included in a public species search, such records do **not automatically include the surveyed-but-silent wetland visits, full audio categories or individual follow-up records needed to infer acoustic transitions**.
3. The Ocock article's **ancillary hydrology/exposure inputs are on request**, not asserted as publicly linked by a stable `species×site×event` key. Do not silently convert a BioNet occurrence/nonoccurrence list into a repeated survey panel, and do not infer missing survey dates are biological absences.
4. BioNet specifically **redacts or coarsens locations of sensitive species**. A coordinate-coarsened sighting cannot be joined to centimetre-scale water depth, stop-specific historical CI or an immutable physical wetland simply by geographic nearest-neighbour matching.

**Decision:** the *species observation access route is now located and verified*, but a complete joined frog-calling × water-depth × antecedent hydroperiod × metamorph table is **NOT retrieved or verified**. The first actionable step for a separate future study is a **schema-only audit of public BioNet species sightings**, without claiming a joint hydro-ecological source; if the necessary survey opportunity and metadata keys are not there, the raw nonpublic ancillary records would require a separately authorised request to the data custodian. No emails, paid requests, login bypasses, original results or source data were accessed.

## 4. Sampling/selection biases the public sources warn about

- **Water-dependent observation:** inundation may change which wetlands can be visited; not surveyed ≠ calling zero or no offspring. Test whether missing survey probability depends on site wetness/season, and never use imputed zeros to boost hydrology effects.
- **Programme/site reuse:** Ocock 2015–2020, Sarker's surveys, and NSW 2025 synthesis share geographic monitoring systems and, potentially, site-years; one cannot count these as three independent sets of biological replications.
- **Outcome scales differ:** frogcs/NAAMP ordinal CI 0–3; Ocock ordinal ‘rare/common/abundant/very abundant’; Sarker timed chorusing; acoustic PAM number of events; subsequent tadpoles/metamorphs. Requires documented measurement crosswalk, not an assumed single standardized calling index.
- **Site-history collider:** historically stronger sites may already have more frogs or better habitat; history moderation does not prove memory, occupancy, phenotypic adaptation or a direct site-cue effect.
- **Hydrologic temporal confounding:** rainfall can initiate calls while a water-filled pond persists for months; regional flow and season are not randomized. Report prediction before attributing individual causal pathways.

## 5. Honest decision

**Confirmed now:** there are source-documented, repeated, more-than-six-site studies in Australia with **both acoustic breeding-attempt and actual metamorph follow-up information**, and they show different environmental predictive timescales. These facts make an additional project on **spatial memory of chorus opportunities vs real breeding payoffs** conceptually well-motivated.

**Not confirmed:** any accessible row-level independent frog × wetland × night dataset that both recreates RC6's multiple simultaneous physical-site configurations and has strictly prior site acoustic history plus downstream metamorphs. Nor do the existing publications isolate random water, immediate rain sound, and full before/after controls.

**Next operational stop:** do not write another fitted frog effect or call this a new finding. First establish whether raw site-event hydrology+calling+offspring outcomes can be accessed with fixed site IDs and adequate contemporaneous controls; if no, retain v3.7's independently designed Stage-0 monitoring as the proposed empirical route.

## Sources

- [Ocock et al. 2024 (publisher)](https://doi.org/10.1071/MF23181).
- [Sarker et al. 2022 (publisher)](https://doi.org/10.1016/j.ecolind.2022.109640).
- [NSW DCCEEW 2025 official synthesis (programme information)](https://www.environment.nsw.gov.au/publications/evaluation-flow-dependent-frog-objectives-and-targets).
- [The Sound of Water, Nap Nap Swamp, multi-sensor example](https://doi.org/10.1177/14744740231197813) — an existing 9-day managed-flow hydrology/audio visualisation, **not** multi-pond randomized exposure or raw open dataset by itself.
- frogcs internal observed estimates are those already frozen in `paper/manuscript.md` and `paper/supporting_information.md`; no new NAAMP analysis.
