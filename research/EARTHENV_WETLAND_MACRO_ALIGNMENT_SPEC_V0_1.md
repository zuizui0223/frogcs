# EarthEnv global 1-km wetland habitat proxy → GBIF global stage grid v0.1

2026-10-25. **Frozen before inspecting any EarthEnv×GloBI×GBIF wetland overlap results**, following failure of a strictly predation-specific seasonality interpretation. New globally explicit environmental stratification for the research branch. The RC6 submission `main` remains scientifically frozen.

## Controlling environmental source

Tuanmu, M.-N. & Jetz, W. (2014), *A global 1-km consensus land-cover product for biodiversity and ecosystem modelling*, *Global Ecology and Biogeography* 23:1031–1045. https://www.earthenv.org/landcover. Full v1.0 (with DISCover), licensed **CC BY-NC 4.0** for scientific use. Download individual original 30 arc-second global GeoTIFFs:

- `consensus_full_class_8.tif` = **Regularly Flooded Vegetation**;
- `consensus_full_class_12.tif` = **Open Water**;
- `consensus_full_class_6.tif` = **Herbaceous Vegetation** as the general green/background control.

Exact origin: `https://data.earthenv.org/consensus_landcover/with_DISCover/consensus_full_class_{8,12,6}.tif`. Data integrate products from the 1990s–2000s and cover 90°N to ~56°S; do not claim that they show 2026 live marsh stems. Pixels indicate remotely sensed class consensus prevalence **0–100**, not observed `Typha` stem densities, guaranteed emergent reeds, species-level vegetation, egg-laying substrate, or current wetness. The full version's composite of several remote sensors is not precisely dated to 2021.

## Pre-outcome source validation and aggregation

1. Download each layer with URL, file size, cryptographic checksum, raster CRS/transform/nodata/resolution/shape recorded. Abort on HTML/empty response, bad GeoTIFF, impossible value or more than 150 MB per layer. Preserve source license/credits.
2. Warp source raster to **global 1° grid** using documented area-averaged EarthEnv consensus pixel values in EPSG:4326, from [-180,180]×[-90,90] (360 columns ×180 rows). Pixel-value average is equal-angle (not exact equal-area). At high latitudes, use cos(latitude) weight for *global* statements; do not treat 1° cells as equal ground area. Keep no-data southern-latitude cells missing, not zero.
3. Keep independent `regularly_flooded_vegetation_prevalence`, `open_water_prevalence`, `generic_herbaceous_prevalence` and `total_valid_landcover_bands`, source checksum and 1° `latitude,longitude` centre. Invalid/missing values must not be imputed to zero. Do not pretend the three classes sum to exactly 100 (consensus class probabilities are imperfect/partly overlapping).
4. Validate geography using known ocean/no-data locations and representative spatial cells. No "global emergent plant cover" conclusion from this source.

## Prespecified ecological comparisons (only if actual data source is accessible)

Matched input: previously observed GBIF Anura+Odonata 1° `species×life stage×year×month` from public experimental 2026-08 taxon-parquet complete source scan; pinned GloBI full 2026-09 24,453,954-source records with stage-specific edges.

- **Primary non-causal comparison**: for *already documented GloBI stage links*, calculate one-degree within-grid/year/month coincidence by pooled wetland-background exposure bands Q1–Q4 **conditional on having GBIF occurrence reports for both named taxa**, weighted by species-stage source effort and preferably holding predator taxon/region fixed. Avoid comparing simply more recorded wetlands with less surveyed cells.
- **Matched prey negative control**: compare the seasonal phase-ratio in GloBI documented predators and 2–5 same-guild/stage alternative prey whose species×stage overall reporting and predator-shared grid-year footprint were already matched; stratify wetland background **without selecting controls after seeing wetland map**. If documented and matched controls behave similarly across flooded vegetation, reject an interaction-specific vegetation conclusion.
- **Climate layer**: 2010–2024 historical CRU-WorldClim *monthly* precipitation joined to GBIF grid-year-month; distinguish between monthly precipitation and NAAMP 72-hour rainfall bursts and actual pond inundation. Stage response is recording presence, not population quantity. Climate effect must not be called frog oviposition or predator attack.
- **Negative guardrails**: high EarthEnv flooded vegetation at coarse 1° cells is not a local wetland where either specific species was found; no direct GloBI photo location, egg mass, predator abundance, wetland hydroperiod or plant structure co-measure. No causal habitat engineering inference without stage-and-wetland-matched primary survey or intervention.
- Species native versus introduced ranges and observer/reporting effort are not yet fully controlled; no independent p-values or global predation prevalence.

### Feasibility gate

If EarthEnv rasters are blocked (403/timeout/invalid), record **source access failure** and stop repeated retries; do not invent maps. The fallback is ESA WorldCover 2021 10 m COG with class 90 `herbaceous wetland`, class 80 `permanent water`, and class 30 `grassland`, distinct time/legend and expensive global tile aggregation. Do not silently substitute it without separate source validation and methodology.

