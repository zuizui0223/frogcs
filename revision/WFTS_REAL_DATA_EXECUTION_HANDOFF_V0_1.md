# WFTS real-data execution handoff v0.1

> **CURRENT PROJECT STATUS (2026-10-05): SUPERSEDED / DO NOT EXECUTE.** The prospective WFTS replication was specified but not pursued; no WFTS data were requested or analysed. Current authority: `revision/WFTS_NOT_PURSUED_2026-10-05.md`. This file is retained only as historical prospective-design provenance.


**Status:** ready before receipt of WFTS frog-response data. No WFTS taxon × station × year outcome has been inspected.

This document is operational only. Scientific authority remains:

`revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`

Byte-level execution authority is frozen in:

`revision/WFTS_REAL_DATA_EXECUTION_LOCK_V0_1.json`

If the lock QA fails, do not use real WFTS response data until the discrepancy is resolved without inspecting outcomes.

---

## 0. What is complete before data arrival

Already frozen and implemented:

- candidate network and one-shot rule;
- traditional-route eligibility;
- canonical run/matrix schema;
- primary Daymet rain-recency definition;
- matched-pair construction;
- principal concentration endpoint;
- route-cross-fit comparator;
- structural coverage gate;
- three-way primary result classification;
- common-environment secondary;
- bounded route-night dependence secondary;
- far-lag secondary;
- monitoring-uncertainty diagnostic;
- exact-k recurrent-site placement secondary;
- deep-minus-shallow placement contrast;
- simulation counts and seeds;
- anti-tuning rules;
- raw-byte receipt tool;
- schema-only inspector;
- route-master structural auditor;
- primary and secondary weather adapters;
- response-blind preflight;
- primary/secondary/deep-placement analysis code;
- byte-level real-data authority lock.

The only scientifically legitimate work that remains before primary execution is **adapting received raw tables to the already-frozen canonical schema using schema/codebook/structural metadata only**.

---

## 1. On receipt: preserve raw bytes first

Do not open a spreadsheet manually to inspect frog outcomes.

Create a receipt from the untouched original files:

```bash
python scripts/wfts/receipt_raw_wfts_files.py \
  RAW_FILE_1 RAW_FILE_2 [RAW_FILE_3 ...] \
  --output build/wfts-real/raw_byte_receipt.json \
  --source-note "SOURCE/SENDER/DELIVERY CONTEXT" \
  --received-at-utc "YYYY-MM-DDTHH:MM:SSZ"
```

Freeze:
- original filenames;
- byte sizes;
- SHA256;
- sender/source;
- receipt time.

Original files must remain unchanged.

---

## 2. Schema-only inspection

Run without browsing biological rows:

```bash
python scripts/wfts/inspect_wfts_schema_only.py \
  RAW_FILE_1 RAW_FILE_2 [RAW_FILE_3 ...] \
  --output build/wfts-real/schema_only_receipt.json
```

Use only:
- file/container names;
- sheet/table names;
- column names;
- data types where available;
- documented missing/non-detection codes;
- codebook/database documentation.

Do not summarize species occurrence, call-index frequencies, richness, multi-site patterns or effect direction.

---

## 3. Freeze raw-to-canonical mapping before response endpoint access

Start from:

`revision/WFTS_RAW_TO_CANONICAL_MAPPING_TEMPLATE_V0_1.json`

Complete it only from:
- schema receipt;
- codebook;
- route master;
- station master/history;
- documented programme rules.

Resolve, before endpoint calculation:
- route type;
- RouteID lineage;
- SurveyPeriod mapping;
- survey-date parsing;
- physical_site_id construction;
- station replacement/relocation rules;
- valid/incomplete-run rules;
- blank vs missing call-index semantics;
- taxon synonym mapping.

Change manifest status from:

`TEMPLATE_NOT_FROZEN`

to:

`FROZEN_BEFORE_RESPONSE_ENDPOINT`

and commit the completed manifest plus adapter code.

If any ambiguity requires looking at ecological effect direction, stop.

