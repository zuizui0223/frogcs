# v1.8 — Iowa 360417 mapped forest-change sensitivity to site-coordinate displacement

**Study status: independent, descriptive environmental audit. 2026-10-08.** RC6 is unchanged. Earlier negative H1-versus-H0 climate acoustic forecast remains negative. **NO frog Counts.csv was accessed in this audit.**

## Controlling data and provenance

The original downloadable USGS-authored / Esri-hosted Annual NLCD **Collection 1.0 (C1V0)** source is GitHub Actions [37754405051](https://github.com/zuizui0223/frogcs/actions/runs/37754405051), artifact [11539925980](https://github.com/zuizui0223/frogcs/actions/runs/37754405051/artifacts/11539925980). Immutable source artifact ZIP SHA256 `570c17d302046eecccf1013ccd610c35c0172bccf32c052ae1dd34c7780ea82d`; individual TIFF hashes are in the machine receipt. This is **not** Annual NLCD Collection **1.2** (USGS June 2026). All 2004/2009/2014 TIFFs have one uint8 categorical band at 30m, EPSG:5070, **409×170 fully valid aligned pixels**, with an identical cropped spatial extent. Class codes are checked against the approved legend; `0` and `255` remain missing, not dry/open/nonforest.

The fixed nominal station source is `reference_routes/iowa_dnr_360417_source_only_stops_v16.csv` (SHA256 `8b7be934dc32aa71791b4e6c38295d25cbcebb66f2f6ab39714d41ce7b65f227`). The 2021 Iowa DNR 360417 map agrees with USGS archived coordinates at all 10 stops (median discrepancy 4.15m; max 5.84m), but these sources may share inputs. **Historically independently verified physical stations during 2001–2015 = 0.** No site-level frog–landscape effect is licensed.

## Actual pixel readout and positional sensitivity

Source: every original C1V0 30m categorical pixel. The 250m circular buffer has about 217 native pixel centers. Results here are directly computed from the 3 source rasters and are **NOT statistical significance tests**. Since the result has already been viewed, this shift audit is explicitly *postreadback descriptive sensitivity*, not independent confirmation.

| DNR Stop | 2004 forest % | 2009 % | 2014 % | 2004→2014 change (pp) | ±6m range (pp) | ±30m range (pp) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 27.19 | 27.19 | 25.35 | -1.84 | [-1.88, -1.81] | [-1.87, -1.82] |
| 2 | 0.45 | 0.45 | 0.45 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 3 | 16.97 | 16.97 | 16.97 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 4 | 4.13 | 4.13 | 4.13 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 5 | 2.31 | 2.31 | 2.31 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 6 | 13.82 | 14.75 | 14.29 | 0.46 | [0.45, 0.47] | [0.45, 0.47] |
| 7 | 2.74 | 2.74 | 2.74 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 8 | 0.00 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 9 | 5.91 | 5.91 | 5.91 | 0.00 | [0.00, 0.00] | [0.00, 0.00] |
| 10 | 12.73 | 8.18 | 5.45 | -7.27 | [-7.34, -6.85] | [-7.48, -5.48] |

**Shifts used for sensitivity (fixed to interpretable physical scales):** original centre, then cardinal and diagonal directions at 6m (exceeds the maximum **inter-document discrepancy**, not a bound on true historical location error), 15m (half a source pixel), and 30m (one pixel). This is a deterministic edge-pixel stress test, not a spatial bootstrap. Across all stops, buffer radii and offsets this produces **500 station×scale×location centre evaluations** (not 500 statistically independent replicates).

- **Site 10 / SiteID 7280 (250m):** mapped forest fraction decreases **12.73% (2004) → 8.18% (2009) → 5.45% (2014)**. The original centre shows **17 loss vs 1 gain forest pixels**, **12** forest→agriculture, **0** forest→developed. The -7.27 percentage-point net forest change remains negative for all 8 directional shifts at 6m (**-7.34 to -6.85 pp**) and 30m (**-7.48 to -5.48 pp**).
- **Site 3 (250m):** no change in any NLCD class at the exact centre from 2004 to 2014, and zero net forest change even with all 30m shifts. **But its 1km buffer contains 192 changed-class pixels** over the same years; no assertion that the wider landscape was stable.
- **The spatial scale matters:** site 10 net forest change is only **-1.72 percentage points at 1km**, compared with -7.27 pp at 250m. Site 3's 1km net forest change is -0.115 pp rather than zero. **Nine of 45 pairs of 1km buffers overlap geometrically** (center distance <2km), while none of the 250m pairs overlap; do not interpret ten 1km buffers as independent landscapes.

## What can and cannot be concluded

This is credible **mapped source-image change** rather than a numerical artifact from placing a circle 6m differently. It does **not** independently verify a real on-the-ground forest conversion: Collection 1.0 categorical classification errors, land-cover temporal smoothing, independent 1.2 accuracy/confidence products, and historic physical-station relocation are unmeasured. The static 2021 map cannot prove the pre-2015 sites were unchanged. There is **no causal inference, frog acoustic change, breeding habitat fate, or population response** in this receipt.

## Next authoritatively justified source step

USGS reports **Annual NLCD Collection 1.2 Land Cover** and **Land Cover Confidence** via EarthExplorer, MRLC Viewer, official tiles and AWS (some paths require viewer-mediated download or requester-pays credentials):
- https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access
- https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover
- https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover-confidence

Before any species-specific outcome-stage analysis: (i) verify the **2004/2009/2014** environmental changes against official C1.2 labels and confidence, (ii) establish contemporary/historical physical SiteID positions and relocation history independent of 2021 map, (iii) preregister site-time recruitment/attrition, time and geographic blocks, and detection noise. Do **not** try a new acoustic threshold/species subgroup to rescue the earlier negative climate forecast.

## Reproduction

`python studies/climate_landscape/scripts/audit_nlcd_geolocation_sensitivity_v18.py --artifact-zip original_c1v0_three_year_zip --station-csv studies/climate_landscape/reference_routes/iowa_dnr_360417_source_only_stops_v16.csv --outdir out`

Source-only synthetic tests: `pytest -q studies/climate_landscape/tests/test_nlcd_geolocation_sensitivity_v18.py`.

Machine result: `receipts/nlcd_geolocation_sensitivity_v18/site_scale_sensitivity.csv` and `receipt.json`.
