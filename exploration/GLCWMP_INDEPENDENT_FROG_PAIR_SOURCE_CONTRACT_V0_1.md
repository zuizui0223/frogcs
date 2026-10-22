# External Great Lakes Coastal Wetland Monitoring Program (CWMP) frog pair — source-first falsification

Frozen 2026-10-22 before parsing any external frog outcome values. **Independently collected dataset**, separate from USGS NAAMP. New hypothesis and data quality gate are exploratory/post-hoc relative to the NAAMP discovery. JAE RC6 manuscript, SI, main and submission remain frozen.

## Independent source and immutability
Tozer et al., *Ecosphere* (2025): DOI https://doi.org/10.1002/ecs2.70248
Public frog/wetland flat file: Dryad https://doi.org/10.5061/dryad.hmgqnk9v8.
Dryad API dataset ID `151710`, version ID **350431** (2025-03-07).
- Source file **CWMP_MaxOcc.csv**, Dryad file ID **3932974**, 4,004,194 bytes, pinned SHA-256 **9b6e1b11d371a6bfac2b49e0aee369a57ed4fdeaeb7378c81ea79dc92c9b2587**.
- README file ID **3932975**, 13,021 bytes, SHA-256 **70a0753ddcfbde7fd41178045843c68333136495d4b64f63b3af6c579865c7e8**.
- API metadata: https://datadryad.org/api/v2/versions/350431/files.
- Source URL to test (no silent replacement): https://datadryad.org/api/v2/files/3932974/download. If 401/403, try the *official dataset ZIP* https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.hmgqnk9v8/download, and require an exact hash match for the extracted CSV. Refuse inferred alternate data, scraping without provenance or unauthenticated third-party mirrors if both official endpoints fail.
- Raw source must **not** be committed to GitHub or released in GitHub Actions artifacts; archive only metadata, quality receipts and scientifically appropriate aggregated results.

## Original grain and ecological constraints

The 2025 published file has one record per **wetland site_id × listening point_id × year × species/group**, indicating whether a species was heard on **at least one** of three listening visits that season (2011–2023), plus habitat/environmental covariates. 1–6 listening points per wetland per sampled year; 1,550 point-count locations in 747 wetlands; eight analyzed taxa/taxon groups.

Unlike NAAMP:
- The response collapses **three survey occasions** into a point-year acoustic occurrence. A same point-year positive for two species is **not same-night or simultaneous** detection.
- There is no guaranteed ten-stop community fixed-margin unit. A site-year may have only one point. Fixed row/column null analysis requires sufficient **3+ point wetland-years** and observed **2+ species** and nondegenerate margins, and cannot mechanically transfer NAAMP row/column null to one-point wetlands.
- Vegetation-zone fish/odonate measurements are taken by CWMP, **but those individual trophic measurements are not established as part of this exact publicly provided frog flat file**; wetland/forest landscape cover is not a macrophyte species census.
- Sampling and water chemistry windows differ from frog observation windows; annual covariates are associations, not causal antecedents.

## Pre-outcome source-only QA (run first and freeze receipt)
1. Download via verified Dryad official endpoint, check exact hash and size of **both files**.
2. Profile columns, dtypes and candidate key `site_id, point_id, year, [taxon column]`; identify response field names from the README and source header (do not guess). Fail if missing.
3. Count exact duplicates and conflicting outcome keys **only after checking file integrity**. Measure years, site+point uniqueness, location rounding and possible coordinate drift.
4. Count number of unique point_id per site_id/year, number of wetlands with ≥2/≥3 sampled points, number of point-years with 8 complete valid taxa outcomes. **Do not inspect association direction or pair co-occurrence until this coverage ledger has been frozen.**
5. Coverage gate for any within-wetland fixed-margin analysis: ≥80 independent 3+ point wetland-year groups, ≥40 distinct wetlands, and ≥20 groups with nonconstant eligible community margins. If it fails, **do not** run NAAMP-style fixed-margin inference; use a separately frozen point-year observational prediction specification without portraying it as same-night.
6. Named focal source taxa: `Lithobates clamitans` and `Lithobates catesbeianus` (NAAMP positive association). Secondary negative partners `Anaxyrus fowleri` and `Hyla versicolor` **only if unambiguously published** in the eight taxon list; if absent or combined at a different taxonomic unit, record as unavailable, no opportunistic replacement by other species. If these taxa are not present, only the positive-pair portability question can be addressed.
7. Mixed presence/absence in a provided complete panel is valid; **never** treat a missing species row as an absence without verifying that all eight taxa have a recorded row per point-year. No taxonomic complexes interpreted as resolved species.
8. Environmental covariates must be checked for direction, units and time, via README. If none are aquatic emergent vegetation cover at survey point scale, the dataset **cannot independently confirm plant-mediated acoustic segregation**; it tests broader cross-dataset partner associations.

## Frozen validation goals, if QA passes

1. **Primary (portability):** positive, species-identity-specific bullfrog–green frog association conditional on wetland-year location, environmental availability and observed survey coverage, estimated from independent CWMP data, NOT reusing NAAMP coefficients.
2. If site-year has ≥3 points with different species composition: test with route-independent wetland-block holdout and fixed species-by-point margins (same wetland×year), no optimizing cutoffs or redefining source analysis.
3. If fixed-margin scope insufficient: an alternative **separately predeclared** logistic model of bullfrog/greenfrog point-year detection with wetland/environmental covariates and blocking by wetland; must be presented as a weaker *cross-site association* and never as NAAMP exact fixed-margin replication. Do not silently switch models.
4. Independent plant–frog or indirect plant→predator→frog mediation can only be assessed if synchronized plant structural and fish/invertebrate survey data with actual keys are subsequently verified and lawfully accessible.

**Stop on data-source failure**: document the HTTP status and verified archive metadata. Do not treat a program description as measured evidence.

## Deliverables
- `exploration/run_glcwmp_independent_source_audit_v0_1.py`: only authoritative source download and count-blind data structure/coverage checks, source metadata/hash.
- GitHub Actions with exact SHA check before parsing, result-only uploaded JSON, no raw redistribution, fail closed source status.
- Independent ecological claim only after source rows, keys and coverage verified, with code and receipt. RC6 frozen.
