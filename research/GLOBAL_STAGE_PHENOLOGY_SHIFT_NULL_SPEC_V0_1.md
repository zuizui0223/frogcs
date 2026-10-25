# 全球の発生段階別・月単位の共報告：時間シフト帰無モデル v0.1

2026-10-25. **Prespecified before opening the in-flight full GloBI→GBIF joined spatial output** (workflow 40193636562). This is a prospective *post-API-pilot* diagnostic, not formal preregistration and not a prediction of observed kill frequency. Distinct from the frozen RC6 JAE manuscript.

## Biological question

Given a literature/index-recorded directed predator-stage→prey-stage GloBI link and independent GBIF **co-reporting** of both stages within the same **1° grid, calendar year**, does the number of **same month** GBIF grid-year reports exceed what one would expect if one partner's reporting calendar were displaced by months? This may detect seasonal synchronization in recorded activity — but **neither spatial grid co-reporting nor calendar concordance establishes actual local predation, direct acoustic listening, or trophic dependence.**

## Frozen inputs and primary population

1. GloBI version pinned to 2026-09-10, Zenodo 10.5281/zenodo.22691479 (MD5 8212776b7ba0c4fa8de26a00b5ce8595), **full 24,453,954 records** screened to freshwater focal guilds.
2. [Full-stage join](scripts/full_globi_staged_gbif_grid.py) expected artifact `nonself_stage_pair_grid_results.csv` with unique named predator species, prey species, **both unambiguous normalized stages**, source-guild and citation provenance, distinct GloBI directional association link.
3. GBIF [complete checked experimental taxon-partition scan](scripts/gbif_open_full_stage_grid.py) prior successful CI run [40190152042](https://github.com/zuizui0223/frogcs/actions/runs/40190152042), `focal_stage_1deg_month_year.csv`, **61 selected Anura/Odonata target taxa**, species×stage×1° grid×year×month records with observation counts. This is a noncanonical (August 2026 experimental) taxon snapshot and **not** the official authenticated GBIF 2026-10 bulk release. No fine-scale pond locations, exact interactions or years with zero *biological presence* are asserted.
4. Main eligible analysis set: distinct **non-self species-stage directed links** with both predator and prey positive GBIF stage grid observations; exclude missing stage or unmatched species. Preserve each original citation and source DOI, no independent source inference across rows. Do **not** condition on *positive actual month overlap* when selecting pairs.
5. Multiple GloBI citations or rows for the same directed named predator-stage/prey-stage combination count as **one candidate**, not replicated ecological experiments. Keep `n_original_studies` and source provenance in reporting.

## Main estimand and a negative control

For each eligible pair-stage `e`, compute:

- `C0(e)`: number of *unique 1° grid × year × month* cells in which both species' stipulated developmental stage each have ≥1 GBIF report. Strict sensitivity requires ≥5 reports for each species-stage-cell.
- `C_year(e)`: grid×year cells where both stages have ≥1 report at **any** month, so lack of C0 is not confused with no spatial/year co-reporting.
- **Fixed cyclic months null:** for `d=1…11`, shift **prey** GBIF month `m` to `((m-1+d)%12)+1` independently in each grid×year. Preserve prey geographic/year footprint, number of recorded prey months, seasonal profile, species stages and recording counts; only relative calendar phase changes. Compute `Cd(e)` and descriptively report `C0 - mean(Cd)` and `C0/(mean(Cd)+1)`, `rank among 12 phases`.
- One-sided phase-rank `(1 + count_{d>0}(Cd≥C0))/12` is **diagnostic** only; 11 global shifts supply coarse resolution (minimum 1/12) and do **not** support a statistically independent P-value for all worldwide interactions. Do not report 0.001 from artificially treating matching cells as independent trials.
- **Resampling caution**: global stage/reporting phenologies reflect taxon traits, daylight, weather, spatial range and observer activity; excess phase overlap can arise even if predator-prey link is biologically unrelated. The null distinguishes calendar congruence from arbitrary month offsets, **not causation**.

## Robustness and interpretation

- Report first-order `C_year` and `C0` separately; include nonoverlapping pairs with actual GBIF stage coverage as zero observed **reporting** overlap, never zero biological coexistence.
- Split descriptive summaries by `predator_guild × prey_guild × predator_stage × prey_stage`, source evidence (Quick Pond interpreted metaweb, iNaturalist link or other), and occupancy coverage. Use no significance test for sparse strata and prevent one large repeated food web source counting as independent evidence.
- As controls: compare `d=6` half-year shifted month co-reporting vs `C0`; include threshold ≥5 each in a grid/month; compare annual spatial overlap to show role of month resolution. Maintain a country/continent sampling-effort warning.
- If less than 5 eligible complete pairs with any shared spatial/year cells, **do not claim an ecological seasonal-network result**; report data feasibility and bottleneck.
- Interpret presence of `C0>0` as **compatible recorded-stage encounter opportunity** only, *not observed interaction*. If `C0 > null`, label “excess seasonal co-reporting within coarse GBIF grids,” not predator-prey attraction or acoustic eavesdropping.
- Data outputs: `stage_phenology_shift_pair_results.csv`, `stage_phenology_shift_summary.json`, QA counts, and source lineage. Use registered GBIF download DOI and finer wetland masks before inferential extensions.

## Why this is the appropriate intermediate study

The frogcs original macro finding is that rain gates chorus activity and the activated species×physical sites recurred (NAAMP). NPS external multi-year series replicated historical acoustic site association; the GloBI/GBIF global panel now tests whether the **temporal developmental-state overlap** required for trophic interactions is detectable. All three are different estimands. Connecting them causally requires observed plant structure, wetland hydrology, local frog acoustics, larvae and direct predator interactions within the **same physical wetland/time**, not opportunistic data aggregation.
