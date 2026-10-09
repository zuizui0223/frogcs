# v4.2 — NSW BioNet observation records ≠ complete amphibian survey opportunities

**2026-10-09 JST. Independent source-design audit only. JAE RC6 locked and unchanged.**
**No actual 2015–2020 Ocock frog species observations, negative call records, private coordinates or water measurements retrieved. No external request sent.**

## 1. Verified authority: 2026 BioNet CoreDataExtended is a *sighting-level* extension

The official [BioNet Web Service February 2026 release 4.1.0](https://www.environment.nsw.gov.au/publications/bionet-web-service-release-notes-february-2026) explicitly introduced `SpeciesSightings_CoreDataExtended` to supply **new sighting-level fields** from systematic flora and fauna surveys; it did **not** announce an independent, complete survey-visit census API. The old `SpeciesSightings_CoreData` was scheduled for retirement after roughly six months, so **use the extended entity going forward** rather than assume the old entity remains authoritative.

Our successful [public metadata-only CI run 37799096501](https://github.com/zuizui0223/frogcs/actions/runs/37799096501) verified the public service document and OData schema: `CoreDataExtended` has **124 field names**, `CoreData` 93, `AdditionalMeasurementsOrFacts` 7. Present names include `siteID`, `surveyID`, `surveyName`, `eventID`, `visitID`, `eventDate`, `startDateTime`, `endDateTime`, `occurrenceStatus`, `abundanceScore`, `samplingEffortValue`, `samplingEffortUnit` and `reproductiveCondition`. Separate measurements have `measurementType`, `measurementValue` and `measurementUnit`.

**Important asymmetry:** those fields may occur on a **species sighting** even if a no-frog-call survey visit produces **no species sighting record at all**. Their schema presence cannot certify survey visit completeness or give a zero-calling denominator.

The [official BioNet terms](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/bionet-access/bionet-terms-and-conditions) explicitly caution that sightings are patchy, human-effort dependent and not a census of true abundance or presence. Systematic survey sightings are **included within** the Species Sightings search results, but that inclusion does not imply missing taxon × survey opportunity combinations equal observed absences. This is a data-generating distinction, not a mere problem of missing columns.

Also, [official BioNet basic-access policy](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/bionet-access) generalizes/withholds sensitive fauna location detail. The Feb 2026 release documentation also identifies `siteID`, `surveyID`, `eventID`, `visitID`, timestamps or effort/context fields as **conditionally withheld or generalized for sensitive species**. Hence a physically stable SiteID must be independently verified for eligible non-sensitive taxon/site records, rather than inferred from a published map point. Do **not** attempt to reverse masked coordinates.

### 2026-10-09 source-only follow-up: no independently named public *fauna visit* entity was found

A second live [BioNet schema audit, run 37800327766 (SUCCESS)](https://github.com/zuizui0223/frogcs/actions/runs/37800327766), inspected only official service/entity/field names. Of the current service-document entity set names containing **visit**, **survey** or **effort**, the only name was **`SystematicFloraSurvey_SiteData`** — not a systematic **fauna** survey-visit manifest. The service still exposes `visitID` as a property on **`SpeciesSightings_CoreDataExtended`**, but did **not** expose a separately named public `SystematicFaunaSurvey_VisitData` or equivalent `visit`-named fauna table through this audited service document.

**Precisely bounded negative finding:** the inspected public entity *names* do not establish a complete public **fauna survey-visit denominator**. This is **not a proof** that complete fauna visit records are absent from the underlying NSW BioNet Atlas, from a differently named entity or via registered access. The [official systematic fauna data access page](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/systematic-fauna-survey-data) says login is required to analyze/export systematic fauna survey records. Do not infer that public sighting rows enumerate all visited-with-no-calls occasions.

The same checked extended entity published `siteID`, `surveyID`, `visitID`, `eventID`, `abundanceScore` and `samplingEffortValue` as **field definitions only**. No actual animal/survey rows, nonmissing-field rates, identifiers, coordinates or water observations were accessed. The saved public-meta field-name output is version-specific and should be rechecked after API migration.

## v4.3 authoritative field-semantics correction — 2026-10-09

The [official BioNet Species Sighting Data Standard v6.3 (February 2026)](https://www.environment.nsw.gov.au/sites/default/files/2026-02/bionet-species-sighting-data-standard-6-3-260021.pdf) was reviewed **as an actual data dictionary**, not inferred from OData field names. Detailed findings and page-level provenance: [v4.3 official field-semantics/zero policy](V4_3_BIONET_2026_CANONICAL_FIELD_SEMANTICS_AND_ZERO_POLICY.md).

**Important substantive correction to v4.1/v4.2 schema optimism:** `abundanceScore` (PDF p.56; printed p.52) explicitly describes the **abundance of PLANTS in vegetation plots**, not the original frog 5-minute CallingIndex or Ocock acoustic categories. **Mapping this directly to a frog chorus index is invalid**.

**Important identity correction:** `eventID` and `visitID` (PDF p.40; printed p.36) are documented as **duplicate keys for the SAME census**, not separate event and visit replications. `surveyID` groups a survey conducted across one or more sites; it is not an individual census count.

**Important status distinction:** `occurrenceStatus` is a controlled presence/absence field and the standard allows **explicit 'Absent'** (PDF p.78 for legacy fields; current extended table gives the presence/absence definition). This means the schema is **not necessarily presence-only**. However a missing sighting row is **not** an explicit Absent, and a recorded taxon's absence is **not automatically the CI=0 acoustic state of a present but silent frog population**.

**Access/effort caveats:** `samplingEffortValue` requires `samplingEffortUnit` and the original protocol; `startDateTime` can be time-generalized for sensitive taxa; `siteID/eventID/visitID/surveyID` can be withheld in public output. Neither a field name nor a generic reproductive stage tag authenticates a site-event metamorph-success record.

The [fail-closed source semantic check](scripts/audit_bionet_semantics_source_gate_v43.py) now refuses default plant-abundance→frog-CI conversion, fabricated absence rows, double-counted visit aliases and invalid effort units. These are **synthetic source checks only**. The critical remaining blocker is still a complete *independently authenticated* 343-visit acoustic opportunity ledger and frog category/hydroperiod/metamorph crosswalk, not yet obtained.

## v4.4 refinement: the registered Systematic Surveys collection explicitly supports negative data

Official NSW [BioNet data-submission guidance](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/contribute-data-to-bionet-atlas) states that systematic **flora and fauna** survey information is submitted with effort and **the ability to infer negative data at surveyed-but-not-sighted sites**. The [Systematic Fauna Survey access page](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/systematic-fauna-survey-data) specifies that **analysis/export requires login**.

This revises the scope of the v4.2 negative finding: **the public Species Sightings web-service did not expose a separately named complete fauna visit-opportunity entity**, but the registered Systematic Fauna collection **is designed to preserve the underlying survey opportunities**. That does not prove the *specific* Ocock et al. 2015–2020 343 visits are complete there.

An actual NSW [blank 2025 Fauna Survey upload workbook](https://www.environment.nsw.gov.au/publications/bionet-atlas-fauna-survey-upload-datasheet) was obtained via HTTP 200 and its five sheet names were inspected in the [source-only SUCCESS run 37888035114](https://github.com/zuizui0223/frogcs/actions/runs/37888035114). Its named sheets are `Sighting Records`, `Reference`, `Fauna`, `Flora`, `Info`, **not** an independently listed `Survey Visit Ledger`. This is a limitation of **that blank upload form**, not a claim about the logged-in database's internal tables or export facilities. See [v4.4 documented source finding](V4_4_SYSTEMATIC_FAUNA_SOURCE_OPPORTUNITY_AND_BLANK_TEMPLATE_AUDIT.md).

**Conclusion unchanged:** a fully verifiable denominator **including genuine 5-minute no-call and no-visit opportunities** is still unverified for the 29-site original Ocock study. It must not be generated by adding zero rows to sighting-only extracts. No frog observations or field hydrology were inspected here.

## 2. Decision: one ID is not a survey denominator

The published source [Ocock et al. 2024](https://doi.org/10.1071/MF23181) describes:
- 29 original survey sites (15 Gwydir, 14 Macquarie), 343 **actual site surveys** during 95 survey nights (2015–2020);
- **a 5-minute auditory survey at each actually visited wetland**, with per-species categorical calls (rare / common / abundant / very abundant);
- a separate visual/aural frog transect, tadpole visits and observations of metamorphs; some site access was blocked or deferred;
- environmental rainfall/inundation/flow predictor data. The original article's explicit **Data availability** states: **frog survey records via BioNet, ancillary data on request**.

If a public BioNet export lists only the species observed calling, absence of a taxon at a named visit could mean **not present**, **present but silent**, **not detected**, **not attempted**, **masked**, **visit not uploaded**, or **survey outside eligible protocol**. These alternatives cannot be separated from sightings alone.

**Critical verification before ANY acoustic analysis:** independently establish an exact, original `site × date/time × method × visitID` opportunity manifest **including visits with zero eligible frog calls**, complete original frog call categories, original skip/status codes and denominator audit against the published 343 actual surveys. No BioNet species sightings row or inferred sum of distinct `visitID` values is an adequate replacement for this manifest unless the source custodian documents complete upload and zero-call visit representation.

The 343 number applies to the authors' original 2015–2020 analysis; an online public export or the wider 2025 NSW programme need **not** match it without an explicit version/crosswalk. An exact count difference must be explained, not repaired by outcome-based filters. The 29 locations' coordinate privacy must be respected.

## 3. Three separate source tables (required for the future hypothesis)

**A. Visit/opportunity manifest**: one row per original *scheduled or attempted* `physical_wetland_id × survey_visit_id × date/time × method`; includes planned/actual opportunity, survey completeness, reason not surveyed, 5-minute auditory effort, observer/noise flags and source archive version. This table's existence/census cannot be concluded from public BioNet sightings.

**B. Species/acoustic observation**: one row per *actually observed and adequately sampled* `visit × species`, preserving exact original categorical CI classes and valid non-detection rules. Do not map NAAMP CI0–3 onto Ocock's 4 positive abundance categories by ordinal labels alone; define the conversion against original field protocol and any observed-absence coding.

**C. Physical water and downstream metamorph**: water depth/inundation area/duration linked to the **same verified physical site** and event/time; actual metamorph follow-up dates, detection effort and valid non-detection status. Flow/rain prior windows are separately timestamped to avoid time leakage. Original paper states hydrology ancillary sources are on request, so do not assume BioNet `AdditionalMeasurementsOrFacts` contains enough data or the full predictor derivations.

A fourth **strictly prior strong-chorus history** table would be built *only if* verified independent baseline visits exist with the same site and species. History missing/not visited ≠ historically weak. The 2015–2020 site panel may not have sufficient separate independent years for both training and held-out recruitment outcomes; assess year/site coverage **before** any model fit.

## 4. Exact source-access plan / triage, with no credential bypass

**First public-only gate (currently met):** public entity and property names are present. All access receipts version-stamped, no observations read.

**Second original-protocol gate (NOT MET):** a source-authoritative code dictionary for `abundanceScore`, `occurrenceStatus`, `visitID`, `surveyID`, `samplingEffortValue/Unit`, and original Ocock 5-minute CI categories; explicit handling of zero-call and skipped visits.

**Third visit-denominator gate (NOT MET):** a complete authentic **non-response-based 343-site-survey manifest** and dated site-ID crosswalk; a public sightings-only dump is not enough.

**Fourth original linkage gate (NOT MET):** source-preserved site-event local water depth / inundation and later metamorph monitoring; at least two independent source-proven conditions of event-specific water variation and strictly prior chorus history.

**Fifth response gate (NOT AUTHORIZED/EXECUTED):** preregister independent years/sites, control opportunity/detection, compute a proper out-of-block *predictive* site-history/metamorph contrast, and keep the post-treatment-k configuration check non-causal. No additional outcome-driven taxon or wetland selection.

If second/third/fourth gates fail, record **NOT IDENTIFIABLE FROM PUBLIC BIONET SPECIES SIGHTINGS ALONE**. Do not treat insufficient identification as a negative ecological finding.

## 5. Scientific consequence

The original frogcs RC6 shows a **rain-associated spatial recurrence of strong calling**, without measuring reproductive payoff. Ocock et al. independently show **different hydrology-related predictors for calls and recently metamorphosed frogs**. Neither demonstrates:

> **Does *strictly prior* taxon × physical-wetland strong chorus history predict independently verified later metamorph success, above direct hydroperiod, in new site-years?**

This remains a legitimate, **untested** follow-on if and only if a complete physical site × survey opportunity × species × hydrology × recruitment panel can be established. It is stronger than calling the original BioNet sightings an apparent replication. The necessary missing element is **source linkage and denominator coverage**, not yet another regression.

## 6. Provenance

Official NSW February 2026 BioNet release; BioNet basic-access and data limitation webpages; Ocock et al. 2024 Methods and Data availability; our [previous live metadata-only source audit](https://github.com/zuizui0223/frogcs/actions/runs/37799096501). **No new field or frog outcomes read; no API record-level query, paid request, email, or manuscript change.**
