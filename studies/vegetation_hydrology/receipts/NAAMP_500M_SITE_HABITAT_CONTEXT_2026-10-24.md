# Observed NLCD habitat setting of historically surveyed NAAMP sites — 2026-10-24

## Input/method (environment only)
Full original-value USGS Annual NLCD **Collection 1.2, 2001–2015** extracted 500-m categorical land-cover fractions for 64,779 actually surveyed physical site-years. For each unique (RouteNumber,SiteID) with passed coordinate QC, calculate each class's **arithmetic mean of available surveyed years** and count whether a threshold is met. **Each of 11,588 physical sites contributes once**, irrespective of number of repeated years. These categories can overlap: no forced single-category assignment. This is an outcome-blind observational selection frame, not a random sample of North American wetlands. Raw frog `Counts.csv` not accessed.

## Results: site-balanced 500-m land cover

| Site-level threshold | Physical sites | Fraction of 11,588 |
|---|---:|---:|
| Woody + emergent wetland vegetation ≥10% | 4,918 | **42.44%** |
| NLCD open water ≥10% | 845 | **7.29%** |
| Woody + emergent wetland + open water ≥10% | 5,449 | **47.02%** |
| Forest ≥50% | 3,195 | 27.57% |
| Agriculture ≥50% | 3,590 | 30.98% |
| Developed ≥30% | 1,240 | 10.70% |

## Implication for feasibility
Many listening stations occur near mapped woody/emergent wetlands without extensive NLCD open-water pixels. Failure to retrieve open-water pixels in a coarser previous-month dataset cannot establish that breeding water was absent. In particular, vegetation and water should be modelled as **distinct components**, with no-observation pixels excluded from dry denominators.

This simple threshold census is descriptive **and NOT evidence that a given vegetation type increases or decreases frog calling**, spawning, presence, reproductive success or response to rainfall. All percentages reflect the observed accepted survey-site sampling frame.
