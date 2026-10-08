# v2.5 — Actual official C1.2 archive provenance and independent Iowa NAIP aerial source check

**2026-10-08. Independent frog climate×landscape line. Source-only review. RC6/JAE frozen.** No new amphibian Counts.csv was read. This is not an independently preregistered landscape-effect test.

## Original USGS C1.2 file identities finally located

USGS [ScienceBase original parent](https://www.sciencebase.gov/catalog/item/655ceb8ad34ee4b6e05cc51a) metadata identified itself as "Annual National Land Cover Database (NLCD) Collection 1 Products (ver. 1.2, June 2026)". [Source-only GitHub Actions](https://github.com/zuizui0223/frogcs/actions/runs/37766501003) checked 20 child catalog items without downloading a national raster. The official matched C1.2 product children are:

- [Land Cover, item 697b9279b66b0197c3043cc3](https://www.sciencebase.gov/catalog/item/697b9279b66b0197c3043cc3)
- [Land Cover Confidence, item 697b92b8b66b0197c3043cc7](https://www.sciencebase.gov/catalog/item/697b92b8b66b0197c3043cc7)
- [Land Cover Change, item 697b9298b66b0197c3043cc5](https://www.sciencebase.gov/catalog/item/697b9298b66b0197c3043cc5)

Actual archive entries for 2011–2013 are named `Annual_NLCD_LndCov_{year}_CU_C1V2.zip` (each approximately **1.38–1.39 GB**), and `Annual_NLCD_LndCnf_{year}_CU_C1V2.zip` (each approximately **7.67–7.70 GB**). These are true original C1.2 *catalog entries*, not the old Esri ImageServer C1V0. **ZIP entries and metadata alone do not mean we have downloaded a single C1V2 pixel.** Avoid large blind downloads and requester-pays AWS. The separate bounded-range zip central-directory diagnostic is recorded by workflow `climate_nlcd_c12_sciencebase_zip_range_v26.yml`.

Official [June 2026 release note](https://www.usgs.gov/centers/eros/news/annual-nlcd-collection-12-now-available) emphasizes *intra-collection continuity* with previous C1.0/C1.1 products. C1.2 rechecking is a critical **version consistency** check, but should not be represented as a truly independent remote-sensing ground-truth dataset.

## Independent 2011 vs 2013 *aerial photographs*

The [original successful source-only NAIP WMS run](https://github.com/zuizui0223/frogcs/actions/runs/37766635939) fetched **four** 600×600 USDA NAIP orthophoto PNGs from Iowa State University Geography's original `naip_2011_nc` and `naip_2013_nc` WMS layers, with exact same EPSG:3857 bounding boxes for each of two fixed nominal points (rather than independent land-cover-map re-renderings):
- `360104`, stop 3, SiteID `6613`: 2011 hash `0db6632a2e56db9cdf6fc94cd02a0359756344e743a63dff12bbd82a94f04d92`; 2013 hash `d32e05992ffb03ee10173e22fcbaf17dd00fa1766571332eee121f88c0cac3de`.
- `360412`, stop 7, SiteID `7247`: 2011 hash `58c513c366b111df5c8a949c58b25805173b8aa7d44baf7f90158ba03ea4fff7`; 2013 hash `365fbbc218f1d44370edc99a3a45eb74a92fa7d20063e5b7b95a790007f8f0a4`.

[Original archived four photographs and source receipt](https://github.com/zuizui0223/frogcs/actions/runs/37766635939/artifacts/11544688039). Both sites were chosen **after viewing C1V0 mapped environmental classes** (but before new-route frog calls were read); this is an explicitly biased targeted source-quality diagnostic, not an independent random-sample confirmation. Forest stands, agricultural boundaries and streamside wooded corridors remain visibly present in both image dates. No conspicuous *large-scale* canopy clearance is apparent in these limited viewports, but localized removal, partial growth and tree type change cannot be reliably determined without image-georeferencing and time-of-year control.

Critically, original C1V0 **2012 loss pixels numbered just five** across these two 250m stops (three at SiteID 6613, two at SiteID 7247); 2012 class confidence values `44,46,7,39,34` were low. At SiteID 7247, net mapped forest percentage actually **increased** despite a few gross-loss pixels. Neither the older class map nor the WMS photos justify an "2012 deforestation treatment" or any acoustic-site reallocation claim.

## Current decision

Do not reopen the negative route-level past-five-year climate prediction or original JRC/DSWEmod surface hydrology mechanisms. No new seven-route calling endpoints. Retain the stronger alternative evidence path: exact C1V2 **land-cover + confidence at the same georegistered source pixels**, and separately recorded historical 2001–2015 fixed-station relocation evidence. If either remains absent, declare confirmatory land–frog causal inference not identifiable. A published state map from 2021 is not independent confirmation of pre-2015 station continuity.

The v2.5 study has **zero historically independently field-verified sites**, **zero original C1V2 pixels**, and **no demonstrated land-cover-caused frog effects**. It has genuine official C1.2 product item IDs and independent airborne-imagery pairs for future QA.
