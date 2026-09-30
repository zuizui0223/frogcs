# Prospective external replication candidate audit v0.1

**Status:** candidate eligibility and priority frozen before requesting or inspecting any external outcome data for the NAAMP within-taxon multi-site concentration claim.

The confirmatory endpoint and comparator are already fixed in:

`revision/PROSPECTIVE_EXTERNAL_REPLICATION_SPEC_V0_1.md`

No candidate outcome matrix has been opened.

## Priority rule

The first candidate that:
1. passes all structural/data-access gates,
2. is demonstrably non-overlapping with the frogcs NAAMP analytic sample, and
3. provides adequate route/site replication,

becomes the **one-shot primary external confirmation dataset**.

Do not choose the candidate after comparing endpoint results.

---

## Candidate A — Great Lakes Marsh Monitoring Program amphibian surveys (MMPFROGS)

### Public programme metadata

NatureCounts dataset:
- dataset code: `MMPFROGS`
- DOI: `10.71842/qshy-t720`
- access level: by request
- >100,000 records
- >1,300 locations
- 14 taxa
- Great Lakes basin, United States and Canada
- long-running multi-year programme
- stated target of three amphibian visits per year

Official/programme sources:
- https://naturecounts.ca/nc/mmp/datasets.jsp?code=MMPFROGS
- https://www.birdscanada.org/programs/marsh-monitoring-program

Historical MMP amphibian protocols specify:
- three survey nights per year;
- visits separated through the breeding season and keyed to temperature thresholds;
- fixed survey stations;
- species-specific call-level codes 0–3;
- code 3 = continuous/full chorus.

### Prospective-spec match

| Requirement | Status before data request |
|---|---|
| independent programme from frogcs NAAMP analysis | **LIKELY PASS** |
| repeated physical locations | **PASS at programme level** |
| species-level acoustic records | **PASS** |
| ordinal call state including full chorus | **PASS in protocol** |
| multi-year history | **PASS** |
| external rainfall linkage | **LIKELY PASS** from date/location |
| >=3 sites per repeated spatial unit | **MUST VERIFY in raw route/station fields** |
| stable route/site identifiers | **MUST VERIFY in raw data** |
| enough informative route-years | **MUST VERIFY before endpoint calculation** |
| raw data access | **AVAILABLE BY REQUEST, not yet obtained** |

### Main advantage

MMP offers substantially better independence from the NAAMP discovery process than another NAAMP-derived or state-partner route network.

### Main uncertainty

NatureCounts metadata describe 1–8 listening stations on routes, but the raw schema must show that station identities and route membership are retained in a form that supports repeated within-route multi-site matrices.

### Frozen priority

**PRIMARY CANDIDATE**, conditional on the raw-schema gate.

Do not request or inspect endpoint summaries until the schema/overlap/power gates below are signed off.

---

## Candidate B — Wisconsin Frog and Toad Survey (WFTS)

### Public programme metadata

WFTS:
- began statewide annual surveys in 1984;
- approximately 100 permanent roadside routes;
- 10 listening stations per route;
- three runs per year;
- five-minute calling surveys;
- species-specific call index 1–3;
- exact station descriptions and coordinates are maintained.

Official sources:
- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/overview.cfm
- https://wiatri.net/inventory/frogtoadsurvey/Volunteer/manual.cfm
- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/history.cfm
- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/analysis.cfm

### Structural fit

| Requirement | Status |
|---|---|
| repeated physical sites | **PASS** |
| 10 sites per route | **PASS** |
| species-level acoustic state | **PASS** |
| CI1–3/full chorus | **PASS** |
| same-night route survey | **PASS** |
| multi-year history | **PASS** |
| site coordinates/descriptions | **PASS** |
| rainfall linkage from date/site | **LIKELY PASS** |
| raw station-level bulk access | **UNRESOLVED** |

### Independence concern

WFTS is historically connected to NAAMP. The programme reports that NAAMP protocols were modelled from WFTS, and in 1997–1998 WFTS operated additional NAAMP-protocol routes; a small number reportedly continued later.

Therefore WFTS cannot be labelled independent merely because it is a separately named programme.

Before any outcome calculation:
- compare State / route / date / station identities with the complete frogcs NAAMP source;
- identify any WFTS records incorporated into the NAAMP release;
- exclude overlap before testing;
- if overlap cannot be ruled out, classify WFTS as non-confirmatory.

### Frozen priority

**SECONDARY CANDIDATE** because the structural match is excellent but independence requires a stricter source-overlap audit.

---

## Candidate C — British Columbia Marsh Monitoring Program amphibian surveys

NatureCounts dataset:
- dataset code: `BCMMP_FROGS`
- DOI: `10.71842/d69j-r378`
- began 2020;
- approximately 931 records, 148 locations, 9 taxa in current public metadata;
- standardized passive amphibian surveys;
- access by request.

### Frozen classification

**BACKUP / likely underpowered for the primary multi-site endpoint until raw route structure and informative sample size are verified.**

Do not use merely because Candidates A or B give an inconvenient result.

---

## Pre-access schema gate for the primary candidate

Before receiving/opening species outcomes, obtain a data dictionary or schema confirmation for:

- route or spatial-unit identifier;
- physical station identifier;
- survey date/time;
- survey/run/phenology identifier;
- taxon identifier;
- call-level/intensity value;
- observer identifier if available;
- station coordinates or a weather-linkable locator;
- missing/not-surveyed semantics;
- years of repeated observation.

### Required spatial coverage gate

Before endpoint readback, calculate using identifiers only:

- number of repeated spatial units with >=3 stable sites;
- number with >=5 stable sites;
- years per spatial unit;
- number of route-year/run comparisons with usable prior history;
- number of independent spatial folds.

Set the minimum evaluability threshold **before species/call-state outcomes are opened**.

If the candidate fails, declare it structurally ineligible rather than modifying the endpoint.

---

## Rainfall exposure gate

Rainfall exposure must be constructed without looking at the chorus endpoint.

Preferred:
- gridded weather source independent of the frog monitoring programme;
- exact local survey date;
- fixed wet-day threshold and antecedent window chosen before endpoint readback;
- same signed target-vs-reference definition as the NAAMP prospective specification where feasible.

Programme scheduling rules and temperature thresholds must be included as design covariates/sensitivities fixed before endpoint readback.

---

## Primary endpoint and comparator

No change from the frozen prospective specification.

Endpoint:
- route/cluster-new taxon;
- (k_i) target sites occupied;
- (e_i=max(k_i-1,0));
- within-taxon concentration (C = Σ_i choose(e_i,2)).

Principal comparator:
- opposite-fold taxon-specific rainfall response;
- strictly-prior taxon × physical-site propensity;
- reference-state persistence;
- pair-level magnitude matching.

The exchangeable exact N,K calculation is secondary only.

---

## One-shot confirmation rule

Candidate A is tested first **only if it passes all pre-outcome eligibility gates**.

If A is ineligible before outcomes are opened, proceed to B.

If A is eligible and is tested, its result is the primary external confirmation outcome whether positive, null or opposite-direction.

Do not switch to B after seeing A's endpoint in order to obtain a positive confirmation.

All subsequently tested eligible datasets are labelled additional replications, not replacements.

---

## Current decision

1. **MMPFROGS — first choice, schema/data request needed.**
2. **WFTS — second choice, excellent design but source-overlap audit mandatory.**
3. **BCMMP_FROGS — backup, likely smaller.**

No external outcome analysis has been performed.
