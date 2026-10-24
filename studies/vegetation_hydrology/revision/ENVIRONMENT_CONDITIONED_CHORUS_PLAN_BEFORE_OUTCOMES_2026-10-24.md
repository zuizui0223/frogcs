# Vegetation × preceding-month wetland water: frozen design *candidate* (outcome-blind)
Date: 2026-10-24
Status: **data-covariate analysis plan, not an authorisation to open acoustic outcomes**. The parent `frogcs` RC6 is a frozen exploratory analysis of NAAMP. A subsequent NAAMP analysis is not independent replication or confirmatory validation, even if its environmental covariates were prepared without calling data.

## Biological question
On meteorologically favourable survey nights, why does a taxon re-enter a substantial chorus at *some* historically recurrent physical stations, rather than uniformly along the route? Separate:
(A) durable habitat context (wetland vegetation/open-water mosaic); 
(B) transient, preceding-month remotely observed surface water; 
(C) taxon × route-night dependence remaining after those environments are represented.

The immediate analysis before any frog response is an **environmental estimability audit**, not a new ecological mechanism test.

## Environmental data authority
- USGS Annual NLCD Collection 1.2, 2001–2015: 64,779 QC-site×year records, 100/500m measured class fractions. **Primary spatial scale 500m**; 100m developed cover is a separate detection/road-setting sensitivity. Individual survey dates are not guaranteed to precede retrospectively assigned annual land-cover classes; avoid same-day causal wording.
- EC JRC/Google GSW MonthlyHistory VER5-0, pixel codes 0=no observation, 1=nonwater, 2=water. **Use the entire immediately preceding calendar month** as a coarse temporally prior proxy, not a rolling 30-day window or water depth. Primary water pixel summary is `n_water / n_observed(land+water)` within a geodesic 500m buffer. Primary availability criterion: **>=50% observed pixels**, ≥80% for sensitivity. Missing (0) pixels never count as nonwater. Preserve original TIFF URL and SHA256 for each site-month.
- NLCD open water and JRC monthly water are distinct variables and may disagree at vegetated/shaded wetlands. Never equate either with measured breeding pond depth/hydroperiod.
- NAAMP canonical physical IDs require exact RouteNumber × SiteID and coordinate QC. Held sites are excluded for geographic reasons independent of frog data; report exclusions.

## Before acoustic outcomes may be linked
1. Complete and reconcile all 2001–2015 original JRC tile-month source fragments (expected **700** distinct source URL/month tiles and **172,153** site×previous-month source keys across 185,221 station visits). At most 4 parallel source jobs; each original source hash and item validation required; absent source outputs are not silently dropped.
2. Audit coverage by **State × survey year × preceding-month season × 500m habitat class**. Report loss rates in the exact NAAMP matched-pair subset separately, **only after** the overall geography-only source audit and primary outcome rules are fixed. The 2001 source sample shows striking seasonal unevenness (January 18.2% usable, May 98.5%); this requires visibility adjustment/stratification, not fill-as-dry.
3. Audit within-route water support: for a route×pre-survey-month group with ≥8 candidate stations, count ≥6 valid stations and the max-min 500m water fraction. Do not treat route-month groupings as one verified route-run. Audit within-site *same seasonal month across years* water changes to separate apparent seasonality from potential hydrologic event variation. If measurable water variation or season-specific overlap is too low, declare temporal hydrology effect **non-estimable** rather than negative.
4. Freeze exact frog subset, temporal/spatial train/test split, outcome processing, missingness handling, null-model simulation and stopping criteria *as a new document* before `Counts.csv` is opened for this new study. Do not reopen/retune JAE RC6 endpoints.

## Proposed primary comparison (future; not executed)
The response-magnitude-conditioned within-taxon multi-site concentration from RC6 remains the biological organizing object: an acoustically route-new taxon is one that was not **recorded calling** anywhere in the drier run, not an absent population. CallingIndex CI2–3 denotes overlapping/continuous chorus; route stops were surveyed **sequentially**, not simultaneously. Total wet incidence and first-order recruitment/spread remain explicitly conditioned as in the parent comparator.

- M0: route-cross-fitted taxon-specific weather/rain sensitivity, strictly prior SiteID calling propensity, dry persistence, total activation magnitude.
- M1: M0 + route-centred 500m wetland-vegetation fraction and open-water fraction; species/taxon-specific slopes with partial pooling or fixed prechosen regularisation. Include 100m developed-cover indicator as a road/detection sensitivity rather than interpreting its slope as ecology.
- M2: M1 + strictly preceding-calendar-month JRC water fraction and `taxon × water` response; include observed-pixel completeness and season, with spatially/temporally blocked evaluation. Never impute missing water to zero.
- M3: M2 + residual taxon×route-night dependence to assess whether first-order water+vegetation reproduces the observed multi-site configuration. Post-environment residual could reflect unmeasured fine-scale hydrology, breeding readiness, local demography, acoustic communication or other causes; it cannot uniquely establish social facilitation.

Co-primary reporting dimensions (future): (1) marginal strong chorus prediction/calibration at held-out route locations; (2) response-magnitude-conditioned configuration residual versus predeclared simulations; (3) historical strong-SiteID targeting attenuation after habitats are included. Distinguish prediction/calibration and explanatory identification.

## Robustness / stopping
- Block training/test by complete **RouteNumber**, with all historical SiteIDs kept in their route fold; perform a separate blocked **year** sensitivity; cluster uncertainty by route, not station IID.
- Report source-availability selection by habitat/season in every model stage. Source-complete-only models must use same-sample comparisons; sensitivity can weight for *observed-source availability only* if propensity and overlap diagnostics permit and are frozen in advance. Never claim observations are missing at random without diagnostics.
- Sources are retrospective maps with cloud/visibility biases and satellite hydrology is poorly sensitive to some vegetated ponds. Species, observer, site history and date are intertwined; these are observational conditional associations.
- No extra new NAAMP post-hoc mechanism family or JAE manuscript changes are authorised by this draft. External confirmation would require genuinely independent frog monitoring with verified water/habitat series.

## Empirical environment-only feasibility already known
For 2001, 42/42 monthly original TIFF tiles; 7,511 station×preceding-month keys; 5,639 (75.1%) with ≥50% monthly observed pixels; 1,570 (27.8%) with water pixels among usable. 563 route×previous-month groups had ≥8 candidate stations and ≥6 usable; 232 had ≥5pp water contrast. Strong missingness and low within-site temporal contrast make the cross-year, season-matched hydrology audit decisive before any outcome linkage.