---

## 4. Build response-free structural station-survey input

Construct a table containing only:

- `route_id`
- `survey_period`
- `survey_year`
- `survey_date`
- `station_order`
- `physical_site_id`
- `latitude`
- `longitude`

No `taxon_key`, `call_index`, richness or response-derived columns may be present.

Recommended path:

`build/wfts-real/structural_station_surveys.csv`

---

## 5. Build frozen primary Daymet weather

```bash
python scripts/wfts/build_daymet_covariates.py \
  --station-surveys build/wfts-real/structural_station_surveys.csv \
  --output-runs build/wfts-real/daymet_runs.csv \
  --output-stations build/wfts-real/daymet_stations.csv \
  --receipt build/wfts-real/daymet_receipt.json \
  --cache-dir build/wfts-real/daymet-cache
```

This step must remain response-free.

The resulting primary exposure is the frozen mean station `log(1 + dry_days)` rain-recency measure.

---

## 6. Build frozen secondary 1/3/7-day precipitation weather

Also before response unlock:

```bash
python scripts/wfts/build_common_environment_covariates.py \
  --station-surveys build/wfts-real/structural_station_surveys.csv \
  --output-runs build/wfts-real/common_env_runs.csv \
  --output-stations build/wfts-real/common_env_stations.csv \
  --receipt build/wfts-real/common_env_weather_receipt.json \
  --cache-dir build/wfts-real/common-env-cache
```

The 3-complete-day exposure is primary for the secondary mechanism chain.

The 1-day and 7-day windows are named sensitivities only.

---

## 7. Create canonical structural files without reading response endpoints

Using the frozen mapping, build canonical files matching:

`revision/WFTS_CANONICAL_SCHEMA_V0_2.json`

Required structural portion of `runs.csv`:
- route_id;
- survey_period;
- survey_year;
- survey_date;
- rain_recency;
- tmean_run.

Required structural portion of `matrix.csv` before unlock:
- route_id;
- survey_period;
- survey_year;
- survey_date;
- station_order;
- physical_site_id.

The full matrix file may physically contain response columns, but the preflight script is the authority that must prove it did not parse them.

---

## 8. Response-blind structural preflight

Run exactly:

```bash
python scripts/wfts/preflight_wfts_structure.py \
  --runs build/wfts-real/runs.csv \
  --matrix build/wfts-real/matrix.csv \
  --output build/wfts-real/preflight.json
```

Freeze the receipt before any endpoint is read.

PASS requires:
- ≥30 principal-history traditional routes;
- ≥300 principal-history matched pairs;
- ≥10 routes in each deterministic fold.

The receipt must record:
- runs SHA256;
- matrix SHA256;
- schema SHA256;
- `response_columns_read = false`;
- `taxon_key_read = false`;
- `call_index_read = false`.

### If preflight FAILS

Stop.

Classify WFTS as structurally/data-access ineligible or underpowered for the frozen confirmatory test.

Do **not** inspect response outcomes to rescue eligibility.

### If preflight PASSES

Commit/freeze:
- raw byte receipt;
- schema-only receipt;
- completed mapping manifest;
- raw-to-canonical adapter;
- route/station structural audit;
- weather receipts;
- canonical file hashes;
- preflight receipt.

Only then proceed.

---

# RESPONSE UNLOCK BOUNDARY

Everything above must be completed and frozen before this line is crossed.

---

## 9. Run the primary confirmatory analysis exactly once

```bash
python scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py \
  --runs build/wfts-real/runs.csv \
  --matrix build/wfts-real/matrix.csv \
  --preflight-receipt build/wfts-real/preflight.json \
  --output build/wfts-real/primary_confirmatory_result.json
```

Immediately freeze the raw output before narrative interpretation.

Exactly one primary classification is allowed:

- `replication_support`
- `informative_nonreplication_of_half_discovery_effect`
- `inconclusive_nonpass`

No secondary result may change this classification.

---

## 10. Run the common-environment / route-night secondary only after primary freeze

