# NAAMP previous-calendar-month JRC surface-water pixels — 9-event outcome-blind pilot
Date: 2026-10-24

## Verification
- **Succeeded**: [GitHub Actions run 40057069164](https://github.com/zuizui0223/frogcs/actions/runs/40057069164); source/data artifact ID 12545922215.
- Input NAAMP station IDs and survey calendar: exactly checksum-pinned pre-existing **environment-only** GH artifact (run 39960918335). Accepted-coordinate SHA256 `2dbd226a117e5d2c9c10dbd6340fb86a07320b2925aaca3249c8a307a5071afc`, calendar SHA256 `e6fc079ace3642a0ed4330dc05a4b8770fdf89cefabfaca0e490dcb3fd8c45cf`. Zero `Counts.csv` access.
- Source: [EC JRC/Google Global Surface Water MonthlyHistory v1.4](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory), original JEODPP VER5-0 monthly GeoTIFFs. Band values 0=no observation, 1=nonwater, 2=water. Cite Pekel et al. (2016), DOI 10.1038/nature20584.
- For each survey event, the **entire previous calendar month** is selected. This is guaranteed to end before the survey date, but is **not** its previous 30-day interval, daily water state, instantaneous pond depth, or local breeding hydroperiod.
- Sample: nine deterministic, acoustically outcome-blind survey site-events, three states/year in 2001/2008/2015, selected to audit the earlier DSWE STAC metadata coverage. Selection was not stratified by habitat, so not a representative US sampling frame.

## Pixel-level outcome-blind results
- Source original TIFFs successfully opened: **9/9 station-surveys**.
- 500-m geodesic buffers with ≥50% valid monthly imagery: **8/9**; the 2008 Indiana source tile has all 500-m local pixels with value 0 (no observation), **not** dry or nonwater.
- Of the eight valid-coverage buffers, only **one** (Delaware, April 2015) contained any monthly open-water pixel: exactly **one** out of 1,322 observed 500-m pixels (0.000756). The remaining seven had zero observed open-water pixels. All nine used true-original TIFF categorical pixel values, not visualizations.
- Source transfer: **215,301,995 bytes** with on-disk original file SHA256 records in artifact.
- None of these measurements is an estimate of frog reproduction, occupancy, species responses, or the ecological association between local water and frog chorusing.

## Consequence for next mechanism test
The tool can reach month-specific archived JRC water layers without Earth Engine credentials, resolving the DSWE unauthenticated pixel-download blocker at the **source-access** level.

But the early geographic pilot contains too few open-water pixels to show whether this proxy measures event-varying habitat state at relevant frog sites. It would be invalid to infer "little water matters" or that local hydrology is unimportant.

**Next registered feasibility-only test:** draw a second nine-event sample from the already completed C1V2 500-m vegetation panel, one `open_water>=10%`, one `woody+emergent wetland>=25% with open_water<1%`, and one `dry context` station-event for each of years 2001/2008/2015; distinct states within year. The manifest with route/site IDs, dates and coordinates is pinned before querying these JRC water outcomes. Compare only **JRC observation coverage and water pixel detectability**, not a causal/sounding ecology model.

## Integrity/scope
This is an **independent research branch**; RC6 JAE `main` and paper results are unchanged. It is not independent frog-data replication. Monthly satellite products have error and can miss small, shaded, vegetated or short-lived water.
