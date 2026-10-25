# Full-global GloBI × GBIF developmental-stage interaction ecology: audited results

**Date 2026-10-25 — new dominant research endpoint for frogcs research branch only.**
Source analyses are independent of the RC6 JAE scientific lock. This document reports **actual data results** and distinguishes *database source links*, *stage-by-place-by-month reporting opportunities*, *general phenology* and *predation-specific mechanisms*.

## Executive finding

**Global species×life-stage reporting has rich, seasonally structured spatial coincidence, but these data have not established an excess that is robustly specific to known predator-prey partners.** For a mechanistic macroecological conclusion, stage/guild-matched partner comparisons and synchronized wetland hydrology/emergent plant structural data are critical. Avoid treating same-country species presence, GBIF same-cell recording, or GloBI co-indexed relations as observed attacks.

## 1. Pinned complete GloBI food-web — no longer the former API first-page screen

[Full GloBI data receipt](../globi_fixed_full_foodweb/observed_results.json) from GloBI **2026-09-10 v0.11**, [DOI 10.5281/zenodo.22691479](https://doi.org/10.5281/zenodo.22691479), file MD5 `8212776b7ba0c4fa8de26a00b5ce8595`, 2,375,721,521 bytes:

- **24,453,954 original indexed records** inspected.
- **77,720** focal food-web rows with amphibians, odonates and diving beetles, **28,958 distinct named directed pairs**.
- **1,835** focal raw rows with a GloBI label for both predator and prey stage; raw label ≠ a valid unambiguous stage.
- Full-source stage QA: **114** self-species stage rows excluded; **481** distinct non-self rows with unknown/noncanonical stages excluded; 23 contained explicitly mixed/ambiguous stage strings (these are tracked within stage-exclusion QA; do not sum independently as non-overlapping); **1,240 certain, non-self, explicitly stage-labelled source rows**, **881 unique named directed stage patterns** involving **768 directed species pairs**.
- **29 different-species pairs** have directed staged links both ways in the eligible source data. They are only *candidate reciprocal database relationships*. They are not independently confirmed predation-role reversals; some derive from one curated inferred food web. **Not 29 independent ecological events**.
- Source DOI richness is extremely limited (3 distinct source dataset DOIs among 1,240 stage-labelled records), despite hundreds of reference strings; a reference string is not an independent replicated food web.

[Full-source × GBIF first controlled join](../full_globi_2026_stage_gbif_grid/observed_results.json) | [successful run](https://github.com/zuizui0223/frogcs/actions/runs/40193636562).

## 2. Independent experimental GBIF global taxon partitions: actual geography and months

The anonymous **August 2026 experimental** GBIF Parquet order partitions for Anura and Odonata were scanned (stage-selected full rowgroups), not merely GBIF's first API pages. Two related populations:

**Initial 61-source-selected focal taxa ([CI 40190152042](https://github.com/zuizui0223/frogcs/actions/runs/40190152042))**: 4,026,251 quality-filtered georeferenced records, 1,253,335 explicitly staged, 655,843 distinct `species × stage × 1° grid × year × month` records, **59 species** actually detected. In the *full GloBI* 881-stage-link population, 18 links had both correct species and stages in this restricted GBIF cube, 17 with ≥1 same grid×year×month, 12 with ≥5 recorded GBIF observations per species-stage-cell-month. **863/881** missing from the link stage-eligibility join are mainly absent **from this selected 61-species GBIF input**; never call them unsupported biological interactions worldwide.

**Expanded 73 source-selected Anura/Odonata species ([CI 40194946916](https://github.com/zuizui0223/frogcs/actions/runs/40194946916))**: 3,996,520 quality-filtered occurrence records, 1,970,585 staged rows, 238,034 `species × stage × 1° grid × year × month` aggregate rows. Both sides in Anura/Odonata yielded **78** original GloBI directed stage patterns; 77 had both stages recorded in GBIF, 71 had same-cell/year/month reporting, and 61 had same month/year/cell when each partner had ≥5 records. This is the **more targeted two-guild expanded test**, not a numerical correction to the original 59-species subset; source-selected species and underlying scan differ.

GBIF `lifeStage` is frequently missing, dates and taxa change with GBIF interpreted taxonomy, and original `speciesKey` in this experimental partition is alphanumeric rather than directly matching older numeric API keys. The focal analysis matched interpreted binomial names and requires further synonym QC.

## 3. Simple month-phase control — positive but nonspecific

[Result/QA](../month_shift_globi_gbif/observed_results.json) | [program](../../scripts/fixed_globi_gbif_month_shift_null.py) | [CI PASS](https://github.com/zuizui0223/frogcs/actions/runs/40194612247).

Same species-stage × 1° grid × year reporting, prey months cyclically rotated by d=1…11:
- At ≥1 record threshold, **17/18** GloBI patterns had some observed same-month cells, **16/18** had more shared monthly cells than their own shifted mean. Pooled observed same-grid/year/month cells **16,605**, shifted means sum ~**6,805**.
- At ≥5 records threshold, **12/18** had actual shared same-month grid-years. Twelve were above their shift average among 14 with shared grid-years.
- A 12-phase diagnostic cannot by itself yield a strong frequentist P-value (best phase rank =1/12); more importantly, this contrast can be fully compatible with **joint flight emergence/seasonal sampling** absent any trophic partner preference.

## 4. Biotic partner-specificity test — more demanding ecological comparator

[18-link matched contrast](../guild_matched_specificity/observed_results.json), [expanded 78-link matched contrast](../expanded_stage_specificity/observed_results.json) | [expanded CI PASS](https://github.com/zuizui0223/frogcs/actions/runs/40195786751).

**Comparator construction:** same predator, alternative prey of same taxonomic guild/stage, GBIF reported month-volume within factor 3, same predator–candidate grid-year overlap within factor 2, excluding documented full-stage links. Alternative prey are **undocumented candidate partners** in the available GloBI full-stage subset, not verified true non-prey; this is post-readback exploratory.

- **Initial 18 edges:** 11 had ≥2 appropriate alternative prey. Only **7/11** showed stronger phase-concordance than matched alternative-prey median (≥1 threshold); **4/11** at ≥5. Focal-control difference medians **+0.060** and **−0.063**.
- **Expanded 78 edges:** 77 eligible with both stages and 56 had matched alternatives; **35 distinct predator taxa**. **31/56** exceeded alternative median under ≥1 reporting; **26/56** at ≥5. Median focal-minus-control phase ratio **+0.090** and **−0.019**. Expanded mean differences **+0.225** and **+0.346**, but outliers dominate: predator-cluster resampling on these fixed matched controls yields −0.186 to +0.695 at ≥1, and +0.028 to +0.709 at ≥5. The latter positive *exploratory mean* does not override the near-zero/negative strict median and only 26/56 positive, and **cannot be treated as a confirmed dietary signal**.
- Reported pair-year-month overlap is correlated by space, effort, life stage and study source. Matching controls removes only two reporting confounders, not genus, phylogeny, natural habitat use, climate or real prey availability.

**Supported conclusion:** general seasonal synchronization of reported developmental stages is widespread; **an additional predator–prey-specific phenology signal is not robustly established** in the current observational comparison.

## 5. Independent climate stratum: historical monthly rain rather than frogcs 72h pulse

[Actual rain joined to GBIF](../gbif_worldclim_monthly_rain/observed_results.json) | [GloBI species-stage rain contrast](../globi_gbif_rain_contrast/observed_results.json) | [CI PASS](https://github.com/zuizui0223/frogcs/actions/runs/40195677642).

- 2010–2024 downscaled CRU-TS4.09 monthly precipitation, WorldClim 2.1. **542,757** GBIF grid-stage-month-year rows, **495,803** with land precipitation and **46,954** no valid on-land climate. Only one source-accepted precipitation cell >3,000 mm/month (max 3,124.94), retained with QA instead of silently truncating real source values.
- Comparing within **exact 1° grid×year** on-land months where the two GloBI partner stages both had GBIF records against months with exactly one stage: 15 of 18 pairs had at least 5 informative grid-year contrasts at ≥1 GBIF observation; **10/15** mean contrasts positive, **5/15** negative, *median across pair means* **+3.38 mm/month**. At ≥5 GBIF reports, 8 eligible pairs, 7 positive, median **+6.72 mm/month**.
- Mostly *adult Odonata–adult Odonata*; source precipitation is monthly climatological reconstruction at the **1° centroid**. It is not **hours-to-days NAAMP rain timing**, local hydroperiod, pond inundation or direct wetland water availability. Hence positive association can simply reflect rainy-season observer/phenological activity. **No causal rainfall→predation, rainfall→frog cohort, vegetation→predation estimate** authorized.

## 6. Relation to original frogcs chorus findings and vegetation hypothesis

Existing **independent, distinct** endpoints:
- NAAMP RC6: 4,236 matched wet/dry listening-route cases, rain-associated switch into CI2/3, within-taxon multi-stop concentration residual +0.2969 after assessed broad weather and source-aware nulls; same-site prior acoustic CI2/3 β=+0.151.
- Independent NPS GLKN 2016–2023: prior same-taxon strong CI2/3 at a physical listening station predicts next-year strong CI, even controlling other taxa's previous station chorus, broad hydroperiod class and observation effort (adjusted β~+0.464, *not the same estimand as NAAMP*).
- Hamer et al. 55 Australian wetlands published fish×emergent vegetation occupancy interaction, and 29 Hungarian field-site acoustic study found simple emergent cover (%) did not improve held-out calling prediction beyond basin/wetland class. These are **not the same wetlands** as the GloBI/GBIF grid co-reports and cannot simply be merged as realized predation.

**Main next test** for a global ecology paper: does verified wetlands' **drying permanence and emergent plant vertical architecture** mediate transition-specific predator and prey abundances, after source/study/observer bias and habitat type are controlled? Plant `Phragmites`/`Typha` GBIF sightings alone measure taxon reporting, **not structural stem density**; they cannot establish refuge or emergence mechanics. Wetland-raster specificity and actual 0.5°/1° monthly GBIF grid outputs at stage/date resolution are needed to screen what is observable, then independent ponds and acoustic monitoring to test causal processes.

## 7. Next execution gates

1. **Global stable-source coverage:** extend beyond the 73 GBIF stage-selected Anura/Odonata species using citable GBIF bulk stage×grid×month downloads, with independent taxon synonym and source-by-source GloBI link validity QA. GBIF bulk 1°/0.5° queries were validated HTTP201 but download has **not been submitted**. The GBIF open experimental 2026-08 source is not a substitute for a DOI-versioned published citation.
2. **Plant & water mechanism dataset:** acquire monthly wetland persistence/inundation and actual emergent-plant architecture (not just country occurrence or broad vegetation classes), map to genuine wetland polygons; defend recording and habitat-detection biases. Carry out within-ecoregion/holdout source tests before generalizing.
3. **Time-series hierarchy:** test GloBI–GBIF potential pair distribution and season while keeping the original rainfall-gated frog chorus dynamics **as a separate observable**. Only station-matched co-surveys can bridge frog calls, larvae, wetland plants and predation effects.
4. **eDNA methylation:** future validated assay for stage/reproduction, not a currently measured chemical signature of acoustic warning or predation.

**Decision:** retain the positive global seasonal-reported-state pattern; classify *partner specificity* and *monthly rainfall mediation* as **inconclusive**. This is a real scientific constraint, not a failure of the acquisition/analysis pipelines. RC6 main must remain scientifically frozen.
