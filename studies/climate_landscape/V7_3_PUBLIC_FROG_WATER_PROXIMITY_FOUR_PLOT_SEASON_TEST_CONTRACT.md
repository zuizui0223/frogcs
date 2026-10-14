# v7.3 — Distance-to-water spatial grouping and season-dependence, public frog detections

**Method/source contract committed BEFORE examining any v7.3 outcomes. 2026-10-13 JST. Explicitly exploratory after seeing v7.1–v7.2 aggregate results.** Only independent draft PR #135; RC6/main unchanged. No TinyFish. No external custodian communication or original protected coordinates.

## Original study design and source provenance

[Hoefer et al. (2026) frog original preprint, Figure 1 and study methods](https://ecoevorxiv.org/repository/object/11696/download/21102/) states each of **six Australian survey sites** contained four 1-ha acoustic survey plots, including two Autonomous Recording Units **within 50 m of a waterbody** (`WetA`, `WetB`) and two **>500 m from a water source** (`DryA`, `DryB`). The same broader study design is documented in the [authors' 2025 mammals methods article](https://doi.org/10.1111/2041-210X.70169) and the [2026 frog paper's analysis code](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/scripts/R_code_biodiversityFrogs.qmd). **This is physical distance/proximity, NOT measured local wetland water depth/hydroperiod and not a randomized assignment.** Recorder sound propagation, recording effort, plot distances and habitat covariates can confound ecological interpretation.

Analyzed published source remains `frog_data_season.csv` of [Hoefer et al. 2026 Zenodo v2.0](https://zenodo.org/records/21634473), Git blob SHA `e5a419574be5e3f9922989f9aa6001fbb7f09d01`, exactly **13,577 positive acoustic detection rows**, 34 detected species across 6 sites×4 plots. Source-only verification (CI 38364038791) established the southern summer year crossing; v7.2 (CI 38364526890) corrected December to next season-year, leaving **197** nonempty `site × plot × season × season-cycle-year` detected species-list cells.

**Precondition:** do not create empty/zero species list for any unsampled or source-empty cell. A published positive detection is not a recorded survey opportunity, not proof of species absence in another cell, and not a causal measure of water preference.

## Primary structural question — does the physical 2+2 water-proximity grouping organize the observed frog species lists beyond alternative 2+2 pairings?

In each **complete four-plot positive cell group** `site×author-season×season-cycle-year` (all `DryA`, `DryB`, `WetA`, `WetB` with ≥1 published species), define binary species-list Jaccard similarity for every pair of plots. For exactly the *same frame* and six pairwise Jaccards, compute:

- **True grouping:** average of `J(DryA,DryB)` and `J(WetA,WetB)` minus the mean of the four `J(Dry*,Wet*)` cross-group pairs. No asymmetric rescaling or raw detection-row weights.
- **Two alternative groupings:** the only other two unordered partitions of four plots into two pairs: `(DryA,WetA) + (DryB,WetB)` and `(DryA,WetB) + (DryB,WetA)`, each contrasted against its complementary four cross-group pairs using the *same six comparisons*.
- **Site-summarization:** average each grouping's matched-frame score *within one original site* (all available seasons and year-cycles equal per frame), then give six original sites **equal weight** to produce `D_proximity`. Report pair coverage (number of full 4-plot groups), number of contributing sites, across-site mean, site signs and range. If fewer than 3 source sites have any complete four-plot frames, report **insufficient site support** rather than inventing a direction.
- **Site bootstrap:** 5000 draws of six **site-level** observed true-group means, with seed `20261013+73`, percentile descriptive interval, no confirmatory p-value.
- **Site-fixed label reference:** enumerate exactly `3^6 = 729` possible *site-level* choices among the 3 grouping partitions, keeping each site's chosen grouping **unchanged for all its observed seasons/years**. Report the rank/fraction of the observed distance-defined grouping among the 729 pseudo-groupings and the null range/central quantiles. This is a **conditional structural comparison**, NOT a probability of randomized water-distance assignment, causal evidence, or a frequentist hypothesis test for water.

This paired complete-frame comparator repairs the varying-pair denominators in the earlier v7.2 partial-group Jaccard diagnostic; do not preferentially cite whichever estimate is more positive.

## Fixed season heterogeneity (ecological core, no selected-season-only claim)

In each author season (`autumn, winter, spring, summer`), compute the same true grouping mean separately within each source site with ≥1 complete four-plot positive frame, then equal-weight original site means. Report **all four** seasons in fixed order (autumn, winter, spring, summer), n sites, n complete frames, group-score signs. Do not selectively highlight the maximum. To assess season variation **within a comparable site subset**, retain only sites containing complete four-plot positive groups in **all four** seasons; if at least 3, compute `H = max(mean_D_season)−min(mean_D_season)` and compare it to site-fixed label-reference heterogeneity using the same exact three groupings per site. Otherwise emit `INSUFFICIENT_ALL_SEASON_SITES`. This is **descriptive conditional heterogeneity only**, not climate/rainfall mechanism.

### Positive-date support sensitivity — fixed, may induce selection bias

Repeat primary grouping and all four season summaries requiring **≥5 distinct calendar dates with at least one positive frog record in EACH of the four plots in the group**. This is not acoustic recorder uptime or recording effort, and selects on the biological response; report differences and how many source sites/groups survive. If estimates reverse or disappear, mark **source-support sensitivity**; if estimates strengthen, **do not elevate** restricted results to a causal/confirmatory finding. No threshold search.

## Interpretation scope and stopping

- Strongest legitimate claim even if a positive pattern survives: detected frog species-list similarity aligns with the authors' water-proximity grouping more than alternative plot partitions **conditional on published positive records**, potentially seasonal in magnitude.
- Alternatives remain unequal recorder operating time, frog vocal detectability, recording beam direction/noise, distance/spatial separation, particular waterbody, season and detection biases.
- **NOT estimable from this source alone:** species occupancy, complete negative detections, actual seasonal water depth, water arrival, hydrological hysteresis, breeding success, individual site fidelity or memory.
- Do not hunt individual species, best months, best plot, p values or post-outcome threshold choices. Separate public source, not CEWH original Murrumbidgee archive or JAE RC6 replication.

## Execution audit

Use `scripts/analyze_hoefer_biological_summer_and_plot_category_v72.py` source-pinned `biological_cells()`, re-fetch at most 4 MB from the exact public GitHub raw host, verify Git blob. Include unit tests of exhaustive 2+2 partitions, site-fixed assignment count, four-positive-only frames, exact-match time granularity, no raw name/coordinates release. Output one JSON receipt containing only anonymized aggregate statistics, original source hash and official completed CI run; keep one-off CI code removable after execution. All source animal names/IDs read only in runner memory.

This work revises a **post-v7.2 exploratory hypothesis**. Honest negative findings are equally valid. Do not touch frozen RC6/main.
