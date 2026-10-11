# v6.2 — REAL official Flow-MER Portal 69-entry inventory and API 403 result

> **Superseding v6.3 source-identity correction (2026-10-10):** The CKAN frog package slug `flow-mer-frog-abundance` used in this v6.2 run was **not independently verified**. Charles Sturt University and the Australian Research Data Commons both identify the canonical external dataset path as [`flow-mer-frogs`](https://researchdata.edu.au/flow-mer-program-frog-abundance/3535992). A separately frozen [correct-slug official API check v6.3](V6_3_REAL_CANONICAL_FROGS_SOURCE_AND_403_STOP.md) also returned **HTTP 403** ([real CI](https://github.com/zuizui0223/frogcs/actions/runs/38058441199)). This means package content and newer record schema remain **NOT RETRIEVED**; the registry's 2014–2024 coverage and `Open` access label are documentary metadata, not proof of a downloadable observational panel. Keep the v6.2 original run as a transparent historical audit, not an authoritative identity of the actual frog package. No animal data accessed and no JAE RC6 change.



**2026-10-10 JST. Independent draft PR #135 only; JAE RC6/main unchanged.** Newly browsed government/Flow-MER public index and a live **source-only CKAN API request** have been checked. No new frog observational data, water values, coordinates, source-site IDs, protected recordings or custodial responses were accessed.

## Actual operational official Flow-MER Data Portal — PUBLIC HTML verified

- [Live official Flow-MER CKAN portal](https://data.flow-mer.org.au/), linked from [Flow-MER's programme website](https://www.flow-mer.org.au/areas/murrumbidgee); its [public dataset index](https://data.flow-mer.org.au/dataset/) lists **69 datasets** on **four pages**.
- Public catalogue [page 3](https://data.flow-mer.org.au/dataset/?page=3) explicitly shows **Flow-MER Frog Abundance 2014–2024** with displayed CSV/PDF/HTML resources. That is **a newer labelled time range** than the separate `data.gov.au` old 2014–2022 frog release audited at 673 source rows in v5.0–v5.8. The new portal entry's actual animal-observation count, source dates in 2023–24, species code compatibility, denominator, completed site visits, rights and data transformations **HAVE NOT BEEN VERIFIED**.
- Same catalogue page 3 shows [Basin flow gauges matched to Monitoring Sample Points](https://data.flow-mer.org.au/dataset/basin-flow-gauges-matched-to-monitoring-sample-points), described as circa 2020 **qualitative mapping of monitoring sample points to *representative basin river gauges***. This **is not** an original `recording station ↔ same-wetland water-depth logger` key and **does not** satisfy local hydrology control in a frog acoustic analysis.
- [Data Standards](https://data.flow-mer.org.au/dataset/data-standards) are visibly offered as a downloadable official PDF updated **2025-12-22**, potentially supporting schema/metadata interpretation rather than acoustic observations.
- The four publicly indexed pages include spatial data, water/flow, frog-abundance, vegetation, birds, fish, and method standards, but **no indexed package clearly advertised a 2016–2025 `recorder × timestamp × species call × measured local depth` joined raw panel**. This is a bounded public-listing observation, **not proof that no internal archive or restricted database exists**.

## Live CKAN API attempt — executed, fail-closed

**Pre-read contract**: [v6.2 metadata-only source protocol](V6_2_OFFICIAL_DATA_PORTAL_METADATA_ONLY_CONTRACT.md), committed before live source queries.

**Executable**: [`scripts/audit_flowmer_public_ckan_schema_v62.py`](scripts/audit_flowmer_public_ckan_schema_v62.py) (only `package_show` and optional zero-row `datastore_search`, never animal records).

**CI**: [GitHub Actions run **38057752707 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38057752707). This **SUCCESS means the bounded QA executed successfully**, not that data were retrieved.

| Exact official package slug | HTTPS official API `package_show` result | What was actually established |
| --- | --- | --- |
| `flow-mer-frog-abundance` | **HTTP 403** | No live package metadata, actual newer row total or schema was retrieved |
| `basin-flow-gauges-matched-to-monitoring-sample-points` | **HTTP 403** | The publicly listed gauge-point dataset exists as catalogue text, but its source table was NOT opened |
| `data-standards` | **HTTP 403** | The publicly listed standards PDF exists as a resource listing, but no PDF was downloaded by CI |

Original artifact (GitHub Actions run): `FLOWMER_PUBLIC_REGISTRY_METADATA_ONLY_V62.json`. Because all three API queries returned 403, no optional zero-record `datastore_search` was executed.

**Access control is not biological absence.** Do not try to evade 403 or call these inaccessible API rows verified. The public HTML index is independent evidence of published catalogue entries, not a substitute for server JSON/resource access and verified data contents.

## Interpretive update and hypothesis protection

1. **Do NOT rewrite the old v5.2 579-row or 673-source-row Flow-MER results as if they refer to the 2014–2024 portal product.** Its contents and version compatibility remain unexamined.
2. **Do NOT call the 2014–2024 package an independent external replication or newly added valid 2023/24 observations.** Chronological title alone is insufficient: it may be a revised multi-year dataset with backfilled records, protocol drift, source carryover, and ambiguous site-level aggregation.
3. Even if the gauge crosswalk were public, representative river gauge flow is **not local logger depth** and cannot separate water arrival, local hydroperiod, sound cues, and recurrent site use without strong extra assumptions.
4. Public portal **existence** helps establish a legitimate place to ask for newer metadata. The decisive original source request remains **an authenticated recorder–depth logger–independent wetland × time opportunity manifest** and access/usage rights.
5. The v6.0 source-only **custodian enquiry is UNSENT**. If the author elects to send, it may now request the official newer `2014–2024` frog product's exact source version/resource metadata and the difference from the `2014–2022` original, in addition to the original audio-depth inventory, without requesting animal observations in the initial inquiry.

**Decision**: stop further website scraping/model fitting; keep the metadata-only no-outcome boundary. A source-resolved field dictionary or authorized public download and original wetland-unit mapping is needed before making biological comparisons. JAE RC6/main unchanged.
