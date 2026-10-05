# WFTS receipt and structural-preflight protocol v0.1

> **CURRENT PROJECT STATUS (2026-10-05): SUPERSEDED / DO NOT EXECUTE.** The prospective WFTS replication was specified but not pursued; no WFTS data were requested or analysed. Current authority: `revision/WFTS_NOT_PURSUED_2026-10-05.md`. This file is retained only as historical prospective-design provenance.


**Historical status:** response-blind handling protocol fixed before any WFTS frog-response outcomes were received or inspected; retained for provenance only.

## Purpose

Define the exact handling sequence from receipt of WFTS files to the frozen v0.5 confirmatory analysis. This protocol protects the prospective external test from accidental manual outcome browsing or post-readback structural choices.

## Stage 0 — acquisition

Accept files only as existing records/exports. Do not ask WFTS/DNR staff to calculate:

- rain associations;
- route-level or species-level effect directions;
- third-and-later concentration;
- replication/non-replication;
- subsets with stronger effects.

Preferred files are listed in `revision/WFTS_DATA_REQUEST_TEMPLATE_V0_2.md`.

## Stage 1 — immutable byte receipt

Immediately upon receipt:

1. store the original files unchanged in a non-versioned/raw-data location;
2. do **not** open them in Excel, RStudio data viewer, pandas preview, GIS attribute table, or other row browser;
3. run `scripts/wfts/receipt_raw_wfts_files.py`;
4. record filename, byte size, SHA256, receipt time and source note;
5. preserve the receipt before any schema adapter is written.

The receipt tool reads file bytes only and does not parse schema or response values.

## Stage 2 — container/schema inspection

Allowed after the byte receipt:

- file type/container;
- sheet/table names;
- column names;
- declared field types;
- row counts;
- documentation/codebooks;
- missing-value codes described in documentation.

Still prohibited:

- printing response rows;
- frequency tables of taxa/call index;
- species × station matrices;
- route/year concentration summaries;
- wet/dry direction;
- any subset choice informed by frog values.

Create a schema receipt that documents which raw fields map to the frozen structural concepts.

## Stage 3 — freeze raw-to-canonical adapter

Before calculating an ecological endpoint, freeze a purely syntactic adapter that maps raw records into:

- `RouteID`;
- `SurveyPeriod`;
- `SurveyYear`;
- survey date;
- station order;
- physical SiteID;
- route type;
- validity/continuity fields.

The adapter may also define how the later response stage will map taxon names and call-index fields, but it must not select records according to response direction or magnitude.

Any taxonomic synonym table used later must be frozen before the endpoint is calculated.

## Stage 4 — route type and physical-site continuity

Resolve, response-blind:

1. traditional versus NAAMP/protocol/other route type;
2. exact ten-station completeness;
3. station replacements/relocations;
4. periods for which the same physical sites can be verified;
5. invalid/incomplete run flags.

Sources may include:
- DNR route/station master tables;
- current public WFTS route pages;
- archived route descriptions such as SWIMS records.

If a station change cannot be resolved without response inspection, exclude the affected structural pair according to the frozen physical-site rule rather than guessing identity.

## Stage 5 — weather construction

Using only structural station/date/coordinate records:

1. construct Daymet covariates with `scripts/wfts/build_daymet_covariates.py`;
2. retain raw weather/source SHA256 provenance;
3. build `rain_recency` and `tmean_run` exactly under `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`.

No frog-response column is needed or allowed in this stage.

## Stage 6 — response-blind structural preflight

Build the canonical structural input and run:

`scripts/wfts/preflight_wfts_structure.py`

The gate must be evaluated before `taxon_key` or `call_index` is loaded.

Frozen minimums:

- ≥30 traditional routes in the principal-history subset;
- ≥300 matched pairs with strictly-prior history;
- ≥10 routes in each deterministic fold.

Also verify:
- exact input SHA256;
- canonical schema SHA256;
- structural pair count;
- route-fold assignment;
- route/site continuity rules.

### If the gate fails

Stop.

Classify WFTS as structurally underpowered/ineligible for the frozen confirmatory test. Do not load frog responses and do not calculate the endpoint. Follow only the already-predeclared fallback rule.

### If the gate passes

Freeze and commit the preflight receipt before proceeding.

## Stage 7 — response unlock

Only after the Stage 6 receipt is frozen may the pipeline parse:

- taxon identity;
- call index / valid zero state.

At this point response access is authorized because all structural choices, endpoint, comparator, weather definition, fold assignment, coverage gate and interpretation rule are already fixed.

Do not manually browse the outcome before running the canonical pipeline.

## Stage 8 — one-shot confirmatory execution

Run exactly:

`scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`

against the exact runs/matrix bytes covered by the preflight receipt.

The confirmatory core must fail closed if:
- preflight read response values;
- gate did not pass;
- runs/matrix bytes changed;
- schema SHA changed;
- pair set changed.

Report the frozen decision exactly as returned:

1. `replication_support`;
2. `informative_nonreplication_of_half_discovery_effect`;
3. `inconclusive_nonpass`.

No outcome permits retuning of endpoint/comparator.

## Stage 9 — post-result audit

After the frozen primary result exists, exploratory diagnostics may be inspected only if clearly labeled post-confirmatory/exploratory.

Always preserve:
- original received bytes;
- byte receipt;
- schema receipt;
- raw-to-canonical adapter commit;
- structural preflight receipt;
- weather provenance;
- confirmatory output;
- software commit hashes.

## Manual-viewing rule

The purpose of the pre-response embargo is not secrecy for its own sake. It is to prevent human choices from adapting to the external outcome.

Accordingly:

> **Do not manually browse biological response values before Stage 8. Let the frozen pipeline be the first process that computes the confirmatory endpoint.**

After Stage 8, the response data may be inspected normally for interpretation, QA and disclosed secondary/exploratory work.

## Current access status

As of the public-data audit v0.2:

- public structural design: resolved;
- current public station coordinates: resolved;
- historical route-description existence: resolved;
- native call-index grain: resolved;
- response export: not yet obtained;
- structural gate: not yet run.

Therefore the next dependency is acquisition of the DNR-held station-level export, not further NAAMP analysis.
