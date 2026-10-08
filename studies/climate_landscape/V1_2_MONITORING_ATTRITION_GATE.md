# NAAMP climate–terrestrial-change study: monitoring attrition, not frog extinction (v1.2)

**2026-10-08. Independent source-only diagnostic. RC6 and the completed negative v0.9 climate–frog held-out pilot are untouched.**

## Actual evidence carried forward

1. **Study sampling and location identity.** The checksum-pinned USGS Runs/Stops/coordinate source produced 7,848 standardized ten-stop runs (78,480 visited stops), 8,223 route × SiteID keys, 6,423 sites sampled in at least two years, 95 keys with different recorded StopNumber through time, and 28,330 adjacent-year same-season site comparisons with stable number and plausible source coordinates. These are **geometry-only candidates**; zero physical stations have independent archival groundtruthing. Source: `receipts/site_identity/NAAMP_SITE_IDENTITY_STABILITY_ACTUAL_V1_0.json`.
2. **Roadside listening conditions.** From the original outcome-blind source audit (GitHub Actions run 37744683508, artifact 11535637019), 29,986 adjacent-year site comparisons were reconstructed; 23,107 had paired valid CarCount records, 27,332 shared the same ObserverTrackingID, and 29,986 had at least a coded hearing-impairment proxy and TimeOut. Of paired CarCount contrasts, 7,183 increased, 7,504 decreased, 8,420 were equal, median paired difference 0. This is an *observation process* as well as a possible biological pressure: do not adjust it away indiscriminately. Original receipt: `receipts/NAAMP_ROADSIDE_DETECTION_HISTORY_ACTUAL_V1_1.json`.
3. **Frog–climate model held-out result (frozen).** Adding preceding-five-year temperature/precipitation to recent weather, site route, round and season *failed* to improve strong chorus prediction in the 9-route exploratory temporal test: held-out log-loss 0.561468 (H0) versus 0.563726 (H1). Do not retune climatic lags, taxa or endpoints after this result.

## New necessary methodological issue

The official [USGS NAAMP protocol](https://www.usgs.gov/centers/eesc/science/north-american-amphibian-monitoring-program) states that sites could be relocated for safety, and that when wetland habitat was destroyed, sites were to be surveyed for three additional seasons and then could be retired after prolonged no activity, with null counts used in some historical trend analysis. Site changes were not always reflected promptly in national route maps.

Consequently a longitudinal model that starts only from *completely observed ten-stop routes* may select away the landscape-loss and severe-disturbance events it aims to study. Conversely, interpreting an unvisited/retired stop as CallingIndex=0 would also bias inference. The raw NAAMP data set and program protocol cannot be presumed to have a uniform historical implementation. We must audit *whether observation opportunities persisted* prior to inspecting frog outcomes.

## New executable v1.2 audit

`scripts/audit_naamp_survey_attrition.py` (with `tests/test_naamp_survey_attrition.py`) uses **only original checksum-pinned Runs.csv and Stops.csv**. It applies the same survey-level eligible-year, unified-protocol and rain metadata checks as the existing independent cohort, then measures:

- All potentially eligible run–round opportunities **before** requiring 10 completely sampled stops, compared with the complete 7,848-run analytical panel.
- Skipped, surveyed, missing and unrecognized stop statuses **without making up acoustic zeroes**.
- Consecutive-year, same-round, within-21-calendar-day pairs with complete→incomplete and incomplete→complete monitoring transitions, excluding duplicate route×round×year records from pair inference.
- A stop *recorded with the same SiteID at the same numeric position* transitioning surveyed→skipped or skipped→surveyed, distinct from a change in recorded SiteID.
- Source-only numerical receipts with exact USGS SHA256 provenance. Does **not** classify habitat destruction, retirement, local extinction, biological site fidelity or relocation causes; no Counts.csv or satellite outcome is read.

Local synthetic tests passed (six new attrition tests; 123 total at v1.2 construction). **Actual USGS attrition counts remain pending execution** until an authoritative CI receipt is obtained. Do not report synthetic checks as ecological findings.

## Biological decision rule

The eventual core question is not whether developed cover predicts a lower average frog count—already studied—but whether *historically verified* land conversion changes which sites express strong calling **and** which sites remain in the monitoring frame. A valid ecological interpretation should distinguish three processes:

1. True change in calling under continuing site observation.
2. Observability change (skip, route realignment, retirement, traffic/noise and volunteer detection), not assumed biological absence.
3. Site identity/land-cover errors (30-m raster precision, map classification confidence, site relocation).

For any truly verified converted/unconverted site subset, report both an intention-to-monitor missingness analysis and an observed-site acoustic analysis. No imputation of no-call from absent surveys. At least two *post-change* surveys would be needed to infer a lag, and only a separate externally validated historical site ledger can certify exact same physical locations.

## Next access/evidence gate

Run the new no-frog attrition receipt in the same GitHub Actions pipeline that successfully downloaded USGS original metadata; then compare its attrition population to the 28,330 geometry-only repeat candidates and the 23,107 traffic-complete pairs. The denominators differ, and cannot be multiplied together without a joined independent metadata ledger. The source-derived **retirement pathway must not be treated as proven for any specific missing stop**.

Annual NLCD Collection 1.2 land cover and confidence imagery is available from [USGS](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover) (1985–2025, 30m). A pixel-level historical footprint still requires externally confirmed coordinates and same-pixel image validity; 30m landscape effects remain unestimated.
