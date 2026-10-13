# v7.2 — Real public frog community analysis: southern-summer correction and author-labelled Dry/Wet plot comparisons

**2026-10-13 JST. Executed actual published animal detections, not simulation. Source units repaired; no strong ecological habitat mechanism demonstrated.** Independent frogcs draft PR #135. Frozen [v7.2 analysis contract](V7_2_PUBLIC_FROG_SOUTHERN_SUMMER_REPAIR_AND_PLOT_LABEL_CONTRACT.md) committed **before v7.2 species-similarity outcomes were examined**, but *after* v7.1 aggregate analyses. Thus the plot-label comparison is explicitly exploratory, not preregistered confirmation.

> **v7.3 later matched-frame update (2026-10-13):** The [original 2026 frog preprint Figure 1](https://ecoevorxiv.org/repository/object/11696/download/21102/) specifies **Wet = recorder within 50 m of a body of water; Dry = recorder >500 m from water**, rather than merely arbitrary plot labels. This is fixed waterbody proximity, **not measured time-varying wetness**. The present v7.2 +0.023781 plot result pooled positive pairs from some *partial* four-plot frames. The [actual v7.3 matched **all-four-plot positive frames** analysis](V7_3_REAL_PUBLIC_FROG_WATER_PROXIMITY_SITE_FIXED_SEASON_RESULT.md) instead used **26** common-source groups and a site-fixed exact 3-way grouping reference, obtaining **+0.035027**, descriptive six-site bootstrap **[−0.027797,+0.095111]**, and label-reference fraction **0.123457**. Both are weak exploratory descriptions; cite **v7.3** when discussing grouping against alternative plot partitions and retain the v7.2 source results unchanged for provenance.

## Original source, ecological frame and why the repair matters

The study [Hoefer et al. (2026), Zenodo version 2](https://zenodo.org/records/21634473), [original code](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/scripts/R_code_biodiversityFrogs.qmd) at author lines 92–97 and 1321–1328, explicitly uses **DryA, DryB, WetA, WetB** four plot labels at each six independent study sites and describes southern-hemisphere author-season windows **Dec–Mar summer, Mar–Jun autumn, Jun–Sep winter, Sep–Dec spring**. The actual published CSV has positive rows in December–February summer, March–May autumn, June–August winter, September–November spring, confirmed in [live source-grain-only v7.0 CI run 38364038791](https://github.com/zuizui0223/frogcs/actions/runs/38364038791).

The [original v7.1 temporal comparison](V7_1_REAL_PUBLIC_FROG_SEASONAL_RECURRENCE_RESULT.md) unintentionally keyed the author's **summer** by ordinary calendar year and thus counted December of one real summer separately from January/February of the *same* southern summer. Actual source-only diagnostic: **34 site×plot×summer seasonal episodes** have positive dates spanning two calendar years. Under the corrected rule, summer December YYYY belongs to **season-cycle year YYYY+1**, whereas January–February and other season dates stay in their own calendar year. The nonempty positive community cell total changes from **216** under old calendar partition to **197** under faithful season cycle partition. The old 216-cell / +0.031310 result remains **mathematically valid for the old bins but should NOT remain the best ecological interpretation**.

Original CSV pinned by Git blob `e5a419574be5e3f9922989f9aa6001fbb7f09d01`, SHA256 `07a825f7b3269b7d15a353c11a099bceecafef4a5d9a5ffb8a80126bc18d4bc5`. Total **13,577 positive acoustic detections** of **34 frog species**, not 13,577 completed listening opportunities and not validated species absences. All 24 plot identities are exact original four plot codes within six source sites; no coordinates or individual taxon/site labels are published in this follow-up.

## 1. CORRECTED same-season recurrence vs within-cycle turnover

[Real-data CI run **38364526890 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38364526890), [executed aggregate JSON result](receipts/HOEFER_2026_REAL_SOUTHERN_SUMMER_AND_DRY_WET_PLOT_V72.json). Each comparison uses detected species *sets* (presence among published positive detection rows) and the Jaccard intersection/union similarity. Each site contributes one mean contrast; equal weight across **six sites**.

| Axis under corrected Dec–Nov season cycle | Positive-cell pairs | Equal-site mean Jaccard |
| --- | ---: | ---: |
| A: same site and plot, same author season in *adjacent* season-cycle years | **97** | **0.451253** |
| T: same site and plot/season-cycle-year, different seasons | **213** | **0.438275** |
| P: same site/season-cycle-year/author season, different plot | **233** | **0.451345** |

**Corrected primary A − T = +0.012978** (was v7.1 old **+0.031310**). Only **3/6 sites positive**; descriptive six-site bootstrap 95% interval **[−0.026417, +0.050185]**, crossing 0. Site differences range **[−0.071365, +0.075563]**. The earlier value's small positive magnitude was partially dependent on how southern summers were incorrectly split by calendar year. **No strong seasonal-year recurrence effect is supported**.

Corrected secondary P − T = **+0.013070** (4/6 sites positive), descriptive interval **[−0.059616, +0.085349]**, also crossing 0.

## 2. NEW exploratory nominal Dry/Wet label grouping

Source plot codes identify two `Dry*` plots and two `Wet*` plots at each site; actual water depth, season-specific hydroperiod, physical distance between plots and microhabitat sensor validation are **NOT** in this dataset. We test only whether the **author's nominal plot label** corresponds to similarities among *detected* frog species lists.

At **matched site × author season × corrected season-cycle year**, compare same-category pairs **DryA–DryB / WetA–WetB** against the four cross-category Dry↔Wet plot pairs.

| Pair category | Paired comparisons | Equal-site mean Jaccard |
| --- | ---: | ---: |
| Same Dry/Wet plot label class | **75** | **0.467760** |
| Between Dry and Wet label classes | **158** | **0.443978** |

**Δ_H = same-category minus cross-category = +0.023781** Jaccard units. **4/6 sites positive, 2 negative**, site effects range **[−0.040875, +0.107275]**. Six-site descriptive bootstrap 95% interval **[−0.020382, +0.067945]**, crossing zero. Therefore **weak descriptive ordering only; no clear, general Dry/Wet plot-category separation demonstrated.**

This cannot be called water-induced ecological filtering: nominal `Wet` is **not a measured hydroperiod for each observation**, and the plot classes were **not randomized treatments**. Shared landscape location, unequal recorder effort, acoustic propagation and calling detectability can all affect observed positive species lists. This dataset is a separate source from Australian CEWH Flow-MER.

## 3. Fixed positive-detection-day support sensitivity (both comparisons)

Requiring ≥5 distinct calendar days with any positive frog detection in EACH compared seasonal cell (threshold fixed before v7.2 contrast) changes comparisons:

| Axis | Pair counts | Equal-site contrast | Site directions | Descriptive 95% site-bootstrap |
| --- | ---: | ---: | ---: | --- |
| Corrected A − T | A **68**, T **160** | **+0.033781** | **5/6 positive** | **[−0.000631, +0.062058]** |
| Nominal Dry/Wet Δ_H | same **54**, cross **114** | **+0.065911** | **5/6 positive** | **[+0.019542, +0.108368]** |

**This stronger-looking restricted Dry/Wet result is NOT effort-corrected evidence.** Positive detection days are influenced by the same frogs' activity and species detection; the restriction conditions on the response and may select easier-to-detect or better-sampled plots. The unrestricted primary within-vs-cross plot result crosses zero. Do not cherry-pick the restricted interval or claim statistically established habitat filtering. For the temporal contrast the restriction still crosses zero.

## 4. Code and validation

- [Source pinned, corrected analysis script](scripts/analyze_hoefer_biological_summer_and_plot_category_v72.py) imports [the original v7.1 code](scripts/analyze_public_hoefer_seasonal_recurrence_v71.py) for unchanged Jaccard/site-bootstrap calculations.
- Tests checked correct December→January summer cycle merging, source-month matching (reject invalid March summer), two same-category vs four cross-category plot pairs in full groups, no zero-filled missing cells, and previous v7.1 primary mean +0.03131 reproduced exactly on its legacy calendar bins.
- Actual [Actions **38364526890 SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38364526890). Source git blob hash, 13,577 rows, six physical site labels, all 24 original plot codes, **197** corrected nonempty cells were asserted before result export. No raw site/species/event records, location coordinates, source audio, synthetic ecological outcomes or raw original data were committed.
- [Machine-readable, permanent aggregate result](receipts/HOEFER_2026_REAL_SOUTHERN_SUMMER_AND_DRY_WET_PLOT_V72.json) documents the correction and both predeclared plot/temporal comparisons; see the actual job logs for the full executed JSON.

## Biological conclusion and handoff

**Supported:** In this original multi-year public frog acoustic source, apparent annual detected-species assemblage recurrence is *sensitive to proper southern summer-year definition*. With season repaired, site-averaged repeatability advantage is near zero and inconsistent. Detected communities are **slightly more similar in within-author-Dry or within-author-Wet plot label pairs than across labels on average**, but this modest pattern is inconsistent across six sites and changes substantially under conditioning on positive-detection support.

**Not supported:** seasonal site fidelity, true occupancy/disappearance, measured local wet/dry water effects, hydrological path hysteresis, causal acoustic memory or evolutionary adaptation, acoustic chorus duration, recruitment or successful reproduction. No valid no-call/recorder opportunity manifest or local water depth from the same original observations exists in this exposed file.

**Decision:** preserve this correction as an honest *empirical* sensitivity result. Further species-by-species subgroup searches or method tuning to manufacture significance are not justified by these data. The separate CEWH Murrumbidgee passive recorder↔wetland↔local depth source gate Q-A/Q-B remains blocked and [single custodian enquiry](V6_0_CEWH_ACOUSTIC_HYDROLOGY_SOURCE_INVENTORY_REQUEST_UNSENT.md) remains **UNSENT**. Do not alter JAE RC6 main, do not use TinyFish.
