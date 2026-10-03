# NAAMP coordinate-geometry quality audit v0.1

Date: 2026-10-03

## Why this audit exists

A post-reopening exploratory analysis attempted to replace route stop-number lag with exact great-circle distance between physical SiteIDs. The resulting distance table contained an impossible maximum within-route distance of 12,498 km. Before interpreting any distance-response pattern, the pinned USGS coordinate file itself was audited without reference to frog outcomes or residual-dependence values.

## Source

Pinned coordinate source already used by the antecedent-rain analyses:

- SHA256: `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`
- columns: `RouteNumber, SiteID, lat, lon`
- 12,064 coordinate rows
- 1,183 route identifiers

## Geometry-only findings

The source file contains clear coordinate transcription errors.

- **one positive longitude** occurs in the U.S. route table: Route **270107**, SiteID **4507**, longitude **+83.302** while the other route sites are near longitude −83°; this alone generates the 12,498-km within-route distance;
- **5 routes** have raw maximum within-route distance >100 km;
- **8 routes** exceed 50 km;
- examples of internally implausible single-site deviations include:
  - Route 880113: one latitude 39.12925 versus the route near 37.3°;
  - Route 720214: one longitude −78.8535 versus the route near −76.9°;
  - Route 350414: one latitude 38.46873 versus the route near 39.6°;
  - Route 270218: one latitude 31.1187 versus the route near 32.1°.

These checks use only coordinate geometry and RouteNumber grouping.

## Decision

The receipt

`exploration/NAAMP_ROUTE_NIGHT_RESIDUAL_DISTANCE_PROFILE_RECEIPT_V0_1.json`

is retained for provenance but is **not authorized for biological interpretation** because the raw coordinate geometry contains known gross errors and no externally validated coordinate-repair table was fixed before that endpoint was read.

No post-result distance cutoff, winsorization, manual coordinate correction or route exclusion is introduced to rescue this analysis.

The spatial-scale inference instead uses the separately frozen **stop-number lag profile**, which requires no coordinate repair. In the primary dry-route-silent stratum, residual correlation remains positive from lags 1–3 (0.296) through lags 7–9 (0.272), both P=0.000999. Stop-number lag is explicitly interpreted as route topology, not exact geographic distance.
