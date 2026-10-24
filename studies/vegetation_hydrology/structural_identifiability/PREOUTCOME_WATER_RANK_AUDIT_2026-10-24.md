# OUTCOME-BLIND source-information rank audit — frozen before calculation
2026-10-24. Companion to preregistered structural proof & synthetic instrument audit.
Parent paper and last acoustic outcome study remain frozen. **No frog Counts.csv read.**

## Target
For conditioned ten-stop spatial placement, a spatially **uniform** water change between dates cannot distinguish the site-specific effect of water from route-wide activation (whose intercept cancels given k). Compare the water *spatial-change vector* across the SAME physical monitoring stations between years and the same prior calendar month.

## Exact source & unit
JRC MonthlyHistory VER5-0 original 2001–2015 previous-month 500-m panel, SHA256 `bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b`, 172,153 unique `RouteNumber × SiteID × SurveyYear × PreviousMonth` records; only ≥50% JRC observed-pixel fraction. Unobserved pixel 0 is MISSING, not dry. NO original acoustic record used. Optional class context from exact C1V2 500-m panel SHA256 `137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a`.

For each `RouteNumber × calendar month(PreviousMonth)`, list *observed survey years* in increasing order. For each **adjacent observed pair of years** (not necessarily consecutive), intersect physical accepted SiteIDs that have valid JRC water fraction in BOTH years. If >=6 common stations, compute `d_i = water_i,year2 - water_i,year1`. Compute:
- raw `mean(d_i)` (route-common shift);
- route-centred `d_i - mean_j(d_j)`, `range(d_i)` (site-specific change beyond common shift);
- RMS centred contrast `sqrt(mean_i[(d_i-mean d)^2])`;
- flags spatial contrast >=0.05 / >=0.10 (water fractional percentage points).

Denominator: **eligible adjacent observed-year pairs with >=6 common sites**. Also aggregate equal weight per `route × previous-calendar-month` by retaining the FIRST eligible adjacent-year pair, and equal route weight by averaging those first eligible route-month pairs per route. Bootstrap resample **physical routes** (not years/stops) 1000 times; random seed 2840223. Do not treat repeated route-month pairs as IID.

## Interpretation
This is a **measurement/estimability diagnostic**, not a frog association:
- All `d_i = c` means no *spatial rearrangement* of water even if water broadly increased: route-common change disappears from fixed-k configuration likelihood.
- Positive centred `d_i` rank support is necessary but not sufficient for identifying hydrological effect; detection error, habitat correlation and unmeasured time-varying site processes still confound.
- Satellite previous-month water is not day-of-survey temporary pond depth; JRC can miss vegetated wetland.

Do not change thresholds after calculation, including if support proves scarce. Report all years, routes, site intersection attrition, and fraction of eligible comparisons with a meaningful spatial-change contrast. Do not run new acoustic outcome model to compensate if rank support is poor.
