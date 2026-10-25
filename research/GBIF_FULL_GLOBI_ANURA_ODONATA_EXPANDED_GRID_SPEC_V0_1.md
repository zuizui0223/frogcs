# Full GloBI (2026-09) → expanded GBIF (2026-08) Anura + Odonata stage grid v0.1

2026-10-25; **post-readback exploratory** extension to correct the initial 61-species sampling bottleneck, specified before reading this expanded GBIF outcome. NOT a second source-independent confirmation of the same GBIF program.

## Eligibility before querying GBIF

Use **the complete precomputed full GloBI source MD5-pinned** [stage provenance](results/full_globi_2026_stage_gbif_grid/observed_results.json) (1240 valid certain staged non-self source rows, 881 species×stages directed patterns, 768 species-directed pairs). Download actual source-level row CSV from the successful earlier run [40193636562](https://github.com/zuizui0223/frogcs/actions/runs/40193636562); never infer the 881 patterns from the 10-pair pilot.

Select **only non-self** species-pair stages where BOTH actor and target are within `Anura` or `Odonata`, because these are the two *actual anonymous, verified publicly available* whole-order GBIF partitions in the experimental `development/2026-08-01-DWCA/p_taxon` S3 release. Do **not** call a link with `Caudata`, Dytiscidae, a bird, a snake, other aquatic guild, or other species unobserved in these partitions a negative; those taxa are unavailable to this grid scan and form a separate explicit missing-coverage tally.

Include every source-selected Anura/Odonata species with eligible staged nonself edges; no GBIF-geographic postselection and no convenience hand fallback. Deduplicate species by exact canonical binomial string, retain stage classes adult, aquatic_immature, juvenile, egg. Input taxonomic labels inherit interpreted GloBI taxonomy and may disagree with GBIF August 2026 snapshot; note this limitation.

## Full GBIF source and analysis

Read every Parquet rowgroup overlapping selected species-name range from all 7 S3 files in the whole-order `Anura` and `Odonata` partitions. Replicate 2010–2026 and coordinate uncertainty ≤10 km (NA uncertainty retained), `occurrenceStatus='PRESENT'`, `hasGeospatialIssues=false`, year/month present. Record original count with species filter, quality-filtered count, accepted stage-labeled count, number of rowgroups skipped/scanned, and unique species-stage × 1° grid × year × month counts. Fully stage-unlabelled records are separately counted but excluded from stage comparisons.

For every eligible source-staged nonself GloBI pair, compare 1° grid-month-year GBIF stage reporting overlap and 1° grid-year without month, with ≥5 GBIF records per species-stage-grid-month as robustness. Count source patterns with missing species/stages and data coverage separately from **positive** grid-year-month co-reporting; a missing overlap is not a species' absence or a refuted predator–prey link.

Also distinguish **conspecific cannibalism** from interspecific trophic edges, **reciprocal species pair in GloBI** from **verified stage reversal**, **same GBIF grid-year-month** from **same wetland/attack**. Source DOI/reference citation count is evidence attribution, not independent observed attacks. Fix issue where prior full GBIF scan reported 9/9 co-occurrences but 7 were self-pairs and only 2 were nonself; this is a selection artifact, not biological evidence of 100% overlap.

## Source-specific limits and next global escalation

The GBIF experimental Parquet `speciesKey` uses its own identity format; this job uses species names and must be followed by accepted name/synonym comparison for all selected taxa. Caudata is not an accessible standalone partition under the known 2026-08 `p_taxon` S3 path, and Coleoptera is too large (8 Parquet files totaling >14 GB) for unrestricted opportunistic scanning. These require a separate study-wide GBIF archive request; **do not silently restrict ecological hypotheses to Anura/Odonata worldwide**.

The stage-gridded observations are site/time reporting opportunities only, not actual interaction, mortality, abundance or chorus history. Rainfall and emergent plants need independent wetland-specific observations; a global climatic raster cannot by itself supply frogcs RC6 72-hour rainfall cues.
