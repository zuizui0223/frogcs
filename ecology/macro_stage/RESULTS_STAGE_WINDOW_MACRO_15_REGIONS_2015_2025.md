# Ecological macro result: developmental stage shifts the seasonal availability of potential amphibian antagonists
**2026-10-25 | REAL GBIF RECORDS | exploratory macro phenology, not witnessed predation**

## Research question and biological conclusion
The same frog tadpole cannot encounter a salamander as an egg or an aquatic larva unless the relevant stages are seasonally available in the same landscape. We measured how 2015–2025 **stage-annotated occurrence phenology** differed between these potential antagonistic life stages, rather than doing another literature survey or NAAMP method audit.

**MAIN NEW DESCRIPTIVE RESULT:** At a broad northern-temperate scale, **frog aquatic larvae have more seasonally overlapping occurrence distributions with salamander aquatic larvae than with salamander eggs**. The comparison is consistent across five prespecified North American latitude bands when using the same GBIF iNaturalist publisher. Importantly the pattern also persists in record-level, year-stratified and equal-species-weighting checks. This **suggests** that possible larva–larva encounters have a broader timing window than possible tadpole–salamander-egg encounters in sampled landscapes. It is **not evidence** that either interaction actually occurred, that salamanders eat frog tadpoles or that wood frogs damage eggs at the original GBIF observation locations.

## Original ecological dataset and measurement grain
- GBIF Orders: `Anura=952`, `Caudata=953`, `Odonata=789`, independently confirmed through live GBIF species match. Original coordinate-bearing GBIF records **2015–2025**. Initial source counts: **5,466,222** frogs, **1,221,755** salamanders, **9,764,002** odonates. These are observations, **not individual abundance or random aquatic samples**.
- Aquatic stage source facet counts across all publishers: frog Egg **30,183**; frog Larva **38,628** + Tadpole **5,867**; salamander Egg **9,551**, salamander Larva **28,231**; odonate Larva **17,809** + Nymph **14,084**. Strongly uneven annotation and taxonomic coverage.
- Primary source restricted to one publisher and annotation system, **iNaturalist Research-grade Observations**, original GBIF dataset UUID `50c9509d-22c7-4a22-a47d-8c48425ef4a7`, to avoid mixing frog photographs with NEON benthic insect monitoring. Same publisher does **not** mean standardized stage-photo observation effort or equal ecological detectability.
- 15 fixed latitude/country bands in USA, Canada, Europe, Japan and Australia. Only regions with **≥30 stage-coded coordinate records** and ≥2 nonempty observed months per stage are considered estimable. Australia contains no sampled Caudata egg stage in these bands; zero availability is **not a zero biological interaction**.
- Coarse regional phenology: monthly counts normalized to within-stage observation totals. Stage-pair overlap `O = Σ_month min(p_stageA, p_stageB)` ∈ [0,1]. Adjusted sensitivity is based on stage-specific month counts divided by *all records of the same taxonomic order in that month* with 0.5 pseudocount. Neither is measured pond-scale interaction opportunity.

## All 15-region sample: ecological stage-window differences
| Macro guild pair (potential stage encounter) | Regions with sufficient source records | Mean `O` (equal region) | Seasonal-effort proxy adjusted mean |
|---|---:|---:|---:|
| Frog larvae × salamander eggs | **5** | **0.42856** | **0.53435** |
| Frog larvae × salamander larvae | **9** | **0.70381** | **0.63517** |
| Frog larvae × odonate aquatic nymphs | **12** | **0.70769** | **0.45547** |

These **different eligible-region sets cannot be compared as if they were a matched experiment**. The odonate stage window changes greatly with seasonal-effort adjustment; **do not claim a universal dragonfly predator guild effect from these statistics**. Original all-publisher results are separately archived as detection-platform sensitivity, not primary ecology.

## Matched-region comparison, key novel ecological contrast
All three target frog/salamander stage groups had adequate records in exactly five North American latitude bands (US 30–35, 35–40, 40–45, 45–50°N; Canada 45–50°N).
- In all **5/5** bands, the frog-larva × salamander-larva raw monthly overlap exceeded the frog-larva × salamander-egg overlap. Equal-region paired mean difference **+0.351** on a 0–1 overlap scale.
- A within-order seasonal-observation-effort proxy reduced the paired difference to **+0.154** and **4/5** bands positive. This loss of full agreement is explicitly retained, not omitted.
- **Original iNaturalist observation-level rows were then obtained**, not just GBIF facets: **21,979** dated, stage-tagged observations from five bands, 2015–2025. 5 original source CSV SHA256 receipts and raw API-page hashes preserved; *original precise coordinates were NOT redistributed*, only 0.5-degree spatial bins, original stage label, year/month, species identifiers and GBIF occurrence IDs.

### Actual year-resolved result, not an artifact of pooling 11 years
Among **37 region×year** combinations with ≥15 original records in each frog-larva, salamander-egg and salamander-larva group and observations spanning ≥2 months each:
- **37/37** have frog-larva × salamander-larva monthly overlap > frog-larva × salamander-egg monthly overlap.
- Average paired raw stage-window difference: **+0.292244**.
- Each of the five latitude bands contributes positive results in all its eligible years: US30–35 **6/6**, US35–40 **10/10**, US40–45 **10/10**, US45–50 **5/5**, Canada45–50 **6/6**. However **37 region-years are nested, not 37 independent communities**, and there is no valid independent-subject p-value.

