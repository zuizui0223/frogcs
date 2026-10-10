# v5.5 — Government MDMS source sample-point identity crosswalk (source-only)

**2026-10-10 JST — prior to obtaining any MDMS geometry/label join.** Independent exploratory frog study PR #135; locked JAE RC6/main remain unchanged.

## New original source

The Australian Government CEWH [MDMS sample points (Flow-MER monitoring locations)](https://data.gov.au/data/dataset/mdms-monitoring-locations) is a published government monitoring-site **GeoJSON**, including LTIM 2014–19, Flow-MER 2019–23 and hydrological model nodes. It is **not merely a cartographic image**, and its existence opens a *possible* primary-source site identity check for the [Flow-MER Frog Abundance 2014–22](https://data.gov.au/data/dataset/flow-mer-frog-abundance) `SamplePoint` labels.

**Caution:** even an exact label match between resources does not prove a physical wetland identity, identity through time, biological independence, equal sample coverage, or that sample points correspond one-to-one to the original Wassens et al. 12 core wetlands or Ocock's 29 sites. The MDMS data may have a different version and include gauge/model nodes irrelevant to frog sampling.

### Actual original MDMS file and source property schema (verified before join)

[Original official GeoJSON schema CI 38014708544 — SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38014708544) successfully fetched the actual **435,791-byte** [government `MDMS_Sample_Points_extracted_24Dec2022.geojson`](https://data.gov.au/data/dataset/mdms-monitoring-locations) and inspected **681 point features**, without emitting individual names or coordinate values. It contains source property **`NAME` (681 nonmissing)** and **`SAMO_ID` (681 nonmissing)**, plus `PROGRAM`, `POINT_CATE`, `DESCRIPTIO`, other fields and geolocation properties. `NAME` and `SAMO_ID` are *candidate* source label/name and ID keys, respectively; source semantics and physical-site unit identity are still not authenticated. The spatial file's date (extracted 24 Dec 2022) is a separate version from the frog record source.

**Before viewing join results**, use source-only exact normalized `SamplePoint` string matching against `NAME` and `SAMO_ID` **separately**. No fuzzy, nearest-location, geometry or derived ID join. Report match cardinality, key duplicates and unmatched counts **only**, by broad `Program` label. A match does not prove one physical wetland per point.

## Source-only independent authentication plan

The primary original government GeoJSON resource entry is `35b2b6d7-2557-49c9-bcc0-af98d17cb49a`, from the official MDMS dataset listing. First query its **CKAN resource_show metadata** for actual format/content URL, declared size, CKAN archival status and update date. Never use the reported Web Feature Service blindly to infer original field-site IDs.

If the official material is safely available as JSON under a bounded byte cap, inspect **properties keys** of GeoJSON features and the data-relevant label identifiers **in memory**, without persisting or printing coordinates/site names/geometry. Only then query the frog source with CKAN projection `Program,SamplePoint` (no fauna responses, site GPS or identifiers in logs), derive distinct source sample labels, and evaluate:
1. exact normalized **casefold/space-trimmed** label matches only for the MDMS source attribute **explicitly described as a sample point label** in official metadata; do not match to arbitrary free text or description;
2. matched, unmatched and *ambiguous* site-label counts by **broad government Program**; duplicates in MDMS within the same normalized key must not be promoted to independently verified physical wetlands;
3. source version mismatches (frog CSV 2014–22, MDMS GeoJSON extracted 24 Dec 2022 and catalogue updates afterwards), geometry-bearing features, missing project/site ID, and whether the MDMS labels are a potentially useful external site alias crosswalk.
4. Field-level `speciesCode`↔original fyke-net larval taxon crosswalk is **NOT expected in a geographical MDMS sample-point file**. Do not claim that finding a site alias solves genus-pooled *Limnodynastes* larvae.

**Absolute source protection:** never publish any individual site label, species/coordinate value, point location, lat/long, WKT, geometry, or a reversible site hash; output aggregate counts and field/property **names only**. Do not attach/download private records. Fail closed on unknown official URL host, unexpectedly large GeoJSON or unknown feature properties. A failed API route indicates access/format limitations, not biological site mismatch.

## Ecological decision

- If exact original site-label linkage is source verified, we can say the government public records share a *name-level sample-point system*. It is still necessary to check physical wetland uniqueness, naming continuity, and original field monitoring event identities before revisiting 24-cluster bootstrap inference.
- If the official site label is not available, sample-point identity and physical independent unit stay **UNRESOLVED**; do not improvise nearest-coordinate matches.
- In either case, v5.2's −16.1pp pooled / +19.8pp same source-label repeated-pair sign flip stays *table-level only*. Stage-taxonomy assignments, sampling effort, survey-negative opportunities, pond water availability and relevant time lags remain unproven.

Original external-source links: [CEWH MDMS](https://data.gov.au/data/dataset/mdms-monitoring-locations), [CEWH Flow-MER frog](https://data.gov.au/data/dataset/flow-mer-frog-abundance), [v5.4 larval-genus identity audit](V5_4_REAL_GENUS_CPUE_TIE_CLASSES_AND_SOURCE_CORRECTION.md). No external email sent.
