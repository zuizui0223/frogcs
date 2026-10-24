# Habitat × local-water identifiability: prospectively usable route panel
2026-10-24 — environment-only historical NAAMP route candidate shortlist, **not frog outcome refitting**. Parent `main`/JAE RC6 frozen and unchanged.

## Actual progress
- [Selection contract](DESIGN_AND_SELECTION_RULES_2026-10-24.md) fixed before exporting site candidates; 15-year original environmental sources and checksum pins were verified.
- **30 original physical NAAMP routes × 10 accepted physical SiteIDs = 300 station records**, split into 10 routes each:
  - **A**: high observed site-relative monthly-water changes (original JRC source; source-energy top decile and NLCD wetland contrast ≥25pp).
  - **B**: ≥2 stations with NLCD vegetated wetland ≥25% / mapped open water <1%, despite very little observable JRC year-to-year water change. These may be satellite-blind wetland contexts, **not necessarily stable/dry water**.
  - **C**: low mapped wetland/openwater land-cover and low JRC water variation. No verified absence of actual breeding ponds or amphibians.
- At most 2 routes per state within each category (each group spans 6 states), all exactly 10 accepted coordinate locations, pairwise separation ≤25km, and at least one matched March–June previous-month year pair with ≥6 common stations and observed JRC source pixels.
- [Route shortlist](ROUTE_SHORTLIST_V0_1.csv) retains the 30 RouteNumbers and representative spatial source scores. The full 300 station coordinate records, metadata and source reproducibility script are distributed in the attached analysis ZIP; **historical coordinates are not evidence of current site access**.

## New environment-only quantification of where *measurable* water changes concentrate
The official JRC MonthlyHistory VER5-0 2001–2015 source was SHA256 pinned. At ≥50% valid satellite observations, **9,420** same-route/same-previous-month adjacent-observed-year pairs had ≥6 identical sites. Restricting to the *first* eligible pair for each route×month gives **2,793** contrasts across **964** routes.

Let `d_i` be the same-site change in JRC surface-water fraction between years; define *spatial-change energy* `E_rm=Σ(d_i-mean d)²`. For route `r`, average across available spring and nonspring route-months: `E_r=mean_m E_rm`. This is **NOT Fisher information, statistical power or a frog effect**.

| Route-balanced descriptive diagnostic | Value |
|---|---:|
| Route fraction in highest-energy decile | 10% (97/964) |
| Share of observed squared spatial-change energy in that decile | **86.38%** |
| Top 1% share | 40.37% |
| Squared-weight-effective route count | **38.07 / 964** |
| With ≥80% valid satellite pixels, top 10% route share | **86.56%** (950 routes) |
| Restrict same-month first-pair to adjacent one-year survey gaps, top 10% route-month energy | **92.22%** |

Strong concentration is a fact about the **measured JRC signal and the environmental sampling frame**, not an estimate of relative ecological informativeness or real pond-water change. Measurement bias, unequal field effort, ephemeral pools and vegetated water can cause concentration. Avoid "sampling 97 routes guarantees X power" interpretations.

## Original environmental source pins
- USGS Annual NLCD Collection 1.2 land-cover full 2001–2015 panel (2001–2015 station-year original): `137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a`.
- EC JRC/Google Global Surface Water MonthlyHistory VER5-0, previous-calendar-month 500m water: `bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b`.
- Original NAAMP fixed-site coordinate QC accepted table: `2dbd226a117e5d2c9c10dbd6340fb86a07320b2925aaca3249c8a307a5071afc`.
- **No** original acoustic `Counts.csv` used for selecting candidates or energy scores.

## What the independent study must measure
At each of 10 sites, record direct water presence under vegetation, local water depth in **centimeters against a consistent datum**, flooded area, microphone detection covariates, ambient noise and exact recording timestamp. Visit the same sites after **independent** rainfall events and dry spells within a biological calling season. Record unmeasured values as missing, not zero; acoustic CI0 means **assessed nondetection**, not frog absence. See source-only [field study design](../structural_identifiability/FIELD_DESIGN_TO_DISTINGUISH_STATIC_HABITAT_AND_WATER_2026-10-24.md).

A within-site/time water process becomes distinguishable from a stable site propensity when the actual station×event water matrix has nonzero residual after removing both physical-site and route-event means. This is a **rank necessity**, not sufficient causal identification. Static habitat `E_i` remains nonidentifiable against unrestricted `U_i` in a fixed-site effects model even with a perfect local water instrument; static effects require cross-site assumptions, randomized manipulation, or transport to truly novel independent sites.

### Possible independent public dataset for the dynamic *time* hypothesis
Buckley et al. (2020), [Boreal chorus frog calling activity, Central Platte River Valley](https://doi.org/10.17632/p6nbn2hyz9.1) provides **daily** frog calling, time-lapse vegetation phenology and wet-meadow inundation records from 2015–2017 (a wet meadow and a slough). The wet meadow's HYDRO is image-based flooding; the slough HYDRO is river discharge, **different measurement processes**. Original source dataset file was not ingested this turn because the public metadata API returned HTTP 401; no independent temporal water–calling effect was calculated. This dataset could investigate water–calling timing, but it cannot directly replicate NAAMP's ten-stop multi-site configuration without additional sites. Other USGS [Midwest ARMI call-survey data](https://doi.org/10.5066/P19ZCGWM) provide repeat acoustic surveys, but hydroperiod must be verified separately.

## Artifacts and reproducibility
- Exact 30-route CSV in GitHub; 300 station coordinates and full source-audit data in the accompanying ZIP.
- `validate_future_field_panel.py` plus five unit tests and empty input templates are included in the ZIP. Original NAAMP acoustic tables never required.
- The field route roster is **not a travel recommendation**. Confirm contemporary wetlands, legal access, conservation permissions, taxon population presence, logistical safety, and local data quality before any sampling.
