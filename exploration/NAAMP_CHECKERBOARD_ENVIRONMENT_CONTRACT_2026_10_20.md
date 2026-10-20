# Independent exploratory checkerboard analysis contract — 2026-10-20

## Authority and firebreak
New user-directed exploration, separate from frozen RC6. This analysis cannot modify `paper/manuscript.md`, SI, frozen primary comparator, endpoint or submission evidence. A checkerboard result is a new question, not a re-labelling of within-taxon multi-site concentration.

## Biological question
Among taxa acoustically detected on the same NAAMP ten-stop route-night, do species avoid sharing calling stops (checkerboard segregation), co-occur more than expected (aggregation), or show no fixed-margin departure?

## Primary design (locked before analysis)
- Source: pinned USGS NAAMP source files via existing `scripts/naamp/run_naamp_ecological_pulse.py`; 2001–2015 standardized 10-stop runs.
- Matrix: species rows and ten listening-stop columns, positive = CallingIndex 1–3 (acoustic detections only).
- Eligibility: at least three positive taxa; at least two taxa occur at two or more stops; at least three active stops. Do **not** select cases by observed C-score or by rain effect.
- Per-matrix statistic: Stone–Roberts C-score = mean over species pairs of `(R_i-S_ij)*(R_j-S_ij)`; positive departure means more exclusion/checkerboarding than fixed-fixed expectation, negative means aggregation.
- Null: Curveball fixed-fixed trades preserve **both** taxon detection incidence (row sums) and total calling richness at each stop (column sums). 399 Monte Carlo states per matrix after 20*n_taxa trade proposals burn-in and 8*n_taxa proposals thinning. Seed 2840260.
- Primary summary: mean observed minus mean null C-score over eligible informative survey runs; route-clustered SE and interval; global Monte Carlo tail test on mean C-score.
- Frozen interpretation: environmental control holds *observed stop richness* and *taxon incidence depth* exactly, not local water state or the causes of those margins. Calling co-occurrence is not physical occupancy, and a positive checkerboard deviation does not identify competition.

## Secondary (fixed upfront)
- Among stable matched wetter/drier NAAMP pairs where both runs qualify, regress wet-minus-dry fixed-margin C-score residual on original rainfall contrast, air-temperature difference, day-of-year difference, year gap, State and seasonal RunNumber with route-clustered SE. This tests modulation of residual segregation, not precipitation causality.
- CallingIndex >=2 sensitivity on exactly the same initial run universe with its own fixed-fixed null. Do not promote secondary if primary is null.
- Report nonexchangeable and null-zero-variance matrices separately. If fewer than 100 informative matrices or fewer than 30 routes, report insufficient information rather than significance.

## Independent environment/history discrimination (separate specification)
Past strong site targeting has already been tested with within-pair-by-species fixed effects and strictly prior physical SiteID history. Such an estimate controls species and shared route-night atmosphere, but not changing wetland hydrology. A new direct check should add **simultaneous stop air temperature**, sound masking and survey position on a same-sample comparison. It still cannot prove environment-independent memory without local water-level/hydroperiod observations.

## Reproducibility
Do not overwrite existing receipts. Emit a new result JSON and an audit of retained populations, null sampling and margins. The result is exploratory, not independent replication or an RC6 claim.
