# E3 Landsat NDMI response-blind metadata coverage stage — v0.1 (2026-10-08)

**Scientific contract unchanged:** `revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md`.

## Prerequisite

Planetary Computer signed public Landsat C2 Level-2 source access passed all three historical non-NAAMP eras (2002, 2008, 2014), GitHub Actions run 37711481855. The source-only repair affects API request pacing and not ecological data or the NDMI definition.

## Purpose

Test a **necessary, not sufficient** condition for the frozen E3 pixel-coverage gate, before reading any E3 spectral values at NAAMP sites:

> Does each focal survey RunID have at least one USGS Landsat C2L2 acquisition within the preceding 32 days whose *single product footprint* includes all ten physical SiteIDs?

No frog CallingIndex, NDMI pixel values, or fitted mechanism residuals are calculated during this stage. The already fixed principal-pair universe is reconstructed for identity/date joins only.

## Frozen metadata rules

- Product: Planetary Computer STAC `landsat-c2-l2`, same USGS C2L2 as the E3 science contract.
- For every unique focal RunID in the frozen 2,916-pair strictly-prior-history universe, use the survey date and ten physical SiteIDs only.
- Exclude routes failing the already fixed strict coordinate geometry authority. Never repair coordinates after outcomes.
- Search exactly the **32 calendar days preceding and including** the survey date, never later scenes.
- Require the same STAC item/product, not merely separate scene availability at each stop.
- Require all four asset keys `nir08`, `swir16`, `qa_pixel`, `qa_radsat` and a verified TM/ETM+/OLI Landsat sensor ID.
- Check the STAC footprint polygon against all ten stop coordinates (fallback to item bbox only if valid polygon geometry is absent, and disclose that fallback).
- Sort candidates by most recent acquisition, then lexicographic product ID. Store only public item IDs/dates/lags; never signed SAS URLs.
- Use at most 100 STAC items per RunID. Overflow, service errors or missing geometry fail closed as `metadata_unresolved` rather than silently negative.
- This phase does not select a final QA-qualified image or inspect pixel quality.

## Interpretation and gates

Report unique RunIDs; metadata-complete runs; focal pairs whose both wet/dry RunIDs have at least one **same-product/all-ten-stops** candidate; represented routes and states.

If the number of metadata-complete focal pairs is below 1,500, or routes below 300, or states below 15, the **final E3 pixel gate cannot pass**. Close as `E3_remote_moisture_coverage_inconclusive` (metadata upper-bound shortfall), with no search for alternate radii or time windows.

If all metadata thresholds pass, proceed to the **unchanged** final 500-m/70%-valid-pixel/one-scene-per-RunID E3 source extraction and QA gate. Metadata PASS is not authorization to inspect frog endpoints.

The E3 route remains the final abiotic remote-sensing test. Do not change the search period, sensor, NDMI definition, route sample, scene footprint rule, or gate to rescue coverage.
