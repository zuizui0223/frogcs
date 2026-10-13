# v7.3 — PUBLIC Australian frog assemblages: matched four-plot water-proximity grouping and seasonal heterogeneity

**Executed 2026-10-13 JST. Real published frog detections; exploratory original source ecology; NOT evidence of causal water effects, individual frog memory or source-complete population monitoring.** Independent [frogcs PR #135](https://github.com/zuizui0223/frogcs/pull/135) only, manuscript JAE RC6/main unchanged. [Source design/contrasts frozen BEFORE new v7.3 results](V7_3_PUBLIC_FROG_WATER_PROXIMITY_FOUR_PLOT_SEASON_TEST_CONTRACT.md), **after** seeing v7.1 and v7.2 aggregates. The exploration status must not be misreported as prospective preregistration.

## Source-grounded ecology of the actual plot classes

The original [Hoefer et al. (2026) frog preprint, Figure 1](https://ecoevorxiv.org/repository/object/11696/download/21102/) explicitly describes six Australian sampling sites each with two ARUs **within 50 m of water** (original `WetA,WetB`) and two **more than 500 m from a water source** (`DryA,DryB`). The same layout is described in the [authors' 2025 related methods paper](https://doi.org/10.1111/2041-210X.70169). The original code [lists the same four actual plot IDs per site](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/scripts/R_code_biodiversityFrogs.qmd). **These are waterbody-proximity categories, NOT measured water-depth, wet-versus-dry episodes, random treatments or identified frog home wetlands.**

Source file [Hoefer et al. 2026 Zenodo v2.0](https://zenodo.org/records/21634473) `data/frog_data_season.csv` pinned Git blob `e5a419574be5e3f9922989f9aa6001fbb7f09d01`, SHA-256 `07a825f7b3269b7d15a353c11a099bceecafef4a5d9a5ffb8a80126bc18d4bc5`. It has **13,577 positive** PAM.all frog detection rows and **34 detected species identities** across six original sites × four plots, 2019–2023. Using the corrected [southern-summer season-year from v7.2](V7_2_REAL_FROG_SUMMER_YEAR_REPAIR_AND_DRY_WET_PLOT_RESULTS.md) leaves **197** nonempty `site×plot×season×year-cycle` detected species-list cells. **Records of complete valid listening opportunities and non-detections are not contained in this released file.**

## Primary comparison: actual water-proximity grouping versus all alternative 2+2 labels

Only **26** `site × author-season × corrected season-year` groups had positive detection species lists in **all four** plot identities. This smaller, explicitly matched frame corrects the denominator problem in the earlier v7.2 **partial-group** plot comparison. Each complete group uses the same **six** pairwise binary Jaccard similarities:

- Original distance-defined two-pair grouping: `DryA–DryB`, `WetA–WetB` (mean of two within-distance-class similarities), contrasted against the four between-class plot pairs.
- Other two possible unordered 2+2 groupings: `DryA–WetA` & `DryB–WetB`, or `DryA–WetB` & `DryB–WetA`, with identical within-minus-across formula.
- Scores are first averaged across eligible complete groups **within each of the six original sites** and then six sites given **equal weight**. No species detection row, overlapping pair or repeated year is treated as an independent site.

The **observed mean original water-proximity grouping advantage is +0.035027 Jaccard units**; **4/6 sites** have a positive contrast, **1/6 negative**, the remaining site zero. Site-average scores range **[−0.085780,+0.155397]**, and the descriptive 5000-draw **site-bootstrap 95% interval [−0.027797,+0.095111] crosses zero**.

**Exact site-fixed grouping reference:** there are **three** possible unordered 2+2 partitions of four plots; choosing one *fixed per site across all its seasons/years* yields **3^6 = 729** alternative assignments, avoiding spurious season/day independence. The observed class partition is not extreme: **0.123457** of assignments yield an equal or larger mean; reference 2.5–97.5% scores **[−0.050532,+0.053200]**, centered at 0. **The fraction is NOT a randomized-experiment p-value**, because the original near/far classes were environmentally structured, not randomly assigned.

**Conclusion:** physical water-proximity classes align with slightly more similar observed frog acoustic detected-species lists, but **the evidence for systematic six-site community differentiation by the actual 2+2 grouping is weak**. A positive mean should not be framed as proof of water-driven filtering or evolved habitat choice.

## Prespecified season heterogeneity: report ALL four, not the biggest

| Author season | Complete four-plot positive groups | Sites represented | Mean site-weighted original grouping advantage |
| --- | ---: | ---: | ---: |
| Autumn | **7** | **4** | **+0.084673** |
| Winter | **5** | **5** | **−0.001667** |
| Spring | **10** | **5** | **+0.066925** |
| Summer | **4** | **4** | **+0.090724** |

The apparent stronger contrast outside winter **does not establish seasonal ecological hydrological moderation**. The site subsets and numbers of complete frames vary by season; summer includes only **4** source-complete positive groups. To compare seasons *within the same site subset*, just **3 sites** had eligible complete frames in all four seasons. For those three, the original grouping's seasonal max-minus-min contrast was **0.232473**, and the site-fixed 3^3=27 label reference fraction at least that large was **0.111111** (reference central 95% **[0.033436,0.269340]**). This heterogeneity is not extreme relative to re-grouping and is not a robust season-by-water-proximity interaction.

Do not pick the apparently highest summer contrast and claim climatic driver; Australia's sites span multiple latitudes and local rainfall regimes, while this dataset does not provide date-specific water level, rainfall, acoustic effort or seasonal water permanence at each recorder.

## Fixed positive-detection-date support sensitivity (NOT effort adjustment)

Requiring **≥5 distinct days with any frog positive detection in each of all four plots** removes source groups and one site.

- **17** matched complete groups across **5** original sites (compared with 26 groups/six sites).
- Mean physical water-proximity grouping advantage **+0.034618**, 4/5 sites positive and one negative; site-bootstrap descriptive interval **[−0.033421,+0.089224]**.
- Exact 3^5=**243** site-fixed alternative grouping assignments: fraction ≥ observed **0.127572**. Similar to unrestricted 0.123457; not compelling structural separation.
- By season the *remaining four-plot complete groups* are autumn **6** (3 sites), winter **1** (1 site), spring **7** (5 sites), summer **3** (3 sites). **Zero sites** retain valid four-plot complete groups in every season; the seasonal heterogeneity sensitivity is **NOT EVALUABLE**.

Positive-detection dates are biological outcomes affected by frog calling intensity, detection probability and variable recorder availability; conditioning on five detected days is not equivalent to controlling verified acoustic recording effort, and cannot confirm the source mechanism.

## Technical QA and correction of counting bug

[Actual executed GitHub Actions run **38404243197 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38404243197), [frozen analysis code](scripts/analyze_public_frog_water_proximity_season_partition_v73.py), [aggregate executed JSON result](receipts/HOEFER_2026_REAL_PUBLIC_WATER_PROXIMITY_SEASON_PARTITIONS_V73.json). Prior to completion, the first result run had an **output count bug:** each complete group was appended three times to seasonal summaries, once per alternative plot partition. It printed 26 actual complete frames but season counts summing to 78. This *did not alter per-frame group scores or site-average similarities* because all entries were repeated equally. The [new regression-test-only run 38404155825 correctly FAILED](https://github.com/zuizui0223/frogcs/actions/runs/38404155825) on `SEASON_FRAME_COUNT_REPEATED`. Moving one append outside the loop repaired counts; [subsequent CI 38404243197 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38404243197) confirms seasonal **7+5+10+4=26** and sensitivity **6+1+7+3=17**. Programmatic source checks included original file SHA, 13,577 positive detection rows, 197 corrected positive cells, required exactly four author plot labels and 729 site-fixed labels. No source rows, site/animal names or coordinates were committed.

## Inference limits and handoff

There is no full standardized acoustic opportunity denominator, site-specific measured water-depth trajectory, original recorder noise/quality model, spatial microhabitat/recorder-distance covariate or independent manipulation. **Near-water detects more of certain frog calls** is a possibility, not a causal effect inferred here. The pairs differ geographically, in acoustic propagation, and possibly effort. Source-based community Jaccard is **not** true colonization, extinction, habitat-specific frog residency, chorus duration, memory, adaptation, larval recruitment or reproduction.

The public frog source is **different** from CEWH Flow-MER Murrumbidgee acoustic/depth monitoring. The independent water-arrival Q-A / previous-chorus Q-B need authenticated original wetland↔recorder↔logger/timestamp/effort/rights, which remain **not acquired**. The one metadata inquiry remains **UNSENT**. Stop further post hoc public-animal species stratification and toy mechanisms on this source unless an independent genuinely full acoustic opportunity ledger or recorded environment becomes available. Keep RC6/main untouched and PR #135 draft.

**Best supported original open-data finding across v7.1–v7.3:** Positive-detection frog species assemblages display modest, heterogeneous temporal recurrence and weak proximity-structured similarity, but apparent seasonal-year effects depended on repairing Australian summer and the apparent proximity seasonal interaction lacks common verified observation effort. This is a rigorous **ecological limit / falsification of overly strong generalization**, not a definitive ecological mechanism.
