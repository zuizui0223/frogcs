# v2.1: eight new Iowa NAAMP routes — actual pre-outcome cohort audit

Date 2026-10-08. **Actual USGS source-only receipt**, executed on GitHub Actions [37761985679](https://github.com/zuizui0223/frogcs/actions/runs/37761985679). This gate read **Runs, Stops and source coordinates only**, never `Counts.csv`. The eight sites were chosen from the complete current Iowa DNR × original NAAMP 56-route metadata intersection via **>=5 observed years, exactly 10 recorded SiteIDs**, excluding the previously outcome-explored 360417 route. These criteria were fixed *before reading any new-route calls*, but the earlier 2012 ecological breakpoint was chosen after the 360417 land-cover maps were inspected. This is not independent preregistration of a climate effect.

## Actual results

- **8/8** routes retained stable recorded StopNumber → SiteID mapping across standardized source years.
- **8/8** routes have observations before 2012 and in at least two distinct years after 2012.
- **7/8** have all ten archived nominal site coordinates passing the prior geometry-only screen. Route **360109** has **zero of ten** passing geometry; it is **excluded** from high-resolution environmental exposure pending independent original-source correction. Do not force or patch coordinates after seeing any frog outcomes.
- Every route remained **zero independently historically field-verified physical stations**. Geometry-only passing coordinates do not license station-level causal habitat inference.
- Observed source years were 2009–2015 depending on route; counts and the actual year calendar appear in the original JSON receipt.

### Seven provisional nominal-geometry routes (no new-route calls opened)

| Route | Standardized runs | Surveyed years | Pre-2012 runs | Post-2012 runs |
|---|---:|---:|---:|---:|
| 360104 | 14 | 5 | 3 | 9 |
| 360110 | 18 | 6 | 6 | 9 |
| 360125 | 14 | 6 | 5 | 7 |
| 360213 | 11 | 5 | 3 | 6 |
| 360219 | 14 | 6 | 3 | 8 |
| 360316 | 11 | 6 | 3 | 6 |
| 360412 | 10 | 5 | 4 | 6 |

The eighth source-selected route `360109` had 13 standardized runs and a pre/post window, but is blocked by source geometry. All **ten** sites from route 360417 are the previously exploratory discovery population, not an independent replication.

## Scientific stop rules

1. Do not claim that a 2012 landscape event happened at each of the seven routes. **Their Annual NLCD site-level paired pixels have NOT been extracted.** The 2012 split here tests *sampling feasibility*, not habitat conversion, climate-change response or a treatment effect.
2. The DNR public maps postdate NAAMP and may inherit coordinates from the original source. Reconcile archive field-station continuity with dated state coordinator route/stop descriptions before 30m acoustic-site effects can be claimed.
3. Do not read `Counts.csv` for new routes to choose which changes, species, dates, radii or stop locations should be mapped. First assess real annual C1.2 Land Cover **and Confidence**, exact source provenance, prior-year support, aligned pixels and missingness across all provisional routes.
4. Single state and a maximum of seven geometry-pass routes is still a weak independent route count; no cross-geography generalization or Nature-level causal claim is warranted.

This is a separate future landscape study; the 9-route Daymet v0.9 out-of-time result stayed negative and frozen, and JAE RC6 was not amended.
