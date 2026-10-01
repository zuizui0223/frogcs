# WFTS public data-access audit v0.2

**Status:** PUBLIC STRUCTURE VERIFIED / RESPONSE EXPORT REQUIRED  
**Audit date:** 2026-10-01  
**Outcome boundary:** no WFTS species × station × survey outcome matrix was inspected in this audit.

## Purpose

Determine, as far as possible from public information, whether the traditional Wisconsin Frog and Toad Survey (WFTS) can supply the exact structural and response grain required by the frozen external confirmation, and isolate the remaining data-access dependency before any ecological outcome is calculated.

This is a data-access audit, not a result analysis.

## Bottom line

WFTS is **structurally well matched** to the frozen confirmation. Public sources now establish all of the following:

1. traditional routes are fixed 10-station spatial units;
2. routes are surveyed three times per year;
3. station-level species call index 1–3 is the native recording grain;
4. blanks on the field sheet mean no call and can therefore be reconstructed as 0 once a valid complete route-run is established;
5. current physical station coordinates and descriptions are publicly exposed route-by-route;
6. historical route descriptions exist in Wisconsin DNR records, including old 10-site forms;
7. long-running route coverage is easily large enough that the frozen coverage gate is plausible;
8. DNR operates a secure WFTS electronic submission/account system and retains the monitoring records;
9. Wisconsin DNR has a formal public-records route for electronic records.

The remaining unresolved dependency is **access to the station-level historical response export and route/site change metadata**. No complete public download containing the traditional-route species × station × survey records was located in this audit.

Accordingly, the current classification is:

> **DESIGN_ELIGIBLE / PUBLIC_METADATA_SUFFICIENT / RESPONSE_EXPORT_REQUIRED**

It is not yet `CONFIRMATORY_DATASET_READY`.

## 1. Native survey grain is exactly the required grain

Official WFTS materials describe approximately 100 permanent roadside routes. Each traditional route has 10 listening stations, and the route is surveyed in early spring, late spring and summer.

At each station the observer records each calling taxon using the three-level call index:

- 1 — individual calls countable with no overlap;
- 2 — calls overlap but individuals remain distinguishable;
- 3 — full continuous chorus.

The 2022 manual further states that species not calling are left blank rather than entered as 0. Thus, for a survey that passes the complete-route validity rules, a blank species × station field has an explicit zero-call interpretation.

The official sample field sheet demonstrates the stored logical structure directly: one route/year, three dated runs, 10 site rows per run, water temperature, and a column for every frog/toad taxon with call-index values.

### Consequence

No ecological endpoint needs to be approximated from route totals. If the electronic records preserve the field-sheet grain, the frozen WFTS `taxon × 10-station call-index matrix` is native to the programme.

## 2. Physical station identity is publicly recoverable

The public WFTS route-map system exposes, for individual traditional routes:

- RouteID;
- county;
- Site 1–10;
- listening-point description;
- latitude;
- longitude.

Examples verified during this audit include RouteIDs 121, 123, 132, 211, 412, 432, 521, 531, 602, 603, 622, 654, 701 and 702.

Canonical public route-page pattern:

`https://wiatri.net/inventory/frogtoadsurvey/Volunteer/Maps/DrawMap.cfm?RouteID=<RouteID>`

The current coordinates therefore do **not** need to be supplied with the response export in order to link eligible present-day site identities to Daymet. A route/site table from DNR remains preferable because it can carry stable internal identifiers and history.

## 3. Historical site identity is an auditable issue, not a fatal ambiguity

The WFTS instructions require route descriptions precise enough that a later observer can survey the exact same locations. They also warn that replacing a bad site after a first run can void the first year's monitoring data and recommend selecting the ten permanent sites before reporting the year.

Historical Wisconsin DNR records in SWIMS include WFTS route-description forms. A verified 1994 Dodge County record contains ten site-by-site location and wetland descriptions.

