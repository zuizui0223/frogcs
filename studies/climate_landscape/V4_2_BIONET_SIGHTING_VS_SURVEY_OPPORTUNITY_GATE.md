# v4.2 — NSW BioNet observation records ≠ complete amphibian survey opportunities

**2026-10-09 JST. Independent source-design audit only. JAE RC6 locked and unchanged.**
**No actual 2015–2020 Ocock frog species observations, negative call records, private coordinates or water measurements retrieved. No external request sent.**

## 1. Verified authority: 2026 BioNet CoreDataExtended is a *sighting-level* extension

The official [BioNet Web Service February 2026 release 4.1.0](https://www.environment.nsw.gov.au/publications/bionet-web-service-release-notes-february-2026) explicitly introduced `SpeciesSightings_CoreDataExtended` to supply **new sighting-level fields** from systematic flora and fauna surveys; it did **not** announce an independent, complete survey-visit census API. The old `SpeciesSightings_CoreData` was scheduled for retirement after roughly six months, so **use the extended entity going forward** rather than assume the old entity remains authoritative.

Our successful [public metadata-only CI run 37799096501](https://github.com/zuizui0223/frogcs/actions/runs/37799096501) verified the public service document and OData schema: `CoreDataExtended` has **124 field names**, `CoreData` 93, `AdditionalMeasurementsOrFacts` 7. Present names include `siteID`, `surveyID`, `surveyName`, `eventID`, `visitID`, `eventDate`, `startDateTime`, `endDateTime`, `occurrenceStatus`, `abundanceScore`, `samplingEffortValue`, `samplingEffortUnit` and `reproductiveCondition`. Separate measurements have `measurementType`, `measurementValue` and `measurementUnit`.

**Important asymmetry:** those fields may occur on a **species sighting** even if a no-frog-call survey visit produces **no species sighting record at all**. Their schema presence cannot certify survey visit completeness or give a zero-calling denominator.

The [official BioNet terms](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/bionet-access/bionet-terms-and-conditions) explicitly caution that sightings are patchy, human-effort dependent and not a census of true abundance or presence. Systematic survey sightings are **included within** the Species Sightings search results, but that inclusion does not imply missing taxon × survey opportunity combinations equal observed absences. This is a data-generating distinction, not a mere problem of missing columns.

Also, [official BioNet basic-access policy](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/bionet-access) generalizes/withholds sensitive fauna location detail. The Feb 2026 release documentation also identifies `siteID`, `surveyID`, `eventID`, `visitID`, timestamps or effort/context fields as **conditionally withheld or generalized for sensitive species**. Hence a physically stable SiteID must be independently verified for eligible non-sensitive taxon/site records, rather than inferred from a published map point. Do **not** attempt to reverse masked coordinates.

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
