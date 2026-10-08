# Landsat interannual metadata feasibility — real NAAMP subset (2026-10-08)

**Independent climate × terrestrial landscape × frog study. Response-blind empirical source-readout; NOT a biological effect result.** Existing `frogcs` RC6/JAE science lock remains unchanged.

## Primary source and its exact scope

Retrieved GitHub Actions artifact `e3-ndmi-metadata-coverage-v01` (`11522991495`), created by the existing E3 Landsat-STAC metadata coverage workflow ([source run 37711481855](https://github.com/zuizui0223/frogcs/actions/runs/37711481855)). The archived JSON's SHA256 is `f375494c3ee4897d45729866f771521753a1a9ed070908ce4002d1db3ab599ce`.

This outcome-blind metadata covers **3,811 NAAMP survey RunIDs across 395 route identities**, from the previously selected E3 subset (not the full 7,848-run NAAMP historical universe). All 3,811 records have at least one Landsat candidate scene in the **0–32 days before** the visit that covers the route's ten stations according to the source footprint metadata. It reports no pixel QA, NDMI, climate-trend or frog outcome estimates.

Of 395 route identities, 389 had survey observations in at least two different years; 195 had a calendar-year span of at least five years, and 101 at least eight years. These are route-level temporal opportunities, **not validated repeated physical wetland locations**.

## Actual longitudinal scene availability

For comparability, original NAAMP survey dates were matched *within route* across years if seasonal date-of-year differed by ≤21 days (with a no-leap calendar). For adjacent and exact-five-year comparisons, multiple surveys were matched closest-in-season one-to-one **within that pair of years**. For the long-gap result, each route contributed only one maximally separated ≥5-year pair (ties by seasonal distance, then RunID). A separate early/late test chose one 2001–05 vs 2011–15 pair per eligible route. Multiple adjacent-year pairs can share one NAAMP RunID across years; they are **not independent biological observations**.

| Temporal contrast, ±21 days | Candidate run pairs | Routes | Same Landsat sensor family and season-matched scene candidates |
|---|---:|---:|---:|
| Adjacent years | 1,817 | 337 | 1,817 |
| Exactly five years apart | 571 | 146 | 571 |
| ≥5 years, one pair per route | 179 | 179 | 177 |
| Early (2001–05) to late (2011–15), one pair per route | 91 | 91 | 89 |

Strict ±7-day survey-and-image-acquisition seasonal sensitivity still yielded **1,154 adjacent-year pairs (298 routes), 164 ≥5-year route pairs, and 81 early-to-late route pairs**. Matching at ±14 days yielded 1,587 adjacent pairs (323 routes), 174 ≥5-year route pairs, and 87 early-to-late route pairs. All counts are **metadata coverage only**: no guarantee of a clear usable scene, equal pixel support, stable coordinates or sensor harmonization.

## Crucial difference between satellite metadata and pixels

A separately obtained deterministic, **diagnostic-only** E3 pixel-QA pilot ([run 37715319743](https://github.com/zuizui0223/frogcs/actions/runs/37715319743)) tested 18 survey runs using *only the first candidate* image: 12 raster QA checks were evaluable, 6 encountered retrieval errors, and just **3 of the 18** achieved the frozen ≥70% valid-pixel threshold simultaneously at all ten route stops for that first scene. The pilot is tiny and not a population-level success-rate estimate; fallback scenes could alter success rates. It demonstrates why 100% matching of scene timestamps should **not** be translated into 100% real Landsat land-condition coverage.

## Ecological hypothesis worth the next independent test

> Do formerly recurrent frog acoustic sites persist when terrestrial land cover and hydrologic conditions deteriorate, or do they reallocate toward landscape buffers, and is this response lagged relative to persistent climatic warming/drying?

Retain three distinct measurements: **event-scale calling/chorus state** (not breeding success), **interannual ground/satellite habitat change** (not equivalent to water depth), and **long-term meteorological background** (not in itself anthropogenic attribution). Analyse frog outcome only after site identities and remotely-sensed exposures are independently checked.

Competing predictions (must be frozen before response read-back):
1. **Fast cue only:** weather and long-established species × site use explain the changes in acoustic site use; land-cover changes add no transferable effect.
2. **Land-cover buffering:** loss of forest cover, increased developed land, or loss of mapped wetland setting predict less recurrent strong calling under comparable short-term weather.
3. **Delayed response / ecological legacy:** sites remain acoustically recurrent for several seasons after negative land-cover/hydroclimate change, then decline; apparent habitat–calling mismatch is tested via prior changes (not simultaneous correlations). Lagged effects must be contrasted with survey date shifts and observer turnover.

## Inference and no-retuning boundary

Existing JRC visible-water and MODIS DSWEmod hydroperiod tests did **not** close the higher-order within-taxon concentration residual. Their negative outcomes are retained, not reparameterized. A predeclared 3-month wetness increment improved out-of-route prediction of strong chorus only, without saving the full hydrology model. This project must **not** mine new water-radii or frog taxa to reverse those results.

Next gates are: independently verify physical SiteID coordinates and relocations; acquire cloud/QA-masked Landsat scenes at comparable years and dates or official annual NLCD v1.2; quantify valid scene-pair coverage and sensor-family harmonization; extract Daymet/PRISM antecedent climate without post-survey look-ahead; only then estimate out-of-block, species-level acoustic-site changes with repeated-route uncertainty and explicit null results.

**Current decision:** longitudinal metadata feasibility is supported. The climate-change and frog-site-reorganization *biological* hypotheses remain entirely untested in this new lane.