# 全球 GloBI × GBIF 発生段階・地理格子・季節の独立照合 v0.1

2026-10-25. *Descriptive exploratory prospectively fixed relative to the new grid outcome; past country-stage evidence and limited GloBI links already inspected. This is not registered confirmation and does not touch RC6 JAE main.*

## Main research question

For pairs whose **directed** predator- and prey-developmental stages are documented in GloBI, is it possible to recover occurrence observations of these *same stages* in GBIF within the same **0.5°, 1°, or 2° land/sea grid cell** and the same **calendar month-year**? This test is substantially more spatially precise than the prior country facet but **still does not prove the two individuals encountered, interacted, or were present in the same pond**.

## Frozen inputs

- Previously collected [GloBI pair-stage patterns](results/global_globi_gbif/stage_bridge/observed_results.json) from 2026-10-25: ten stage combinations within eight named directed species-pair associations, mixed direct observations and interpreted Quick Pond metaweb edges.
- GBIF /species/match for exact names, accepted rank species, exact match confidence >=90. GBIF API /occurrence/search date 2010–2025 inclusive; 2026 is partial and excluded from phenological comparisons.
- GBIF filter: `taxonKey`, exact `lifeStage`, `hasCoordinate=true`, `hasGeospatialIssue=false`, `occurrenceStatus=PRESENT`, `year=2010,2025`. Drop records lacking calendar month, invalid lat/lon, and coordinate uncertainty >10 km. Retain records with unknown uncertainty in primary but flag as sensitivity. Remove duplicates by GBIF occurrence `key`.
- Normalize stage vocab exactly: adult=Adult/Imago; aquatic immature=Larva/Nymph/Tadpole (and Pupa only in sensitivity, not primary); eggs=Egg; juvenile=Juvenile/Subadult/Immature/Young. Do not treat GloBI's "juv./adults" as a certain adult state; treat mixed stage as uncertain and exclude from main stage-specific inference.
- For each **taxon×GBIF lifeStage label**, get facet total before any outcome. If total ≤ 3,000, retrieve **all records** using 300/page; if > 3,000 retrieve a pre-fixed maximum 1,200 sampled from four offset strata along GBIF default sorting (metadata availability check only) and mark stage `INCOMPLETE_SAMPLE`. These nonrandom slices cannot be used to prove absence or calculate stage overlap prevalence.
- Exclude incomplete stage rows from the main 'complete pair' estimate but report *positive overlaps only* as lower-bound evidence with full stage status. Retain API error reasons; never equate failed query with biological absence.
- Primary exact outcome: the number of 1° grid × year × month cells containing **at least one predator-stage AND one prey-stage GBIF observation**. Secondary: 0.5°, 2°; spatial-only grid overlap, grid×year, grid×month pooled across years. Grid equations use floor((lon+180)/res), floor((lat+90)/res), 0≤lon≤180 edge clamped. A cell with coincident reports is **spatiotemporal observation compatibility**, not a true predator-prey encounter.
- Positive counts per stage-pair are grouped by evidence provenance `GLOBI_META_WEB`, `GLOBI_INAT_OBSERVATION`, or `OTHER_DOCUMENTED_SOURCE`. Record largest GBIF source dataset share, record basis of record and reporting stages, years and coordinates. Species with observations from introduced populations are not yet certified native; no causal or trophic flux inference.
- For complete stage pairs, aggregate 0.5/1/2 overlap differences without significance testing. No "global number of ontogenetic reversals" because the input is a nonrandom 8-edge pilot with only 10 patterns.
- Keep captured geolocated records with GBIF stable occurrence ID, source dataset ID, taxon/stage, coordinates, year/month, uncertainty, and coarse grid codes in a **GitHub Actions artifact**. Avoid repository-committing tens of thousands of raw occurrence records. Commit small JSON and summary CSV with exact per-pair fractions/counts, including zeros when truly absent *only within completely retrieved and filtered input*.
- Data-source and model QA: report `returned_total`, `retrieved_rows`, `accepted_rows`, `complete`, sampled bias, missing months, uncertainty drop, per-stage source completeness. No claims about realized predation or wetland macrophyte structure.

## Independent environmental follow-up

After complete or bounded stage grid counts are available, join **monthly climate normals** (WorldClim v2.1) as climate *background*, not recorded frogcs rain pulses. Ecologically relevant empirical rain event needs locally observed/reconstructed rain windows and wetland inundation at same stage × pond × time. GBIF plant reports can be co-plotted but not used as a density or refuge proxy without habitat geometry.
