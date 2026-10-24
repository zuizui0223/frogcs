# Fully preceding-month JRC water × NLCD habitat stratification (9 source-only events)
Date: 2026-10-24

## Verified execution
- [GitHub Actions SUCCESS, run 40057317925](https://github.com/zuizui0223/frogcs/actions/runs/40057317925). Source-only JSON artifact: **12546111256**.
- **9 original JRC monthly TIFFs opened for 9 selected NAAMP historical site-surveys** from 2001, 2008, 2015. **7/9** 500-m buffers contained at least 50% real monthly observations. Source transfer **255,999,401 bytes**.
- Sampling manifest [JRC_PRIOR_MONTH_ENVIRONMENT_STRATIFIED_N9_2026-10-24.csv](../feasibility/JRC_PRIOR_MONTH_ENVIRONMENT_STRATIFIED_N9_2026-10-24.csv), SHA256 **82b2037f88b78e3af3599fce9ff78d385c8f24611cb4bffdb8c77a299eaaa3bf**. The nine source NAAMP calendar events were selected using **500-m USGS Annual NLCD Collection 1.2 land-cover categories only**; `Counts.csv` was never accessed. One station-event in each of 3 predeclared strata for years 2001, 2008, 2015; distinct states.
- JRC VER5-0 band: 0=no observation, 1=non-water, 2=water. The **previous entire calendar month** (not a rolling 30-day window) is used, strictly ending before survey date. Observation coverage and water fraction are calculated separately.

## Environmental pixel results — deliberately nonrepresentative technical sample
| C1V2 land-cover stratum | N | >=50% clear monthly observations | Water-positive among usable |
|---|---:|---:|---:|
| 500m mapped open water >=10% | 3 | 2 | 2 |
| Woody + emergent wetland >=25%, mapped open water <1% | 3 | 3 | 2 |
| Mapped open water <0.5% and woody+emergent wetland <5% | 3 | 2 | 1 |

Illustrative individual results (500m water among **observed** JRC pixels):
- Maine 2001 open-water habitat: **6.79%** previous-month water.
- Minnesota 2008 open-water habitat: **44.72%** previous-month water.
- Missouri 2008 emergent-wetland-rich habitat: **45.36%** previous-month water despite almost zero annual NLCD open-water classification.
- New Jersey 2001 woody wetland context: **0%** observed open-water pixels; no claim the wetland is dry.
- The Maryland 2001 dry-context site had only **26.2%** observed pixels; Massachusetts 2015 open-water-prone site only **7.5%**. Neither can serve as a sufficiently observed 500m water estimate under a 50% threshold.

## Ecological relevance and limits
This demonstrates **source-verified ability to distinguish certain open-water-rich and wetland-vegetation-rich site-months from dry terrestrial contexts** in real historical NAAMP geography. It is *not* evidence that frogs call preferentially in those locations, nor a general water-detection sensitivity estimate. The sample is purposely stratified, N=9, with no species/outcome records accessed.

In particular, a woody/emergent wetland can be flooded without showing as Annual NLCD `open_water`, so time-specific satellite water and stable annual cover are not interchangeable. But JRC monthly imagery is still not water depth, same-night pond state, breeding success, nor a true measure of vegetation inundation under canopy.

The next source-only step is the **full 2001 site × preceding-month geospatial extraction** from 42 shared original tile-month rasters, caching per tile-month rather than downloading per site. A later 15-year coverage audit must precede any frog outcome analysis.
