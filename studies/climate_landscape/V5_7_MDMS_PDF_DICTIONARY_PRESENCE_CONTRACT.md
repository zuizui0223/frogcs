# v5.7 — official MDMS metadata-PDF dictionary availability gate (frozen before reading PDF)

**2026-10-10 JST; independent draft PR #135.** Locked JAE RC6 and all prior frog results remain unchanged. This is *source documentation retrieval and field-name presence inspection*, not biological analysis or independent-wetland identification.

## Precisely defined source

- Original Australian Government [MDMS sample points dataset](https://data.gov.au/data/dataset/mdms-monitoring-locations), resource listed as **Metadata description for MDMS Sample Points** (PDF), public CKAN resource ID `52a2a361-b1a0-466a-a971-8e046bf99e75`.
- Fetch only via the official `data.gov.au` HTTPS CKAN resource metadata and associated official file URL. Bound the PDF to 10 MB; fail closed if the host changes or the response lacks a true `%PDF-` header.
- No point GeoJSON, geometry, frog source CSV, outcomes or nonpublic files are part of this stage.

## Response-blind inspection

Use `pypdf` solely to extract PDF text *in memory*, record PDF byte length and SHA-256, page count, per-page extraction lengths, and presence/count of **literal column-name tokens**:
`DESCRIPTIO`, `ANAE_TYPE`, `DATATYPENA`, `SystemType`, `SAMPLECOUN`, `COMMENTS`, `POINT_CATE`, `PROGRAM`, `SAMO_ID`, and `NAME`.

Output only token hit counts, no raw lines, sampled site values, geographic words, personal names, coordinates, PDF metadata fields, or source text. A substring embedded in unrelated prose is *not* a verified schema definition. Flag `POSSIBLE_DICTIONARY_NEEDS_MANUAL_REVIEW` if tokens are present; otherwise `NO_EXACT_FIELD_DICTIONARY_SIGNAL_IN_EXTRACTED_TEXT`. If text is empty, classify `NO_EXTRACTABLE_TEXT`, not `NO_FIELD_DICTIONARY`.

If the source responds with an error or text cannot be safely extracted, record the failure without inferring anything about a source wetland-key field.

## Decision

Even a positive hit is only a **candidate source documentation route**. The previously identified 28 official Murrumbidgee frog monitoring points and their 16 distinct `DESCRIPTIO` values **remain 28 points of unknown ecological wetland membership**. Do not infer 16 wetlands, call 13 points one wetland, refit a biological model, or identify species-specific larvae.

Human inspection of the publication, under normal source rights and without sensitive site disclosure, and confirmation by CEWH are necessary before any point→wetland parent crosswalk can be declared verified. No email or records request is authorized or sent by this gate.
