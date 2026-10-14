# v6.3 — Real 2014–2024 source registry identity, corrected CKAN slug, and metadata access STOP

**2026-10-10 JST. Independent frog mechanism draft PR #135.** This is a **factual source-provenance correction and original-source availability result**, not a frog ecological outcome. Submitted Journal of Animal Ecology RC6 `main` remains untouched.

## 1. Independently registered public source identity — POSITIVE

**University**: [Charles Sturt University, *Flow-MER Program Frog Abundance*](https://researchoutput.csu.edu.au/en/datasets/flow-mer-program-frog-abundance/):
- creator **Skye Wassens**;
- publisher **Commonwealth Environmental Water Holder**;
- made available **30 June 2024**;
- catalogue's declared temporal coverage **1 July 2014 – 30 June 2024**;
- declared external access target `https://data.flow-mer.org.au/dataset/flow-mer-frogs`.

**Australian Research Data Commons**: [*Flow-MER Program Frog Abundance*, Research Data Australia](https://researchdata.edu.au/flow-mer-program-frog-abundance/3535992):
- independent research registry number **`0e2db3d4-c13d-48f3-bdf2-ca546e4a87fa`**;
- confirms the same dataset title, author, publisher and temporal coverage;
- lists access classification **Open** and links to `data.flow-mer.org.au/dataset/flow-mer-frogs`.

These are reliable **metadata statements about a registered research dataset**, and they materially corroborate the formerly portal-only 2014–24 title. They do **not** prove that additional 2023–24 source observations are present, that original published rows were unchanged, that a 2014–24 CSV is currently downloadable, or that a source-level survey-opportunity denominator is available.

## 2. Important v6.2 error corrected

The prior v6.2 source probe used guessed CKAN package slug **`flow-mer-frog-abundance`**, based on a title-like URL rather than an authenticated source identifier. It received 403, as did two other catalogue package requests. **That specific query cannot be described as a successful request of the canonical 2014–24 frog package.**

The corrected, independently sourced slug is **`flow-mer-frogs`**. We retain the historical v6.2 audit and original errors for transparency; no analysis, model or data result is retroactively replaced.

## 3. Actual corrected original official API attempt — STILL 403

- **Pre-read contract:** [v6.3 canonical source URI and exact audit rules](V6_3_CANONICAL_2014_2024_FROG_SOURCE_URI_AND_METADATA_CONTRACT.md) committed before querying new source.
- **Auditable script:** `scripts/audit_correct_official_flowmer_frogs_slug_v63.py`.
- **Original live GitHub Actions run:** [**38058441199 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38058441199).
- **Only endpoint requested:** official HTTPS `https://data.flow-mer.org.au/api/3/action/package_show?id=flow-mer-frogs`.
- **Live result:** HTTP **403**, classified as `CORRECT_PACKAGE_API_403_METADATA_NOT_RETRIEVED`. The workflow's SUCCESS denotes *proper execution and fail-closed receipt*, **NOT successful retrieval**.
- No package metadata fields, row totals, column schema, licence/resource response, source observations, station names/coordinates or original recordings were returned. No record-level `datastore_search` was run.

**Do not equate HTTP 403 to a dataset-specific "closed" classification, invalid public registry record, missing data, or prohibition against legitimate approved use.** The endpoint's access restrictions may apply at the whole API/edge layer. No authentication circumvention or parallel endpoint probing is authorized by this audit.

## 4. Three separate data product claims must remain separate

| Evidence object | What it actually supports | What remains unverified |
| --- | --- | --- |
| data.gov.au CEWH Frog Abundance 2014–2022 | Prior actual public source: **673** records; 16-column source field schema, earlier v5.0–v5.8 audits; 579 selected Murrumbidgee post-filter rows | Survey-negative/opportunity ledger, independent wetland units, original tadpole field genus→species mapping |
| University + ARDC 2014–2024 registered dataset | **Public research dataset registration**, declared **2014–2024** coverage, canonical external slug **`flow-mer-frogs`**, classification **Open** | Whether full content actually includes 2023–2024 rows, original release date/version, identity/backfill of older rows, real downloadable file/signed access, validity of survey effort |
| v6.0 2016–2025 Murrumbidgee frog audio archive | Government monitoring plan and 2026 executed public pilot confirm historical recordings and classifier use | Genuine matched `wetland × recorder × depth logger × timestamp × valid audio/opportunity` source export and licence |

**None** of the three sources establishes independent confirmation of JAE RC6, species-specific reproductive payoffs, or a confirmed wetland-depth-versus-historical-use comparison. A new 2014–24 registration is not the same as an external independent monitoring programme.

## 5. Defensible next action and hard stop

Source research should now STOP repeated portal requests. There are only two active original *metadata questions*, included in the existing **single UNSENT** custodian inventory draft:

1. Is there a permitted, versioned official **2014–2024 Flow-MER Frog Abundance** metadata/download route; what changed relative to `data.gov.au` 2014–2022 (source row counts, actual time coverage, speciesCode, field stage and survey denominator, without releasing any observations in the initial enquiry)?
2. Is there a source-authenticated, permit-compatible 2016–2025 **recorder × valid recording opportunity × physical wetland × local depth logger × time** manifest and species detection QA ledger, with distinct overlapping wetland-year coverage, source field semantics and rights?

**Human approval is required before any external message.** If either answer is unavailable, downgrade the prospective ecological test; do not fabricate zeros, map gauge discharge to local water depth, or treat descriptive sound clips as independent wetland replicates.

No new frog outcomes downloaded or fitted, no metadata custodian contacted, no change to frozen manuscript/SI, no merge of draft PR into JAE RC6/main.
