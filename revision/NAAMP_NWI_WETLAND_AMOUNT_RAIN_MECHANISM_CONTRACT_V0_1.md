# NAAMP NWI wetland-amount × rain mechanism contract v0.1 — 2026-10-07

**Status:** post-NWI-regime follow-up frozen before any 500-m wetland-area metric is calculated for focal NAAMP SiteIDs or joined to frog outcomes.

## Scientific role

The existing within-taxon multi-site concentration remains the response endpoint.

Dynamic surface-water mechanisms were not supported, and the first NWI nearest-regime/type interaction analysis did not materially reduce the residual.

This test asks a distinct landscape question:

> Does the amount of mapped wetland habitat surrounding a stop determine how strongly that location converts a common rainfall pulse into reproductive acoustic activation?

The hypothesis concerns landscape capacity × environmental pulse, not static site quality alone.

## Why this is not redundant with prior SiteID propensity

The principal comparator already contains strictly-prior species × SiteID propensity, which represents persistent baseline use of each physical location.

NWI wetland amount is therefore never added as a standalone focal generator effect.

It enters only as a modifier of the within-SiteID temporal rainfall response.

## Source and coordinate authority

Wetland geometry:
- official U.S. Fish & Wildlife Service NWI Wetlands MapServer polygon layer 0.

Site coordinates:
- reuse the frozen NWI assignment artifact derived from the strict remote-sensing coordinate gate;
- do not re-fetch or repair NAAMP coordinates in this analysis.

## Spatial support

Primary landscape radius: **500 m** around each physical SiteID.

All area calculations use EPSG:5070.

NWI polygon holes are preserved.

The 500-m circle is the scientific support. Any larger server-side search is retrieval-only.

No radius sensitivity is authorized for the primary wetland-amount hypothesis.

## Primary landscape metric

For every SiteID with a successful NWI service query:

`wetland_area_fraction_500m`

= area of the union of all NWI wetland polygons intersecting the 500-m circle divided by the area of the 500-m circle.

Rules:
- clip each polygon to the 500-m circle;
- union clipped geometries before calculating area, so overlapping/multipart features are not double-counted;
- if the official query succeeds and no NWI polygon intersects the circle, assign exactly 0;
- API/query failures are missing, not zero.

Range is [0,1].

## Frozen secondary landscape descriptors

Reported for interpretation but cannot replace the primary metric:

- `wetland_patch_count_500m`: number of distinct NWI polygon OBJECTIDs with positive-area intersection with the circle;
- `nearest_wetland_distance_m`: exact EPSG:5070 stop-to-nearest-polygon distance; successful no-wetland sites are recorded as no polygon rather than assigned an arbitrary distance.

These secondaries cannot rescue a failed primary wetland-area mechanism.

## Retrieval

Prefer one route-envelope query for efficiency.

If a route-envelope query fails, use the already validated per-SiteID point-distance retrieval with a 700-m server window and then enforce the exact 500-m EPSG:5070 circle locally.

The 700-m retrieval distance is not a scientific radius.

## Coverage gate

Before any frog endpoint is read, require:
- successful wetland-area assignment for >=90% of focal SiteIDs represented in the strict-coordinate principal universe;
- >=1,500 principal-comparator focal pairs with all ten SiteIDs assigned;
- >=300 routes;
- >=15 states.

Do not lower the gate after readback.

## Model

M0 = existing principal comparator:
- cross-fitted species-specific rainfall response;
- strictly-prior species × SiteID propensity;
- dry-state persistence a=0.75;
- pair-level total wet-incidence matching.

M_AREA adds a species-specific rainfall × wetland-area redistribution term.

### Training variable construction

Within each deterministic training route fold:

1. `dry_x = log(1 + DaysSinceRain)`.
2. Center `dry_x` within physical SiteID using training-fold runs only: `dry_x_c = dry_x - mean_trainingSite(dry_x)`.
3. Let `A = wetland_area_fraction_500m`.
4. Standardize A across training stop-cells: `A_z = (A - mean_training(A)) / sd_training(A)`. If training SD is zero/nonfinite, set the interaction coefficient to zero.
5. Interaction term: `rain_area = dry_x_c * A_z`.

For each species fit a single binomial model with:
- dry_x_c common slope;
- A_z main effect;
- rain_area interaction;
- mean air temperature;
- annual sine/cosine;
- State;
- RunNumber.

The fitted coefficient of rain_area is the dryness × wetland-area interaction. Convert to a wet-response deviation by changing sign.

The M0 species rainfall response remains the common rain response; M_AREA adds only the area-dependent deviation.

### Estimability

Species interaction is estimated only when:
- >=20 positive stop-cells;
- >=5 positive routes;
- training A has nonzero finite SD.

Primary GLM; ridge fallback alpha=0.01.

If the interaction coefficient is nonfinite or |beta|>20 after fallback, set it to zero.

No species subset is selected after readback.

## Focal-pair generator

For focal stop i with training-fold-standardized wetland area A_z,i:

`eta_AREA = eta_M0 + delta_gamma_area_species * A_z,i * rain_contrast`.

The unchanged pair-level common shift then matches observed total wet incidence.

Thus the model tests where activation is allocated, conditional on how much activation occurred.

## Primary diagnostic

On the identical landscape-complete sample compare M0 vs M_AREA using:
- same observed concentration beta;
- 1,000 simulations;
- conditional residual;
- simulated residual 95% interval;
- plus-one upper-tail P.

Primary quantity:

`fraction_residual_removed = (residual_M0 - residual_M_AREA) / residual_M0`.

M_AREA is sufficient only if its observed residual no longer exceeds its simulated upper 95% bound.

## Interpretation

Support would mean that local wetland amount/capacity filters how a common rain pulse is spatially expressed as frog reproductive acoustic activity.

Non-support would mean that neither dynamic surface inundation, nearest mapped hydroperiod class, nor simple local wetland amount explains the concentration.

It does not establish reproductive success, abundance, recruitment, or unique causal mediation.

## Anti-tuning

After wetland-area values are read, do not change:
- 500-m radius;
- union-area definition;
- query-success zero/missing rule;
- within-SiteID rain centering;
- A standardization;
- interaction model;
- species estimability gates;
- route folds;
- a=0.75 anchor;
- concentration endpoint;
- total-incidence conditioning.
