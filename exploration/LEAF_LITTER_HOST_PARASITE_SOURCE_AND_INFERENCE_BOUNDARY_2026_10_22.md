# Plant-litter mediation source gate — scientific interpretation boundary

**2026-10-22.** Historical published study, *not* newly acquired frogcs experiment and *not* a causal three-biotaxon discovery. This branch is separate from frozen `main` JAE RC6.

Original publication: DiGiacopo & Hua (2022), *Aquatic Ecology* 56:59–73, DOI https://doi.org/10.1007/s10452-021-09893-y. Dataset: Dryad DOI https://doi.org/10.5061/dryad.np5hqbztq. Public original names `Litter_Toad_Ecology_DiGiacopo_Hua_2021.xlsx`, `LITTER_TOAD_ECOLOGY_readme.txt`.

## Source-derived findings *reported by original authors* (not new frogcs computations)
- Plant-origin litter chemistry changes host susceptibility and free-swimming trematode cercarial survival in distinct experimentally manipulated exposure arms, altering final encystment patterns.
- For the huckleberry–autumn-olive pair, the study reports a reversal between host-only susceptibility predictions and the net observed host–parasite encystment assay. Such sign reversal motivates a non-additivity question, **but cross-arm differences cannot be called a statistically identified interaction without correct replication, comparator, and randomization design**.
- Litter modified **conspecific** tadpole crowding effects for one plant comparison, **not** interspecific frog competition.
- A separate odonate `Anax` predation assay did not support plant-litter difference in predator avoidance. Predation exposure used restricted subsets conditioned on surviving rearing, not randomized simultaneous fish×insect×frog regimes.

## Current scientific decision
The plant→frog behavioral-site-choice experiment and the plant-litter→host–parasite experimental pathway give two separate mechanistic leads. The missing frogcs hypotheses remain: (A) experimentally altered heterospecific frog-frog competition by live macrophytes, (B) randomized plant→fish/odonate→frog survival mediated effect, (C) higher-order multi-biotaxon factorial contrast. A different published experiment with hosts and parasites alone cannot prove B or C.

## Data integrity
Audit only metadata first. API: `GET /api/v2/datasets/{encoded-doi}`, `/versions`, `/versions/{id}/files`, `/files/{id}/download`. Verify original DOI, named workbook, source digest (if supplied) and **sheet names/header columns only**. Do not inspect response values or record any numerical reanalysis until grain, experimental unit and response-specific model are specified. Original manuscript already publishes results: any future reanalysis will be retrospective by definition. **Never claim retrospective selection is preregistration**. Original Dryad workbook is not checked into GitHub.
