# Verified full Annual NLCD C1V2 panel: 2001–2015 (2026-10-23)

## State of work
**DONE: source-verified, outcome-blind, 15-year habitat classification panel.** 
It is not an analysis of frog calling and does not amend main, RC6, or the Journal of Animal Ecology paper.

### Executed evidence
- [2001 extraction run 39960285085](https://github.com/zuizui0223/frogcs/actions/runs/39960285085) — SUCCESS, **2,901 site-year keys, 5,802 100-/500-m buffers**.
- [2002–2015 matrix run 39960918335](https://github.com/zuizui0223/frogcs/actions/runs/39960918335) — **15/15 successful jobs** (1 shared NAAMP source/coordinate/calendar preparation + 14 annual jobs).
- Annual products: official **Annual NLCD Collection 1.2, June 2026**, 30-m native categorical land-cover rasters; original USGS ScienceBase [item 697b9279b66b0197c3043cc3](https://www.sciencebase.gov/catalog/item/697b9279b66b0197c3043cc3), DOI 10.5066/P94UXNTS. MRLC public original-year ZIP URLs available via byte ranges; total original ZIP sizes **20,609,040,760 bytes**. Each annual ZIP + extracted TIFF recorded with SHA256 in the annual artifacts and full-panel local manifest.
- Survey/coordinate sources are USGS checksum-pinned `Runs.csv`, `Stops.csv`, and physical coordinate table. `Counts.csv` was **NEVER downloaded/read**.
- Matched physical SiteID × year calendar covers **64,779 unique site-year keys** among **11,588 physical sites, 1,145 routes, 25 states** from 2001–2015. All received annual files exactly match that outcome-blind calendar without duplicates.
- **129,558 buffer records** (64,779 × 2 radii). All pass >=80% valid categorical pixel coverage (in fact observed 100% across the full panel). Annual 30-m TIFF data are extracted then discarded; only small environmental tables and audit receipts are retained.

### Empirical descriptive land-cover findings (NOT frog selection)
Mean fractions calculated **site balanced** (each site's observation years averaged before weighting physical sites equally):

| Class | 100 m | 500 m | mean 100−500 | route-cluster 95% bootstrap interval |
|---|---:|---:|---:|---:|
| Developed | 35.182% | 15.585% | +19.597 percentage points | +19.047 to +20.135 pp |
| Forest | 21.324% | 31.442% | −10.119 pp | −10.726 to −9.467 pp |
| Agriculture | 23.678% | 32.342% | −8.664 pp | −9.216 to −8.107 pp |
| Woody wetland | 12.531% | 12.298% | +0.233 pp | −0.071 to +0.554 pp |
| Emergent wetland | 4.064% | 3.596% | +0.468 pp | +0.258 to +0.695 pp |
| Open water | 1.554% | 2.350% | −0.796 pp | −0.960 to −0.637 pp |

The 100-m roadside-focused stations are systematically more developed and less forested than their surrounding 500-m context. This is **survey setting / spatial-scale bias**, not an inference that frogs prefer developed land.

### Within-site annual stability
Among **7,010 physical sites spanning >=5 years** (median temporal span 9 years):
- 500-m developed cover: median absolute change between first and last surveyed years 0.232 percentage points; only **1.284%** of sites show an absolute >=10 percentage point difference.
- 500-m forest: median abs change 0.231 pp; **4.679%** with >=10 pp change.
- Woody and emergent wetland 500m fractions have median absolute change **zero**.

Therefore NLCD landscape cover is predominantly stable at these spatial buffers on observed time scales, while the unresolved mechanism requires **event-specific local hydrological state** (water level, inundation, temporary wet/dry habitat), not just static wetland class.

### Inference boundaries
- **No frog response or CallingIndex analysed. No causal environmental effect or independent species response replication claimed.**
- 25-state environmental calendar does not equal RC6's 21-state 4,236 matched-pair data. The calculation describes only sites with QC-approved coordinates and actual survey years, not random wetland habitat.
- 30-m annual cover ≠ canopy height, actual calling microhabitat, vegetated shallow water, water depth, or survey-night inundation. Same-year annual imagery is not guaranteed strictly before survey dates.
- Site observations across years/routes are dependent; site-balanced differences and **route-level bootstrap** were used for spatial-scale descriptive comparisons.

### Follow-on gate
1. Complete strictly-prior Landsat C2 DSWE surface-water data availability and QC audit for these site-survey dates.
2. Define environmental predictors, missing-data gates, pre-event timing, spatial blocking and comparison of static habitat versus transient wetland state before reading frog calls.
3. Any later outcome analysis is a **new independently documented analysis**, not an update to the frozen frogcs RC6 science. NAAMP reuse by itself is not independent confirmation.

This repository receipt records the completed pipeline; full annual per-year tables remain available as GitHub Actions artifacts (retention-limited). The consolidated 15-year derived CSV, QC source manifest and rebuild script were also packaged in the conversation as a separate downloadable research artifact.
