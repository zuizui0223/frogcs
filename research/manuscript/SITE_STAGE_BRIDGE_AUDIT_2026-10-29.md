# Actual-site bridge for stage, timing and vegetation conditions

Date: 2026-10-29. Scope: existing source tables, scripts and manifests only; no new simulation or inferred cross-source joins.

## Finding

The fixed 4,248-site NAAMP cohort supports a test of whether the observed Odonata × pond-breeding Caudata association varies with measured **landscape vegetation context**. It does not currently measure the arrival order, aquatic-stage duration, body sizes, local predator densities or recruitment needed to place actual sites inside a simulation's stage/timing conditions. A successful vegetation comparison would connect a model prediction to an observed environmental context; it would not demonstrate that the model's stage conditions occurred there.

## What is measured at the macro sites

The primary file is `research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz`: 4,248 rows, 69 columns, with one row per acoustic site. The retained history covers 2001–2015, with at least six visits and three years per site. The source survey file, `research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz`, retains `year,date,month,doy,season,air,noise,any,strong`. These are dated adult-call surveys. `season` derives from the survey run, not an animal's developmental stage.

| Simulation condition | Available site information | Defensible correspondence | Not identified |
|---|---|---|---|
| Vegetation/refuge strength | `flooded_3000m_mean`; 1 km sensitivity; herbaceous and water context | A static wetland-vegetation landscape gradient can moderate the fitted acoustic association | Pond stem density/architecture, which animal is protected, encounter-rate reduction, or a calibrated numerical refuge multiplier |
| Longer `Sduration` | Caudata environmental suitability and climate | Environmental context only | Number of days that aquatic salamanders overlap tadpoles or odonates |
| `Darrival` before frogs | Dated frog calls and survey DOY | Adult calling season is observable | Odonate arrival/hatching, tadpole hatching, arrival order or larval overlap |
| Stage/size-dependent reciprocal predation | No local size or developmental-stage field | A mechanism to test in the model | Predator/prey size ratios, actual reciprocal feeding at these sites |
| Recruitment or emergence support | Repeated calling and previous use; landscape vegetation | Reuse of an acoustic site | Egg production, larval recruitment, emergence survival, or next-season local predator abundance |
| Odonate and salamander density | `mean_suitability_Odonata_{uniform,target_group}` and `mean_suitability_pond_breeding_Caudata_{uniform,target_group}` | Relative climate/landscape suitability | Density, occupancy probability calibrated to observations, or predation pressure |
| Frog density and low-density thresholds | `strong_rate`, `any_rate` and effort-balanced variants | Frequency of strong/any adult calling among surveys | Tadpole density, a conversion from call frequency to density, or the model's numerical low-density threshold |
| Hydroperiod | Separate preceding-year GLAD water-detection summaries | Interannual surrounding surface-water context | Actual pond drying dates or the aquatic duration of any of the three groups |

The suitability source explicitly labels projections as relative suitability, not calibrated occupancy probability. The SDMs use WorldClim 2.1 base bioclimatic layers (`bio1,bio4,bio12,bio15`, 10 arc-minute download) and EarthEnv landscape classes. The GBIF training query uses 1980–2015 presence records; it does not measure predator density in the NAAMP survey years. The pond-breeding Caudata group is five species: *Notophthalmus viridescens*, *Ambystoma maculatum*, *A. tigrinum*, *A. laterale* and *A. mavortium*.

## Vegetation source, units and temporal limits

`naamp_remote_vegetation_context.py` reuses hash-pinned EarthEnv full v1 rasters: class 6 (herbaceous), class 8 (regularly flooded vegetation), class 12 (water). Source provider: EarthEnv; class-8 URL is `https://data.earthenv.org/consensus_landcover/with_DISCover/consensus_full_class_8.tif`. Source attribution is Tuanmu & Jetz (2014), CC BY-NC 4.0. The repository's global extraction script describes the composite input period as approximately 1992–2006. It is a static historical composite, not an annual vegetation observation aligned to each call survey.

- Native grid spacing: 0.008333333333333335 degrees (approximately 1 km), EPSG:4326.
- `flooded_3000m_mean`: cosine-latitude weighted mean of valid source pixel values whose centres lie within an approximate 3 km circle. Units are the source's 0–100 consensus/prevalence scale. They are not a surveyed percentage of a breeding pond covered by plants, nor an exact wetland-area percentage.
- `*_sd`: weighted dispersion on that same scale; `*_positive_fraction`: weighted fraction of valid pixel centres with values above zero, on a 0–1 scale; `*_valid_cells` and `*_total_cells`: counts.
- Source values 0–100 are valid; 255 is missing. All 4,248 primary sites have valid 3 km values, with 36–50 valid pixels per circle. There are 506 positive sites on 110 routes and 3,742 zero-valued sites. A zero denotes no positive class-8 value in this coarse composite buffer, **not absence of aquatic plants or refuges at a pond**. Route sets overlap between positive and zero sites.
- The existing vegetation report notes a mean–SD Spearman correlation of 0.999840. These are not independent measurements of vegetation quantity and physical complexity.

