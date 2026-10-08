# v2.3: Reversal vs persistence of annual mapped classes, source-only

Date: 2026-10-08. This is a post-environmental-readback diagnostic on Iowa 360417, **not** a frog acoustic or causal effect analysis. JAE RC6, the negative held-out v0.9 climate prediction and the v2.2 absence of a common 2012 local forest-loss treatment remain frozen.

## Actual immutable-source result

Loaded all 15 original `Annual_NLCD_LndCov_2001..2015_CU_C1V0` 30m same-grid TIFFs from the original successful [15-year environment-only source extraction](https://github.com/zuizui0223/frogcs/actions/runs/37756736760). Checked each source TIFF against its original-year source SHA256. Every nominal DNR 360417 SiteID 7271–7280, and both 250m and 1000m frozen buffers, was included. Counted one-year post-change persistence for 2001→02 through 2013→14; the final 2014→15 transition has no subsequent year in the source and is **not** assigned a fabricated persistence status.

| Year-to-year functional-group changes, 13 transitions | 250m (summed site-buffer cells) | 1km (summed, potentially overlapping) |
|---|---:|---:|
| Functional-group changed cells | **70** | **950** |
| Returned to earlier group the following year | **7 (10.0%)** | **99 (10.42%)** |
| Still in new group the following year | 63 | 846 |
| Switched to a third different group | 0 | 5 |
| Forest→nonforest class cells | **22** | **200** |
| Forest-loss classification reverted to forest the following year | **0** | **9 (4.5%)** |

Among the 250m forest-loss classifications with a following-year observation, 2006 had 9 forest-loss cells, 2012 had 5 and 2014 had 5. Thus **2012 is not the only year with mapped forest loss**, even in the initial exploratory route. The complete by-year table, source validator, unit tests and 260 site×radius×year records are committed under `scripts/audit_c1v0_transition_reversals_v23.py`, `tests/test_c1v0_transition_reversals_v23.py` and `receipts/c1v0_temporal_reversal_v23/`. Two new synthetic tests passed; the local full study suite passed **166/166** on this code state.

## Ecological inference limits

- These are **classification transitions within Collection 1.0**, not observed felling, wetland drainage, vegetation mortality, or frog movement. NLCD's interannual algorithms may favor temporal smoothness, making apparent persistence partly methodological. Annual images also do not resolve the exact disturbance date.
- One-kilometer circles within a route overlap; aggregate counts are not independent land area or ecological units. Repeated yearly pixels are not independent samples.
- The original 2021 DNR published route map agrees with archived USGS coordinates numerically, but the true 2001–2015 field station positions remain **unverified**.
- The source study does not read `Counts.csv`. The earlier retrospective 360417 strong calling contrast was non-causal and unconvincing, and cannot become confirmatory because the mapped environmental categories are stable.
- The current USGS Annual NLCD **Collection 1.2 land cover and confidence** product has been released; source-version audit must precede using its confidence or comparing it to Collection 1.0. Do not merge classification versions in one numeric transition.

## Next decision

Rather than repeat the preselected 2012 breakpoint or retune ecological predictors, check whether the few mapped forest-loss pixels are classified with consistent and meaningful **source-matched class confidence**; and separately obtain historical field-site corroboration. Only a previously uninspected, independently selected landscape panel with exact sampling dates could eventually support a new ecological hypothesis test.
