# NAAMP frog and rainfall data-volume audit — 2026-10-03

## Purpose

Quantify the actual amount of frog and rainfall information behind the current manuscript, distinguishing:

1. the full public NAAMP source release;
2. the filtered survey-run dataset;
3. the matched wetter–drier analysis dataset;
4. the post-hoc ERA5 72-h rainfall subset.

This audit is descriptive only. It does not change any endpoint, filter, model or inferential rule.

## Source

Public USGS data release:

Foreman, T.M., Grant, E.H.C. & Weir, L.A. (2017), *North American Amphibian Monitoring Program (NAAMP) anuran detection data from the eastern and central United States (1994–2015)*, DOI 10.5066/F7G44NG0.

The repository pins the source tables by SHA256 before analysis.

## 1. Full public NAAMP source tables

Direct row counts from the pinned CSV files:

| Table | Data rows | File size |
|---|---:|---:|
| Runs.csv | **21,934** | 2,194,381 bytes |
| Stops.csv | **219,340** | 14,070,232 bytes |
| Counts.csv | **337,848** | 17,214,148 bytes |

The three core tables therefore contain **579,122 data rows** and occupy about **33.48 MB** uncompressed.

Stops.csv contains exactly ten rows per raw run in this release (219,340 / 21,934 = 10), although individual stops can be marked skipped and are filtered accordingly.

### Full Counts.csv CallingIndex distribution

All **337,848** rows in Counts.csv are positive calling records:

- CallingIndex 1: **141,570**
- CallingIndex 2: **92,402**
- CallingIndex 3: **103,876**

The raw Species field contains **68 distinct string tokens**. This exceeds the 58 biological species listed in the source metadata because the raw detection table also contains complexes / alternative taxonomic labels. Do not use 68 as the biological species count.

## 2. Filtered survey-run dataset used to construct the analysis

The current eligibility rules retain unified-protocol years 2001–2015, valid survey date, numeric DaysSinceRain in 0–180, valid route/run identifiers, ten non-skipped stops, at least eight usable stop temperatures, and mean converted temperature between −10 and 45 °C.

This yields **7,848 eligible survey runs**.

Because each retained run has ten stops:

- eligible survey nights: **7,848**
- eligible stop visits: **78,480**

Within those eligible runs:

- positive species × stop calling records: **115,638**
- CI1: **48,419**
- CI2: **30,834**
- CI3: **36,385**
- distinct positive taxonomic tokens: **57**
- taxon × run combinations with at least one positive call: **29,625**
- stop × run combinations with at least one positive call: **59,434**
- runs with at least one positive call: **7,703**
- completely call-silent eligible runs: **145**

Thus about **75.7%** of eligible stop visits contained at least one positive frog record.

These 115,638 rows are observed positives. Analyses that represent a species × stop matrix additionally encode non-detections as zeros under the documented acoustic-state rules.

## 3. Main matched wetter–drier dataset

Adjacent observed years within State × RouteNumber × RunNumber are paired after excluding equal DaysSinceRain.

This produces:

- matched wetter–drier comparisons: **4,236**
- routes: **585**
- states: **21**
- taxa in the paired concentration decomposition: **53**

Because an eligible run can serve in two adjacent-year comparisons, 4,236 pairs do not equal 8,472 independent survey nights.

The 4,236 pairs are built from:

- **6,075 unique survey runs**
- **8,472 run appearances** across the two sides of all pairs
- **60,750 unique stop visits** across those unique runs
- **84,720 stop appearances** when repeated use of a run in adjacent pairs is counted

Across the **6,075 unique runs** contributing to at least one pair:

- positive frog calling records: **88,743**
- CI1: **37,017**
- CI2: **23,521**
- CI3: **28,205**
- distinct paired-analysis taxa: **53**
- positive taxon × run combinations: **22,576**
- active stop × run combinations: **45,991**

This is the most useful scale statement for the main paper:

> **The 4,236 wetter–drier comparisons are built from 6,075 unique survey nights, 60,750 fixed-stop visits and 88,743 positive species × stop calling records spanning 53 taxa.**

