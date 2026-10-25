# Post-readback precipitation × global GloBI-stage GBIF co-reporting screen (2010–2024)

Date 2026-10-25. This is an *explicitly exploratory follow-up* after reading the species-stage spatial co-report and phase-shift screens, **not** RC6 NAAMP 72-hour rainfall replication nor new evidence of actual predation.

## Input
- GloBI source-fixed 2026-09-10 full 24.45M records, MD5 `8212776b7ba0c4fa8de26a00b5ce8595`; the **18** full GloBI nonself and unambiguously staged predator→prey candidate patterns with both species-stage observed in experimental GBIF Anura/Odonata source.
- GBIF anonymous experimental 2026-08 taxon-partition, 1° × species × stage × calendar year × month, original workflow 40190152042. Some species are from non-native populations; absent/undocumented GBIF stage = unobserved, not necessarily biologically absent.
- Monthly precipitation from [WorldClim 2.1 CRU-TS4.09 downscaled historical archives](https://www.worldclim.org/data/monthlywth.html), 2010–2024, **1° GBIF cell-centre samples** produced by verified workflow 40194019270 (two source ZIP SHA256 pinned). This is monthly rainfall, **not** local NAAMP antecedent hours or same pond hydroperiod.

## Main descriptive estimand
For each predator×prey stage association (no conspecifics), and in each **1° grid-year** where each species-stage was observed in **at least one month**:
- `C`: months where both GBIF species-stages are co-reported, with precipitation value at the grid-year-month.
- `U`: months where exactly one of the two species-stages is reported, also with on-land precipitation value.
- Keep a grid-year only if ≥1 C month **and** ≥1 U month with valid rain.
- Calculate `D_gridyear = mean(precipitation in C) − mean(precipitation in U)` in mm/month; each *unique* grid-year contributes once to pair average, not weighted by number of GBIF sightings.
- Also compare `P(C | months with either species-stage reported)` above vs below median available month precipitation *within each grid-year*, reporting sample-size not independent binomial p-value.
- Repeat both thresholds: ≥1 and ≥5 records per species-stage-grid-month; keep the same GloBI link set in both.
- Do **not** interpret as increased predator behaviour or egg survival; this comparison is strongly confounded by the shared seasonal availability, phenology, survey effort, plant/wetland state and the coarse 1° cell.
- If <5 informative grid-years for an edge, output `INSUFFICIENT_GRIDS` and do not report an effect direction.
- Keep distinct bird/odonate/frog guilds and Quick Pond vs iNaturalist index links separate.
- Report median and mean D across informative grid-years per edge and whether positive/negative, plus the share of candidate edges with D positive. No global p-values or FDR claims from multiple nonrepresentative edges.

## QA and negative controls
- Climate values must agree exactly for every repeated `latcell,loncell,year,month` across species. Contradiction causes error.
- Not-on-land / missing precipitation months are missing and never treated as zero rain. Exclude out-of-source 2025/2026 GBIF months without extrapolation. No future rainfall lookahead.
- Source observation rows can be repeated source plots; grid-year treated as repeated environmental exposure, not independent animals. Report number of informative independent grid-years and distinct cell locations.
- Any apparent positive monthly-rain contrast is a **phenology/reporting hypothesis**, not evidence of trophic specialization; previous same-guild prey controls gave inconclusive/weak specificity.
- Final causal hydrology/vegetation tests require spatial wetland geometries, true emergent/submerged plant stem structure, predator and prey abundance/stage, repeated frog acoustic activity and specific-rain-event water level.
