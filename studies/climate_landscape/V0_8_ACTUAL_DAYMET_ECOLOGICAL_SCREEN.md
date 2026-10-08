# v0.8 — Actual measured Daymet climate histories at NAAMP monitored routes

**Data retrieved and verified 2026-10-08. Independent source-only study; does not amend RC6/JAE.**

## Provenance and sample

Official Daymet single-pixel API, NAAMP Runs/Stops/Coordinates source SHA256-pinned. GitHub Actions [37736273058](https://github.com/zuizui0223/frogcs/actions/runs/37736273058), artifact 11532307596. The original complete-source status is `complete_source_screening`. The route screening population had 180 longitudinal geometry-eligible routes across 16 states; 12 routes in 12 states were selected with a fixed SHA256 hash, at most one per state, **without inspecting frog calling**. All 12 source receipts contain 35 complete Daymet years (1981–2015): **153,300 real daily climate records**. The route-median coordinates are NOT externally verified historical physical stations.

See machine-readable [ACTUAL_DAYMET_ROUTE_TRENDS_V0_8.json](ACTUAL_DAYMET_ROUTE_TRENDS_V0_8.json) for source hashes, climate values and no-outcome evidence markers.

## Full historical annual-temperature and precipitation slopes (Theil–Sen)

Units: °C per decade and millimetres per decade respectively, for 1981–2015. Slopes are **descriptive historical summaries**, not predictors for past observations.

| State | T slope °C/decade | P slope mm/decade |
|---|---:|---:|
| Delaware | 0.278 | 53.4 |
| Indiana | 0.139 | 19.6 |
| Kentucky | 0.116 | 53.9 |
| Maine | 0.272 | 91.8 |
| Maryland | 0.193 | 45.9 |
| Mississippi | 0.128 | 10.0 |
| NewJersey | 0.255 | -3.6 |
| NorthCarolina | 0.153 | -17.9 |
| Pennsylvania | 0.156 | 70.7 |
| Vermont | 0.103 | 42.6 |
| Virginia | -0.008 | 23.8 |
| WestVirginia | -0.026 | 48.5 |

The across-route **descriptive medians** are:
- temperature: **+0.146 °C per decade**, positive in 10/12;
- precipitation: **+44.3 mm per decade**, positive in 10/12.

Past-only prior-5-year climate state relative to 1981–2000 (1996–2000 as available for 2001 surveys vs 2010–2014 as available for 2015 surveys):
- median **+0.255 °C** difference in recent-five-year temperature anomaly, with 10/12 positive;
- median **+0.014** difference in annual-precipitation ratio, with 8/12 positive.

## Biological hypothesis revised by actual climate evidence

The initial story of ubiquitous *warming and drying* is **not supported as a description of these 12 monitored route-scale annual climate histories**: rainfall trends are positive at most selected routes. Warming and annual rainfall increase can co-occur; breeding wetland water availability can still depend on seasonal rainfall timing, evapotranspiration, runoff, hydroperiod, vegetation and land use, none established by these annual Daymet indices. Do not call a higher annual precipitation ratio an observed longer wetland hydroperiod.

For the next species-response step, compare **actual historical antecedent thermal state and actual precipitation state separately**, with short-term weather and season controls. Evaluate taxon × route strong chorus *magnitude* independently from fixed-K among-stop *configuration*. The latter needs validated historical site identities and terrestrial land-cover changes; no site-level 30 m overlay has been completed.

## External validity and evidence boundary

This 12-route pilot lies in eastern/central U.S. states and was deliberately selected at most one route per state from a long-term surveyed/geometry-eligible subpopulation, **not** a random nationwide sample. Do not report p-values as if 12 routes represent all NAAMP sites. Climate is observational and these slopes do not attribute changes to anthropogenic forcing or establish a frog reproductive outcome. The derived data above contain **no CallingIndex, frog count, larval success or species activity measurements**.

## Next execution

A standalone [Daymet-to-survey year workflow](../../.github/workflows/climate_landscape_daymet_survey_join.yml) reuses the successful frozen climate artifact rather than fetching the 153,300 Daymet records again, downloads original pinned NAAMP Runs/Stops (never Counts.csv), and uses `scripts/build_daymet_survey_exposure_panel.py` to yield survey-date-keyed prior-five-year route climatology. Its success and route-year exposure counts must be confirmed from its own uploaded receipt before proceeding to frog outcomes.
