# ONTO-TIME independent original-data macroecology: 36 Australian lat×year panels (2026-10-25)

## Status and ecological answer

**NEW INDEPENDENT ORIGINAL-DATA EXPLORATORY MACRO RESULT — DONE.** Not the Beranek 2023 paper enlarged, not NAAMP RC6 analysis, not a paper-level meta-analysis. One independently constructed Australia-wide biodiversity macro panel using original GBIF and FrogID occurrence observations (2018–2023) with prespecified six 6° latitudinal strata.

Biological question for this lane:

> At which geographic and temporal scales do source-recorded frog acoustic occurrence seasons and odonate-adult observation seasons coincide, potentially making a stage-transition interaction opportunity available?

**Strict claim ceiling:** patterns in occurrence-reporting seasonal distributions only. Neither true predator/prey role direction nor amphibian tadpole and dragonfly larval stages nor predator alarm-recipient behavior are measured in this macro source.

## Original-data denominator

- **6 latitude bands × 6 years (2018–2023) × 3 original record streams = 108 GBIF monthly-facet source queries**, all original source URLs and 12-month vectors saved in `ORIGINAL_GBIF_AU_6LAT_6YEAR_3STREAM_MONTHLY_V0_1.json`.
- FrogID version 7.0 source datasetKey `47c9fee2-619a-481c-a114-386bc4748256`: **1,026,737 frog species-positive acoustic-derived occurrence rows** across the 36 included panels (not number of unique recordings).
- GBIF Odonata `taxonKey=789`, explicitly `lifeStage=Adult`: **16,148 records**.
- Same Odonata with no life-stage filter, known calendar month only: **114,179 records**. The explicit Adult label is a selected subset.
- An *original-data error* was caught and fixed: four Odonata any-stage year×latitude counts included **263 records with year but no month** (252+9+1+1); source queries with explicit `month=1,12` exactly recovered the independently returned 12-month facet totals. Undated events were not added as zeros.
- Before the 36-panel retrieval we fixed eligibility: ≥100 frog source rows, ≥30 adult Odonata, ≥100 all Odonata; ≥4 observed months in both frog and adult. **34/36 passed**; northmost 2018 (28 Adult) and 2020 (9 Adult) were excluded under the frozen rule.

## Macro result: annualized phenology opportunity alignment is not universal

For each usable latitude×year, compute 12 monthly occurrence fractions for FrogID (`p_f`) and explicitly tagged adult Odonata (`p_o`). The descriptive **seasonal overlap** is:

`O = Σ_{m=1}^{12} min(p_f[m], p_o[m])` (range 0–1).

The seasonal rotation benchmark is the mean `O` over all 12 integer month shifts of the odonate monthly distribution (including the observed zero shift). **This is not a seasonally adjusted causal null**, only a reference for whether the actually reported seasons align more than arbitrary circular shifts.

- Mean observed O across 34 eligible bands×years: **0.445764**.
- Mean 12-month rotation reference: **0.442050**.
- Difference **+0.003714**, with **17/34 positive** and **17/34 nonpositive**. **No common nationwide surplus alignment** appears in this exploratory original-data endpoint.
- Equal weighting over six latitude-band mean differences gives **−0.003915**, again effectively zero.
- Sensitivity using *all* Odonata in place of explicitly stage-labeled adults changes overlap on average by **0.060541** (Adult overlap lower). Stage annotation is not ignorable.

## More interesting spatial heterogeneity (descriptive; not a direct role reversal)

| Latitude °S | Eligible years | Frog/Adult observation overlap | Rotation baseline | Difference | Positive years |
| --- | ---: | ---: | ---: | ---: | ---: |
| 44–38 | 6 | 0.3940 | 0.4315 | −0.0375 | 1/6 |
| 38–32 | 6 | 0.5158 | 0.4881 | +0.0278 | 3/6 |
| **32–26** | 6 | **0.6459** | 0.5486 | **+0.0973** | **5/6** |
| 26–20 | 6 | 0.4293 | 0.4382 | −0.0089 | 4/6 |
| 20–14 | 6 | 0.4376 | 0.4063 | +0.0314 | 4/6 |
| **14–10** | **4** | **0.1550** | 0.2886 | **−0.1336** | **0/4** |

