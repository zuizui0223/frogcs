# Full 2001 historical NAAMP previous-month surface-water pixel audit — six shards reconciled
Date: 2026-10-24

## Scope and verified inputs
- JRC Global Surface Water MonthlyHistory `VER5-0`, original 30m TIFFs. Each event uses the **entire calendar month before the original NAAMP survey date**, never the same/future calendar month. 0 = **no satellite observation**, 1 = observed non-water, 2 = observed water; neither absent JRC water nor satellite no-observation proves no breeding pond.
- NAAMP fields: checksum-pinned `Runs.csv`, `Stops.csv`, accepted physical `SiteID` coordinates only. No frog `Counts.csv`, CallingIndex, abundance, colonisation, occupancy or reproductive success analysis.
- Six deterministic SHA256(URL)-assigned source shards, [GitHub Actions run 40059404586](https://github.com/zuizui0223/frogcs/actions/runs/40059404586): **6/6 SUCCESS**; exact original source TIFF SHA256 per image in source receipt.
- Independently verified in the working container: six archive internal CSV SHA256s all match their receipts; 42 distinct original tile-month source URLs, zero missing/unavailable; exactly **7,511** unique site×previous-month keys matched to the original 2001 survey calendar, no duplicate/extra/missing keys, and the source tile hash for each station-month matched its expected source URL. All category counts/fractions and missing-observation semantics verified.
- Survey calendar context for 2001: **8,394 station visits**, **2,901 unique physical sites**, **7,511 unique physical site×previous-month keys**.

## 500-m water quality and observed contrasts — full 2001 station-month frame
- **5,639 / 7,511 (75.08%)** have ≥50% original month-level Landsat observation coverage in the 500-m buffer; **5,321 / 7,511 (70.84%)** meet ≥80%; 1,872 (<50%) are treated as **missing/insufficient**, not dry.
- **1,570 / 5,639 (27.84%)** of the ≥50%-coverage station-months have at least one pixel classified as JRC observed open water. This is a water-detection frequency in a repeated station/month dataset, **not frog site occupancy or waterbody coverage truth**.
- At the *route×previous-month* environmental grouping level, 750 groupings have ≥8 nominal station records and **563** have ≥8 nominal and ≥6 usable sites; among these 563, **232** show ≥5 percentage-point within-route difference in JRC water fraction, **168** show ≥10pp difference. Median observed within-group water range 2.63pp. Groupings are not necessarily single NAAMP route-night runs, and multiple months/routes are correlated.

## Outcome-blind land-cover × JRC availability
The original-year USGS Annual NLCD C1V2 500-m fraction is joined to each physical site-month (2001). Classes defined from NLCD before looking at acoustic data.

| NLCD 500-m context | Site-months | ≥50% JRC clear | Water pixel among ≥50% |
|---|---:|---:|---:|
| Open water ≥10% | 605 | 442 (73.1%) | 440 (99.5%) |
| Woody+emergent wetland ≥25%, open water <1% | 1,238 | 885 (71.5%) | 104 (11.8%) |
| Wetland <5%, open water <0.5% | 2,528 | 1,983 (78.4%) | 114 (5.7%) |
| Other | 3,140 | 2,329 (74.2%) | 912 (39.2%) |

This difference is about **satellite data semantics and mapped land cover**; it does not demonstrate frog habitat selection or hydrologic causation. JRC may miss under-canopy/shallow/temporary water.

## Strong calendar-month missingness — MUST remain visible
Usable (≥50% observed) sample counts:
- December 2000 preceding month: **57 / 150 (38.0%)**
- January 2001: **20 / 110 (18.2%)**
- February 2001: **255 / 448 (56.9%)**
- March 2001: **784 / 1,856 (42.2%)**
- April 2001: **1,464 / 1,795 (81.6%)**
- May 2001: **1,989 / 2,020 (98.5%)**
- June 2001: **1,060 / 1,122 (94.5%)**
- July 2001: **10 / 10 (100%)**

This strong calendar-month sampling dependence means analyses conditioned only on having satellite water pixels could select later-season site-months. All coverages must be stratified by state, year, season, habitat and route before any acoustic outcome is examined.

## Audit tools / reproducibility
- GitHub `scripts/run_jrc_prior_month_shard.py` and `scripts/merge_jrc_shards.py`; source-only test workflows and missing-pixel checks.
- Independently rederived exact site-month coverage and joined the JRC pixel data to the original-year NLCD panel in a working-container analysis. Full derived joined CSV, per-state/per-month/per-habitat summaries, route×month contrast table, six artifact manifests and independent QA source code are distributed as a separate ZIP.
- The original monolithic [2001 run 40057552583](https://github.com/zuizui0223/frogcs/actions/runs/40057552583) is not used as authority; the 6 successful shards are independently validated.

## Decision and bounds
Year **2001 environmental coverage is complete at the JRC monthly-source level**, but this is **not complete hydrological characterization**: satellite missingness depends heavily on season, only observable surface water is classified, and temporal resolution is monthly. The full 2002–2015 source-only design may be executed using bounded deterministic shards, provided that full annual product completeness and absent source failures are checked. The frozen RC6 JAE manuscript remains unmodified. A new ecological outcome protocol must be frozen before opening frog response data, with route/time blocked evaluation and recognition that NAAMP reuse is not independent external validation.

## Monolithic execution failure, diagnosed and repaired
The original single-job 2001 runner [40057552583](https://github.com/zuizui0223/frogcs/actions/runs/40057552583) was **cancelled at the configured 35-minute job limit** after processing only **30 of 42** monthly source tiles. The job wrote no complete output artifact: the original implementation buffered results until all tiles finished. Its logs showed approximately 72 seconds per source tile, making the sequential budget insufficient.

**Repair and retest:** split the same original source URL set by a stable SHA256-based six-way partition; each shard independently downloaded its assigned tiles, audited pixel no-observation categories, and uploaded partial provenance. [All 6 shard jobs succeeded](https://github.com/zuizui0223/frogcs/actions/runs/40059404586), covering **42/42** source tile-month URLs and **7,511/7,511** survey site-month keys. [A separate canonical merger passed](https://github.com/zuizui0223/frogcs/actions/runs/40059724239), and its original pixel counts/flags/hashes match a second independently derived local audit for all 7,511 records.

Thus the recovered result is **not** a partial or substituted source. The original cancelled run remains historical failure provenance, not an alternative scientific estimate.
