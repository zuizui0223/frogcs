# 360417: source-only ten-stop coordinate agreement, and an extended temporal opportunity (v1.5)

Date: 2026-10-08. Independent climate–landscape research lane. **No changes to RC6**.

## Verified source-only crosscheck

Official Iowa DNR [route 360417 document](https://www.iowadnr.gov/media/1999/download?inline=) has a numbered ten-stop latitude/longitude table on PDF pages 4–5, dated **12 January 2021** on those pages. The printed "Established" field is blank. PDF SHA256: `74c37c9ed7c3aaccd0a3eb3a0f6ab3834d404313380b8819987f2822add1c1b0`.

A source-hash-checked USGS NAAMP Runs/Stops/Coordinates join found 27 eligible ten-stop runs, six distinct sampled years, and exactly one historic SiteID per each numbered stop (SiteID 7271–7280). The comparison was fixed before seeing USGS-vs-DNR distances, with the published stop order retained and threshold checks at 100m and 250m. **All ten** DNR-to-USGS geographic points matched within 100m: **median 4.150m**, maximum **5.844m**. Source-only CI: [run 37749856908](https://github.com/zuizui0223/frogcs/actions/runs/37749856908), original downloadable [receipt and rendered table pages](https://github.com/zuizui0223/frogcs/actions/runs/37749856908/artifacts/11537855061). Machine-readable compact mirror: `receipts/IOWA_360417_STATE_MAP_USGS_COORDINATE_AGREEMENT_V1_5.json`.

**Critical interpretation:** this is proof of **archived-coordinate vs later state-map agreement**, not independently observed 2001–2015 station continuity. The state map and archived USGS coordinates could have a shared input, so historical field-site validation remains **zero**. The recorded consistency and numerical agreement are adequate to target an **environmental source-only pilot** on the same nominal point coordinates, but not to declare frog habitat change or spatial reallocation until historical field identity/relocation documentation is corroborated.

The first frozen route 360101 has a map with coordinates printed in graphic labels, but no extractable unambiguous ten-row latitude/longitude table in the original PDF text. Its ambiguous alignment has **not** been forced.

## A new, genuinely distinct time-series opportunity

Iowa DNR's [2025 survey report](https://www.iowadnr.gov/media/9064/download?inline=) states: Iowa added 84 USGS NAAMP routes in 2010; after USGS stopped the program in 2015, Iowa incorporated these routes into its own traditional survey/database. This suggests an opportunity to bridge **2010–2025** monitoring and link station-level recorded wet/dry state and land-cover changes across a longer period, but **no longitudinal 2016–2025 route×stop records have been retrieved** and the portal currently exposes an account-based entry system. Do not assert site continuity or availability of raw public downloads until demonstrated.

The same 2025 DNR report notes that volunteer observers record **wet vs dry** site state, car counts, moon visibility, noise, and call indices. Those fields may be materially better than coarse satellite-derived inundation, **but must be checked in the actual historical export schema** before claiming they are accessible in original USGS NAAMP records.

## Next source-only ecological test

Extract official USGS **Annual NLCD Collection 1.2** class and confidence rasters for fixed nominal coordinates for the 360417 stops, with exactly aligned before/after pixels, 250m and 1km buffers, and 80% complete paired pixel coverage. This is strictly **an environmental feasibility/description pilot**, not an acoustic response analysis. Do not substitute category-colored WMS PNG images for true class rasters or treat a later map as proof that the physical wetland location did not change. The previously fixed negative route-scale long-climate acoustic forecast and negative JRC/DSWEmod higher-order mechanism results remain closed.

All results above use official public source data. No frog Counts.csv or NAAMP landscape outcomes were opened in the v1.5 source crosscheck.
