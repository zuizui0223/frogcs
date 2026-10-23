# 2001 real-NAAMP vegetation extraction: five-site QA pilot (2026-10-23)

## Execution and data provenance
- **SUCCESS**: [GH Actions run 39935061682](https://github.com/zuizui0223/frogcs/actions/runs/39935061682), artifact [12493706103](https://github.com/zuizui0223/frogcs/actions/runs/39935061682/artifacts/12493706103).
- Source: validated original **Annual NLCD C1V1 2001 land-cover categorical TIFF** (USGS STAC/OSN); this is **Collection 1.1, NOT final Collection 1.2**. Verified HTTP 206 original TIFF byte ranges; no 1.37 GB mosaic download.
- Input survey/site universe: hash-pinned original NAAMP `Runs.csv`, `Stops.csv`, `NAAMP_SiteCoordinates.csv`. Accepted physical-site coordinates + 2001 calendar. **`Counts.csv` not fetched or loaded.**
- Selection independent of frog calling: for each of the first five alphabetically ordered states with eligible 2001 visits, select the RouteNumber×SiteID with the lowest SHA256 string value. The sample is illustrative, not stratified or representative.
- Output: **5 distinct real sampled sites in 5 states, 10 buffers** (100 and 500 metres), **all 10 buffers ≥80% valid categorical pixel coverage**, in fact 100% under the tool's valid-pixel calculation.

## Actual source pixel-derived 500-m buffer percentages, rounded
| State | Agriculture | Forest | Woody wetland | Developed | Open water |
|---|---:|---:|---:|---:|---:|
| Delaware | 75.3% | 0.8% | 11.1% | 12.5% | 0.0% |
| Indiana | 92.9% | 1.2% | 0.0% | 6.0% | 0.0% |
| Kentucky | 84.5% | 6.3% | 0.0% | 9.3% | 0.0% |
| Louisiana | 13.8% | 18.5% | 11.5% | 48.2% | 0.2% |
| Maine | 4.4% | 69.2% | 16.0% | 7.4% | 0.0% |

Omitted classes (e.g. shrub) make these **non-100% sum rows**. The complete category fractions, 100-m results and exact site keys are in the artifact JSON `qc/real_naamp_nlcd_c1v1_pilot.json`.

## Interpretation boundary
This validates **land-cover heterogeneity can be measured with source-native categorical pixels at actual historical listening stations**. It does NOT show whether any class predicts calling, historical strong-chorus site recurrence, local hydrology or rainfall response. NLCD open-water class approaching zero in these 500-m buffers does not indicate lack of wetland water: 30-m classification may not capture small or vegetated breeding waters. C1V1 cannot be reported as C1.2.

## Safe next phase
1. Pin and verify Collection **1.2** land-cover source/version for the full 2001–2015 period. Current publicly queried STAC was C1V1; do not silently substitute.
2. Construct state-year/site buffers **only on the 64,779 observed site-years** and measure missingness by state/year/site type. Source QA remains outcome blind.
3. Pair genuine per-acquisition DSWE with survey dates; quantify missingness before designing hydrology × vegetation contrasts.
4. Freeze outcomes/validation separately, without modifying `frogcs` RC6.
