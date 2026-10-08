# v2.7–v2.9: directly geolocated C1V0 loss cells, independent imagery, and USDA tree-canopy test

**2026-10-08 — independent environmental verification line only. RC6 untouched.** New-route NAAMP acoustic Counts.csv is not read in any of these tasks. The earlier v0.9 out-of-time route climate prediction and the v2.2 common-2012 treatment failure remain frozen.

## 1. What the source geolocation actually established

Source-only action [37767652136](https://github.com/zuizui0223/frogcs/actions/runs/37767652136), original [georeferencing receipt and annotated NAIP images](https://github.com/zuizui0223/frogcs/actions/runs/37767652136/artifacts/11547081037), located all five original Annual NLCD **Collection 1.0** mapped forest→nonforest 30m squares on independently served USDA NAIP photos in **2011** and **2013**, as original 600×600 images of exactly the same WMS viewport at each site:

- `360104`, Stop 3, SiteID `6613`: 3 mapped old-forest cells at the southeastern **forest-field edge**. The woodland remains clearly present in both dates. Exact partial canopy changes are unresolved.
- `360412`, Stop 7, SiteID `7247`: 2 mapped old-forest cells in ground that appears **open/agricultural in both NAIP dates**; this suggests boundary/classification ambiguity rather than confirmed clearance, but formal geometric accuracy and manual land-cover validation are pending.

The C1V0 2012 classification confidence values at the five squares were `44, 46, 7, 39, 34` of 100. Visual photo comparison is not ground-truth verification: imagery may differ by month, radiometry, viewing angle, spatial alignment and shadows. The two locations were selected after inspecting older mapped class changes; do **not** promote this to an unbiased accuracy assessment.

## 2. Official C1.2 pixels still blocked

The original [USGS C1.2 annual land-cover release](https://www.sciencebase.gov/catalog/item/697b9279b66b0197c3043cc3) is identified at ScienceBase. The 2012 national archive is listed as `Annual_NLCD_LndCov_2012_CU_C1V2.zip`, with metadata size 1,388,935,096 bytes. A [bounded HTTP Range verification](https://github.com/zuizui0223/frogcs/actions/runs/37767375318) received HTTP 206 **but actually returned HTML**, `text/html`, **4,255 bytes** with `Content-Range: bytes 0-4254/4255`, not a portion of the 1.39GB ZIP. The download endpoint cannot be considered a byte-range-valid original raster. Do not interpret HTTP 206 alone as raster retrieval, adjust source identities post hoc, or mix C1V0 and C1V2 classes.

USGS documents tile-bundled Collection 1.2 downloads through EarthExplorer; the MRLC viewer can produce clipped TIFFs by AOI with email-based delivery. Both are genuine alternatives, but neither has yet produced original site-level C1V2 pixels in this study.

## 3. New source not dependent on NLCD 16-class calls

USDA Forest Service released the `TCC v2025.6` 30m annual tree-canopy product for 1985–2025, with a **Science TCC** product giving percent canopy values without NLCD's water/non-tree-cropland masking, and a separately masked/smoothed **NLCD TCC** product. Both use remote sensing, so they are **not independent field observations** and can share imagery with Annual NLCD. Science TCC is nevertheless a substantially different quantitative **measurement** from a categorical 'forest/not-forest' assignment.

Real [v2.8 official image-service metadata](https://github.com/zuizui0223/frogcs/actions/runs/37770471192) confirmed exactly one `v2025_6` original mosaic entry in each of 2011/2012/2013 for both services:

| Year | Science TCC official catalog item | NLCD TCC catalog item |
|---|---:|---:|
| 2011 | OBJECTID 145 | 66 |
| 2012 | 146 | 67 |
| 2013 | 147 | 68 |

The active v2.9 source-only code `scripts/extract_usfs_science_tcc_at_five_nlcd_cells_v29.py` freezes exactly these **two sites / five cells / three years**, requests original numeric image data on aligned 30m projected windows, requires full 3-year validity, and independently reports canopy-percent differences in both USFS products. It also computes 250m mean canopy at each site as a descriptive reference.

**Status:** Source catalog verified; actual 2011/2012/2013 *TCC pixels have not yet been established until the CI artifact is successful and checked*. CI: [v2.9 original tree-canopy source-only pixels](https://github.com/zuizui0223/frogcs/actions/runs/37770883686). The outcome is allowed to be canopy unchanged, increased, declined, mixed, or source-unavailable. Do not change sites or years to rescue one sign.

## 4. Scientific stop boundary

Old Annual NLCD's isolated 2012 forest loss at 2 of 70 nominal sites does not support a replicated regional treatment; the exploratory discovery route 360417 was previously negative/ambiguous for acoustic reallocation. New seven-route frog outcomes remain unopened. Historical pre-2015 fixed physical station continuity has **zero independently verified sites**. Neither canopy coincidence nor classification confidence establishes movement, reproductive success, loss of occupancy, or causal land-change effects. If the original C1.2 or the independent measurement remains unavailable or weak, leave the ecological effect **untested**, rather than relabel an unreliable five-pixel signal as evidence.
