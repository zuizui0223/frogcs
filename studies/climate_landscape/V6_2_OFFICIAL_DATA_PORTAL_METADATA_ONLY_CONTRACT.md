# v6.2 — official live Flow-MER CKAN registry pre-read verification contract

**2026-10-10 JST.** Independent study PR #135, NOT JAE RC6. Frozen **before** querying newly discovered official Flow-MER Data Portal resource metadata through a live script. No new 2014–24 species/response observations or site identifiers are to be read.

## New actual index discovery

The **official [Flow-MER Data Portal](https://data.flow-mer.org.au/dataset/)** is an operational CKAN catalogue showing **69 public indexed datasets** (inspection 2026-10-10), with four result pages. The third page explicitly advertises:
- [Flow-MER Frog Abundance 2014–2024](https://data.flow-mer.org.au/dataset/flow-mer-frog-abundance), distinct in title from the prior `data.gov.au` CEWH Flow-MER Frog Abundance **2014–22** source (673 rows, version/audit pinned in v5.0–v5.8);
- [Basin flow gauges matched to Monitoring Sample Points](https://data.flow-mer.org.au/dataset/basin-flow-gauges-matched-to-monitoring-sample-points): catalogue states this is circa 2020 **qualitative matching of sample points to representative river gauges**, *not* point-specific wetland depth;
- [Flow-MER Data Standards](https://data.flow-mer.org.au/dataset/data-standards), PDF resource described as updated **2025-12-22**;
- separate open hydrological and vegetation layers, but no verified indexed raw matched **recorder × logger × wetland × recording-time frog-call** dataset on the four visible public listing pages.

The operational presence of a CKAN catalogue, even with a Data API, **does not establish** the older planning document's proposed secure Data Register is publicly exposing all acoustic archive records. Do not equate portal package count with accessible unregistered archive.

## Frozen first live check — metadata and structure ONLY

Use only `https://data.flow-mer.org.au/api/3/action/package_show?id=...` for these three exact known package slugs:
1. `flow-mer-frog-abundance`;
2. `basin-flow-gauges-matched-to-monitoring-sample-points`;
3. `data-standards`.

Return ONLY predeclared metadata fields:
- package ID, title, metadata_created/modified, notes length (NOT raw long descriptions), license_id, authoring agency name if present, declared temporal coverage fields by **field name only**;
- per-resource ID, format, size if provided, last_modified, datastore_active, MIME type, URL **hostname only** (NO location-bearing path), and filename **only if not containing sample-point identifiers**;
- for openly DataStore-backed resources, optionally query `datastore_search?resource_id=...&limit=0` strictly for **server total row count and field-name/type schema**, NOT any `records` (fail closed if record body nonempty);
- no CSV download, no species calls, tadpole CPUE, monitoring site labels, protected coordinates, individual station IDs, or full raw JSON logging;
- bounded HTTPS with host/redirect allowlist `data.flow-mer.org.au`; field/type names from schema only and packet size limits. Reject malformed source response and report errors instead of guessing counts.

## Interpretation and next data-authority gate

- **PASS new-vintage source *existence* only** if the original `package_show` title and source metadata indicate 2014–2024; that is not proof that actual dated surveys exist in **2023–24**, nor independent holdout or stable taxon/effort coding.
- **PASS machine-readable structure** if explicit schema fields or server-declared total are returned without opening observational records; do not infer number of changed records from row count alone.
- **New source-vintage correction:** legacy government `2014–22 673-row` is a *different exact data product/version*. Never silently replace historical v5.2 579-row table or treat newer data as untouched preregistered external replication. Newer dates may overlap 2026 pilot exposure, source publication updates may backfill old rows, and field key semantics might change.
- **Crosswalk boundary:** a **representative river gauge** is not a depth logger inside a frog wetland; it cannot satisfy local-hydrology sufficiency alone.
- The next genuinely informative *biological* step still requires station/wetland/time/recording/actual-depth original authorized dictionary and outcome-blind data availability from custodian, as in v6.1.

No user emails, logged-in accounts, private files, original audio or hydrology values. This prospective audit is **post-original-NAAMP-data**, independent and source-quality only. No edit to `paper/` or JAE main.