### Priority research statement

Global *GloBI/GBIF* supports a potential stage-specific interaction network; EarthEnv maps environmental **background**. The core scientific claim can emerge only if environmentally moderated source-backed stage overlap exceeds matched taxon/prey/year/month reporting expectations, survives ecoregion holdout, and later predicts actual within-pond encounters. NPS/NAAMP chorus recurrence is a separate behavioral timescale and must not be asserted as a GBIF mechanistic result.


## Fixed numerical wetland comparator before seeing global grid joint results

EarthEnv 1° flooded-vegetation prevalence was downloaded and its global **marginal** distribution audited before the occurrence link; EarthEnv class 8 had 14,917 positive out of 52,560 raster-valid global 1° cells and 90th percentile 0.322%. The thresholds below are therefore fixed **from marginal habitat coverage, not GloBI/GBIF co-reporting**.

- Three `flooded_veg` tiers: **zero** if <0.01 percentage point; **low/intermediate** if [0.01,1) percentage point; **relatively high** if >=1%. Handle exact missing raster separately. The 1% cut is an ecological background threshold, not 1% live reed cover; do not interpret it as a measure of emergent plant density at the focal pond.
- On **source 73 expanded species** GBIF 1° stage grid and **56 precomputed matched GloBI documented vs alternative prey comparisons**, form predator-stage × prey-stage joint GBIF reporting month bitmasks in each valid 1° grid×year. Use each originally chosen 2–5 matched alternative prey species (as selected without EarthEnv access). Exclude a source pair if its parent matched controls unavailable; never redefine matching using EarthEnv co-occurrence outcomes.
- For focal and matched alternative prey, compute observed same-cell-year-month co-reports **C0** and shifted-month null **Cshift mean** in each habitat tier; `Q=(1+C0)/(1+Cshift)`. Compare documented focal Q minus **median control Q**, with at least 2 controls. Report number of **unique predators** and qualifying pair-tiers, number of contributing grid-years, Q differences, and source tiers. No guaranteed equal number of reporting cells across habitat tiers; proportions are exploratory and can reflect survey effort.
- Threshold sensitivity **>=5 GBIF reports per species-stage-gridmonth** keeps the prey controls fixed, and requiring both stages measured vs one missing is automatic from normalized source-stage key. If a habitat tier has too few observed pair-grid-year cells (<5), label not estimable; never report a zero biological interaction.
- Compare general herbaceous and open water layer as negative/alternative **background habitat covariates** in a secondary descriptive cross-check, rather than deriving post-hoc a "best" flooded-vegetation threshold.
- For rain, only join the existing CRU-WorldClim 2010–2024 observed grid-month rain file as source coverage QA; rain data are conditional on selected GBIF positive report grids and do not provide a complete 12-month climatic null for all expanded species; defer causal wet/rain effects and explicitly report nonmatching grid years.
- **Null**: the difference between known vs undocumented same-guild/stage matched alternative prey remains roughly similar in relatively high vs near-zero flooded vegetation backgrounds. A positive contrast would only justify an externally testable hypothesis, not proof plant architecture mediates trophic interactions.


## Post-readback spatial QA correction: ocean-dominated 1° cells (2026-10-25)

The first EarthEnv × expanded GBIF matched-prey calculation exposed a substantial **ocean-dominated** confound: the `near_zero` flooded-vegetation class contains 1° grid cells with **median 100% open-water background**, because the global grid includes most open sea. This is *not* comparable to a zero-emergent, land-dominated pond habitat; it is the wrong counterfactual. This correction was designed after reading initial habitat results and is **post-hoc QA**, not an untouched confirmation.

- In the revised **land-dominant** comparison, exclude/label separately any 1° EarthEnv grid with **open_water_pct >=50 percentage points**, before assigning flooded-vegetation tiers. Such coastal cells may still contain actual wetland and frog GBIF sightings, so absence in the restricted analysis is missing from the comparison, not a biological assertion of no wetland.
- Keep three original flooded-vegetation tiers `near_zero(<0.01)`, `low_intermediate[0.01,1)`, `relatively_high(>=1)` within the **open_water_pct <50%** grid, with old 2014 source temporal and non-emergent-structure caveats. Missing EarthEnv raster pixels still excluded without zero fill.
- Recompute **same original 56 matched directed-stage pairs**, exact fixed controls and GBIF thresholds of 1 and 5. Compare whether the **paired same-species high-minus-nearzero median** and number of eligible predator species persist. Do NOT treat differences as confirmed trophic effects.
- Preserve full source audit and previous first run separately; the revised result should carry `QA_LAND_DOMINANT_EARTHENV_LT50_OPENWATER_POSTHOC` status and an explicit count of excluded ocean-dominated species-stage-grid-years.
