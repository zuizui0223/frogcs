# NAAMP remote-sensing coordinate eligibility contract v0.1 — 2026-10-07

## Purpose

Define an outcome-blind coordinate-quality gate for a separate dynamic-hydrology mechanism study.

No frog calling outcome, concentration endpoint, wet/dry pair direction, or species identity is used in this gate.

## Source

Pinned USGS/NAAMP physical-site coordinate table already used by the archived ERA5 audit:
- columns: RouteNumber, SiteID, lat, lon
- expected SHA256: f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83

## Why a stricter gate is needed

The archived exact-distance analysis identified gross transcription errors. Remote sensing at 30-m pixels and 250-m buffers requires a stricter geometry-only screen than route-centroid weather extraction.

## Fixed geometry-only rules

A RouteNumber is **remote-sensing eligible** only if all of the following hold:

1. at least 8 nonmissing unique SiteIDs have coordinates;
2. every coordinate is within broad conterminous-US bounds:
   - latitude 24 to 50 degrees N;
   - longitude -125 to -66 degrees E;
3. no duplicate SiteID maps to multiple distinct coordinate pairs;
4. route maximum pairwise great-circle distance <= 30 km;
5. no site lies > 15 km from the coordinate-wise route median point;
6. robust route geometry is internally coherent:
   - compute each site's distance to the route median coordinate;
   - if MAD of those distances is >0, no site's distance may exceed median + 8*MAD;
7. at least 8 sites remain after applying rules 2–6; no coordinate is repaired, winsorized or moved.

## Important boundary

Passing this gate means only that a route lacks gross coordinate inconsistencies detectable from geometry alone.

It does **not** prove sub-250-m positional accuracy.

Therefore:
- JRC/DSWE extraction will initially use 250-m and 500-m buffers, not single pixels or 50-m buffers;
- a 100-m sensitivity may be used only after independent coordinate validation;
- 30-m single-pixel inference is not authorized from this gate alone.

## Reporting

Before joining any frog outcome:
- report total routes;
- eligible routes;
- excluded routes by reason;
- distribution of route maximum span;
- distribution of site-to-median distance;
- count of known previously flagged routes retained/excluded.

No threshold may change after frog outcomes are joined.