This matters because the frozen confirmation requires the same physical stations in each matched pair and strictly-prior site history. Site replacement therefore needs to be treated explicitly rather than assumed away.

### Required metadata

The response request should ask for, if held:

- stable station/site identifier;
- route start/end years;
- site start/end years;
- station replacement or relocation flags;
- route-description revision date;
- invalidated run/year flag;
- route type (traditional versus 1997–1998 NAAMP/protocol or other survey type).

If no explicit replacement table exists, public/current coordinates plus archived route-description documents can support a secondary historical identity audit, but DNR's internal route/site history is preferred.

## 3b. Public RouteID numbering is highly structured but is not a substitute for a master table

Public/current route pages and historical forms indicate a stable RouteID convention in which the leading digits correspond to the Wisconsin county's alphabetical ordinal and the final digit identifies a route within that county.

Verified examples include:

- Burnett = 7th county → Route 73;
- Crawford = 12th → Route 121/123;
- Dane = 13th → Route 132, and the official sample sheet uses Route 134;
- Dodge = 14th → sample route 142;
- Forest = 21st → Routes 211/213;
- Oneida = 44th → Routes 441/442;
- St. Croix = 56th → historical Route 561;
- Sauk = 57th → historical Routes 572/573;
- Sheboygan = 60th → historical Route 601;
- Vilas = 64th → historical Route 641;
- Walworth = 65th → historical Routes 651/652;
- Washington = 67th → historical Route 671;
- Waupaca = 69th → historical Route 691;
- Waushara = 70th → current Route 701;
- Winnebago = 71st → historical Routes 711/712;
- Wood = 72nd → historical Route 721.

This convention is useful for auditing a supplied route master and detecting obvious route/county inconsistencies.

It should **not** be used to invent the current route master. Counties can have more than two routes, route numbers have changed historically, cross-county routes exist, and old reports also contain special/non-Wisconsin comparison identifiers. The authoritative traditional-route set must therefore come from DNR records or an official route listing.

## 4. Traditional routes must be separated from protocol routes

Official WFTS history records that in 1997–1998 an additional 80 NAAMP-based/protocol routes were run, and that a small number of those routes remain active.

The frozen external confirmation already restricts the primary test to **traditional WFTS routes**. A route-type field or an authoritative traditional-route list is therefore required before response loading.

This is a structural eligibility issue and must be resolved without looking at frog outcomes.

## 5. Coverage gate is highly plausible but not yet declared PASS

The frozen pre-response gate requires:

- at least 30 traditional routes in the principal history subset;
- at least 300 matched pairs with strictly-prior history;
- at least 10 routes in each deterministic fold.

Public programme history shows:

- statewide permanent coverage began in 1984;
- during 1984–1995, 58–100 routes were surveyed per year;
- 122 routes were run at least twice during 1984–1995 in the 1998 programme analysis;
- 73 routes were run in 2009 and 76 in 2008;
- current programme materials describe about 100 permanent roadside routes;
- a 2023 DNR release reported more than 10,500 survey nights and 103,400 sites surveyed since launch.

This makes the numerical gate very likely to be feasible **if** DNR can provide the historical station-level records and route identity is sufficiently stable. It is still not valid to mark the gate PASS until the response-blind structural export has been run through `preflight_wfts_structure.py`.

## 6. Electronic records clearly exist, but public download was not located

WFTS maintains a secure online account/data-entry page for volunteers. Wisconsin DNR also describes ATRI as the programme that collects monitoring data from statewide surveys and citizen-based monitoring projects.

The official WFTS analysis page states that occurrence is evaluated at each listening station and call index is summarized from the survey data. Historical peer-reviewed analyses also used site-level WFTS records.

The following public discovery paths were checked without locating a complete traditional-route row-level export:

- WFTS public website and survey-summary pages;
- WFTS secure public-facing login/data-entry landing page;
- Wisconsin DNR website/open-data searches;
- ArcGIS service searches;
- old USGS/Patuxent WFTS pages;
- USGS publication/data searches;
- Dryad/Zenodo/Figshare-style repository searches;
- GitHub public code/data search;
- Wisconsin DNR SWIMS;
- third-party WFTS visualizations.

