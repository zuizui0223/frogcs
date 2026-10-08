# Actual Iowa DNR–USGS route-code intersection (v1.4)

**2026-10-08; original USGS NAAMP Runs/Stops/Coordinates and the publicly retrieved Iowa DNR map-index HTML; no frog Counts.csv was read.** Independent from the frozen RC6/JAE submission.

Source-checked GitHub Actions run: [37747421150](https://github.com/zuizui0223/frogcs/actions/runs/37747421150) (success). Raw small receipt: `receipts/IOWA_DNR_NAAMP_INDEX_OVERLAP_ACTUAL_V1_4.json`; artifact 11536367004. Original USGS source checksums and downloaded DNR index SHA256 are in the receipt.

## First-route negative then all-route positive

- The first predetermined map, **360411**, is not in the 2001–2015 standardized NAAMP cohort and has **no original NAAMP coordinate SiteIDs**. This is a *cohort non-overlap*, not a geographic disagreement between a map and survey stops.
- The current Iowa DNR directory has **85 distinct six-digit mapped route keys**.
- **59** match an original route ID in the full national USGS coordinate table.
- **56** match route IDs actually appearing in the standardized **2001–2015 Iowa NAAMP** Runs+Stops eligibility set.
- The standardized source-only Iowa cohort itself has **56** distinct eligible route IDs. Hence each eligible Iowa route ID occurs in the current DNR map list. This is **route-code compatibility**, not independent field-site confirmation.
- The frozen next map-verification target is the **lexicographically smallest matching ID, 360101** (2 distinct sampled years, 6 complete ten-stop runs, 10 distinct SiteIDs). Its official current DNR map is listed under Sioux County. Selecting this short-history route for validation is not selecting it because it gives a desired biological effect; **no frog data or land change was inspected**.
- For a later long-term environmental-effects analysis, only after independent physical-site/historical evidence and Annual NLCD valid-pixel data are available can long-history monitored routes be selected by a separately frozen, outcome-blind chronology criterion; 360101 is a map provenance pilot, not a sufficient 15-year trend study.

## Critical inferential boundary

No identified historical physical site has been independently verified in the 2001–2015 window. Published map files may have been generated after 2015 or may derive coordinates from the same field metadata as USGS. A six-digit route match does not establish stable stop locations. Annual NLCD class transitions and frog-specific within-route allocation effects remain **unmeasured** in the independent study. Route-based climate forecast v0.9 remains a negative held-out result.

Official map directory: https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey
