# frogcs GLOBAL G0 — response-blind stage and sampling-event feasibility gate, 2026-10-26

**Status: protocol frozen BEFORE the new global stage coverage counts or species × predator relationship results. The GloBI/GBIF pilot and its adverse matched-prey specificity checks were ALREADY seen; this is prospective only relative to the new wider source-coverage scan, never a registered confirmation.** All code, original-result QA and any future research manuscript remain within `zuizui0223/frogcs`; RC6 NAAMP is frozen and editorially deferred as a stand-alone submission.

## What new global data must actually measure

Use GBIF's [official sampling-event publishing specification](https://www.gbif.org/data-quality-requirements-sampling-events) for `eventID`, `samplingProtocol`, `sampleSizeValue`, `sampleSizeUnit` and a repeatable wetland identifier. GBIF `eventID` is not globally unique; key by (`datasetKey`, `eventID`), and treat taxon × event explicitly surveyed zeros separately from missing/unassessed taxa.

**Snapshot prior to seeing counts:** 2026-08-01 experimental taxon-partitioned public `gbif-public-data/development/2026-08-01-DWCA/p_taxon/` (a citable snapshot DOI is required before publication; experimental source is NOT itself stable). Calendar years **2010–2025** inclusive (exclude partial 2026), primary spatial cells **1°**, 0.5° sensitivity when supported. Retain archive/source provenance, raw life-stage label, latitude/longitude uncertainty, year/month, original `datasetKey` and GBIF ID. No proportional sampling or first-rowgroup extrapolation to population totals. A record is not a unique animal; count records, not organisms.

**G0 audit is explicitly blind to frog survival/transition outcome indices, phase-overlap effects, and prey abundance regressions.** Reading life-stage labels and raw record-count coverage is allowed, but no juvenile:tadpole *ratio*, stage-width predictor coefficient or predator–prey negative relationship is computed or used for selecting taxa, dates or grids.

### G0.A Exact source partitions and stage ontology

Find source `taxonpartition` using the official S3 list, do not invent partition names. Required target guilds:

- **Focal frogs (Anura):** `egg` only explicitly "egg"/"eggs"/"ovum" (not string "early"); `tadpole` = explicit "tadpole"/"larva" in verified anuran species; `postmetamorphic juvenile` = explicitly "juvenile", "froglet", or source-verified recently metamorphosed observation. "Immature", "subadult", "young", and taxonomically ambiguous or generic larvae must **not** be equated with the juvenile denominator or with Gosner 46 without a source-level check. Egg and juvenile may be *different source cohorts*.
- **Potential aquatic predators:** Odonata `nymph`/`larva`, **Caudata** `larva` (some are prey/competitors rather than true tadpole predators). Species-pair diet validity must be fixed by independent source and documented **before** running abundance/timing outcome tests. In the global coverage census these are only *potential exposure reports*, not real resident predator biomass or actual tadpole ingestion.
- **Matched nonpredator candidates:** Ephemeroptera `nymph`/`larva` and Diptera **Chironomidae** `larva` are source coverage populations. They do **not** automatically qualify as nonpredators: filter control families/species using independently checked feeding guild traits; **exclude predatory Tanypodinae**, unknown feeding mode and nonaquatic stages. Final prey controls must be matched on stage, grid/year coverage and reporting volume *before response effects*, otherwise G1/G2 are ineligible.
- **Odonate emergence:** documented `exuvia`/`exuviae`, `emergence` as explicit observation property only; **adult odonate** records and `pupa` cannot be inferred to be exuviae or emergent individuals. Report separately by identifiable source terms.
- Keep raw `lifeStage` label frequencies including unknown/missing/ambiguous/mixed, and count records with valid `year`, `month`, coordinates, `occurrenceStatus=PRESENT`, no `hasGeospatialIssues` and coordinateUncertaintyInMeters <=10 km (missing uncertainty flagged and separate). No native/non-native label inference from country records.

Report **all** source-class year-bucket/continent totals and record volume per stage; joinable grid×year×month coverage can be computed **within a single stage category** but do **not** calculate cross-guild overlap or outcome response ratios at G0. Display explicitly zero stage-labelled original records, not guessed absent biology. Exclude 2026.

### G0.B Sampling event stage-grain preflight

