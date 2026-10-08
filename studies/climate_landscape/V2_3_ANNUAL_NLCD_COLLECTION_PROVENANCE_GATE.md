# v2.3 NLCD source provenance and confidence-gate readout

**Date: 2026-10-08. Source-only, no new frog outcomes.** This is not a claim of Collection 1.2 exposure completeness. RC6 and the frozen v0.9 negative climate forecast remain unchanged.

The official [USGS Annual NLCD Collection 1.2](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover) release provides Land Cover, Land Cover Change and Land Cover Confidence; its Land Cover Confidence is a 1–100 model classification confidence, **not a field-calibrated probability of true change**. Different collections must not be pooled within a two-year pixel transition.

A new read-only [GitHub Actions source probe](https://github.com/zuizui0223/frogcs/actions/runs/37764311875) tested 2011, 2012 and 2013 for three Esri public original ImageServer products. Original machine-readable [provider-catalogue receipt](https://github.com/zuizui0223/frogcs/actions/runs/37764311875/artifacts/11543487446):

| Public imagery product / 2011–2013 | Exact source catalogue naming | C1V2 (1.2)? |
|---|---|---|
| Annual Land Cover | `Annual_NLCD_LndCov_<year>_CU_C1V0`, Version 1.0 | **No** |
| Annual Land Cover Confidence | `Annual_NLCD_LndCnf_<year>_CU_C1V0`, Version 1.0 | **No** |
| Annual Land Cover Change | `Annual_NLCD_LndChg_<year>_CU_C1V0`, Version 1.0 | **No** |
| Separate federal vegetation endpoint | No year-catalogue rows for queried years | **Unresolved** |

**Decision:** none of these catalogue endpoints validates Collection 1.2. The already downloaded C1V0 raster source remains historical/provisional. The old same-version C1V0 *confidence* product is nevertheless available, and a matched 2011–2013 per-pixel diagnostic is being attempted. Do not label its raw values C1.2, and do not substitute confidence values for independent aerial-photo classification.

Additional actual 2001–2015 **temporal stability QC** is independently recorded at `V2_3_ACTUAL_TEMPORAL_CLASS_REVERSAL_AUDIT.md`: among 13 eligible transitions with a following year at the initial nominal Iowa 360417 route, 10% of functional-group changes in 250m buffers reverted after one year while mapped forest-to-nonforest cells did not revert. Those numbers are for NLCD **classes**; annual classifier temporal consistency can mechanically increase persistence and does not verify field disturbance.

The new seven-route environmental gate (v2.2) showed just **1/70** nominal sites with a negative 250m net forest proportion change from 2011 to 2012, despite 2/70 having at least one gross forest-class loss cell. The shared-2012 treatment hypothesis remains stopped.

## Next evidence gate

Only claim a class-confidence-supported forest change when pixel-aligned `LndCov` and `LndCnf` from the **same collection and years** pass original-catalogue verification, spatial grid checks, exact fixed-site selection and a repeatable SHA256 source readback. Independently field-dated station geometry remains zero.
