# Frogcs G0: independent acoustic–larval bridge via Meetnetten.be (source-blind preflight)

Date: 2026-10-26. **New independent data; exploratory extension of existing frogcs RC6 and NPS evidence, not a confirmatory rescue for the failed NPS H1A.** Ownership, code, artefacts and analysis remain within `frogcs` research branch. Keep `main` JAE RC6 untouched.

## Source versions and why these records might actually join

- CC0 **Meetnetten.be — Chorus counts for Amphibia**, DOI [10.15468/d4bu8j](https://doi.org/10.15468/d4bu8j). Original IPT archive: `https://ipt.inbo.be/archive.do?r=meetnetten-amfibieen-roepkoren-occurrences`.
- CC0 **Meetnetten.be — Larvae and metamorph counts for Amphibia**, DOI [10.15468/swgure](https://doi.org/10.15468/swgure), 2026-02-26 v1.24 (metadata). Original IPT archive: `https://ipt.inbo.be/archive.do?r=meetnetten-amfibieen-larven-metamorfen-occurrences`. Published summary: 697 event records, 2,995 occurrences and 3,741 measurements/facts, 2016–2023.
- Audited publisher's **SQL transformation source** at `inbo/meetnetten-occurrences`, under `datasets/5+33 …/sql/…events.sql` and `datasets/25+32 …/sql/…events.sql`. **Both calculate `locationID` from the same backing `dimLocation.LocationID` with the same string transformation**, and `parentEventID` from `FieldworkVisitID`, `eventID` from `FieldworkSampleID`. This offers a plausible exact-location join, *not* a geographic centroids join. SQL source is an old view definition (2020) and must be verified against actual 2026 exports.
- Note **coordinates deliberately blurred by 1/5/10-km grids**. Do not join on coordinates, city, grid center or generic text locality. Even a matching exact LocationID requires proof the underlying object is the same aquatic observation location and that the genus/site protocol refers to the same pond. Keep original location IDs confidential in aggregate reports.
- Larval event environmental fields from `MeasurementOrFacts`: maximum depth, number of sweeps, fish present, permanent water column, water quality, shade and pond surface. Fish present ≠ measured predation event; permanent water column ≠ verified historical summer dry-down; larval observations ≠ egg survival.

## G0 eligibility audit BEFORE biological outcomes

Download the two original DwC-A releases separately and compute file SHA256, ZIP entry lists, row counts, field lists and `meta.xml` term mappings. Check:
1. `locationID` is identical **exact string** across sources, nonblank, and stable across multiple years in each; `eventDate`, event protocol and time-of-day are valid. Never identify location by generalized coordinates.
2. Both source schemes can be traced back to `dimLocation.LocationID` not `eventID` or `parentEventID` (these are survey IDs, not station IDs).
3. Build a source-blind crosswalk: number of shared location IDs, unique years / location-years, same-location same-year chorus vs larval event pairs, and temporal order `adult-date < larva-date`. Tabulate which target species and life stages have *recording opportunity*, not the observed values of `individualCount`.
4. Check for between-source contradictions: one location ID mapping to multiple incompatible habitat-type/protocol records, taxon name ambiguities, duplicate eventIDs or dates, and measurement completeness.
5. **Fail closed** if no exact location overlap, or ambiguity about physical pond mapping, or incompatible sample-year coverage. Publishing a dataset is not itself G0 passage.

## Frozen G1 question IF AND ONLY IF G0 passes

New G1 differs from previous-year long-larval *predator proxy* H1A, which was unsupported at NPS. It asks whether ***same taxon*** adult chorus at an exactly matched monitored pond predicts its **later** larval/metamorph record within the same breeding year beyond habitat and observation effort.

- Target organisms `Hyla arborea` and `Pelobates fuscus` (publisher's target species), **no post-outcome taxon switching**.
- Unit `verified LocationID × taxon × breeding year`, with adult chorus exposure aggregated only from sampling events occurring **before** the relevant larval census. Respect event-level `lifeStage`, `occurrenceStatus` and `individualCount` separately.
- Baseline M0: previous-year own-taxonomic adult chorus history, year effects, site/environment attributes known before larval census, observation opportunities/effort including sweeps; same-species adult signal enters M1; M2 adds measured fish presence, depth and permanent-water classification. Do not use target larval outcome to build predictors.
- Valid comparison: matching exactly the same eligible rows and held-out **entire location IDs** (primary) plus leave-year-out temporal generality. Performance = proper held-out log loss/Brier for larval presence or appropriate count likelihood, not unadjusted significance. Evaluate with no imputing missing monitoring as true absence. Confidence via location clusters. If no genuinely observed 0 under verified target protocol, declare larval presence cannot be estimated.
- Important competing explanations: adult and larval species detection varies with survey timing, call propensity and sex, fish affects larval recruitment and detectability, observer effort and water depth, and same-year habitat can affect both stages. Out-of-sample improvement is **prediction of phenophase coupling only**.
- H1B overwintering tadpole predation and H3 summer dry-out reset are **NOT estimable** from these sources without direct relevant predator-stage/egg survival or drying dates. No feeding-flux or direct egg predation conclusion.

## Status and execution

Run `python research/scripts/inbo_stage_bridge_g0.py --out /tmp/inbo_stage_g0.json` under the dedicated research workflow. Commit **only aggregate source QA**, not location IDs, sensitively generalized coordinates or full source tables, unless licence and location controls are rechecked. Pass/fail is computed from actual source bytes; if downloads fail, report source gate blocked and stop.