The third-party Frog Night site is **not** suitable as a substitute: it states that route/month views are modeled estimates derived from statewide totals rather than observed local station counts.

### Current conclusion

Do not spend further analysis effort trying to reconstruct the response matrix from annual summaries or modeled web displays. Request the actual electronic export.

## 7. Best data-acquisition path

### First choice: direct research/data request

Current official programme contacts:

- `WFTS@wisconsin.gov`
- Andrew Badje, Wisconsin DNR Natural Heritage Conservation Biologist / WFTS coordinator
- `Andrew.Badje@wisconsin.gov`

Ask for an electronic export already held by the programme, not a bespoke ecological analysis.

### Second choice: Wisconsin DNR public-records request

Wisconsin DNR states that records in its possession are presumptively available unless exempt and identifies email as the preferred request route:

- `DNRRecordsResponse@wisconsin.gov`

For records already existing electronically, DNR's public-records notice says electronic copies are not charged on a per-page basis; location costs may apply for sufficiently time-consuming requests.

A narrowly specified database export is therefore a legitimate fallback if the programme cannot provide the data informally for research.

## 8. Minimum requested response export

Preferred long format:

| field | required? | purpose |
|---|---|---|
| route_id | yes | repeated spatial unit |
| route_type | yes or separate lookup | traditional-only gate |
| survey_year | yes | history and pairing |
| survey_period/run | yes | aligned seasonal stratum |
| survey_date | yes | Daymet linkage |
| station/site_id | yes | physical-site history |
| site_number | yes | ten-site completeness |
| taxon/species | yes | response matrix |
| call_index | yes | 0–3 acoustic state |
| valid_run flag | strongly preferred | protocol validity |
| valid_site flag | strongly preferred | site exclusions |
| station start/end or replacement metadata | strongly preferred | physical-site continuity |
| observer id | helpful | sensitivity only |
| begin/end time | helpful | audit/descriptive |
| recorded weather/temp | helpful | audit/sensitivity |

If the database is wide rather than long, that is acceptable. The request should explicitly ask how **non-detections/blanks** are represented.

## 9. Files to request in addition to responses

Preferably request:

1. response table/export;
2. route master table;
3. station master/history table;
4. route-type lookup;
5. data dictionary/codebook;
6. any invalid survey/run flags;
7. any station replacement/relocation log;
8. a description of missing-value coding.

Coordinates are helpful but not essential because current route coordinates are public.

## 10. Response handling once received

Do not browse the biological outcome manually.

Immediately:

1. save the raw bytes unchanged;
2. record filenames, sizes and SHA256;
3. inspect only schema/column names and structural fields;
4. construct a response-free structural table;
5. reconcile route type and physical-site history;
6. build Daymet covariates;
7. run `preflight_wfts_structure.py`;
8. if the frozen gate fails, stop before loading taxon/call-index values;
9. if it passes, freeze the preflight receipt and run v0.5 once on the exact same bytes.

## 11. What is now solved versus unsolved

### Solved from public information

- traditional design and survey periods;
- 10-site route grain;
- 1–3 call-index semantics;
- zero/non-call semantics on valid sheets;
- current route/station coordinates for public route pages;
- existence of historical route descriptions;
- likely route-scale sample size;
- presence of a long-running electronic programme database;
- direct programme contact;
- formal DNR public-records fallback.

### Still unsolved

- complete response-table access;
- full authoritative traditional-route list;
- stable internal station IDs across all years;
- route/station replacement history;
- exact structural row count by year/period before response loading;
- final response-blind coverage-gate result.

## 12. Decision

WFTS remains the correct first external candidate.

The next scientific step is **data acquisition and structural preflight**, not more NAAMP analysis and not manuscript re-framing.

No WFTS ecological outcome has been calculated in this audit.
