# Actual public NAAMP longitudinal feasibility — GitHub CI source-log readout

Date: 2026-10-08. Source: [successful workflow 37728326242](https://github.com/zuizui0223/frogcs/actions/runs/37728326242), job 113151474731. This is the full response-blind NAAMP Runs/Stops+coordinate acquisition and audit, **not** the selected E3 Landsat metadata sample.

The networked workflow downloaded three pinned official NAAMP source tables (Runs, Stops, Coordinates) and confirmed all three SHA256 digests. It never downloaded or opened Counts.csv (frog acoustic responses). USGS source SHA256 pins remain in the repository scripts.

| Log-proven statistic | Value |
|---|---:|
| Eligible ten-stop runs | 7848 |
| Surveyed stop visits | 78480 |
| State:route × SiteID keys | 8223 |
| Routes / states | 807 / 21 |
| Source coordinate rows | 12064 |
| Stop visits joining raw coordinates | 75849 |
| Visits with no raw coordinate match | 2631 |
| Visits passing geometry QC, **not externally verified** | 74861 |
| Other visited stops: geometry review/failure/ambiguous/missing | 3619 |
| Same physical SiteID × survey round, adjacent-year, similar-season potential stop comparisons | 29986 |
| Such stop comparisons with geometry-only pass | 28751 |
| Independently station-verified sites | 0 |
| Actual satellite overlays / climate site series completed | 0 / 0 |

These comparison counts are **not independent statistical replicates**: visits and comparisons share routes, observers, survey rounds, and years. Matching SiteID and geometric plausibility do not establish that a listening stop stayed at one physical wetland across years. Nor is this evidence of breeding success or environmental causation.

### Receipt correction
The original workflow's audit computation **succeeded**, but its `actions/upload-artifact` step silently created no artifact: literal shell-style `${RUNNER_TEMP}` variables in a `with.path` field were not expanded. The workflow was corrected to use the GitHub Actions expression `${{ runner.temp }}` and `if-no-files-found: error`; a later successful run is needed to persist the canonical detailed JSON. This file is a log-grounded interim readout, not that JSON.

### Ecological next step
Use this full 7,848-run observation-opportunity cohort, not the E3 3,811-run selected sample, for new climate/terrestrial source selection. Independently verify physical sites and 30m land-cover pixel alignment, and hold back frog CallingIndex before frozen habitat covariates are constructed.
