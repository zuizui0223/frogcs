# frogcs comparison database v1 — observations, support and ecological inference

**2026-10-26. Single working-home: frogcs/research/comparable_db/.**
This is a **virtual, source-pinned unified database**, not a pile of copy-pasted CSVs and not a single biological pond×time panel magically covering all datasets. It standardizes names, observation windows, sampling protocols and epistemic limits. Existing source repositories and evidence receipts remain immutable. Original RC6 frozen files stay read-only.

## Canonical atomic record (data long form)

Each source-specific ingestion generates an **observation claim** with:
- `source_id`; `source_doi`; `source_sha256`; `record_scope` (`actual_wetland`, `publisher_source_location`, `audio_recorder_station`, `roadside_stop`, `coarse_grid`, `lab_container` or `directed_literature_edge`), `location_token` (only during in-memory operations, not committed);
- `year`, `month` and optional `date`; `temporal_resolution` (`dated_event` / `annual_max` / `grid_month`); `taxon` and source-verified `stage` (adult_call / egg / larva / metamorph / juvenile / unknown), `method` (acoustic/visual/dipnet/bottletrap/GBIF_occurrence/lab/etc);
- `status` = one of `present`, `absent_explicit`, `unassessed`, `ambiguous`. The source's `occurrenceStatus=absent` is **non-detection under specified monitoring**, not guaranteed biological absence; a missing taxon row is always `unassessed`;
- `measured_count` and `count_unit` when independently validated; stage-specific detection/effort when actually measured (`effort_value`, `effort_unit`); **no missing-to-zero**;
- pre-existing measurable covariates (`rain_value`/`rain_window`/`rain_unit`, `hydroperiod_class`, `water_depth`, `emergent_cover_pct`, `submerged_cover_pct`, `substrate_or_vegetation_phenology_date`, `candidate_other_stage`), each with `measured_at`/source and independent valid observation window;
- `response_type` = adult calling/larval report/body mass/true survival, `comparison_target`, `evidence_class` = observational/acoustics/mesocosm/source_relation/synthetic, with `pond_join_verified` boolean;
- **spatial join key** = `source_id`+`original_locationID` ONLY if publisher has documented original physical site mapping. A road stop and a pond, or a 1° grid and a pond, NEVER silently share a site key. Site-month rows may be aggregated per source but cannot assert simultaneous surveys.

No automatic conversion of a calling index into a number of calling animals, of a larval presence report into absolute density, of a larva:juvenile GBIF report ratio into survival or of predator-guild stage-label concurrence into predation.

## Comparable aggregate level

For reports, the reproducible output `source × support_class × year × month × taxon × life_stage × method` contains:
`survey_events`, `explicit_present_rows`, `explicit_absent_rows`, `distinct_source_locations`, `sampled_zero_evidence`, `environmental_covariate_coverage` and source reference. These are **sampled reports**, not populations. It is valid to compare seasonality and observation-coverage at this level, conditional on method/effort; it is invalid to subtract a NPS annual CI coefficient from an INBO larval count or treat cross-source monthly means as simultaneous wetland observations.

Within each original source, ephemeral `site × year × month × taxon × stage` views may be constructed (for exact-site paired analyses and site-heldout validation). Raw original IDs, exact private site geometry and individual records must never be committed.

| Source | Physical support | Actual temporal support | What we can compare directly | What is NOT jointly available |
|---|---|---|---|---|
| NAAMP RC6 | roadside sequential listening stop/route | paired wet/dry routes, timed visits | conditional adult multi-stop acoustic concentration | verified individual pond, other-species aquatic-stage census, live plants |
| NPS GLKN | fixed acoustic station | annual max 2016–23 + static hydroperiod class | species-specific historical strong chorus site persistence by class | 1 pond geometry, larvae/eggs, dated water level and stem refuges |
| Hungary 2024 | 29 source-defined waterbodies | 129 acoustic visits on 26 dates + other methods | rain/calendar timing × site water depth/emergent/submerged cover ↔ acoustic detection | measured predator-stage size, pond drying history, year-over-year stability |
| INBO adult + larva | common original publisher locationID, probable monitoring waterbody | separate source event days 2016–25 | same location/year adult choir ↔ later species stage, day/month lags and cross-taxon larval stage times | rainfall/plant growth on these sites, body size/diet/true survival, verified predator kills |
| GloBI × GBIF macro | directed relation + independent coarse grid | source phenophase in 1° grid×year×month | broad seasonality and negative partner-specificity control | actual predator–prey encounter, acoustic frog site, actual pond vegetation |
| Fuscus factorial G2B | 79 independent small lab containers within 8 baths | development to metamorphosis | randomized cue/water/temp among surviving larvae | actual aquatic attacks or natural year-to-year hydroperiod |

## Standardization & seasonality conventions

- Timestamps in source local dates. **Within-year day-of-year** for seasonal calling and larval stage; within-year absolute dates only when the source provides them. Across continents/hemispheres, shift relative to **source-specific rainy season/temperature season**, never blindly aggregate calendar January with local reproductive phase.
- Plot *calling* and *larval* season curves with separate effort denominators, keeping observational surveys and explicit positive sightings apart. A month with no data is **NA**, not 0. The difference between first adult call and first larval sighting is the gap between detections, not a measured embryonic maturation delay. A “similar stage” comparison needs stage size or age, not two species both tagged larva.
- Plant phenology: `cover_emerged` (%) and `cover_submers` (%) measured only once in Hungary; **neither identifies the month of Typha/Phragmites growth** nor actual use as frog hiding cover. Water-level permanence (NPS categorical) differs from Hungary `depth` and lab artificial DD. Keep all three separate.
- For correlation/“commonality” beyond forecasts, show **within-source measured association and uncertainty**: site-level Spearman/cluster-bootstrap for static vegetation; site/date-block seasonal stage lags for INBO; broad NPS hydroperiod-stratified history association. Do **not** numerically meta-pool these different estimands.
- Analyses with samples selected after earlier outcomes are explicitly **exploratory**. Full unpublished mechanistic causal claims require independently measured stage pressure/prey survival/water dynamics in the same pond, and strong nonpredatory controls.
- Rain-triggered within-species spatial contraction C of RC6 cannot be reproduced by `frog_any` detection in the Hungary one-year panel, nor by an annual NPS CI indicator. Such summaries are independent constraints, not exact replication.

## Output contract and QA

1. `SOURCE_REGISTRY_V1.json` is the single source authority for all named datasets, their grain, stage, meteorological/habitat availability and causal ceiling; replacing scattered “current” prose.
2. `scripts/build_comparable_observations_v1.py` ingests immutable source datasets, validates checksum and creates a **single aggregate reported-observation table** and unified QA. It must fail on malformed stage/category/effort and source hash drift. It makes **no** across-source raw joining on geographic proximity and exports no raw station IDs.
3. `scripts/test_seasonality_and_vegetation_v1.py` computes observed within-source rainy-day/plant-structure correlations and same-INBO-location chorus/larva lag & seasonal month pairing, with explicit observational status and source-specific sample sizes. Keep separate effect labels.
4. `results/comparable_db_v1/*` is the only new normalized observed output directory; old source receipts remain source-of-truth for auditing, and original large raw files remain upstream/only small source-preserved files inside the existing archive.
5. CI must assert original RC6 protected files were not changed, no observational claim is promoted to causal “competition/predation” and source-specific missing fields remain NA.
