# Independent Iowa DNR route-map crosscheck (v1.3)

**2026-10-08. Source-only validation design, no new frog or Annual NLCD pixel effects.**

## The first concrete external coordinate reference

Iowa Department of Natural Resources [Frog and Toad Survey Maps](https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey) include public maps with six-digit NAAMP-style route identifiers, numbered listening stops and textual latitude/longitude tables. The map for **Route 360411** (Black Hawk County) is at `https://www.iowadnr.gov/media/2019/download?inline=`. Its map pages give **Created on: 3/11/2020** and the accompanying directions page is printed **Thursday, January 14, 2021**. Source-to-code transcription is in `reference_routes/iowa_dnr_360411_2020_route_waypoints.csv` (all 10 published stop coordinates and original PDF URL); this is **not** a new GPS field survey by this project.

This source is valuable because the national USGS coordinate source is known to contain transcription errors and the DNR document separately specifies named stops and road/wetland descriptions. **But** the state map is posterior to the 2001–2015 NAAMP analysis years, may inherit some original coordinates, and by itself cannot prove the same physical station was used uninterrupted through that earlier period. Even a perfect DNR-versus-USGS match must remain `map_agreement_after_study`, **not** `verified_external_historical_site`.

## Frozen, outcome-blind first route test

Run `scripts/audit_iowa_route_map_crosscheck.py` with original SHA256-pinned 2017 USGS `Runs.csv`, `Stops.csv`, `Coordinates.csv` and the Iowa DNR waypoint table. Without reading Counts.csv or environmental outcomes:

1. Determine whether **Iowa route 360411** is actually present in the standardized NAAMP 2001–2015 sampling frame.
2. Match each numbered stop to a unique SiteID based on **historical original run/stop records only**, marking ambiguous/replaced numbers as unresolved rather than picking the best geographic match.
3. Compare frozen DNR map stop coordinates to the unedited USGS coordinate table by haversine distance, after the preexisting geometry-only screen. Report exact distances and fixed thresholds 100m (primary), 250m (sensitivity) along with any unresolved/missing stop IDs.
4. Preserve all source hashes and PDF provenance and mark historical physical-site verification **zero** even if coordinate matches are good.

The test returns a clear nonmatches/absence category if no route meets the published record. It will **not** certify full historical site continuity, movement, habitat conversion, breeding success, or climate mechanism. Synthetic code tests were passed before reading any real route crosscheck outcome.

## Current outcome evidence (frozen)

The independently sampled 9-route v0.9 frog–climate forecast remained negative; adding previous-five-year annual Daymet temperature and precipitation information did not improve held-out strong-call prediction beyond short weather and route/season controls. Other surface-hydrology explanations for the original concentration were also negative. No further climatic predictor retuning is authorized.

## Recent source-only monitoring attrition

The v1.2 [GitHub Actions source audit](https://github.com/zuizui0223/frogcs/actions/runs/37745542779) evaluated 9,401 candidate runs, 8,975 ten-stop complete field opportunities and 7,848 fully eligible runs. It found 425 candidate runs with at least one explicitly skipped stop (626 skipped stop rows), and consecutive-year, same-season route-round pairs included 103 full-to-incomplete and 78 incomplete-to-full transitions. Same stop identity transitions observed→skipped numbered 158 and skipped→observed numbered 136; another 202 transitions reused the same stop order but a different SiteID. These are **record-state transitions**, not proven ecology or retirement. The original code receipt is `receipts/NAAMP_MONITORING_ATTRITION_ACTUAL_V1_2.json`.

## Next decision

If DNR and USGS coordinates agree, this validates a **2020 map–archived coordinate alignment pilot** only. Historical station confirmation would require dated 2001–2015 route descriptions, state coordinator records, or other contemporaneous sources, plus explicit relocation history. No post-2015 match will be counted as 2001–2015 historically verified physical sites. If independent historical documentation is unavailable, use a clearly labelled coarse route-scale exposure pilot instead of a false 30-m same-site analysis.
