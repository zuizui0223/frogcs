# Climate × terrestrial landscape × NAAMP acoustic site use — independent study v1.1

**Scientific status (2026-10-08):** the past-five-year climate-history add-on did **not** improve held-out strong-calling prediction in the frozen 9-route v0.9 pilot (test gain −0.002257 per stop); do not retune the pilot. A separate USGS Runs/Stops-only audit found 95/8,223 route × SiteIDs with nonconstant stop number and 28,330 adjacent-year same-season candidate stop comparisons with invariant stop numbering and geometry-only passing coordinates. **Exactly 0 historical physical stations have independent location corroboration; no real 30-m Annual NLCD land conversion × species calling allocation result exists.** Response-blind traffic/noise longitudinal coverage is a newly implemented gate, with actual-source execution separate from the frozen frog result.

- [Actual negative acoustic forecast](V0_9_REAL_FROG_RESULT.md)
- [Actual pinned USGS site-identity continuity result](V1_0_HISTORICAL_SITE_IDENTITY_GATE.md)
- [Source-only roadside detection-confounder audit](V1_1_ROADSIDE_DETECTION_COVERAGE_GATE.md)
- [Main two-scale biological inference contract](TWO_SCALE_CLIMATE_LANDSCAPE_INFERENCE_CONTRACT_V0_1.md)

The rest of this README describes the historical v0.3 extraction prototype, retained for reproducibility.

---

# Climate × remote sensing × NAAMP frog calling: independent v0.3 research package

This is a separate, **response-blind environmental extraction prototype** developed on 2026-10-08. It **does not** contain actual NAAMP acoustic outcomes or a validated station-to-satellite overlay. It does **not** modify the submitted RC6 scientific story.

The 2001–2015 10-stop NAAMP network is suitable for a possible longitudinal study of how hydroclimatic trends, water availability and terrestrial land-cover change relate to **where frogs are acoustically detected**, but not for concluding successful breeding, true absence, abundance or anthropogenic attribution without more evidence.

## Inputs and order

1. Obtain the pinned NAAMP coordinate table and run `scripts/audit_coordinates.py` (geometry-only); see `remote_sensing/EXPORT_CONTRACT.md` for source hash.
2. Independently verify a subset of station identities/coordinates against field/route documentation, then prepare metadata-only surveyed stop records. Geometry-pass alone never creates `verified_external` status.
3. Run `scripts/build_extraction_manifest.py` to list JRC water image-months and USGS Annual NLCD raster years strictly before each survey.
4. Run the **unauthenticated local** annual NLCD GeoTIFF area extractor only after separately downloading/archiving official source files. For JRC, use the **unexecuted Google Earth Engine recipe** in `remote_sensing/jrc_monthly_export_gee.js` in an authenticated GEE workspace, with the verified site/month manifest uploaded.
5. Run `scripts/build_remote_sensing_features.py` to derive strictly lagged water/landcover features, preserving missing imagery and last observation dates.
6. Run `scripts/build_climate_features.py` on separately downloaded Daymet/PRISM daily series (with 1981–2000 baseline) and `scripts/build_climate_trend_diagnostics.py` (1981–2015 descriptive site trends only).
7. After freezing exposure availability, merge the environmental tables by exact `run_id,route_id,site_id,survey_date,coordinate_qc_status`. Only a separately approved response-stage study may then read taxon calling records.

## v0.3 scientific changes

- Build a source-pinned, response-blind NAAMP surveyed-site opportunity panel from Runs and Stops only.
- Compare exact consecutive years at the same verified physical site and survey round, within a 21-day season window.
- Preserve JRC missing observations and distinguish visible water area from observed water-month frequency.
- See `IMPLEMENTATION_STATUS_V0_3.md` for source and biological inference limits.

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

## Actual longitudinal Landsat coverage, outcome-blind

The real 3,811-run metadata feasibility audit (395 routes) and geographic sampling-bias check are documented in [`LANDSAT_LONGITUDINAL_METADATA_RESULT_V0_1.md`](LANDSAT_LONGITUDINAL_METADATA_RESULT_V0_1.md). Comparisons remain **scene-metadata only**, not verified QA-good satellite pixels or frog climate effects.
