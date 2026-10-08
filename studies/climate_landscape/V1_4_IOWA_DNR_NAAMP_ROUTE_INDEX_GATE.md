# Official Iowa DNR map index vs USGS NAAMP source identity v1.4

**Scientific status: response-blind route-key feasibility, no frog outcomes, no Annual NLCD pixels. Separate from RC6.**

## Trigger

The prespecified first route comparison using Iowa DNR's current map **360411** (2020-03-11) completed successfully as an execution but produced `ROUTE_NOT_IN_STANDARDIZED_NAAMP_COHORT`, with **zero eligible Runs, zero coordinate SiteIDs**, and no geographic waypoint comparison. This is an **unavailable-join finding, not evidence of geographic disagreement**. Authoritative result: `receipts/iowa_dnr_360411_original_noncoverage_v13.json`, original Actions run [37746441280](https://github.com/zuizui0223/frogcs/actions/runs/37746441280), original zip artifact 11536595931.

## Necessary second gate before looking at more maps

Rather than select individual map routes because their picture appears ecologically interesting, build an **exhaustive route-code intersection** between:

1. all six-digit route keys in the **current Iowa DNR official map directory**, downloaded only from `https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey` (with raw HTML SHA256 recorded);
2. the entire checksum-verified original USGS coordinate table (12,064 route–SiteID rows);
3. the checksum-verified 2001–2015 standardized Iowa NAAMP `Runs.csv`+`Stops.csv` *observation opportunity* panel.

No `Counts.csv`, water indicators, prior road response, satellite land-cover effects, frog outcome or route attractiveness may influence inclusion. Exact six-digit keys are used; no fuzzy nearest-location matching. Report counts and every matching route ID. If any route is truly observed in both sources, select the **lexicographically smallest matching route code** for the next independently documented waypoint comparison. If none overlaps, classify the DNR index as a **different or historically nonoverlapping map resource** for this 2001–2015 source sample, and **do not** assume the 2020 maps authenticate the NAAMP fixed sites.

A match of a route ID is strictly a **necessary condition**, not proof of stable physical stations or any mapped land change. Historical 2001–2015 field identity still requires contemporaneous route records, documented stop relocation history, and independent station evidence. Historical externally verified stations remain zero until those checks succeed.

## Source-pinned reproducibility

Code: `scripts/audit_iowa_dnr_route_index_overlap.py` and synthetic unit tests `tests/test_iowa_dnr_route_index_overlap.py`. Original source hashes checked before reading. Current DNR HTML is fetched and SHA256 recorded, but may change over time. If DNR access is blocked, fail closed with explicit source unavailability; do not substitute unsourced 6-digit keys. GitHub workflow `climate_iowa_route_index_overlap.yml` downloads original NAAMP metadata on the network runner; uploads only source-only metadata receipts, not raw NAAMP tables.

## Biological boundary

The fixed v0.9 route-climate heldout result was negative; earlier JRC/DSWEmod surface-water configuration mechanisms were negative. Do not search outcome thresholds or climatic lags after those results. The long-term environmental tracking vs historic acoustic site legacy hypothesis remains **untested** pending real pixel-dated land-cover change with credible physical-station identity and repeated pre/post observations. A post-2015 DNR match is not an excuse to call 2001–2015 stations field verified.
