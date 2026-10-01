# Wisconsin DNR open-records request — WFTS electronic records v0.1

**Use only if the direct WFTS research-data request cannot provide the existing electronic export.**

Recipient:

`DNRRecordsResponse@wisconsin.gov`

Wisconsin DNR identifies email as the preferred and most efficient route for public-records requests.

## Suggested subject

Public records request — Wisconsin Frog and Toad Survey traditional-route electronic records

## Suggested request

Dear DNR Open Records Coordinator,

I am requesting an electronic copy of existing Wisconsin Frog and Toad Survey records held by the Wisconsin Department of Natural Resources for the traditional 10-stop calling-survey routes.

I am seeking existing records in their existing electronic form. I am **not** asking DNR staff to perform an ecological analysis, calculate trends, summarize effects, or create a new research product.

### Primary requested records

For the traditional Wisconsin Frog and Toad Survey driving routes, from the earliest electronically available records through the latest completed season, please provide the existing station-level survey records containing, where maintained:

- route identifier;
- route type/classification;
- survey year;
- survey period/run;
- survey date;
- station/site identifier and/or site number;
- species/taxon identity;
- call index or recorded calling-abundance value;
- valid/incomplete survey or station flags.

### Structural lookup records

Please also provide existing route/station lookup or history records, where maintained, including:

- route master table;
- former or legacy route identifier;
- first year the route was treated as permanent;
- route start/end dates;
- station master table;
- station start/end dates;
- station replacement, relocation or renumbering history;
- route-description revision dates;
- traditional versus NAAMP/protocol/phenology/mink/other survey type.

### Documentation

Please provide any existing:

- data dictionary/codebook;
- documentation of missing-value or non-detection coding;
- database/export field definitions;
- documentation identifying invalid or incomplete survey records.

### Preferred format

An existing CSV, XLSX, database export, text export, or other existing electronic format is acceptable. There is no need to convert the records into a custom format if doing so would require additional work.

If some requested fields are held in separate existing tables, providing those tables separately is fine.

### Scope clarification

This request is limited to records already held by DNR. I am not requesting:

- analysis of rainfall;
- species trend summaries;
- calculation of multi-site concentration;
- interpretation of whether any ecological hypothesis is supported;
- bespoke joining or reshaping beyond an existing export if that would constitute creation of a new record.

If the request as written would require substantial location work, I would appreciate an estimate and an opportunity to narrow the request before incurring a charge.

Electronic delivery is preferred.

Thank you for your assistance.

Sincerely,

[NAME]  
[AFFILIATION]  
[EMAIL]

## Narrowing order if DNR asks to reduce scope

Preserve, in this order:

1. station-level traditional-route response records;
2. route master with route type;
3. station/route lineage and replacement history;
4. data dictionary/missing-value documentation;
5. ancillary observer/weather fields.

Ancillary observer/weather fields can be dropped first because external Daymet weather is already frozen for the confirmatory analysis.

## Why the request includes early years

WFTS began experimental surveys in 1981 and standardized permanent statewide coverage in 1984. Early programme documentation explicitly records former RouteIDs and first permanent years. Requesting the earliest electronically available records allows the structural preflight to use documented permanence/lineage rules rather than inferring them from later response values.

## Handling boundary after receipt

Received files must first be processed by:

1. `scripts/wfts/receipt_raw_wfts_files.py`;
2. `scripts/wfts/inspect_wfts_schema_only.py`;
3. the frozen raw-to-canonical mapping manifest;
4. response-blind route/site continuity audit;
5. `scripts/wfts/preflight_wfts_structure.py`.

Frog-response rows are not to be manually browsed before the structural gate is frozen.