## 4. Rainfall information

### A. NAAMP DaysSinceRain — primary exposure

The primary rain variable is the NAAMP run-level DaysSinceRain.

Because valid DaysSinceRain is part of the eligibility filter:

- run-level DaysSinceRain observations in the eligible dataset: **7,848**
- unique run-level DaysSinceRain observations represented in the 4,236 matched comparisons: **6,075**
- wetter/drier run appearances across all pairs: **8,472**
- pair-level rain-recency contrasts: **4,236**

This is not rainfall amount. It is the reported number of days since the most recent rain event and is transformed as log(1 + DaysSinceRain_dry) − log(1 + DaysSinceRain_wet).

### B. ERA5 72-h precipitation — post-hoc measured rainfall amount

The post-hoc common-environment analysis links ERA5 hourly total precipitation (tp) to survey runs.

For each weather-eligible run:
- the survey midpoint is converted to UTC;
- the nearest ERA5 grid cell is selected;
- the **72 hourly precipitation values ending at the floored survey-midpoint hour** are extracted;
- hourly metres of precipitation are converted to mm and summed to rain72_mm.

Coverage:

- run-level 72-h rainfall sums: **7,559**
- underlying hourly ERA5 precipitation values sampled: **544,248** (= 7,559 × 72)
- weather-eligible principal-history pairs: **2,835**
- routes: **428**
- states: **20**

Coverage relative to the eligible NAAMP runs:
- 7,559 / 7,848 = **96.3%**

Coverage relative to the 2,916 principal-history pairs:
- 2,835 / 2,916 = **97.2%**

The ERA5 amount analysis is therefore nearly complete for the principal spatial subset, but it is explicitly post-hoc and does not replace the primary DaysSinceRain exposure.

## 5. Why the data structure matters

This is not primarily a “large rainfall dataset”.

The environmental side is comparatively low-dimensional:
- one primary DaysSinceRain value per survey night;
- several survey-night covariates;
- one post-hoc 72-h rainfall sum per weather-linked night, derived from 72 hourly ERA5 values.

The frog side is the high-dimensional component:
- repeated survey nights;
- ten fixed locations per run;
- multiple taxa;
- ordinal chorus state at each positive taxon × stop observation;
- repeated physical SiteIDs through years.

The distinctive information is therefore the **repeated species × place × night structure**, not simply the number of rainfall observations.

A concise conceptual description is:

> **A few night-level environmental variables are linked to tens of thousands of repeated fixed-stop observations and nearly ninety thousand positive frog-call records in the matched analysis.**

That structure is what makes it possible to ask whether favourable-night reproductive activity is organized independently by wetland, uniformly across a route, or selectively across recurrent taxon-specific locations.

## 6. Numbers appropriate for reader-facing use

### Abstract
Keep the current 4,236 matched comparisons, 53 taxa, 585 ten-stop routes, 21 states and 15 years. Do not add raw row counts to the Abstract.

### Methods
Useful compact scale sentence:

> The 4,236 matched comparisons were built from 6,075 unique survey runs, representing 60,750 fixed-stop visits and 88,743 positive species × stop calling records across the 53 taxa retained in the paired analysis.

### Talks / overview
Useful fuller scale description:

> The filtered NAAMP dataset contains 7,848 standardized survey nights and 78,480 fixed-stop visits. The matched analysis uses 6,075 unique nights and 88,743 positive frog-call records; the post-hoc 72-h rainfall analysis links 7,559 nights to 544,248 hourly ERA5 precipitation values.

## Boundaries

- Counts.csv contains positive call detections, not explicit zero rows.
- Non-detection zeros in analysis matrices are constructed under the documented stop/run eligibility rules.
- 68 raw Species-string tokens are not 68 biological species.
- 57 positive taxonomic tokens occur across all 7,848 eligible runs, whereas the matched concentration analysis contains 53 taxa.
- Pair-level run appearances are not independent survey nights because runs can participate in adjacent-year pairs.
- ERA5 72-h precipitation is a gridded atmospheric measure, not direct local hydroperiod or water-level measurement.
