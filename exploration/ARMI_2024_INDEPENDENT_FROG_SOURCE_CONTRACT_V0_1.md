# Independent USGS Midwest ARMI 2024 frog survey: pinned source-first replication contract (v0.1)

Frozen 2026-10-22 **before reading any 2024 frog-detection outcomes**. The source is a distinct USGS ARMI survey programme and sampled sites, not reuse of the USGS NAAMP 2001–2015 archive. Outside frozen JAE RC6, Supporting Information and main.

## Authoritative version and exact source

Official ScienceBase data release `68016413d4be0263cab109a8`: [USGS 2024 ARMI survey](https://www.sciencebase.gov/catalog/item/68016413d4be0263cab109a8), [DOI 10.5066/P19ZCGWM](https://doi.org/10.5066/P19ZCGWM). Revised **2026-04-02**, version 1.1.

- CSV `ARMI_2024_cricket_frog_data_release_2025_v1.1.csv`, **235,391 bytes**, official checksum **MD5 `e201e24463d90e23c1f5f903e730e26c`**.
  Verified official ScienceBase URL: `https://www.sciencebase.gov/catalog/file/get/68016413d4be0263cab109a8?f=__disk__13%2F46%2F9a%2F13469adf4b11c2b0e99797f0e5b47a992130010e`.
- FGDC XML `ARMI_2024_cricket_frog_data_release_2025_v1.1.xml`, **41,317 bytes**, official checksum **MD5 `a5a72215d0cd2ad0a027de814edfa701`**.
  `https://www.sciencebase.gov/catalog/file/get/68016413d4be0263cab109a8?f=__disk__a7%2Fb9%2F9b%2Fa7b99b29ed1611b7666ec1012a0da1bef21f9c77`.
- Original primary source official ScienceBase JSON `https://www.sciencebase.gov/catalog/item/68016413d4be0263cab109a8?format=json`; source metadata and file size/checksums inspected **before** opening detection cells.

No third-party mirrors. Download only with verified size, official MD5 and computed SHA256, guard against HTML/error content. If source fails, archive failure and **stop**: absence of data is not a biological negative result. Raw source never committed or redistributed.

## Source metadata and positive-list observation semantics

USGS FGDC author-supplied metadata says all anuran species **heard** during each nighttime survey are recorded. A source row with `Species=none` explicitly indicates no frogs heard. The column `Number_heard` is a **binned** number of audible individuals, not necessarily a point count or CallingIndex 0–3.

2024 surveys were ~5 minutes long at one site and method (ear or parabolic microphone), beginning ~30–60 minutes after sunset; multiple observers independently resurveyed sites 1–4 occasions over June 6–August 15, 2024. Multiple rows may represent species heard on a SINGLE survey event, not independent survey replicates. Spatial coordinates are rounded to ~0.1 degrees (potentially many km) to protect species and **must not be used to split sites or infer microscale habitat**. Use site/project identities in original CSV.

Official FGDC named fields:
`Date` YYYY-MM-DD, `Arrival_time` 24h time, `Project` original sampling project, `Site` site identity, `Site_original`, `Observer` (initials), `Method` (Ear/Microphone), `Wind_Beaufort`, `Cloud_cover_percent`, `Species`, `Number_heard`, `Compass_direction`, `Comments`; may include locations. Actual header names must match source before proceeding.

Target species fixed:
- response green frog `Lithobates clamitans`;
- named partner bullfrog `Lithobates catesbeianus`;
- secondary fixed negative candidate `Dryophytes versicolor` (published 2024 species name corresponding to NAAMP `Hyla versicolor`); `Anaxyrus fowleri` **not in source 2024 FGDC taxon list**, do **not** replace it with another species.

2024 ARMI detects acoustic species presence somewhere during a single 5-min survey, not frog individuals interacting. `Species=none` represents empty species set, not `none` as a 10th real taxon.

## Pre-outcome source-only audit

Run after official checksum validation but **before reading Species contents**:
1. Verify UTF-8 comma-separated file, headers and expected fields, row counts, missingness and unknown survey-event ID fields. Compute SHA256, MD5 and bytes.
2. With pandas `usecols` excluding `Species`, `Number_heard` and `Comments`, count candidate unique surveys by `Project×Site×Date×Arrival_time×Observer×Method`, per-project sites, repeat visits per site, date span, metadata missingness and duplicate row multiplicity; avoid exposing private original site IDs.
3. Survey visit grouping must be **uniquely determined**: if multiple independent visits have identical all six survey event components, report ambiguity and stop. Duplicate rows within one event are expected for multiple frog species, so source metadata/rows are compared only after the metadata-only source gate.
4. Required source gate: >=150 distinct survey events, >=40 physical project×site groups, >=2 projects, >=20 sites with ≥2 survey events, >=90% of events with parsable date/method/observer. If gate fails, `insufficient_source_scope` — no outcome test.
5. Metadata must establish `Species` is **positive-list for all detected calling taxa** and `none` means truly no frogs heard. This allows species-specific *recorded-call nondetection* = 0 for surveyed eligible events with no named row, **not occupancy absence**. No other species response imputation.
6. Verify that two named focal taxa appear in 2024 FGDC taxonomic definitions; source values have NOT been read, so actual detection counts await the next gate.

Freeze pre-outcome source-only receipt with original source SHA, event keys and event/site thresholds. Do not quietly shift source years or combine source populations.

## Frozen biological inference if and only if source QA passes

Primary question: **Does hearing bullfrog on the same survey improve prediction of greenfrog recorded-call detection at a new site beyond observer/method/time/environment and the generic number of other frog taxa heard?** This is independent observational association, NOT the NAAMP site-allocation fixed-fixed null.

- Binary `green = 1` if any row in a validated survey has exact `Species = Lithobates clamitans`, `bull = 1` analogously; otherwise 0 because metadata explicitly records **all frogs heard**. Never infer animals absent from the habitat, only calls not recorded during the 5-minute survey.
- Main scope: all source-valid unique survey visits, *no selecting visits based on focal species being heard*. Exclude unknown/ambiguous event keys before seeing species.
- Source/target information gates after readback: ≥30 green-positive survey visits and ≥30 bull-positive; ≥10 physical site groups with at least one recorded bullfrog; ≥10 sites with at least one recorded greenfrog; at least 2 projects with survey visits; 2 geographically disjoint site-folds each with ≥10 observed green calls and ≥10 bull calls and ≥60 visits.
- Fixed 2-fold split by SHA256 of `Project:Site` site keys, alternating within `Project` when ≥2 sites per project; a physical site is never shared between training and heldout. Each sampled site is weighted by its number of survey visits in the heldout score; site-block bootstrap accounts for within-site pseudoreplication.
- **M0:** scikit-learn LogisticRegression C=1, solver lbfgs, max_iter 500, no class weights; features one-hot `Project` (one baseline), `Observer` (one baseline), `Method` (Ear/Microphone), `Wind_Beaufort` (numeric), `Cloud_cover_percent` (categorical one-hot incl missing), plus day-of-year sin/cos, local arrival hour sin/cos, `n_other_species` = count of frog species heard excluding green, bull, negative fixed candidate. Missing `Wind_Beaufort` produces NA category only if source lists missing as meaningful, otherwise exclusion frozen at QA. Coefficients trained ONLY on training sites; no NAAMP offsets imported.
- **M1:** same features + `bull` binary contemporaneous observation.
- Heldout outcome: change in **per-visit Bernoulli log score** `logP_M1(green)-logP_M0(green)` (nats/visit; positive is improvement); require site-block bootstrap 2,000 replicates seed 2840347 and both fold means positive, both fold `bull` coefficients positive, 95% bootstrap lower bound >0 to call a **portable survey-level positive partner association candidate**. The statistic is not the conditional fixed-margin NAAMP pseudolikelihood and should not be compared numerically.
- Main output also report the same-visit co-calling observed minus independence expectation by Project and overall, with transparent detection denominators.
- Complete-case covariate loss and independent site location count must be reported; do not silently drop outcome observations due to missing Wind or clouds. If site covariates cannot be represented under predeclared coding, stop.
- Per-site persistence sensitivity: on sites with both bull=0/1 and green=0/1 records and ≥2 visits, estimate site-blocked effect using route/site fixed effects or exact stratification if ≥10 such sites; avoid a saturated fixed-effect model on very few observations.
- Secondary fixed negative partner `Dryophytes versicolor` may be fitted incrementally only if ≥30 positive recorded-call events from ≥10 sites. No threshold/extra species replacement.
- Other years (2003–2008 ARMI file) are a **separately frozen next dataset**, no automatic pooling if 2024 fails.

## Limits
Survey-based nondetection may arise from calling season, observer/microphone, wind/noise, rainfall and animal activity. Co-detection can be caused by shared habitat or calling phenology, not real-time individual interaction. ARMI was designed to survey cricket frogs at historically selected sites; sampling is **not random across all upper Midwest wetlands**, limiting portability. Study overlaps NAAMP archive geography but **not survey provenance**. No aquatic macrophyte structure, fish/odonate predators or experimental biotic manipulation is measured here. No main/RC6 edits.
