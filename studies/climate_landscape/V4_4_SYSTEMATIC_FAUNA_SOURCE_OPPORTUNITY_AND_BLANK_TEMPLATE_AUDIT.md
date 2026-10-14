# v4.4 — Official blank fauna survey upload workbook vs a complete frog non-detection ledger

**Audit date: 2026-10-09. Status: ACTUAL ORIGINAL PUBLIC BLANK TEMPLATE INSPECTED; NO FROG DATA.**
Separate source-only study PR #135. JAE RC6, its science and `main` remain unchanged. No actual species sightings, survey visits, personally identifiable observers, site coordinates, animal outcome values or ancillary hydrology data were accessed or sent.

## 1. Source clarification that resolves a false dichotomy

NSW DCCEEW's [Contribute data to BioNet Atlas](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/contribute-data-to-bionet-atlas) explicitly states that the **Systematic Surveys data collection** records survey **effort** and is intended to allow inference of **negative data** (sites where species were not observed). The [Systematic Fauna Survey access page](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/systematic-fauna-survey-data) states that **login access is needed to analyse/export systematic fauna survey data**.

These statements imply:
- **Invalid pessimism:** “BioNet contains only positive sightings; non-detection information does not exist.” The official systematic survey **collection design explicitly supports** inference of negatives.
- **Invalid optimism:** “Species Sightings OData has `visitID`/`occurrenceStatus`; therefore a complete, public, reconstructable 343-visit amphibian opportunity table exists.” A sighting-level API, even with some explicit `Absent`, has **not been verified** as providing all original visits and source-specific calling categories.

