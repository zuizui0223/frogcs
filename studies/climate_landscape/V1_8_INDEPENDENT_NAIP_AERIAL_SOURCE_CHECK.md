# Independent Iowa NAIP aerial-orthophoto source check (v1.8)

**Date: 2026-10-08. Source-only visual corroboration, not a classification accuracy assessment.** RC6 untouched; climate strong-calling holdout v0.9 remains negative.

## Motivation

USGS-authored Annual NLCD **C1V0** records a mapped forest-fraction decrease at nominal NAAMP route 360417 SiteID 7280 (stop 10), 250m, between 2004 and 2014; mapped forest loss is robust to 6–30m shifts in the nominal center, but categorization error is not addressed by coordinate stress tests. SiteID 7273 (stop 3) was chosen as a second site **after** reading the mapped categories. This is postreadback descriptive site selection, not an independent prospective or random-sample test.

## Actual independent imagery

Iowa State University [Iowa Geographic Map Server](https://ortho.gis.iastate.edu/), under its [official WMS directory](https://ortho.gis.iastate.edu/IGMS_WMS.html), serves USDA NAIP **summer natural-color orthophotos** for 2004 (2m maximum ground resolution) and 2014 (1m maximum). Their source mosaic acquisition periods, radiometry and resolution differ.

[Successful source-only GitHub Actions run 37756461934](https://github.com/zuizui0223/frogcs/actions/runs/37756461934) retrieved four original PNGs: stops 3 and 10, 2004 and 2014. [Image and provenance artifact 11540550588](https://github.com/zuizui0223/frogcs/actions/runs/37756461934/artifacts/11540550588).

- 2004 WMS layer: `naip_2004_nc`; server capabilities SHA256 `9d4e12cc1395e8405acfae231b1848e8ec5955fbb98848858329428aa91bfef3`.
- 2014 WMS layer: `naip_2014_nc`; server capabilities SHA256 `2264d79867f222a1902eea8a8483ef91cedbf2d7815936f6cde975a935fb8955`.
- Both source images for each site were requested in exactly the **same Web Mercator BBOX** and dimensions 600×600; all four returned valid images.
- Stop 3 2004: `41a6503576404920d627ed66287696618f362d75217e5a834dc6ffed1285248d`.
- Stop 3 2014: `795284db2d24a4893bb5594fbf4c40682cd37ecc2f55b1576c179884f43fb6ee`.
- Stop 10 2004: `565466400001c96de8d80ac30521d65e963124dbef59fb004bf28be17f6520b4`.
- Stop 10 2014: `b9a325fadef5a5cf97a8f54ebb45a6b86b1c04bfe8f1caac07ec230757480b72`.

## Careful visual assessment

Roads and field boundaries can be matched visually between dates at both sites. The stop-10 upper-centre/upper-right wooded and scattered-tree landscape **appears different** between 2004 and 2014; agricultural field appearance also differs. The stop-3 ponds and nearby wooded corridor are visible in both years. This provides **an independent original-imagery opportunity to investigate** the older C1V0 mapped pattern; it is **not yet an independently georeferenced manually classified change map**.

Do NOT use a subjective screenshot comparison to declare the 17 C1V0 'forest loss' pixels correct, or to infer actual wetland drying, amphibian breeding, habitat abandonment or a climatic cause. Before interpreting changes quantitatively, georegister actual source pixels, account for 2004-vs-2014 acquisition season, sensor/radiometric differences, canopy shadows and source-image spatial resolution, and verify C1.2 land-cover and confidence data. Current independent verification of 2001–2015 physical station continuity remains **zero**.

No `Counts.csv`, acoustic response, reproduction or occupancy was read by the NAIP source workflow. The NAIP raster files are retained as an Actions source artifact, not committed as binary files into the research branch. For imagery provenance/attribution, acknowledge Iowa State University GIS Facility and USDA NAIP.
