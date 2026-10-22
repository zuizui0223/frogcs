# NAAMP macroecology: vegetation filters versus spatial and observational-time frog acoustic β-diversity

**Source-backed empirical synthesis — 2026-10-23** | All analyses carried out on the separate exploration branch; **frozen JAE RC6 `main`/paper/SI/submission not modified**. No new literature review, animals, field experiments or third-party raw data redistributed.

## Core macroecological question

> **Across a continental frog acoustic monitoring network, how much of species-pair association and within-landscape community turnover is organized by mapped aquatic vegetation, versus measured geographic separation and survey time?**

Inputs: original pinned **USGS NAAMP 2001–2015**, 7,848 protocol-standardized ten-stop survey runs; verified response-blind 12-shard USFWS NWI 250m habitat overlay, 5,147 geocoded physical sites; **6,236** complete ten-stop NWI/environment joins. Only qualifying sampling units enter each question. Source-workflow and frozen prespecified *new* analysis specifications are given below.

## 1 — Mapped plant affinity fails to account for global residual frog–frog acoustic pair structure

Across **25** historically eligible taxon units with estimated within-route NWI emergent PEM coefficient, compare taxon-pair difference in those PEM coefficients against their pre-existing, full-row/column-fixed, route-cross-fitted NWI-weighted acoustic co-detection residual. Controls: source pair detection count, null co-detection, same genus, relative taxon activity frequency. Test by **node-label permutation**, not naive 57 independent observations.

| Source acoustic definition | Eligible pair edges | β, percentage points per 0.1 taxon-slope gap | Taxon-node permutation one-sided P | Partial R² |
|---|---:|---:|---:|---:|
| strong CI≥2, primary | 57 | −0.1213 | **0.3264** | 0.24% |
| any CI≥1, secondary | 110 | −0.2656 | **0.1021** | 1.00% |