Official 2026 [BioNet Sightings Standard v6.3](https://www.environment.nsw.gov.au/publications/bionet-species-sighting-data-standard) still applies: `abundanceScore` concerns **plant plots**, not original frog 5-minute calling categories; `visitID`/`eventID` are duplicated identifiers of the **same census**, not two surveys.

## 2. An actual original NSW blank fauna survey workbook was downloaded and its structure inspected

Government-issued, openly downloadable [BioNet Atlas Fauna Survey upload datasheet (1 July 2025)](https://www.environment.nsw.gov.au/publications/bionet-atlas-fauna-survey-upload-datasheet): the official link resolves to
`https://www.environment.nsw.gov.au/sites/default/files/2025-05/fauna-survey-datasheet-6000_0.xlsx`.

[Automated public blank-template inspection run **37888035114 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/37888035114) returned HTTP **200** and extracted only sheet names and first few static **template header rows**, using a bounded XML/ZIP streaming reader. No external workbook connections/macros or embedded formulas were executed and no ecological source records were retrieved. [Reproducible source-only script](scripts/audit_blank_nsw_fauna_template_structure_v44.py).

The official *blank submission template* has **five worksheet names**:

| Actual sheet | Header content confirmed | What it establishes |
| --- | --- | --- |
| **Sighting Records** | `SiteNo`, `Technique`, `SpeciesCode`, `DateFirst`, `DateLast`, `NumberIndividuals`, `EstimateCode`, `BreedingCode`, `ObservationType`, and observer/source fields | The **input row grain is sighting-oriented**. It includes field codes and does not by itself certify that every site visit, including no-sighting visits, is represented. |
| **Reference** | Controlled vocabulary for estimate, sex, breeding, observation/microhabitat and source codes | Possible *source* code definitions, **not original Ocock frog call index meaning**. |
| **Fauna** | Species names and codes | Taxonomic validation reference, not a census/visit table. |
| **Flora** | Species names and codes | Plant taxonomy reference, not frog data. |
| **Info** | Template metadata | Version/custodian context. |

**No separate worksheet named `Survey Visits`, `Survey Opportunities`, `Fauna Site Data`, `Event Ledger` or equivalent exists in this public blank workbook.** This is a **fact about this one template**, not evidence that the registered BioNet Atlas Systematic Surveys application/database lacks internal visit/census records. The government specifically says systematic survey information is housed there; its registered export schema may include additional records.

### Why this matters biologically

Suppose a wetland was visited on date t, but no *Litoria* was heard. If there is no row representing that survey opportunity, then a later positive sighting does not prove “rain switched the animal from acoustic silence to chorus.” It can equally reflect no prior sampling, partial effort, detector masking, absence of frogs, or an unseen recording. A positive-sightings-only table used as a calling panel biases both the **magnitude** and **which sites** are active after rain. The Ocock manuscript reports **343** visits, but a complete original run/visit ledger from this precise analysis has not been recovered.

## 3. Exact source package that would turn this into an empirical test

Three source-authoritative files (or a documented normalized database export) are **necessary**:

**A. Study-specific survey-opportunity manifest**
- Original Ocock programme/site IDs for 29 physical wetland units, original survey/census/visit keys, exact date/time, methods (especially 5-minute frog calls), attempted/completed/skipped, valid genuine no-calling codes, detection effort and missingness reasons, original export version.
- A *source-defined*, not outcome-assembled reconciliation to the paper's 343 site-visits and 95 survey nights. Counts may differ in new exports if explicitly explained; cannot fabricate zeros for unmatched opportunities.

**B. Frog acoustic + life-stage dictionary and records**
- Species detections and **original 5-minute calling classes** with original source codes at those survey IDs, separated from opportunistic sightings; identify if a category represents call frequency, adult abundance or count.
- Independent eggs/tadpoles/recent metamorph follow-up observations with date/method, enough to test site- and time-specific downstream recruitment while acknowledging larval lag and imperfect stage detection.

**C. Ancillary water/rain and physical-site linkage**
- The author's site-visit water depth, inundation extent/onset/consecutive duration, environmental flows and day/lag rain, their original data dictionaries and the preserved physical site key (no reverse engineering of protected fauna locations).
- The article [Data availability](https://doi.org/10.1071/MF23181) explicitly states **frog survey records are in NSW BioNet; ancillary data are available on request**. Hence this combined package **cannot be assumed to be available from public Species Sightings OData alone**.

## 4. Candidate contrast and meaningful outcome conditions

The next *prospective/held-out* inference would be:

> On verified repeated physical wetlands, does **strictly earlier species×site strong chorusing** predict *later* actual metamorph recruitment after rain, over and above contemporaneous measured inundation and hydroperiod, compared with genuine surveyed-but-silent baseline sites?

Do not expect `abundanceScore` to substitute the original frog call intensity. Any complete panel must match calling and breeding stage to the **same wetland and biologically plausible lag**, and preserve both true zeros and unsurveyed statuses. Ecological specificity matters: a site with many loud adults might be a **calling hotspot but larval sink** if water dries before metamorphosis. This is a testable hypothesis, **not an observed result**.

If original survey opportunities and physical sites cannot be established, outcome analysis is **NOT IDENTIFIABLE**; this is not negative evidence that historical sites fail to produce metamorphs.

## 5. Final decision / safeguards

- **Confirmed:** NSW Systematic Surveys intentionally captures effort and data from which non-detections may be inferred. Its fauna analysis/export requires registered login. The public upload workbook does not include a separate visit ledger worksheet, though internal records may exist.
- **Confirmed:** source-only HTTP 200 retrieval and five actual blank-template sheets; government form contains `BreedingCode`, `NumberIndividuals`, `ObservationType` etc., not automatically the original published frog call categories.
- **Not confirmed:** publicly retrievable full Ocock 343-visit manifest; row-level original CI; exact verified site mapping; repeated matched metamorph follow-ups; raw linked hydrology; external holdout.
- **Recommended next authorized source action:** use the **official registered NSW BioNet Systematic Fauna Survey export** to verify whether a complete visit denominator and original method/call-category fields survive, plus a separate narrow source-custodian query for the ancillary water/metamorph linkage. This requires user-authorized access or a properly scoped data request. No login or request was submitted.
- **Do not scrape sensitive coordinates, infer missing taxa as absence, map plant `abundanceScore` onto frog CI, or merge NSW 2025 monitoring report with Ocock as an independent biological replication.**
- **No new causal or statistical amphibian effect** was estimated. The original JAE RC6 paper and `main` remain untouched.
