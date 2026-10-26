# Frogcs cross-dataset canonical ecological observation contract v1 — 2026-10-26

**One integrated future ecological manuscript, not a pooled cross-source model by default.** Earlier outcomes have been inspected; the following cross-dataset phenology and correlation work is exploratory, with all positive, negative and incompatible findings retained. Original JAE RC6 is immutable, no edits to `main` or any `paper/`, `submission/`, `provenance/`, `figures_pulse_template/`, `scripts/naamp/` path. Document owner: `frogcs/research` only.

## The comparable unit — AND what cannot be made comparable

**One source-native site × calendar year × calendar month × taxon × stage × survey method**, with the source observation/effort definition, plus the original event date where available. The source namespace and physical sampling-unit ontology are part of the composite key and may NEVER be dropped merely to concatenate tables.

| Dataset | Physical unit (`site_type`) | Actual observation and effort / time | Stage / habitat / temporal limitations |
|---|---|---|---|
| NAAMP RC6 | roadside acoustic `listening_stop` within multi-stop route | standardized within-run audio `CallingIndex 0–3` for **positive calling records**; stops with completed survey are survey opportunities, NOT automatically species-specific biological zeros; `DaysSinceRain`, date | Stop may hear multiple ponds; no local hydroperiod, emergent vegetation or resident larval predator. Bad source coordinates; `SiteID` cannot be replaced by a pond name |
| NPS GLKN 2016–2023 | fixed audio `recorder_station` | species×soundfile manually scored `ManualCIV 0–3` including explicit zeros, source `StartTime` → date and month, number of scored species×recordings, site broad `Hydroperiod` class | No source-station GPS or measured local plants; time-of-year acoustic windows differ by species. Strong calls not spawning/offspring |
| Hungary 2024 | field `verified_wetland_site` | visit-specific acoustic/visual/dipnet/bottletrap × identified taxa numeric records; `date`, temperature, humidity, rain; site water depth, fish 0/1 and **static** emergent and submerged `cover (%)` | Acoustic is binary positive, no ordinal chorus or multiple years; dipnet taxa not necessarily larva life stage; cover (%) is not plant seasonal sprouting or emergence timing |
| INBO Flanders 2016–2025 | source original `locationID` across adult chorus and larval protocol; physical waterbody affiliation **not independently geocoded** | `eventDate`, explicit species×`lifeStage`, `occurrenceStatus` present/absent, protocol and available measurements / effort category | Larva/newt co-report is not ingestion or competition intensity; `permanente waterkolom` is missing for the focal Hyla matched 245 site-years |
| GloBI × GBIF worldwide | **1° grid × year × month** source-selected, NOT one wetland | stage-labelled positive biodiversity reports, density of reports and source taxon quality; original GloBI edge stage | Geographic and temporal reporting compatibility only. Not real same-pond encounter or true absence, cannot join to NAAMP stops by ID |
| EarthEnv / WorldClim | gridded environment, variable observation year and season | historical month precipitation, periodically flooded vegetation background (%) | No event-level live wetland, plant height, density, stems, emergence dates, refuge area or drydown measured |

**Canonical columns** for record-level rows:

`source_id, source_sha256, site_namespace, site_id_token, site_type, location_verification, survey_event_token, observation_date, year, month, day_of_year, taxon, stage, method, value_kind, status_code, numeric_value, effort_n, effort_unit, sampled_zero_semantics, rain_mm, water_depth_cm, hydroperiod_class, emergent_cover_pct, submerged_cover_pct, fish_recorded, raw_measurement_name, source_license`.

Unknowns are **null**, not guessed zero; GBIF presence records are not translated into source-positive predator abundance or biological species absence. A source token hash is consistent only within its source namespace; the INBO two-archive exact source locationID is kept under the same **INBO namespace**, with raw field IDs not emitted into Git versioned summaries. No individual wildlife source coordinates are committed. Dates remain literal YYYY-MM-DD if source precise; no universal northern/southern year phase assumed.

**Second canonical layer** `source_id × site_id_token × year × month × taxon × stage × method` with `observed_event_count, status_present_event_count, status_absent_event_count, unknown_event_count, max_call_index_if_source_ordinal, measured_rain_sum_or_mean_with_units, hydroperiod_source, plant_cover_source` and denominators. One acoustic visit is not one actual adult animal, and a site-year-month with no original species-assessment is missing, not zero.

**Third canonical layer** correlation/evidence register: `dataset, physical_grain, contrast_definition, sample_size, independent_group_count, effect_statistic, effect_value, interval, covariate_set, detection_effort, heldout_or_permutation_scheme, claim_ceiling, source_status`. This is the proper cross-dataset comparative interface: **effect definitions** and evidence levels must be recorded before treating different numerical coefficients as comparable.

