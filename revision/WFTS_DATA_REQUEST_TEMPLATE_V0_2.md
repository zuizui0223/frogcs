# WFTS data request template v0.2 — station-level historical export

**Purpose:** obtain the existing station-level WFTS records required for the already-frozen prospective external confirmation.

**Do not request:** effect summaries, rain associations, positive/negative directions, species drivers, or any calculation of the endpoint.

## Preferred recipient

Wisconsin Frog and Toad Survey / Wisconsin DNR Natural Heritage Conservation

Current direct contact reverified on 2026-10-04 from the Wisconsin DNR 2026 WFTS release:

- coordinator: Andrew Badje, `Andrew.Badje@wisconsin.gov`

Historical programme aliases remain available as optional CCs:
- `WFTS@wisconsin.gov` — 2022 WFTS manual
- `DNRWFTS@wisconsin.gov` — 2025 brochure PUB-NH-931

Recommended first message: send directly to Andrew Badje. Copying the historical programme aliases is optional; successful routing does not depend on them.

If a direct research-data request cannot provide an existing electronic export, the same narrowly specified record set can be requested through Wisconsin DNR Open Records at `DNRRecordsResponse@wisconsin.gov`.

Contact-route verification: `revision/WFTS_CONTACT_ROUTE_VERIFICATION_2026-10-04.md`

## Suggested research-data request

**Subject:** Request for station-level Wisconsin Frog and Toad Survey historical data export

Dear Wisconsin Frog and Toad Survey team,

I am preparing a prospective external replication using the traditional Wisconsin Frog and Toad Survey. The analysis endpoint and decision rules have already been fixed before inspection of any WFTS species × station × year outcomes.

I am writing to ask whether the existing electronic station-level WFTS records can be provided for research use. I am interested only in the traditional 10-stop calling routes, ideally for all available years from 1984 through the latest completed season.

The minimum information needed is:

- route identifier;
- indication of route type, so traditional routes can be distinguished from NAAMP/protocol, phenology, mink-frog or other route types;
- survey year;
- survey period/run (early spring, late spring, summer);
- survey date;
- station/site identifier and site number;
- species/taxon identity;
- station-level call index (1–3), including documentation of how non-detections/blanks are represented.

If available, the following structural metadata would be especially helpful:

- route master table, including former/legacy RouteID and first permanent year if those fields exist;
- station master table with stable internal site identifiers;
- dates when routes or stations began/ended, including the first year a route was treated as permanent;
- station replacement, relocation or renumbering history;
- flags for invalid/incomplete surveys or individual stations;
- a data dictionary/codebook and missing-value definitions.

Observer ID, survey start/end time, recorded temperatures, wind and sky variables would also be useful for audit or sensitivity analyses, but they are not required for the primary replication.

Current station coordinates and descriptions are publicly available on the WFTS route-map pages, so coordinates are helpful but not essential if a stable station identifier and route/site history can be supplied.

A CSV, XLSX, database export, or the programme's existing native electronic format would all be suitable. A long table is convenient but not required; I can reshape a wide field-sheet-style export.

To preserve the prospective nature of the study, please **do not provide any summary of whether the focal pattern is present, any comparison with rainfall, or any species-level effect direction**. I would prefer the raw records and documentation only.

Thank you for maintaining this unusually valuable long-term monitoring programme and for considering the request.

Sincerely,

[NAME]  
[AFFILIATION]  
[CONTACT]

## Narrow public-records fallback

If an informal research-data export is unavailable, request records rather than an analysis.

Suggested wording:

> Please provide an electronic copy/export of the Wisconsin Frog and Toad Survey traditional-route station-level calling records held by Wisconsin DNR for 1984 through the latest completed season, together with available route/station lookup tables and data documentation. I am requesting existing records in their existing electronic form; I am not asking DNR to calculate any ecological summary or create a new analysis.

Scope fields:

- traditional route identifier / route type;
- year and survey period;
- survey date;
- station/site identifier or site number;
- species/taxon;
- call index;
- valid/incomplete survey flags;
- route/station replacement or change metadata;
- codebook/missing-value definitions.

If narrowing is needed for extraction cost, priority order is:

1. traditional-route response table;
2. route-type lookup;
3. station/site history table;
4. data dictionary;
5. ancillary observer/weather fields.

## Receipt procedure

When files are received:

1. do not open them in a spreadsheet for ecological browsing;
2. save original bytes unchanged;
3. record sender/source, receipt time, filename, byte size and SHA256;
4. inspect only file container, schema and column names first;
5. identify the structural columns needed by `preflight_wfts_structure.py`;
6. freeze any purely syntactic raw-to-canonical adapter before outcome calculation;
7. run the response-blind structural gate before reading taxon/call-index values.

## Why coordinates are no longer a blocking request field

Public WFTS pages expose current Site 1–10 descriptions and latitude/longitude for individual RouteIDs. Historical DNR route-description records also exist in SWIMS. Therefore coordinate delivery from the response database is preferred for provenance but is not required to start structural reconciliation.

## Outcome boundary

The requester should not ask WFTS staff to identify:
- which years are wetter/drier based on frog responses;
- which taxa respond positively;
- whether third-and-later concentration occurs;
- whether the NAAMP result replicates;
- which subset gives the strongest result.

Those are outputs of the frozen analysis, not data-access questions.
