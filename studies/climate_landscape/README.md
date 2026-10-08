# Climate × remote sensing × NAAMP frog calling — independent study (source gate v3.1)

## Current status — 2026-10-08

**Separate from locked JAE RC6. No manuscript, null model or accepted ecological result has changed.**

- **Source-only Iowa archive verification (v3.1):** checksum-pinned 21,934 original Runs and 219,340 original Stops; **zero direct wet/dry, water level or inundation columns** in the national `Stops.csv`. [Successful original workflow](https://github.com/zuizui0223/frogcs/actions/runs/37774857243). Full interpretation: [v3.1 actual schema receipt](V3_1_ACTUAL_USGS_WETNESS_SCHEMA_RESULT_2026-10-08.md) and [historical state-native archive gate](V3_1_HISTORICAL_STATION_AND_LOCAL_WETNESS_SOURCE_GATE.md).
- **Potential Iowa source not yet available:** historical 2010–2015 state-native wet/dry records and stop relocation logs remain **unknown**. [Iowa DNR enquiry draft (UNSENT)](IOWA_DNR_NAAMP_2010_2015_ARCHIVE_ENQUIRY_UNSENT.md).
- **Land-cover source check:** v2.2 examined 7 new Iowa routes / 70 nominal stops without opening their frog calling outcomes. Five source-selected old NLCD C1V0 category-loss pixels did not support a common regional 2012 clearing event. Later USDA Science TCC gave mixed tree-canopy results; historical physical-site continuity is unverified. See [v3.0 canopy uncertainty result](V3_0_REAL_CANOPY_SE_INTERPRETATION_AND_NO_CAUSAL_CLAIM.md).
- **Explored exception:** the earlier **Iowa 360417** v2.0 pilot **did** read actual `Counts.csv` (592 positive acoustic records) and is **post-hoc descriptive only**, not proof of a forest-caused frog response. The new 7 route outcome records remain unopened. See [v2.0 acoustic readout](V2_0_ACTUAL_FROG_ACOUSTIC_LANDCOVER_RESULT.md).

**Current stop rule:** The USGS national archive alone cannot test direct local hydrology. Do not use present-day Iowa forms as historical data, select more forest-loss cells after response inspection, or fit a new acoustic model until archived field schema, historical stop identity and source comparability are independently verified.

---

## Historical v0.3 environment-extraction prototype

The following describes the initial **response-blind environmental prototype**, not the later v2.0 descriptive acoustic pilot. This prototype by itself did not contain frog calls or validated historical station-to-satellite overlays.

The 2001–2015 10-stop NAAMP network is suitable for a possible longitudinal study of how hydroclimatic trends, water availability and terrestrial land-cover change relate to **where frogs are acoustically detected**, but not for concluding successful breeding, true absence, abundance or anthropogenic attribution without more evidence.

## Inputs and order

1. Obtain the pinned NAAMP coordinate table and run `scripts/audit_coordinates.py` (geometry-only); see `remote_sensing/EXPORT_CONTRACT.md` for source hash.
2. Independently verify a subset of station identities/coordinates against field/route documentation, then prepare metadata-only surveyed stop records. Geometry-pass alone never creates `verified_external` status.
3. Run `scripts/build_extraction_manifest.py` to list JRC water image-months and USGS Annual NLCD raster years strictly before each survey.
4. Run the **unauthenticated local** annual NLCD GeoTIFF area extractor only after separately downloading/archiving official source files. For JRC, use the **unexecuted Google Earth Engine recipe** in `remote_sensing/jrc_monthly_export_gee.js` in an authenticated GEE workspace, with the verified site/month manifest uploaded.
5. Run `scripts/build_remote_sensing_features.py` to derive strictly lagged water/landcover features, preserving missing imagery and last observation dates.
6. Run `scripts/build_climate_features.py` on separately downloaded Daymet/PRISM daily series (with 1981–2000 baseline) and `scripts/build_climate_trend_diagnostics.py` (1981–2015 descriptive site trends only).
7. After freezing exposure availability, merge the environmental tables by exact `run_id,route_id,site_id,survey_date,coordinate_qc_status`. Only a separately approved response-stage study may then read taxon calling records.

## v0.3 scientific and implementation changes

- A site-by-survey **metadata-only** observation panel is generated from pinned NAAMP Runs and Stops. This does not use the sparse-positive `Counts.csv` or infer fake zeros.
- Calendar-matched consecutive-year exposure comparisons are constructed for the same route/physical site/survey round before consulting any calling responses.
- JRC visible **water area** and detected **water-month frequency** are separate, with observation-gap bounds. A detected pixel is not proof of adequate frog breeding water.
- See `IMPLEMENTATION_STATUS_V0_3.md` for limitations, definitions and the status of actual public-data acquisition.

## Synthetic checks

```bash
pip install -r requirements.txt
pytest -q tests
```

The test suite creates synthetic geographic rasters, synthetic Daymet timeseries and synthetic image-month totals. It ensures no survey-day/future imagery or weather leaks into features; no-data is not treated as dry; coordinates are never automatically externally verified. **Synthetic test values are not ecological results.**

## Input ceilings

Official Annual NLCD Collection 1.2, CONUS, 30 m, 1985–2025: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover

JRC Monthly Water History, 30 m, 1984–2021: https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory

Daymet single pixel calendar: https://daymet.ornl.gov/single-pixel-tool-guide — leap years have 365 Daymet records: Dec 31 is omitted. The climate adapter does not silently interpolate such gaps.

Original NAAMP public dataset: https://doi.org/10.5066/F7G44NG0

See `RESEARCH_SPEC.md` for competing ecological hypotheses and causal-inference limits. See `remote_sensing/EXPORT_CONTRACT.md` for extraction input/output schemas and commands.

## First real longitudinal coverage readout

See `LANDSAT_LONGITUDINAL_METADATA_RESULT_V0_1.md` for a source-pinned, outcome-blind analysis of 3,811 NAAMP runs across 395 routes and multi-year Landsat acquisition metadata. It does **not** demonstrate climate change effects on frogs, or guarantee QA-passing satellite pixels.

## New source-backed land-cover results (v1.8, independent exploratory route)

For Iowa NAAMP route 360417, actual USGS-authored **Annual NLCD Collection 1.0**, not the preferred 1.2, pixels were retrieved for 2004, 2009 and 2014. The additional source-only checks are now in [`V1_8_REAL_NLCD_C1V0_ECOLOGICAL_GROUP_CHANGE.md`](V1_8_REAL_NLCD_C1V0_ECOLOGICAL_GROUP_CHANGE.md) and [`V1_8_NLCD_SITE_SHIFT_QC.md`](V1_8_NLCD_SITE_SHIFT_QC.md). **No historical physical-site validation or new frog-landcover causal result exists.** Previous v0.9 negative held-out five-year climate acoustic forecast is unchanged; do not tune it after readout. The locked JAE RC6 is unaffected.