### Nontrivial test: control for the seasonal width/phase of each original stage distribution
A narrow egg-stage season will mechanically overlap less with a broad larval season even if the stage centroids are similarly located. Thus, after inspecting the first results, an explicitly **exploratory** 12-calendar-month circular phase-shift benchmark was applied: for each year×region pair, `O_excess = O_observed - mean_{shift=0..11} O_shift`. Then compare `O_excess(lavra–salamander larva) - O_excess(frog larva–salamander egg)`. This preserves each observed stage's seasonal width/shape and changes only its relative phase; circular shifts are an artificial reference, **not** a biological causal null.
- Phase-adjusted difference positive in **31/37** eligible region×years, average **+0.134369**, median **+0.124231**.
- Phase-adjusted *region-year mean* positive in **all 5/5** bands: US30–35 +0.0603; US35–40 +0.0979; US40–45 +0.0761; US45–50 +0.3612; Canada45–50 +0.1772.
- No p-value or precision interval for original ecological interaction is claimed from this post-hoc phase exercise.

### Separate species-composition sensitivity
Within each region, count only original `taxonRank=SPECIES` records for each unique speciesKey with ≥10 GBIF stage records spanning ≥2 months. Normalize that species' own monthly observations to sum to 1, then average equally across qualifying species, rather than allowing a few heavily photographed species to dominate.
- All **5/5** latitude bands have ≥3 qualifying species for each of frog larvae, salamander eggs and salamander larvae.
- **5/5** bands retain the larva–larva > larva–egg overlap; **5/5** retain the positive difference after the 12-month phase reference.
- Qualifying species per guild vary by band (frog larvae **8–16**, salamander eggs **3–8**, salamander larvae **4–19**). Species non-detection and photographic selectivity remain serious limitations.
- Source code uses an explicitly **post-result** sensitivity; this is not an independent replication.

### Positive spatial co-observation, without inventing shared ponds
At 0.5° × 0.5° × year × month observation bin level across five source-matched regions, frog aquatic larvae were recorded in **2,969** grid-year-month cells. Of these, **417 (14.0%)** additionally contain a salamander-larva observation and **275 (9.3%)** contain a salamander-egg observation. This is **co-recording at roughly 50-km landscape scale, not co-occurrence in the same wetland**; unequal source frequency affects these fractions.

## What we can and cannot infer
**Supported new macro-scale pattern:** seasonal stage availability and potential cross-stage antagonistic opportunity are structured; larva–larva guild overlap exceeds larva–egg overlap in the same source, place/time strata and equal-species check. This is not yet a demonstration of developmental-stage-mediated **predation strength** or realised network-edge switching. In particular, adult frog calling can precede actual eggs and larvae unpredictably.

**Unresolved confounding:** opportunistic iNaturalist image submissions, missing lifeStage labels, rarity/missed capture of salamander eggs, yearly species composition, time-varying sampling effort, latitude bin heterogeneity, coordinate obscuring, egg vs larva phase-duration differences, and unmeasured ponds/water/canopy. Stage-width correction strengthens plausibility but does not eliminate selection.

**Next ecological discriminator:** use original pond × date stage census data to test whether the regional larval-coavailability pattern predicts actual same-pond larval encounters and predation or offspring survival when salamander egg/larval timing and hydroperiod are measured. Existing Mohonk pond-year series, independent of NAAMP, supplies one source for egg/tadpole stage detections; a larger pond-level sample is needed to link geographic macro pattern to trophic consequences.

## Reproducibility
- Initial [GBIF all-source 15 regional matrix run 40149175967](https://github.com/zuizui0223/frogcs/actions/runs/40149175967) plus [pilot run 40149080917](https://github.com/zuizui0223/frogcs/actions/runs/40149080917).
- Primary [shared iNaturalist 15-region source run 40149401485](https://github.com/zuizui0223/frogcs/actions/runs/40149401485).
- [Full 15-region macro overlap run 40149611064](https://github.com/zuizui0223/frogcs/actions/runs/40149611064), original stage availability tables and response URL checksums.
- [Original 21,979 observation fetch run 40150013130](https://github.com/zuizui0223/frogcs/actions/runs/40150013130).
- [Original species/year/coarse-grid ecological analysis run 40150271511](https://github.com/zuizui0223/frogcs/actions/runs/40150271511).
- [Species-balanced and phase-reference analysis run 40150588455](https://github.com/zuizui0223/frogcs/actions/runs/40150588455).
- Code: `ecology/macro_stage/scripts/probe_gbif_stage.py`, `run_gbif_region.py`, `analyze_gbif_macro.py`, `harvest_gbif_observations.py`, `analyze_gbif_observations.py`, `macro_species_phase_sensitivity.py` and tests.
- The paper-ready macro figures, source receipts and original coarsened observations are also exported as downloadable, inspectable data products in this conversation. All development is isolated in `research/macro-stage-interactions-2026-10`; frozen `main` untouched.
