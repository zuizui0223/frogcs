# Climate–landscape change and frog acoustic-site use — independent study v0.1

**Date:** 2026-10-08. **Status:** design and testable climate feature adapter only; no remotely sensed pixel stacks extracted, no frog outcomes reopened, no climate-effect estimates. This is a *new independent study*, not an RC6/JAE correction or extension, and must not change the locked manuscript, endpoints, or release claims. The prospective WFTS route remains not pursued.

## Scientific question

**Does gradual hydroclimatic and terrestrial landscape change reorganize the places where anurans express reproductive calling, beyond the familiar short-term rain pulse?** Specifically, do warmer but more hydroperiod-limited years decouple the immediate cues for calling from the seasonal availability of candidate breeding water, and do forested, hydrologically persistent patches buffer this change?

Do not call acoustic detections successful reproduction, abundance, individual site fidelity or demographic occupancy. Climate *change attribution* is not supplied by a spatial association with an annual anomaly.

## Testable, competing ecological mechanisms

1. **Short-term cue only (M0):** species-specific calling responds to recent weather and the historical acoustic propensity of a physical site; slow climate and landscape changes add little predictive power for later-years' site-specific strong calling.
2. **Hydrological filter (M1):** the same immediate weather cue is expressed at different sites when wetland water persistence or wet–dry state differs. Dynamic water availability should absorb much of the apparent long-term site-memory effect; *only* in wetlands resolved adequately by imagery. Simultaneous acoustic activation must not automatically imply connected populations or frog movement.
3. **Hydroclimatic mismatch (M2):** warming/early warmth advances the seasonal acoustic activity window without equivalent gain in stable water availability. Strong calling can then become disconnected from satellite-visible persistent water, especially in dry years. A true mismatch **with larval survival** cannot be established without larvae/success data; the observable endpoint is calling–water-proxy mismatch.
4. **Terrestrial buffering / isolation (M3):** land-cover composition and changing imperviousness/forest continuity modify hydrological sensitivity and the spatial redistribution of taxon-specific calling. Local buffers and landscape context can counteract regional dry/warm anomalies, potentially producing spatially uneven rather than monotonic responses.

Predictions should be genuinely competing; do not turn a failed directional prediction into a new confirmatory direction. M1/M2/M3 could co-occur, so the main model comparison is incremental and out-of-block; interactions are secondary preregistered tests.

## Study scales and inputs

Existing NAAMP 2001–2015 survey opportunities: 7,848 eligible standardized route runs at 10 stops/run; 807 routes (21 states). The locked RC6 paired analysis uses 4,236 rain-contrasted pairs from 585 routes; these are **not** the appropriate complete panel for climate-change inference. Rebuild an annual/site panel from eligible survey effort independently, including explicit nondetections only where visits occurred. Prefer repeated fixed physical sites and harmonized within-season visits. Do not treat 78,480 stop visits as independent random samples. Respect NAAMP's sparse positive CallingIndex rows.

| Scale | Source | Frequency and coverage | Exposure (descriptive, unless prespecified) |
|---|---|---|---|
| Days 1–90 **before** each survey | NASA Daymet V4 (1 km North America, 1980–); PRISM daily (~4 km US, 1981–) corroboration | daily | recent temperature anomaly, accumulated rain, dry-day count, snow conditions where supported |
| Seasonal/interannual, including drought | GRIDMET/DROUGHT (~4 km CONUS, 1980–) | 5-day drought indices | 30/90/180-day SPEI, EDDI, SPI; cross-dataset drought sensitivity |
| Long-term antecedent climate | Daymet/PRISM 1981–2000 reference plus past 5-y rolling means | annual or seasonal | antecedent multi-year anomaly, not a climate-attribution claim |
| Satellite-detectable standing water | JRC/GSW1_4/MonthlyHistory (1984–2021, 30 m) | monthly **with no-data state** | water fraction, seasonal persistence, wet/dry transitions, observation coverage |
| Terrestrial land cover | USGS Annual NLCD Collection 1.2 (CONUS 1985–2025, 30 m); independent Landsat C2 | annual and cloud-masked scene composites | forest, wetland class, imperviousness, cropland, structural shifts, vegetation anomaly |

**Do not use TerraClimate alone to independently infer a climate trend.** Its own documentation says temporal trends are inherited from its parent datasets. May be used for modelled climatic water deficit as a secondary proxy, with that limitation attached.

**Do not assume** Annual NLCD Collection 1.2 has a valid Earth Engine asset matching the old epoch NLCD asset. Confirm current catalog distribution/API before extraction. Separate collection version, area and temporal coverage in receipts. For JRC, per-month 0 is *no data*, 1 non-water, 2 water; missing is not drought. Pre-2022 water history does not directly report small seasonal pools, deep canopy pools or intramonth water-level changes. For survey-event antecedents, use last completed monthly image, **never a monthly summary that includes observations taken after the survey date**. Year-y Annual NLCD classification can likewise contain post-survey imagery; for strictly antecedent analyses use year y-1, or treat year-y class as descriptive/contemporaneous only, not predictive prior exposure.

