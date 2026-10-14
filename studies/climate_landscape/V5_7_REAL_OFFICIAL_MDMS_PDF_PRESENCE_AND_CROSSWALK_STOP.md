# v5.7 real official MDMS metadata PDF — field presence, not source wetland crosswalk

**2026-10-10 JST — source-only real-document retrieval.** Independent frog mechanism draft PR #135; no change to the JAE RC6 paper, SI, conclusions, or source NAAMP analyses.

## Original government document actually obtained

- [Australian Government MDMS sample points listing](https://data.gov.au/data/dataset/mdms-monitoring-locations) provides resource **"Metadata description for MDMS Sample Points"**, CKAN resource ID `52a2a361-b1a0-466a-a971-8e046bf99e75`.
- [Real GitHub Actions run **38035612098 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38035612098), under [pre-read frozen v5.7 contract](V5_7_MDMS_PDF_DICTIONARY_PRESENCE_CONTRACT.md), actually downloaded the official PDF from an allowlisted government HTTPS address.
- Source is **242,037 bytes**, **2 PDF pages**, PDF SHA-256 **`b802f313e58981e6919baa08a300303adeca86ea451a630c06c6b8ba63509b7a`**. PDF text extractor returned 2,697 and 1,642 characters on those pages.
- This run did not inspect the frog biological dataset, GeoJSON site values, locations, original response data, or put PDF source text in logs; only official metadata **field name hit-counts**.

## Exact-string token presence only

| Public MDMS property name | Literal field-name hits in extracted official PDF text |
| --- | ---: |
| `DESCRIPTIO` | 1 |
| `DATATYPENA` | 1 |
| `SAMPLECOUN` | 1 |
| `NAME` | 6 |
| `PROGRAM` | 8 |
| `SAMO_ID` | 0 |
| `ANAE_TYPE` | 0 |
| `SystemType` | 0 |
| `POINT_CATE` | 0 |
| `COMMENTS` | 0 |

**Crucial:** a literal token appearing in an extractable PDF does not establish that it is a documented field definition, a valid parent-wetland identifier or a stable site key. Zero hits is not proof the field is undocumented in all versions, and no PDF excerpt was semantically verified.

## Identifiability conclusion

The v5.6 source property summary remains: of 28 Murrumbidgee official frog-linked **point features**, `DESCRIPTIO` has 16 nonempty distinct values and one value shared by 13 points. There is **no** authenticated reason to interpret 16 as the number of wetlands or 13 as points in one wetland. Source data product versions and site membership across 2014–2022 also remain unverified.

A **non-sensitive CEWH original `NAME / SAMO_ID`→independent ecological wetland unit crosswalk**, field definitions, and survey-point temporal continuity are still essential. Equally essential for any reproductive-payoff claim: original adult census effort/opportunity records and larval stage-to-species assignments, especially genus-pooled `Limnodynastes`. Never infer conspecific larval recruitment from the public table-level 579-row sign reversal.

## Next bounded decision

The public page identifies the responsible data contact as `cewomonitoring@dcceew.gov.au`. The metadata-only, no-coordinates source-enquiry **draft is prepared but NOT SENT** under `V5_7_CEWH_MINIMAL_SOURCE_DICTIONARY_REQUEST_UNSENT.md`.

No more frog outcome re-fitting, spatial clustering or wetland count estimation from name/description similarity is warranted. An authorized external answer is needed for a biological go/no-go.
