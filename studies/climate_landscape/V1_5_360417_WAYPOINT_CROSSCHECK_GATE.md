# Iowa 360417: numerical published-map coordinate crosscheck (v1.5)

Date: 2026-10-08. Source-only: **no NAAMP frog outcomes or satellite change values used**. Does not amend RC6.

After a response-blind original DNR-PDF text audit, route 360417 (Warren/Madison counties) has a ten-row `Site Number / County / Latitude / Longitude` table on pages 4–5 of its [official current route document](https://www.iowadnr.gov/media/1999/download?inline=). The PDF is **post-2015** (metadata 2021), so numerical agreement is **not historical field verification**. The earlier first map 360101 contains point coordinate labels but no unambiguous ten-row text table; no coordinate guessing is allowed.

This analysis freezes the original DNR PDF SHA256 `74c37c9ed7c3aaccd0a3eb3a0f6ab3834d404313380b8819987f2822add1c1b0`, the official source URL, ten stop numbers, and comparison thresholds 100m and 250m, all before USGS coordinate differences are read. USGS original Runs/Stops/Coordinates SHA256 must match the existing immutable pins. Only a stable, unambiguous historical `StopNumber -> SiteID` mapping may be used. No nearest-point reassignment, missing-site replacement, threshold tuning or outcome-based route selection.

The output will report per-stop coordinate distances and exact matched/ambiguous counts, plus an explicit zero for independently documented **2001–2015 physical field-site continuity**. Even if all ten coordinates agree, downstream site-level 30m historical landscape-effect inference remains unlicensed without independently dated route relocation records.