## Coordinate/identity gate: MUST precede outcome overlay

The pinned NAAMP USGS coordinates include clear errors (route 270107 SiteID 4507 longitude +83.302 in U.S.; other within-route >100 km anomalies). The abandoned exact-distance analysis is non-authoritative. Before consulting any response endpoint:

1. Audit all site coordinates for domain, duplicates, unexpected route dispersion and cross-year shifts, independent of species and acoustic intensity.
2. Verify anomalous positions against independently sourced route/station documentation or an independently validated geographic reference; do **not** repair with guessed sign flips or post-result selection.
3. Distinguish actual station relocations from transcription errors; require unambiguous `route_id + physical_site_id + survey_year` identity for annual linkage.
4. Freeze `verified_external`, `ambiguous`, `failed` statuses and a reproducible site inclusion ledger. This project's climate adapter **fails closed** on non-verified sites. Avoid claiming that the previous coordinate audit gives all remaining sites meter-scale correctness.
5. Report number of eligible sites, site-years, and route coverage *after* this gate. If robust verified sample is small, favor route-/region-scale climate trends, not site-level 30 m inference.

Proposed spatial buffers (fixed before reading outcomes): **250 m** local terrestrial context and **1 km** landscape context around independently verified stations; calculate exact available pixels and cloud/no-data fraction. Wetland water may be smaller than one 30 m pixel; remote sensing is a water-availability **proxy**, not in situ hydroperiod or larval success.

## Feature-level time alignment

Raw response table grain: `RunID × RouteNumber × physical_SiteID × taxon`, with `SurveyDate`, `RunNumber`, calling index 0–3 constructed from documented positive records *only* for eligible, unskipped sampled stops.

Covariate grain: `route_id × site_id × survey_date`, with source hash, data version, grid-cell ID, spatial radius, pixel-valid fraction, and acquisition/composite date retained.

- **Fixed baseline:** 1981–2000 (monthly seasonal climatologies at each site; for raw long-term trends additionally examine full 1981–2015 annual series as a diagnostic, not as a feature for past-year prediction).
- **Weather before survey:** fully observed preceding 7/30/90 days, excluding survey day; annotate coverage rather than interpolate whole missing periods.
- **Slow climate state:** complete five preceding years (`year-5` through `year-1`), compared with fixed 1981–2000 climatology. This is a trailing climate state, not proof of anthropogenic forcing.
- **Remote-sensing water:** last completed and adequately observed month(s) before survey; parallel phenology-matched month windows; never convert cloudy/no-data to water absence.
- **Land cover:** prior calendar year for prospective exposure and coincident year only for descriptive mapping; forest conversion cannot be reconstructed by taking the differences of two isolated satellite scenes without cloud/phenology and classification uncertainty checks.
- **Phenological alignment:** use local calendar date and protocol `RunNumber`, then optionally preregister spring thermal-start indices with an independent, biologically justified definition. NAAMP's few within-season visits cannot identify true first breeding date precisely.

## Primary evidence strategy

**Step 0 — response-blind feasibility:** independent coordinate-QC gate, data availability by space/time, sensor observation gaps, land-cover class consistency, climatic multi-year change; choose sample before inspecting call outcomes.

**Step 1 — landscape-history panel:** map forest, agriculture, impervious fraction, and seasonal water at eligible sites year by year. Maps show image dates and missing coverage. Distinguish environmental trend from classification shifts, seasonal imaging artifacts and local development.

**Step 2 — calibrated change in calling-site use:** separate detection effort, seasonal survey timing and taxon. Describe transitions in repeated acoustic use at stable sites. Compare matched route/year/taxon strata where survey opportunity exists. Zero during an eligible visit is non-detection, not permanent site extinction.

**Step 3 — competing mechanisms:** baseline `recent weather + year/season/protocol + strictly prior historical site use`, add `slow climate`, then `dynamic water and terrestrial change`, then predeclared `slow climate × local hydrological/landscape buffer`. Test both individual site-level call probability and **joint taxon × site configuration conditional on total activation**. Marginal prediction alone cannot establish spatial reorganization.

**Step 4 — inferential design:** train before 2011, temporal test on 2011–2015, plus spatially held-out route/region blocks. Freeze all choices using training geography/time alone. Block bootstrap/cluster at route (or greater spatial units); report changes in held-out log-loss/calibration **and** configuration residuals. Include taxon-level heterogeneity, spatial autocorrelation and sensitivity to coordinate-QC exclusions.

**Step 5 — negative controls and falsification:** restrict to documented stable physical sites; check future land-cover/hydrological change as a *diagnostic placebo* (not an exogeneity guarantee); compare same-site different climate years, sites with similar climate but different land-cover change, and stations with high/low valid-pixel support. If local inundation is not reliably observed, label M1/M2 untestable with satellite data rather than calling a statistical non-association negative evidence.

## Novelty check / literature ceilings

Climate-change impacts on amphibian phenology, hydroperiod and occupancy are not in themselves new. Wetland drying can also coexist with quick post-drought calling/occupancy recovery. Directly relevant studies include:

- USGS, *Multi-year data from satellite- and ground-based sensors show details and scale matter in assessing climate’s effects on wetland surface water, amphibians, and landscape conditions* (2018): satellite indicators failed to show consequential intra-seasonal pond-water fluctuations detected by ground sensors. **Critical spatial/temporal proxy limitation.** https://www.usgs.gov/publications/multi-year-data-satellite-and-ground-based-sensors-show-details-and-scale-matter
- *Multistate occupancy modeling improves understanding of amphibian breeding dynamics in the Greater Yellowstone Area* (2018): separates wetland drying from amphibian breeding. https://pubmed.ncbi.nlm.nih.gov/30403314/
- *Resilience of native amphibian communities following catastrophic drought* (2021): drought-driven site drying and post-drought recovery with hydroperiod diversity. https://pubmed.ncbi.nlm.nih.gov/34737459/
- USGS, *Climate-driven changes in wetland hydroperiods predict losses in habitat suitability for amphibian breeding* (2026-09-15): directly forecasts climate-driven breeding-habitat loss. https://www.usgs.gov/publications/climate-driven-changes-wetland-hydroperiods-predict-losses-habitat-suitability

Distinct potential contribution **if supported:** quantifying whether long-term climate/terrestrial change decouples **fast acoustic activation** from the **spatial pattern and temporal persistence of suitable water** across a multispecies monitoring network — not merely documenting warmer years or wetland loss. Do not describe this as established until verified-site extraction and outcome-independent hypothesis testing are done.

## Reproducible first artifact

`scripts/build_climate_features.py` is a response-blind CSV adapter with tests. It computes fixed-climatology 7/30/90-day anomalies and a trailing five-year climate-state contrast **after** external site-coordinate verification. It does **not** download Daymet or LandSat, perform Earth Engine raster extraction, read outcomes or estimate biological effects.

To run after preparing the validated inputs:

```bash
python scripts/build_climate_features.py \
  --surveys verified_survey_sites.csv \
  --daily daymet_daily_by_site.csv \
  --out climate_exposure.csv \
  --receipt climate_exposure_receipt.json
pytest -q tests/test_climate_features.py
```

Inputs:
- `verified_survey_sites.csv`: `run_id,route_id,site_id,survey_date,coordinate_qc_status`, with `coordinate_qc_status=verified_external` for every row.
- `daymet_daily_by_site.csv`: `route_id,site_id,date,tmin_c,tmax_c,precip_mm` containing full reference years 1981–2000 and all prior dates. Record Daymet/PRISM input source/version, grid IDs, geometry QC and raw hashes separately.

**Status/limitations:** offline adapter with synthetic tests, no validated U.S. NAAMP satellite-climate overlay as of this file. Only after coordinate verification and response-blind extraction will the study be capable of examining climate-linked reorganization.

### Separate long-term trend diagnostic

`scripts/build_climate_trend_diagnostics.py` computes *descriptive* Theil–Sen slopes of annual temperature (°C/decade) and precipitation (mm/decade) over **1981–2015**, with at least 30 complete station years (≥350 daily records each). It takes a daily climate CSV with the same columns plus `coordinate_qc_status=verified_external` and emits `route_id,site_id,n_valid_years,trend_status,warming_c_decade,annual_precip_change_mm_decade`.

This uses future years relative to 2001 events, so **never use the 1981–2015 slope as a predictor in a model claiming to forecast outcomes in 2001–2014**. It is a retrospective climate-data diagnostic. The *event predictor* is the past-only five-year exposure from `build_climate_features.py`. Trends and shift estimates remain meteorological descriptions, not attribution to greenhouse-gas forcing. Compare independently to PRISM before giving scientific weight to fine-scale slopes.

```bash
python scripts/build_climate_trend_diagnostics.py \
  --daily validated_daymet_daily_with_coordinate_status.csv \
  --out climate_trend_diagnostic.csv
```

Both scripts operate on separately prepared site/batch CSVs and cannot automatically download national NAAMP records or imagery. The initial prototype is **pilot-scale**, not yet engineered for a continental 1981–2015 × station daily array. Before scaling, group and cache daily climate by native climate grid cell, then process route/region chunks.
