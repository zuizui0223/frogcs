# v4.3 — Official NSW BioNet Species Sightings data standard 6.3: correction of frog-call joins

**Audit date:** 2026-10-09 JST. **Official source:** NSW DCCEEW, [BioNet Species Sighting Data Standard v6.3 (117 pages), 6 February 2026](https://www.environment.nsw.gov.au/sites/default/files/2026-02/bionet-species-sighting-data-standard-6-3-260021.pdf). The source is a published **data dictionary**, not a query to real frog sightings. **No actual amphibian records were read.**

**Governance:** separate source-analysis branch and PR #135, not JAE RC6, whose submitted manuscript/main remains unchanged.

## The new decisive correction

A successful **OData `$metadata` schema check** (124 `SpeciesSightings_CoreDataExtended` properties; [source-only CI 37800327766](https://github.com/zuizui0223/frogcs/actions/runs/37800327766)) verified **column presence** only. The official 2026 data standard now resolves critical **meanings**:

| Public column | Official normative definition / location in 117-page standard | Allowed use in frogcs-type data work | Forbidden substitution |
| --- | --- | --- | --- |
| `abundanceScore` | **PDF p. 56** (printed standard p. 52): *number of individuals in a PLANT species present in a plot according to scoring system allocated to the survey*, optional; integer example 3. | Plant-survey abundance only unless a **separate, original project-specific dictionary** explicitly establishes an amphibian recoding. | **Never** automatically map to frog CallingIndex or the Ocock 5-minute frog calling categories. |
| `individualCount` | **PDF p. 52** (printed p. 48): number of organisms represented as present at the occurrence. | Recorded individual count with its original method and detection limitations. | Never assume an ordinal calling category or a metamorph/recruitment count. |
| `eventID` and `visitID` | **PDF p. 40** (printed p. 36): **duplicate unique keys for the same census**, which is a temporally distinct assessment within a survey at a designated site. Optional and access-limited. | One alias-checked visit/census key when actually present and matching. | **Never** count both fields as two independent visit IDs; never assume all visits are represented by sighting records. |
| `surveyID` | **PDF p. 45** (printed p. 41): survey identifier, where a survey is activity undertaking observations at one or more sites; optional and possibly withheld. | Survey grouping key with an independent census/visit denominator. | Never treat `surveyID` alone as one individual visit or as a physical site ID. |
| `occurrenceStatus` | **PDF p. 52** (and legacy PDF p. 78): controlled presence/absence status; **Present / Absent** are defined values. | Preserve explicit `Absent` as **recorded taxon absence**, conditional on valid taxon, census key, protocol and provenance. | **Never** manufacture `Absent` for a missing species sighting row, skipped/noise-masked visit or all unrecorded species. Not sufficient to prove *acoustic silence* versus true species absence. |
| `samplingEffortValue` and `samplingEffortUnit` | **PDF pp. 42–43** (printed pp. 38–39): optional quantitative effort and its unit; units include Minutes, Hours, Person Hours, Trap Nights, Units Unknown. Often withheld for sensitive fauna. | Compare only after checking BOTH fields, observation protocol, expected five-minute audio effort, and source-specific missing codes. | A lone number, a trap-night effort unit, or a field name is not five minutes of comparable frog listening. |
| `startDateTime`, `endDateTime` | **PDF p. 41** (printed p. 37): sighting start/end timestamps; sensitive-species public results can have time removed. | Timestamp only where original precision/version is maintained. | Generalised or removed clock time is not a complete exact-time-of-night frog covariate. |
| `reproductiveCondition` | **PDF pp. 52–53** (printed pp. 48–49): optional state/codes including eggs, immature and other reproductive conditions. | Observed reproductive-condition indicator with taxon, date, stage detection method. | Not a linked frog metamorph count, breeding success probability or egg viability without an original independent stage-survey crosswalk. |
| `SpeciesSightings_AdditionalMeasurementsOrFacts` | **PDF p. 7** (printed p. 3): *zero to many extra facts associated with an event or occurrence*, e.g. temperature or mass. | Source-specific additional environmental field, once original `measurementType` vocabulary and site×visit join are verified. | Presence of a free-form `measurementValue` column does not establish water-level/inundation records or complete survey non-detections. |

Source cautions:
- **Sensitive species:** public `siteID`, `eventID`, `visitID`, `samplingProtocol`, `surveyID`, `samplingEffortValue/Unit` and other location/time fields may be withheld; no reconstructing withheld precise locations by inference.
- **Observation grain:** the new 2026 Extended entity collects survey information *on species-sighting records*. Our live source-only [public OData audit 37800327766](https://github.com/zuizui0223/frogcs/actions/runs/37800327766) found only one entity name containing survey/visit/effort, `SystematicFloraSurvey_SiteData` (flora, not fauna). That does NOT establish either complete absence of fauna survey data or a complete public fauna visit denominator.
- **Version:** the official data standard itself instructs readers to match standard version (6.3) with live service metadata. A later version can modify field meaning.

## Gate decision for the 29-site/343-visit Ocock study

The published [Ocock et al. (2024), DOI 10.1071/MF23181](https://doi.org/10.1071/MF23181) reports 29 original wetlands, **343 actual site surveys / 95 survey nights**, and distinguishes calling activity from recently metamorphosed frogs. Original field protocols have frog-specific **5-minute call categories**, not a plant plot abundance score.

A legitimate new frogcs-like comparative test needs all source-proven layers, **before** response extraction or model-fitting:

1. **Original audited visit/census ledger** including calls present, explicit verified no-calls and unvisited/skipped/noise-masked sites, keyed by *physical wetland* × date/time × protocol. A sighting's `visitID` is a useful join key, not by itself a complete denominator of 343 visits.
2. **Original frog call-category coding dictionary**, with separate species detection, ordinal CI/chorus strength and valid zero states. Reject `abundanceScore` as a default shortcut; explicit BioNet `Absent` may record species absence, which is **not equivalent to a listening session in which present frogs were silent**.
3. **A physical-site and organism-stage linkage:** validated `siteID`, 5-minute auditory visit ID, contemporaneous water depth/inundation, later follow-up metamorph observations with correct independent stage detection/effort, and strictly **prior** chorus history. No nearest-neighbour attachment to coordinate-generalized sites.
4. **Independent temporal and geographic held-out prediction**, after a date-independent event source, survey opportunity, original hydrology and recruitment source are authenticated. Avoid leakage from the original authors' dataset or NSW reports into "independent replication."

**If the visit ledger, call-category original coding, or hydroperiod–metamorph crosswalk cannot be verified, stop at `DATA_NOT_IDENTIFIABLE`.** This is a source-availability result, not a no-effect result.

## Source-only executable check

[Fail-closed synthetic mapping rules](scripts/audit_bionet_semantics_source_gate_v43.py) and its GitHub Actions workflow verify the code rejects:
- automatic `abundanceScore` → amphibian chorus index;
- a missing sighting row → inferred `Absent`;
- distinct `eventID` and `visitID` values counted as distinct events;
- unsupported or missing effort unit and no authoritative opportunity ledger;
- broad reproductive-stage codes → fabricated metamorph success.

The synthetic checks do **not** read the public API's real amphibian rows or prove Ocock's original site/visit linkage.

**Scientific outcome remains:** rain-selective historical strong calling is an existing frogcs observational result; whether those sites have higher successful later metamorph recruitment is **not yet evaluated**. No emails, logins, permissions, research participant data, new frog outcomes, or changes to locked RC6 occurred.
