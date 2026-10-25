# Record-level biological macro audit (after source/facet inventory)
Date 2026-10-25. **Source-feasibility-driven extension**, not a newly blinded preregistration.

## Aim: test whether regional seasonality reflects actual species/site/year distributions
The 15-region source-matched iNaturalist GBIF faceted counts suggest strong differences in phenological stage windows. However regional aggregation over 2015–2025 can conflate year and site turnover, which is especially critical when inferring potential *staged* frog-salamander interactions. This line retrieves original dated, stage-coded **observation-level** records for five North American latitude zones where both egg and larval salamander strata meet a ≥30-record coverage gate in the original inventory:
`US30_35`, `US35_40`, `US40_45`, `US45_50`, `CA45_50`.
Use original live GBIF 2015–2025, identical dataset UUID `50c9509d-22c7-4a22-a47d-8c48425ef4a7`, only original `lifeStage` labels `Anura/Larva`, `Caudata/Egg`, `Caudata/Larva`, `Odonata/Nymph`, plus `Anura/Egg`. Other records or unvalidated labels are excluded. The selection of five bands follows the source coverage inspection; it is exploratory, not representative North America.

## Original observation and geospatial safety
Store `gbifID` (dedup key), year, month, day if recorded, scientificName, speciesKey and **0.5° grid** derived from the GBIF coordinates. Do NOT publish exact occurrence latitude/longitude or treat grid bins as actual pond IDs; an iNaturalist occurrence need not be aquatic or from a monitored pond. Avoid longitude/latitude perturbation for GBIF obscured protected taxa: coarse bin can still carry GBIF location uncertainty.
Checksum each returned API page raw JSON and pin endpoint filters. The 5-region original live endpoints must not silently truncate offset pages or exceed the GBIF 100,000 offset cap. Remove no records based on ecological result sign. Report missing day, taxonomic species-level resolution, and GBIF coordinate uncertainty.

## Locked exploratory analyses
1. **Year-resolved phenological overlap**: within each `region×year` and edge `frog larvae ↔ salamander egg`, `frog larvae ↔ salamander larvae`, calculate the 12-month normalized min-overlap. Only use strata with ≥15 dated observations in both groups and ≥2 nonempty months each. Compare egg-window vs larval-window on the **same region-year** where both are estimable, report count and group-level direction, source effort per month, and year-blocked (not iid observation) sensitivity. Do not infer feeding, hydroperiod or offspring survival.
2. **Spatial–temporal observed concurrence**: for each species-group pair, count how many **0.5° grid × year × month** cells have at least one dated observation of frog larva and the partner stage, and the fraction among frog-larva-positive cells. Report same-grid **only**, not same pond. The absence of a partner record is not a biological nondetection.
3. **Taxon composition**: count distinct speciesKey for each stage and region-year. If a purported pattern is entirely due to a few species/source dates, report limitation and do not generalize to all species.
4. **Sampling bias controls**: stage-label and source heterogeneity cannot be eliminated by identical GBIF dataset selection. No standardized survey effort, observation-platform seasonal visibility or developmental-stage detectability. GBIF year, month and date are records, not actual oviposition/metamorphosis times.

**Stop criteria:** If fewer than 10 `region×year` cells have three-stage ≥15-record coverage, do not claim broad temporal consistency. Always report how many are eligible; do not fill unobserved months as sampled absences or run broad post-hoc species searches to obtain positive results.
