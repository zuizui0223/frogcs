# WFTS raw-data intake protocol v0.1

**Status:** frozen before receipt of any WFTS frog-response file.

## Purpose

Record provenance and structural metadata for WFTS files **before opening or summarizing frog-response values**.

This intake step is separate from:
- the structural eligibility preflight;
- canonical-schema conversion;
- Daymet weather extraction;
- the confirmatory endpoint.

## Allowed intake operations

Before response readback, the intake process may inspect only:

- file name;
- byte size;
- SHA256;
- text encoding detectability;
- first non-empty line / header row;
- number of physical lines;
- ZIP/archive member names and member byte sizes, if an archive is supplied;
- obvious delimiter type;
- presence/absence of candidate field names in headers.

It must **not**:
- calculate species frequencies;
- inspect call-index distributions;
- compute route richness;
- compute station occupancy;
- compute rain-response direction;
- compute multi-site concentration;
- choose subsets based on frog-response values.

## Required receipt

For every received file, record:

- original file name;
- local immutable copy name;
- byte size;
- SHA256;
- acquisition date/time;
- sender/source;
- transport method;
- detected header fields;
- raw line count;
- whether the file appears compressed;
- if compressed, archive member names/sizes/hashes.

## Immutable copy rule

The first received bytes are the authority.

Do not overwrite them.

If WFTS staff later send a corrected file:
- retain both versions;
- hash both;
- document which version supersedes which and why;
- rerun structural preflight from the new bytes before any endpoint is opened.

## Header-based structural screen

After intake, classify each file as one of:

- candidate response data;
- route/station metadata;
- station coordinates;
- route-description/history metadata;
- observer/protocol metadata;
- data dictionary;
- unrelated.

This classification must use only file names and header/schema information, not response values.

## Transition to canonicalization

Only after the intake receipt is committed may a schema adapter be written.

If the raw schema differs from the frozen canonical schema, the adapter must:
1. map identifiers/columns without calculating the confirmatory endpoint;
2. document every transformation;
3. create a new canonical-file SHA256;
4. pass the outcome-blind structural preflight before the confirmatory core is allowed to load taxon/call-index values.

## Outcome embargo

The first time frog-response values may be parsed is the response stage of the frozen confirmatory pipeline, after:
- data intake;
- schema adapter freeze;
- Daymet weather build;
- canonical runs/matrix build;
- structural preflight PASS;
- SHA256 identity checks.

## Authority

Use:
- `scripts/wfts/intake_wfts_files.py`
- `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_1.md`

No WFTS response file had been received when this protocol was frozen.