The largest positive and negative latitude-band contrast was selected *after reviewing all band effects* and is descriptive, not a preregistered significance test. On the four shared valid years between 32–26 and 14–10°S, the positive-mid minus far-north difference is **+0.03136, +0.23018, +0.24680, +0.25503** (2019, 2021, 2022, 2023), but both regions differ in observing systems and source stage annotations. No confidence interval/p-value is promoted from these dependent panels.

## Independent evidence layers: real trophic inversion vs cue persistence

The independent comparative atlas (`../registry/COMPARATIVE_INTERACTION_CLOCK_ATLAS_V0_1.json`) records **nine source-backed contexts** rather than extrapolating *Litoria×Anax* alone:

- **Direct reciprocal stage roles:** *Litoria×Anax* across tadpole and adult frog stages; asp×bleak egg/adult fish; juvenile/adult stage-specific reciprocal IGP of *Neoseiulus×Phytoseiulus*. These are different stage clocks, not one pooled response.
- **Size-dependent potential reversal:** pike×stickleback, early predation directly observed but pike→stickleback threshold is gape-modelled. Not an observed crossover date.
- **Context-dependent attack:** *Xenopus×Gambusia* experimental stages×light.
- **Risk-cue identity change without reciprocal predation:** tadpole predator-odor generalization between diving beetle stages but not salamander stages in Thapa et al. 2024; cannot say “frog sounds warn other species”.
- **Risk persists after attack becomes impossible:** Japanese *Zhangixalus×Notonecta*, predator cues can alter metamorphic life history even past physical prey-size vulnerability (Urushihara & Takatsu 2026), **not** mutual predation or a sound experiment.

The direct/behavioural citations and observational clocks remain isolated in this registry; duplicate programmes are not counted as independent ecological populations or pooled “meta effect size”.

## Ecology-first next source decision

The original Australian Anura stage metadata are insufficient for direct large-scale stage-switch estimation: in 2018–24 GBIF Anura has 1,378,754 occurrence records but only 88 explicitly Larva and 20 Egg; Odonata has 147,911 records with 105 explicitly Nymph and only 3 Larva. Unknown lifeStage cannot be treated as adults or larvae. This is a data-observation limitation, not an ecological absence of stages.

A decisive cross-system macro test of predator/prey **direction** would need original `species_A × lifeStage_A × species_B × lifeStage_B × interaction_direction × risk_response × observation_effort × site/date` data from harmonized independent programmes. Neither GloBI missing edges nor GBIF species occurrence co-listing replaces source-observed direction. An independently validated receiver cue experiment is required before claiming acoustic warning.

## Reproducibility

- Original frozen 108 month facets: `ORIGINAL_GBIF_AU_6LAT_6YEAR_3STREAM_MONTHLY_V0_1.json`
- Calculated 36-panel results and six latitude effects: `AU_36_PANEL_STAGE_ACOUSTIC_PHASE_RESULTS_V0_1.json` and `AU_36_PANEL_SUMMARY_V0_1.csv`
- Independent pure Python source checksum/eligibility/overlap reproduction: `../analyze_australian_phase_atlas.py`
- 11 dedicated regression/source-boundary tests: `../../tests/test_australian_macro_stage_phase.py`
- CI: `.github/workflows/onto_time_original_macro_qa.yml`, **SUCCESS**.
- All data used are aggregate monthly GBIF occurrence counts. No sensitive frog coordinates or event identifiers are reposted. JAE RC6 remains untouched.

## Scientific status (precise)

**Supported in original multi-region data:** heterogeneous relative phase/overlap in *reported* frog call-positive observations and *tagged adult odonate* observations, with no near-universal national excess.

**Not supported by these sources:** the original hypothesis that frog calls reliably forecast *actual* imminent trophic-role reversal, a receiver's defensive/alarm use of such calls, a causal latitude effect, or an Australian-wide demographic predator-prey transition.

This is an independent macroecological **source atlas and exploratory result**, not a claim of a universal trophic-stage mechanism.
