# Macro ecology: amphibian and odonate life-stage phenology (2015–2025)

## Actual ecological result — 25 October 2026

**Stage identity changes the seasonal availability of potential amphibian antagonists.** Using **21,979 original, dated, species/stage-annotated iNaturalist observations** archived through GBIF from five North American latitude zones, frog larval timing overlapped more with salamander **larval** timing than salamander **egg** timing in **37/37 eligible region×years** (mean 12-month overlap difference **+0.292** on the [0,1] scale).

The pattern remained directionally positive in **31/37** region-years after a 12-month circular timing-shift reference (mean **+0.134**) and in **5/5** geographic bands when qualifying species rather than individual photo observations were weighted equally. These are **post-result exploratory sensitivities**, not independent replications. The 37 region-year cells are repeated observations nested in only five geographical strata.

At a coarser **0.5° grid×year×month** scale, frog larvae were documented in **2,969** cells. **417 (14.0%)** also recorded salamander larvae, while **275 (9.3%)** recorded salamander eggs. This means *co-reporting at landscape scale*, not the same pond or direct interactions. Missing species records do not indicate sampled biological absence.

The first broad original GBIF facet audit covered **15 regions** across North America, Europe, Japan and Australia. Matched-source stage coverage permitted a frog larva–salamander egg index in 5 regions, frog larva–salamander larva in 9, and frog larva–odonate nymph in 12. Because eligible strata differ across comparisons, the principal interpretable ecological contrast uses the **same five North American bands and years**. Dragonfly larval phenology is especially sensitive to uneven aquatic-insect collection and photo-reporting methods; do **not** claim a macro dragonfly predation result.

**Critical biological boundary:** guild-level seasonal stage occurrence is **potential exposure opportunity only**. It does not demonstrate predation, direct competition, life-stage transition dates for the same individual, actual tadpole/salamander coexistence in a pond, or reproductive consequences. iNaturalist life-stage labels and monthly seasonal sampling are opportunistic, even within one original GBIF dataset.

## Research record and reproducing the actual analysis

- [Detailed primary macro-results report](RESULTS_STAGE_WINDOW_MACRO_15_REGIONS_2015_2025.md).
- [Source/biological comparisons fixed before regional results](STUDY_PROTOCOL_BEFORE_REGIONAL_COUNTS_2026-10-25.md) and [observation-level extension](RECORD_LEVEL_STAGE_WINDOW_AUDIT_PROTOCOL_2026-10-25.md).
- [GBIF facet stage data source (15 matched-publisher bands)](https://github.com/zuizui0223/frogcs/actions/runs/40149401485).
- [Macro 15-region overlaps and publisher-method sensitivity](https://github.com/zuizui0223/frogcs/actions/runs/40149611064).
- [Actual original observation-level source harvest, 5 geographical bands](https://github.com/zuizui0223/frogcs/actions/runs/40150013130).
- [Same year / 0.5-degree-grid original-species macro result](https://github.com/zuizui0223/frogcs/actions/runs/40150271511).
- [Species-balanced and circular-month phase sensitivity](https://github.com/zuizui0223/frogcs/actions/runs/40150588455).

Primary code: `scripts/harvest_gbif_observations.py`, `scripts/analyze_gbif_observations.py`, `scripts/macro_species_phase_sensitivity.py`. All source URL SHA256s, monthly counts, taxon, period, region and source-dataset filters were preserved; original exact coordinates were reduced to 0.5° bins in the downloadable analysis package.

This research branch is intentionally separate from the **frozen Journal of Animal Ecology RC6** on `main`. No original NAAMP CallingIndex/Counts data were used in these macro calculations.

## Biological next discriminator (not yet measured)

To test **true stage-dependent trophic network rewiring**, link the macro egg/larval timing pattern to *same-pond × date* direct predator-prey data across many ecosystems and include hydroperiod, canopy/wetland plants, predator stage sizes and observed egg/tadpole survival. A macro time-overlap index by itself is not a signed food-web edge. The independently analysed Mohonk egg/tadpole co-detection series illustrates possible overlap in natural pools but does not contain actual predation measurements.