Sources: `research/results/naamp_remote_vegetation_20261026/observed_results.json`, `coverage.csv`; `research/scripts/naamp_remote_vegetation_context.py`; `research/scripts/earthenv_global_flooded_vegetation_1deg.py`; `research/REMOTE_VEGETATION_NETWORK_REPORT_2026-10-26.md`.

## Water context is not larval duration

The existing prior-water source is **GLAD surface water dynamics Collection 2 annual water percent**, not a measured pond hydroperiod. Its manifest defines the value as the percentage of classified land/water observations classified as water, explicitly not inundation days. The extraction uses 3 km and 1 km radii and water years 2001–2014. A conditional mean over water-positive pixels is undefined when none are positive; it must not be changed to zero persistence.

The existing water analysis contains 4,040 fixed pairs (3,907 with both-side defined conditional frequency), a different observation unit from the 4,248-site cohort. Its metadata verifies preceding-year alignment for those pairs only. That verification must not be silently transferred to a new site-level aggregation. Sources: `research/results/naamp_prior_water_20261026/{observed_results,association_metadata}.json`.

## Existing developmental evidence: useful, but not a local stage bridge

The source registry explicitly prohibits implicit geographic or life-stage joins. Its observational key retains source, original location, year/month, taxon, stage and method.

| Existing source | Information available | Why it cannot assign the NAAMP model conditions |
|---|---|---|
| NAAMP GBIF occurrence pilot | Historical occurrences within 25 km; some same-year/month records | Circles are not ponds; no verified co-pond larval encounter. Exact-name NAAMP–GBIF matching visits were zero in the saved pilot; non-retrieval is not absence. |
| Global GBIF stage reports | Explicit life-stage labels in opportunistic records, coarse grid × year × month | Recording counts are not densities, and coarse overlap is not local coexistence. |
| Staged GloBI audit | Literature feeding edges and some source-labelled stages | Audit has `naamp_site_time_join:false`; both-aquatic-immature rows among the exact-name audited subset were zero. These establish candidate topology, not local direction or rate. |
| INBO chorus and larval records | Date/location matched within the INBO source; larva/metamorph/adult labels, 2016–2025 | Belgian source locations are not NAAMP sites; no sampled odonate counterpart or measured predation/size overlap. Within-INBO linkage does not authorize an NAAMP join. |
| Hungary 2024 wetlands | Emergent/submerged plant cover and survey-method data at actual wetlands | Separate locations/year; one-time water depth is not hydroperiod, and local three-group stage overlap was not established. |
| NPS GLKN calling stations | Annual adult-call summaries and broad permanence categories | Different station keys; broad water class does not supply larval arrival, duration or predator counts. |
| NWI–GBIF stage point pilot / EarthEnv stage grid analysis | Wetland polygon intersections or broad vegetation–stage-report associations | Nonrandom opportunistic points / coarse grids; neither reconstructs the NAAMP site's actual stage sequence. |

Primary receipts: `research/comparable_db/SOURCE_REGISTRY_V1.json`; `research/results/naamp_pair_connection/staged_global_exact_name_audit.json`; `research/results/naamp_three_guild_occurrence/observed_results.json`; `research/results/nwi_gbif_stage_point_pilot/observed_results.json`; `research/results/earthenv_gbif_matched_stage/observed_results.json`.

## Interpretation of the new comparison

Use the fixed acoustic cohort to ask whether the Odonata × pond-breeding Caudata association is stronger in the measured vegetation context, retaining both SDM backgrounds and the same adjustment set. Report actual support, including the small positive class-8 subset. Do not label survey DOY as predator phenology or use SDM suitability as density. Do not identify the synthetic model's refuge coefficient with a percent of EarthEnv cover.

If macro moderation and simulation conditions agree, the justified claim is: **a vegetation-associated acoustic pattern is compatible with a mechanism that depends on stage overlap and predator effects; the local stage conditions remain unmeasured**. If they disagree, the landscape proxy and the proposed mechanism remain separable explanations. Neither outcome verifies or refutes a specific local arrival sequence without a same-site developmental observation bridge.
