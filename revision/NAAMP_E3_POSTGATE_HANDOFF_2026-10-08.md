# E3 NDMI postgate handoff and specification authority — 2026-10-08

## Status at handoff

**E3 focal NDMI values and the frog concentration endpoint have not been evaluated in this branch.**

Pre-response metadata necessary gate:
- GitHub Actions run 37711943954, PASS
- 2,633 geometry-qualified focal pairs
- 395 routes
- 20 states
- 3,811 unique focal RunIDs with same-product scene metadata candidates
- Pixel QA still required; a metadata gate cannot authorize frog endpoint readback

Formal pixel-quality gate:
- GitHub Actions run **37723985357**, 16 shards
- The exact outcome is determined only by its final aggregated receipt,
  `E3_NDMI_FINAL_PIXEL_COVERAGE_V0_1.json`.
- Do not extrapolate the final gate from small first-candidate pilot statistics.

Postgate code prepared here:
- `scripts/remotesensing/extract_e3_ndmi_postgate_shard.py`
- `scripts/remotesensing/aggregate_e3_ndmi_postgate.py`
- `scripts/remotesensing/run_e3_ndmi_final_mechanism.py`
- `.github/workflows/e3_ndmi_postgate_mechanism.yml`

Static compilation and guard checks succeeded in GitHub Actions run **37724560102**.
This is code QA, not an ecological result.

## Specification authority: document an important difference honestly

Two E3 science documents exist:
1. `revision/NAAMP_LANDSAT_NDMI_PROSPECTIVE_MECHANISM_V0_1.md`:
   an **earlier** 16-day, 250-m, >=50%-valid design.
2. `revision/NAAMP_E3_LANDSAT_NDMI_FINAL_ABIOTIC_CONTRACT_V0_1.md`:
   the **later, authoritative** 32-day, 500-m, >=70%-valid design.

The first must not be described as if it used the final parameters. The later design was frozen before focal E3 NDMI values and the E3 frog concentration endpoint were read, but after upstream source-access and feasibility work. Therefore call it **pre-outcome frozen**, not a design prospectively registered before every source-inspection step.

Only the final E3 contract governs this test. If its coverage fails, do not revert to the older 16-day/250-m scheme. Do not report the older scheme as a sensitivity analysis.

## Exact frozen science

- USGS Landsat C2L2 surface reflectance
- TM/ETM+ NIR B4, SWIR1 B5; OLI NIR B5, SWIR1 B6
- SR = DN*0.0000275 - 0.2
- NDMI = (NIR-SWIR1)/(NIR+SWIR1)
- median QA-qualified NDMI within 500-m radius
- >=70% valid nominal pixels; cloud/snow/shadow/water/saturation masking
- one same Landsat scene/product for all 10 physical stops per RunID
- acquisition from 0–32 days before survey, never later
- most recent full-route QA-qualified candidate; lexicographic tie-breaking
- frozen strict coordinate gate
- >=1,500 complete pairs, >=300 routes, >=15 states to pass

If the pixel gate passes, M_E3 adds opposite-route-fold species-specific NDMI coefficients, fitted from SiteID-then-RunID-centered NDMI, to the unchanged principal comparator (M0). The focal stop shift uses same-SiteID wet-minus-dry NDMI. Pair-wide expected wet incidence is matched as before.

The exact within-taxon concentration endpoint, null simulation framework and 1,000-replicate rule are unchanged. Compare M0 and M_E3 **on the identical pixel-QA-qualified sample**.

## Implementation guards

1. No spectral NDMI calculation unless the formal pixel gate classification equals `E3_pixel_QA_coverage_gate_pass`.
2. The postgate extraction checks metadata and QA receipt hashes, selected product IDs and RunID-to-site identity.
3. Sixteen complete extraction shards and all ten stop values per selected RunID are required before aggregation.
4. The mechanism runner checks that its sample counts equal the gate's confirmed pairs/routes/states and refuses mismatches.
5. If the gate fails, the workflow records an E3 coverage-inconclusive receipt without calculating frog concentration.
6. If the gate passes, it runs **M0 vs M_E3 once**. Do not tune the index, radius, cloud rule, 32-day window, taxa or subsets after readback.

The workflow is prepared for an isolated, explicit push to `remotesensing/e3-ndmi-postgate-run-v1` when the formal QA receipt exists. Do not dispatch it before the gate decision is known.

## Relation to existing results

Published/closed JRC visible open-water, MODIS DSWEmod partial/potential-water, 3-month persistence and 12-month variability did not explain the excess concentration.

NWI official water-regime × rain interaction on 2,028 pairs / 300 routes / 20 states reduced the residual by **-0.18%** and was unsupported.

NWI wetland-area × rain interaction passed its corrected response-blind coverage gate on 2,409 pairs / 364 routes / 20 states. Its residual changed from **0.367787 (M0)** to **0.372321 (M_AREA)**, fraction removed **-1.23%**; the observed concentration still exceeded null bounds (P=.000999). GitHub Actions run 37705731375.

Nighttime thermal LST E2 was coverage-inconclusive, not disproven.

E3 is the **last** frozen public remote-abiotic candidate. It measures spectral vegetation moisture, not direct water depth, water temperature or soil moisture.

## Decision after E3

- Pixel gate below threshold: **coverage-inconclusive**. Do not read frog endpoint or relax parameters.
- Gate passes, residual inside E3 null interval: sufficient under this statistical generator; candidate ecological filter, not unique causal proof.
- Gate passes, residual decreases but stays outside: partial mechanism only.
- Gate passes, residual does not decrease: E3 non-support.

If E3 is non-support or inconclusive, stop this remote-abiotic search and prioritize biological/latent mechanisms on genuinely independent evidence: local demographic availability, species×route-night reproductive readiness and acoustic/chorus-state processes.

**Keep RC6/JAE submission main unchanged throughout.**
