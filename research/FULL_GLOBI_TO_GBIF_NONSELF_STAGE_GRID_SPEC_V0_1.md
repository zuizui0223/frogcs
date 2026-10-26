# Global full GloBI → GBIF 1° stage grid non-self trophic opportunity v0.1

2026-10-25. New correction test specified **after** first GloBI full source results and GBIF preliminary grid results were seen. This is exploratory post-hoc QA, **not preregistered discovery**. Keep RC6 JAE main unchanged.

## Motivation and exact error being repaired

Full frozen GloBI 0.11 [DOI:10.5281/zenodo.22691479] was successfully downloaded and checksum-verified (2,375,721,521 bytes, MD5 8212776b7ba0c4fa8de26a00b5ce8595), yielding 24,453,954 interactions. An aquatic focal subset has 77,720 eligible records and 1,835 raw records where *both* stage fields are populated.

The first anonymous August 2026 GBIF 1-degree species-stage raster scan covered ~4 million georeferenced records, but its **nine** selected trophic pairs with month-year grid overlap contained **seven self-pairs**, incorrectly elevating conspecific source observations into supposed independent trophic direction evidence. This source selection, not the GBIF spatial gridding, must be corrected.

## Updated fixed edge gate (no GBIF geography dependent selection)

1. Use **all** full GloBI 0.11 focal species species-level original interaction records `eats/preysOn`; refuse live API head rows as input.
2. Keep **predator != prey** for interspecific trophic analyses. Report same-species cannibalism in a *separate* accounting variable only, never as A→B/B→A.
3. Require both sourceLifeStageName and targetLifeStageName to be unambiguously staged into `adult`, `aquatic_immature` (tadpole/larva/nymph), `juvenile`, `egg`, `pupa` [exclude pupa from strict aquatic immature unless verified stage-specific habitat]. Unknown, `-999`, composite `juv./adults`, `adult and juvenile` and ambiguous mixed-stage terms must be excluded from confirmed-stage analysis.
4. Retain original sourceDOI, referenceDoi, referenceCitation, sourceNamespace and original raw stage strings per row. Distinct citation strings are **not independent predation events**; "metaweb"/"Quick Pond" remain source-reported links until origin-specific evidence assessed.
5. Aggregate unique **directed species×predator-stage×prey-stage** patterns, with source rows, source DOI/reference diversity and sample source strings. Do **not** rank by output geography and do not call any of these stage patterns actual predation flux.
6. Define **different-species reciprocal candidate** only if both A→B and B→A have stage-known links after 1–5. For a genuine *stage-dependent* trophic reversal, additionally require source-verified stage contrasts in distinct timing windows; no such causality is inferred from the GloBI table alone.
7. Reuse independently executed, complete experimental GBIF Aug 2026 `Anura` and `Odonata` species-stage source snapshots: 4,026,251 accepted focal rows in 655,843 species×stage×1°×year×month report cells; 61 requested species (59 detected). **Anura/Odonata only**; Caudata/Dytiscidae staged edges cannot be spatially tested from these two partitions and should be counted as uncovered, NOT negative/zero.
8. Compare all distinct nonself GloBI stage patterns that have GBIF stage observations for BOTH species in this GBIF artifact. Compute 1° site/grid overlap, grid×year overlap, and grid×year×month overlap; retain `n_records` cell report counts, and report a threshold >=5 for both stages as sensitivity. Month/year overlap is **not same pond or confirmed feeding**.
9. Separate source-complete coverage `eligible GloBI stage patterns` from `GBIF target species included` from `both stage GBIF detected`; tests on only observed subsets are reporting-opportunity feasibility, not representative worldwide rate. Exclude all species self-links from pair-count numerator and denominator, and report exact how many earlier spurious "nine" arose from self-links.
10. Time: GloBI fixed 2026-09; GBIF experimental 2026-08 source, 2010–2026 occurrences. Both are versioned/pinned source *editions*, but GBIF experimental taxonomic species names must be matched to source species literal and accepted GBIF taxonomy separately. No global ecological prevalence/P values from these source observations.

## Outputs

- `full_staged_edge_provenance.csv`: all source-verified staged original GloBI rows in focal guilds, with nonself flag.
- `nonself_stage_pair_grid_results.csv`: every nonself staged GloBI species pair, with GBIF coverage and 1° month-year overlap, missing coverage distinguished from biological zero.
- `observed_results.json`: checksum, total source rows, raw and stage-valid rows, independent citation distribution, reciprocal candidates and actual checked GBIF grid comparison.
- Provenance: executable Python + CI with checksum-pinned 2.4 GB source and prior successful GBIF artifact. **If download/retrieval fails, do not substitute stale source or infer results.**
