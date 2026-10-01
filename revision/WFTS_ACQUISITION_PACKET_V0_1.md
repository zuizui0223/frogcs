# WFTS acquisition packet v0.1

**Status:** ready to send; no WFTS frog-response outcome has been inspected.

## Objective

Obtain the existing electronic traditional-route WFTS records needed to run the already-frozen external confirmation. Do not ask DNR/WFTS staff to calculate any ecological result.

## Current official contacts

### Primary coordinator

Andrew Badje  
Wisconsin DNR Natural Heritage Conservation Biologist / WFTS coordinator  
`Andrew.Badje@wisconsin.gov`  
715-921-5886

Verified in Wisconsin DNR's 26 March 2026 WFTS volunteer release.

### Programme aliases

- `WFTS@wisconsin.gov` — listed in the 2022 WFTS manual.
- `DNRWFTS@wisconsin.gov` — listed in the 2025 WFTS brochure (PUB-NH-931).

Because both programme aliases appear in recent official material, the recommended research-data request is:

**To:** Andrew.Badje@wisconsin.gov  
**Cc:** WFTS@wisconsin.gov; DNRWFTS@wisconsin.gov

### Public-records fallback

Wisconsin DNR Open Records Coordinator  
`DNRRecordsResponse@wisconsin.gov`  
608-266-2177

Wisconsin DNR states that email is the preferred and most efficient public-records request route.

## Send order

1. Send the direct research-data request from `revision/WFTS_DATA_REQUEST_TEMPLATE_V0_2.md`.
2. Request an **existing electronic export**, not a custom analysis.
3. Ask for response table + route master + station history + codebook together.
4. If WFTS can provide access directly, stop there.
5. If WFTS says the records must go through records staff, submit the narrow open-records fallback.
6. Do not broaden the request to annual summaries, modeled displays, or bespoke effect calculations.

## Files/fields requested

### Essential response records

- traditional route identifier;
- route type;
- survey year;
- survey period/run;
- survey date;
- station/site identifier;
- site number;
- species/taxon;
- call index;
- valid/incomplete run flags if present.

### Essential structural lineage

- route master;
- former/legacy RouteID if present;
- first permanent year;
- route start/end dates;
- station master;
- station replacement/relocation/renumbering history;
- route-description revision dates;
- traditional versus NAAMP/protocol/phenology/mink/special survey type.

### Documentation

- data dictionary;
- missing/non-detection coding;
- field meanings;
- database/export notes.

### Helpful but not primary

- observer ID;
- route start/end time;
- recorded air/water temperature;
- wind;
- sky/weather notes.

Current coordinates are helpful but not required because public WFTS route pages expose Site 1–10 locations for many current RouteIDs.

## Why this request is narrow and defensible

Public WFTS material already establishes:

- approximately 100 permanent traditional roadside routes;
- exactly ten listening stations per traditional route;
- three annual survey periods;
- native station-level call index 1–3;
- zero/non-call semantics via blank cells on valid field sheets;
- current public route/site coordinate pages;
- historical route descriptions;
- explicit route-lineage/permanence documentation;
- an electronic programme database;
- sufficient historical scale to make the frozen coverage gate plausible.

Therefore DNR is not being asked to create a new research product. The unresolved dependency is an export of records the programme already collects/maintains, plus structural lookup metadata.

## Public-search stop rule

Public discovery has been exhausted across:

- WFTS current/public site;
- WFTS secure landing page;
- WFTS annual summaries;
- WFTS route map pages;
- legacy USGS/Patuxent pages;
- USGS data catalog/data releases;
- Wisconsin DNR data/search pages;
- government/open-data searches;
- major research repositories;
- GitHub/public code search;
- Wisconsin SWIMS;
- indexed file-type searches.

No complete public traditional-route station-level response export was found.

Separate USGS Upper Midwest ARMI frog-calling datasets exist, but they are not the traditional WFTS long-term route series and must not be substituted post hoc for the frozen WFTS candidate.

## Handling once received

1. save original bytes unchanged;
2. run `scripts/wfts/receipt_raw_wfts_files.py`;
3. run `scripts/wfts/inspect_wfts_schema_only.py`;
4. freeze a raw-to-canonical adapter without browsing response rows;
5. audit route type and site continuity;
6. construct Daymet structural covariates;
7. run `scripts/wfts/preflight_wfts_structure.py`;
8. freeze the preflight receipt;
9. only if PASS, unlock taxon/call-index parsing and run v0.5 once.

Full handling authority:

`revision/WFTS_RECEIPT_AND_PREFLIGHT_PROTOCOL_V0_1.md`

## Evidence references

- current design: WFTS Survey Overview;
- current coordinator: Wisconsin DNR WFTS release, 2026-03-26;
- WFTS programme email: WFTS Survey Manual (2022);
- updated brochure alias: WFTS brochure PUB-NH-931 (2025);
- open-records route: Wisconsin DNR Public Records Request page;
- data-analysis grain: WFTS Analysis page;
- route permanence/history: WFTS Survey History and historical WFTS reports.