## User-requested ecological correlation/overlap panel (new)

Predefine three **falsifiable and distinct** correlations:

1. **Timing alignment / developmental lag (INBO)**: at verified source exact location×year, first explicitly positive adult `Hyla arborea` chorus date to later earliest explicitly positive `Hyla` larva date; report signed lag median/IQR, separately explicit non-detection and survey effort. This is **observed phenophase of reporting**, not true egg-to-tadpole developmental time or a one-cohort estimate. Same-source Caudata larva positive record of the same event is *co-detection* only; retain mixed/unknown/absent.
2. **Enemy or competition reporting (INBO)**: (i) prior independently recorded other-anuran adult chorus species richness at that exact original location/year before first focal larval census, correlation with later focal larva `present`; (ii) measured same-survey `Hyla` vs Caudata larvae co-detection (2×2 phi, risk difference), **not** an abundance-of-predators or cause of frog chorus site allocation. Standardize sampling opportunities; never treat nonobserved species as documented absent. Assess site-cluster/bootstrap and year-stratified permutations; no posthoc species selection based on signs.
3. **Rain–plant–water acoustic correlation (Hungary)**: 29 source wetlands, actual acoustic-positive visit fraction vs **measured water depth, static emergent cover and submerged cover**, and mean observed visit rainfall. Report site-level Spearman with 29 independent sites, and partial correlation controlling wetland class and depth/rain as feasible. Repeat visual detection as method sensitivity, not as a genuine "calling" event. Only 2 fish-positive wetlands make a fish/predator × vegetation inferential correlation **non-estimable**.
4. **NPS seasonal chorusing (not larval stages)**: species×recorder×year×month maxima, site–month multiple species strong chorus fraction and distribution by permanent/semi/ephemeral source classification, adjusted for species/day recording effort. Do not attach lifeStage=larva to these acoustic scores.
5. **Global season matching**: full GloBI×GBIF month-shift and matched-prey specificity readouts already exist: 16/18 broad phase above shifts but only 26/56 source linked stage patterns above stage/guild matched alternative at strict volume. Interpret **shared climatic/sampling phenology** as serious rival to predator-specific encounter timing.

### Plant growth versus shelter — currently distinct, not measured jointly

Three unrelated variables must not be called one emergent plant process:

- **Plant presence** from GBIF taxa (`Typha`, `Phragmites`, etc.) is occurrence/reporting with possible flowering phenology, not live emergent cover/juvenile refuge.
- **Plant percent cover** in Hungary is a measured static habitat site attribute, valuable for acoustic correlations, but not a date-stamped new-shoot/emergent height time series.
- **Shelter efficacy** would require actual stem density × water depth × fish/odonate sizes and behavior or experiment, plus a stage-specific interaction term and predator attack/survival. None of these ingredients co-occur in the current 29-site Hungarian acoustic study or same-event INBO larva visits.

Do not assert `emergent plant phenophase matches frog calling` from a calendar-season overlap between flowering GBIF plants and acoustic data when plant observations come from different locations and independent observer populations. Preserve water persistence as a separately measured physical attribute, not identical to Cowardin wetland mapping class.

## Execution and stopping criteria

- New master script `research/scripts/build_common_ecology_units.py` generates **source-native site × time × taxon × stage records** from pinned/archived original INBO, Hungary and NPS data (optional NAAMP source index read-only). It uploads a compact, source-annotated analysis table as an **Actions artifact**, not raw location-identifying data to the repo. Original scientific snapshot SHA checks must pass.
- Summary `research/results/common_units/observed_profile.json` contains cross-source unit coverage, missingness, stage+method frequency, site/year/month span and measured environmental variables with correct denominators, plus explicitly identifies **unavailable common water×plant×predator triple samples**.
- `research/scripts/common_ecology_correlations.py` computes the predeclared observable correlations where source columns satisfy the same-site survey eligibility. Missing stages must fail closed without selecting other species/signs in their place. One original site is the independent bootstrap unit, not a pseudo-replicated soundfile or frog.
- **No shared same-pond predator attack + dynamically measured water permanence + emergent seasonal stem structure exists in existing source receipt.** Even after canonical transformation, it remains a missing joint exposure, not a new numeric effect. A NULL field does not become measured through harmonization.

**Scientific goal**: distinguish *shared seasonality, favorable physical wetland and sampling conditions* from *specific interspecific interaction* rather than optimizing one classifier. The cross-source standardized correlation **evidence register** will link empirical positive, negative and not-estimable findings while keeping their true inferential units.
