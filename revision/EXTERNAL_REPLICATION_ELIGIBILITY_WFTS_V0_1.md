# External replication eligibility audit v0.1

**Status:** structural eligibility only. No external outcome data have been inspected for the NAAMP multi-site concentration endpoint.

## Candidate

Wisconsin Frog and Toad Survey (WFTS)

Official programme sources:
- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/overview.cfm
- https://wiatri.net/inventory/frogtoadsurvey/Volunteer/manual.cfm
- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/analysis.cfm
- example route pages under https://wiatri.net/inventory/frogtoadsurvey/Volunteer/Maps/

## Match to the prospective specification

| Requirement | WFTS status | Evidence |
|---|---|---|
| repeated physical sites | PASS | permanent roadside routes with persistent station descriptions |
| >=3 sites per spatial unit | PASS | 10 listening stations per route |
| taxon-level acoustic state | PASS | species-specific call index 1–3 at each station |
| repeated surveys | PASS | each route surveyed three times per year; long-running annual programme |
| same-night route survey | PASS | all 10 sites must be surveyed on the same evening |
| physical-site identity | PASS | exact station descriptions and coordinates are maintained |
| historical site-use estimation | STRUCTURALLY PASS | long-running repeated routes provide prior years |
| external rainfall linkage | LIKELY PASS | survey date and location permit external weather linkage; exact data fields to verify before analysis |
| independent spatial folds | LIKELY PASS | routes provide natural spatial units for deterministic folding |
| raw outcome access | UNRESOLVED | public pages document summaries, protocol and route locations; no bulk public station-level download was located in the targeted audit |

## Important relationship to NAAMP

WFTS is historically related to NAAMP and uses a highly similar ten-stop calling-survey protocol.

Therefore, if WFTS station-level records overlap the exact NAAMP observations already used in frogcs, they **must not** be treated as an independent replication dataset.

Before any outcome analysis, perform a source-overlap audit using route IDs, dates, station identities and record counts.

Eligibility outcomes:

1. **No record overlap with frogcs NAAMP sample:** eligible as prospective external confirmation.
2. **Partial overlap:** remove all overlapping records before any endpoint calculation; then re-check power/coverage gates.
3. **Substantial/uncertain overlap:** classify WFTS as non-independent and do not use it as confirmatory evidence.

## Data-access gate

Do not inspect species × site outcome matrices until all of the following are documented:

- provenance and custodian;
- whether station-level records can be obtained;
- fields for route, station, survey date/run, species and call index;
- site identifiers/coordinates;
- overlap status with the frogcs NAAMP release;
- weather-linkage plan;
- deterministic fold assignment;
- minimum sample/route gates.

If station-level data require a request to Wisconsin DNR/WFTS, requesting the data does not violate the prospective freeze as long as no response endpoint is inspected before the above gates are locked.

## Frozen primary endpoint

Use the already frozen external specification:

`revision/PROSPECTIVE_EXTERNAL_REPLICATION_SPEC_V0_1.md`

The primary comparator remains:
- cross-fit taxon-specific rainfall response;
- strictly-prior taxon × physical-site propensity;
- reference-state persistence;
- pair-level magnitude matching.

The exact N,K exchangeable diagnostic is secondary only.

## Current classification

**STRUCTURALLY ELIGIBLE / OUTCOME ACCESS UNRESOLVED / INDEPENDENCE FROM NAAMP MUST BE AUDITED.**

No confirmatory claim is authorized yet.
