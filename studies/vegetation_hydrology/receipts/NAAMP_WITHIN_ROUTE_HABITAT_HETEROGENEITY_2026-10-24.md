# Route-balanced habitat contrast in real NAAMP vegetation sampling frame (2026-10-24)

## Status
**New empirical environmental-only analysis complete.** No `Counts.csv`, CallingIndex, or other frog acoustic outcomes were accessed. Not independent replication, not frog habitat preference, and not a revision of the frozen RC6 Journal of Animal Ecology candidate.

Source: official **USGS Annual NLCD Collection 1.2**, 2001–2015; environment-only source CSV SHA256 `137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a`, 129,558 100/500m rows, 64,779 physical site-year keys, 11,588 unique physical sites.

## Primary descriptive unit: ROUTE, not route-year
Within each physical RouteNumber × SiteID, calculate the arithmetic mean of its 500-m annual land-cover class fractions over actually surveyed years. Each site then contributes **once**, and each route contributes **once**. The within-route range is the maximum minus the minimum site fraction. Retain routes with **≥8** fixed-site records, yielding **1,140 independent route identifiers** (not assuming biological independence across neighbouring routes).

| Class | Routes with ≥10 percentage-point site range | ≥25 percentage-point range | Median range (pp) |
|---|---:|---:|---:|
| Woody + emergent wetland vegetation | **840/1,140 (73.7%)** | 619 (54.3%) | **28.05** |
| Forest | 1,013 (88.9%) | 870 (76.3%) | 43.45 |
| Developed | 789 (69.2%) | 366 (32.1%) | 14.62 |
| Open water | 364 (31.9%) | 173 (15.2%) | 3.57 |
| Agriculture | 956 (83.9%) | 833 (73.1%) | 45.00 |

Among 11,588 unique sites, **3,461 (29.9%)** had mean vegetation-wetland fraction ≥10% but open-water land-cover fraction <1%. This shows that broad satellite **wetland vegetation** and NLCD **open-water** classifications have different coverage; it does not prove standing water below vegetation.

Secondary repeat-year description (not independent replication): 6,472 route×year cells with ≥8 sites; wetland vegetation site range ≥10pp in 4,901 (75.7%) and ≥25pp in 3,592 (55.5%). Neither these repeated route-years nor the 15-year NLCD pixel counts should be interpreted as independent ecological replicates.

## Why this matters for the next ecology test
The environmental predictor has substantial *within-route site-level support*. Thus a future **within species × route × matched survey** comparison could ask whether persistent chorusing locations correlate with measured habitat differences after response magnitude and rainfall/season are held fixed. This does NOT yet show the relation or identify mechanism: the observed frog data are deliberately sealed.

The spatial selection of road-acoustic stations can bias land cover, and 500-m annual classes are not direct wetland depth, understory structure, exact survey-day water, or verified spawning substrate. Temporally constant habitat may explain historical site propensities but cannot alone identify survey-to-survey state switching.

## Reproducibility
`studies/vegetation_hydrology/scripts/audit_route_habitat_contrast.py` (strict input checksum, physical site means, route-balanced contrasts, duplicate/field validation). Companion synthetic tests: `tests/test_route_habitat_contrast.py`. Numerical source table and report also produced in the conversation artifact `frogcs_route_habitat_qc_2026-10-24`.

No changes to `main`, paper/figures, prior RC6 inference, or the WFTS-not-pursued decision.

## Overlap and within-route covariate collinearity

Of the 1,140 routes with ≥8 sites, **564 (49.5%)** have ≥10-percentage-point site contrasts in **both wetland vegetation and developed cover**. After averaging annual cover within each physical site and subtracting the route-specific mean from each 500-m site fraction, the *descriptive* within-route Pearson correlations are:

- wetland vegetation vs developed cover: **−0.198**;
- wetland vegetation vs forest: **−0.269**;
- wetland vegetation vs agriculture: **−0.348**;
- wetland vegetation vs open water: **−0.055**;
- forest vs agriculture: **−0.512**.

These are simple environment-only correlations across nested physical sites, **not effect sizes or uncertainty estimates for frog habitat use**. Nonzero composition dependence remains, and any later ecological model must guard against collinearity and road-related detection bias. The result supports including wetland vegetation and open water as **distinct prespecified axes**, rather than assuming they are interchangeable. Route means were removed only to describe *within-route* contrast availability, not to infer habitat causality.