Discover source `datasetKey` candidates from the observed GBIF records and registry `SAMPLING_EVENT` type plus original IPT datasets, not same-grid matching. Each inspected dataset gets:
- source title, DOI/URL, original version/MD5/SHA, licence;
- number of true event cores; events with survey method, a stable *actual aquatic site identity* (ID must be source-confirmed and not blurred centroid) and valid year;
- unique event × assessed frog tadpole stage, potential verified predator larva stage and nonpredatory control stage rows, including **explicit surveyed absence**, numeric `individualCount` and measured effort;
- identical wetland site repeatedly surveyed in >=2 years; exact same event cross-guild overlaps and taxon-specific count denominator, before any abundance response is inspected.
- In each dataset predeclare contrast that is *actually* measured; never turn a frog-only larval net event with nonsampled dragonfly into a predator zero. An amphibian target sampling protocol can be a poor odonate detection protocol. Taxon non-detection does not demonstrate biological absence unless the protocol explicitly assesses that group.

Source G3 minimum **before outcome:** >=15 independent actual wetlands, >=3 years, >=30 wetland×year cells with adequate complete prey and predator effort; >=20 events with explicit zero or positive for *both* prey and predator stages. More sources with no matched effort are listed **non-estimable**. These thresholds are pragmatic design gates, not significance filters.

### Three prespecified hypotheses and stop rules

**H_GBIF-1 (weakest scientifically, only a reporting transition).** Compare log record reporting of verified *juvenile/tadpole* stage conditional on total source effort, **not cohort survival**. A ratio `n_juvenile / n_tadpole` is a **detection- and cohort-confounded composition statistic**, even when differenced within a grid over time. Each source's stage-specific detectability, recruitment lags, photo labeling and observer behavior can vary by year and violate cancellation. Require >=20 original reported tadpole and juvenile records per *species × grid × year* before an index is even defined; >=3 nonmissing years in >=30 independent cells and >=5 species with verified mature stage terms. Primary endpoint must be held-out **stage-composition reporting** and reported with source effort adjustments (no "metamorphosis survival %" label). If stage index insufficient, no model or manufactured zero denominator.

**H_GBIF-2 (breeding concentration vs stage exposure).** For frog eggs, require >=10 independent taxon×grid×year cells with >=20 explicit egg-stage records, >=3 months' opportunities for method-reported eggs, >=3 years of repeated coverage, **at least five frog taxa**, and matched aquatic predator and independently certified nonpredatory controls. Predeclare stage-season width using circular month concentration (not arbitrary raw min/max span) with fixed source effort and equal species×grid×year observation eligibility. Egg *photo* timing is only a **reporting phenology**, not eggs deposited across all females, genetic synchronization, nor selective predation release. Test the predator exposure conditional on species×region×year phenology and matched controls, with survey effort. Any null in the nonpredator control is *necessary but not sufficient* to conclude predation.

**H_GBIF-3 (highest physical inference if event-panel is available).** A source-bundled `datasetKey×eventID×siteID×date` multistage count panel, eligible only if the same method can plausibly count amphibian larvae, documented tadpole predators and nonpredatory benthos with protocol/effort/true zero. Within-site comparisons over time and matched nontrophic control test whether prior or contemporaneous measured predator stage density *predicts* prey counts beyond hydroperiod/effort. For prior-year effects, **same-pond stage order and lag** must be measured. Capture efficiency and breeding phenology need negative controls; neither event counts nor an interaction coefficient automatically identifies kills or egg survival. Predeclare destination of null/adverse effects.

### Reportable after inventory

Emit ``G0_COUNTS_ONLY`` source receipt with partition coverage, columns, records by stage and year/location; and G3 original event dataset eligibility, source identifiers and counts **without inspecting prey responses**. Gate decisions independent of biological effect sign:

- G1 viable only if both frog juvenile and tadpole stage label coverage meets floors *and* stage provenance not confounded by inconsistent GBIF taxon source; if not, **STOP**.
- G2 viable only if verified egg stage/year and valid predator/negative-control month reporting meets floors; else **STOP**.
- G3 viable only if source-confirmed cross-guild event sampling + original wetland IDs + repeat years + explicit numeric counts/zeros exists. Otherwise STOP; sampling-event metadata alone is not an eligible event-panel.
- A positive global stage-reporting effect cannot be sold as "first proof of predation-induced recruitment decline": no individually followed cohort, direct feeding, attack rate, mortality or intervention is observed, and matched negative controls cannot eliminate all seasonal detection biases.

**Do not run global directional effect estimation after seeing the feasibility counts until this fixed eligibility and source-bias audit is checked.** Keep RC6 `paper/`, `submission/`, `provenance/`, `scripts/naamp/` and figures untouched.
