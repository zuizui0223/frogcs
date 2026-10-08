# v3.0 Actual USDA Science TCC model uncertainty at five C1V0 mapped forest-loss pixels

**2026-10-08. Source-only. Not independently sampled; not a frog effect. RC6 untouched.**

Original [GitHub Actions 37772164538](https://github.com/zuizui0223/frogcs/actions/runs/37772164538) completed successfully with **5/5 synthetic tests passing** and **zero errors** in actual USDA raster requests. Its original full [source-only artifact](https://github.com/zuizui0223/frogcs/actions/runs/37772164538/artifacts/11547428557) preserves source-hash, year-specific mosaic identities, v2025.6 catalog responses and numeric original USFS science canopy and standard-error values. The compact permanent source-linked machine-readable result is at `receipts/USFS_SCIENCE_TCC_V2025_6_FIVE_PIXEL_MODEL_SE_ACTUAL_V30.json`.

**USFS Science TCC and official Science TCC SE are *different outputs from the same USFS modeling pipeline*.** A corresponding independent USDA NAIP aerial-image comparison exists, but this is not five field-verified sites or a calibrated independent accuracy test. TCC model SE values are encoded 100× in **U16** and decoded by dividing by 100; missing sentinels 65534 and 65535 are excluded.

| Previously selected route / pixel | Science canopy 2011→2012→2013 (%) | SE 2011→2012→2013 (percentage points) | 2011–2013 change |
|---|---:|---:|---:|
| 360104/6613, pixel 1 | 23 → 9 → 8 | 1.10 → 1.36 → 1.38 | −15 pp |
| 360104/6613, pixel 2 | 35 → 8 → 6 | 5.96 → 2.04 → 2.10 | −29 pp |
| 360104/6613, pixel 3 | 9 → 3 → 2 | 1.66 → 1.72 → 1.73 | −7 pp |
| 360412/7247, pixel 1 | 3 → 3 → 3 | 2.74 → 2.63 → 2.65 | 0 pp |
| 360412/7247, pixel 2 | 3 → 2 → 3 | 2.57 → 2.75 → 2.75 | 0 pp |

All 3/3 nominal forest-loss cells at **360104 stop 3** exhibit substantial *modeled* canopy decline and, as a descriptive magnitude check, their absolute declines exceed the sum of annual source SEs (2.48, 8.06, 3.39 pp respectively). All 2/2 cells at **360412 stop 7** show no persistent modeled canopy change. The distinct NLCD TCC product **masks all five pixels to 0% for all years**: hence using *postprocessed NLCD TCC alone* would hide the difference visible in the unmasked Science product.

**This is not a statistical hypothesis test.** The source's SE summarizes forest-regression prediction variation, not an independently calibrated error of the interannual change; annual errors can be correlated; the sum-of-SE check is not a 95% interval or a P-value. Post-readback site and pixel selection precludes claiming generalizable or independent accuracy. NAIP photographs show a field-forest edge at 360104 and agricultural/open space at 360412, but different acquisition/radiometric conditions mean they cannot definitively prove the exact canopy amount removed.

**Biological implication:** The naive common-2012 forest-conversion treatment was rejected earlier (only 2/70 nominal 250m stops with even one C1V0 loss cell, and five cells total, with low C1V0 class confidence). The canopy data add one *possible local canopy-decline candidate* at 360104—not a replicated regional habitat intervention or evidence of frog movement. We still have **0 independently confirmed historical 2001–2015 physical stations, 0 original Annual NLCD C1.2 land-cover/confidence pixels**, and no frog outcomes examined for these newly selected routes. No species- or lag-window post hoc tuning will follow.

**Next source gate:** determine whether dated Iowa route-station relocation records exist for 360104/360412, and independently obtain Annual NLCD C1.2 land-cover + confidence or comparable original imagery. If either fails, label the within-route acoustic adaptation/legacy mechanism untested. Do not promote these five environmentally postselected pixels as an ecological effect.


## Listening-stop ecology, verified from separate DNR route descriptions

Official post-study Iowa DNR route descriptions specify the **listening context**, rather than merely categorizing a generic land-cover pixel:

- [Route 360104](https://www.iowadnr.gov/media/1953/download?inline=), stop 3 (SiteID 6613), is described as a **grassy roadside drainage ditch bordering a small woodlot** in Worth County. The large modeled canopy declines occur on that woodlot's **field-facing edge**. Tree canopy change is a potential *terrestrial-buffer* exposure, **not a direct measurement of water, breeding pools, reproductive fitness or a verified clearing date**.
- [Route 360412](https://www.iowadnr.gov/media/2011/download?inline=), stop 7 (SiteID 7247), is described as a **gravel crossing of the Volga River** in Fayette County. The two older “forest loss” labels fall on visually open/agricultural ground, with Science TCC stable at 3%. These are consistent with raster category/boundary ambiguity, not a demonstrated change in the stream crossing.

Both DNR documents are dated in **January 2021** with blank site establishment date. They are independent textual clues to recorded monitoring habitat type, but **do not resolve station relocation/continuity during NAAMP 2001–2015**. No other Iowa route is selected because of these text descriptions. This further distinguishes **a terrestrial canopy buffer changing near a listening stop** from **the aquatic reproductive site changing**.