```bash
python scripts/wfts/run_wfts_secondary_route_night_diagnostics_v0_2.py \
  --runs build/wfts-real/runs.csv \
  --matrix build/wfts-real/matrix.csv \
  --preflight-receipt build/wfts-real/preflight.json \
  --primary-result build/wfts-real/primary_confirmatory_result.json \
  --common-env-runs build/wfts-real/common_env_runs.csv \
  --common-env-receipt build/wfts-real/common_env_weather_receipt.json \
  --output build/wfts-real/secondary_route_night_result.json
```

Freeze before interpretation.

Required guard:

`primary_replication_classification_unchanged = true`

Outputs include:
- 3-day measured-common-environment sufficiency;
- named 1/7-day sensitivities;
- bounded route-night residual dependence;
- dry-route-silent far-lag persistence;
- monitoring clustered/IID uncertainty ratios.

---

## 11. Run recurrent-site/deep-placement secondary last

Only after both primary and common-environment secondary files are frozen:

```bash
python scripts/wfts/run_wfts_deep_template_alignment_v0_1.py \
  --runs build/wfts-real/runs.csv \
  --matrix build/wfts-real/matrix.csv \
  --preflight-receipt build/wfts-real/preflight.json \
  --primary-result build/wfts-real/primary_confirmatory_result.json \
  --common-env-runs build/wfts-real/common_env_runs.csv \
  --common-env-receipt build/wfts-real/common_env_weather_receipt.json \
  --secondary-result build/wfts-real/secondary_route_night_result.json \
  --output build/wfts-real/deep_recurrent_site_result.json
```

Prospective informativeness gate:
- ≥50 deep k≥4 clusters;
- ≥100 shallow k=1–3 clusters;
- ≥5 taxa;
- ≥20 routes.

Exactly one secondary classification:
- `template_link_support`
- `template_link_non_support`
- `inconclusive_secondary_template_link`

This classification cannot alter the primary replication classification.

---

## 12. Interpretation matrix fixed before outcomes

### Primary = replication_support

Allowed:
> The NAAMP within-taxon multi-site concentration pattern transferred to the external WFTS dataset under the prospectively aligned endpoint/comparator.

Then report secondaries independently.

### Primary = informative_nonreplication_of_half_discovery_effect

Allowed:
> WFTS did not support a residual concentration effect at least half the NAAMP discovery magnitude under the aligned endpoint, delimiting transferability.

Do not call this proof of zero effect.

### Primary = inconclusive_nonpass

Allowed:
> WFTS did not pass the support gate, but precision was insufficient to exclude a discovery-scale residual; external generality remains unresolved.

Do not call this biological non-replication.

### Deep recurrent-site secondary

Report independently as support / non-support / inconclusive.

Never use it to rescue a non-PASS primary.

---

## 13. Hard stop after execution

After the frozen primary + predeclared secondary chain:

Allowed:
- descriptive tables;
- implementation debugging that corrects demonstrable bugs;
- manuscript reporting of the frozen results;
- explicit exploratory follow-up clearly separated from confirmation.

Not allowed:
- changing k≥4;
- changing prior-strong CI≥2;
- trying new rain windows and promoting the best;
- changing Daymet product;
- changing route/station eligibility because results are weak;
- changing q construction;
- changing simulations/seeds/tails;
- changing the 50%-of-NAAMP informativeness benchmark;
- changing the primary classification based on secondary results;
- searching another external network and reporting only the successful one.

---

## 14. Current external dependency

No public complete station-level WFTS response export has been found.

The remaining external dependency is therefore:

> **obtain the existing WFTS station-level historical response export plus route/station lineage metadata.**

Acquisition authority:
- `revision/WFTS_ACQUISITION_PACKET_V0_1.md`
- `revision/WFTS_DATA_REQUEST_TEMPLATE_V0_2.md`
- fallback: `revision/WFTS_OPEN_RECORDS_REQUEST_V0_1.md`

Do not request custom ecological summaries or ask WFTS staff to calculate any study endpoint.