Strong edges also fail a within-genus label permutation (P=0.322); geographic halves disagree in slope sign and route-count reweighting reverses sign. **Do not claim that taxa diverging in mapped vegetation affinity consequently segregate acoustically.** This does *not* erase the earlier positive taxon-level associations (five of 25 were BH-supported); species-wise propensity alone was already shown insufficient to reproduce the original checkerboard fixed-margin residual. [Workflow #39869396031](https://github.com/zuizui0223/frogcs/actions/runs/39869396031), SUCCESS.

## 2 — Full community turnover across PEM boundaries is not supported

Independently read original NAAMP site species lists, not only the 25 slope-screened taxa. Among two **acoustically active** stations visited during the same ten-stop survey compute Sørensen community **dissimilarity** `1−2×shared/(rich_i+rich_j)`. Include run fixed effects, different mapped PEM class, wetland proportion gap, richness controls and ordinal station gap. Route-cluster uncertainty (station pairs are *not* independent replicates).

| Population | Sample | Mapped PEM boundary coefficient (CI95) | P | Stop-number 9-interval difference |
|---|---|---|---:|---:|
| any calls CI≥1 | 3,249 runs / 282 routes / 106,615 pairs / **48 taxa / 20 States** | +0.00244 (−0.00132 to +0.00619) | **0.202** | +0.04553, P=3.58×10⁻¹⁸ |
| strong CI≥2 | 2,481 runs / 275 routes / 70,385 pairs / **47 taxa** | +0.00150 (−0.00343 to +0.00643) | **0.549** | +0.05386, P=6.65×10⁻¹⁸ |

The rapid decline in community similarity along ordinal station sequence suggests a landscape/temporal pattern, not PEM category discontinuity. This is conditional on each station having at least one audible taxon: missing calls/silent sites are **not** “identical empty communities.” NWI zero means no mapped emergent polygon, *not biological plant absence*. [Workflow #39870416356](https://github.com/zuizui0223/frogcs/actions/runs/39870416356), SUCCESS.

## 3 — Actual physical geographic distance predicts community turnover better than station order alone

Compute **haversine physical site separation** from independently prevalidated physical SiteID latitude/longitude, maintaining **exactly the same** NWI/time-complete station-pair population of macro test 2 and keeping ordinal station index as a nuisance. Geographic distances span 0–37.19 km (median ~4.67 km). Report `log1p(km)` slope and its implied Sørensen dissimilarity change comparing **1 km to 10 km**.

| Sample | Conditional physical log-km β (95% CI) | P | Dissimilarity difference, 1→10 km | Ordinal difference P |
|---|---:|---:|---:|---:|
| any calls | **+0.01572** (+0.00873 to +0.02272) | **1.37×10⁻⁵** | **+2.68 percentage points** | 0.102 |
| strong calls | **+0.02170** (+0.01373 to +0.02967) | **1.77×10⁻⁷** | **+3.70 pp** | 0.265 |

Both deterministic geographic route halves have positive 95% intervals; all 20 State omissions retain the positive sign; the richness-matched and route-equal sensitivity signs stay positive. However, survey sequence also reflects **elapsed clock time**, which had not yet entered this model. [Workflow #39871101668](https://github.com/zuizui0223/frogcs/actions/runs/39871101668), SUCCESS.

## 4 — Most stringent follow-up: condition on *actual* stop start timestamps

Official `Stops.csv StartTime` is an actual `HH:MM` time (the field `TimeOut` is binary, **not** elapsed minutes). Literal `NULL` is excluded, no interpolation. Among the 6,236 NWI-joined runs there are **52,507 / 62,360 (84.20%)** strictly parseable stop start times. The additional fixed source rules require both recorded site times, forward visit time modulo midnight `<=360 minutes`, ≥10 both-active station pairs and ≥2 mapped-cross / ≥2 mapped-same PEM comparisons within that night. Model `log1p(actual elapsed minutes)` **with** `log1p(geographic km)`, ordinal gap, PEM and wetland, community richness and survey-run fixed effect. Compare physically same-sample models, not against the prior larger complete-case sample.

| Acoustic definition | Valid runs / site pairs | Geographic β adjusted for actual clock (CI95) | P geo | P actual-time | Effect 1→10 km | Effect 10→60 min |
|---|---:|---|---:|---:|---:|---:|
| **Any calling** | **2,520 / 81,279** | **+0.01036** (+0.00026 to +0.02047) | **0.0445** | **0.000421** | **+1.77 pp** | **+2.94 pp** |
| Strong only | 1,882 / 52,336 | +0.01272 (−0.00019 to +0.02563) | **0.0535** | 0.0196 | +2.17 pp, nonconfirmatory | +3.29 pp |

Same-sample geographic beta **without** measured time is +0.01819 for any calls and +0.02136 for strong, both clearly positive. The actual-time term absorbs a substantial part of the earlier physical distance association. Physical geography coefficient remains **positive** in both geographic halves and all **19** available leave-one-State-out deletions; route-equal and strict richness-matched any-call CIs are also positive. However geographic-fold CIs themselves now each **include 0**, so the effective replication strength is less than before clock correction.

The `log1p(km)` and `log1p(elapsed minutes)` covariates are **r ≈0.899** correlated (stop-order vs elapsed r≈0.934), making independent coefficient attribution fragile. Even with P=.0445 for any calls, this should be regarded as **exploratory, boundary-level evidence of spatial differentiation net of observed timing**, not a stable mechanistic proof. Strong-only geo P=.0535 and sensitivity CIs include zero. [Workflow #39872141438](https://github.com/zuizui0223/frogcs/actions/runs/39872141438), SUCCESS. Initial run failed because a Python exclusion-counter dictionary was not initialized with zero defaults; corrected and verified on real data before result interpretation. Numerical records are captured with the original precise coefficient values in `exploration/NAAMP_MACRO_REAL_DATA_FOUR_TEST_RECEIPT_2026_10_23.json`.

## Ecological answer and evidence hierarchy

**Supported within the present post-hoc source and model:** Within-night frog *acoustic assemblages* become compositionally more different across the observed spatial gradient. Unlike coarse mapped PEM classes, physical site distance is an appreciable predictor; time elapsed between recorded stop visits is also predictive. This pattern involves nearly **the complete NAAMP taxon pool on eligible route-nights**, not a small hand-picked focal trio, and actual coordinates/timestamps improve interpretation beyond stop numbers.

**Not supported:** Under the tested NWI macroscale first-order proxies, plant-conditioned frog affinity differences do not reproduce the residual pair network, and mapped emergent-wetland boundary presence does not generate a clear step in entire-community Sørensen beta diversity. Those are *failures of these measurements/models*, not a demonstration that actual aquatic vegetation never affects frogs.

**Unresolved identification:** True ecological mechanisms behind spatial turnover, including hydroperiod, wetland geometry, latitude/season, species ranges, observer/detection, within-night phenology, dispersal, competition, call cue interactions and fish/invertebrate predators. Measuring spatial acoustic turnover does **not** prove plants causally alter frog–frog relationships, let alone fish/insect mediated interactions or ≥3-species higher-order causality. Present-day NWI polygons **are not contemporaneous** with the NAAMP 2001–2015 calls. Clock availability also selects fewer runs and 19 instead of 20 States; models properly use one consistent population for timing contrasts, but possible selection bias remains.

This is **four sequential, exploratory user-directed analyses of one original database** with later questions chosen after earlier result readback. It must not be narrated as a prospectively independent four-fold confirmation. The appropriate publication-focused result is a transparent source-backed **acoustic landscape beta-diversity pattern**, not a claimed novel causal multi-species mechanism. A rigorous future expansion would need matched, contemporaneous plant/hydrology and fish/invertebrate measurements. No claim is made that those data were analyzed here.

## Reproducibility / branch

- Scientific original-data scripts:
  - `exploration/run_naamp_macro_niche_network_v0_1.py`
  - `exploration/run_naamp_macro_pem_community_turnover_v0_1.py`
  - `exploration/run_naamp_macro_actual_geographic_distance_v0_1.py`
  - `exploration/run_naamp_macro_actual_clock_vs_geodesic_v0_1.py`
- Four methodological contracts are separate `exploration/NAAMP_MACRO_*_SPEC_2026_10_23.md`.
- Corresponding source-compatible GitHub Actions workflows all **SUCCESS** after a syntax fix and a missing-default-counter fix; original source QA, geographic coordinate binding, sampled populations and scientific inferential boundaries verified.
- Small exact source-derived JSON cross-analysis numerical record: `exploration/NAAMP_MACRO_REAL_DATA_FOUR_TEST_RECEIPT_2026_10_23.json`; full 4 analysis artifacts remain attached to their successful workflows.
- **`main`, JAE RC6 scientific package, SI and submission not modified.**
