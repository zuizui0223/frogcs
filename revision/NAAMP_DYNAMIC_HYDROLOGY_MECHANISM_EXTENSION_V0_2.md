# NAAMP dynamic-hydrology mechanism extension v0.2

**Status:** supersedes v0.1 before any JRC water value was extracted at a focal NAAMP SiteID.  
**Purpose:** explain the already-established within-taxon concentration residual; this is not a new ecological endpoint.

## Fixed biological target

Existing RC6 result:
- observed concentration beta = 1.6503;
- principal prediction = 1.3535;
- residual = 0.2969.

The endpoint remains exactly the frozen higher-order within-taxon concentration statistic.

The only mechanistic question is:

> **Does dynamic local wetland state explain the remaining concentration after taxon-specific rain response, prior SiteID use, dry-state persistence and total activation are already represented?**

## Why v0.2 changes the hydrology baseline

The response-blind request manifest showed:
- 2,814 coordinate-safe focal pairs on 423 routes;
- 4,245 unique physical SiteIDs;
- only 8 JRC 10-degree tiles;
- 397 survey-month tile files;
- 1,224 additional tile-month files would be required for a literal 1984-2000 site climatology.

No JRC value at a focal SiteID and no frog endpoint value was read to make this change.

JRC already supplies **Monthly Recurrence**, a 12-image climatology giving the percentage recurrence of water for each calendar month across the dataset period. v0.2 therefore uses that fixed seasonal expectation instead of reconstructing an unnecessary pre-study climatology.

This change is computational and conceptual: persistent seasonal wetness belongs to the baseline; the mechanism of interest is deviation from expected monthly wetness.

## Coordinate authority — unchanged

Official coordinate table:
- SHA256 `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`.

Geometry-only exclusion rules:
1. non-finite coordinate;
2. outside 24-50 N or -125 to -66 E/W longitude bounds;
3. route maximum pairwise physical-SiteID span >100 km.

No manual repair.

Response-blind preflight result:
- 1,178 / 1,183 routes safe;
- excluded routes: 270107, 270218, 350414, 720214, 880113;
- frozen focal intersection before water-value coverage: 2,814 pairs, 423 routes.

## Primary remote-sensing products

Use JRC Global Surface Water **v1.0**, matching the 1984-2015 NAAMP study endpoint.

1. `JRC/GSW1_0/MonthlyHistory`
   - 30 m;
   - monthly;
   - class 0 = no data, 1 = non-water, 2 = water.

2. `JRC/GSW1_0/MonthlyRecurrence`
   - 30 m;
   - 12 climatological monthly images;
   - recurrence expressed as percent water recurrence for that calendar month.

Direct public source is the JRC JEODPP archive under `GSWE/MonthlyHistory/VER1-0` and `GSWE/MonthlyRecurrence/VER1-0`.

The MonthlyHistory GeoTIFFs are remotely range-readable, EPSG:4326, 10-degree tiles, 40,000 x 40,000 pixels at 0.00025 degrees.

## Fixed spatial support

Primary radius: **250 m** around the official physical SiteID coordinate.

Named sensitivities only:
- 100 m;
- 500 m.

The primary radius cannot change after focal hydrology values are joined to frog outcomes.

## Current monthly water fraction

For each physical SiteID x survey month:

`W_current = n(water class 2) / n(valid class 1 or 2)`

using pixels whose centres fall within the 250-m geodesic buffer.

A current site-month is valid only if >=50% of pixels in the circular buffer are class 1 or 2.

## Seasonal expected water state

For each physical SiteID x calendar month, extract the 250-m mean of Monthly Recurrence:

`W_expected = mean(monthly_recurrence) / 100`

over pixels with valid recurrence observations.

Require >=50% valid buffer coverage.

## Primary local-hydrology exposure

`H = W_current - W_expected`

This is the event-specific monthly surface-water anomaly relative to that site's usual water recurrence for the same calendar month.

For each wetter-drier focal pair and physical stop:

`delta_H = H_wet - H_dry`.

This is the primary hydrology variable entering the mechanistic generator.

## Named hydrology sensitivity

Direct water-state difference:

`delta_W = W_current_wet - W_current_dry`.

This sensitivity does not replace delta_H regardless of result.

## Coverage gate before mechanism outcome calculation

Remote-sensing values are extracted and coverage is frozen before calculating any hydrology-augmented concentration endpoint.

Proceed only if hydrology-complete data contain at least:
- 1,500 focal pairs;
- 300 routes.

A focal pair is hydrology-complete only when all ten physical stops have valid primary H for both wet and dry surveys.

Failure classification:
`hydrology_coverage_inconclusive`.

No missing hydrology value is imputed from frog activity or neighboring stops.

## Comparator sequence

M0: same-sample frozen principal comparator:
- strictly-prior species x SiteID probability;
- a=0.75 dry-state persistence;
- opposite-route-fold taxon rainfall response;
- pair-level total-incidence matching.

M1: M0 + dynamic local hydrology.

The exact M1 coefficient parameterization is frozen after the response-blind hydrology coverage receipt and before hydrology is joined to frog outcome values.

The M1 model must:
- preserve pair-level total-incidence matching;
- use delta_H only in the primary test;
- estimate hydrology influence out of route fold;
- not introduce a new outcome or geometry statistic.

A taxon-specific hydrology extension is allowed only if its estimability rule and shrinkage are frozen before outcome readback; it cannot replace M1 based on which looks better.

## Primary mechanistic estimand

On the identical hydrology-complete sample:

`fraction residual removed = (M0 residual - M1 residual) / M0 residual`.

Report also the M0 and M1 predicted concentration and residual null envelopes.

## Sufficiency rule

Dynamic local hydrology is **sufficient for the concentration pattern** only if the M1 observed residual does not exceed the M1 simulated upper 95% residual bound.

If the residual remains significant, report the continuous fraction removed without inventing a post-readback threshold for “partial support”.

## Interpretation

If sufficient:
> remotely sensed dynamic local surface-water state can reproduce the previously unexplained within-taxon concentration on the analysed sample, supporting local hydrological filtering as the leading mechanism.

If residual is reduced but remains outside the null:
> local hydrology is a partial generator of the configuration, but additional taxon-level or local processes remain.

If little predictive/residual improvement:
> JRC-scale monthly surface-water state does not explain the concentration; finer hydroperiod, water depth/temperature, vegetation, demographic state or social facilitation remain plausible.

Even a sufficient model does not prove unique causal mediation because both frog activity and hydrology are observational.

## Secondary remote sensing

Landsat Collection 2 DSWE may later refine timing to scene scale:
- nearest valid acquisition on or before survey within 16 days;
- 32-day named sensitivity.

DSWE is secondary and cannot replace the JRC monthly primary based on its result.

NWI remains static context only and cannot rescue a failed dynamic-hydrology test.

## Anti-tuning

After focal hydrology values are joined to frog outcomes, do not change:
- coordinate source/exclusion;
- JRC v1.0 source;
- primary 250-m radius;
- MonthlyHistory class handling;
- MonthlyRecurrence seasonal baseline;
- 50% valid-pixel rule;
- delta_H definition;
- coverage gate;
- concentration endpoint;
- residual-removal estimand;
- sufficiency rule.
