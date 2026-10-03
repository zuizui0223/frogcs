# WFTS acquisition execution checklist v0.1

## A. Before contacting WFTS

- [x] public-data search exhausted
- [x] current coordinator verified
- [x] programme aliases verified
- [x] open-records fallback verified
- [x] request fields minimized to existing records
- [x] response-free receipt tool ready
- [x] schema-only inspector ready
- [x] raw-to-canonical rules frozen
- [x] mapping manifest template ready
- [x] public route metadata parser ready
- [x] route-master structural audit ready
- [x] Daymet adapter ready
- [x] response-blind structural preflight ready
- [x] confirmatory v0.5 implementation ready
- [x] unified real-data authority v0.3 frozen before WFTS outcomes
- [x] prospective common-environment v0.2 secondary specification frozen
- [x] response-free 1/3/7-day precipitation adapter ready and synthetic QA passed
- [x] prospective bounded route-night / far-lag secondary implementation ready

## B. Direct WFTS research-data request

Recommended routing:

- To: Andrew.Badje@wisconsin.gov
- Cc: WFTS@wisconsin.gov
- Cc: DNRWFTS@wisconsin.gov

Request authority:
- `revision/WFTS_DATA_REQUEST_TEMPLATE_V0_2.md`
- `revision/WFTS_ACQUISITION_PACKET_V0_1.md`

Tracking fields:

- [ ] request sent
- sent_at_utc: null
- sending account: null
- message-id / thread-id: null
- [ ] acknowledgement received
- acknowledgement_at_utc: null
- [ ] WFTS confirms data can be provided directly
- [ ] WFTS redirects request to records staff
- [ ] WFTS says requested records do not exist in exportable form

## C. Open-records fallback

Use only if direct research-data access cannot produce the existing export.

Authority:
- `revision/WFTS_OPEN_RECORDS_REQUEST_V0_1.md`

Tracking:

- [ ] open-records request sent
- sent_at_utc: null
- DNR case/reference number: null
- [ ] fee estimate received
- estimated fee: null
- [ ] narrowing requested by DNR
- [ ] records released
- released_at_utc: null

## D. Raw file receipt

Before opening any response table:

- [ ] original bytes saved unchanged
- [ ] source/sender recorded
- [ ] filenames recorded
- [ ] byte sizes recorded
- [ ] SHA256 recorded
- [ ] byte receipt created with `scripts/wfts/receipt_raw_wfts_files.py`

Receipt path:
- null

## E. Schema-only inspection

- [ ] file containers identified
- [ ] sheet/table names recorded
- [ ] column names recorded
- [ ] documented missing/non-detection codes recorded
- [ ] no biological response rows manually browsed
- [ ] schema receipt created with `scripts/wfts/inspect_wfts_schema_only.py`

Schema receipt path:
- null

## F. Raw-to-canonical freeze

Complete from schema/codebook/structural metadata only:

- [ ] response table identified
- [ ] route master identified
- [ ] station master/history identified
- [ ] route type mapping frozen
- [ ] survey period mapping frozen
- [ ] date parsing frozen
- [ ] SiteID construction frozen
- [ ] former RouteID lineage frozen
- [ ] first permanent year handling frozen
- [ ] blank-versus-missing call-index semantics frozen
- [ ] taxon synonym table frozen
- [ ] raw-to-canonical adapter code committed
- [ ] mapping manifest changed from TEMPLATE_NOT_FROZEN to FROZEN_BEFORE_RESPONSE_ENDPOINT

Mapping authority:
- `revision/WFTS_RAW_TO_CANONICAL_RULES_V0_1.md`
- `revision/WFTS_RAW_TO_CANONICAL_MAPPING_TEMPLATE_V0_1.json`

## G. Structural route/site audit

- [ ] traditional routes identified from authoritative metadata
- [ ] protocol/NAAMP routes excluded
- [ ] phenology/mink/ad hoc records excluded
- [ ] current route IDs checked against county-code convention
- [ ] former RouteIDs reconciled
- [ ] first permanent years applied if available
- [ ] ten physical sites verified per eligible run
- [ ] station replacements/relocations reconciled response-blind
- [ ] ambiguous physical-site pairs excluded fail-closed

## H. Weather build

- [ ] structural station/date table contains no frog-response values
- [ ] Daymet extraction completed
- [ ] Daymet source/version recorded
- [ ] Daymet/raw/output SHA256 recorded
- [ ] rain_recency calculated under frozen specification
- [ ] tmean_run calculated under frozen specification
- [ ] secondary 1/3/7-day precipitation exposures built from response-free structural station/date data
- [ ] secondary weather receipt and output SHA256 frozen

Authority:
- `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_3.md`
- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- `scripts/wfts/build_daymet_covariates.py`
- `revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_2.json`
- `scripts/wfts/build_common_environment_covariates.py`

## I. Response-blind structural preflight

Run:
`scripts/wfts/preflight_wfts_structure.py`

Freeze:

- [ ] eligible traditional routes count
- [ ] matched structural pairs count
- [ ] strictly-prior-history pair count
- [ ] deterministic fold route counts
- [ ] runs SHA256
- [ ] matrix/container SHA256
- [ ] schema SHA256
- [ ] preflight receipt committed

Frozen gate:

- ≥30 principal-history routes
- ≥300 principal-history pairs
- ≥10 routes per fold

Decision:

- [ ] PASS
- [ ] FAIL — structural/data-access ineligible; stop before response unlock

## J. Response unlock

Only after preflight PASS receipt is committed:

- [ ] taxon field parsed
- [ ] call-index field parsed
- [ ] documented blank non-detections converted to 0
- [ ] explicit missing/unknown retained as missing
- [ ] canonical taxon × 10-site matrices built
- [ ] no endpoint/comparator retuning

## K. One-shot confirmatory execution

Run exactly:
`scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`

- [ ] exact preflight-covered bytes used
- [ ] v0.5 completed once
- [ ] raw output frozen before interpretation
- [ ] decision recorded exactly as returned

Allowed decision:

- [ ] `replication_support`
- [ ] `informative_nonreplication_of_half_discovery_effect`
- [ ] `inconclusive_nonpass`

## L. After primary result

Only after K and after the primary result file is frozen:

- [ ] run `scripts/wfts/run_wfts_secondary_route_night_diagnostics_v0_2.py` on the exact preflight-covered primary bytes
- [ ] freeze the three-day common-environment comparator and named one-/seven-day sensitivities
- [ ] freeze bounded all-cluster and dry-route-silent route-night dependence
- [ ] freeze near 1–3 and far 7–9 station-number lag diagnostics
- [ ] freeze predeclared specieswise IID versus clustered uncertainty summary
- [ ] verify the secondary output records `primary_replication_classification_unchanged = true`
- [ ] inspect response values normally for non-gating descriptive audit
- [ ] label any additional unplanned analysis explicitly exploratory
- [ ] update manuscript interpretation only after the primary + predeclared secondary WFTS outputs are frozen

## Current state

As of 2026-10-03:

> **Waiting on external acquisition only.** The primary confirmation and the prospective common-environment / bounded route-night / far-lag secondary chain are frozen and implemented before WFTS outcome access.

No unresolved same-data NAAMP analysis is required to define the WFTS tests.
